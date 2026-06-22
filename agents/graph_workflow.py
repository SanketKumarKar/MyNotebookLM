"""LangGraph StateGraph assembly — the central orchestration pipeline."""

from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.query_analyzer import query_analyzer_node
from agents.memory_agent import memory_agent_node
from agents.retriever_agent import retriever_agent_node
from agents.graph_agent import graph_agent_node
from agents.reranker_agent import reranker_agent_node
from agents.reasoning_agent import reasoning_agent_node
from agents.quiz_agent import quiz_agent_node
from agents.revision_agent import revision_agent_node
from agents.memory_updater import memory_updater_node


def route_by_intent(state: AgentState) -> str:
    """Route to the appropriate response agent based on classified intent."""
    intent = state.get("intent", "question")
    if intent == "quiz":
        return "quiz_agent"
    elif intent == "revision":
        return "revision_agent"
    else:
        # question, explain, summary all go to reasoning
        return "reasoning_agent"


def build_workflow():
    """
    Build and compile the LangGraph pipeline:

        query_analyzer → memory_agent → retriever_agent → graph_agent → reranker_agent
              ↓ (conditional by intent)
        reasoning_agent | quiz_agent | revision_agent
              ↓
        memory_updater → END
    """
    workflow = StateGraph(AgentState)

    # Register all nodes
    workflow.add_node("query_analyzer", query_analyzer_node)
    workflow.add_node("memory_agent", memory_agent_node)
    workflow.add_node("retriever_agent", retriever_agent_node)
    workflow.add_node("graph_agent", graph_agent_node)
    workflow.add_node("reranker_agent", reranker_agent_node)
    workflow.add_node("reasoning_agent", reasoning_agent_node)
    workflow.add_node("quiz_agent", quiz_agent_node)
    workflow.add_node("revision_agent", revision_agent_node)
    workflow.add_node("memory_updater", memory_updater_node)

    # Set entry point
    workflow.set_entry_point("query_analyzer")

    # Linear flow: analyze → memory → retrieve → graph → rerank
    workflow.add_edge("query_analyzer", "memory_agent")
    workflow.add_edge("memory_agent", "retriever_agent")
    workflow.add_edge("retriever_agent", "graph_agent")
    workflow.add_edge("graph_agent", "reranker_agent")

    # Conditional routing after reranking
    workflow.add_conditional_edges(
        "reranker_agent",
        route_by_intent,
        {
            "reasoning_agent": "reasoning_agent",
            "quiz_agent": "quiz_agent",
            "revision_agent": "revision_agent",
        },
    )

    # All response agents feed into memory updater
    workflow.add_edge("reasoning_agent", "memory_updater")
    workflow.add_edge("quiz_agent", "memory_updater")
    workflow.add_edge("revision_agent", "memory_updater")

    # Memory updater is the terminal node
    workflow.add_edge("memory_updater", END)

    return workflow.compile()


# Compiled graph — import this singleton
mynotebooklm_graph = build_workflow()
