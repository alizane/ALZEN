-- ALZEN V3.0 — Database Initialization
-- Run: docker exec -i alzen_postgres psql -U alzen_admin -d alzen_db < init.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
\i migrations/001_core_tables.sql
\i migrations/002_triggers.sql
\i migrations/003_seed_data.sql
