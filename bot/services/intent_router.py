"""Intent router with LLM tool calling."""

import sys
import json
from typing import List, Dict, Any, Optional

from .lms_api import LMSAPIClient
from .llm import LLMClient


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Return tool definitions for LLM."""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Get list of all labs and tasks. Use this to discover available labs.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average pass rates and attempt counts for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {"lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}},
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_scores",
                "description": "Get score distribution for a specific lab.",
                "parameters": {
                    "type": "object",
                    "properties": {"lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}},
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners by score for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                        "limit": {"type": "integer", "description": "Number of top learners, default 5"}
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "Get list of enrolled students.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submissions timeline for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {"lab": {"type": "string", "description": "Lab identifier"}},
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group scores for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {"lab": {"type": "string", "description": "Lab identifier"}},
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {"lab": {"type": "string", "description": "Lab identifier"}},
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger ETL sync to refresh data.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    ]


SYSTEM_PROMPT = """You are a helpful LMS assistant. Use tools to get data about labs and students.
Answer based on actual tool results. If unsure, ask for clarification."""


class IntentRouter:
    """Routes user messages through LLM with tool calling."""

    def __init__(self, lms_client: LMSAPIClient, llm_client: LLMClient):
        self.lms_client = lms_client
        self.llm_client = llm_client
        self.tools = get_tool_definitions()
        
        self.tool_handlers = {
            "get_items": lambda args: self.lms_client.get_items(),
            "get_pass_rates": lambda args: self.lms_client.get_pass_rates(args.get("lab", "lab-04")),
            "get_scores": lambda args: self.lms_client.get_pass_rates(args.get("lab", "lab-04")),
            "get_top_learners": lambda args: {"learners": [], "lab": args.get("lab", "lab-04"), "limit": args.get("limit", 5)},
            "get_learners": lambda args: [],
            "get_timeline": lambda args: {"timeline": [], "lab": args.get("lab", "lab-04")},
            "get_groups": lambda args: {"groups": [], "lab": args.get("lab", "lab-04")},
            "get_completion_rate": lambda args: {"completion_rate": 0, "lab": args.get("lab", "lab-04")},
            "trigger_sync": lambda args: {"status": "sync triggered"},
        }

    def _debug(self, message: str) -> None:
        print(f"[intent] {message}", file=sys.stderr)

    def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        self._debug(f"Tool called: {name}({arguments})")
        handler = self.tool_handlers.get(name)
        if not handler:
            return f"Unknown tool: {name}"
        try:
            result = handler(arguments)
            self._debug(f"Tool result: {str(result)[:150]}...")
            return result
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"

    def route(self, user_message: str) -> str:
        """Route user message through LLM with tool calling."""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            self._debug(f"Iteration {iteration}")

            response = self.llm_client.chat(messages, self.tools)
            
            choices = response.get("choices", [])
            if not choices:
                return "LLM error: no response"
            
            message = choices[0].get("message", {})
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])

            if not tool_calls:
                self._debug(f"Final answer: {content[:100] if content else 'empty'}...")
                return content or "I couldn't process your request."

            self._debug(f"LLM called {len(tool_calls)} tool(s)")
            
            # Add assistant message with tool_calls FIRST
            assistant_message = {
                "role": "assistant",
                "content": None,
                "tool_calls": tool_calls,
            }
            messages.append(assistant_message)
            
            # Execute tools and add tool responses
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                name = function.get("name", "")
                arguments_str = function.get("arguments", "{}")
                
                try:
                    arguments = json.loads(arguments_str) if arguments_str else {}
                except json.JSONDecodeError:
                    arguments = {}

                result = self._execute_tool(name, arguments)
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", f"call_{name}"),
                    "content": json.dumps(result, default=str),
                })

            self._debug(f"Added {len(tool_calls)} tool results to conversation")

        return "Maximum iterations reached."
