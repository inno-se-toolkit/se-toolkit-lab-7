FROM harbor.pg.innopolis.university/docker-hub-cache/python:3.12-slim

WORKDIR /app

# Copy bot
COPY bot/ ./bot/
COPY pyproject.toml ./

# Install packages directly
RUN pip install --no-cache-dir httpx python-telegram-bot

ENV PYTHONPATH=/app

CMD ["python", "bot/bot.py"]
