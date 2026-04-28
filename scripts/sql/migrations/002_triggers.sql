-- ============================================================
-- ALZEN V3.0 — Triggers, Views & Functions (Phase 16)
-- ============================================================

-- ============================================================
-- Trigger: Auto-update updated_at on leads
-- ============================================================
CREATE OR REPLACE FUNCTION update_leads_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_leads_updated_at ON leads;
CREATE TRIGGER trg_leads_updated_at
    BEFORE UPDATE ON leads
    FOR EACH ROW
    EXECUTE FUNCTION update_leads_updated_at();

-- ============================================================
-- Trigger: Auto-create voice_calls record when lead becomes INTERESTED
-- ============================================================
CREATE OR REPLACE FUNCTION on_lead_interested()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'interested' AND OLD.status != 'interested' THEN
        INSERT INTO voice_calls (lead_id, priority, outcome)
        VALUES (NEW.id, 'high', 'pending');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_lead_interested ON leads;
CREATE TRIGGER trg_lead_interested
    AFTER UPDATE ON leads
    FOR EACH ROW
    EXECUTE FUNCTION on_lead_interested();

-- ============================================================
-- Trigger: Log agent events on lead status change
-- ============================================================
CREATE OR REPLACE FUNCTION log_lead_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO agent_events (agent_name, event_type, task_id, outcome, decision_log)
        VALUES (
            COALESCE(current_setting('alzen.agent_name', true), 'system'),
            'lead_status_change',
            NEW.id::text,
            'success',
            format('Status: %s → %s', OLD.status, NEW.status)
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_lead_status_change ON leads;
CREATE TRIGGER trg_lead_status_change
    AFTER UPDATE ON leads
    FOR EACH ROW
    EXECUTE FUNCTION log_lead_status_change();

-- ============================================================
-- Trigger: Update leads.voice_call_status when voice_calls.outcome changes
-- ============================================================
CREATE OR REPLACE FUNCTION sync_voice_call_status()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE leads SET
        voice_call_status = CASE NEW.outcome
            WHEN 'pending' THEN 'pending'
            WHEN 'completed' THEN 'completed'
            WHEN 'no-answer' THEN 'no-answer'
            WHEN 'interested' THEN 'completed'
            WHEN 'closed' THEN 'closed'
            WHEN 'dead' THEN 'completed'
            ELSE 'none'
        END,
        status = CASE
            WHEN NEW.outcome = 'closed' AND OLD.outcome != 'closed' THEN 'closed'
            WHEN NEW.outcome = 'interested' THEN 'interested'
            ELSE leads.status
        END
    WHERE id = NEW.lead_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_voice_call_sync ON voice_calls;
CREATE TRIGGER trg_voice_call_sync
    AFTER UPDATE ON voice_calls
    FOR EACH ROW
    EXECUTE FUNCTION sync_voice_call_status();

-- ============================================================
-- View: Voice Performance (weekly rollup)
-- ============================================================
CREATE OR REPLACE VIEW voice_performance AS
SELECT
  DATE_TRUNC('week', created_at) AS week,
  COUNT(*) AS total_calls,
  COUNT(*) FILTER (WHERE outcome = 'completed') AS connected,
  COUNT(*) FILTER (WHERE outcome IN ('interested','closed')) AS positive,
  COUNT(*) FILTER (WHERE outcome = 'closed') AS closed_deals,
  ROUND(AVG(duration_seconds)) AS avg_duration_sec,
  COALESCE(SUM(deal_value_usd), 0) AS total_deal_value
FROM voice_calls
GROUP BY DATE_TRUNC('week', created_at)
ORDER BY week DESC;

-- ============================================================
-- View: Pipeline Funnel
-- ============================================================
CREATE OR REPLACE VIEW pipeline_funnel AS
SELECT
  status,
  COUNT(*) AS count,
  ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM leads), 0), 1) AS pct
FROM leads
GROUP BY status
ORDER BY
  CASE status
    WHEN 'new' THEN 1 WHEN 'qualified' THEN 2 WHEN 'enriched' THEN 3
    WHEN 'emailed' THEN 4 WHEN 'called' THEN 5 WHEN 'replied' THEN 6
    WHEN 'interested' THEN 7 WHEN 'closed' THEN 8 WHEN 'disqualified' THEN 9
  END;

-- ============================================================
-- View: Email A/B Performance
-- ============================================================
CREATE OR REPLACE VIEW email_ab_performance AS
SELECT
  variant,
  COUNT(*) AS sent,
  COUNT(*) FILTER (WHERE replied = TRUE) AS replied,
  ROUND(COUNT(*) FILTER (WHERE replied = TRUE) * 100.0 / NULLIF(COUNT(*), 0), 1) AS reply_rate,
  ROUND(AVG(opened_count)) AS avg_opens
FROM emails
WHERE status IN ('sent', 'replied')
GROUP BY variant;

-- ============================================================
-- View: Daily Cost Summary
-- ============================================================
CREATE OR REPLACE VIEW daily_cost_summary AS
SELECT
  DATE_TRUNC('day', created_at) AS day,
  SUM(cost_usd) AS total_cost,
  SUM(tokens_used) AS total_tokens,
  COUNT(*) AS api_calls
FROM agent_events
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY day DESC;

-- ============================================================
-- View: Lead Source Performance
-- ============================================================
CREATE OR REPLACE VIEW lead_source_performance AS
SELECT
  source,
  COUNT(*) AS total_leads,
  COUNT(*) FILTER (WHERE status = 'qualified' OR qual_score >= 6) AS qualified,
  COUNT(*) FILTER (WHERE status = 'closed') AS closed,
  ROUND(AVG(qual_score), 1) AS avg_score
FROM leads
GROUP BY source
ORDER BY total_leads DESC;
