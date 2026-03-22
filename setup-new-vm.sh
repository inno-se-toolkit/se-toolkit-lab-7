#!/bin/bash
# Complete VM Setup Script for Lab 7
# Run this on your NEW VM after SSH access works

set -e

echo "=== Lab 7 VM Setup - Fresh Install ==="
echo ""

# 1. Install Docker
echo "[1/10] Installing Docker..."
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 2. Configure Docker DNS
echo "[2/10] Configuring Docker DNS..."
sudo tee /etc/docker/daemon.json <<'EOF'
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
EOF
sudo systemctl restart docker

# 3. Install uv (Python package manager)
echo "[3/10] Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

# 4. Clone repository
echo "[4/10] Cloning repository..."
cd ~
git clone https://github.com/vanya630/se-toolkit-lab-7 ~/se-toolkit-lab-7
cd ~/se-toolkit-lab-7

# 5. Setup .env.docker.secret
echo "[5/10] Configuring .env.docker.secret..."
cp .env.docker.example .env.docker.secret
sed -i 's|LMS_API_KEY=.*|LMS_API_KEY=lab7-secret-key-root1|' .env.docker.secret
sed -i 's|REGISTRY_PREFIX=.*|REGISTRY_PREFIX=|' .env.docker.secret

# 6. Start backend services
echo "[6/10] Starting Docker services..."
docker compose --env-file .env.docker.secret up -d --build

# Wait for backend to be ready
echo "Waiting for backend to start (30 seconds)..."
sleep 30

# 7. Run ETL sync
echo "[7/10] Running ETL sync..."
curl -X POST http://localhost:42002/pipeline/sync \
  -H "Authorization: Bearer lab7-secret-key-root1" \
  -H "Content-Type: application/json" \
  -d '{}'
echo ""

# 8. Setup Qwen Code API proxy
echo "[8/10] Setting up Qwen Code API..."
cd ~
if [ ! -d ~/qwen-code-oai-proxy ]; then
  git clone https://github.com/innopolis-se-toolkit/qwen-code-oai-proxy ~/qwen-code-oai-proxy
fi
cd ~/qwen-code-oai-proxy

# Create .env for Qwen proxy
cat > .env <<'QWENEOF'
PORT=8080
HOST_ADDRESS=127.0.0.1
CONTAINER_ADDRESS=0.0.0.0
QWEN_CODE_API_HOST_PORT=42005
LOG_LEVEL=error
QWEN_CODE_AUTH_USE=true
QWEN_CODE_API_KEY=my-secret-qwen-key
QWENEOF

# Setup Qwen authentication
echo "Setting up Qwen authentication..."
mkdir -p ~/.qwen
cat > ~/.qwen/oauth_creds.json <<'QWENCREDS'
{
  "access_token": "27539Eai-QC3XIFPmRP5bR3wW1ytS7odusf4OghXNs-StSyhTqhEs_gYo_HCHThb_TVr28cUaGT4_N9EwzUGKg",
  "token_type": "Bearer",
  "refresh_token": "l_AIt3EuiD7USAk_uX2IFBgZ8-l3rMgb1RM6b93PA5Cwa8QbyCdDqGGFMbLWir48sG-_frdlcxV9JMAoZU5ttg",
  "resource_url": "portal.qwen.ai",
  "expiry_date": 1774154556331
}
QWENCREDS

# Start Qwen proxy
docker compose up --build -d
sleep 15

# Test Qwen API
echo "Testing Qwen API..."
curl -s http://localhost:42005/v1/models -H "Authorization: Bearer my-secret-qwen-key" | head -c 100
echo ""

# 9. Setup bot
echo "[9/10] Setting up bot..."
cd ~/se-toolkit-lab-7
cp .env.bot.example .env.bot.secret
cat > .env.bot.secret <<'BOTENV'
# Telegram bot token
BOT_TOKEN=8707129062:AAGSXBqg-qaWUOULA4GJ-rWyD9o-iud6SBs

# LMS API
LMS_API_BASE_URL=http://localhost:42002
LMS_API_KEY=lab7-secret-key-root1

# LLM API
LLM_API_MODEL=coder-model
LLM_API_KEY=my-secret-qwen-key
LLM_API_BASE_URL=http://localhost:42005/v1
BOTENV

# Sync bot dependencies
export PATH=$HOME/.local/bin:$PATH
cd ~/se-toolkit-lab-7/bot
uv sync

# Test bot
echo "Testing bot commands..."
uv run bot.py --test "/health"
uv run bot.py --test "/labs"
uv run bot.py --test "/scores lab-04"

# 10. Setup SSH for autochecker
echo "[10/10] Setting up SSH for autochecker..."
mkdir -p ~/.ssh
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFNoSIw2aJzdNW79s5mtUa7DL21DFWpHJJCpM8rCLPiQ se-toolkit-student' >> ~/.ssh/authorized_keys
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKiL0DDQZw7L0Uf1c9cNlREY7IS6ZkIbGVWNsClqGNCZ se-toolkit-autochecker' >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "1. Start the bot: cd ~/se-toolkit-lab-7/bot && nohup uv run bot.py > ../bot.log 2>&1 &"
echo "2. Test in Telegram: send /start, /health, /labs to your bot"
echo "3. Check logs: tail -20 ~/se-toolkit-lab-7/bot.log"
echo ""
echo "Services running:"
echo "  - Backend: http://localhost:42002"
echo "  - Qwen API: http://localhost:42005"
echo "  - Bot: running in background"
