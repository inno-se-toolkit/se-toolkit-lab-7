"""Handler for /start command."""


def handle_start(user_input: str = "") -> str:
    """Handle the /start command.
    
    Args:
        user_input: Optional input from user (not used for /start)
        
    Returns:
        Welcome message text
    """
    return (
        "👋 Welcome to the SE Toolkit Lab 7 Bot!\n\n"
        "I'm your assistant for tracking lab progress and scores.\n\n"
        "Available commands:\n"
        "/start - Show this welcome message\n"
        "/help - Show available commands\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores <lab> - Get scores for a specific lab\n\n"
        "You can also ask me questions like:\n"
        "• What labs are available?\n"
        "• Show my scores for lab-04\n"
        "• How am I doing in the course?"
    )
