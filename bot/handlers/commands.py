"""
Command handlers - pure functions that take input and return formatted text.
No Telegram dependencies. Uses LMS client for backend integration.
"""
import asyncio
from services.lms_client import get_lms_client

def handle_start(user_input: str) -> str:
    """Handles /start command."""
    return "👋 Welcome to the SE Toolkit Bot! I can help you check lab status, scores, and more. Use /help to see available commands."

def handle_help(user_input: str) -> str:
    """Handles /help command."""
    return (
        "📚 Available Commands:\n\n"
        "/start - Welcome message\n"
        "/help - Show this help message\n"
        "/health - Check backend system status\n"
        "/labs - List all available labs\n"
        "/scores <lab_id> - Show pass rates for a specific lab (e.g., /scores lab-04)\n\n"
        "💡 Tip: You can also ask questions like 'what labs are available' for natural language help."
    )

async def handle_health_async(user_input: str) -> str:
    """Handles /health command - async version that calls backend."""
    client = get_lms_client()
    result = await client.health_check()
    
    if result.get("status") == "healthy":
        count = result.get("item_count", 0)
        return f"✅ Backend is healthy. {count} items available."
    else:
        error = result.get("error", "Unknown error")
        return f"❌ Backend error: {error}"

def handle_health(user_input: str) -> str:
    """Handles /health command - sync wrapper for test mode."""
    return asyncio.run(handle_health_async(user_input))

async def handle_labs_async(user_input: str) -> str:
    """Handles /labs command - async version that calls backend."""
    client = get_lms_client()
    result = await client.get_labs()
    
    if "error" in result:
        return f"❌ Error fetching labs: {result['error']}"
    
    labs = result.get("labs", [])
    if not labs:
        return "📭 No labs found. Try running a pipeline sync first."
    
    lines = ["🔬 Available Labs:"]
    for lab in labs:
        lab_id = lab.get("id", "unknown")
        name = lab.get("name", lab_id)
        desc = lab.get("description", "")
        if desc and len(desc) > 50:
            desc = desc[:47] + "..."
        lines.append(f"- {lab_id} — {name}" + (f" ({desc})" if desc else ""))
    
    return "\n".join(lines)

def handle_labs(user_input: str) -> str:
    """Handles /labs command - sync wrapper for test mode."""
    return asyncio.run(handle_labs_async(user_input))

async def handle_scores_async(user_input: str) -> str:
    """Handles /scores command - async version that calls backend."""
    parts = user_input.split()
    if len(parts) < 2:
        return "⚠️ Please specify a lab ID. Example: `/scores lab-04`"
    
    lab_id = parts[1].lower()
    client = get_lms_client()
    result = await client.get_pass_rates(lab_id)
    
    if "error" in result:
        return f"❌ Error: {result['error']}"
    
    tasks = result.get("tasks", [])
    lab_id = result.get("lab_id", lab_id)
    
    if not tasks:
        return f"📭 No score data found for {lab_id}. Try another lab or check if the lab exists with /labs"
    
    lines = [f"📊 Pass rates for {lab_id}:"]
    for task in tasks:
        name = task.get("name", "Unknown task")
        pass_rate = task.get("pass_rate")
        attempts = task.get("attempts", 0)
        
        if pass_rate is not None:
            # Format percentage
            if isinstance(pass_rate, float):
                percentage = f"{pass_rate:.1f}%"
            else:
                percentage = f"{pass_rate}%"
            lines.append(f"- {name}: {percentage} ({attempts} attempts)")
        else:
            lines.append(f"- {name}: N/A ({attempts} attempts)")
    
    return "\n".join(lines)

def handle_scores(user_input: str) -> str:
    """Handles /scores command - sync wrapper for test mode."""
    return asyncio.run(handle_scores_async(user_input))

def handle_natural_language(user_input: str) -> str:
    """Handles natural language queries (fallback)."""
    text = user_input.lower().strip()
    
    # Simple keyword matching for common queries
    if any(phrase in text for phrase in ["what labs", "available labs", "list labs"]):
        return handle_labs(user_input)
    elif "health" in text or "status" in text or "working" in text:
        return handle_health(user_input)
    elif any(phrase in text for phrase in ["score", "pass rate", "results"]):
        # Try to extract lab ID from natural language
        import re
        match = re.search(r'lab[-\s]?\d+', text)
        if match:
            lab_id = match.group().replace(" ", "-").lower()
            return handle_scores(f"/scores {lab_id}")
        return "🔍 To check scores, please specify a lab. Example: `/scores lab-04` or ask 'scores for lab 04'"
    elif "help" in text:
        return handle_help(user_input)
    
    return "🤔 I'm not sure how to help with that. Try /help to see available commands, or ask about labs, scores, or system status."