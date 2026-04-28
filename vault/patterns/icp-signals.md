---
type: icp-definition
version: 1.0.0
last_updated: 2026-04-28
updated_by: operator
model: deepseek-chat-v3
---

# ICP Signals — ALZEN Ideal Customer Profile

## Strong Positive Signals (Qualify Immediately if 2+)
- Series A-C funding within last 12 months (via Crunchbase RSS / web scraping)
- 50-500 employees (via LinkedIn / Angel List)
- SaaS product with existing sales team
- Growing headcount +20% YoY (via LinkedIn scraping)
- Job postings for SDRs or AEs (active pipeline problem → HIGH PRIORITY)
- Tech stack includes modern tools (Snowflake, Databricks, Kubernetes, AWS/GCP)

## Immediate Voice Call Triggers (Skip Email Queue)
- Email reply contains: 'interested', 'call', 'demo', 'pricing', 'when can we talk', 'let's chat'
- Lead replies within 2 hours of email send (high intent signal)
- Prospect opens email 3+ times without replying (Mailgun webhook tracking)
- ICP score >= 8 AND reply sentiment = INTERESTED
- Funding announcement AND SDR job posting within same week

## Medium Signals (Qualify if 3+)
- 20-200 employees with +10% headcount growth
- Non-SaaS tech company (consulting, agency, services)
- CTO/VP Engineering as primary contact
- Active blog or content marketing (signals market education)
- Conference speaking or webinar activity

## Disqualification Signals (Auto-Reject)
- <10 employees (no budget for external tools)
- >5000 employees (enterprise — 12+ month sales cycle, wrong channel)
- Non-SaaS, government, education, non-profit
- No online presence (no LinkedIn, no company website)
- Generic email address (gmail.com, yahoo.com — not business)
- Company founded <6 months ago (pre-revenue, no budget)
- Previously disqualified within 90 days (no change in signals)

## Closer Signal Scoring Matrix
| Signal | Weight | Auto-Voice-Call Threshold |
|--------|--------|---------------------------|
| ICP Score 7+ | +3 | Yes |
| INTERESTED reply | +5 | Yes (immediate) |
| Funding <3 months | +2 | If combined with INTERESTED |
| SDR Job Posting | +2 | If ICP >= 7 |
| 3+ Email Opens | +1 | If 2+ other signals |
| LinkedIn Profile View | +1 | Supplementary only |

## Scoring Rules
- Score range: 1-10
- 8-10: Auto-qualify, enrich immediately, voice call eligible
- 6-7: Qualify, enrich, email first (voice only if INTERESTED reply)
- 4-5: Qualify, hold (low priority queue, process during low-volume periods)
- 1-3: Auto-disqualify, log reason in leads.disqual_reason

## Token Budget Per Lead
- Qualification: <200 tokens
- Enrichment: <300 tokens
- Email A/B pair: <500 tokens
- Call script: <300 tokens (pre-generated, not live)
- **Total per lead: <500 tokens** (qual + enrich + email)
