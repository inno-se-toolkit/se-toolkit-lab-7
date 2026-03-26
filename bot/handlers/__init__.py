"""Command handlers for the Telegram bot.

Handlers are pure functions that take input and return text.
They have no dependency on Telegram - this makes them testable.
"""

from .start import handle_start
from .help import handle_help
from .health import handle_health
from .labs import handle_labs
from .scores import handle_scores
from .general import handle_general_query

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "handle_general_query",
]
