#!/bin/bash
# Lab 7 Bot Deployment Script for VM
# Run this on your VM after SSH connection

set -e

echo "=== Lab 7 Bot Deployment ==="
echo ""

# 1. Navigate to project directory
cd ~/se-toolkit-lab-7

# 2. Pull latest changes
echo "[1/5] Pulling latest changes from GitHub..."
git pull origin main

# 3. Check if .env.docker.secret exists
if [ ! -f .env.docker.secret ]; then
    echo ""
    echo "[ERROR] .env.docker.secret not found!"
    echo "Please create it with required values:"
    echo ""
    echo "  cp .env.docker.example .env.docker.secret"
    echo "  # Edit .env.docker.secret with real values:"
    echo "  # - BOT_TOKEN (from @BotFather)"
    echo "  # - LMS_API_KEY"
    echo "  # - LLM_API_KEY, LLM_API_BASE_URL (optional)"
    echo ""
    exit 1
fi

# 4. Check if bot/.env.bot.secret exists
if [ ! -f bot/.env.bot.secret ]; then
    echo "[2/5] Creating bot/.env.bot.secret from .env.docker.secret..."
    cp .env.docker.secret bot/.env.bot.secret
else
    echo "[2/5] bot/.env.bot.secret already exists"
fi

# 5. Stop any running bot process
echo "[3/5] Stopping any existing bot processes..."
pkill -f "bot.py" 2>/dev/null || true

# 6. Build and start with Docker Compose
echo "[4/5] Building and starting bot with Docker Compose..."
docker compose --env-file .env.docker.secret up --build -d bot

# 7. Wait for bot to start
sleep 5

# 8. Check status
echo ""
echo "[5/5] Checking bot status..."
echo ""
docker compose --env-file .env.docker.secret ps bot
echo ""
echo "=== Bot Logs (last 20 lines) ==="
docker compose --env-file .env.docker.secret logs bot --tail 20
echo ""
echo "=== Deployment Complete ==="
echo ""
echo "To verify:"
echo "  1. Send /start to your bot in Telegram"
echo "  2. Check logs: docker compose --env-file .env.docker.secret logs bot -f"
echo "  3. Test commands: /health, /labs, /scores lab-04"
echo ""
