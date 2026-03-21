"""LMS Telegram Bot entry point."""

import asyncio
import sys

from handlers.commands import (
    handle_health,
    handle_help,
    handle_labs,
    handle_scores,
    handle_start,
    handle_unknown,
)


async def run_test(command: str) -> None:
    """Parse and dispatch a command string, print result to stdout."""
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else ""

    match cmd:
        case "/start":
            print(await handle_start())
        case "/help":
            print(await handle_help())
        case "/health":
            print(await handle_health())
        case "/labs":
            print(await handle_labs())
        case "/scores":
            print(await handle_scores(arg))
        case _:
            print(await handle_unknown(cmd))


async def run_bot() -> None:
    """Start the Telegram bot using aiogram."""
    from aiogram import Bot, Dispatcher
    from aiogram.filters import Command
    from aiogram.types import Message

    from config import settings

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def on_start(message: Message) -> None:
        await message.answer(await handle_start())

    @dp.message(Command("help"))
    async def on_help(message: Message) -> None:
        await message.answer(await handle_help())

    @dp.message(Command("health"))
    async def on_health(message: Message) -> None:
        await message.answer(await handle_health())

    @dp.message(Command("labs"))
    async def on_labs(message: Message) -> None:
        await message.answer(await handle_labs())

    @dp.message(Command("scores"))
    async def on_scores(message: Message) -> None:
        arg = ""
        if message.text:
            parts = message.text.split(maxsplit=1)
            arg = parts[1] if len(parts) > 1 else ""
        await message.answer(await handle_scores(arg))

    await dp.start_polling(bot)


if __name__ == "__main__":
    if "--test" in sys.argv:
        idx = sys.argv.index("--test")
        command = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "/help"
        asyncio.run(run_test(command))
    else:
        asyncio.run(run_bot())
