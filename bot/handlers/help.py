"""Handler for /help command."""


def handle_help(user_input: str = "") -> str:
    """Handle the /help command.
    
    Args:
        user_input: Optional input from user (not used for /help)
        
    Returns:
        Help message with available commands
    """
    return (
        "📚 SE Toolkit Lab 7 - Help\n\n"
        "Commands:\n"
        "/start - Welcome message and bot introduction\n"
        "/help - Show this help message\n"
        "/health - Check if backend service is running\n"
        "/labs - List all available labs\n"
        "/scores <lab-name> - Get your scores for a specific lab\n\n"
        "Natural language queries (Task 3):\n"
        "• what labs are available\n"
        "• show my scores for lab-04\n"
        "• how many submissions did I make\n"
        "• what is my average score\n\n"
        "For more information, check the course repository."
    )
