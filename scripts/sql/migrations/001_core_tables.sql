-- ============================================================
-- ALZEN V3.0 — Core Schema (Phase 16)
-- PostgreSQL 16 | Database: alzen_db
-- 7 production tables + extensions + indexes
-- ============================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search on email/company

-- ============================================================
-- Table 1: leads
-- ============================================================
CREATE TABLE IF NOT EXISTS leads (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company VARCHAR(255) NOT NULL,
  contact_name VARCHAR(255),
  email VARCHAR(255) UNIQUE NOT NULL,
  title VARCHAR(255),
  linkedin_url TEXT,
  company_size INTEGER,
  funding_stage VARCHAR(50),
  industry VARCHAR(100),
  source VARCHAR(50)
    CHECK (source IN ('web_scraper','public_apis','email_matcher','job_boards','funding')),
  status VARCHAR(50) DEFAULT 'new'
    CHECK (status IN ('new','qualified','enriched','emailed','called','replied',
                      'interested','closed','disqualified')),
  qual_score SMALLINT CHECK (qual_score >= 1 AND qual_score <= 10),
  voice_call_status VARCHAR(30) DEFAULT 'none'
    CHECK (voice_call_status IN ('none','pending','scheduled','completed',
                                  'no-answer','closed')),
  disqual_reason TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for leads
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_qual_score ON leads(qual_score) WHERE qual_score IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_leads_company_trgm ON leads USING gin (company gin_trgm_ops);

-- ============================================================
-- Table 2: enrichments
-- ============================================================
CREATE TABLE IF NOT EXISTS enrichments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  pain_points JSONB,               -- [{point, evidence, confidence}]
  buying_signals JSONB,
  dm_profile JSONB,                -- {title, likely_objections, preferred_channels}
  recommended_email_angle TEXT,
  recommended_call_opener TEXT,    -- 30-second cold call opener
  model_used VARCHAR(100) DEFAULT 'deepseek-chat-v3',
  tokens_used INTEGER DEFAULT 0,
  cost_usd NUMERIC(8,6) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_enrichments_lead ON enrichments(lead_id);

-- ============================================================
-- Table 3: emails
-- ============================================================
CREATE TABLE IF NOT EXISTS emails (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  variant CHAR(1) CHECK (variant IN ('A','B')),
  subject TEXT,
  body TEXT,
  status VARCHAR(30) DEFAULT 'draft'
    CHECK (status IN ('draft','approved','sent','replied','failed')),
  sent_at TIMESTAMPTZ,
  opened_count INTEGER DEFAULT 0,
  replied BOOLEAN DEFAULT FALSE,
  reply_text TEXT,
  reply_sentiment VARCHAR(30)
    CHECK (reply_sentiment IN ('INTERESTED','OBJECTION','NOT_NOW','NO_FIT','AUTOMATED')),
  mailgun_message_id VARCHAR(255),
  model_used VARCHAR(100) DEFAULT 'deepseek-chat-v3',
  tokens_used INTEGER DEFAULT 0,
  cost_usd NUMERIC(8,6) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_emails_lead ON emails(lead_id);
CREATE INDEX IF NOT EXISTS idx_emails_status ON emails(status);
CREATE INDEX IF NOT EXISTS idx_emails_sentiment ON emails(reply_sentiment) WHERE reply_sentiment IS NOT NULL;

-- ============================================================
-- Table 4: voice_calls (NEW in V3.0)
-- ============================================================
CREATE TABLE IF NOT EXISTS voice_calls (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  asterisk_call_id VARCHAR(255) UNIQUE,
  phone_number VARCHAR(50),
  duration_seconds INTEGER DEFAULT 0,
  outcome VARCHAR(50) DEFAULT 'pending'
    CHECK (outcome IN ('pending','no-answer','busy','completed',
                       'interested','closed','dead','follow-up')),
  transcript_url TEXT,
  sentiment VARCHAR(50),
  objections JSONB,
  close_attempt BOOLEAN DEFAULT FALSE,
  deal_value_usd NUMERIC(12,2),
  recording_url TEXT,
  priority VARCHAR(20) DEFAULT 'standard'
    CHECK (priority IN ('high','standard','low')),
  attempt_number SMALLINT DEFAULT 1,
  call_time TIMESTAMPTZ,
  prospect_timezone VARCHAR(50) DEFAULT 'America/New_York',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_voice_calls_lead ON voice_calls(lead_id);
CREATE INDEX IF NOT EXISTS idx_voice_calls_outcome ON voice_calls(outcome);
CREATE INDEX IF NOT EXISTS idx_voice_calls_priority ON voice_calls(priority) WHERE priority = 'high';
CREATE INDEX IF NOT EXISTS idx_voice_calls_created ON voice_calls(created_at);

-- ============================================================
-- Table 5: agent_events
-- ============================================================
CREATE TABLE IF NOT EXISTS agent_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_name VARCHAR(100),
  event_type VARCHAR(100),
  task_id VARCHAR(255),
  model_used VARCHAR(100) DEFAULT 'deepseek-chat-v3',
  tokens_used INTEGER DEFAULT 0,
  cost_usd NUMERIC(8,6) DEFAULT 0,
  outcome VARCHAR(50) CHECK (outcome IN ('success','failed','blocked')),
  error_message TEXT,
  decision_log TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_events_agent ON agent_events(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_events_outcome ON agent_events(outcome);
CREATE INDEX IF NOT EXISTS idx_agent_events_created ON agent_events(created_at);

-- ============================================================
-- Table 6: patterns
-- ============================================================
CREATE TABLE IF NOT EXISTS patterns (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  pattern_type VARCHAR(100)
    CHECK (pattern_type IN ('icp_signal','email_angle','objection','call_opener','subject_line')),
  content TEXT,
  performance_score NUMERIC(4,2),
  sample_size INTEGER DEFAULT 0,
  source_week_start DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_patterns_score ON patterns(performance_score DESC);

-- ============================================================
-- Table 7: lead_finder_jobs (NEW in V3.0)
-- ============================================================
CREATE TABLE IF NOT EXISTS lead_finder_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source VARCHAR(50)
    CHECK (source IN ('web_scraper','public_apis','email_matcher','job_boards','funding')),
  search_params JSONB,
  leads_found INTEGER DEFAULT 0,
  leads_qualified INTEGER DEFAULT 0,
  cost_usd NUMERIC(8,4) DEFAULT 0,
  status VARCHAR(30) DEFAULT 'running'
    CHECK (status IN ('running','completed','failed')),
  error_message TEXT,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_lead_finder_jobs_status ON lead_finder_jobs(status);
CREATE INDEX IF NOT EXISTS idx_lead_finder_jobs_source ON lead_finder_jobs(source);
