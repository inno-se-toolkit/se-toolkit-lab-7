"""Command handlers — pure async functions, no Telegram dependency."""

import httpx

from services import lms


async def handle_start() -> str:
    return "👋 Welcome to the LMS Bot! Use /help to see available commands."


async def handle_help() -> str:
    return (
        "Available commands:\n"
        "/start — welcome message\n"
        "/help — list commands\n"
        "/health — check backend status\n"
        "/labs — list available labs\n"
        "/scores <lab> — per-task pass rates (e.g. /scores lab-04)"
    )


async def handle_health() -> str:
    try:
        items = await lms.get_items()
        return f"✅ Backend is healthy. {len(items)} items available."
    except httpx.ConnectError as e:
        return f"❌ Backend error: connection refused ({e}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code}. The backend service may be down."
    except Exception as e:
        return f"❌ Backend error: {e}"


async def handle_labs() -> str:
    try:
        items = await lms.get_items()
        labs = [i for i in items if i.get("type") == "lab"]
        if not labs:
            return "No labs found."
        lines = "\n".join(f"- {lab['title']}" for lab in labs)
        return f"Available labs:\n{lines}"
    except httpx.ConnectError as e:
        return f"❌ Backend error: connection refused ({e}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code}."
    except Exception as e:
        return f"❌ Error: {e}"


async def handle_scores(lab: str) -> str:
    if not lab:
        return "Usage: /scores <lab>  (e.g. /scores lab-04)"
    try:
        rates = await lms.get_pass_rates(lab)
        if not rates:
            return f"No data found for {lab}. Check the lab name (e.g. lab-04)."
        lines = "\n".join(
            f"- {r['task']}: {r['avg_score']}% ({r['attempts']} attempts)" for r in rates
        )
        return f"Pass rates for {lab}:\n{lines}"
    except httpx.ConnectError as e:
        return f"❌ Backend error: connection refused ({e}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code}."
    except Exception as e:
        return f"❌ Error: {e}"


async def handle_unknown(command: str) -> str:
    return f"Unknown command: {command}. Use /help to see available commands."
