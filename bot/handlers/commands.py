def handle_start(user_input: str) -> str:
    """Handles /start command."""
    return "Welcome to the SE Toolkit Bot! Use /help to see available commands."

def handle_help(user_input: str) -> str:
    """Handles /help command."""
    return (
        "Available Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/health - Check backend status\n"
        "/scores <lab_id> - Get scores for a specific lab\n"
        "You can also ask natural language questions like 'what labs are available'"
    )

def handle_health(user_input: str) -> str:
    """Handles /health command."""
    # In Task 2, this will ping the backend API
    return "System Status: OK (Backend connection not yet implemented)"

def handle_scores(user_input: str) -> str:
    """Handles /scores command."""
    # Expecting input like "/scores lab-04"
    parts = user_input.split()
    if len(parts) < 2:
        return "Please specify a lab ID. Example: /scores lab-04"
    
    lab_id = parts[1]
    return f"Scores for {lab_id}: [Placeholder - API integration pending]"

def handle_natural_language(user_input: str) -> str:
    """Handles natural language queries (Task 3)."""
    text = user_input.lower()
    if "lab" in text and "available" in text:
        return "Available Labs: lab-01, lab-02, lab-03, lab-04 (Placeholder)"
    
    return "I'm not sure how to help with that yet. Try /help."