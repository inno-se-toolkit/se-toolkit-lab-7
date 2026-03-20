ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}python:3.12-slim-bookworm

WORKDIR /app

# Install uv
RUN pip install uv

# Copy bot files
COPY bot/pyproject.toml bot/uv.lock ./
COPY bot/ ./bot/

# Install dependencies
RUN uv sync --frozen

# Set environment
ENV PYTHONPATH=/app

CMD ["uv", "run", "python", "bot/bot.py"]
