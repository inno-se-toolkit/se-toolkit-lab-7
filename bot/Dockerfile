FROM harbor.pg.innopolis.university/docker-hub-cache/python:3.12-slim

WORKDIR /app

# Copy bot files
COPY bot/ ./bot/

# Copy uv and sync from host (pre-cached)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy lock files
COPY pyproject.toml uv.lock ./

# Sync dependencies using cached uv
RUN uv sync --locked --no-install-project || true

# Set environment
ENV PYTHONPATH=/app

# Run the bot
CMD ["python", "bot/bot.py"]
