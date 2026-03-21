from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Look for .env.bot.secret in the repo root (two levels up from bot/config.py)
_ENV_FILE = Path(__file__).parent.parent / ".env.bot.secret"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), extra="ignore")

    bot_token: str = ""
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = ""
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = "coder-model"


settings = Settings()
