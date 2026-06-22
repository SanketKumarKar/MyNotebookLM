"""Graph agent node: traverse Neo4j for related concepts."""

from retrieval.graph_retriever import get_related_concepts
from ingestion.entity_extractor import extract_entities
from agents.state import AgentState
from utils.logger import get_logger

log = get_logger("graph_agent")


def graph_agent_node(state: AgentState) -> AgentState:
    """Extract concepts from query and find related concepts in Neo4j."""
    try:
        extraction = extract_entities(state["query"])
        concept_names = extraction.get("concepts", [])
        if concept_names:
            related = get_related_concepts(concept_names, depth=2)
            if related:
                lines = [
                    f"- {r['concept']} (subject: {r.get('subject', '?')}, "
                    f"chapter: {r.get('chapter', '?')})"
                    for r in related
                ]
                state["graph_context"] = (
                    "Related concepts from knowledge graph:\n" + "\n".join(lines)
                )
            else:
                state["graph_context"] = ""
        else:
            state["graph_context"] = ""
    except Exception as e:
        log.warning(f"Graph agent error: {e}")
        state["graph_context"] = ""
    return state
