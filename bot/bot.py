"""
Telegram bot entry point with --test mode.

Usage:
    uv run bot.py --test "/start"   # Test a command locally
    uv run bot.py --test "hello"    # Test natural language query
    uv run bot.py                   # Run the Telegram bot
"""

import argparse
import sys
from pathlib import Path

# Add bot directory to path for imports
bot_dir = Path(__file__).parent
sys.path.insert(0, str(bot_dir))

from handlers.commands.commands import run_command
from config import load_config


def main():
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="MESSAGE",
        help="Test a message locally (e.g., --test '/start' or --test 'hello')",
    )
    args = parser.parse_args()

    if args.test:
        # Test mode: run command and print result
        result = run_command(args.test)
        print(result)
        return

    # Load configuration
    config = load_config()

    # Telegram bot mode (to be implemented in Task 4)
    print("Telegram bot mode not yet implemented.")
    print("Run with --test to test commands locally.")
    print(f"\nConfiguration loaded:")
    print(f"  LMS API URL: {config['lms_api_base_url']}")
    print(f"  LLM API URL: {config['llm_api_base_url']}")
    print(f"  LLM Model: {config['llm_api_model']}")


if __name__ == "__main__":
    main()
