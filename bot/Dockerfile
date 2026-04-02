FROM python:3.14-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy pyproject.toml and uv.lock from project root
COPY bot/pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync

# Copy bot source code
COPY bot/ .

# Run the bot
CMD ["uv", "run", "bot.py"]
