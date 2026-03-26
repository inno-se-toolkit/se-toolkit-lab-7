# Bot Dockerfile - uses pre-cached packages from lab-6 image
FROM se-toolkit-lab-6-app:latest

WORKDIR /app

# Copy bot files
COPY bot/ ./bot/

# Set environment
ENV PYTHONPATH=/app

# Run the bot
CMD ["python", "bot/bot.py"]
