"""
Command handlers — pure functions that take input and return text.

These handlers have NO dependency on Telegram. They can be called from:
- --test mode (direct function calls)
- Unit tests
- Telegram bot (via aiogram)

This is separation of concerns: the same logic works regardless of transport.
"""

from .commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from .intent_router import route as route_intent

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "route_intent",
]
