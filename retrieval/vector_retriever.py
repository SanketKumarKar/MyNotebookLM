"""Qdrant dense vector retrieval with optional subject filtering."""

from ingestion.vector_store import similarity_search
from langchain_core.documents import Document


def retrieve(query: str, k: int = 15, subject_filter: str | None = None) -> list[Document]:
    """
    Run a dense similarity search against the Qdrant collection.

    Args:
        query: search query string
        k: number of results to return
        subject_filter: optional subject name to filter results by
    """
    filter_dict = None
    if subject_filter:
        filter_dict = {
            "must": [{"key": "metadata.subject", "match": {"value": subject_filter}}]
        }
    return similarity_search(query, k=k, filter_dict=filter_dict)
