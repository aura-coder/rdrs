#!/usr/bin/env bash
# Start RDRS — Docker if available, else local Python
set -e
cd "$(dirname "$0")"

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  RDRS — Starting                                 ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ─── 1. Ensure venv exists ───
if [ ! -d ".venv" ]; then
    echo "✗ No .venv found. Run ./install.sh first."
    exit 1
fi
source .venv/bin/activate

# ─── 2. Decide: Docker or local ───
USE_DOCKER=false
if command -v docker >/dev/null && docker info >/dev/null 2>&1; then
    USE_DOCKER=true
fi

# ─── 3. Docker path ───
if [ "$USE_DOCKER" = true ]; then
    echo "→ Mode: Docker"
    echo ""

    echo "→ Building container..."
    docker compose build --quiet
    echo "  ✓ Built"
    echo ""

    echo "→ Starting container..."
    docker compose up -d
    sleep 5
    echo ""

    # Ensure sandbox is clean
    rm -f data/sandbox/* 2>/dev/null || true

    echo "→ Container status:"
    docker compose ps
    echo ""

# ─── 4. Local Python path (fallback) ───
else
    echo "→ Mode: Local Python (no Docker available)"
    echo ""

    # Kill any old processes on port 8000
    pkill -f "app.detectors.monitor" 2>/dev/null || true
    pkill -f "uvicorn" 2>/dev/null || true
    sleep 1

    # Start monitor in background
    python -m app.detectors.monitor > logs/monitor.out 2>&1 &
    MONITOR_PID=$!
    echo "  ✓ Monitor started (PID $MONITOR_PID)"

    # Start API in foreground of a background process
    python -m app.main > logs/api.out 2>&1 &
    API_PID=$!
    echo "  ✓ API started (PID $API_PID)"
    sleep 4
fi

# ─── 5. Health check ───
echo "→ Health check..."
for i in {1..10}; do
    if curl -s http://127.0.0.1:8000/health >/dev/null 2>&1; then
        echo "  ✓ API responding"
        break
    fi
    sleep 1
done
echo ""

# ─── 6. Open browser ───
URL="http://127.0.0.1:8000/static/index.html"
echo "╔══════════════════════════════════════════════════╗"
echo "║  ✓ RDRS is running                               ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "  Dashboard:  $URL"
echo "  API docs:   http://127.0.0.1:8000/docs"
echo "  Health:     http://127.0.0.1:8000/health"
echo ""
echo "  Stop with:  ./stop.sh"
echo ""

# Try to open browser (best effort, no failure if no GUI)
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" >/dev/null 2>&1 || true
fi
