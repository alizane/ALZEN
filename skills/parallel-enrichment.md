---
name: parallel-enrichment
description: Batch enrichment across multiple qualified leads using parallel subagents. 10 concurrent workers.
trigger: After batch qualification / Paperclip routine "Enrich:{lead_id}" × N
module: modules/enrichment/
db: enrichments
---

# Parallel Enrichment Skill

Runs enrichment across multiple qualified leads simultaneously using Hermes subagents.

## Execution
- Spawns up to 10 parallel enrichment subagents
- Each subagent processes 1 lead (3 pain points, buying signals, DM profile, email angle, call opener)
- Token budget: <300 tokens per lead
- Writes results to vault/enrichments/{lead_id}-enrich.md
- Updates PostgreSQL enrichments table
- Creates Paperclip task "Write Email:{lead_id}" for each enriched lead

## Parallelization Rules
- Max 10 concurrent subagents
- Each subagent is fully isolated (no shared state)
- Communicate via PostgreSQL + Paperclip tasks only
- Failed enrichments auto-retry once, then escalate to Telegram

## Cost
- 10 leads × 300 tokens × $0.00005 = ~$0.0015 per batch
