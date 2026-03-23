#!/bin/bash
# Final setup script for Task 2
# Run this on your VM: ssh root@10.93.26.132

set -e

echo "=== Task 2 Final Setup ==="

cd ~/se-toolkit-lab-7

# Create .env.bot.secret
cat > .env.bot.secret << 'BOTENV'
BOT_TOKEN=8707129062:AAGSXBqg-qaWUOULA4GJ-rWyD9o-iud6SBs
LMS_API_BASE_URL=http://localhost:42002
LMS_API_KEY=lab7-secret-key-root
LLM_API_MODEL=coder-model
LLM_API_KEY=my-secret-qwen-key
LLM_API_BASE_URL=http://localhost:42005/v1
BOTENV

echo ".env.bot.secret created"

# Setup PATH
export PATH=$HOME/.local/bin:$PATH

# Start bot
cd ~/se-toolkit-lab-7/bot
pkill -f 'bot.py' 2>/dev/null || true
nohup uv run bot.py > ../bot.log 2>&1 &
sleep 5

echo ""
echo "=== Testing bot commands ==="
uv run bot.py --test "/health"
echo "---"
uv run bot.py --test "/labs"
echo "---"
uv run bot.py --test "/scores lab-04"

echo ""
echo "=== Bot status ==="
ps aux | grep bot.py | grep -v grep || echo "Bot not running"

echo ""
echo "=== Services ==="
docker compose --env-file ~/se-toolkit-lab-7/.env.docker.secret ps

echo ""
echo "=== Qwen API ==="
docker compose -f ~/qwen-code-oai-proxy/docker-compose.yml ps

echo ""
echo "=== Done! ==="
echo "Bot is running. Test in Telegram with /start, /health, /labs"
