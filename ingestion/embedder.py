"""Thin embedding wrapper around the shared Ollama embeddings client."""

from utils.llm import embeddings


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts using qwen3-embedding:4b via Ollama."""
    return embeddings.embed_documents(texts)


def embed_query(text: str) -> list[float]:
    """Embed a single query string."""
    return embeddings.embed_query(text)
