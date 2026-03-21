"""
LLM Client service for intent routing.
Handles communication with the LLM API.
"""
import httpx
import json
from typing import Optional, List, Dict, Any


class LLMClient:
    """Client for interacting with the LLM API."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def chat(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Send a chat request to the LLM and get a response."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers,
                    json={
                        "model": self.model,
                        "messages": messages
                    },
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("choices", [{}])[0].get("message", {}).get("content")
                return None
        except Exception:
            return None

    async def classify_intent(self, user_message: str) -> Optional[str]:
        """
        Classify user intent and return the appropriate command with arguments.
        Returns a string like "/labs" or "/scores lab-04" or None if unclear.
        """
        prompt = f"""You are a Telegram bot assistant for an LMS (Learning Management System).

Classify the user's message into one of these commands:
- /start - Welcome message (when user says hello, hi, start)
- /help - List available commands (when user asks for help, what can you do)
- /health - Check backend status (when user asks if system is working, is backend up)
- /labs - List available labs (when user asks what labs exist, show labs)
- /scores <lab> - Get scores for a specific lab (when user asks about scores, grades, results for a lab)

Rules:
1. If the user mentions a specific lab (like "lab 1", "lab-04", "first lab"), include it in the command.
2. For scores-related questions, always include the lab number if mentioned.
3. If unclear, return /help.
4. Respond with ONLY the command, nothing else.

Examples:
- "What labs are available?" → /labs
- "Show me scores for lab 4" → /scores lab-04
- "Is the system working?" → /health
- "Hello!" → /start
- "Help me" → /help
- "What is my grade for the first lab?" → /scores lab-01
- "Check lab-03 results" → /scores lab-03

User message: "{user_message}"

Command:"""

        messages = [{"role": "user", "content": prompt}]
        result = await self.chat(messages)
        
        if result:
            # Clean up the response - extract just the command
            result = result.strip()
            # Remove any extra text after the command
            if "\n" in result:
                result = result.split("\n")[0].strip()
            return result
        
        return None

    async def extract_lab_number(self, user_message: str) -> Optional[str]:
        """
        Extract lab number/ID from user message.
        Returns lab identifier like "lab-01" or None.
        """
        prompt = f"""Extract the lab number or identifier from this message.
Respond with ONLY the lab ID in format "lab-XX" (e.g., "lab-01", "lab-04").
If no lab is mentioned, respond with "none".

Message: "{user_message}"

Lab ID:"""

        messages = [{"role": "user", "content": prompt}]
        result = await self.chat(messages)
        
        if result and result.strip().lower() != "none":
            return result.strip()
        return None
