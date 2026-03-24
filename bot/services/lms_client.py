"""
LMS Backend API client.

Uses httpx for HTTP requests with Bearer token authentication.
All errors are caught and returned as user-friendly messages that include
the actual error (for debugging) without raw tracebacks.
"""

import httpx


class LMSClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str) -> None:
        """Initialize the LMS client.
        
        Args:
            base_url: Backend base URL (e.g., http://localhost:42002)
            api_key: API key for Bearer token authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10.0,
        )

    def health_check(self) -> tuple[bool, str]:
        """Check if the backend is healthy.
        
        Returns:
            Tuple of (is_healthy, message)
        """
        try:
            response = self._client.get("/items/")
            response.raise_for_status()
            items = response.json()
            count = len(items) if isinstance(items, list) else "unknown"
            return (True, f"Backend is healthy. {count} items available.")
        except httpx.ConnectError as e:
            return (False, f"Backend error: connection refused ({self.base_url}). Check that the services are running.")
        except httpx.HTTPStatusError as e:
            return (False, f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.")
        except httpx.HTTPError as e:
            return (False, f"Backend error: {str(e)}. Check that the backend is running.")
        except Exception as e:
            return (False, f"Backend error: {str(e)}.")

    def get_items(self) -> tuple[bool, list | str]:
        """Get all items (labs and tasks).
        
        Returns:
            Tuple of (success, items_list or error_message)
        """
        try:
            response = self._client.get("/items/")
            response.raise_for_status()
            items = response.json()
            return (True, items if isinstance(items, list) else [])
        except httpx.ConnectError:
            return (False, f"Backend error: connection refused ({self.base_url}).")
        except httpx.HTTPStatusError as e:
            return (False, f"Backend error: HTTP {e.response.status_code}.")
        except Exception as e:
            return (False, f"Backend error: {str(e)}.")

    def get_pass_rates(self, lab: str) -> tuple[bool, list | str]:
        """Get pass rates for a specific lab.
        
        Args:
            lab: Lab identifier (e.g., 'lab-04')
            
        Returns:
            Tuple of (success, pass_rates_list or error_message)
        """
        try:
            response = self._client.get("/analytics/pass-rates", params={"lab": lab})
            response.raise_for_status()
            data = response.json()
            # Handle both list and dict responses
            if isinstance(data, dict):
                data = [data]
            return (True, data if isinstance(data, list) else [])
        except httpx.ConnectError:
            return (False, f"Backend error: connection refused ({self.base_url}).")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return (False, f"Lab '{lab}' not found. Use /labs to see available labs.")
            return (False, f"Backend error: HTTP {e.response.status_code}.")
        except Exception as e:
            return (False, f"Backend error: {str(e)}.")
