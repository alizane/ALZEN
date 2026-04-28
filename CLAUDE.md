# ALZEN V3.0 — DeepSeek-Only Autonomous Closing Agency

## Graph-First Navigation (MANDATORY)
Before exploring ANY file, query the graph:
- MCP server: http://localhost:8889/mcp
- Visual browser: http://localhost:8888/graph.html
- Report: graphify-out/GRAPH_REPORT.md

## Quick Links
- [[.planning/PROJECT]] — Mission, stack, architecture
- [[.planning/ROADMAP]] — 40-phase build map
- [[vault/ALZEN_CORE]] — Vault index
- [[vault/patterns/icp-signals]] — ICP definition (MOST IMPORTANT FILE)

## Tech Stack
DeepSeek V3 · Graphify (MCP 8889) · Hermes · Paperclip (3100) · PostgreSQL (5432) · Redis (6379) · Asterisk SIP

## Cost
$0 infrastructure + ~$12/month DeepSeek API

## Module Independence
Every module in `modules/` is fully independent. PostgreSQL + Paperclip tasks = only bridge.
