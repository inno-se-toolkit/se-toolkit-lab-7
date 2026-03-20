"""OpenAI-compatible LLM client for tool calling."""

from typing import Any

import httpx


class LLMClientError(RuntimeError):
    """Raised when the LLM API call fails."""


class LLMClient:
    """Thin wrapper over the OpenAI-compatible chat completions API."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None,
        model: str,
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""

        await self._client.aclose()

    async def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = "auto",
    ) -> dict[str, Any]:
        """Send a chat completion request and return the assistant message."""

        if not self._api_key:
            raise LLMClientError("LLM_API_KEY is not configured.")

        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice

        try:
            response = await self._client.post(
                "/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text.strip()[:300]
            raise LLMClientError(
                f"HTTP {exc.response.status_code} {exc.response.reason_phrase}: {detail}"
            ) from exc
        except httpx.ConnectError as exc:
            raise LLMClientError(
                f"connection refused for {self._client.base_url}. Check that the LLM API is running."
            ) from exc
        except httpx.TimeoutException as exc:
            raise LLMClientError("request to the LLM API timed out.") from exc
        except httpx.HTTPError as exc:
            raise LLMClientError(str(exc)) from exc

        payload = response.json()
        choices = payload.get("choices", [])
        if not choices:
            raise LLMClientError("LLM returned no choices.")
        message = choices[0].get("message")
        if not isinstance(message, dict):
            raise LLMClientError("LLM returned an invalid message payload.")
        return message
