"""Handler for /start command."""


def handle_start() -> str:
    """Handle /start command.

    Returns:
        Welcome message with bot name.
    """
    return """👋 Welcome to the LMS Bot!

I can help you check lab status, scores, and more.

Use /help to see available commands, or just ask me a question like:
- "what labs are available?"
- "show me scores for lab 4"
"""
