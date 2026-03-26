FROM harbor.pg.innopolis.university/docker-hub-cache/python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy bot-specific files
COPY pyproject.toml uv.lock ./
COPY bot/ ./bot/
COPY backend/ ./backend/

# Sync dependencies
RUN uv sync --locked --no-install-project

# Set environment variables
ENV PYTHONPATH=/app

# Run the bot
CMD ["uv", "run", "bot/bot.py"]
