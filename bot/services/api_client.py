"""Async LMS backend client."""

import re
from typing import Any

import httpx


class BackendClientError(RuntimeError):
    """Raised when the backend request fails in a user-visible way."""


class BackendClient:
    """Small wrapper around the LMS backend REST API."""

    def __init__(self, base_url: str, api_key: str, timeout: float = 20.0) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""

        await self._client.aclose()

    async def get_items(self) -> list[dict[str, Any]]:
        return await self._request("GET", "/items/")

    async def get_learners(self) -> list[dict[str, Any]]:
        return await self._request("GET", "/learners/")

    async def get_scores(self, lab: str) -> list[dict[str, Any]]:
        return await self._request(
            "GET", "/analytics/scores", params={"lab": normalize_lab_id(lab)}
        )

    async def get_pass_rates(self, lab: str) -> list[dict[str, Any]]:
        return await self._request(
            "GET", "/analytics/pass-rates", params={"lab": normalize_lab_id(lab)}
        )

    async def get_timeline(self, lab: str) -> list[dict[str, Any]]:
        return await self._request(
            "GET", "/analytics/timeline", params={"lab": normalize_lab_id(lab)}
        )

    async def get_groups(self, lab: str) -> list[dict[str, Any]]:
        return await self._request(
            "GET", "/analytics/groups", params={"lab": normalize_lab_id(lab)}
        )

    async def get_top_learners(
        self, lab: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"limit": limit}
        if lab:
            params["lab"] = normalize_lab_id(lab)
        return await self._request("GET", "/analytics/top-learners", params=params)

    async def get_completion_rate(self, lab: str) -> dict[str, Any]:
        return await self._request(
            "GET", "/analytics/completion-rate", params={"lab": normalize_lab_id(lab)}
        )

    async def trigger_sync(self) -> dict[str, Any]:
        return await self._request("POST", "/pipeline/sync", json={})

    async def list_labs(self) -> list[dict[str, str]]:
        """Return lab records with normalized ids."""

        items = await self.get_items()
        labs = []
        for item in items:
            if item.get("type") != "lab":
                continue
            title = str(item.get("title", "")).strip()
            labs.append({"id": title_to_lab_id(title), "title": title})
        return sorted(labs, key=lambda row: row["id"])

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        try:
            response = await self._client.request(
                method, path, params=params, json=json
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            detail = _extract_error_detail(exc.response)
            raise BackendClientError(
                f"HTTP {exc.response.status_code} {exc.response.reason_phrase}. {detail}"
            ) from exc
        except httpx.ConnectError as exc:
            raise BackendClientError(
                f"connection refused for {self._client.base_url}. Check that the services are running."
            ) from exc
        except httpx.TimeoutException as exc:
            raise BackendClientError(
                f"request timed out while calling {self._client.base_url}{path}"
            ) from exc
        except httpx.HTTPError as exc:
            raise BackendClientError(str(exc)) from exc


def normalize_lab_id(value: str) -> str:
    """Normalize lab identifiers like 'lab 4' or 'Lab 04' to 'lab-04'."""

    cleaned = value.strip().lower()
    match = re.search(r"lab[-\s_]*0*(\d+)", cleaned)
    if match:
        return f"lab-{int(match.group(1)):02d}"
    return cleaned


def title_to_lab_id(title: str) -> str:
    """Convert a lab title to the expected lab id format."""

    match = re.search(r"lab\s+0*(\d+)", title.lower())
    if match:
        return f"lab-{int(match.group(1)):02d}"
    return title.lower().replace(" ", "-")


def _extract_error_detail(response: httpx.Response) -> str:
    """Render a short, user-visible backend error detail."""

    try:
        payload = response.json()
    except ValueError:
        text = response.text.strip()
        return text[:200] if text else "The backend returned an empty error response."

    if isinstance(payload, dict):
        for key in ("detail", "message", "error"):
            if key in payload:
                return str(payload[key])
    return "The backend returned an unexpected error response."
