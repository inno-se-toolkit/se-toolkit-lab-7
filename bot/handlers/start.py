"""Handler for /start command."""


def handle_start() -> str:
    """Handle /start command.

    Returns:
        Welcome message with bot capabilities overview.
    """
    return (
        "👋 Welcome to SE Toolkit Bot!\n\n"
        "I can help you with:\n"
        "• Viewing your lab scores\n"
        "• Checking backend health\n"
        "• Getting help with commands\n\n"
        "Use /help to see all available commands."
    )
