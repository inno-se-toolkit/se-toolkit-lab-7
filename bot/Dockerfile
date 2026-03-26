FROM harbor.pg.innopolis.university/docker-hub-cache/python:3.12-slim

WORKDIR /app

# Copy bot
COPY bot/ ./bot/
COPY pyproject.toml ./

# Use host DNS
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf && \
    pip install --no-cache-dir httpx python-telegram-bot

ENV PYTHONPATH=/app

CMD ["python", "bot/bot.py"]
