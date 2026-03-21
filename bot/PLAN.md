# Bot Development Plan

## Architecture

The bot is split into three layers:

1. **Handlers** (`handlers/commands.py`) — pure async functions that take arguments and return strings. No Telegram dependency. This makes them directly testable via `--test` mode and in unit tests.
2. **Services** (`services/lms.py`) — `httpx` async client wrapping the LMS backend API. Handlers call services; services never know about Telegram.
3. **Entry point** (`bot.py`) — wires handlers to either Telegram (aiogram polling) or stdout (`--test` mode).

## Task breakdown

### Task 1 — Scaffold
- Create `bot/`, `handlers/`, `services/` structure.
- Implement `--test` mode: parse command string, dispatch to handler, print result, exit 0.
- Handlers return placeholder text initially.

### Task 2 — Backend integration
- Implement `services/lms.py` with `httpx` calls to `/items/` and `/analytics/pass-rates`.
- Implement real handlers: `/health`, `/labs`, `/scores <lab>`.
- Error handling: catch `httpx.ConnectError` and `HTTPStatusError`, return friendly messages that include the actual error detail.

### Task 3 — Intent routing (P1)
- Add `services/llm.py` wrapping the OpenAI-compatible LLM API.
- Define tool schemas for all 9 backend endpoints.
- Plain-text messages go through the LLM which selects and calls the right tool, then formats the result.

### Task 4 — Containerize
- Write `bot/Dockerfile` using `uv` to install dependencies.
- Add `bot` service to `docker-compose.yml` with `env_file: .env.bot.secret`.
- Update README with deployment instructions.

## Testing strategy

Every command is verified via `--test` mode before deploying to Telegram. This catches logic errors without needing a live bot token. Edge cases (missing args, non-existent lab, backend down) are tested explicitly.
