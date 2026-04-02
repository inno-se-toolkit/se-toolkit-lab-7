"""Health check service for the bot."""

from typing import Optional
import httpx


def check_backend_health(base_url: str, api_key: str = "") -> dict:
    """Check if the backend is healthy.

    Args:
        base_url: The backend URL to check.
        api_key: Optional API key for authentication.

    Returns:
        Dict with status and details.
    """
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        response = httpx.get(f"{base_url}/items/", timeout=5.0, headers=headers)
        if response.status_code == 200:
            data = response.json()
            item_count = len(data) if isinstance(data, list) else "unknown"
            return {
                "status": "healthy",
                "details": f"{item_count} items available",
            }
        return {
            "status": "unhealthy",
            "details": f"Status code: {response.status_code}",
        }
    except httpx.ConnectError as e:
        return {
            "status": "unreachable",
            "details": f"connection refused ({base_url}). Check that the services are running.",
        }
    except httpx.TimeoutException:
        return {
            "status": "timeout",
            "details": "Backend request timed out",
        }
    except httpx.HTTPStatusError as e:
        return {
            "status": "unhealthy",
            "details": f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.",
        }
