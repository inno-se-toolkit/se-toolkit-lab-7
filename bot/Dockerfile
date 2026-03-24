# LMS Telegram Bot — Dockerfile
# Uses uv for dependency management (no requirements.txt or pip)

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}astral/uv:python3.14-bookworm-slim

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy bot project files
COPY bot/pyproject.toml /app/pyproject.toml

# Install dependencies using uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync && \
    # Activate venv by adding it to PATH
    echo 'export PATH="/app/.venv/bin:$PATH"' >> /root/.bashrc

# Copy bot source code
COPY bot/ /app/bot/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8
ENV PATH="/app/.venv/bin:$PATH"

# Run the bot using venv Python
CMD ["python", "-m", "bot.bot"]
