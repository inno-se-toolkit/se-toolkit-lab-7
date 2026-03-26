"""
Intent Router for natural language queries.

Uses LLM to route user messages to appropriate tools.
NO regex/keyword matching in the routing path - LLM decides.
"""

import sys
import json
from services.llm_client import LLMClient, get_tool_definitions


# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS). 
You have access to tools that fetch data about labs, students, scores, and analytics.

When a user asks a question:
1. First understand what they're asking
2. Call the appropriate tool(s) to get the data
3. Use the tool results to provide a helpful, accurate answer

Available tools:
- get_items: List all labs and tasks
- get_learners: List all students and enrollment data
- get_scores: Score distribution (4 buckets) for a lab
- get_pass_rates: Per-task average scores and attempt counts for a lab
- get_timeline: Submissions per day for a lab
- get_groups: Per-group average scores and student counts
- get_top_learners: Top N learners by average score
- get_completion_rate: Completion rate percentage
- trigger_sync: Refresh data from autochecker

For multi-step questions (e.g., "which lab has the lowest pass rate"):
1. First call get_items to get all labs
2. Then call get_pass_rates for each lab
3. Compare the results and provide an answer

If the user's message is unclear or gibberish, politely ask for clarification.
If greeted, respond warmly and mention what you can help with.
Always call tools to get real data before answering questions about labs, students, or scores.
"""


def route_intent(user_message: str) -> str:
    """
    Route a user message through the LLM to get a response.
    
    Args:
        user_message: The user's input text
    
    Returns:
        Response text from the LLM
    """
    llm = LLMClient()
    tools = get_tool_definitions()
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    print(f"[intent] Processing: {user_message}", file=sys.stderr)
    
    try:
        response = llm.chat_with_tools(messages, tools)
        
        print(f"[response] {response[:100]}...", file=sys.stderr)
        return response
    except Exception as e:
        print(f"[error] {e}", file=sys.stderr)
        return f"Error processing request: {str(e)}"


def get_inline_buttons() -> list:
    """
    Get inline keyboard buttons for common actions.
    Returns list of button configurations.
    """
    return [
        {"text": "📋 List Labs", "callback_data": "list_labs"},
        {"text": "📊 Lab Scores", "callback_data": "show_scores"},
        {"text": "🏆 Top Students", "callback_data": "top_students"},
        {"text": "👥 Groups", "callback_data": "show_groups"},
    ]
