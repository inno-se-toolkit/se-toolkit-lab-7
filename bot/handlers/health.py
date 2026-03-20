from services.lms_api import LMSAPIClient
from config import LMS_API_URL, LMS_API_KEY


def handle_health(user_input: str = "") -> str:
    """Handle /health command."""
    try:
        client = LMSAPIClient(LMS_API_URL, LMS_API_KEY)
        items = client.get_items()
        if items:
            count = len(items) if isinstance(items, list) else "unknown"
            return f"Backend is healthy. {count} items available."
        return "Backend is healthy. No items found."
    except ConnectionError as e:
        return f"Backend error: {e}"
    except Exception as e:
        return f"Backend error: {type(e).__name__}: {e}"
