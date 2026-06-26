#!/bin/bash
# Установка AVsound MCP сервера на Hetzner
# Запуск: bash install.sh

set -e

echo "=== AVsound MCP Server Setup ==="

# Зависимости
apt-get update -q
apt-get install -y python3 python3-pip python3-venv git

# Клонируем репозиторий
REPO_DIR="/opt/avsound"
if [ -d "$REPO_DIR" ]; then
    cd $REPO_DIR && git pull
else
    git clone https://github.com/avsoundmsk-ux/avsound.git $REPO_DIR
fi

cd $REPO_DIR/mcp-server

# Python venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# .env файл
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  Заполни /opt/avsound/mcp-server/.env:"
    echo "   GITHUB_TOKEN=ghp_...        (база знаний)"
    echo "   ARK_API_KEY=...                  (Seedance 2.0 — генерация видео)"
    echo "   SEEDANCE_MODEL=seedance-2-0      (ID эндпоинта Seedance 2.0)"
    echo "   SEEDANCE_MODEL_MINI=seedance-2-0-mini (ID эндпоинта 2.0 mini)"
    echo ""
fi

# systemd сервис
cat > /etc/systemd/system/avsound-mcp.service << 'EOF'
[Unit]
Description=AVsound Knowledge Base MCP Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/avsound/mcp-server
EnvironmentFile=/opt/avsound/mcp-server/.env
ExecStart=/opt/avsound/mcp-server/venv/bin/python server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable avsound-mcp
systemctl start avsound-mcp

echo ""
echo "✅ MCP сервер запущен на порту 8080"
echo "   Проверь: systemctl status avsound-mcp"
echo "   Логи:    journalctl -u avsound-mcp -f"
