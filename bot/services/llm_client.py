"""LLM client for intent routing and natural language queries."""

import httpx


class LLMClient:
    """Client for the LLM API (Qwen Code)."""

    def __init__(self, api_key: str, base_url: str, model: str):
        """Initialize the LLM client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL of the LLM API
            model: Model name to use
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0,
        )

    def chat(self, messages: list[dict]) -> str:
        """Send a chat completion request.
        
        Args:
            messages: List of message dicts with role and content
            
        Returns:
            Response text from the LLM
        """
        try:
            response = self._client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except httpx.RequestError as e:
            return f"LLM error: {e}"

    def detect_intent(self, user_message: str) -> str:
        """Detect the intent of a user message.
        
        Args:
            user_message: The user's message
            
        Returns:
            Intent name (e.g., "start", "help", "health", "labs", "scores")
        """
        system_prompt = (
            "You are an intent classifier for a Telegram bot. "
            "Classify the user message into one of these intents: "
            "start, help, health, labs, scores, or general. "
            "Respond with ONLY the intent name."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        
        response = self.chat(messages)
        return response.strip().lower()

    def answer_query(self, user_message: str, context: str = "") -> str:
        """Answer a natural language query.
        
        Args:
            user_message: The user's question
            context: Optional context data (e.g., lab info, scores)
            
        Returns:
            Answer text
        """
        system_prompt = (
            "You are a helpful assistant for a Software Engineering course. "
            "Answer questions about labs, scores, and submissions. "
            "Be concise and helpful."
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})
        
        messages.append({"role": "user", "content": user_message})
        
        return self.chat(messages)
