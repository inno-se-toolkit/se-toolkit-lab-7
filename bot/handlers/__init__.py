"""Command handlers for the LMS bot.

These handlers are testable without Telegram - they just take input and return text.
"""

from .commands import handle_start, handle_help, handle_health, handle_labs, handle_scores

__all__ = ["handle_start", "handle_help", "handle_health", "handle_labs", "handle_scores"]