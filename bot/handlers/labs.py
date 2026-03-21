"""
Handler for /labs command.

Returns list of available lab assignments.
"""

import json
import logging
import urllib.error
import urllib.request

from config import get_settings

from .base import HandlerResult

logger = logging.getLogger(__name__)


def _fetch_json(url: str, api_key: str) -> dict:
    """Fetch JSON from URL with API key authentication."""
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=10.0) as response:
        return json.loads(response.read().decode())


def handle_labs(args: str = "") -> HandlerResult:
    """
    Handle the /labs command.

    Args:
        args: Command arguments (can be used for specific lab lookup)

    Returns:
        HandlerResult: List of lab assignments
    """
    # Check if user requested a specific lab
    lab_arg = args.strip() if args else ""

    if lab_arg:
        return _get_specific_lab(lab_arg)

    settings = get_settings()
    backend_url = settings.lms_api_url.rstrip("/")

    try:
        data = _fetch_json(f"{backend_url}/items/", settings.lms_api_key)
        # API can return {"items": [...]} or just [...]
        if isinstance(data, dict):
            items = data.get("items", [])
        elif isinstance(data, list):
            items = data
        else:
            items = []

        if not items:
            return HandlerResult.ok("ℹ️ Лабораторные работы пока не добавлены.")

        # Filter only labs (type: lab)
        labs = [item for item in items if item.get("type") == "lab"]

        if not labs:
            return HandlerResult.ok("ℹ️ Лабораторные работы пока не добавлены.")

        lines = ["🔬 Доступные лабораторные работы:\n"]
        for i, lab in enumerate(labs, 1):
            title = lab.get("title", "Без названия")
            description = lab.get("description", "")[:100]
            lines.append(f"{i}. {title}")
            if description:
                lines.append(f"   {description}")
            lines.append("")

        message = "\n".join(lines)
        if len(lines) > 1:
            message += "\n💡 Используйте /scores <lab> для просмотра оценок."
        return HandlerResult.ok(message)

    except urllib.error.HTTPError as e:
        if e.code == 401:
            return HandlerResult.fail(
                "Backend error: HTTP 401 Unauthorized. Проверьте LMS_API_KEY.",
                message="Ошибка аутентификации в backend.",
            )
        return HandlerResult.fail(
            f"Backend error: HTTP {e.code}",
            message=f"Backend вернул неожиданный статус: {e.code}",
        )
    except urllib.error.URLError as e:
        return HandlerResult.fail(
            f"Backend error: connection refused ({backend_url}). Check that the services are running.",
            message=f"Не удалось подключиться к backend.",
        )
    except Exception as e:
        logger.exception(f"Unexpected labs fetch error: {e}")
        return HandlerResult.fail(
            f"Backend error: {str(e)}",
            message=f"Неожиданная ошибка: {str(e)}",
        )


def _get_specific_lab(lab_arg: str) -> HandlerResult:
    """
    Get details for a specific lab.

    Args:
        lab_arg: Lab number or identifier

    Returns:
        HandlerResult: Lab details
    """
    settings = get_settings()
    backend_url = settings.lms_api_url.rstrip("/")

    try:
        data = _fetch_json(f"{backend_url}/items/", settings.lms_api_key)
        # API can return {"items": [...]} or just [...]
        if isinstance(data, dict):
            items = data.get("items", [])
        elif isinstance(data, list):
            items = data
        else:
            items = []

        # Filter only labs
        labs = [item for item in items if item.get("type") == "lab"]

        # Try to find lab by index or title
        lab_item = None
        if lab_arg.isdigit():
            idx = int(lab_arg) - 1
            if 0 <= idx < len(labs):
                lab_item = labs[idx]
        else:
            # Search by title
            for lab in labs:
                if lab_arg.lower() in lab.get("title", "").lower():
                    lab_item = lab
                    break

        if not lab_item:
            return HandlerResult.fail(
                error="lab_not_found",
                message=f"❌ Лабораторная работа \"{lab_arg}\" не найдена.",
            )

        title = lab_item.get("title", "Без названия")
        description = lab_item.get("description", "")
        attributes = lab_item.get("attributes", {})
        start_date = attributes.get("start", "N/A")
        finish_date = attributes.get("finish", "N/A")

        lines = [
            f"🔬 {title}\n",
            f"📝 Описание: {description}\n",
            f"📅 Начало: {start_date}",
            f"📅 Окончание: {finish_date}",
        ]

        return HandlerResult.ok("\n".join(lines))

    except urllib.error.HTTPError as e:
        if e.code == 401:
            return HandlerResult.fail(
                "Backend error: HTTP 401 Unauthorized.",
                message="Ошибка аутентификации.",
            )
        return HandlerResult.fail(
            f"Backend error: HTTP {e.code}",
            message=f"Backend вернул статус: {e.code}",
        )
    except urllib.error.URLError:
        return HandlerResult.fail(
            f"Backend error: connection refused ({backend_url}).",
            message="Не удалось подключиться к backend.",
        )
    except Exception as e:
        logger.exception(f"Unexpected lab fetch error: {e}")
        return HandlerResult.fail(
            f"Backend error: {str(e)}",
            message=f"Неожиданная ошибка: {str(e)}",
        )
