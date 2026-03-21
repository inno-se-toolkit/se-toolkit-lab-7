# Bot Development Plan

## Overview
This document outlines the development strategy for the SE Toolkit Telegram Bot. The architecture prioritizes testability and separation of concerns, ensuring business logic is decoupled from the Telegram transport layer.

## Phase 1: Scaffolding (Current Task)
- Establish `bot/` directory structure with `handlers`, `services`, and `config`.
- Implement `--test` CLI mode to verify handler logic without Telegram API dependencies.
- Configure `uv` for dependency management via `pyproject.toml`.
- Define environment variable standards (`.env.bot.example` vs `.env.bot.secret`).

## Phase 2: Backend Integration
- Implement `services/lms_client.py` to interact with the existing backend API.
- Securely handle `LMS_API_KEY` and `LMS_API_BASE_URL` via config.
- Create `services/llm_client.py` for natural language intent processing.
- Ensure all service calls are mocked during unit testing.

## Phase 3: Intent Routing & Logic
- Expand `handlers/` to support complex commands (`/scores`, `/labs`).
- Implement natural language processing for queries like "what labs are available".
- Connect handlers to services: Handlers orchestrate, Services execute.
- Add error handling for API failures (timeouts, auth errors).

## Phase 4: Deployment & Monitoring
- Containerize the bot using Docker (align with existing `docker-compose.yml`).
- Set up production logging (JSON format, log levels).
- Configure CI/CD pipeline for automated testing before deployment.
- Implement health checks for orchestration tools.

## Testing Strategy
- Unit tests for handlers (pure functions).
- Integration tests for services (mocked HTTP).
- Manual verification via `--test` mode before every commit.
- End-to-end testing in a private Telegram group before public release.