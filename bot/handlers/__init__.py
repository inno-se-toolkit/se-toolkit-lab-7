"""Command handlers - pure functions that take input and return text.

These handlers have no dependency on Telegram. They can be called from:
- --test mode (CLI)
- Unit tests
- Telegram bot
"""


def handle_start(args: str) -> str:
    """Handle /start command."""
    return "Welcome to the LMS Bot! Use /help to see available commands."


def handle_help(args: str) -> str:
    """Handle /help command."""
    return """Available commands:
/start - Welcome message
/help - Show this help message
/health - Check backend status
/labs - List available labs
/scores <lab_id> - Get scores for a lab"""


def handle_health(args: str) -> str:
    """Handle /health command."""
    return "Backend status: OK (placeholder)"


def handle_labs(args: str) -> str:
    """Handle /labs command."""
    return "Available labs: lab-01, lab-02, lab-03, lab-04 (placeholder)"


def handle_scores(args: str) -> str:
    """Handle /scores command."""
    if not args.strip():
        return "Please specify a lab ID. Usage: /scores lab-04"
    return f"Scores for {args}: Not implemented yet (placeholder)"
