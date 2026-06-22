"""BM25Okapi keyword search built from Qdrant-stored documents."""

import re

from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from config.settings import settings
from utils.logger import get_logger

log = get_logger("bm25_retriever")

client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)

# Module-level index state
_bm25_index: BM25Okapi | None = None
_bm25_docs: list[Document] = []


def _tokenize(text: str) -> list[str]:
    """Simple whitespace tokenizer with punctuation removal."""
    return re.sub(r"[^a-zA-Z0-9\s]", "", text.lower()).split()


def rebuild_bm25_index():
    """
    Fetch all documents from Qdrant via scroll and rebuild the BM25 index.
    Called after every ingestion.
    """
    global _bm25_index, _bm25_docs
    _bm25_docs = []
    offset = None

    while True:
        results, offset = client.scroll(
            collection_name=settings.qdrant_collection,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        for point in results:
            payload = point.payload or {}
            text = payload.get("page_content", "")
            if text:
                _bm25_docs.append(
                    Document(
                        page_content=text,
                        metadata=payload.get("metadata", {}),
                    )
                )
        if offset is None:
            break

    if _bm25_docs:
        tokenized_corpus = [_tokenize(doc.page_content) for doc in _bm25_docs]
        _bm25_index = BM25Okapi(tokenized_corpus)
        log.info(f"BM25 index rebuilt with {len(_bm25_docs)} documents")
    else:
        _bm25_index = None
        log.info("BM25 index is empty (no documents in Qdrant)")


def bm25_search(query: str, k: int = 15) -> list[Document]:
    """Return top-k documents by BM25 keyword relevance score."""
    if _bm25_index is None or not _bm25_docs:
        return []
    tokenized_query = _tokenize(query)
    if not tokenized_query:
        return []
    scores = _bm25_index.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    results = []
    for idx in top_indices:
        if scores[idx] > 0:
            doc = Document(
                page_content=_bm25_docs[idx].page_content,
                metadata={**_bm25_docs[idx].metadata, "bm25_score": float(scores[idx]), "retrieval_source": "bm25"},
            )
            results.append(doc)
    return results


# Build index on module import (best-effort; collection may be empty on first run)
try:
    rebuild_bm25_index()
except Exception:
    pass
