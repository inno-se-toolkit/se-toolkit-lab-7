"""LLM client for intent-based natural language routing.

This client talks to the Qwen Code API (or any OpenAI-compatible endpoint)
and uses tool calling to route user queries to the appropriate backend APIs.
"""

import httpx
import json
import sys
from typing import Any


class LLMClient:
    """Client for LLM-powered intent routing with tool calling."""

    def __init__(self, api_key: str, base_url: str, model: str):
        """Initialize the LLM client.

        Args:
            api_key: API key for the LLM service.
            base_url: Base URL of the LLM API endpoint.
            model: Model name to use (e.g., 'coder-model').
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )

    def _debug_log(self, message: str) -> None:
        """Print debug message to stderr (visible in --test mode)."""
        print(message, file=sys.stderr)

    def chat_with_tools(
        self,
        user_message: str,
        tools: list[dict[str, Any]],
        system_prompt: str,
        max_iterations: int = 5,
    ) -> str:
        """Send a message to the LLM with tool definitions and execute tool calls.

        Args:
            user_message: The user's natural language query.
            tools: List of tool/function schemas for the LLM to choose from.
            system_prompt: System prompt to guide the LLM's behavior.
            max_iterations: Maximum number of tool-calling iterations.

        Returns:
            The LLM's final response text.
        """
        # Build the conversation history
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        iteration = 0
        while iteration < max_iterations:
            iteration += 1

            # Call the LLM
            response = self._client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": tools,
                    "tool_choice": "auto",
                },
            )

            if response.status_code == 401:
                self._debug_log("[tool] LLM error: HTTP 401 - token may be expired")
                return "LLM authentication failed. Please check your API key."
            
            if response.status_code == 500:
                self._debug_log("[tool] LLM error: HTTP 500 - server error")
                return "LLM server error. Please try again."

            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                self._debug_log(f"[tool] LLM HTTP error: {e}")
                return f"LLM request failed: {e}"

            data = response.json()

            # Get the assistant's message
            choice = data["choices"][0]
            assistant_message = choice["message"]

            # Check if the LLM wants to call tools
            tool_calls = assistant_message.get("tool_calls", [])

            if not tool_calls:
                # No tool calls - the LLM is done (final response)
                return assistant_message.get("content", "No response generated.")

            # Add the assistant's message (with tool calls) to history
            messages.append(assistant_message)

            # Execute each tool call
            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])
                tool_call_id = tool_call["id"]

                self._debug_log(f"[tool] LLM called: {function_name}({function_args})")

                # Execute the tool and get result
                result = self._execute_tool(function_name, function_args)
                result_str = json.dumps(result, default=str)

                self._debug_log(f"[tool] Result: {result_str[:100]}...")

                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": result_str,
                })

            self._debug_log(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM")

        return "Maximum iterations reached. Unable to complete the request."

    def _execute_tool(self, function_name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool based on the LLM's request.

        Args:
            function_name: Name of the function/tool to call.
            arguments: Arguments to pass to the function.

        Returns:
            The result of the function call.
        """
        # Import here to avoid circular imports
        from services.lms_client import LMSClient
        from config import load_config

        config = load_config()
        lms = LMSClient(config["LMS_API_BASE_URL"], config["LMS_API_KEY"])

        # Map function names to actual method calls
        if function_name == "get_items":
            return lms.get_items()
        elif function_name == "get_learners":
            return lms.get_learners()
        elif function_name == "get_scores":
            return lms.get_scores(arguments.get("lab", ""))
        elif function_name == "get_pass_rates":
            return lms.get_pass_rates(arguments.get("lab", ""))
        elif function_name == "get_timeline":
            return lms.get_timeline(arguments.get("lab", ""))
        elif function_name == "get_groups":
            return lms.get_groups(arguments.get("lab", ""))
        elif function_name == "get_top_learners":
            return lms.get_top_learners(
                arguments.get("lab", ""),
                arguments.get("limit", 5),
            )
        elif function_name == "get_completion_rate":
            return lms.get_completion_rate(arguments.get("lab", ""))
        elif function_name == "trigger_sync":
            return lms.trigger_sync()
        else:
            return {"error": f"Unknown function: {function_name}"}
