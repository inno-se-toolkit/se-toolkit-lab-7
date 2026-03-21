"""
LMS API Client - Handles all communication with the backend.
Designed to be testable and mockable.
"""
import httpx
import logging
from typing import Optional, Dict, Any, List
from config import Config

logger = logging.getLogger(__name__)

class LMSClientError(Exception):
    """Base exception for LMS client errors."""
    pass

class LMSClient:
    """Client for the LMS backend API."""
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or Config.LMS_API_BASE_URL
        self.api_key = api_key or Config.LMS_API_KEY
        self._client: Optional[httpx.AsyncClient] = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Return authorization headers."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self._get_headers(),
                timeout=10.0  # 10 second timeout
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check backend health by calling GET /items/
        Returns: {"status": "healthy", "item_count": N} or {"status": "error", "error": "..."}
        """
        try:
            client = await self._get_client()
            response = await client.get("/items/")
            response.raise_for_status()
            data = response.json()
            
            # Handle both list and dict responses
            if isinstance(data, list):
                count = len(data)
            elif isinstance(data, dict) and "items" in data:
                count = len(data["items"])
            else:
                count = len(data) if data else 0
                
            return {"status": "healthy", "item_count": count}
            
        except httpx.ConnectError as e:
            return {"status": "error", "error": f"connection refused ({self.base_url}). Check that the services are running."}
        except httpx.HTTPStatusError as e:
            return {"status": "error", "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."}
        except httpx.RequestError as e:
            return {"status": "error", "error": f"request failed: {str(e)}"}
        except Exception as e:
            # Log full traceback for debugging, but return user-friendly message
            logger.exception("Unexpected error in health_check")
            return {"status": "error", "error": f"unexpected error: {type(e).__name__} - {str(e)}"}
    
    async def get_labs(self) -> Dict[str, Any]:
        """
        Fetch available labs from GET /items/
        Returns: {"labs": [...], "error": "..."} 
        """
        try:
            client = await self._get_client()
            response = await client.get("/items/")
            response.raise_for_status()
            data = response.json()
            
            # Parse items - adjust based on your actual API response structure
            items = data if isinstance(data, list) else data.get("items", [])
            
            # Extract unique labs (assuming each item has a 'lab' or 'lab_id' field)
            labs = []
            seen = set()
            for item in items:
                lab_id = item.get("lab_id") or item.get("lab") or item.get("lab_name")
                if lab_id and lab_id not in seen:
                    seen.add(lab_id)
                    labs.append({
                        "id": lab_id,
                        "name": item.get("name") or item.get("title") or lab_id,
                        "description": item.get("description", "")
                    })
            
            return {"labs": labs}
            
        except httpx.ConnectError:
            return {"error": f"connection refused ({self.base_url}). Check that the services are running."}
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."}
        except Exception as e:
            logger.exception("Unexpected error in get_labs")
            return {"error": f"unexpected error: {type(e).__name__} - {str(e)}"}
    
    async def get_pass_rates(self, lab_id: str) -> Dict[str, Any]:
        """
        Fetch per-task pass rates for a lab from GET /analytics/pass-rates?lab=<lab_id>
        Returns: {"tasks": [{"name": "...", "pass_rate": N, "attempts": M}], "error": "..."}
        """
        try:
            client = await self._get_client()
            response = await client.get("/analytics/pass-rates", params={"lab": lab_id})
            response.raise_for_status()
            data = response.json()
            
            # Parse response - adjust based on your actual API structure
            tasks = []
            if isinstance(data, list):
                for item in data:
                    tasks.append({
                        "name": item.get("task_name") or item.get("name") or item.get("task"),
                        "pass_rate": item.get("pass_rate") or item.get("percentage"),
                        "attempts": item.get("attempts") or item.get("count")
                    })
            elif isinstance(data, dict):
                raw_tasks = data.get("tasks") or data.get("pass_rates") or []
                for item in raw_tasks:
                    tasks.append({
                        "name": item.get("task_name") or item.get("name") or item.get("task"),
                        "pass_rate": item.get("pass_rate") or item.get("percentage"),
                        "attempts": item.get("attempts") or item.get("count")
                    })
            
            return {"tasks": tasks, "lab_id": lab_id}
            
        except httpx.ConnectError:
            return {"error": f"connection refused ({self.base_url}). Check that the services are running."}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": f"lab '{lab_id}' not found. Use /labs to see available labs."}
            return {"error": f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."}
        except Exception as e:
            logger.exception(f"Unexpected error in get_pass_rates for lab {lab_id}")
            return {"error": f"unexpected error: {type(e).__name__} - {str(e)}"}

# Singleton instance for easy import
_lms_client: Optional[LMSClient] = None

def get_lms_client() -> LMSClient:
    """Get or create the singleton LMS client."""
    global _lms_client
    if _lms_client is None:
        _lms_client = LMSClient()
    return _lms_client