"""Configuration loading for the Telegram bot."""

from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parent.parent
BOT_ENV_FILE = ROOT_DIR / ".env.bot.secret"


class Settings(BaseSettings):
    """Bot settings loaded from environment variables or .env.bot.secret."""

    bot_token: str | None = Field(default=None, alias="BOT_TOKEN")
    lms_api_url: str = Field(default="http://localhost:42002", alias="LMS_API_URL")
    lms_api_key: str = Field(alias="LMS_API_KEY")
    llm_api_key: str | None = Field(default=None, alias="LLM_API_KEY")
    llm_api_base_url: str = Field(
        default="http://localhost:42005/v1",
        validation_alias=AliasChoices("LLM_API_BASE_URL", "LLM_API_BASE"),
    )
    llm_api_model: str = Field(
        default="coder-model",
        validation_alias=AliasChoices("LLM_API_MODEL", "LLM_MODEL"),
    )
    llm_tool_round_limit: int = Field(default=8, alias="LLM_TOOL_ROUND_LIMIT")
    request_timeout_seconds: float = Field(
        default=20.0, alias="REQUEST_TIMEOUT_SECONDS"
    )

    model_config = SettingsConfigDict(
        env_file=str(BOT_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


def load_settings() -> Settings:
    """Return the validated application settings."""

    return Settings.model_validate({})
