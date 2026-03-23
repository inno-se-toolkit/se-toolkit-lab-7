"""LMS data query handlers."""

import httpx
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings


class LMSClient:
    """Client for LMS API communication."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def _get(self, endpoint: str, timeout: float = 5.0) -> tuple[Optional[dict], Optional[str]]:
        """Make GET request to LMS API.

        Args:
            endpoint: API endpoint path (e.g., '/items/')
            timeout: Request timeout in seconds

        Returns:
            Tuple of (data, error). If successful, data contains response JSON.
            If failed, error contains human-readable error message.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=self.headers, timeout=timeout)
                response.raise_for_status()
                return response.json(), None
        except httpx.ConnectError as e:
            return None, f"connection refused ({self.base_url}). Check that the services are running."
        except httpx.TimeoutException:
            return None, f"timeout connecting to {self.base_url}. The backend is taking too long to respond."
        except httpx.HTTPStatusError as e:
            return None, f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        except httpx.HTTPError as e:
            return None, f"HTTP error: {str(e)}"
        except Exception as e:
            return None, f"unexpected error: {str(e)}"


def get_lms_client() -> LMSClient:
    """Create LMS client from settings."""
    return LMSClient(
        base_url=settings.lms_api_base_url,
        api_key=settings.lms_api_key
    )


def check_health() -> tuple[bool, str]:
    """Check LMS backend health.

    Returns:
        Tuple of (is_healthy, message).
    """
    client = get_lms_client()
    data, error = client._get("/items/")

    if error:
        return False, f"Backend error: {error}"

    if data is None:
        return False, "Backend error: empty response"

    # Count items if available
    items = data if isinstance(data, list) else data.get("items", [])
    count = len(items) if items else 0

    return True, f"Backend is healthy. {count} items available."


def handle_labs() -> str:
    """Handle /labs command.

    Returns:
        List of available labs from the LMS API.
    """
    client = get_lms_client()
    data, error = client._get("/items/")

    if error:
        return f"❌ Backend error: {error}"

    if not data:
        return "❌ No labs available or backend returned empty response."

    # Parse items to extract labs
    items = data if isinstance(data, list) else data.get("items", [])

    if not items:
        return "📚 No labs found in the system."

    # Group by lab (items have type 'lab' or 'task')
    labs = {}
    for item in items:
        item_type = item.get("type", "")
        if item_type == "lab":
            lab_id = item.get("id", "unknown")
            lab_name = item.get("name", item.get("title", "Unknown Lab"))
            labs[lab_id] = lab_name

    if not labs:
        return "📚 No labs found in the system."

    result = "📚 Available labs:\n"
    for lab_id, lab_name in sorted(labs.items()):
        result += f"- {lab_id} — {lab_name}\n"

    return result.strip()


def handle_scores(lab: str = "") -> str:
    """Handle /scores command.

    Args:
        lab: Lab identifier to get scores for.

    Returns:
        Pass rates information for the specified lab.
    """
    if not lab:
        return "❌ Please specify a lab: /scores <lab-name>\nExample: /scores lab-04"

    client = get_lms_client()
    data, error = client._get(f"/analytics/pass-rates?lab={lab}")

    if error:
        return f"❌ Backend error: {error}"

    if not data:
        return f"❌ No scores data available for '{lab}' or backend returned empty response."

    # Parse pass rates data
    # Expected format: [{"task": "Task Name", "pass_rate": 0.75, "attempts": 100}, ...]
    if isinstance(data, list):
        pass_rates = data
    else:
        pass_rates = data.get("pass_rates", data.get("items", []))

    if not pass_rates:
        return f"📊 No pass rate data available for '{lab}'."

    result = f"📊 Pass rates for {lab.replace('-', ' ').title()}:\n"
    for rate in pass_rates:
        task_name = rate.get("task", rate.get("task_name", "Unknown Task"))
        pass_rate = rate.get("pass_rate", 0)
        attempts = rate.get("attempts", 0)

        # Convert to percentage
        percentage = pass_rate * 100 if pass_rate <= 1 else pass_rate
        result += f"- {task_name}: {percentage:.1f}% ({attempts} attempts)\n"

    return result.strip()
