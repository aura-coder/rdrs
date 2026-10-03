#!/usr/bin/env bash
# One-time setup for RDRS
set -e
cd "$(dirname "$0")"

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  RDRS — One-Time Install                         ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ─── 1. Python version check ───
echo "→ Checking Python version..."
if ! command -v python3 >/dev/null; then
    echo "✗ python3 not found. Install Python 3.12+ first."
    exit 1
fi
PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  Python $PY_VER detected"
if [ "$(printf '%s\n' "3.12" "$PY_VER" | sort -V | head -n1)" != "3.12" ]; then
    echo "✗ Python 3.12+ required. You have $PY_VER."
    exit 1
fi
echo "  ✓ Python OK"
echo ""

# ─── 2. Virtual environment ───
echo "→ Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "  ✓ Created .venv"
else
    echo "  ✓ .venv already exists"
fi
source .venv/bin/activate
echo ""

# ─── 3. Python dependencies ───
echo "→ Installing Python dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "  ✓ Dependencies installed"
echo ""

# ─── 4. Docker check ───
echo "→ Checking Docker..."
if ! command -v docker >/dev/null; then
    echo "  ⚠ docker not found. Install it or run without Docker:"
    echo "     python -m app.main    (starts monitor + API together)"
    echo ""
    echo "  For Docker on Fedora:"
    echo "     sudo dnf install -y docker docker-compose"
    echo "     sudo systemctl enable --now docker"
    echo "     sudo usermod -aG docker \$USER   # then log out and back in"
    echo ""
else
    DOCKER_VER=$(docker --version 2>/dev/null | awk '{print $3}' | tr -d ',')
    echo "  ✓ Docker $DOCKER_VER"
    if ! docker info >/dev/null 2>&1; then
        echo "  ⚠ Docker daemon not running. Starting..."
        sudo systemctl start docker.service || true
        sleep 2
    fi
    if docker info >/dev/null 2>&1; then
        echo "  ✓ Docker daemon running"
    else
        echo "  ⚠ Could not start Docker. You may need sudo privileges."
    fi
fi
echo ""

# ─── 5. Data folders ───
echo "→ Preparing data folders..."
mkdir -p data/sandbox data/quarantine logs
touch data/sandbox/.gitkeep
echo "  ✓ Data + log folders ready"
echo ""

# ─── 6. Sanity test ───
echo "→ Running sanity test..."
pytest -q 2>&1 | tail -2
echo ""

echo "╔══════════════════════════════════════════════════╗"
echo "║  ✓ Installation complete                         ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "Next step:  ./run.sh"
echo ""
