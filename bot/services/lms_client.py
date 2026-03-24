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
                f"{self.base_url}/items/",  # Добавлен слеш в конце
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            # Если данные пришли как список, возвращаем как есть
            if isinstance(data, list):
                return data
            # Если как словарь с ключом 'items'
            return data.get('items', [])
    
    async def get_labs(self) -> List[Dict[str, Any]]:
        """Get only labs (items with type 'lab')."""
        items = await self.get_items()
        # Фильтруем лабы - проверяем разные возможные поля
        labs = []
        for item in items:
            # Проверяем наличие поля type или lab_id
            item_type = item.get('type') or item.get('item_type') or item.get('category')
            if item_type and 'lab' in str(item_type).lower():
                labs.append(item)
            # Также проверяем, если есть поле 'lab_name' или 'name'
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
            # Если данные пришли как список, преобразуем в нужный формат
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
