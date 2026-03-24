"""
Service clients for external dependencies.

- LMSClient: HTTP client for the backend API with Bearer token auth
- LLMClient: Client for the Qwen Code API (Task 3)
"""

from .lms_client import LMSClient
from .llm_client import LLMClient

__all__ = ["LMSClient", "LLMClient"]
