"""Command handlers for the LMS Telegram bot."""

from handlers.data.lms_queries import (
    check_health,
    handle_labs as handle_labs_impl,
    handle_scores as handle_scores_impl,
)


def handle_start() -> str:
    """Handle /start command."""
    return """👋 Welcome to the LMS Bot!

I can help you with:
• /help - Show all available commands
• /health - Check backend status
• /labs - List available labs
• /scores <lab> - Get scores for a lab

Send me any command to get started!"""


def handle_help() -> str:
    """Handle /help command."""
    return """📋 Available Commands:

🔧 System Commands:
/start - Welcome message
/help - Show this help
/health - Check backend status

📊 Data Commands:
/labs - List all available labs
/scores <lab> - Get scores for a specific lab

💬 Natural Language (Task 3):
Just type questions like:
"What labs are available?"
"Show me scores for lab-04"
"How am I doing?"

Send any command to get started!"""


def handle_health() -> str:
    """Handle /health command.

    Queries the LMS backend to check if it's healthy.
    """
    is_healthy, message = check_health()
    if is_healthy:
        return f"✅ {message}"
    return f"❌ {message}"


def handle_labs() -> str:
    """Handle /labs command.

    Fetches list of available labs from the LMS API.
    """
    return handle_labs_impl()


def handle_scores(lab: str = "") -> str:
    """Handle /scores command.

    Args:
        lab: Lab identifier to get scores for.
    """
    return handle_scores_impl(lab)