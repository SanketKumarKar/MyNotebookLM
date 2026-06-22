"""Singleton LLM and Embedding clients."""

from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_mistralai import ChatMistralAI
from config.settings import settings

# ── Chat / Reasoning model ──────────────────────────────────────────
if settings.mistral_api_key:
    llm = ChatMistralAI(
        api_key=settings.mistral_api_key,
        model="mistral-large-latest", # or whatever mistral model you prefer
        temperature=0.1,
    )
elif settings.ollama_llm_model:
    llm = ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_llm_model,
        temperature=0.1,
    )
else:
    raise ValueError("Either mistral_api_key or ollama_llm_model must be configured.")

# ── Embedding model ─────────────────────────────────────────────────
embeddings = OllamaEmbeddings(
    base_url=settings.ollama_base_url,
    model=settings.ollama_embedding_model,
)
