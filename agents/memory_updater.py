"""Memory updater node: persist the current interaction to Mem0."""

from memory.mem0_client import MyNotebookMemory
from agents.state import AgentState
from utils.logger import get_logger

log = get_logger("memory_updater")


def memory_updater_node(state: AgentState) -> AgentState:
    """Save the conversation turn to Mem0 for future personalization."""
    try:
        mem = MyNotebookMemory(state["user_id"])
        messages = [
            {"role": "user", "content": state["query"]},
            {"role": "assistant", "content": state.get("final_answer", "")},
        ]
        metadata = {
            "intent": state.get("intent", "question"),
            "subject": state.get("subject_filter", ""),
            "sources": [s.get("file") for s in state.get("sources", [])],
        }
        mem.add_interaction(messages, metadata=metadata)
        log.debug("Memory updated successfully")
    except Exception as e:
        log.warning(f"Memory update failed: {e}")
    return state
