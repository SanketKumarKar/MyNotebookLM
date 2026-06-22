"""Reasoning agent node: generate a personalized, cited answer."""

from langchain_core.prompts import ChatPromptTemplate
from utils.llm import llm
from agents.state import AgentState
from utils.logger import get_logger

log = get_logger("reasoning_agent")

_system = """You are MyNotebookLM, an intelligent AI tutor powered by a knowledge graph and personal memory.
Your goal is to TEACH, not just answer. Personalize every response.

USER LEARNING CONTEXT:
{memory_context}

KNOWLEDGE GRAPH — RELATED CONCEPTS:
{graph_context}

RETRIEVED STUDY MATERIAL:
{context_text}

INSTRUCTIONS:
1. Use the learning context: if the user struggles with a concept, use extra detail, analogies, or dry-run examples.
2. Match complexity to what you know about the user's level (from memory context).
3. After every key factual claim, add a citation: [Source: <filename>, Page <N>]
4. If the topic has prerequisites (visible in graph context), briefly mention them.
5. End your response with a "**Key Takeaways**" bullet list (max 5 points).
6. If appropriate, suggest what to study next based on graph context.
7. Be concise — do not pad responses unnecessarily.
"""

_prompt = ChatPromptTemplate.from_messages([
    ("system", _system),
    ("human", "Chat history:\n{chat_history}\n\nCurrent question: {query}"),
])


def reasoning_agent_node(state: AgentState) -> AgentState:
    """Generate a personalized, context-rich answer with citations."""
    try:
        # Build numbered context from reranked documents
        context_parts = []
        for i, doc in enumerate(state.get("reranked_context", []), 1):
            context_parts.append(
                f"[{i}] {doc['content']}\n"
                f"    Source: {doc['source']}, Page: {doc['page']}"
            )
        context_text = "\n\n".join(context_parts) if context_parts else "No context retrieved."

        # Format recent chat history (last 3 turns = 6 messages)
        chat_hist = ""
        for msg in state.get("chat_history", [])[-6:]:
            role = getattr(msg, "type", "human")
            content = getattr(msg, "content", str(msg))
            chat_hist += f"{role}: {content}\n"

        response = llm.invoke(
            _prompt.format_messages(
                memory_context=state.get("memory_context", ""),
                graph_context=state.get("graph_context", ""),
                context_text=context_text,
                chat_history=chat_hist,
                query=state["query"],
            )
        )

        state["final_answer"] = response.content
        state["sources"] = [
            {
                "file": d.get("source", "Unknown"),
                "page": d.get("page", "?"),
                "preview": d.get("content", "")[:120] + "...",
            }
            for d in state.get("reranked_context", [])
        ]
    except Exception as e:
        log.error(f"Reasoning agent error: {e}")
        state["final_answer"] = f"I encountered an error generating a response: {e}"
        state["error"] = str(e)
    return state
