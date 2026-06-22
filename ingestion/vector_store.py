"""Qdrant vector store operations — collection creation, add, search."""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document

from config.settings import settings
from utils.llm import embeddings
from utils.logger import get_logger

log = get_logger("vector_store")

# ── Qdrant raw client (for collection management & BM25 scroll) ─────
client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key or None,
)


def ensure_collection():
    """Create the document collection if it doesn't exist."""
    existing = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection not in existing:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(
                size=settings.embedding_dimensions,  # 2560 for qwen3-embedding:4b
                distance=Distance.COSINE,
            ),
        )
        log.info(
            f"Created Qdrant collection '{settings.qdrant_collection}' "
            f"(dim={settings.embedding_dimensions}, cosine)"
        )
    else:
        log.info(f"Qdrant collection '{settings.qdrant_collection}' already exists")


# Create collection on import (best-effort)
try:
    ensure_collection()
except Exception as e:
    log.warning(f"Could not ensure Qdrant collection on startup: {e}")


# ── LangChain vector store ───────────────────────────────────────────
vector_store = QdrantVectorStore(
    client=client,
    collection_name=settings.qdrant_collection,
    embedding=embeddings,
)


def add_documents(docs: list[Document]) -> list[str]:
    """Add documents to Qdrant and return their IDs."""
    if not docs:
        return []
    ids = vector_store.add_documents(docs)
    log.info(f"Stored {len(ids)} document vectors in Qdrant")
    return ids


def similarity_search(
    query: str, k: int = 10, filter_dict: dict | None = None
) -> list[Document]:
    """Dense similarity search against the collection."""
    return vector_store.similarity_search(query, k=k, filter=filter_dict)
