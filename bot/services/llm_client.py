"""LLM service with tool calling support."""

import json
import httpx
from typing import Any


class LLMClient:
    """Client for LLM API with tool calling support.

    Supports OpenAI-compatible APIs including Qwen Code.
    """

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    def get_tool_schemas(self) -> list[dict[str, Any]]:
        """Return tool schemas for LLM function calling.

        These 9 tools cover all backend analytics endpoints.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_items",
                    "description": "Get list of all labs and tasks. Use this to find available labs or get lab IDs.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_learners",
                    "description": "Get list of enrolled students and their groups. Use for questions about student enrollment.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_pass_rates",
                    "description": "Get per-task average scores and attempt counts for a specific lab. Use for questions about task difficulty or pass rates.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_scores",
                    "description": "Get score distribution (4 buckets) for a lab. Use for questions about score ranges.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_timeline",
                    "description": "Get submissions timeline (submissions per day) for a lab. Use for questions about submission patterns over time.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_groups",
                    "description": "Get per-group performance scores and student counts for a lab. Use for comparing groups.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_learners",
                    "description": "Get top N learners by score for a lab. Use for leaderboard questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of top learners to return (default: 5)",
                                "default": 5,
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_completion_rate",
                    "description": "Get completion rate percentage for a lab. Use for questions about how many students finished.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {
                                "type": "string",
                                "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                            },
                        },
                        "required": ["lab"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "trigger_sync",
                    "description": "Trigger ETL sync to refresh data from autochecker. Use when data seems outdated.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
        ]

    async def chat_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_iterations: int = 5,
    ) -> str:
        """Chat with LLM using tool calling loop.

        Args:
            messages: Conversation history with user messages.
            tools: List of tool schemas for function calling.
            max_iterations: Maximum tool call iterations to prevent loops.

        Returns:
            Final response from LLM after tool execution.
        """
        conversation = messages.copy()

        for iteration in range(max_iterations):
            # Call LLM
            response = await self._call_llm(conversation, tools)

            # Check if LLM wants to call tools
            if not response.get("tool_calls"):
                # No tool calls - return final answer
                return response.get("content", "I don't have enough information to answer.")

            # Execute tool calls
            tool_results = []
            for tool_call in response["tool_calls"]:
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"]["arguments"])

                # Execute the tool
                result = await self._execute_tool(func_name, func_args)
                tool_results.append({
                    "tool_call_id": tool_call["id"],
                    "name": func_name,
                    "result": result,
                })

            # Add tool results to conversation
            conversation.append(response)

            for tool_result in tool_results:
                conversation.append({
                    "role": "tool",
                    "tool_call_id": tool_result["tool_call_id"],
                    "name": tool_result["name"],
                    "content": json.dumps(tool_result["result"], ensure_ascii=False),
                })

        # If we reach max iterations, ask LLM to summarize
        conversation.append({
            "role": "system",
            "content": "Please provide a final answer based on the tool results above.",
        })

        final_response = await self._call_llm(conversation, [])
        return final_response.get("content", "I encountered an error processing your request.")

    async def _call_llm(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Call LLM API and return response."""
        system_prompt = """You are a helpful assistant for a Learning Management System.
You have access to backend API tools to fetch real data about labs, students, and scores.

When answering questions:
1. Think step by step about what data you need
2. Call the appropriate tools to fetch that data
3. Use the tool results to provide an accurate, helpful answer
4. If the user asks about multiple things, make multiple tool calls
5. Always base your answers on actual data from tools, not assumptions

Available tools:
- get_items: List all labs and tasks
- get_learners: List enrolled students
- get_pass_rates: Get task scores for a lab
- get_scores: Get score distribution for a lab
- get_timeline: Get submission timeline
- get_groups: Get per-group performance
- get_top_learners: Get top students leaderboard
- get_completion_rate: Get completion percentage
- trigger_sync: Refresh data from autochecker
"""

        payload = {
            "model": self._model,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "temperature": 0.7,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        response = await self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]

    async def _execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool by calling the backend API.

        This method should be overridden or configured with actual API client.
        For now, returns a placeholder that will be replaced by the bot.
        """
        # This will be replaced by actual API client in the bot
        return {"error": f"Tool {name} not configured"}
