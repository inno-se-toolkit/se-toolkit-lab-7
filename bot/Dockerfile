ARG REGISTRY_PREFIX=docker.io/
FROM ${REGISTRY_PREFIX}python:3.14.2-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /uvx /bin/

COPY bot/pyproject.toml ./pyproject.toml
COPY bot/uv.lock ./uv.lock
RUN uv sync --locked --no-dev

COPY bot/ ./

CMD ["uv", "run", "bot.py"]
