#!/usr/bin/env python3
"""
Telegram Bot for LMS Backend Interaction

Usage:
    Normal mode:  uv run bot.py
    Test mode:    uv run bot.py --test "/command"

Test mode prints the response to stdout without connecting to Telegram.
"""
import sys
import asyncio
import argparse
import re
from typing import Optional

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_unknown
)
from keyboards import get_main_keyboard, get_labs_keyboard

from config import load_config
from services.lms_client import LMSClient
from services.llm_client import LLMClient


def parse_command(text: str) -> tuple:
    """Parse a command text into command and arguments."""
    text = text.strip()
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        return command, args
    return "", text


async def process_command(command: str, args: str, lms_client: Optional[LMSClient], llm_client: Optional[LLMClient]) -> str:
    """Process a command and return the response."""
    if command == "/start":
        return await handle_start(lms_client)
    elif command == "/help":
        return await handle_help(lms_client)
    elif command == "/health":
        return await handle_health(lms_client)
    elif command == "/labs":
        return await handle_labs(lms_client)
    elif command == "/scores":
        return await handle_scores(args, lms_client)
    else:
        # Unknown command - return helpful message
        return f"⚠️ Неизвестная команда: {command}\n\nИспользуйте /help для списка команд."


async def process_natural_language(text: str, lms_client: LMSClient, llm_client: Optional[LLMClient]) -> str:
    """Process natural language message using LLM for intent classification."""
    if not llm_client:
        return "⚠️ LLM не настроен. Используйте команды (/start, /help, /health, /labs, /scores)."
    
    # Try to classify intent
    classified = await llm_client.classify_intent(text)
    
    if classified:
        command, args = parse_command(classified)
        if command:
            return await process_command(command, args, lms_client, llm_client)
    
    # If classification failed, try to extract lab number and assume scores request
    if re.search(r'\b(lab|лаб|лабораторная)\s*(\d+|-\d+)', text, re.IGNORECASE):
        lab_id = await llm_client.extract_lab_number(text)
        if lab_id:
            return await handle_scores(lab_id, lms_client)
    
    return "⚠️ Я не понял ваш запрос. Попробуйте использовать команды (/help для списка) или задайте вопрос о лабораторных работах."


async def run_test_mode(command_text: str, config: dict) -> None:
    """Run in test mode - process command and print response."""
    # Always create LMS client for test mode
    lms_client = LMSClient(
        base_url=config["lms_api_url"],
        api_key=config["lms_api_key"]
    )

    # LLM client is optional
    llm_client = None
    if config.get("llm_api_key") and config.get("llm_api_base_url"):
        try:
            llm_client = LLMClient(
                api_key=config["llm_api_key"],
                base_url=config["llm_api_base_url"],
                model=config.get("llm_api_model", "coder-model")
            )
        except Exception:
            llm_client = None

    command, args = parse_command(command_text)

    if command:
        response = await process_command(command, args, lms_client, llm_client)
    else:
        # Natural language input in test mode
        response = await process_natural_language(command_text, lms_client, llm_client)

    print(response)


async def run_telegram_mode(config: dict) -> None:
    """Run the Telegram bot."""
    from aiogram import Bot, Dispatcher
    from aiogram.filters import Command, CommandStart
    from aiogram.types import Message, CallbackQuery

    if not config.get("bot_token"):
        print("Error: BOT_TOKEN not set. Please configure .env.bot.secret")
        sys.exit(1)

    bot = Bot(token=config["bot_token"])
    dp = Dispatcher()

    lms_client = LMSClient(
        base_url=config["lms_api_url"],
        api_key=config["lms_api_key"]
    )

    llm_client = None
    if config.get("llm_api_key") and config.get("llm_api_base_url"):
        try:
            llm_client = LLMClient(
                api_key=config["llm_api_key"],
                base_url=config["llm_api_base_url"],
                model=config.get("llm_api_model", "coder-model")
            )
        except Exception:
            llm_client = None

    @dp.message(CommandStart())
    async def cmd_start(message: Message):
        response = await handle_start(lms_client)
        await message.answer(response, reply_markup=get_main_keyboard())

    @dp.message(Command("help"))
    async def cmd_help(message: Message):
        response = await handle_help(lms_client)
        await message.answer(response, reply_markup=get_main_keyboard())

    @dp.message(Command("health"))
    async def cmd_health(message: Message):
        response = await handle_health(lms_client)
        await message.answer(response)

    @dp.message(Command("labs"))
    async def cmd_labs(message: Message):
        response = await handle_labs(lms_client)
        labs = await lms_client.get_labs()
        keyboard = get_labs_keyboard(labs) if labs else None
        await message.answer(response, reply_markup=keyboard)

    @dp.message(Command("scores"))
    async def cmd_scores(message: Message):
        lab_query = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
        response = await handle_scores(lab_query, lms_client)
        await message.answer(response)

    @dp.message()
    async def handle_message(message: Message):
        """Handle plain text messages using LLM for intent routing."""
        user_text = message.text or ""
        response = await process_natural_language(user_text, lms_client, llm_client)
        await message.answer(response)

    @dp.callback_query()
    async def handle_callback(callback: CallbackQuery):
        """Handle inline keyboard button clicks."""
        data = callback.data or ""
        
        if data == "cmd_start":
            response = await handle_start(lms_client)
            await callback.message.edit_text(response, reply_markup=get_main_keyboard())
        elif data == "cmd_help":
            response = await handle_help(lms_client)
            await callback.message.edit_text(response, reply_markup=get_main_keyboard())
        elif data == "cmd_health":
            response = await handle_health(lms_client)
            await callback.message.edit_text(response)
        elif data == "cmd_labs":
            response = await handle_labs(lms_client)
            labs = await lms_client.get_labs()
            keyboard = get_labs_keyboard(labs) if labs else None
            await callback.message.edit_text(response, reply_markup=keyboard)
        elif data.startswith("scores_"):
            lab_id = data.replace("scores_", "")
            response = await handle_scores(f"lab-{lab_id}", lms_client)
            await callback.message.edit_text(response)
        
        await callback.answer()

    print("Bot is running... Press Ctrl+C to stop.")
    await dp.start_polling(bot)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Test mode: process command and print response (e.g., --test '/start')"
    )
    args = parser.parse_args()

    config = load_config()

    if args.test:
        # Test mode
        try:
            asyncio.run(run_test_mode(args.test, config))
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        # Normal Telegram bot mode
        asyncio.run(run_telegram_mode(config))


if __name__ == "__main__":
    main()
