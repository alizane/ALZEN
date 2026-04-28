---
type: email
lead_id: "{{lead_id}}"
variant: "{{variant}}"  # A or B
status: draft
writer: EmailWriter
model: deepseek-chat-v3
tokens_used: 0
cost_usd: 0
created: "{{date}}"
---

# Email {{variant}}: {{company}} — {{contact_name}}

## Subject
{{subject}}

## Body
{{body}}

## Word Count
{{word_count}} (target: <120 for A, <160 for B)

## Personalization Tokens
- Company: {{company}}
- Pain Point: {{pain_point_ref}}
- Call Opener Hook: {{hook_ref}}

## Approval
- [ ] Sales Director review
- [ ] Board review (first 7 batches)
- [ ] Telegram notification sent

## Send Status
- Sent: {{sent_at}}
- Opened: {{opened_count}} times
- Replied: {{replied}}
- Reply Sentiment: {{sentiment}}
