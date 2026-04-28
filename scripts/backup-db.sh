#!/bin/bash
# ALZEN — Daily Database Backup (runs 2am via cron)
set -e
BACKUP_DIR="$(cd "$(dirname "$0")/.." && pwd)/backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILE="$BACKUP_DIR/alzen_db_$TIMESTAMP.sql.gz"
docker exec alzen_postgres pg_dump -U alzen_admin alzen_db | gzip > "$FILE"
echo "[backup] $FILE ($(wc -c < "$FILE") bytes)"
# Keep last 7 days only
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
