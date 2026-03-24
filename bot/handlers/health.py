"""Health check handler."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import load_config
from services.lms_client import LMSClient


async def handle_health(args: str = "") -> str:
    """Handle /health command - check backend status."""
    config = load_config()
    client = LMSClient(config.lms_api_base_url, config.lms_api_key)
    
    is_healthy, message, count = await client.health_check()
    
    if is_healthy:
        return f"✅ {message}. Found {count} items in database."
    else:
        return f"❌ Backend error: {message}"
