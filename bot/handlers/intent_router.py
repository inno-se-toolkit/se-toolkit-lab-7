"""
Intent router — uses LLM to interpret natural language and call backend tools.

The router:
1. Sends user message + tool definitions to LLM
2. LLM decides which tools to call
3. Bot executes tools and gets results
4. Results are fed back to LLM for final answer
5. LLM summarizes the results for the user

This is the same tool-calling pattern from Lab 6, but embedded in a Telegram bot.
"""

import sys
from typing import Any

from config import settings
from services import LLMClient, LMSClient


# System prompt that tells the LLM how to use tools
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS).
You have access to backend tools that provide data about labs, tasks, students, and scores.

When a user asks a question:
1. Think about what data you need to answer
2. Call the appropriate tool(s) to get that data
3. Once you have the data, summarize it clearly for the user

If the user asks about:
- Available labs → use get_items
- Scores or pass rates for a specific lab → use get_pass_rates with the lab ID
- Top students → use get_top_learners
- Group performance → use get_groups
- Timeline of submissions → use get_timeline
- Completion rates → use get_completion_rate
- Overall student enrollment → use get_learners

For comparison questions like "which lab has the lowest pass rate?", you may need to:
1. First get the list of labs with get_items
2. Then call get_pass_rates for each lab
3. Compare the results and report the answer

If you don't understand the question, ask for clarification or suggest what you can help with.
If the tools return an error, explain the issue to the user in a friendly way.
"""


def get_tool_definitions() -> list[dict[str, Any]]:
    """Return the list of tool definitions for the LLM.
    
    Each tool has a name, description, and parameter schema.
    The LLM uses these to decide which tool to call.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Get the list of all labs and tasks. Use this to see what labs are available.",
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
                "description": "Get the list of enrolled students and their groups.",
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
                "name": "get_scores",
                "description": "Get score distribution (4 buckets) for a specific lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01'"},
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average scores and attempt counts for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01'"},
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submissions per day for a specific lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01'"},
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group scores and student counts for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01'"},
                    },
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
                        "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01'"},
                        "limit": {"type": "integer", "description": "Number of top learners to return (default: 5)"},
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate percentage for a specific lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {"type": "string", "description": "Lab identifier, e.g., 'lab-01'"},
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger ETL sync to refresh data from the autochecker.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
    ]


def execute_tool(name: str, arguments: dict[str, Any], lms_client: LMSClient) -> Any:
    """Execute a tool by calling the appropriate LMS API endpoint.
    
    Args:
        name: Tool/function name
        arguments: Tool arguments from LLM
        lms_client: LMS API client
        
    Returns:
        Tool execution result
    """
    if name == "get_items":
        success, result = lms_client.get_items()
        return result if success else {"error": str(result)}
    
    elif name == "get_learners":
        # TODO: Implement get_learners in LMSClient
        return {"error": "get_learners not implemented yet"}
    
    elif name == "get_scores":
        lab = arguments.get("lab", "")
        success, result = lms_client.get_pass_rates(lab)  # Using pass-rates as proxy
        return result if success else {"error": str(result)}
    
    elif name == "get_pass_rates":
        lab = arguments.get("lab", "")
        success, result = lms_client.get_pass_rates(lab)
        return result if success else {"error": str(result)}
    
    elif name == "get_timeline":
        # TODO: Implement get_timeline in LMSClient
        return {"error": "get_timeline not implemented yet", "lab": arguments.get("lab", "")}
    
    elif name == "get_groups":
        # TODO: Implement get_groups in LMSClient
        return {"error": "get_groups not implemented yet", "lab": arguments.get("lab", "")}
    
    elif name == "get_top_learners":
        lab = arguments.get("lab", "")
        limit = arguments.get("limit", 5)
        # TODO: Implement get_top_learners in LMSClient
        return {"error": "get_top_learners not implemented yet", "lab": lab, "limit": limit}
    
    elif name == "get_completion_rate":
        # TODO: Implement get_completion_rate in LMSClient
        return {"error": "get_completion_rate not implemented yet", "lab": arguments.get("lab", "")}
    
    elif name == "trigger_sync":
        # TODO: Implement trigger_sync in LMSClient
        return {"error": "trigger_sync not implemented yet"}
    
    else:
        return {"error": f"Unknown tool: {name}"}


def route(user_message: str, debug: bool = False) -> str:
    """Route a user message through the LLM tool-calling loop.
    
    Args:
        user_message: The user's natural language query
        debug: If True, print debug info to stderr
        
    Returns:
        Final response text
    """
    lms_client = LMSClient(settings.lms_api_base_url, settings.lms_api_key)
    llm_client = LLMClient(settings.llm_api_base_url, settings.llm_api_key, settings.llm_api_model)
    
    tools = get_tool_definitions()
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]
    
    max_iterations = 5  # Prevent infinite loops
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Call LLM with current conversation
        response_text, tool_calls = llm_client.chat_with_tools(
            messages=messages,
            tools=tools,
            system_prompt=SYSTEM_PROMPT,
        )
        
        if debug:
            print(f"[llm] Response: {response_text[:100]}..." if response_text else "[llm] No text response", file=sys.stderr)
            print(f"[llm] Tool calls: {len(tool_calls)}", file=sys.stderr)
        
        # If no tool calls, return the LLM's text response
        if not tool_calls:
            return response_text or "I'm not sure how to help with that. Try asking about labs, scores, or students."
        
        # Execute each tool and collect results
        tool_results = []
        for tool_call in tool_calls:
            name, arguments = llm_client.parse_tool_call(tool_call)
            
            if debug:
                print(f"[tool] LLM called: {name}({arguments})", file=sys.stderr)
            
            result = execute_tool(name, arguments, lms_client)
            
            if debug:
                result_preview = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
                print(f"[tool] Result: {result_preview}", file=sys.stderr)
            
            tool_results.append({
                "role": "tool",
                "tool_call_id": tool_call.get("id", ""),
                "content": str(result),
            })
        
        # Feed tool results back to LLM
        if debug:
            print(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM", file=sys.stderr)
        
        messages.extend(tool_results)
    
    # If we hit max iterations, ask the LLM to summarize what we have
    messages.append({"role": "user", "content": "Please summarize the data you've collected so far."})
    final_response, _ = llm_client.chat_with_tools(
        messages=messages,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )
    
    return final_response or "I encountered an error. Please try again."
