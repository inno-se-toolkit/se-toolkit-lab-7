# SE Toolkit Bot Development Plan

## Overview

This document outlines the development plan for the SE Toolkit Telegram Bot, which provides students with quick access to their lab scores, backend health status, and general course information through a conversational interface.

## Task 1: Project Scaffold (Current Task)

Create the basic project structure with a testable handler architecture. The key design principle is **separation of concerns**: handlers are pure functions that don't know about Telegram, making them easily testable via the `--test` mode. This task establishes:
- `bot/` directory with proper Python package structure
- Entry point (`bot.py`) with CLI test mode
- Handler modules in `handlers/` directory
- Configuration loading from environment files
- Dependencies managed via `pyproject.toml` and `uv`

## Task 2: Backend Integration

Implement real backend connectivity for the `/health` and `/scores` commands:
- Create `services/lms_client.py` for LMS API communication
- Create `services/health_checker.py` for backend status verification
- Update handlers to fetch real data instead of returning placeholders
- Add error handling for API failures and network issues
- Implement caching to reduce API calls

## Task 3: Intent Routing

Add natural language understanding for general queries:
- Integrate LLM for intent classification
- Map user queries to appropriate handlers (e.g., "what labs are available" → `/labs`)
- Create fallback responses for unrecognized intents
- Implement context-aware responses for follow-up questions

## Task 4: Deployment

Prepare the bot for production deployment:
- Create Docker configuration for containerized deployment
- Set up environment-specific configuration management
- Implement logging and monitoring
- Add health check endpoints
- Document deployment procedures for the VM

## Architecture Decisions

1. **Testable Handlers**: All command logic is in pure functions that take input and return text. This enables offline testing without Telegram.
2. **Environment-based Configuration**: Secrets are loaded from `.env.bot.secret`, with `.env.bot.example` as a template.
3. **Dependency Isolation**: Bot dependencies are separate from the backend/frontend via `pyproject.toml`.
4. **Progressive Enhancement**: Start with placeholder responses, then add real functionality in subsequent tasks.
