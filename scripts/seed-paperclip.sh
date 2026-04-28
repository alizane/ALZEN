#!/bin/bash
# ============================================================
# ALZEN Phase 09 — Seed Paperclip Company + 9-Agent Org Chart
# Run AFTER Paperclip is running on port 3100
# ============================================================
set -e

PAPERCLIP_URL="${PAPERCLIP_URL:-http://localhost:3100}"
CONFIG_FILE="$(cd "$(dirname "$0")/.." && pwd)/paperclip/alzen-company.json"

echo "[seed] Creating ALZEN company in Paperclip at $PAPERCLIP_URL..."

# 1. Create company
COMPANY_RESP=$(curl -sf -X POST "$PAPERCLIP_URL/api/companies" \
  -H "Content-Type: application/json" \
  -d '{"name":"ALZEN","description":"Enterprise Autonomous B2B Sales Closing Agency"}')
COMPANY_ID=$(echo "$COMPANY_RESP" | python -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
echo "[seed] Company created: $COMPANY_ID"

# 2. Set budget
curl -sf -X PATCH "$PAPERCLIP_URL/api/companies/$COMPANY_ID" \
  -H "Content-Type: application/json" \
  -d '{"budgetMonthlyCents":1200}' > /dev/null
echo "[seed] Budget set: \$12.00/month"

# 3. Create 9 agents
AGENTS=$(python -c "
import json
with open('$CONFIG_FILE') as f:
    data = json.load(f)
for agent in data['agents']:
    print(json.dumps(agent))
")

echo "$AGENTS" | while read -r agent_json; do
    agent_name=$(echo "$agent_json" | python -c "import sys,json; print(json.load(sys.stdin)['name'])")
    curl -sf -X POST "$PAPERCLIP_URL/api/companies/$COMPANY_ID/agents" \
      -H "Content-Type: application/json" \
      -d "$agent_json" > /dev/null
    echo "[seed] Agent created: $agent_name"
done

echo "[seed] Done. 9 agents seeded into Paperclip."
echo "[seed] Dashboard: $PAPERCLIP_URL"
