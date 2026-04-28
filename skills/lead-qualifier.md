---
name: lead-qualifier
description: DeepSeek V3 ICP scoring gate — scores leads 1-10, triggers voice calls for high-intent
trigger: Every 15min / Paperclip routine "Lead Intake Queue"
module: modules/qualifier/
db: leads (qual_score, status, voice_call_status)
---

# Lead Qualifier Skill

Scores every lead 1-10 against ICP signals in `vault/patterns/icp-signals.md`.

## Scoring
- 8-10: Auto-qualify → enrich immediately, voice call eligible
- 6-7: Qualify → enrich, email first
- 4-5: Hold → low priority queue
- 1-3: Auto-disqualify

## Voice Call Triggers
- ICP score >= 8
- ICP 7 + INTERESTED email reply
- Funding announcement + SDR job posting within same week

## Token Budget: <200 tokens/lead
