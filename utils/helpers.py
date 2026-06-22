"""Miscellaneous utility functions for MyNotebookLM."""

from datetime import datetime, timezone
import hashlib
import re


def utcnow_iso() -> str:
    """Return current UTC timestamp as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def truncate(text: str, max_len: int = 500) -> str:
    """Truncate text to max_len characters, appending '…' if trimmed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def stable_hash(text: str) -> str:
    """Return a stable hex digest for deduplication / ID generation."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def clean_text(text: str) -> str:
    """Normalize whitespace and strip control characters."""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def file_extension(filename: str) -> str:
    """Return lowercase file extension without the dot."""
    parts = filename.rsplit(".", 1)
    return parts[-1].lower() if len(parts) > 1 else ""


def chunk_list(lst: list, size: int) -> list[list]:
    """Split a list into sublists of *size*."""
    return [lst[i : i + size] for i in range(0, len(lst), size)]
