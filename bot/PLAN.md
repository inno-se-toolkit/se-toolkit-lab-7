# Development Plan — LMS Telegram Bot

## Overview

This plan describes the approach for building a Telegram bot that provides chat-based access to the LMS backend. The bot supports both slash commands (`/start`, `/help`, `/health`, `/labs`, `/scores`) and natural language queries ("which lab has the lowest pass rate?") powered by an LLM.

## Architecture

### Separation of Concerns

The bot follows a layered architecture:

1. **Handlers layer** (`bot/handlers/`) — Pure functions that take input and return formatted text. They have no dependency on Telegram, making them testable via `--test` mode and reusable in unit tests.

2. **Services layer** (`bot/services/`) — API clients for external dependencies:
   - `LMSClient` — HTTP client for the backend API with Bearer token authentication
   - `LLMClient` — Client for the Qwen Code API with tool-calling support

3. **Transport layer** (`bot/bot.py`) — aiogram-based Telegram bot that:
   - Routes slash commands to handlers
   - Runs the intent router for plain text messages
   - Supports `--test` mode for offline verification

4. **Configuration** (`bot/config.py`) — Loads secrets from `.env.bot.secret` using pydantic-settings.

### Test Mode

The `--test` flag enables offline testing without Telegram:

```bash
uv run bot.py --test "/start"
uv run bot.py --test "which lab has the lowest pass rate?"
```

Handlers are called directly, responses print to stdout, and the bot exits. This allows rapid iteration without deploying to Telegram.

## Task Breakdown

### Task 1: Scaffold

- Create `bot/bot.py` with `--test` mode and placeholder handlers
- Create `bot/handlers/` directory with handler modules
- Create `bot/config.py` for environment loading
- Create `bot/PLAN.md` (this file)

### Task 2: Backend Integration

- Implement real handlers for `/start`, `/help`, `/health`, `/labs`, `/scores`
- Build `LMSClient` service with proper error handling
- Add friendly error messages when backend is down (include actual error, not raw tracebacks)
- Test all commands via `--test` mode and deploy to Telegram

### Task 3: Intent-Based Natural Language Routing

- Build `LLMClient` service with tool-calling support
- Define 9 backend endpoints as LLM tools with clear descriptions
- Implement intent router: user message → LLM decides tools → execute → summarize
- Add inline keyboard buttons for common actions
- Support multi-step reasoning (chaining API calls)
- Handle fallbacks for gibberish and ambiguous queries

### Task 4: Containerize and Document

- Create `bot/Dockerfile` using `uv sync` from `pyproject.toml`
- Add `bot` service to `docker-compose.yml` with proper networking
- Update project README with deployment instructions
- Deploy bot as Docker container alongside backend

## Key Design Decisions

1. **Handlers are pure functions** — This enables testing without Telegram and keeps logic separate from transport.

2. **Environment variables for secrets** — URLs and API keys come from `.env.bot.secret`, not hardcoded values.

3. **LLM decides tool calls** — No regex or keyword matching for routing. The LLM reads tool descriptions and decides which to call. If it picks the wrong tool, fix the description — don't bypass the LLM.

4. **Docker networking** — Inside Docker, the bot uses `http://backend:8000` (service name), not `localhost:42002`.

5. **Error messages include context** — When backend fails, show the actual error (e.g., "connection refused") so users can debug, but don't show raw Python tracebacks.

## Testing Strategy

1. **Unit testing** — Handlers can be tested directly since they're pure functions.
2. **Test mode** — `--test` flag verifies end-to-end without Telegram.
3. **Telegram testing** — Deploy and verify real user experience.
4. **Edge cases** — Test missing arguments, non-existent labs, backend down, gibberish input.

## Deployment

The bot runs as a Docker service alongside the backend:

```bash
docker compose --env-file .env.docker.secret up --build -d
```

Environment variables:
- `BOT_TOKEN` — Telegram bot authentication
- `LMS_API_BASE_URL` — Backend URL (use `http://backend:8000` in Docker)
- `LMS_API_KEY` — Backend API key
- `LLM_API_BASE_URL` — Qwen Code API URL
- `LLM_API_KEY` — Qwen API key
- `LLM_API_MODEL` — Model name (e.g., `coder-model`)
