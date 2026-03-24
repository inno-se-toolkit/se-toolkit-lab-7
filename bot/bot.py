#!/usr/bin/env python3
"""Telegram bot entry point with --test mode support."""
import httpx
import sys
import asyncio
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import load_config
from handlers.start import handle_start
from handlers.help import handle_help
from handlers.health import handle_health
from handlers.labs import handle_labs
from handlers.scores import handle_scores

# Try to import telegram, but don't fail if not installed
try:
    from telegram.ext import Application, CommandHandler
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("Warning: python-telegram-bot not installed. Install with: uv add python-telegram-bot")


async def test_mode(command: str) -> int:
    """Run bot in test mode: process command and print output."""
    try:
        # Parse command and arguments
        parts = command.strip().split()
        if not parts:
            print("Error: No command provided")
            return 1
        
        cmd = parts[0]
        args = " ".join(parts[1:]) if len(parts) > 1 else ""
        
        # Route to appropriate handler
        if cmd == "/start":
            result = handle_start(args)
        elif cmd == "/help":
            result = handle_help(args)
        elif cmd == "/health":
            result = await handle_health(args)
        elif cmd == "/labs":
            result = await handle_labs(args)
        elif cmd == "/scores":
            result = await handle_scores(args)
        else:
            result = f"Unknown command: {cmd}\nTry /help for available commands"
        
        print(result)
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


# Telegram wrapper handlers
async def handle_start_telegram(update, context):
    """Telegram wrapper for /start."""
    result = handle_start()
    await update.message.reply_text(result)


async def handle_help_telegram(update, context):
    """Telegram wrapper for /help."""
    result = handle_help()
    await update.message.reply_text(result)


async def handle_health_telegram(update, context):
    """Telegram wrapper for /health."""
    result = await handle_health()
    await update.message.reply_text(result)


async def handle_labs_telegram(update, context):
    """Telegram wrapper for /labs."""
    result = await handle_labs()
    await update.message.reply_text(result)


async def handle_scores_telegram(update, context):
    """Telegram wrapper for /scores."""
    args = " ".join(context.args) if context.args else ""
    result = await handle_scores(args)
    await update.message.reply_text(result)


async def telegram_mode():
    """Run bot in Telegram polling mode."""
    if not TELEGRAM_AVAILABLE:
        print("Error: python-telegram-bot is not installed")
        print("Install it with: uv add python-telegram-bot")
        return
    
    config = load_config()
    
    # Check if bot token is set
    if not config.bot_token or config.bot_token == "your-telegram-bot-token-here":
        print("Error: BOT_TOKEN not set in .env.bot.secret")
        print("Please add your bot token from @BotFather")
        return
    
    # Create application
    application = Application.builder().token(config.bot_token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", handle_start_telegram))
    application.add_handler(CommandHandler("help", handle_help_telegram))
    application.add_handler(CommandHandler("health", handle_health_telegram))
    application.add_handler(CommandHandler("labs", handle_labs_telegram))
    application.add_handler(CommandHandler("scores", handle_scores_telegram))
    
    # Start bot
    print(f"Starting bot with token: {config.bot_token[:10]}...")
    print("Bot is running. Press Ctrl+C to stop.")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Keep running until interrupted
    stop_signal = asyncio.Event()
    try:
        await stop_signal.wait()
    except KeyboardInterrupt:
        print("\nStopping bot...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        help="Run in test mode with command",
        type=str
    )
    args = parser.parse_args()
    
    if args.test:
        # Test mode - run once and exit
        exit_code = asyncio.run(test_mode(args.test))
        sys.exit(exit_code)
    else:
        # Normal mode - start Telegram polling
        asyncio.run(telegram_mode())


if __name__ == "__main__":
    main()
