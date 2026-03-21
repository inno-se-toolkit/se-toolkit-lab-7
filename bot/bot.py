import argparse
import sys
import logging
from config import Config
from handlers import (
    handle_start,
    handle_help,
    handle_health,
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

def run_telegram_mode():
    """
    Initializes the Telegram bot and starts polling.
    """
    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        
        Config.validate(require_telegram=True)
        
        app = Application.builder().token(Config.BOT_TOKEN).build()
        
        # Register Command Handlers
        app.add_handler(CommandHandler("start", lambda u, c: send_response(u, c, handle_start)))
        app.add_handler(CommandHandler("help", lambda u, c: send_response(u, c, handle_help)))
        app.add_handler(CommandHandler("health", lambda u, c: send_response(u, c, handle_health)))
        app.add_handler(CommandHandler("scores", lambda u, c: send_response(u, c, handle_scores)))
        
        # Natural language fallback
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: send_response(u, c, handle_natural_language)))
        
        logger.info("Starting bot polling...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except ImportError:
        logger.error("telegram library not found. Run 'uv sync'")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)

async def send_response(update, context, handler_func):
    """Helper to bridge handlers and Telegram."""
    text = update.message.text if update.message else ""
    try:
        response = handler_func(text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred processing your request.")

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