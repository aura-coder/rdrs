#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "→ Starting Docker daemon..."
sudo systemctl start docker.service

sleep 2

echo "→ Starting RDRS container..."
docker compose up -d

sleep 4

echo ""
echo "✅ RDRS running at http://127.0.0.1:8000/static/index.html"
echo "   Stop with:  ~/rdrs/stop.sh"
