"""Handler for general queries (intent routing with LLM)."""

from services.llm_client import LLMClient
from services.tools import get_tool_definitions, get_system_prompt
from config import load_config


def handle_general_query(query: str) -> str:
    """Handle general queries using LLM-powered intent routing.

    Args:
        query: The user's natural language query.

    Returns:
        Response text from the LLM after executing necessary tool calls.
    """
    config = load_config()

    # Check if LLM is configured
    llm_api_key = config.get("LLM_API_KEY", "")
    llm_base_url = config.get("LLM_API_BASE_URL", "")
    llm_model = config.get("LLM_API_MODEL", "coder-model")

    if not llm_api_key or not llm_base_url:
        return (
            "⚠️ LLM is not configured. Please set LLM_API_KEY and LMS_API_BASE_URL "
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
