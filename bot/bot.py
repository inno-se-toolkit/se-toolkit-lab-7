import argparse
import sys
import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from config import Config
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,        # ← NEW: Added import
    handle_scores,
    handle_natural_language,
)

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def route_command(text: str) -> str:
    """
    Routes input text to the appropriate handler.
    This function is pure logic - no Telegram dependencies.
    """
    if not text:
        return "Empty command."
    
    command = text.split()[0].lower()
    
    if command == "/start":
        return handle_start(text)
    elif command == "/help":
        return handle_help(text)
    elif command == "/health":
        return handle_health(text)
    elif command == "/labs":           # ← NEW: Handle /labs command
        return handle_labs(text)
    elif command == "/scores":
        return handle_scores(text)
    else:
        # Natural language fallback
        return handle_natural_language(text)

def run_test_mode(command: str):
    """
    Runs a command directly and prints output to stdout.
    Used for offline verification.
    """
    logger.info(f"Running test mode for: {command}")
    try:
        # Validate config (non-telegram)
        Config.validate(require_telegram=False)
        
        response = route_command(command)
        print(response)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


# ============ Telegram Async Handlers (Preserving Your Structure) ============

async def handle_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram handler for /start"""
    text = update.message.text if update.message else ""
    try:
        response = handle_start(text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    except Exception as e:
        logger.error(f"Error in /start: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred processing your request.")

async def handle_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text if update.message else ""
    try:
        response = handle_help(text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    except Exception as e:
        logger.error(f"Error in /help: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred processing your request.")

async def handle_health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text if update.message else ""
    try:
        response = handle_health(text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    except Exception as e:
        logger.error(f"Error in /health: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred processing your request.")

async def handle_labs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):  # ← NEW
    """Telegram handler for /labs"""
    text = update.message.text if update.message else ""
    try:
        response = handle_labs(text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    except Exception as e:
        logger.error(f"Error in /labs: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred processing your request.")

async def handle_scores_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text if update.message else ""
    try:
        response = handle_scores(text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    except Exception as e:
        logger.error(f"Error in /scores: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred processing your request.")

async def handle_natural_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fallback for non-command messages"""
    text = update.message.text if update.message else ""
    try:
        response = handle_natural_language(text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    except Exception as e:
        logger.error(f"Error in natural language handler: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred processing your request.")

def run_telegram_mode():
    """Initializes the Telegram bot and starts polling."""
    try:
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        
        Config.validate(require_telegram=True)
        
        app = Application.builder().token(Config.BOT_TOKEN).build()
        
        # Register proper async handlers (your structure preserved)
        app.add_handler(CommandHandler("start", handle_start_command))
        app.add_handler(CommandHandler("help", handle_help_command))
        app.add_handler(CommandHandler("health", handle_health_command))
        app.add_handler(CommandHandler("labs", handle_labs_command))      # ← NEW
        app.add_handler(CommandHandler("scores", handle_scores_command))
        
        # Natural language fallback
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_natural_language_command))
        
        logger.info("Starting bot polling...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except ImportError as e:
        logger.error(f"telegram library not found. Run 'uv sync'. Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="SE Toolkit Bot")
    parser.add_argument("--test", type=str, help="Run a command in test mode (e.g., '/start')")
    
    args = parser.parse_args()
    
    if args.test:
        run_test_mode(args.test)
    else:
        run_telegram_mode()

if __name__ == "__main__":
    main()