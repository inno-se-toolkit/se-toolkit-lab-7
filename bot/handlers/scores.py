"""Handler for /scores command."""


def handle_scores(user_input: str = "") -> str:
    """Handle the /scores command.
    
    Shows scores for a specific lab.
    
    Args:
        user_input: Lab name or ID (e.g., "lab-04")
        
    Returns:
        Scores information for the specified lab
    """
    if not user_input.strip():
        return (
            "⚠️ Please specify a lab name.\n\n"
            "Usage: /scores lab-04\n"
            "Available labs: lab-01, lab-02, lab-03, lab-04, lab-05, lab-06, lab-07"
        )
    
    # TODO: Implement actual scores fetching in Task 2
    # For now, return a placeholder
    lab_name = user_input.strip().upper()
    return (
        f"📊 Scores for {lab_name}:\n\n"
        f"Status: In Progress\n"
        "Score: --\n"
        "Submissions: --\n\n"
        "(Real scores will be fetched from backend in Task 2)"
    )
