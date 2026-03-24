"""
LLM API client for tool-based intent routing.

Uses httpx for HTTP requests to the Qwen Code API (or compatible OpenAI-style API).
The LLM receives:
- User message
- Tool definitions (function schemas)
- System prompt

The LLM responds with tool calls, which the bot executes and feeds back.
"""

import json
from typing import Any

import httpx


class LLMClient:
    """Client for LLM API with tool calling support."""

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        """Initialize the LLM client.
        
        Args:
            base_url: LLM API base URL (e.g., http://localhost:42005/v1)
            api_key: API key for authentication
            model: Model name to use (e.g., 'coder-model')
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=60.0,
        )

    def chat_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        system_prompt: str,
    ) -> tuple[str, list[dict[str, Any]]]:
        """Send a chat message with tool definitions and get response.
        
        Args:
            messages: Conversation history (list of {role, content})
            tools: List of tool/function schemas
            system_prompt: System prompt to guide the LLM
            
        Returns:
            Tuple of (response_text, list_of_tool_calls)
        """
        # Build the request with system prompt
        all_messages = [{"role": "system", "content": system_prompt}] + messages
        
        try:
            response = self._client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": all_messages,
                    "tools": tools,
                    "tool_choice": "auto",
                },
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract the assistant message
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            
            # Check for tool calls
            tool_calls = message.get("tool_calls", [])
            content = message.get("content", "")
            
            return (content or "", tool_calls)
            
        except httpx.HTTPStatusError as e:
            return (f"LLM error: HTTP {e.response.status_code}. Check your API key and connection.", [])
        except httpx.ConnectError:
            return (f"LLM error: connection refused ({self.base_url}). Check that the LLM service is running.", [])
        except Exception as e:
            return (f"LLM error: {str(e)}.", [])

    def parse_tool_call(self, tool_call: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Parse a tool call from the LLM response.
        
        Args:
            tool_call: Tool call object from LLM response
            
        Returns:
            Tuple of (function_name, arguments_dict)
        """
        function = tool_call.get("function", {})
        name = function.get("name", "unknown")
        arguments_str = function.get("arguments", "{}")
        
        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError:
            arguments = {}
        
        return (name, arguments)
