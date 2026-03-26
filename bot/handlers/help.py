"""Handler for /help command."""


def handle_help() -> str:
    """Handle /help command.

    Returns:
        List of available commands with descriptions.
    """
    return """📖 Available commands:

/start — Welcome message
/help — Show this help message
/health — Check if the backend is running
/labs — List all available labs
/scores <lab> — Show pass rates for a specific lab (e.g., /scores lab-04)

You can also ask questions in plain text, like:
- "what labs are available?"
- "show me scores for lab 4"
- "which lab has the lowest pass rate?"
"""
