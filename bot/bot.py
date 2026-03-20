"""Telegram bot entry point with transport-agnostic handlers."""

from __future__ import annotations

import argparse
import asyncio
import sys
from contextlib import suppress
from dataclasses import dataclass

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import load_settings
from handlers.commands import CommandHandlers
from services.api_client import BackendClient
from services.intent_router import IntentRouter
from services.llm_client import LLMClient


@dataclass(slots=True)
class AppRuntime:
    """Shared application runtime dependencies."""

    handlers: CommandHandlers
    backend: BackendClient
    llm: LLMClient

    async def close(self) -> None:
        await self.backend.close()
        await self.llm.close()


def build_keyboard() -> ReplyKeyboardMarkup:
    """Return the main reply keyboard."""

    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(text="/help"), KeyboardButton(text="/health")],
            [
                KeyboardButton(text="/labs"),
                KeyboardButton(text="what labs are available?"),
            ],
            [
                KeyboardButton(text="/scores lab-04"),
                KeyboardButton(text="which lab has the lowest pass rate?"),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Type /help or ask an LMS question",
    )


def build_runtime() -> AppRuntime:
    """Construct application dependencies."""

    settings = load_settings()
    backend = BackendClient(
        base_url=settings.lms_api_url,
        api_key=settings.lms_api_key,
        timeout=settings.request_timeout_seconds,
    )
    llm = LLMClient(
        base_url=settings.llm_api_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_api_model,
        timeout=settings.request_timeout_seconds,
    )
    intent_router = IntentRouter(
        backend=backend,
        llm=llm,
        round_limit=settings.llm_tool_round_limit,
    )
    handlers = CommandHandlers(backend=backend, intent_router=intent_router)
    return AppRuntime(handlers=handlers, backend=backend, llm=llm)


async def run_test_mode(query: str) -> int:
    """Execute a request in CLI test mode."""

    runtime = build_runtime()
    try:
        response = await runtime.handlers.handle_text(query)
        print(response)
        return 0
    finally:
        await runtime.close()


async def run_polling() -> int:
    """Start the Telegram bot."""

    settings = load_settings()
    if not settings.bot_token:
        print("BOT_TOKEN is required to run Telegram polling mode.", file=sys.stderr)
        return 1

    runtime = build_runtime()
    keyboard = build_keyboard()
    application = Application.builder().token(settings.bot_token).build()

    async def answer_text(update: Update, text: str) -> None:
        if update.effective_message is None:
            return
        response = await runtime.handlers.handle_text(text)
        await update.effective_message.reply_text(
            response,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )

    async def handle_command(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        text = update.effective_message.text if update.effective_message else ""
        if text.startswith("/scores") and context.args:
            text = f"/scores {' '.join(context.args)}"
        await answer_text(update, text)

    async def handle_plain_text(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        del context
        text = update.effective_message.text if update.effective_message else ""
        await answer_text(update, text)

    async def handle_unknown_command(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        del context
        text = update.effective_message.text if update.effective_message else ""
        response = await runtime.handlers.handle_text(text)
        if update.effective_message is not None:
            await update.effective_message.reply_text(
                response,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )

    application.add_handler(CommandHandler("start", handle_command))
    application.add_handler(CommandHandler("help", handle_command))
    application.add_handler(CommandHandler("health", handle_command))
    application.add_handler(CommandHandler("labs", handle_command))
    application.add_handler(CommandHandler("scores", handle_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_plain_text)
    )
    application.add_handler(MessageHandler(filters.COMMAND, handle_unknown_command))

    try:
        await application.initialize()
        await application.start()
        if application.updater is None:
            raise RuntimeError("Telegram updater is not available.")
        await application.updater.start_polling()
        await asyncio.Event().wait()
        return 0
    finally:
        if application.updater is not None and application.updater.running:
            with suppress(RuntimeError):
                await application.updater.stop()
        with suppress(RuntimeError):
            await application.stop()
        with suppress(RuntimeError):
            await application.shutdown()
        await runtime.close()


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description="LMS Telegram bot")
    parser.add_argument(
        "--test",
        metavar="TEXT",
        help='Run one request locally without Telegram, for example --test "/help"',
    )
    return parser.parse_args()


def main() -> None:
    """CLI entry point."""

    args = parse_args()
    if args.test:
        raise SystemExit(asyncio.run(run_test_mode(args.test)))

    try:
        raise SystemExit(asyncio.run(run_polling()))
    except KeyboardInterrupt:
        raise SystemExit(0)


if __name__ == "__main__":
    main()
