# ALZEN V3.0 — Core Reference

**Enterprise Autonomous B2B Sales Closing Agency**
**Stack:** DeepSeek V3 · Graphify · GSD · Hermes · Paperclip
**Cost:** $0 infrastructure + ~$12/month DeepSeek API
**Status:** Layers 0-3 complete, Layer 4 in progress

## Quick Links
- [[icp-signals]] — ICP definition and scoring matrix
- [[../.planning/ROADMAP]] — 40-phase build map
- [[../.planning/PROJECT]] — Mission, stack, architecture
- [[../graphify-out/GRAPH_REPORT]] — Knowledge graph report

## Pipeline
```
Lead Discovery (6am) → Qualify (15min) → Enrich (4hr) → Email (4hr)
→ [TELEGRAM APPROVAL] → Mailgun Send → Reply Classify (5min SLA)
→ INTERESTED → Voice Call (30min) → CLOSED → Telegram Alert
```

## Services
| Service | Port | Status |
|---------|------|--------|
| Graphify MCP | 8889 | Configured |
| Graphify Browser | 8888 | Configured |
| Paperclip | 3100 | Configured |
| PostgreSQL (ALZEN) | 5432 | Docker |
| PostgreSQL (Paperclip) | 54329 | Docker |
| pgAdmin | 5050 | Docker |
| Redis | 6379 | Docker |
| Asterisk SIP | 5060 | Phase 31 |

## Key Files
- `vault/patterns/icp-signals.md` — ICP definition (MOST IMPORTANT)
- `hermes/SOUL.md` — Agent persona
- `hermes/cli-config.yaml` — DeepSeek V3 routing
- `vault/alzen-company-seed.json` — 9-agent org chart
- `vault/alzen-governance.json` — Budget + 6 gates
- `.planning/ROADMAP.md` — 40-phase build tracker

## Vault Structure
```
vault/
├── _templates/    ← 6 markdown templates
├── leads/         ← Raw lead intake (one .md per lead)
├── enrichments/   ← {lead_id}-enrich.md
├── emails/        ← {lead_id}-A.md, {lead_id}-B.md
├── calls/         ← {lead_id}-script.md
├── patterns/      ← icp-signals.md, weekly-{date}.md
└── agents/        ← Audit logs
```
