# Task 2: Backend Integration

## Overview

Implement real backend connectivity for `/health` and `/scores` commands by integrating with the LMS API running on `http://localhost:42002`.

## Files to Create/Modify

### 1. Create `services/lms_client.py`

```python
"""LMS API client for fetching scores and health data."""

import httpx
from typing import Optional


class LMSClient:
    """Client for the LMS API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5.0,
        )

    def get_health(self) -> dict:
        """Get backend health status."""
        response = self._client.get("/health")
        response.raise_for_status()
        return response.json()

    def get_scores(self, lab_name: str) -> Optional[dict]:
        """Get scores for a specific lab."""
        try:
            response = self._client.get(f"/scores/{lab_name}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    def get_labs(self) -> list:
        """Get list of all available labs."""
        response = self._client.get("/labs")
        response.raise_for_status()
        return response.json()
```

### 2. Create `services/health_checker.py`

```python
"""Health check service for the bot."""

from typing import Optional
import httpx


def check_backend_health(base_url: str) -> dict:
    """Check if the backend is healthy.

    Args:
        base_url: The backend URL to check.

    Returns:
        Dict with status and details.
    """
    try:
        response = httpx.get(f"{base_url}/health", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "healthy",
                "details": data,
            }
        return {
            "status": "unhealthy",
            "details": f"Status code: {response.status_code}",
        }
    except httpx.ConnectError:
        return {
            "status": "unreachable",
            "details": "Cannot connect to backend",
        }
    except httpx.TimeoutException:
        return {
            "status": "timeout",
            "details": "Backend request timed out",
        }
```

### 3. Update `handlers/health.py`

```python
"""Handler for /health command."""

from services.health_checker import check_backend_health
from config import load_config


def handle_health() -> str:
    """Handle /health command."""
    config = load_config()
    lms_url = config.get("LMS_API_BASE_URL", "http://localhost:42002")

    result = check_backend_health(lms_url)

    if result["status"] == "healthy":
        return "✅ Backend is healthy\n\n" + str(result.get("details", ""))
    elif result["status"] == "unreachable":
        return "❌ Backend is unreachable\n\n" + result["details"]
    else:
        return f"⚠️ Backend status: {result['status']}\n\n" + result["details"]
```

### 4. Update `handlers/scores.py`

```python
"""Handler for /scores command."""

import httpx
from config import load_config


def handle_scores(lab_name: str = "") -> str:
    """Handle /scores command."""
    if not lab_name:
        return "📊 Scores: Please specify a lab (e.g., /scores lab-04)"

    config = load_config()
    base_url = config.get("LMS_API_BASE_URL", "http://localhost:42002")
    api_key = config.get("LMS_API_KEY", "")

    try:
        response = httpx.get(
            f"{base_url}/scores/{lab_name}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5.0,
        )

        if response.status_code == 404:
            return f"❌ Lab '{lab_name}' not found"

        response.raise_for_status()
        data = response.json()

        # Format the response
        lines = [f"📊 Scores for {lab_name}:"]
        if isinstance(data, dict):
            for key, value in data.items():
                lines.append(f"  • {key}: {value}")
        else:
            lines.append(str(data))

        return "\n".join(lines)

    except httpx.ConnectError:
        return "❌ Cannot connect to LMS API"
    except httpx.TimeoutException:
        return "❌ LMS API request timed out"
    except Exception as e:
        return f"❌ Error: {str(e)}"
```

### 5. Update `handlers/labs.py`

```python
"""Handler for /labs command."""

import httpx
from config import load_config


def handle_labs() -> str:
    """Handle /labs command."""
    config = load_config()
    base_url = config.get("LMS_API_BASE_URL", "http://localhost:42002")
    api_key = config.get("LMS_API_KEY", "")

    try:
        response = httpx.get(
            f"{base_url}/labs",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5.0,
        )
        response.raise_for_status()
        data = response.json()

        lines = ["📋 Available labs:"]
        if isinstance(data, list):
            for lab in data:
                if isinstance(lab, dict):
                    name = lab.get("name", lab.get("id", "unknown"))
                else:
                    name = str(lab)
                lines.append(f"  • {name}")
        else:
            lines.append(str(data))

        return "\n".join(lines)

    except httpx.ConnectError:
        return "❌ Cannot connect to LMS API"
    except httpx.TimeoutException:
        return "❌ LMS API request timed out"
    except Exception as e:
        return f"❌ Error: {str(e)}"
```

### 6. Update `pyproject.toml` - add httpx dependency

```toml
[project]
dependencies = [
    "python-telegram-bot>=21.0",
    "python-dotenv>=1.0.0",
    "httpx>=0.27.0",
]
```

## Testing

After implementing:

```bash
# Sync dependencies
uv sync

# Test commands
uv run bot.py --test "/health"
uv run bot.py --test "/labs"
uv run bot.py --test "/scores lab-04"

# Restart the bot
pkill -f "bot.py"
nohup uv run bot.py > bot.log 2>&1 &
```

## Acceptance Criteria

- [x] `/health` returns real backend status
- [x] `/scores <lab>` returns actual scores
- [x] `/labs` returns list of labs from backend
- [x] All handlers handle API errors gracefully
- [x] Dependencies install without errors
