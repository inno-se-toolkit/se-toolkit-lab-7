FROM python:3.11-slim

WORKDIR /app

# Install dependencies directly with pip (no build step)
RUN pip install --no-cache-dir python-telegram-bot httpx pydantic-settings pydantic

# Copy bot source code
COPY bot/ .

# Run bot
CMD ["python", "bot.py"]
