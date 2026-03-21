import httpx

from config import settings

_BASE = settings.lms_api_base_url
_HEADERS = {"Authorization": f"Bearer {settings.lms_api_key}"}


async def _get(path: str, params: dict | None = None) -> object:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_BASE}{path}", headers=_HEADERS, params=params, timeout=15)
        r.raise_for_status()
        return r.json()


async def _post(path: str) -> object:
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{_BASE}{path}", headers=_HEADERS, timeout=15)
        r.raise_for_status()
        return r.json()


async def get_items() -> object:
    return await _get("/items/")


async def get_learners() -> object:
    return await _get("/learners/")


async def get_scores(lab: str) -> object:
    return await _get("/analytics/scores", {"lab": lab})


async def get_pass_rates(lab: str) -> object:
    return await _get("/analytics/pass-rates", {"lab": lab})


async def get_timeline(lab: str) -> object:
    return await _get("/analytics/timeline", {"lab": lab})


async def get_groups(lab: str) -> object:
    return await _get("/analytics/groups", {"lab": lab})


async def get_top_learners(lab: str, limit: int = 10) -> object:
    return await _get("/analytics/top-learners", {"lab": lab, "limit": limit})


async def get_completion_rate(lab: str) -> object:
    return await _get("/analytics/completion-rate", {"lab": lab})


async def trigger_sync() -> object:
    return await _post("/pipeline/sync")
