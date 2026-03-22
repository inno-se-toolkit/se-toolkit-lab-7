"""Command handlers organized by category.

This module re-exports handlers for backward compatibility.
"""

from bot.handlers.start import handle_start
from bot.handlers.help import handle_help
from bot.handlers.health import handle_health
from bot.handlers.labs import handle_labs
from bot.handlers.scores import handle_scores

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
]
