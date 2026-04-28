#!/bin/bash
# ============================================================
# ALZEN Phase 11 — Hermes Gateway + Telegram Bot
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$PROJECT_DIR/logs"

mkdir -p "$LOG_DIR"

echo "[hermes] Starting Hermes agent gateway..."

# Source environment
set -a
source "$PROJECT_DIR/.env" 2>/dev/null || true
source "$PROJECT_DIR/.env.hermes" 2>/dev/null || true
set +a

cd "$PROJECT_DIR"

# Start Hermes in gateway mode (Telegram bot)
echo "[hermes] Gateway mode — Telegram bot starting..."
hermes gateway \
    --config hermes/cli-config.yaml \
    > "$LOG_DIR/telegram-gateway.log" 2>&1 &

GATEWAY_PID=$!
echo "$GATEWAY_PID" > /tmp/alzen-hermes-gateway.pid
echo "[hermes] Gateway started (PID: $GATEWAY_PID)"
echo "[hermes] Telegram bot: @alzen_control_bot"

echo "[hermes] Ready."
