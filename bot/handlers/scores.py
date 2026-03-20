from services.lms_api import LMSAPIClient
from config import LMS_API_URL, LMS_API_KEY


def handle_scores(user_input: str = "") -> str:
    """Handle /scores command with lab argument."""
    if not user_input or not user_input.strip():
        return "Usage: /scores <lab> (e.g., /scores lab-04)"

    lab = user_input.strip()

    try:
        client = LMSAPIClient(LMS_API_URL, LMS_API_KEY)
        data = client.get_pass_rates(lab)

        if not data:
            return f"No pass rate data found for {lab}."

        if isinstance(data, dict):
            pass_rates = data.get("pass_rates", data.get("data", []))
        elif isinstance(data, list):
            pass_rates = data
        else:
            return f"Unexpected data format for {lab}."

        if not pass_rates:
            return f"No pass rate data available for {lab}."

        result = f"Pass rates for {lab}:"
        for task in pass_rates:
            if isinstance(task, dict):
                task_name = task.get("task_name", task.get("task", "Unknown"))
                pass_rate = task.get("pass_rate", task.get("pass_rate_percent", 0))
                attempts = task.get("attempts", task.get("total_attempts", 0))
                result += f"\n- {task_name}: {pass_rate:.1f}% ({attempts} attempts)"
        return result
    except ConnectionError as e:
        return f"Backend error: {e}"
    except Exception as e:
        return f"Backend error: {type(e).__name__}: {e}"
