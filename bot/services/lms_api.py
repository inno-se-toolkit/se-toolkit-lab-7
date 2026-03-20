"""LMS API client."""

import httpx
from typing import Optional


class LMSAPIClient:
    """Client for LMS API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def get_items(self) -> Optional[dict]:
        """Get all items (labs and tasks)."""
        try:
            with httpx.Client() as client:
                response = client.get(f"{self.base_url}/items/", headers=self.headers, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            raise ConnectionError(f"connection refused ({self.base_url}). Check that the services are running.")
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.")
        except httpx.TimeoutException:
            raise ConnectionError("request timed out. The backend is taking too long to respond.")
        except Exception as e:
            raise ConnectionError(f"{type(e).__name__}: {e}")

    def get_pass_rates(self, lab: str) -> Optional[dict]:
        """Get pass rates for a specific lab."""
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}/analytics/pass-rates",
                    headers=self.headers,
                    params={"lab": lab},
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            raise ConnectionError(f"connection refused ({self.base_url}). Check that the services are running.")
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.")
        except httpx.TimeoutException:
            raise ConnectionError("request timed out. The backend is taking too long to respond.")
        except Exception as e:
            raise ConnectionError(f"{type(e).__name__}: {e}")
