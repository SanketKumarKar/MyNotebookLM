"""Mem0 memory client — cloud API for persistent user learning memory."""

from mem0 import MemoryClient
from config.settings import settings
from utils.logger import get_logger

log = get_logger("mem0_client")


class MyNotebookMemory:
    """Wrapper around Mem0 cloud API for user learning context."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        if not settings.mem0_api_key:
            raise ValueError(
                "MEM0_API_KEY is required. Get one from https://app.mem0.ai"
            )
        self.client = MemoryClient(api_key=settings.mem0_api_key)
        log.info(f"Mem0 client initialized for user: {user_id}")

    def add_interaction(self, messages: list[dict], metadata: dict | None = None):
        """Persist a conversation turn to Mem0."""
        try:
            self.client.add(messages, user_id=self.user_id, metadata=metadata or {})
            log.debug(f"Memory added for user {self.user_id}")
        except Exception as e:
            log.warning(f"Failed to add memory: {e}")

    def search_relevant_memories(self, query: str, limit: int = 5) -> list[dict]:
        """Semantic search over stored memories."""
        try:
            results = self.client.search(query, user_id=self.user_id, limit=limit)
            # MemoryClient.search returns a list of dicts directly
            if isinstance(results, dict):
                return results.get("results", [])
            return results if isinstance(results, list) else []
        except Exception as e:
            log.warning(f"Memory search failed: {e}")
            return []

    def get_all_memories(self) -> list[dict]:
        """Fetch entire memory profile for this user."""
        try:
            results = self.client.get_all(user_id=self.user_id)
            if isinstance(results, dict):
                return results.get("results", [])
            return results if isinstance(results, list) else []
        except Exception as e:
            log.warning(f"Failed to fetch all memories: {e}")
            return []

    def update_weakness(self, concept: str, confidence_delta: float):
        """Record a weakness or strength update in memory."""
        direction = "struggles with" if confidence_delta < 0 else "has improved in"
        msg = f"User {direction} the concept: {concept}"
        try:
            self.client.add(
                [{"role": "system", "content": msg}],
                user_id=self.user_id,
                metadata={
                    "type": "weakness_tracker",
                    "concept": concept,
                    "delta": confidence_delta,
                },
            )
        except Exception as e:
            log.warning(f"Failed to update weakness: {e}")

    def get_learning_profile(self) -> str:
        """Build a text summary of the user's learning profile from memory."""
        memories = self.get_all_memories()
        if not memories:
            return "No learning profile built yet."
        lines = []
        for m in memories:
            memory_text = m.get("memory", "") if isinstance(m, dict) else str(m)
            if memory_text:
                lines.append(f"- {memory_text}")
        return "\n".join(lines) if lines else "No learning profile built yet."
