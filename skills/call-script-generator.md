---
name: call-script-generator
description: Generates per-lead call scripts using DeepSeek V3. 5-section scripts: opening, hook, value prop, objection prep, close.
trigger: voice_calls record created with status='pending'
module: modules/voice-closer/
db: voice_calls
---

# Call Script Generator Skill

Generates personalized call scripts for each lead before outbound Asterisk call.

## Script Structure (5 Sections)
1. **Opening (15 sec)** — Name, reason for calling, time check
2. **Hook (30 sec)** — Specific pain point reference + metric
3. **Value Proposition (45 sec)** — What we solve, proof point, relevance
4. **Objection Preparation** — Top 3 likely objections with reframes from objection-tree.json
5. **Close (30 sec)** — Binary choice ("Tuesday or Wednesday?")

## Inputs
- Lead record (company, contact_name, title, qual_score)
- Enrichment data (3 pain points, buying signals, DM profile)
- ICP score and matched signals
- Email reply sentiment (if replied)

## Output
- `vault/calls/{lead_id}-script.md` — Full call script
- `voice_calls` table updated with script metadata

## Token Budget: <300 tokens per script

## Persona: "Alex" (Harvey Specter + Andrew Tate)
See `modules/voice-closer/scripts/closer-persona.md` for full persona rules.
