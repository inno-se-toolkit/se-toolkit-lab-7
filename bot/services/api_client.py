"""LMS API client service."""

import httpx
from typing import Any


class LMSAPIClient:
    """Client for the LMS Backend API.

    All methods require authentication via Bearer token.
    """

    def __init__(self, base_url: str, api_key: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=10.0,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def get_items(self) -> list[dict[str, Any]]:
        """Get all labs and tasks."""
        response = await self._client.get("/items/")
        response.raise_for_status()
        return response.json()

    async def get_learners(self) -> list[dict[str, Any]]:
        """Get enrolled students."""
        response = await self._client.get("/learners/")
        response.raise_for_status()
        return response.json()

    async def get_scores(self, lab: str) -> list[dict[str, Any]]:
        """Get score distribution for a lab."""
        response = await self._client.get("/analytics/scores", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    async def get_pass_rates(self, lab: str) -> list[dict[str, Any]]:
        """Get per-task pass rates for a lab."""
        response = await self._client.get("/analytics/pass-rates", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    async def get_timeline(self, lab: str) -> list[dict[str, Any]]:
        """Get submissions timeline for a lab."""
        response = await self._client.get("/analytics/timeline", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    async def get_groups(self, lab: str) -> list[dict[str, Any]]:
        """Get per-group performance for a lab."""
        response = await self._client.get("/analytics/groups", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    async def get_top_learners(self, lab: str, limit: int = 5) -> list[dict[str, Any]]:
        """Get top N learners for a lab."""
        response = await self._client.get(
            "/analytics/top-learners", params={"lab": lab, "limit": limit}
        )
        response.raise_for_status()
        return response.json()

    async def get_completion_rate(self, lab: str) -> dict[str, Any]:
        """Get completion rate for a lab."""
        response = await self._client.get("/analytics/completion-rate", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    async def trigger_sync(self) -> dict[str, Any]:
        """Trigger ETL sync."""
        response = await self._client.post("/pipeline/sync", json={})
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> dict[str, Any]:
        """Check if backend is healthy and get item count."""
        items = await self.get_items()
        return {"healthy": True, "item_count": len(items)}
