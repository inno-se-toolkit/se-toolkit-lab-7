"""LLM client for Qwen Code API."""

import httpx
import json
from typing import Optional, List, Dict, Any


class LLMClient:
    """Client for Qwen Code API with tool calling support."""

    def __init__(self, base_url: str, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        # Remove trailing /v1 if present
        self.base_url = base_url.rstrip("/")
        if self.base_url.endswith("/v1"):
            self.base_url = self.base_url[:-3]

    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Send chat request with optional tools."""
        url = f"{self.base_url}/v1/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        try:
            with httpx.Client() as client:
                response = client.post(url, headers=self.headers, json=payload, timeout=60.0)
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            raise ConnectionError(f"LLM connection refused ({self.base_url})")
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f"LLM HTTP {e.response.status_code}: {e.response.text}")
        except httpx.TimeoutException:
            raise ConnectionError("LLM request timed out")
        except Exception as e:
            raise ConnectionError(f"LLM error: {type(e).__name__}: {e}")
