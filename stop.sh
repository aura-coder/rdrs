#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "→ Stopping RDRS container..."
docker compose down || true

echo "→ Stopping Docker service and socket..."
sudo systemctl stop docker.service docker.socket 2>/dev/null || true

echo ""
echo "✅ Everything stopped. RAM freed. Docker fully off."
