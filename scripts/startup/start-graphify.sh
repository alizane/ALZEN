#!/bin/bash
# ============================================================
# ALZEN Phase 06 — Graphify MCP + Watch + Visual Browser
# Ports: MCP 8889 | Browser 8888
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$PROJECT_DIR/logs"

mkdir -p "$LOG_DIR"

echo "[graphify] Starting ALZEN knowledge graph services..."

# 1. Start graphify watch (background, rebuilds on code changes)
echo "[graphify] Starting watch mode..."
cd "$PROJECT_DIR"
graphify watch . --no-viz > "$LOG_DIR/graphify-watch.log" 2>&1 &
WATCH_PID=$!
echo "[graphify] Watch mode started (PID: $WATCH_PID)"

# 2. Start MCP HTTP server on port 8889
echo "[graphify] Starting MCP server on port 8889..."
python "$PROJECT_DIR/scripts/graphify-mcp-server.py" > "$LOG_DIR/graphify-mcp.log" 2>&1 &
MCP_PID=$!
echo "[graphify] MCP server started (PID: $MCP_PID) on http://localhost:8889"

# 3. Start visual browser on port 8888
echo "[graphify] Starting visual browser on port 8888..."
python -m http.server 8888 --directory "$PROJECT_DIR/graphify-out" > "$LOG_DIR/graphify-browser.log" 2>&1 &
BROWSER_PID=$!
echo "[graphify] Browser started (PID: $BROWSER_PID) on http://localhost:8888"

# Save PIDs for health checks
echo "$WATCH_PID" > /tmp/alzen-graphify-watch.pid
echo "$MCP_PID" > /tmp/alzen-graphify-mcp.pid
echo "$BROWSER_PID" > /tmp/alzen-graphify-browser.pid

echo "[graphify] All services started."
echo "  MCP Server: http://localhost:8889/mcp"
echo "  Browser:    http://localhost:8888/graph.html"
echo "  Watch log:  $LOG_DIR/graphify-watch.log"
