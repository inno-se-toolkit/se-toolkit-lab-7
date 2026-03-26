"""Handler for general queries (intent routing).

This is a placeholder for Task 3 - Intent-Based Natural Language Routing.
"""


def handle_general_query(query: str) -> str:
    """Handle general text queries.

    Args:
        query: The user's natural language query.

    Returns:
        Response based on intent (placeholder for Task 3).
    """
    # Placeholder - will be implemented in Task 3 with LLM routing
    query_lower = query.lower().strip()

    # Simple keyword-based fallback for testing
    if "hello" in query_lower or "hi" in query_lower:
        return "👋 Hello! Use /help to see what I can do, or ask me a question about your labs."

    if "lab" in query_lower and ("available" in query_lower or "list" in query_lower):
        return "📚 Use /labs to see all available labs."

    if "score" in query_lower or "pass rate" in query_lower:
        return "📊 Use /scores <lab> to see pass rates (e.g., /scores lab-04)."

    # Default fallback
    return f"""🤔 I heard: "{query}"

For now, I can respond to slash commands. Use /help to see what's available.

In Task 3, I'll learn to understand natural language questions!"""
