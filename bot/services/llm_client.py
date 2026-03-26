"""
LLM Client for tool-based intent routing.

Sends user messages + tool definitions to LLM and parses tool calls.
"""

import httpx
import json
import os
from typing import Optional


class LLMClient:
    """Client for interacting with LLM API (Qwen Code)."""
    
    def __init__(self):
        self.api_key = os.environ.get("LLM_API_KEY", "")
        self.base_url = os.environ.get("LLM_API_BASE_URL", "http://localhost:42005")
        self.model = os.environ.get("LLM_API_MODEL", "coder-model")
    
    def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        max_iterations: int = 5
    ) -> str:
        """
        Chat with LLM using tool calling.
        
        Args:
            messages: Conversation history
            tools: List of tool schemas
            max_iterations: Max tool call iterations
        
        Returns:
            Final response text
        """
        conversation = messages.copy()
        
        for iteration in range(max_iterations):
            # Call LLM
            response = self._call_llm(conversation, tools)
            
            if not response:
                return "LLM error: No response"
            
            # Check for tool calls
            tool_calls = response.get("tool_calls", [])
            
            if not tool_calls:
                # No tool calls - return the message
                return response.get("content", "No response")
            
            # Execute tool calls and feed results back
            for tool_call in tool_calls:
                result = self._execute_tool(tool_call)
                conversation.append({
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call.get("id")
                })
            
            # Add assistant message with tool calls
            conversation.append({
                "role": "assistant",
                "tool_calls": tool_calls
            })
        
        return "Max iterations reached"
    
    def _call_llm(self, messages: list[dict], tools: list[dict]) -> Optional[dict]:
        """Make API call to LLM."""
        try:
            response = httpx.post(
                f"{self.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": tools,
                    "tool_choice": "auto"
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {})
        except Exception as e:
            print(f"[LLM] Error: {e}", file=__import__('sys').stderr)
            return None
    
    def _execute_tool(self, tool_call: dict) -> dict:
        """Execute a tool call and return result."""
        function = tool_call.get("function", {})
        name = function.get("name", "")
        arguments = function.get("arguments", "{}")
        
        try:
            args = json.loads(arguments) if isinstance(arguments, str) else arguments
        except:
            args = {}
        
        print(f"[tool] LLM called: {name}({args})", file=__import__('sys').stderr)
        
        # Import handlers to access tools
        from services.api_client import APIClient
        
        api = APIClient()
        
        # Map tool names to API methods
        tool_methods = {
            "get_items": api.get_items,
            "get_learners": api.get_learners,
            "get_scores": api.get_scores,
            "get_pass_rates": api.get_pass_rates,
            "get_timeline": api.get_timeline,
            "get_groups": api.get_groups,
            "get_top_learners": api.get_top_learners,
            "get_completion_rate": api.get_completion_rate,
            "trigger_sync": api.trigger_sync,
        }
        
        method = tool_methods.get(name)
        if not method:
            return {"error": f"Unknown tool: {name}"}
        
        try:
            result = method(**args)
            print(f"[tool] Result: {str(result)[:100]}...", file=__import__('sys').stderr)
            return result
        except Exception as e:
            print(f"[tool] Error: {e}", file=__import__('sys').stderr)
            return {"error": str(e)}


def get_tool_definitions() -> list[dict]:
    """Get tool definitions for LLM."""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "List all labs and tasks in the system",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "Get list of enrolled students and their groups",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_scores",
                "description": "Get score distribution (4 buckets) for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average scores and attempt counts for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submissions per day for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group average scores and student counts for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners by average score for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"},
                        "limit": {"type": "integer", "description": "Number of top learners to return"}
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate percentage for a lab",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01'"}
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger data sync from autochecker",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
    ]
