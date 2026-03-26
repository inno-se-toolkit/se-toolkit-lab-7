"""
Intent Router for natural language queries.

Uses LLM to route user messages to appropriate tools.
"""

import sys
import json
from services.llm_client import LLMClient, get_tool_definitions
from services.api_client import APIClient


# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS). 
You have access to tools that fetch data about labs, students, scores, and analytics.

When a user asks a question:
1. First understand what they're asking
2. Call the appropriate tool(s) to get the data
3. Use the tool results to provide a helpful, accurate answer

Available tools:
- get_items: List all labs and tasks
- get_learners: List all students
- get_scores: Score distribution for a lab
- get_pass_rates: Per-task pass rates for a lab
- get_timeline: Submissions over time
- get_groups: Per-group performance
- get_top_learners: Top students by score
- get_completion_rate: Completion percentage
- trigger_sync: Refresh data

For multi-step questions (e.g., "which lab has the lowest pass rate"):
1. First call get_items to get all labs
2. Then call get_pass_rates for each lab
3. Compare the results and provide an answer

If the user's message is unclear or gibberish, politely ask for clarification.
If greeted, respond warmly and mention what you can help with.
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
        
        # Check if LLM returned an error
        if response.startswith("LLM error"):
            print(f"[fallback] LLM failed, using rule-based routing", file=sys.stderr)
            return fallback_routing(user_message)
        
        print(f"[response] {response[:100]}...", file=sys.stderr)
        return response
    except Exception as e:
        print(f"[error] {e}", file=sys.stderr)
        return fallback_routing(user_message)


def fallback_routing(user_message: str) -> str:
    """
    Fallback routing when LLM is unavailable.
    Uses simple keyword matching.
    
    Args:
        user_message: The user's input text
    
    Returns:
        Response text
    """
    message_lower = user_message.lower()
    api = APIClient()
    
    # Keyword-based routing
    try:
        if any(word in message_lower for word in ["lab", "labs", "available", "list"]):
            items = api.get_items()
            labs = [item for item in items if item.get("type") == "lab"]
            result = "📋 Available Labs:\n\n"
            for lab in labs:
                result += f"• {lab.get('title', 'Unknown')}\n"
            return result
        
        elif "score" in message_lower:
            # Extract lab number
            import re
            match = re.search(r'lab[- ]?(\d+)', message_lower)
            if match:
                lab_num = match.group(1).zfill(2)
                lab_id = f"lab-{lab_num}"
                return handlers.handle_scores(lab_id)
            return "Please specify a lab. Example: 'show scores for lab 4'"
        
        elif any(word in message_lower for word in ["top", "best", "student", "learner"]):
            # Get top learners for a default lab
            lab_num = "04"
            match = re.search(r'lab[- ]?(\d+)', message_lower)
            if match:
                lab_num = match.group(1).zfill(2)
            lab_id = f"lab-{lab_num}"
            top = api.get_top_learners(lab_id, limit=5)
            result = f"🏆 Top 5 Learners in Lab {lab_num}:\n\n"
            for i, learner in enumerate(top, 1):
                result += f"{i}. Avg: {learner.get('avg_score', 0)}% | Attempts: {learner.get('attempts', 0)}\n"
            return result
        
        elif any(word in message_lower for word in ["group", "groups"]):
            lab_num = "04"
            match = re.search(r'lab[- ]?(\d+)', message_lower)
            if match:
                lab_num = match.group(1).zfill(2)
            lab_id = f"lab-{lab_num}"
            groups = api.get_groups(lab_id)
            result = f"👥 Groups in Lab {lab_num}:\n\n"
            for group in groups:
                result += f"• {group.get('group', 'Unknown')}: Avg {group.get('avg_score', 0)}% ({group.get('students', 0)} students)\n"
            return result
        
        elif any(word in message_lower for word in ["hello", "hi", "hey", "greet"]):
            return "👋 Hello! I'm the LMS Bot. I can help you with:\n- Listing labs\n- Showing scores\n- Top learners\n- Group performance\n\nJust ask!"
        
        else:
            return "I'm not sure what you're asking. Try:\n- 'what labs are available?'\n- 'show scores for lab 4'\n- 'who are the top students?'"
    
    except Exception as e:
        return f"Error: {str(e)}"


# Import handlers for fallback
import handlers
