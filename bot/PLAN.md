# LMS Telegram Bot - Development Plan

## Overview

This document outlines the implementation plan for building a Telegram bot that interfaces with the LMS (Learning Management System) backend. The bot allows users to check system health, browse labs and scores, and ask questions in plain language using an LLM for intent understanding.

## Architecture

### Separation of Concerns

The bot uses a **layered architecture** where handlers are separated from the Telegram transport layer. Handlers are pure functions that take input and return text. They don't know about Telegram, which makes them:
- Testable via `--test` mode without a Telegram connection
- Testable via unit tests
- Reusable across different entry points (Telegram, CLI, tests)

### Directory Structure

```
bot/
├── bot.py              # Entry point (Telegram startup + --test mode)
├── config.py           # Environment variable loading from .env.bot.secret
├── handlers/           # Command handlers (no Telegram dependency)
│   ├── __init__.py
│   └── command_handlers.py
├── services/           # External service clients (API, LLM)
├── pyproject.toml      # Bot dependencies
└── PLAN.md             # This file
```

## Task 1: Plan and Scaffold

**Goal:** Create project structure with testable handler architecture.

**Approach:**
1. Create `bot/` directory with entry point `bot.py`
2. Implement `--test` mode that calls handlers directly
3. Separate handlers into `handlers/` package (no Telegram imports)
4. Create `config.py` for loading environment variables
5. Define dependencies in `pyproject.toml` using `uv`

**Verification:** Run `uv run bot.py --test "/command"` for each command and verify output.

## Task 2: Backend Integration

**Goal:** Connect handlers to the LMS backend API.

**Approach:**
1. Create `services/api_client.py` with Bearer token authentication
2. Update handlers to call the API instead of returning placeholders
3. Handle API errors gracefully (backend down → friendly message, not crash)
4. Load `LMS_API_BASE_URL` and `LMS_API_KEY` from `.env.bot.secret`

**Endpoints to integrate:**
- `GET /health` → `/health` command
- `GET /items/` → `/labs` command (list labs)
- `GET /analytics/{item_id}` → `/scores <lab>` command

**Verification:** Commands return real data from the backend.

## Task 3: Intent-Based Natural Language Routing

**Goal:** Allow users to ask questions in plain language.

**Approach:**
1. Create `services/llm_client.py` for LLM API interaction
2. Define tool descriptions for each backend endpoint
3. Implement intent router that sends user messages to LLM
4. LLM decides which tool to call based on tool descriptions
5. Execute the chosen tool and return results to user

**Key insight:** The LLM reads tool descriptions to decide which to call. Description quality matters more than prompt engineering.

**Verification:** Ask "what labs are available" and get the same response as `/labs`.

## Task 4: Containerize and Document

**Goal:** Deploy the bot alongside the backend using Docker.

**Approach:**
1. Create `Dockerfile` for the bot
2. Add bot as a service in `docker-compose.yml`
3. Configure container networking (containers use service names, not `localhost`)
4. Document deployment in README

**Key insight:** Docker containers communicate via service names defined in `docker-compose.yml`, not `localhost`.

**Verification:** Bot responds in Telegram after deployment.

## Environment Configuration

The bot reads configuration from `.env.bot.secret`:

```
BOT_TOKEN=<telegram-bot-token>
LMS_API_BASE_URL=http://backend:8000
LMS_API_KEY=<lms-api-key>
LLM_API_KEY=<llm-api-key>
LLM_API_MODEL=coder-model
LLM_API_BASE_URL=<llm-api-url>
```

## Testing Strategy

1. **Unit tests:** Test handlers in isolation
2. **Test mode:** `--test` flag for manual testing without Telegram
3. **Integration tests:** Test API client with real backend
4. **Manual testing:** Deploy to VM and test in Telegram

## Git Workflow

For each task:
1. Create issue describing the work
2. Create branch: `task-1-scaffold`, `task-2-backend`, etc.
3. Commit changes with meaningful messages
4. Create PR referencing issue (`Closes #...`)
5. Partner review
6. Merge to main
