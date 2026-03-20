def handle_help(user_input: str = "") -> str:
    """Handle /help command."""
    return """Available commands:
/start - Welcome message
/help - Show this help
/health - Check backend status
/labs - List available labs
/scores <lab> - Get scores for a lab"""
