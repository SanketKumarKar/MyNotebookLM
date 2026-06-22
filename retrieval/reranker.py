"""BGE cross-encoder reranker using FlagEmbedding."""

from FlagEmbedding import FlagReranker
from langchain_core.documents import Document
from utils.logger import get_logger

log = get_logger("reranker")

_reranker: FlagReranker | None = None


def get_reranker() -> FlagReranker:
    """Lazy-load the BGE cross-encoder model (heavy; loaded once)."""
    global _reranker
    if _reranker is None:
        log.info("Loading BGE reranker model (bge-reranker-v2-m3)...")
        _reranker = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)
        log.info("BGE reranker loaded")
    return _reranker


def rerank(query: str, documents: list[Document], top_k: int = 5) -> list[Document]:
    """
    Rerank documents using BGE cross-encoder.
    Only reranks if we have ≥ 3 documents; otherwise returns as-is.
    """
    if len(documents) < 3:
        return documents[:top_k]

    reranker = get_reranker()
    pairs = [[query, doc.page_content] for doc in documents]

    try:
        scores = reranker.compute_score(pairs, normalize=True)
        # compute_score may return a single float if only one pair
        if isinstance(scores, (int, float)):
            scores = [scores]
        ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        for doc, score in ranked:
            doc.metadata["reranker_score"] = float(score)
        return [doc for doc, _ in ranked[:top_k]]
    except Exception as e:
        log.warning(f"Reranking failed, returning unranked: {e}")
        return documents[:top_k]
