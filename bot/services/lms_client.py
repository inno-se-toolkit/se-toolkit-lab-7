"""LMS API client for the bot."""
import httpx
from typing import List, Dict, Any


class LMSClient:
    """Client for LMS backend API."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    async def get_items(self) -> List[Dict[str, Any]]:
        """Get all items (labs and tasks)."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/items/",
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return data
            return data.get('items', [])
    
    async def get_labs(self) -> List[Dict[str, Any]]:
        """Get only labs (items with type 'lab')."""
        items = await self.get_items()
        labs = []
        for item in items:
            item_type = item.get('type') or item.get('item_type') or item.get('category')
            if item_type and 'lab' in str(item_type).lower():
                labs.append(item)
            elif 'lab' in str(item.get('name', '')).lower():
                labs.append(item)
        return labs
    
    async def get_pass_rates(self, lab_name: str) -> Dict[str, Any]:
        """Get pass rates for a specific lab."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/analytics/pass-rates",
                params={"lab": lab_name},
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return {"tasks": data}
            return data
    
    async def health_check(self) -> tuple:
        """Check if backend is healthy."""
        try:
            items = await self.get_items()
            return True, "Backend is healthy", len(items)
        except httpx.ConnectError:
            return False, f"Connection refused to {self.base_url}", 0
        except httpx.TimeoutException:
            return False, f"Timeout connecting to {self.base_url}", 0
        except httpx.HTTPStatusError as e:
            return False, f"HTTP {e.response.status_code}: {e.response.text[:100]}", 0
        except Exception as e:
            return False, f"Error: {str(e)}", 0
    
    async def get_learners(self) -> List[Dict[str, Any]]:
        """Get enrolled learners."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/learners/",
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_scores(self, lab: str) -> Dict[str, Any]:
        """Get score distribution for a lab."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/analytics/scores",
                params={"lab": lab},
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_timeline(self, lab: str) -> Dict[str, Any]:
        """Get submission timeline for a lab."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/analytics/timeline",
                params={"lab": lab},
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_groups(self, lab: str) -> Dict[str, Any]:
        """Get per-group performance for a lab."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/analytics/groups",
                params={"lab": lab},
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_top_learners(self, lab: str, limit: int = 5) -> Dict[str, Any]:
        """Get top learners for a lab."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/analytics/top-learners",
                params={"lab": lab, "limit": limit},
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_completion_rate(self, lab: str) -> Dict[str, Any]:
        """Get completion rate for a lab."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{self.base_url}/analytics/completion-rate",
                params={"lab": lab},
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    
    async def trigger_sync(self) -> Dict[str, Any]:
        """Trigger ETL sync."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                f"{self.base_url}/pipeline/sync",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
