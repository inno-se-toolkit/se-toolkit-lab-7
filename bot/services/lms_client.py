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

    def get_scores(self, lab_name: str) -> Optional[dict]:
        """Get scores for a specific lab."""
        try:
            response = self._client.get(f"/scores/{lab_name}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    def get_labs(self) -> list:
        """Get list of all available labs."""
        response = self._client.get("/labs")
        response.raise_for_status()
        return response.json()
