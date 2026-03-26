#!/usr/bin/env python3
"""
Telegram Bot for LMS - Entry Point

Usage:
    uv run bot.py              # Start Telegram bot
    uv run bot.py --test "/command"  # Test mode (no Telegram connection)
    uv run bot.py --test "natural language query"  # LLM-powered
"""

import sys
import os

# Add bot directory to path for imports
bot_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, bot_dir)

import handlers
from handlers.intent_router import route_intent, get_inline_buttons


def main():
    """Main entry point."""
    # Check for test mode
    if len(sys.argv) >= 3 and sys.argv[1] == "--test":
        command = sys.argv[2]
        response = handle_test_command(command)
        print(response)
        sys.exit(0)
    
    # Normal mode - start Telegram bot
    start_telegram_bot()


def handle_test_command(command: str) -> str:
    """
    Handle a command in test mode (no Telegram connection).
    
    Args:
        command: The command string (e.g., "/start", "/help", or natural language)
    
    Returns:
        Response text to print to stdout
    """
    # Slash commands - use handlers
    if command.startswith("/"):
        if command == "/start":
            return handlers.handle_start_with_buttons()
        elif command == "/help":
            return handlers.handle_help()
        elif command == "/health":
            return handlers.handle_health()
        elif command == "/labs":
            return handlers.handle_labs()
        elif command.startswith("/scores"):
            parts = command.split(maxsplit=1)
            lab_name = parts[1] if len(parts) > 1 else ""
            return handlers.handle_scores(lab_name)
        else:
            return f"Unknown command: {command}"
    else:
        # Natural language - use LLM intent router
        return route_intent(command)


def start_telegram_bot():
    """Start the Telegram bot with inline keyboard support."""
    print("Starting Telegram bot...")
    print("Bot token:", os.environ.get("BOT_TOKEN", "NOT SET"))
    print("LMS API URL:", os.environ.get("LMS_API_BASE_URL", "NOT SET"))
    print("LLM API URL:", os.environ.get("LLM_API_BASE_URL", "NOT SET"))
    print("\nInline keyboard buttons enabled for common actions.")
    print("For now, use --test mode to test handlers:")
    print("  uv run bot.py --test '/start'")
    print("  uv run bot.py --test 'what labs are available'")


if __name__ == "__main__":
    main()
