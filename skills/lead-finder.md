---
name: lead-finder
description: Multi-source B2B lead discovery — web scraping, public APIs, email pattern matching, intent signals
trigger: Daily 6am cron / Paperclip routine "Lead Discovery"
module: modules/lead-finder/
db: leads, lead_finder_jobs
---

# Lead Finder Skill

Discovers 300-500 B2B leads/day from 5 independent sources.

## Sources
1. **Web Scraper** (`web_scraper.py`) — Playwright + BeautifulSoup crawler
2. **Public APIs** (`company_scraper.py`) — Angel List, Product Hunt, LinkedIn jobs
3. **Email Matcher** (`email_finder.py`) — Pattern-based email discovery (~70% accuracy)
4. **Intent Signals** (`intent_signals.py`) — Funding, hiring, tech-stack signals
5. **Deduplicator** (`deduplicator.py`) — Remove duplicates, verify emails

## Execution
```bash
python -m modules.lead-finder.src.web_scraper
python -m modules.lead-finder.src.company_scraper
```

## Output
- PostgreSQL: INSERT into leads table
- Vault: vault/leads/{lead_id}.md (from template)
- Paperclip task: "Qualify:{lead_id}" for each new lead

## Module Independence
- NO imports from other modules
- Communicates via PostgreSQL state + Paperclip task creation only
