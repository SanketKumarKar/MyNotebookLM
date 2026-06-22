"""Quiz agent node: generate MCQ and short-answer questions from context."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm import llm
from agents.state import AgentState
from utils.logger import get_logger

log = get_logger("quiz_agent")

_prompt = ChatPromptTemplate.from_messages([
    ("system", """Generate {num_questions} quiz questions from the study material below.

Material:
{context}

Subject: {subject}

Return ONLY valid JSON, no preamble, no markdown fences:
{{
    "questions": [
        {{
            "type": "mcq",
            "question": "...",
            "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
            "correct_answer": "A",
            "explanation": "...",
            "concept": "concept name",
            "difficulty": "beginner|intermediate|advanced"
        }},
        {{
            "type": "short_answer",
            "question": "...",
            "expected_answer": "...",
            "concept": "concept name",
            "difficulty": "beginner|intermediate|advanced"
        }}
    ]
}}

Mix MCQ and short answer. Every question must have a "concept" field.
"""),
    ("human", "Generate the quiz now."),
])

_chain = _prompt | llm | JsonOutputParser()


def quiz_agent_node(state: AgentState) -> AgentState:
    """Generate quiz questions based on retrieved context."""
    try:
        context = "\n\n".join(
            d.get("content", "") for d in state.get("reranked_context", [])
        ) or "General knowledge quiz."

        result = _chain.invoke({
            "num_questions": 5,
            "context": context[:3000],  # trim to avoid overloading local model
            "subject": state.get("subject_filter") or "General",
        })

        state["quiz_questions"] = result.get("questions", [])
        state["final_answer"] = f"📝 Generated {len(state['quiz_questions'])} quiz questions."
        log.info(f"Generated {len(state['quiz_questions'])} quiz questions")
    except Exception as e:
        log.error(f"Quiz generation failed: {e}")
        state["quiz_questions"] = []
        state["final_answer"] = f"Quiz generation failed: {e}"
        state["error"] = str(e)
    return state
