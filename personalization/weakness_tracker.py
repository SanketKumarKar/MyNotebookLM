"""Track concept confidence scores based on quiz performance."""

from memory.mem0_client import MyNotebookMemory
from utils.llm import llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.logger import get_logger

log = get_logger("weakness_tracker")

_eval_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are grading a short-answer exam response. Reply with ONLY 'correct' or 'incorrect'."),
    ("human", "Expected: {expected}\nStudent answer: {student}"),
])
_eval_chain = _eval_prompt | llm | StrOutputParser()


class WeaknessTracker:
    """Track per-concept confidence based on quiz results."""

    def __init__(self, user_id: str):
        self.mem = MyNotebookMemory(user_id)

    def record_quiz_result(self, concept: str, correct: bool):
        """Update weakness memory for a concept based on quiz result."""
        delta = 0.1 if correct else -0.15
        self.mem.update_weakness(concept, delta)
        log.info(f"Weakness update: concept={concept}, correct={correct}, delta={delta}")

    def evaluate_short_answer(self, expected: str, student_answer: str) -> bool:
        """Use LLM to evaluate a short-answer response."""
        try:
            result = _eval_chain.invoke({
                "expected": expected,
                "student": student_answer,
            })
            return "correct" in result.lower()
        except Exception as e:
            log.warning(f"Short answer evaluation failed: {e}")
            return False

    def get_weak_concepts(self) -> list[str]:
        """Return concepts the user struggles with (from memory)."""
        memories = self.mem.get_all_memories()
        weak = set()
        for m in memories:
            text = m.get("memory", "") if isinstance(m, dict) else str(m)
            if "struggles with" in text:
                # Extract concept after "the concept: "
                if "the concept: " in text:
                    concept = text.split("the concept: ")[-1].strip()
                    weak.add(concept)
        return list(weak)

    def get_strong_concepts(self) -> list[str]:
        """Return concepts the user has improved in (from memory)."""
        memories = self.mem.get_all_memories()
        strong = set()
        for m in memories:
            text = m.get("memory", "") if isinstance(m, dict) else str(m)
            if "improved in" in text:
                if "the concept: " in text:
                    concept = text.split("the concept: ")[-1].strip()
                    strong.add(concept)
        return list(strong)
