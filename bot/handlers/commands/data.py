"""Data command handlers."""

from bot.handlers.health import handle_health
from bot.handlers.labs import handle_labs
from bot.handlers.scores import handle_scores

__all__ = ["handle_health", "handle_labs", "handle_scores"]
