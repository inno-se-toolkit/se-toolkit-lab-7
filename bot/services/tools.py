"""Tool definitions for LLM-powered intent routing.

These schemas tell the LLM what tools are available and how to call them.
The LLM reads the descriptions and parameter schemas to decide which tool
to call for a given user query.
"""

from typing import Any


def get_tool_definitions() -> list[dict[str, Any]]:
    """Return all tool definitions for the LLM.

    Each tool has:
    - name: The function name the LLM will call
    - description: What the tool does (critical for LLM to pick the right tool)
    - parameters: JSON schema for the arguments

    Returns:
        List of tool schemas in OpenAI function-calling format.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Get a list of all available labs and tasks. Use this when the user asks about what labs exist, what's available, or needs an overview of the course structure.",
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
                "description": "Get a list of all enrolled learners and their group assignments. Use this when the user asks about students, enrollment, or group membership.",
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
                "description": "Get score distribution (4 buckets) for a specific lab. Use this when the user asks about scores, grade distribution, or how students performed in a particular lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average scores and attempt counts for a lab. Use this when the user asks about pass rates, average scores, difficulty, or how many attempts students needed for a specific lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
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
                "description": "Get submissions per day for a lab. Use this when the user asks about submission patterns, when students submitted, or activity over time for a specific lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
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
                "description": "Get per-group scores and student counts for a lab. Use this when the user asks about group performance, compare groups, or which group did better in a specific lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
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
                "description": "Get top N learners by score for a lab. Use this when the user asks about top students, leaderboard, best performers, or who did best in a specific lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'. Optional - if not provided, returns overall top learners.",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top learners to return, e.g., 5, 10. Default is 5.",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate percentage for a lab. Use this when the user asks about completion rate, how many students finished, or what percentage completed a specific lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
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
                "description": "Trigger a data sync from the autochecker to refresh the database. Use this when the user asks to refresh data, sync, or update from the autochecker.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
    ]


def get_system_prompt() -> str:
    """Return the system prompt for the LLM.

    This prompt guides the LLM to:
    1. Use tools to get data (never make up answers)
    2. Call multiple tools when needed for comparison
    3. Format responses clearly with the data
    4. Handle greetings and ambiguous queries gracefully

    Returns:
        System prompt text.
    """
    return """You are a helpful assistant for a software engineering course. You have access to course data via tools.

IMPORTANT RULES:
1. ALWAYS use tools to get data - never make up answers about labs, scores, or students.
2. If the user asks a comparison question (e.g., "which lab has the lowest..."), you MUST call the relevant tool for EACH item being compared.
3. If the user greeting or says something ambiguous, respond helpfully without using tools.
4. Format your responses clearly - use bullet points and mention specific numbers from the data.

CAPABILITIES:
- List available labs and tasks
- Show score distributions and pass rates
- Compare groups, labs, or students
- Show top performers
- Track submission timelines
- Refresh data from the autochecker

If you don't understand the query, ask for clarification. If the user just says "hello" or something similar, greet them and offer to help with course data."""
