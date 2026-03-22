# Lab 7 — Build a Telegram Bot Client

[Sync your fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork-branch-from-the-command-line) regularly — the lab gets updated.

## Product brief

> Build a Telegram bot that lets users interact with the LMS backend through chat. Users should be able to check system health, browse labs and scores, and get quick guidance about the backend. Deploy it alongside the existing backend on the VM.

This lab is about turning a product brief into a working Telegram client.

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  Telegram    │────▶│  Your Bot                        │   │
│  │  User        │◀────│  (aiogram / python-telegram-bot) │   │
│  └──────────────┘     └──────┬───────────────────────────┘   │
│                              │                               │
│                              │ slash commands                │
│                              ├───────▶ /start, /help         │
│                              ├───────▶ /health, /labs        │
│                              ├───────▶ /scores <lab>         │
│                              │                               │
│                              ▼                               │
│                     LMS Backend (FastAPI + PostgreSQL)       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Requirements

### P0 — Must have

1. Testable handler architecture — handlers work without Telegram
2. CLI test mode: `cd bot && uv run bot.py --test "/command"` prints response to stdout
3. `/start` — welcome message
4. `/help` — lists all available commands
5. `/health` — calls backend, reports up/down status
6. `/labs` — lists available labs
7. `/scores <lab>` — per-task pass rates
8. Error handling — backend down produces a friendly message, not a crash

### P1 — Should have

1. Inline keyboard buttons for common actions
2. Better formatting for long bot responses
3. Multi-step questions answered by combining backend endpoints

### P2 — Nice to have

1. Response caching
2. Conversation context
3. Rich formatting such as tables or images

### P3 — Deployment

1. Bot containerized with Dockerfile
2. Added as service in `docker-compose.yml`
3. Deployed and running on VM
4. README documents deployment

## Learning advice

Notice the progression above: **product brief** (vague customer ask) → **prioritized requirements** (structured) → **task specifications** (precise deliverables + acceptance criteria). This is how engineering work flows.

You are not following step-by-step instructions — you are building a product. The learning comes from planning, building, testing, and debugging iteratively.

## Learning outcomes

By the end of this lab, you should be able to say:

1. I turned a vague product brief into a working Telegram bot.
2. I can explain how the bot talks to the LMS backend.
3. I can add new commands and deployment settings without breaking the app.

## Tasks

### Prerequisites

1. Complete the [lab setup](./lab/setup/setup-simple.md#lab-setup)

> **Note**: First time in this course? Do the [full setup](./lab/setup/setup-full.md#lab-setup) instead.

### Required

1. [Plan and Scaffold](./lab/tasks/required/task-1.md) — P0: project structure + `--test` mode
2. [Backend Integration](./lab/tasks/required/task-2.md) — P0: slash commands + real data
3. [Navigation and Queries](./lab/tasks/required/task-3.md) — P1: smarter command handling
4. [Containerize and Document](./lab/tasks/required/task-4.md) — P3: containerize + deploy

### Optional

1. [Extra Bot Features](./lab/tasks/optional/task-1.md)
