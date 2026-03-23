"""
Command handler implementations.

Each handler is a pure function: it takes input and returns text.
No Telegram dependencies here - this makes handlers testable.
"""


def handle_start() -> str:
    """Handle /start command - returns welcome message."""
    return "Welcome! I'm your LMS assistant bot. Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command - lists available commands."""
    return "Available commands: /start, /help, /health, /labs, /scores"


def handle_health() -> str:
    """Handle /health command - checks backend status."""
    return "Backend status: OK (placeholder)"


def handle_labs() -> str:
    """Handle /labs command - lists available labs."""
    return "Available labs: lab-01, lab-02, lab-03, lab-04 (placeholder)"


def handle_scores(query: str = "") -> str:
    """Handle /scores command - shows per-task pass rates."""
    if query:
        return f"Scores for {query}: Task 1: 80%, Task 2: 75% (placeholder)"
    return "Usage: /scores <lab-name>. Example: /scores lab-04"


def get_handler(command: str):
    """
    Route command to appropriate handler.
    
    Returns the handler function for a given command string,
    or None if the command is not recognized.
    """
    handlers = {
        "/start": handle_start,
        "/help": handle_help,
        "/health": handle_health,
        "/labs": handle_labs,
        "/scores": handle_scores,
    }
    return handlers.get(command)
