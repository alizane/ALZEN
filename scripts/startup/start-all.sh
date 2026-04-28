#!/bin/bash
# ============================================================
# ALZEN V3.0 — MASTER STARTUP (Phase 25)
# Starts all services in dependency order.
# Run: bash scripts/startup/start-all.sh
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "========================================"
echo " ALZEN V3.0 — Startup Sequence"
echo " DeepSeek Edition | Zero-Cost Stack"
echo "========================================"
echo ""

# 1. Docker Infrastructure
echo "[1/6] Starting Docker containers..."
cd "$PROJECT_DIR"
docker compose up -d postgres pgadmin redis paperclip_db 2>/dev/null || echo "  Docker not running — skip (services may already be up)"
echo "  PostgreSQL (5432), pgAdmin (5050), Redis (6379), Paperclip DB (54329)"

# 2. Wait for PostgreSQL
echo "[2/6] Waiting for PostgreSQL..."
until docker exec alzen_postgres pg_isready -U alzen_admin 2>/dev/null; do
    sleep 1
done
echo "  PostgreSQL ready"

# 3. Graphify MCP + Browser
echo "[3/6] Starting Graphify..."
bash "$SCRIPT_DIR/start-graphify.sh"
echo "  MCP: http://localhost:8889 | Browser: http://localhost:8888"

# 4. Paperclip
echo "[4/6] Starting Paperclip..."
bash "$SCRIPT_DIR/start-paperclip.sh" 2>/dev/null || echo "  Paperclip deferred (pnpm install required on first run)"
echo "  Dashboard: http://localhost:3100"

# 5. Hermes Gateway (Telegram Bot)
echo "[5/6] Starting Hermes Gateway..."
bash "$SCRIPT_DIR/start-gateway.sh" 2>/dev/null || echo "  Gateway deferred (Telegram token required)"
echo "  Bot: @alzen_control_bot"

# 6. Health Check
echo "[6/6] Running health check..."
sleep 3
bash "$PROJECT_DIR/scripts/monitoring/health-check.sh" 2>/dev/null || echo "  Health check completed (some services may be deferred)"

echo ""
echo "========================================"
echo " ALZEN V3.0 — Startup Complete"
echo "========================================"
echo ""
echo "Services:"
echo "  PostgreSQL:       http://localhost:5432"
echo "  pgAdmin:          http://localhost:5050"
echo "  Redis:            http://localhost:6379"
echo "  Graphify MCP:     http://localhost:8889/mcp"
echo "  Graphify Browser: http://localhost:8888/graph.html"
echo "  Paperclip:        http://localhost:3100"
echo "  Paperclip DB:     localhost:54329"
echo "  Telegram Bot:     @alzen_control_bot"
echo ""
echo "Next: /graphify query 'pipeline' for architecture overview"
