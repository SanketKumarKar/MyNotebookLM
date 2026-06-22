"""Retriever agent node: run hybrid retrieval pipeline."""

from retrieval.hybrid_retriever import hybrid_retrieve
from agents.state import AgentState
from utils.logger import get_logger

log = get_logger("retriever_agent")


def retriever_agent_node(state: AgentState) -> AgentState:
    """Execute the full hybrid retrieval pipeline (vector + BM25 + graph + rerank)."""
    try:
        docs = hybrid_retrieve(
            query=state["query"],
            k_final=8,
            subject_filter=state.get("subject_filter") or None,
        )
        state["retrieved_docs"] = [
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source_file", "Unknown"),
                "page": doc.metadata.get("page_number", "?"),
                "subject": doc.metadata.get("subject", ""),
                "chapter": doc.metadata.get("chapter", ""),
                "retrieval_source": doc.metadata.get("retrieval_source", "vector"),
            }
            for doc in docs
        ]
        log.info(f"Retrieved {len(state['retrieved_docs'])} docs for query")
    except Exception as e:
        log.error(f"Retriever agent error: {e}")
        state["retrieved_docs"] = []
        state["error"] = f"Retriever error: {e}"
    return state
