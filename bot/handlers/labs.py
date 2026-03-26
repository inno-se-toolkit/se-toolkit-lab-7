"""Handler for /labs command."""

import httpx
from config import load_config


def handle_labs() -> str:
    """Handle /labs command."""
    config = load_config()
    base_url = config.get("LMS_API_BASE_URL", "http://localhost:42002")
    api_key = config.get("LMS_API_KEY", "")

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
