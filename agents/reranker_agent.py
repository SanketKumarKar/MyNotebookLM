"""Reranker agent node: cross-encoder reranking of retrieved documents."""

from retrieval.reranker import rerank
from langchain_core.documents import Document
from agents.state import AgentState
from utils.logger import get_logger

log = get_logger("reranker_agent")


def reranker_agent_node(state: AgentState) -> AgentState:
    """Rerank retrieved documents using BGE cross-encoder."""
    try:
        raw_docs = state.get("retrieved_docs", [])
        if not raw_docs:
            state["reranked_context"] = []
            return state

        # Convert dicts back to Documents for the reranker
        docs = [
            Document(page_content=d["content"], metadata=d) for d in raw_docs
        ]
        reranked_docs = rerank(state["query"], docs, top_k=5)

        state["reranked_context"] = [
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", "?"),
                "subject": doc.metadata.get("subject", ""),
                "chapter": doc.metadata.get("chapter", ""),
                "reranker_score": doc.metadata.get("reranker_score", 0.0),
            }
            for doc in reranked_docs
        ]
    except Exception as e:
        log.warning(f"Reranker agent error: {e}")
        state["reranked_context"] = state.get("retrieved_docs", [])
    return state
