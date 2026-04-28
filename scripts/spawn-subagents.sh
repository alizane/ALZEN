#!/bin/bash
# ============================================================
# ALZEN Phase 13 — Hermes ↔ Paperclip Integration
# CLI adapter + heartbeat + context template
# ============================================================
set -e

PAPERCLIP_URL="${PAPERCLIP_URL:-http://localhost:3100}"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# --- Heartbeat: Hermes reports status to Paperclip ---
send_heartbeat() {
    local agent_name="${1:-unknown}"
    local status="${2:-running}"
    local task_id="${3:-none}"

    curl -sf -X POST "$PAPERCLIP_URL/api/agents/me/heartbeat" \
        -H "Content-Type: application/json" \
        -d "{\"agent\":\"$agent_name\",\"status\":\"$status\",\"taskId\":\"$task_id\"}" \
        2>/dev/null || echo "[heartbeat] Paperclip unreachable (expected if not running)"
}

# --- Create Paperclip task from Hermes ---
create_task() {
    local title="$1"
    local agent="$2"
    local priority="${3:-medium}"

    curl -sf -X POST "$PAPERCLIP_URL/api/issues" \
        -H "Content-Type: application/json" \
        -d "{\"title\":\"$title\",\"assignee\":\"$agent\",\"priority\":\"$priority\"}" \
        2>/dev/null || echo "[task] Paperclip unreachable"
}

# --- Context template: Hermes → Paperclip ---
get_context() {
    cat <<'CTX'
## Hermes → Paperclip Context Template
- Agent: {{agent_name}}
- Task: {{task_id}}
- Vault Decision: vault/{{decision_log}}
- Graph Community: {{community_id}}
- Model: deepseek-chat-v3
- Tokens Used: {{tokens}}
- Cost: ${{cost_usd}}
CTX
}

# --- Main ---
case "${1:-heartbeat}" in
    heartbeat)
        send_heartbeat "${2:-hermes-agent}" "${3:-running}" "${4:-none}"
        ;;
    task)
        create_task "$2" "$3" "$4"
        ;;
    context)
        get_context
        ;;
    *)
        echo "Usage: $0 {heartbeat|task|context} [args...]"
        ;;
esac
