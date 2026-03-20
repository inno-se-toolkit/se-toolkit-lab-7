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

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_intent,
)
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

        # Check if it's a slash command or natural language
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
            # Natural language - use intent router
            response = handle_intent(command)

        print(response)
        sys.exit(0)

    # Telegram mode
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)

    try:
        from aiogram import Bot, Dispatcher, types
        from aiogram.filters import CommandStart, Command
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    except ImportError:
        print("Error: aiogram not installed. Run: uv sync")
        sys.exit(1)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def cmd_start(message: types.Message) -> None:
        """Handle /start with inline keyboard."""
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="📊 Labs", callback_data="labs"),
                    InlineKeyboardButton(text="🏥 Health", callback_data="health"),
                ],
                [
                    InlineKeyboardButton(text="📈 Scores", callback_data="scores"),
                    InlineKeyboardButton(text="❓ Help", callback_data="help"),
                ],
            ]
        )
        await message.answer(handle_start(), reply_markup=keyboard)

    @dp.callback_query(lambda c: c.data == "labs")
    async def callback_labs(callback_query: types.CallbackQuery):
        await callback_query.answer(handle_labs())

    @dp.callback_query(lambda c: c.data == "health")
    async def callback_health(callback_query: types.CallbackQuery):
        await callback_query.answer(handle_health())

    @dp.callback_query(lambda c: c.data == "scores")
    async def callback_scores(callback_query: types.CallbackQuery):
        await callback_query.answer("Use /scores lab-04 or ask me about scores")

    @dp.callback_query(lambda c: c.data == "help")
    async def callback_help(callback_query: types.CallbackQuery):
        await callback_query.answer(handle_help())

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
    async def handle_message(message: types.Message) -> None:
        """Handle all other messages with intent routing."""
        user_text = message.text or ""
        
        # Ignore if it's a command we already handle
        if user_text.startswith("/"):
            await message.answer("Use /help for available commands.")
            return
        
        # Use intent router for natural language
        response = handle_intent(user_text)
        await message.answer(response)

    print("Bot started...")
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
