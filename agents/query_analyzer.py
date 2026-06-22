"""Query analyzer node: classify intent and extract subject filter."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm import llm
from agents.state import AgentState

_prompt = ChatPromptTemplate.from_messages([
    ("system", """Classify the user's query intent and extract subject if mentioned.

Intents:
- question: factual or conceptual question
- explain: request for a detailed explanation
- quiz: user wants to be quizzed
- summary: user wants a summary
- revision: user wants a revision plan or schedule

Return ONLY valid JSON, no preamble:
{{"intent": "question|explain|quiz|summary|revision", "subject_filter": "subject name or empty string"}}
"""),
    ("human", "{query}")
])

_chain = _prompt | llm | JsonOutputParser()


def query_analyzer_node(state: AgentState) -> AgentState:
    """Classify user intent and optionally extract subject filter."""
    try:
        result = _chain.invoke({"query": state["query"]})
        state["intent"] = result.get("intent", "question")
        state["subject_filter"] = result.get("subject_filter", "")
    except Exception:
        state["intent"] = "question"
        state["subject_filter"] = ""
    return state
