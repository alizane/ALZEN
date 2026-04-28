#!/bin/bash
# ============================================================
# ALZEN Health Check — runs every 10min via cron
# Verifies all 6 core services are running
# ============================================================
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_FILE="$PROJECT_DIR/logs/health.log"
TIMESTAMP=$(date -Iseconds)
FAILS=0

check() {
    local name="$1"
    local url="$2"
    if curl -sf --max-time 5 "$url" > /dev/null 2>&1; then
        echo "  ✅ $name — $url"
    else
        echo "  ❌ $name — $url (DOWN)"
        FAILS=$((FAILS + 1))
    fi
}

{
echo "=== Health Check [$TIMESTAMP] ==="
echo ""

# 1. PostgreSQL
docker exec alzen_postgres psql -U alzen_admin -d alzen_db -c "SELECT 1" > /dev/null 2>&1 && \
    echo "  ✅ PostgreSQL (port 5432)" || { echo "  ❌ PostgreSQL DOWN"; FAILS=$((FAILS+1)); }

# 2. Redis
docker exec alzen_redis redis-cli PING > /dev/null 2>&1 && \
    echo "  ✅ Redis (port 6379)" || { echo "  ❌ Redis DOWN"; FAILS=$((FAILS+1)); }

# 3. Graphify MCP
check "Graphify MCP" "http://127.0.0.1:8889/mcp/health"

# 4. Graphify Browser
check "Graphify Browser" "http://127.0.0.1:8888/graph.html"

# 5. Paperclip
check "Paperclip" "http://127.0.0.1:3100/health"

# 6. Asterisk SIP
docker exec alzen_asterisk asterisk -rx "core show version" > /dev/null 2>&1 && \
    echo "  ✅ Asterisk (port 5060)" || { echo "  ⚠️  Asterisk not running (expected if Phase 31+)"; }

echo ""
if [ $FAILS -eq 0 ]; then
    echo "✅ ALL SERVICES HEALTHY"
else
    echo "❌ $FAILS service(s) unhealthy"
fi
echo "---"
} >> "$LOG_FILE" 2>&1

# Also echo to stdout
tail -8 "$LOG_FILE"
