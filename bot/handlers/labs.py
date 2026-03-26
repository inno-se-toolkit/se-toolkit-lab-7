"""Handler for /labs command."""

import asyncio
import httpx

from services.api_client import LMSAPIClient
from config import load_config


def _format_error(error: Exception) -> str:
    """Format an error message for user display."""
    error_str = str(error).lower()

    if "connection refused" in error_str:
        return "connection refused"
    if "connect" in error_str:
        return "cannot connect to backend"
    if "http 502" in error_str or "bad gateway" in error_str:
        return "HTTP 502 Bad Gateway"
    if "timeout" in error_str or "timed out" in error_str:
        return "request timed out"

    return f"{type(error).__name__}: {str(error)[:100]}"


def handle_labs() -> str:
    """Handle /labs command.

    Returns:
        List of available labs or error message.
    """
    config = load_config()
    api_client = LMSAPIClient(
        base_url=config.get("LMS_API_BASE_URL", "http://localhost:42002"),
        api_key=config.get("LMS_API_KEY", ""),
    )

    async def fetch_labs() -> str:
        try:
            items = await api_client.get_items()
            await api_client.close()

            labs = [item for item in items if item.get("type") == "lab"]

            if not labs:
                return "📚 No labs found."

            lab_list = "\n".join(f"- {lab['title']}" for lab in labs)
            return f"📚 Available labs:\n{lab_list}"
        except httpx.HTTPStatusError as e:
            await api_client.close()
            error_message = _format_error(e)
            return f"❌ Failed to fetch labs: {error_message}"
        except httpx.ConnectError as e:
            await api_client.close()
            error_message = _format_error(e)
            return f"❌ Failed to fetch labs: {error_message}"
        except Exception as e:
            await api_client.close()
            error_message = _format_error(e)
            return f"❌ Failed to fetch labs: {error_message}"

    return asyncio.run(fetch_labs())
