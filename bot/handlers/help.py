"""Handler for /help command."""


def handle_help() -> str:
    """Handle /help command.

    Returns:
        List of available commands with descriptions.
    """
    return (
        "📚 Available commands:\n\n"
        "/start - Welcome message\n"
        "/help - Show this help message\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores <lab> - View scores for a specific lab"
    )
