"""LangGraph agent state definition."""

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Shared state passed through all nodes in the LangGraph pipeline."""

    # ── Input ────────────────────────────────────────────────────────
    user_id: str
    query: str
    chat_history: Annotated[list, add_messages]

    # ── Query classification ─────────────────────────────────────────
    intent: str            # "question" | "quiz" | "summary" | "revision" | "explain"
    subject_filter: str    # extracted subject, may be empty string

    # ── Retrieved context ────────────────────────────────────────────
    memory_context: str
    retrieved_docs: list[dict]
    graph_context: str
    reranked_context: list[dict]

    # ── Output ───────────────────────────────────────────────────────
    final_answer: str
    sources: list[dict]             # [{file, page, chunk_preview}]
    quiz_questions: list[dict]
    revision_plan: list[dict]

    # ── Metadata ─────────────────────────────────────────────────────
    error: str
