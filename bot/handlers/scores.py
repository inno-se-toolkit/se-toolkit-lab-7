"""Handler for /scores command."""


def handle_scores(lab_name: str = "") -> str:
    """Handle /scores command.

    Args:
        lab_name: The lab identifier (e.g., 'lab-04'). If empty, prompts user to specify a lab.

    Returns:
        Score information for the specified lab (placeholder for Task 2).
    """
    # Placeholder - will be implemented in Task 2
    if lab_name:
        return f"📊 Scores for {lab_name}: Not implemented yet (placeholder)"
    return "📊 Scores: Please specify a lab (e.g., /scores lab-04)"
