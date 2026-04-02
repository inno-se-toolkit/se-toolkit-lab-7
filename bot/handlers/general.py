<<<<<<< HEAD
"""Handler for general queries (intent routing with LLM)."""

from services.llm_client import LLMClient
from services.tools import get_tool_definitions, get_system_prompt
from config import load_config


def handle_general_query(query: str) -> str:
    """Handle general queries using LLM-powered intent routing.
=======
"""Handler for general queries (intent routing).

This is a placeholder for Task 3 - Intent-Based Natural Language Routing.
"""


def handle_general_query(query: str) -> str:
    """Handle general text queries.
>>>>>>> f1706addcc06a7cd1f01a1fd5a68353c4d238cee

    Args:
        query: The user's natural language query.

    Returns:
<<<<<<< HEAD
        Response text from the LLM after executing necessary tool calls.
    """
    config = load_config()

    # Check if LLM is configured
    llm_api_key = config.get("LLM_API_KEY", "")
    llm_base_url = config.get("LLM_API_BASE_URL", "")
    llm_model = config.get("LLM_API_MODEL", "coder-model")

    if not llm_api_key or not llm_base_url:
        return (
            "⚠️ LLM is not configured. Please set LLM_API_KEY and LLM_API_BASE_URL "
            "in .env.bot.secret to enable natural language queries."
        )

    # Initialize LLM client
    llm = LLMClient(
        api_key=llm_api_key,
        base_url=llm_base_url,
        model=llm_model,
    )

    # Get tool definitions and system prompt
    tools = get_tool_definitions()
    system_prompt = get_system_prompt()

    # Route the query through the LLM
    response = llm.chat_with_tools(
        user_message=query,
        tools=tools,
        system_prompt=system_prompt,
    )

    return response
=======
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
>>>>>>> f1706addcc06a7cd1f01a1fd5a68353c4d238cee
