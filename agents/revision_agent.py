"""Revision agent node: build a spaced repetition schedule."""

from retrieval.graph_retriever import get_all_subjects
from personalization.revision_scheduler import RevisionScheduler
from agents.state import AgentState
from datetime import datetime
from utils.logger import get_logger

log = get_logger("revision_agent")


def revision_agent_node(state: AgentState) -> AgentState:
    """Create a spaced-repetition revision schedule."""
    try:
        subjects = get_all_subjects()
        if state.get("subject_filter"):
            topics = [state["subject_filter"]]
        else:
            topics = subjects[:6] if subjects else ["General"]

        scheduler = RevisionScheduler()
        plan = scheduler.create_schedule(topics, start_date=datetime.now())
        state["revision_plan"] = plan
        state["final_answer"] = f"📅 Created revision schedule for {len(topics)} topic(s)."
        log.info(f"Revision plan created for {len(topics)} topics")
    except Exception as e:
        log.error(f"Revision plan failed: {e}")
        state["revision_plan"] = []
        state["final_answer"] = f"Revision plan generation failed: {e}"
        state["error"] = str(e)
    return state
