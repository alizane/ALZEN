#!/bin/bash
# ============================================================
# ALZEN Phase 12 — Hermes ↔ Graphify Integration
# Pre-tool-use hook: query graph before file reads
# Heartbeat: Hermes reports status to Paperclip
# ============================================================
set -e

MCP_URL="${GRAPHIFY_MCP_URL:-http://localhost:8889}"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Query graph for a symbol
query_graph() {
    local symbol="$1"
    curl -sf "$MCP_URL/mcp/query?q=$(echo "$symbol" | python -c 'import urllib.parse,sys; print(urllib.parse.quote(sys.stdin.read().strip()))')" 2>/dev/null || echo '{"results":[],"error":"MCP unreachable"}'
}

# Get god nodes for architecture overview
get_god_nodes() {
    curl -sf "$MCP_URL/mcp/god-nodes" 2>/dev/null || echo '{"god_nodes":[]}'
}

# Main — if called with a symbol, query it; otherwise show status
if [ $# -gt 0 ]; then
    query_graph "$1"
else
    echo "[hermes-graphify] MCP status:"
    curl -sf "$MCP_URL/mcp/health" 2>/dev/null || echo '{"status":"down"}'
fi
