#!/usr/bin/env python3
"""Telegram LMS Bot entry point."""

import argparse
import sys
import os
import asyncio
import ssl
from pathlib import Path

ssl._create_default_https_context = ssl._create_unverified_context

sys.path.insert(0, str(Path(__file__).parent))

from handlers import handle_start, handle_help, handle_health, handle_labs, handle_scores
from config import BOT_TOKEN


def main() -> None:
    parser = argparse.ArgumentParser(description="Telegram LMS Bot")
    parser.add_argument(
        "--test",
        type=str,
        help="Test mode: run handler with given command",
    )
    args = parser.parse_args()

    if args.test:
        command = args.test.strip()
        response = ""

        if command == "/start":
            response = handle_start()
        elif command == "/help":
            response = handle_help()
        elif command == "/health":
            response = handle_health()
        elif command == "/labs":
            response = handle_labs()
        elif command.startswith("/scores"):
            parts = command.split(maxsplit=1)
            lab = parts[1] if len(parts) > 1 else ""
            response = handle_scores(lab)
        else:
            response = "Command not recognized. Use /help for available commands."

        print(response)
        sys.exit(0)

    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)

    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import CommandStart, Command
    except ImportError:
        print("Error: aiogram not installed. Run: uv sync")
        sys.exit(1)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def cmd_start(message: types.Message) -> None:
        await message.answer(handle_start())

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message) -> None:
        await message.answer(handle_help())

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message) -> None:
        await message.answer(handle_health())

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message) -> None:
        await message.answer(handle_labs())

    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message) -> None:
        lab = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
        response = handle_scores(lab)
        await message.answer(response)

    @dp.message()
    async def echo(message: types.Message) -> None:
        await message.answer("Use /help for available commands.")

    print("Bot started...")
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
