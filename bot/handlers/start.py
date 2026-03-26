"""Handler for /start command."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard for quick actions."""
    keyboard = [
        [
            InlineKeyboardButton("📚 Labs", callback_data="labs"),
            InlineKeyboardButton("📊 Scores", callback_data="scores_help"),
        ],
        [
            InlineKeyboardButton("🔍 Health Check", callback_data="health"),
            InlineKeyboardButton("❓ Help", callback_data="help"),
        ],
        [
            InlineKeyboardButton("🏆 Top Lab", callback_data="top_lab"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def handle_start() -> str:
    """Handle /start command.

    Returns:
        Welcome message with bot name.
    """
    return """👋 Welcome to the LMS Bot!

I can help you check lab status, scores, and more.

Use the buttons below or try commands like:
• /labs — List all available labs
• /scores lab-04 — Show pass rates
• /health — Check backend status

Or just ask me a question like:
• "what labs are available?"
• "which lab has the lowest pass rate?"
• "show me top 5 students in lab 4"
"""
