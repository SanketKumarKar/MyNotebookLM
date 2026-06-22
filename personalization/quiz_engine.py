"""Quiz session management — start quiz, submit answers, score results."""

from dataclasses import dataclass, field
from personalization.weakness_tracker import WeaknessTracker
from utils.logger import get_logger

log = get_logger("quiz_engine")


@dataclass
class QuizSession:
    """Tracks the state of an active quiz session."""

    user_id: str
    questions: list[dict] = field(default_factory=list)
    answers: dict = field(default_factory=dict)      # question_index → user_answer
    results: dict = field(default_factory=dict)       # question_index → bool (correct?)
    completed: bool = False

    @property
    def total(self) -> int:
        return len(self.questions)

    @property
    def answered(self) -> int:
        return len(self.answers)

    @property
    def score(self) -> int:
        return sum(1 for v in self.results.values() if v)


class QuizEngine:
    """Manage quiz sessions: creation, answering, grading."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.tracker = WeaknessTracker(user_id)

    def start_session(self, questions: list[dict]) -> QuizSession:
        """Create a new quiz session from generated questions."""
        session = QuizSession(user_id=self.user_id, questions=questions)
        log.info(f"Quiz session started: {len(questions)} questions")
        return session

    def submit_answer(self, session: QuizSession, question_index: int, user_answer: str) -> dict:
        """
        Submit an answer for a question and return grading result.

        Returns:
            {"correct": bool, "explanation": str, "correct_answer": str}
        """
        if question_index >= len(session.questions):
            return {"correct": False, "explanation": "Invalid question index", "correct_answer": ""}

        question = session.questions[question_index]
        session.answers[question_index] = user_answer

        q_type = question.get("type", "mcq")
        correct = False
        explanation = question.get("explanation", "")

        if q_type == "mcq":
            correct_letter = question.get("correct_answer", "").strip().upper()
            user_letter = user_answer.strip().upper()
            # Handle both "A" and "A. ..." formats
            if user_letter and correct_letter:
                correct = user_letter[0] == correct_letter[0]
        elif q_type == "short_answer":
            expected = question.get("expected_answer", "")
            correct = self.tracker.evaluate_short_answer(expected, user_answer)
        else:
            correct = False

        session.results[question_index] = correct

        # Track weakness/strength
        concept = question.get("concept", "Unknown")
        self.tracker.record_quiz_result(concept, correct)

        result = {
            "correct": correct,
            "explanation": explanation,
            "correct_answer": question.get("correct_answer", question.get("expected_answer", "")),
        }
        log.info(f"Q{question_index}: {'✓' if correct else '✗'} (concept: {concept})")
        return result

    def finalize_session(self, session: QuizSession) -> dict:
        """Mark session as complete and return summary stats."""
        session.completed = True
        return {
            "total": session.total,
            "answered": session.answered,
            "correct": session.score,
            "percentage": round(session.score / max(session.total, 1) * 100, 1),
            "weak_concepts": self.tracker.get_weak_concepts(),
        }
