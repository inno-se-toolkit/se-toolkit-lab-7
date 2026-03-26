"""
API Client for LMS Backend.

Handles all HTTP requests to the backend API.
"""

import httpx
import os
from typing import Optional


class APIClient:
    """Client for LMS Backend API."""
    
    def __init__(self):
        self.base_url = os.environ.get("LMS_API_BASE_URL", "http://localhost:42002")
        self.api_key = os.environ.get("LMS_API_KEY", "")
        self._headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def get_items(self) -> list:
        """Get all labs and tasks."""
        response = httpx.get(f"{self.base_url}/items/", headers=self._headers, timeout=10.0)
        response.raise_for_status()
        return response.json()
    
    def get_learners(self) -> list:
        """Get all learners."""
        response = httpx.get(f"{self.base_url}/learners/", headers=self._headers, timeout=10.0)
        response.raise_for_status()
        return response.json()
    
    def get_scores(self, lab: str) -> list:
        """Get score distribution for a lab."""
        response = httpx.get(
            f"{self.base_url}/analytics/scores",
            headers=self._headers,
            params={"lab": lab},
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    
    def get_pass_rates(self, lab: str) -> list:
        """Get per-task pass rates for a lab."""
        response = httpx.get(
            f"{self.base_url}/analytics/pass-rates",
            headers=self._headers,
            params={"lab": lab},
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    
    def get_timeline(self, lab: str) -> list:
        """Get timeline data for a lab."""
        response = httpx.get(
            f"{self.base_url}/analytics/timeline",
            headers=self._headers,
            params={"lab": lab},
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    
    def get_groups(self, lab: str) -> list:
        """Get per-group data for a lab."""
        response = httpx.get(
            f"{self.base_url}/analytics/groups",
            headers=self._headers,
            params={"lab": lab},
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    
    def get_top_learners(self, lab: str, limit: int = 10) -> list:
        """Get top learners for a lab."""
        response = httpx.get(
            f"{self.base_url}/analytics/top-learners",
            headers=self._headers,
            params={"lab": lab, "limit": limit},
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    
    def get_completion_rate(self, lab: str) -> dict:
        """Get completion rate for a lab."""
        response = httpx.get(
            f"{self.base_url}/analytics/completion-rate",
            headers=self._headers,
            params={"lab": lab},
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    
    def trigger_sync(self) -> dict:
        """Trigger data sync."""
        response = httpx.post(
            f"{self.base_url}/pipeline/sync",
            headers=self._headers,
            json={},
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
