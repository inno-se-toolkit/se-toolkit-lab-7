import httpx

from config import settings

_BASE = settings.lms_api_base_url
_HEADERS = {"Authorization": f"Bearer {settings.lms_api_key}"}


async def get_items() -> list[dict]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_BASE}/items/", headers=_HEADERS, timeout=10)
        r.raise_for_status()
        return r.json()


async def get_pass_rates(lab: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{_BASE}/analytics/pass-rates",
            params={"lab": lab},
            headers=_HEADERS,
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
