#!/bin/bash
# ALZEN — Daily Vault Backup (runs 2:30am via cron)
set -e
BACKUP_DIR="$(cd "$(dirname "$0")/.." && pwd)/backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
VAULT_DIR="$(cd "$(dirname "$0")/.." && pwd)/vault"
FILE="$BACKUP_DIR/alzen_vault_$TIMESTAMP.tar.gz"
tar -czf "$FILE" -C "$(dirname "$VAULT_DIR")" vault/ --exclude='.obsidian' --exclude='leads/*' --exclude='enrichments/*' --exclude='emails/*' --exclude='calls/*'
echo "[backup] $FILE ($(wc -c < "$FILE") bytes)"
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
