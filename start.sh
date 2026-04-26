#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

HOST="localhost"
PORT="8000"
APP_URL="http://${HOST}:${PORT}"

# --- 1. Create .venv if it doesn't exist ---
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv .venv
fi

# --- 2. Install / sync dependencies ---
echo "Syncing dependencies..."
uv sync

# --- 3. Activate .venv ---
# shellcheck source=.venv/bin/activate
source .venv/bin/activate

# --- 4. Open browser (after a short delay so the server is ready) ---
open_browser() {
    sleep 1.5
    if command -v open &>/dev/null; then          # macOS
        open "$APP_URL"
    elif command -v xdg-open &>/dev/null; then    # Linux
        xdg-open "$APP_URL"
    elif command -v start &>/dev/null; then       # Windows / Git Bash
        start "$APP_URL"
    fi
}
open_browser &

# --- 5. Start the server ---
echo "Starting Excel Processor at ${APP_URL} ..."
uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
