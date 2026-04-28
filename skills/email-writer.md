---
name: email-writer
description: A/B cold email drafting via DeepSeek V3 — sub-120/sub-160 word variants, Mailgun SMTP
trigger: After enrichment (Paperclip task "Write Email:{lead_id}")
module: modules/email-outreach/
db: emails
---
# Email Writer Skill
Drafts 2 A/B variants per lead. Variant A: <120 words (punchy). Variant B: <160 words (detailed). Mailgun SMTP send after Telegram approval. Hook types: pain_point, roi, curiosity, competitor.
