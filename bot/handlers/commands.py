"""Start command handler."""


def handle_start() -> str:
    """Handle /start command."""
    return """👋 Welcome to the LMS Bot!

I can help you with:
• /help - Show all available commands
• /health - Check system status
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
    """Handle /health command."""
    return "✅ Bot is running and ready to help!"


def handle_labs() -> str:
    """Handle /labs command."""
    return "📚 Available labs will be listed here (implemented in Task 2)"


def handle_scores(lab: str = "") -> str:
    """Handle /scores command."""
    if not lab:
        return "❌ Please specify a lab: /scores <lab-name>"
    return f"📊 Scores for {lab} will be shown here (implemented in Task 2)"