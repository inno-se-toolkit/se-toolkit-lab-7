"""Handler for /start command with inline keyboard buttons."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def handle_start() -> tuple[str, InlineKeyboardMarkup]:
    """Handle /start command with inline keyboard buttons.

    Returns:
        Tuple of (welcome message text, inline keyboard markup).
    """
    text = (
        "👋 Welcome to SE Toolkit Bot!\n\n"
        "I can help you with:\n"
        "• Viewing lab scores and pass rates\n"
        "• Comparing groups and students\n"
        "• Finding top performers\n"
        "• Checking submission timelines\n\n"
        "Try asking me questions like:\n"
        "• \"what labs are available?\"\n"
        "• \"which lab has the lowest pass rate?\"\n"
        "• \"show me top 5 students in lab-04\"\n"
        "• \"how are groups doing in lab-03?\"\n\n"
        "Or use /help to see all commands."
    )

    # Create inline keyboard with common queries
    keyboard = [
        [
            InlineKeyboardButton("📋 What labs?", callback_data="query_what_labs"),
            InlineKeyboardButton("📊 Lowest pass rate", callback_data="query_lowest_pass"),
        ],
        [
            InlineKeyboardButton("🏆 Top students", callback_data="query_top_students"),
            InlineKeyboardButton("👥 Group comparison", callback_data="query_groups"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    return text, reply_markup


def handle_start_text_only() -> str:
    """Handle /start command - text only version (for test mode).

    Returns:
        Welcome message text.
    """
    text, _ = handle_start()
    return text
