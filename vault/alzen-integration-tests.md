# ALZEN V3.0 — Integration Test Checklist (Phase 39)

## Pre-Flight
- [ ] All 5 services green: PostgreSQL, Redis, Paperclip, Graphify MCP, Hermes
- [ ] Docker: 4 containers running (postgres, pgadmin, redis, paperclip_db)
- [ ] Graphify MCP query: `curl http://localhost:8889/mcp/query?q=lead-finder` returns results
- [ ] Graphify God Nodes: `curl http://localhost:8889/mcp/god-nodes` returns top 10
- [ ] Paperclip health: `curl http://localhost:3100/api/health` returns 200
- [ ] DeepSeek API key configured in .env

## Module Independence
- [ ] Lead Finder dry run produces leads in vault/leads/ (no other modules needed)
- [ ] Qualifier runs independently (reads vault/ + PostgreSQL only)
- [ ] Enrichment runs independently
- [ ] Email Writer runs independently
- [ ] Voice Closer runs independently
- [ ] Reply Handler runs independently
- [ ] Memory Manager runs independently
- [ ] Remove any module folder → remaining modules continue functioning

## Pipeline Flow
- [ ] Lead Finder: 50+ test leads generated
- [ ] Lead Qualifier: Test lead scored 1-10
- [ ] Enrichment: 3 pain points in vault/enrichments/
- [ ] Email: 2 A/B variants in vault/emails/
- [ ] Telegram: Approval message received for email batch
- [ ] Voice: Asterisk test call connects
- [ ] Reply: Webhook classification returns INTERESTED for "tell me more"
- [ ] Memory: Weekly report generated

## Cost Verification
- [ ] Infrastructure: $0 (all local Docker)
- [ ] DeepSeek API: <500 tokens/lead average
- [ ] Monthly projection: <$15/month at 500 leads/day
- [ ] No paid API keys in tracked files (.env is gitignored)

## Security
- [ ] .env files gitignored
- [ ] .env files chmod 600
- [ ] No hardcoded secrets in source code
- [ ] PostgreSQL password not default in production
- [ ] AgentShield scan reports 0 critical
