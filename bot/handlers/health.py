"""Handler for /health command."""


def handle_health(user_input: str = "") -> str:
    """Handle the /health command.
    
    Checks if the backend service is accessible.
    
    Args:
        user_input: Optional input from user (not used for /health)
        
    Returns:
        Health status message
    """
    # TODO: Implement actual health check in Task 2
    # For now, return a placeholder
    return (
        "✅ Bot Status: Running\n"
        "🔗 Backend: Connected\n"
        "📊 Database: Available\n"
        "🤖 LLM Service: Ready\n\n"
        "All systems operational!"
    )
