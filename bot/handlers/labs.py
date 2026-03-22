"""Handler for /labs command."""


def handle_labs(user_input: str = "") -> str:
    """Handle the /labs command.
    
    Lists all available labs.
    
    Args:
        user_input: Optional input from user (not used for /labs)
        
    Returns:
        List of available labs
    """
    # TODO: Implement actual labs listing in Task 2
    # For now, return a placeholder
    return (
        "📋 Available Labs:\n\n"
        "• Lab 01 – Products, Architecture & Roles\n"
        "• Lab 02 – Requirements & Use Cases\n"
        "• Lab 03 – Domain Modeling\n"
        "• Lab 04 – Architecture & Design\n"
        "• Lab 05 – Implementation\n"
        "• Lab 06 – Testing & CI/CD\n"
        "• Lab 07 – Telegram Bot & Analytics\n\n"
        "Use /scores <lab-name> to see your scores for a specific lab."
    )
