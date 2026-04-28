#!/bin/bash
# ALZEN Phase 31 — Asterisk SIP Server Startup
set -e
echo "[asterisk] Starting Asterisk SIP server..."
docker compose -f "$(dirname "$0")/../../docker-compose.yml" up -d asterisk 2>/dev/null || echo "Asterisk container not yet configured (Phase 31)"
echo "[asterisk] SIP: localhost:5060 | AMI: localhost:5038"
