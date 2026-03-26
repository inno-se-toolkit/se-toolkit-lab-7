"""Configuration loading from environment variables."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    # Telegram
    bot_token: str = ""

    # LMS API
    lms_api_url: str = "http://localhost:42002"
    lms_api_key: str = ""

    # LLM API
    llm_api_key: str = ""
    llm_api_base_url: str = "http://localhost:42005/v1"
    llm_api_model: str = "coder-model"

    class Config:
        env_file = ".env.bot.secret"
        env_file_encoding = "utf-8"


def load_config() -> BotSettings:
    """Load configuration from .env.bot.secret file."""
    env_path = Path(__file__).parent / ".env.bot.secret"
    return BotSettings(_env_file=str(env_path))
