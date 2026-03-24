"""Labs listing handler."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import load_config
from services.lms_client import LMSClient


async def handle_labs(args: str = "") -> str:
    """Handle /labs command - list available labs."""
    config = load_config()
    client = LMSClient(config.lms_api_base_url, config.lms_api_key)
    
    try:
        labs = await client.get_labs()
        
        if not labs:
            return "No labs found. Try syncing data first: /sync"
        
        lab_list = []
        for lab in labs[:10]:  # Limit to 10 labs
            # Пробуем получить название из разных полей
            name = lab.get('name') or lab.get('lab_name') or lab.get('id', 'Unknown')
            title = lab.get('title') or lab.get('description', '')
            
            # Если title пустой, используем name
            if not title:
                title = name
            
            lab_list.append(f"• **{name}** — {title}")
        
        result = "📚 **Available Labs:**\n\n"
        result += "\n".join(lab_list)
        result += "\n\nUse `/scores <lab-name>` to see task scores\n"
        result += "Example: `/scores lab-04`"
        
        return result
        
    except Exception as e:
        return f"❌ Error fetching labs: {str(e)}"
