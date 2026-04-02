"""Intent router for natural language queries using LLM."""

import asyncio
import json
from typing import Any

from config import load_config
from services.api_client import LMSAPIClient
from services.llm_client import LLMClient


class IntentRouter:
    """Route natural language queries to backend tools via LLM."""

    def __init__(self) -> None:
        self.config = load_config()
        self.api_client = LMSAPIClient(
            base_url=self.config.get("LMS_API_BASE_URL", "http://localhost:42002"),
            api_key=self.config.get("LMS_API_KEY", ""),
        )
        self.llm_client = LLMClient(
            api_key=self.config.get("LLM_API_KEY", ""),
            base_url=self.config.get("LLM_API_BASE_URL", "http://localhost:42005/v1"),
            model=self.config.get("LLM_API_MODEL", "coder-model"),
        )
        # Bind API client methods to LLM client
        self._bind_tools()

    def _bind_tools(self) -> None:
        """Bind actual API methods to LLM client tool execution."""
        self.llm_client._execute_tool = self._execute_tool

    async def _execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool by calling the backend API."""
        try:
            if name == "get_items":
                return await self.api_client.get_items()
            elif name == "get_learners":
                return await self.api_client.get_learners()
            elif name == "get_pass_rates":
                return await self.api_client.get_pass_rates(arguments.get("lab", ""))
            elif name == "get_scores":
                return await self.api_client.get_scores(arguments.get("lab", ""))
            elif name == "get_timeline":
                return await self.api_client.get_timeline(arguments.get("lab", ""))
            elif name == "get_groups":
                return await self.api_client.get_groups(arguments.get("lab", ""))
            elif name == "get_top_learners":
                return await self.api_client.get_top_learners(
                    arguments.get("lab", ""),
                    arguments.get("limit", 5),
                )
            elif name == "get_completion_rate":
                return await self.api_client.get_completion_rate(arguments.get("lab", ""))
            elif name == "trigger_sync":
                return await self.api_client.trigger_sync()
            else:
                return {"error": f"Unknown tool: {name}"}
        except Exception as e:
            return {"error": str(e)}

    async def route(self, query: str, debug: bool = False) -> str:
        """Route a natural language query to the appropriate tool.

        Args:
            query: User's natural language question.
            debug: If True, print debug info to stderr.

        Returns:
            Response based on intent and tool results.
        """
        import sys
        
        # Check for LLM availability
        if not self.config.get("LLM_API_KEY") or not self.config.get("LLM_API_BASE_URL"):
            if debug:
                print("[router] LLM not configured, using fallback", file=sys.stderr)
            return self._fallback_response(query)

        try:
            messages = [{"role": "user", "content": query}]
            tools = self.llm_client.get_tool_schemas()

            if debug:
                print(f"[router] Processing query: {query}", file=sys.stderr)
                print(f"[router] LLM URL: {self.config.get('LLM_API_BASE_URL')}", file=sys.stderr)
                print(f"[router] LLM model: {self.config.get('LLM_API_MODEL')}", file=sys.stderr)

            response = await self.llm_client.chat_with_tools(messages, tools, debug=debug)

            if debug:
                print(f"[router] Final response: {response[:200]}", file=sys.stderr)

            return response
        except Exception as e:
            if debug:
                print(f"[router] Error: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
            return self._fallback_response(query)
        finally:
            await self.api_client.close()
            await self.llm_client.close()

    def _fallback_response(self, query: str) -> str:
        """Return a fallback response when LLM is unavailable.

        Uses simple keyword matching as a last resort.
        """
        query_lower = query.lower().strip()

        # Greetings
        if any(g in query_lower for g in ["hello", "hi", "hey", "greetings"]):
            return """👋 Hello! I'm your LMS assistant.

I can help you with:
- Viewing available labs
- Checking pass rates and scores
- Comparing group performance
- Finding top learners

Just ask me a question like "what labs are available?" or "show me scores for lab 4"."""

        # Gibberish or unclear
        if len(query_lower) < 3 or query_lower in ["asdfgh", "test", "abc"]:
            return """🤔 I'm not sure I understand. Here's what I can help with:

• List available labs
• Show pass rates for a lab
• Compare group performance
• Find top learners
• Check submission timelines

Try asking something like "which lab has the lowest pass rate?" or use /help for commands."""

        # Lab mention without clear intent
        lab_match = __import__("re").search(r"lab[- ]?(\d+)", query_lower)
        if lab_match:
            lab_num = lab_match.group(1)
            return f"""📊 You mentioned lab {lab_num}. I can help you with:

• Pass rates for each task
• Score distribution
• Top learners in that lab
• Group comparisons
• Submission timeline

Just ask specifically what you'd like to know about lab {lab_num}!"""

        # Default fallback
        return """🤔 I'm still learning to understand natural language questions.

For now, try using slash commands:
• /labs — List all labs
• /scores lab-04 — Show pass rates
• /health — Check backend status

Or ask me specific questions about labs, scores, or students!"""


async def handle_general_query(query: str, debug: bool = False) -> str:
    """Handle general text queries using LLM intent routing.

    Args:
        query: The user's natural language query.
        debug: If True, print debug info to stderr.

    Returns:
        Response based on intent and tool results.
    """
    router = IntentRouter()
    return await router.route(query, debug)
