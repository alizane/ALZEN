-- ============================================================
-- ALZEN V3.0 — Seed Data (Phase 16)
-- Minimal seed for development and testing
-- ============================================================

-- Seed: ICP signals into patterns table
INSERT INTO patterns (pattern_type, content, performance_score, sample_size) VALUES
('icp_signal', 'Series A-C funding within 12 months', 8.5, 50),
('icp_signal', '50-500 employees with SaaS product', 9.0, 75),
('icp_signal', 'SDR job postings (active pipeline problem)', 8.0, 30),
('icp_signal', '20%+ YoY headcount growth', 7.5, 40),
('icp_signal', 'Tech stack: Snowflake, Databricks, Kubernetes', 7.0, 25),
('email_angle', 'ROI-focused cold email: "X companies save $Y/mo with our approach"', 8.2, 15),
('email_angle', 'Pain-point hook: "Are you still doing [pain_point] manually?"', 7.8, 20),
('objection', '"Too expensive" → "What does NOT solving this cost you per month?"', 8.5, 10),
('objection', '"Not right now" → "What changes in [timeframe] that makes this relevant?"', 7.5, 8),
('call_opener', '30-second opener referencing specific pain point + metric', 8.0, 12),
('subject_line', 'Question about [pain_point] at [company]', 8.3, 18),
('subject_line', '[competitor] just [action] — curious if you are seeing this too', 7.9, 14);

-- Seed: Test lead (for development smoke testing)
INSERT INTO leads (company, contact_name, email, title, source, status, qual_score)
VALUES ('Acme SaaS Corp', 'Jane Smith', 'jane@acmecorp.example.com', 'VP Sales', 'web_scraper', 'new', 7)
ON CONFLICT (email) DO NOTHING;
