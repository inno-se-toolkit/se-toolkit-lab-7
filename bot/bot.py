#!/usr/bin/env python3
"""SE Toolkit Telegram Bot entry point.

Supports two modes:
1. Test mode: `uv run bot.py --test "/command"` - prints response to stdout
2. Telegram mode: Connects to Telegram API and handles messages
"""

import sys
import argparse
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from config import load_config
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_general_query,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def parse_command(text: str) -> tuple[str, str]:
    """Parse command text into command and arguments.
    
    Args:
        text: The message text (e.g., "/scores lab-04" or "what labs are available")
        
    Returns:
        Tuple of (command, args)
    """
    text = text.strip()
    if text.startswith("/"):
        parts = text[1:].split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        return command, args
    return "", text


def run_test_mode(command_text: str) -> None:
    """Run in test mode - call handlers directly without Telegram.
    
    Args:
        command_text: The command to test (e.g., "/start" or "what labs are available")
    """
    command, args = parse_command(command_text)
    
    if command == "start":
        response = handle_start()
    elif command == "help":
        response = handle_help()
    elif command == "health":
        response = handle_health()
    elif command == "labs":
        response = handle_labs()
    elif command == "scores":
        response = handle_scores(args)
    else:
        # General query / intent routing
        response = handle_general_query(command_text)
    
    print(response)
    sys.exit(0)


async def handle_start_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Telegram handler for /start command."""
    await update.message.reply_text(handle_start())


async def handle_help_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Telegram handler for /help command."""
    await update.message.reply_text(handle_help())


async def handle_health_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Telegram handler for /health command."""
    await update.message.reply_text(handle_health())


async def handle_labs_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Telegram handler for /labs command."""
    await update.message.reply_text(handle_labs())


async def handle_scores_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Telegram handler for /scores command."""
    lab_name = " ".join(context.args) if context.args else ""
    await update.message.reply_text(handle_scores(lab_name))


async def handle_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle general text messages (intent routing)."""
    text = update.message.text
    if text:
        response = handle_general_query(text)
        await update.message.reply_text(response)


def run_telegram_mode(config: dict) -> None:
    """Run the bot in Telegram mode.
    
    Args:
        config: Configuration dictionary with BOT_TOKEN
    """
    bot_token = config.get("BOT_TOKEN")
    if not bot_token:
        logger.error("BOT_TOKEN not found in configuration")
        sys.exit(1)
    
    logger.info("Starting Telegram bot...")
    
    application = Application.builder().token(bot_token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", handle_start_command))
    application.add_handler(CommandHandler("help", handle_help_command))
    application.add_handler(CommandHandler("health", handle_health_command))
    application.add_handler(CommandHandler("labs", handle_labs_command))
    application.add_handler(CommandHandler("scores", handle_scores_command))
    
    # Add message handler for general queries
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="SE Toolkit Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Run in test mode with the specified command (no Telegram connection)",
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    if args.test:
        # Test mode - no Telegram connection needed
        run_test_mode(args.test)
    else:
        # Telegram mode
        run_telegram_mode(config)


if __name__ == "__main__":
    main()
