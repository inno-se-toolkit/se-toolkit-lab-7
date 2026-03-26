"""Handler for /health command."""

from services.health_checker import check_backend_health
from config import load_config


def handle_health() -> str:
    """Handle /health command."""
    config = load_config()
    lms_url = config.get("LMS_API_BASE_URL", "http://localhost:42002")
    api_key = config.get("LMS_API_KEY", "")

    result = check_backend_health(lms_url, api_key)

    if result["status"] == "healthy":
        return "✅ Backend is healthy\n\n" + str(result.get("details", ""))
    elif result["status"] == "unreachable":
        return f"❌ Backend error: {result['details']}"
    else:
        return f"❌ Backend error: {result['details']}"
