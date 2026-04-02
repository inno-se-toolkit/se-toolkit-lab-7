"""Handler for /health command."""

<<<<<<< HEAD
from services.health_checker import check_backend_health
from config import load_config

=======
import asyncio
import httpx

from services.api_client import LMSAPIClient
from config import load_config


def _format_error(error: Exception) -> str:
    """Format an error message for user display.

    Returns a user-friendly message that includes the actual error
    without raw traceback.
    """
    error_str = str(error).lower()

    # Connection errors
    if "connection refused" in error_str:
        return "connection refused (localhost:42002)"
    if "connect" in error_str:
        return "cannot connect to backend"

    # HTTP errors
    if "http 502" in error_str or "bad gateway" in error_str:
        return "HTTP 502 Bad Gateway"
    if "http 503" in error_str:
        return "HTTP 503 Service Unavailable"
    if "http 500" in error_str:
        return "HTTP 500 Internal Server Error"
    if "http 404" in error_str:
        return "HTTP 404 Not Found"
    if "http 401" in error_str or "unauthorized" in error_str:
        return "HTTP 401 Unauthorized (check API key)"

    # Timeout
    if "timeout" in error_str or "timed out" in error_str:
        return "request timed out"

    # Default: show error type and message
    return f"{type(error).__name__}: {str(error)[:100]}"

>>>>>>> f1706addcc06a7cd1f01a1fd5a68353c4d238cee

def handle_health() -> str:
    """Handle /health command."""
    config = load_config()
    lms_url = config.get("LMS_API_BASE_URL", "http://localhost:42002")
    api_key = config.get("LMS_API_KEY", "")

<<<<<<< HEAD
    result = check_backend_health(lms_url, api_key)

    if result["status"] == "healthy":
        return "✅ Backend is healthy\n\n" + str(result.get("details", ""))
    elif result["status"] == "unreachable":
        return f"❌ Backend error: {result['details']}"
    else:
        return f"❌ Backend error: {result['details']}"
=======
    Returns:
        Backend health status with item count or error message.
    """
    config = load_config()
    api_client = LMSAPIClient(
        base_url=config.get("LMS_API_BASE_URL", "http://localhost:42002"),
        api_key=config.get("LMS_API_KEY", ""),
    )

    async def check_health() -> str:
        try:
            result = await api_client.health_check()
            await api_client.close()
            return f"✅ Backend is healthy. {result['item_count']} items available."
        except httpx.HTTPStatusError as e:
            await api_client.close()
            error_message = _format_error(e)
            return f"❌ Backend error: {error_message}. The backend service may be down."
        except httpx.ConnectError as e:
            await api_client.close()
            error_message = _format_error(e)
            return f"❌ Backend error: {error_message}. Check that the services are running."
        except Exception as e:
            await api_client.close()
            error_message = _format_error(e)
            return f"❌ Backend error: {error_message}. Check that the services are running."

    return asyncio.run(check_health())
>>>>>>> f1706addcc06a7cd1f01a1fd5a68353c4d238cee
