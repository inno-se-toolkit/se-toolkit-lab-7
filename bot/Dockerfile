# Telegram Bot Dockerfile
# Uses uv for dependency management

FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy lockfile from parent directory (Dockerfile is in bot/)
COPY ../uv.lock ./

# Copy project files
COPY ../pyproject.toml ./
COPY bot/bot.py bot/config.py ./
COPY bot/handlers/ ./handlers/
COPY bot/services/ ./services/

# Install dependencies (use --frozen since we have uv.lock)
RUN uv sync --frozen --no-dev

# Set Python path
ENV PYTHONPATH=/app

# Run the bot
CMD ["uv", "run", "bot.py"]
