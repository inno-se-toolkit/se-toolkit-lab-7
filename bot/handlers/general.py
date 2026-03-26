"""Handler for general queries (intent routing).

Uses LLM-powered intent routing for natural language queries.
"""

import asyncio

from handlers.intent_router import handle_general_query as llm_route


def handle_general_query(query: str) -> str:
    """Handle general text queries using LLM intent routing.

    Args:
        query: The user's natural language query.

    Returns:
        Response based on intent and tool results.
    """
    return asyncio.run(llm_route(query, debug=True))
