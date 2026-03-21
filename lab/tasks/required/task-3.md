# Navigation and Queries

Slash commands are useful, but users need a smooth way to discover what the bot can do and move between common actions.

In this task, you improve the bot's command flow, add inline buttons for the most common actions, and make the bot handle ambiguous requests by asking a clarifying question instead of guessing.

## Requirements targeted

- **P1.1** Inline keyboard buttons
- **P1.2** Better command discovery
- **P1.3** Clarifying prompts for ambiguous requests
- **P1.4** Multi-step responses built from existing backend endpoints

## What you will build

A more helpful bot experience:

- `/start` shows a welcome message and buttons
- `/help` lists the available commands
- common commands are reachable from buttons
- ambiguous input like `lab 4` produces a follow-up question
- multi-step answers combine multiple backend calls in a single response

## Scenarios

**Single action:**

| Message                    | Behavior                                  |
| -------------------------- | ----------------------------------------- |
| `/start`                   | Shows welcome text and buttons            |
| `/help`                    | Lists available commands                   |
| `/health`                  | Shows backend status                       |
| `/labs`                    | Lists available labs                       |
| `/scores lab-04`           | Shows per-task pass rates for lab 4        |

**Multi-step:**

| Message                               | Behavior                                         |
| ------------------------------------- | ------------------------------------------------ |
| `which lab is best?`                  | Uses backend data to compare labs                |
| `what are the top students in lab 3?` | Uses the right backend endpoint and formats it   |
| `compare lab 2 and lab 4`             | Pulls both results and summarizes the difference |

**Fallback:**

| Message  | Behavior                                             |
| -------- | ---------------------------------------------------- |
| `hello`  | Friendly greeting + button hints                     |
| `asdfgh` | "I didn't understand. Here's what I can do..."       |
| `lab 4`  | Asks what the user wants to see about lab 4          |

## Inline buttons

Add keyboard buttons so users can discover actions without typing. For example, after `/start`, show buttons for:

- `Health`
- `Labs`
- `Help`

Each button should map to an existing command or response path.

## Verify

### Test mode

```terminal
cd ~/se-toolkit-lab-7/bot
uv run bot.py --test "/start"
uv run bot.py --test "/help"
uv run bot.py --test "lab 4"
uv run bot.py --test "asdfgh"
```

### Expected behavior

- `/start` returns a welcome message with buttons or button hints
- `/help` lists all available commands
- `lab 4` asks a clarifying question
- `asdfgh` returns a helpful fallback response, not a crash

### Deploy and verify in Telegram

```terminal
cd ~/se-toolkit-lab-7 && git pull
cd bot && pkill -f "bot.py" 2>/dev/null; nohup uv run bot.py > bot.log 2>&1 &
```

In Telegram, try:

1. `/start` - should show the bot's welcome path
2. `/help` - should list commands
3. `lab 4` - should ask a clarifying question
4. `asdfgh` - should get a helpful response, not silence

## Acceptance criteria

### On `GitHub`

- [ ] [`Git workflow`](../../../wiki/git-workflow.md) followed (issue, branch, PR, review, merge).

### On `GitHub` on the `main` branch

- [ ] Source code contains keyboard/button setup.
- [ ] `/help` lists all available commands.
- [ ] Ambiguous input results in a clarifying question.
- [ ] Multi-step responses combine more than one backend call when needed.

### On the VM (REMOTE)

- [ ] `--test "/start"` returns a non-empty welcome message.
- [ ] `--test "/help"` lists commands.
- [ ] `--test "lab 4"` asks a clarifying question.
- [ ] `--test "asdfgh"` returns a helpful fallback message.
