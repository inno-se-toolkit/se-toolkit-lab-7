"""Handler for /labs command."""

<<<<<<< HEAD
import httpx
from config import load_config

=======
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

>>>>>>> f1706addcc06a7cd1f01a1fd5a68353c4d238cee

def handle_labs() -> str:
    """Handle /labs command."""
    config = load_config()
    base_url = config.get("LMS_API_BASE_URL", "http://localhost:42002")
    api_key = config.get("LMS_API_KEY", "")

<<<<<<< HEAD
    try:
        response = httpx.get(
            f"{base_url}/items/",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5.0,
        )
        response.raise_for_status()
        data = response.json()

        lines = ["📋 Available labs:"]
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("type") == "lab":
                    name = item.get("title", item.get("id", "unknown"))
                    lines.append(f"  • {name}")
        else:
            lines.append(str(data))

        return "\n".join(lines)

    except httpx.ConnectError as e:
        return f"❌ Backend error: connection refused ({base_url}). Check that the services are running."
    except httpx.TimeoutException:
        return "❌ LMS API request timed out"
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except Exception as e:
        return f"❌ Error: {str(e)}"
=======
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
>>>>>>> f1706addcc06a7cd1f01a1fd5a68353c4d238cee
