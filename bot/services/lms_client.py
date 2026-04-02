"""LMS API client for fetching scores and health data."""

import httpx
from typing import Optional


class LMSClient:
    """Client for the LMS API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5.0,
        )

    def get_health(self) -> dict:
        """Get backend health status."""
        response = self._client.get("/health")
        response.raise_for_status()
        return response.json()

    def get_scores(self, lab: str) -> list:
        """Get score distribution (4 buckets) for a specific lab."""
        response = self._client.get("/analytics/scores", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_labs(self) -> list:
        """Get list of all available labs."""
        response = self._client.get("/labs")
        response.raise_for_status()
        return response.json()

    def get_items(self) -> list:
        """Get list of all items (labs and tasks)."""
        response = self._client.get("/items/")
        response.raise_for_status()
        return response.json()

    def get_learners(self) -> list:
        """Get list of enrolled learners and groups."""
        response = self._client.get("/learners/")
        response.raise_for_status()
        return response.json()

    def get_pass_rates(self, lab: str) -> dict:
        """Get per-task average scores and attempt counts for a lab."""
        response = self._client.get("/analytics/pass-rates", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_timeline(self, lab: str) -> list:
        """Get submissions per day for a lab."""
        response = self._client.get("/analytics/timeline", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_groups(self, lab: str) -> list:
        """Get per-group scores and student counts for a lab."""
        response = self._client.get("/analytics/groups", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_top_learners(self, lab: str, limit: int = 5) -> list:
        """Get top N learners by score for a lab."""
        params = {"lab": lab, "limit": limit}
        response = self._client.get("/analytics/top-learners", params=params)
        response.raise_for_status()
        return response.json()

    def get_completion_rate(self, lab: str) -> dict:
        """Get completion rate percentage for a lab."""
        response = self._client.get("/analytics/completion-rate", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def trigger_sync(self) -> dict:
        """Trigger a data sync from the autochecker."""
        response = self._client.post("/pipeline/sync")
        response.raise_for_status()
        return response.json()
