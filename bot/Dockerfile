FROM python:3.12-slim

WORKDIR /app

# Устанавливаем uv
RUN pip install uv

# Копируем код бота
COPY bot/ .

# Устанавливаем зависимости
RUN uv sync --no-dev

CMD ["uv", "run", "bot.py"]
