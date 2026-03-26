#!/usr/bin/env python3
"""Telegram bot entry point with --test mode for offline verification.

Usage:
    uv run bot.py --test "/start"    # Test mode - prints response to stdout
    uv run bot.py                    # Normal mode - connects to Telegram
"""

import asyncio
import sys
from pathlib import Path

# Add bot directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from handlers import (
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_start,
)

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import load_config

# Command router - maps command strings to handler functions
COMMAND_HANDLERS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
    "/scores": handle_scores,
}


def route_command(command: str) -> str:
    """Route a command string to the appropriate handler.

    Args:
        command: The command string (e.g., "/start" or "/scores lab-04")

    Returns:
        The handler's response string
    """
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd in COMMAND_HANDLERS:
        return COMMAND_HANDLERS[cmd](args)
    else:
        return f"Unknown command: {cmd}. Use /help to see available commands."


def run_test_mode(command: str) -> None:
    """Run the bot in test mode - print response and exit.

    Args:
        command: The command to test (e.g., "/start")
    """
    response = route_command(command)
    print(response)
    sys.exit(0)


async def handle_telegram_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    command: str,
) -> None:
    """Handle a Telegram command."""
    args = " ".join(context.args) if context.args else ""
    full_command = f"{command} {args}".strip()
    response = route_command(full_command)
    await update.message.reply_text(response)


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle /start command."""
    await handle_telegram_command(update, context, "/start")


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle /help command."""
    await handle_telegram_command(update, context, "/help")


async def health_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle /health command."""
    await handle_telegram_command(update, context, "/health")


async def labs_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle /labs command."""
    await handle_telegram_command(update, context, "/labs")


async def scores_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle /scores command."""
    await handle_telegram_command(update, context, "/scores")


async def handle_text_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle plain text messages."""
    text = update.message.text
    await update.message.reply_text(
        "I understand commands like /start, /help, /health, /labs, /scores. "
        "Use /help to see available commands."
    )


def run_telegram_mode() -> None:
    """Run the bot in Telegram mode - connect to Telegram API."""
    config = load_config()

    if not config.bot_token:
        print("Error: BOT_TOKEN not found in .env.bot.secret")
        sys.exit(1)

    # Build application
    application = Application.builder().token(config.bot_token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("health", health_command))
    application.add_handler(CommandHandler("labs", labs_command))
    application.add_handler(CommandHandler("scores", scores_command))

    # Add text message handler for non-command messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    # Start the bot using asyncio.run() for Python 3.14 compatibility
    print("Starting bot...")

    async def run_bot() -> None:
        """Run the bot polling."""
        async with application:
            await application.start()
            await application.updater.start_polling()
            # Keep running until stopped
            while True:
                await asyncio.sleep(1)

    asyncio.run(run_bot())


def main() -> None:
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Usage: uv run bot.py --test \"/command [args]\"")
            sys.exit(1)
        command = " ".join(sys.argv[2:])
        run_test_mode(command)
    else:
        run_telegram_mode()


if __name__ == "__main__":
    main()
