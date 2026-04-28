#!/bin/bash
# ============================================================
# ALZEN Phase 08 — Paperclip Startup
# Dashboard: http://localhost:3100
# Embedded DB: port 54329 (ISOLATED from main alzen_db)
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
PAPERCLIP_DIR="$PROJECT_DIR/paperclip"

mkdir -p "$LOG_DIR"

echo "[paperclip] Starting Paperclip services..."

# 1. Ensure Paperclip DB container is running
if ! docker ps --format '{{.Names}}' | grep -q alzen_paperclip_db; then
    echo "[paperclip] Starting Paperclip PostgreSQL (port 54329)..."
    docker compose -f "$PROJECT_DIR/docker-compose.yml" up -d paperclip_db
    echo "[paperclip] Waiting for DB to be ready..."
    until docker exec alzen_paperclip_db pg_isready -U paperclip_admin -d paperclip_internal > /dev/null 2>&1; do
        sleep 1
    done
    echo "[paperclip] Paperclip DB ready on port 54329"
else
    echo "[paperclip] Paperclip DB already running on port 54329"
fi

# 2. Source environment
set -a
source "$PROJECT_DIR/.env.paperclip" 2>/dev/null || true
set +a

# 3. Install dependencies if needed
cd "$PAPERCLIP_DIR"
if [ ! -d "node_modules" ]; then
    echo "[paperclip] Installing dependencies (pnpm)..."
    pnpm install --frozen-lockfile 2>/dev/null || pnpm install
fi

# 4. Run database migrations
echo "[paperclip] Running database migrations..."
pnpm db:generate 2>&1 | tail -3
pnpm db:migrate 2>&1 | tail -3

# 5. Start Paperclip server on port 3100
echo "[paperclip] Starting Paperclip server on http://localhost:3100..."
cd "$PAPERCLIP_DIR"
pnpm dev:server > "$LOG_DIR/paperclip.log" 2>&1 &
PAPERCLIP_PID=$!
echo "$PAPERCLIP_PID" > /tmp/alzen-paperclip.pid
echo "[paperclip] Server started (PID: $PAPERCLIP_PID)"
echo "[paperclip] Dashboard: http://localhost:3100"

echo "[paperclip] Ready."
