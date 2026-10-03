#!/usr/bin/env bash
# Stop RDRS — Docker or local Python
set -e
cd "$(dirname "$0")"

echo ""
echo "→ Stopping RDRS..."

# Docker mode
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    docker compose down 2>/dev/null || true
    echo "  ✓ Container stopped"
fi

# Local mode (kill any stray processes)
pkill -f "app.detectors.monitor" 2>/dev/null || true
pkill -f "app.main" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
echo "  ✓ Background processes stopped"

# Optional: stop Docker daemon to free RAM (uncomment to enable)
# sudo systemctl stop docker.service docker.socket 2>/dev/null || true

echo ""
echo "  ✓ RDRS stopped"
echo ""
