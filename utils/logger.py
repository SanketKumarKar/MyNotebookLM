"""Loguru-based logging configuration for MyNotebookLM."""

import sys
from loguru import logger
from config.settings import settings

# Remove default handler
logger.remove()

# Add custom handler with configured level
logger.add(
    sys.stderr,
    level=settings.log_level,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
        "<level>{message}</level>"
    ),
    colorize=True,
)

# File logger for debugging
logger.add(
    "logs/mynotebooklm.log",
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} — {message}",
)


def get_logger(name: str = "mynotebooklm"):
    """Return a contextualized logger instance."""
    return logger.bind(name=name)
