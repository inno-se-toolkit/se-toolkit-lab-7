"""Scores handler."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import load_config
from services.lms_client import LMSClient
import httpx


async def handle_scores(args: str = "") -> str:
    """Handle /scores command - get per-task pass rates for a lab."""
    if not args:
        return (
            "Please specify a lab name.\n"
            "Example: `/scores lab-04`\n\n"
            "Use `/labs` to see available labs."
        )
    
    config = load_config()
    client = LMSClient(config.lms_api_base_url, config.lms_api_key)
    
    try:
        # Get pass rates for the lab
        pass_rates = await client.get_pass_rates(args)
        
        if not pass_rates:
            return f"No data found for lab: {args}"
        
        # Извлекаем задачи
        tasks = pass_rates.get('tasks', [])
        if not tasks and isinstance(pass_rates, list):
            tasks = pass_rates
        
        if not tasks:
            return f"No tasks found for lab: {args}"
        
        result = f"📊 **Pass Rates for {args}:**\n\n"
        
        for task in tasks[:15]:  # Limit to 15 tasks
            # Название задачи находится в поле 'task'
            name = task.get('task') or \
                   task.get('name') or \
                   task.get('task_name') or \
                   task.get('title') or \
                   'Unknown'
            
            # Pass rate в поле 'avg_score'
            rate = task.get('avg_score', 0)
            attempts = task.get('attempts', 0)
            
            # Преобразуем в число если нужно
            if isinstance(rate, str):
                rate = float(rate.rstrip('%'))
            
            result += f"• **{name}**: {rate:.1f}% ({attempts} attempts)\n"
        
        return result
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"❌ Lab '{args}' not found. Use `/labs` to see available labs."
        return f"❌ Backend error: HTTP {e.response.status_code}"
    except Exception as e:
        return f"❌ Error fetching scores: {str(e)}"
