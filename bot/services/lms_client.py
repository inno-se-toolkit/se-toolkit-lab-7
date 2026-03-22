"""LMS API client for fetching lab data and scores."""

import httpx


class LMSClient:
    """Client for the Learning Management Service API."""

    def __init__(self, base_url: str, api_key: str):
        """Initialize the LMS client.
        
        Args:
            base_url: Base URL of the LMS API
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10.0,
        )

    def health_check(self) -> bool:
        """Check if the backend is accessible.
        
        Returns:
            True if backend is reachable, False otherwise
        """
        try:
            response = self._client.get("/items/")
            return response.status_code == 200
        except httpx.RequestError:
            return False

    def get_items(self) -> list[dict]:
        """Get all items (labs, tasks, etc.).
        
        Returns:
            List of items from the API
        """
        try:
            response = self._client.get("/items/")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError:
            return []

    def get_labs(self) -> list[dict]:
        """Get all labs.
        
        Returns:
            List of lab items
        """
        items = self.get_items()
        return [item for item in items if item.get("type") == "lab"]

    def get_scores(self, user_id: int, lab_id: int | None = None) -> list[dict]:
        """Get scores for a user.
        
        Args:
            user_id: User ID (Telegram chat ID for now)
            lab_id: Optional specific lab ID
            
        Returns:
            List of score records
        """
        # TODO: Implement actual scores endpoint in Task 2
        return []
