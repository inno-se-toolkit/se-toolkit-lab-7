# Bot Development Plan

## Overview
This document outlines the development strategy for the SE Toolkit Telegram Bot. The architecture prioritizes testability and separation of concerns, ensuring business logic is decoupled from the Telegram transport layer.

## Phase 1: Scaffolding (Current Task)
- Establish `bot/` directory structure with `handlers`, `services`, and `config`.
- Implement `--test` CLI mode to verify handler logic without Telegram API dependencies.
- Configure `uv` for dependency management via `pyproject.toml`.
- Define environment variable standards (`.env.bot.example` vs `.env.bot.secret`).

## Phase 2: Backend Integration (Completed)
- ✅ Implemented `services/lms_client.py` with async httpx client
- ✅ Added error handling that shows actual errors without raw tracebacks
- ✅ Connected handlers to real backend endpoints:
  - `/health` → GET /items/ for health check
  - `/labs` → GET /items/ parsed for unique labs
  - `/scores <lab>` → GET /analytics/pass-rates?lab=<lab>
- ✅ All commands work in both `--test` mode and Telegram mode
- ✅ Natural language fallback with keyword matching
- ✅ Proper async/await handling in Telegram handlers

## Phase 3: Intent Routing & Logic (Next)
- Implement smarter NLP intent detection (beyond keyword matching)
- Add caching layer for API responses to reduce backend load
- Support pagination for large lab lists
- Add user context (remember last viewed lab, etc.)

## Phase 4: Deployment & Monitoring (Future)
- Containerize bot with Docker
- Add structured JSON logging for production
- Implement health check endpoint for orchestration
- Set up CI/CD with automated tests

## Testing Strategy
- Unit tests for handlers (pure functions).
- Integration tests for services (mocked HTTP).
- Manual verification via `--test` mode before every commit.
- End-to-end testing in a private Telegram group before public release.