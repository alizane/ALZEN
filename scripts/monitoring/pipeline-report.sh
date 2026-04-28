#!/bin/bash
# ============================================================
# ALZEN Pipeline Report — Lead funnel status from PostgreSQL
# ============================================================
echo "=== ALZEN Pipeline Report — $(date -I) ==="
echo ""

docker exec alzen_postgres psql -U alzen_admin -d alzen_db -c "
SELECT
  status,
  COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM leads), 1) as pct
FROM leads
GROUP BY status
ORDER BY
  CASE status
    WHEN 'new' THEN 1 WHEN 'qualified' THEN 2 WHEN 'enriched' THEN 3
    WHEN 'emailed' THEN 4 WHEN 'called' THEN 5 WHEN 'replied' THEN 6
    WHEN 'interested' THEN 7 WHEN 'closed' THEN 8 WHEN 'disqualified' THEN 9
  END;
" 2>&1 || echo "PostgreSQL not available — start with: docker compose up -d postgres"

echo ""
echo "Voice Calls Today:"
docker exec alzen_postgres psql -U alzen_admin -d alzen_db -c "
SELECT outcome, COUNT(*) FROM voice_calls
WHERE created_at::date = CURRENT_DATE
GROUP BY outcome;
" 2>&1 || echo "  No voice call data yet"
