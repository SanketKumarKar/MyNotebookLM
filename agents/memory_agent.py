"""Memory agent node: fetch relevant Mem0 memories for the current query."""

from memory.mem0_client import MyNotebookMemory
from agents.state import AgentState
from utils.logger import get_logger

log = get_logger("memory_agent")


def memory_agent_node(state: AgentState) -> AgentState:
    """Retrieve past learning context from Mem0."""
    try:
        mem = MyNotebookMemory(state["user_id"])
        memories = mem.search_relevant_memories(state["query"], limit=5)
        if memories:
            lines = []
            for m in memories:
                text = m.get("memory", "") if isinstance(m, dict) else str(m)
                if text:
                    lines.append(f"- {text}")
            if lines:
                state["memory_context"] = (
                    "User's learning context from past sessions:\n" + "\n".join(lines)
                )
            else:
                state["memory_context"] = "No prior learning context found."
        else:
            state["memory_context"] = "No prior learning context found."
    except Exception as e:
        log.warning(f"Memory agent error: {e}")
        state["memory_context"] = ""
    return state
