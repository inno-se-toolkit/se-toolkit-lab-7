import os
from pathlib import Path
from dotenv import load_dotenv

# Determine env file based on context (secret for prod, example for dev scaffolding)
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env.bot.secret"

if not ENV_FILE.exists():
    # Fallback to example if secret doesn't exist (useful for initial setup)
    ENV_FILE = BASE_DIR / ".env.bot.example"

load_dotenv(ENV_FILE)

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    LMS_API_BASE_URL = os.getenv("LMS_API_BASE_URL", "http://localhost:8000")
    LMS_API_KEY = os.getenv("LMS_API_KEY")
    LLM_API_KEY = os.getenv("LLM_API_KEY")

    @classmethod
    def validate(cls, require_telegram: bool = False):
        if require_telegram and not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required for Telegram mode")
        # API keys might be optional for scaffolding depending on implementation
        return True