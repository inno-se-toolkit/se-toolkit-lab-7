"""Configuration loading from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_config() -> dict[str, str]:
    """Load configuration from environment variables.
    
    Looks for .env.bot.secret in the bot directory, falling back to .env.bot.example.
    """
    bot_dir = Path(__file__).parent
    
    # Try secret file first, then example
    secret_file = bot_dir / ".env.bot.secret"
    example_file = bot_dir / ".env.bot.example"
    
    if secret_file.exists():
        load_dotenv(secret_file)
    elif example_file.exists():
        load_dotenv(example_file)
    
    return {
        "BOT_TOKEN": os.getenv("BOT_TOKEN", ""),
        "LMS_API_BASE_URL": os.getenv("LMS_API_BASE_URL", ""),
        "LMS_API_KEY": os.getenv("LMS_API_KEY", ""),
        "LLM_API_KEY": os.getenv("LLM_API_KEY", ""),
    }
