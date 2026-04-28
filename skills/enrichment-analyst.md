---
name: enrichment-analyst
description: Deep research per qualified lead — 3 pain points, buying signals, DM profile, email angle, call opener
trigger: After qualification (Paperclip task "Enrich:{lead_id}")
module: modules/enrichment/
db: enrichments
---
# Enrichment Analyst Skill
Extracts 3 pain points with evidence + confidence, buying signals, decision-maker profile, recommended email angle, and 30-second cold call opener. Token budget: <300 tokens/lead.
