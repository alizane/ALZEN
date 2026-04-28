# ALZEN V3.0 — DeepSeek-Only Edition

**Enterprise Autonomous Closing Agency | Zero-Cost Stack**
**GitHub:** https://github.com/alizane/ALZEN

## Mission
Build a fully autonomous B2B sales closing agency that runs 24/7 without human involvement. Finds leads, qualifies them, enriches them, writes personalised cold emails, and makes live AI voice calls to close deals.

## Tech Stack
- **LLM:** DeepSeek V3 (chat) — $0.14/1M input, $0.28/1M output
- **Orchestrator:** Paperclip (port 3100) — Boss layer, org chart, budgets, governance
- **Agent Workforce:** Hermes — Skills-based, modular, parallel subagents
- **Knowledge Graph:** Graphify — MCP on port 8889, browser on port 8888
- **Database:** PostgreSQL 16 (port 5432) + Redis 7 (port 6379)
- **Voice:** Asterisk (SIP port 5060) + Google Cloud TTS (free tier)
- **Email:** Mailgun free tier (10k/month)
- **Mobile:** Telegram bot (@alzen_control_bot)
- **Memory:** Obsidian vault (markdown, human-readable)
- **Planning:** GSD workflow engine

## Architecture Principles
1. **Module Independence** — Every department is fully independent. Removing any module does NOT affect others. PostgreSQL + Paperclip tasks = only bridge.
2. **Graph-First** — Always query Graphify MCP before reading source files. God-node navigation.
3. **Vault-First** — All reasoning written to vault/ before any external action.
4. **Zero Cost** — $0 infrastructure. DeepSeek API only (~$12/month).
5. **Governance Gates** — 6 approval gates. Telegram for operator approval.

## Cost Model
| Item | Monthly Cost |
|---|---|
| Infrastructure (Docker, local) | $0 |
| Lead Discovery (web scraping + free APIs) | $0 |
| Email (Mailgun free tier) | $0 |
| Voice (Asterisk + Google TTS free) | $0 |
| LLM (DeepSeek V3 ~500 leads × 500 tokens) | ~$12 |
| **TOTAL** | **~$12/month** |

## 9-Agent Org Chart
1. ALZEN CEO — Strategy, decomposition, budget oversight
2. Sales Director — Coordinates lead-to-close pipeline
3. Lead Finder — Web scraping, public APIs, email matching
4. Lead Qualifier — DeepSeek ICP scoring gate
5. Enrichment Analyst — Deep research, 3 pain points per lead
6. Email Writer — A/B personalised cold email
7. Voice Closer — Asterisk + Google TTS local call closer
8. Reply Handler — Webhook reply classification, routing
9. Memory Manager — Weekly learning, ICP evolution

## Current Phase
Phase 07 — GSD Project Planning Integration
