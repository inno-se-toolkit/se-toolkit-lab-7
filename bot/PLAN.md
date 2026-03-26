# Development Plan: LMS Telegram Bot

## Overview

This document outlines the implementation plan for the LMS Telegram bot, which provides students with access to lab information, scores, and Q&A capabilities through a natural language interface.

## Task 1: Project Scaffold (Current Task)

The foundation of the bot is a testable architecture where handlers are pure functions that take input and return text, with no dependency on Telegram. This separation of concerns allows the same handler logic to work from CLI test mode, unit tests, or the Telegram bot. The entry point (`bot.py`) supports a `--test` flag for offline verification without needing a bot token or network connection.

## Task 2: Backend Integration

Implement service layer components to communicate with the LMS backend API. The `APIClient` service will handle HTTP requests with Bearer token authentication, fetching lab data, scores, and student information. Handlers will call these services to return real data instead of placeholders. Error handling is critical here—network failures and API errors must be caught and reported gracefully to users.

## Task 3: Intent Routing with LLM

Add natural language understanding using an LLM. Instead of requiring slash commands, users can ask questions like "what labs are available?" The LLM will use tool descriptions to decide which handler to invoke. This requires careful prompt engineering and well-structured tool definitions so the model correctly maps user intent to bot functions.

## Task 4: Docker Deployment

Containerize the bot for deployment alongside the existing LMS infrastructure. The Docker configuration must handle environment variables properly, use service names for networking (not localhost), and integrate with the existing docker-compose setup. Health checks and proper logging will ensure the bot runs reliably in production.

## Key Architectural Decisions

1. **Handler separation**: Handlers are pure functions, making them testable without mocking Telegram.
2. **Environment-based config**: All secrets come from `.env.bot.secret`, never hardcoded.
3. **Service layer**: API and LLM clients are separate from handlers, following single responsibility.
4. **Test-first workflow**: The `--test` mode enables rapid iteration without deploying to Telegram.
