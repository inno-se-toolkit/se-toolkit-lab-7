"""Handler for /scores command."""

import httpx
from config import load_config


def handle_scores(lab_name: str = "") -> str:
    """Handle /scores command."""
    if not lab_name:
        return "📊 Scores: Please specify a lab (e.g., /scores lab-04)"

    config = load_config()
    base_url = config.get("LMS_API_BASE_URL", "http://localhost:42002")
    api_key = config.get("LMS_API_KEY", "")

    try:
        response = httpx.get(
            f"{base_url}/analytics/pass-rates?lab={lab_name}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5.0,
        )

        if response.status_code == 404:
            return f"❌ Lab '{lab_name}' not found"

        response.raise_for_status()
        data = response.json()

        # Format the response
        lines = [f"📊 Pass rates for {lab_name}:"]
        if isinstance(data, list):
            if len(data) == 0:
                return f"❌ Lab '{lab_name}' not found or has no scores"
            for item in data:
                if isinstance(item, dict):
                    task = item.get("task", "Unknown")
                    avg_score = item.get("avg_score", 0)
                    attempts = item.get("attempts", 0)
                    lines.append(f"  • {task}: {avg_score}% ({attempts} attempts)")
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
