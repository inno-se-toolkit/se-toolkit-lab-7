"""Handler for /scores command."""

import asyncio
import httpx
import re

from services.api_client import LMSAPIClient
from config import load_config


def _normalize_lab_id(lab_id: str) -> str:
    """Normalize lab ID to match backend format (e.g., 'lab-4' -> 'lab-04')."""
    lab_id = lab_id.lower().strip()

    # Handle formats like "lab 4", "lab4", "lab-4"
    match = re.match(r"lab[- ]?(\d+)", lab_id)
    if match:
        num = int(match.group(1))
        return f"lab-{num:02d}"

    return lab_id


def _format_error(error: Exception) -> str:
    """Format an error message for user display."""
    error_str = str(error).lower()

    if "connection refused" in error_str:
        return "connection refused"
    if "connect" in error_str:
        return "cannot connect to backend"
    if "http 502" in error_str or "bad gateway" in error_str:
        return "HTTP 502 Bad Gateway"
    if "http 404" in error_str or "not found" in error_str:
        return "HTTP 404 Not Found"
    if "timeout" in error_str or "timed out" in error_str:
        return "request timed out"

    return f"{type(error).__name__}: {str(error)[:100]}"


def handle_scores(lab_name: str = "") -> str:
    """Handle /scores command.

    Args:
        lab_name: The lab identifier (e.g., 'lab-04'). If empty, prompts user to specify a lab.

    Returns:
        Score information for the specified lab or error message.
    """
    if not lab_name:
        return "📊 Scores: Please specify a lab (e.g., /scores lab-04)"

    lab_id = _normalize_lab_id(lab_name)

    config = load_config()
    api_client = LMSAPIClient(
        base_url=config.get("LMS_API_BASE_URL", "http://localhost:42002"),
        api_key=config.get("LMS_API_KEY", ""),
    )

    async def fetch_scores() -> str:
        try:
            pass_rates = await api_client.get_pass_rates(lab_id)
            await api_client.close()

            if not pass_rates:
                return f"📊 No data found for {lab_id}. Try /labs to see available labs."

            lines = [f"📊 Pass rates for {lab_id}:"]
            for task in pass_rates:
                task_name = task.get("title", "Unknown task")
                avg_score = task.get("average_score", 0)
                attempts = task.get("attempts", 0)
                percentage = f"{avg_score:.1f}%" if avg_score else "N/A"
                lines.append(f"  - {task_name}: {percentage} ({attempts} attempts)")

            return "\n".join(lines)
        except httpx.HTTPStatusError as e:
            await api_client.close()
            error_message = _format_error(e)
            return f"❌ Failed to fetch scores for {lab_id}: {error_message}"
        except httpx.ConnectError as e:
            await api_client.close()
            error_message = _format_error(e)
            return f"❌ Failed to fetch scores for {lab_id}: {error_message}"
        except Exception as e:
            await api_client.close()
            error_message = _format_error(e)
            return f"❌ Failed to fetch scores for {lab_id}: {error_message}"

    return asyncio.run(fetch_scores())
