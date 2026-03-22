#!/bin/bash
# Deploy Task 2 on VM

set -e

echo "=== Deploying Task 2 ==="

cd ~/se-toolkit-lab-7

# Pull latest changes
git pull

# Update .env.bot.secret with correct API key
sed -i 's|LMS_API_KEY=.*|LMS_API_KEY=lab7-secret-key-vanya630|' .env.bot.secret
sed -i 's|LMS_API_BASE_URL=<lms-api-base-url>|LMS_API_BASE_URL=http://localhost:42002|' .env.bot.secret
sed -i 's|BOT_TOKEN=<bot-token>|BOT_TOKEN=8707129062:AAGSXBqg-qaWUOULA4GJ-rWyD9o-iud6SBs|' .env.bot.secret
sed -i 's|LLM_API_KEY=<llm-api-key>|LLM_API_KEY=my-secret-qwen-key|' .env.bot.secret
sed -i 's|LLM_API_BASE_URL=<llm-api-base-url>|LLM_API_BASE_URL=http://localhost:42005/v1|' .env.bot.secret

echo "Environment configured:"
cat .env.bot.secret

# Sync bot dependencies
export PATH=$HOME/.local/bin:$PATH
cd ~/se-toolkit-lab-7/bot
uv sync

# Test commands
echo ""
echo "=== Testing commands ==="
uv run bot.py --test "/health"
echo ""
uv run bot.py --test "/labs"
echo ""
uv run bot.py --test "/scores lab-04"

# Restart bot
echo ""
echo "=== Restarting bot ==="
pkill -f "bot.py" 2>/dev/null || true
cd ~/se-toolkit-lab-7/bot
nohup uv run bot.py > ../bot.log 2>&1 &

echo "Bot restarted!"
echo "Check logs: tail -20 ~/se-toolkit-lab-7/bot.log"
echo "Test in Telegram: send /health, /labs, /scores lab-04"
