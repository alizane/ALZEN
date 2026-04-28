---
type: call
lead_id: "{{lead_id}}"
company: "{{company}}"
phone: "{{phone_number}}"
closer: VoiceCloser
model: deepseek-chat-v3
status: pending
priority: "{{priority}}"  # high | standard | low
created: "{{date}}"
---

# Call Script: {{company}} — {{contact_name}}

## Pre-Call Context
- **Pain Points:** {{top_3_pain_points}}
- **Email Sent:** {{email_sent_date}}
- **Reply Sentiment:** {{reply_sentiment}}
- **ICP Score:** {{qual_score}}/10

## 30-Second Opener
{{call_opener_30sec}}

## Full Script (5 sections)
### 1. Opening (15 sec)
{{opening}}

### 2. Hook (30 sec)
{{hook}}

### 3. Value Proposition (45 sec)
{{value_prop}}

### 4. Objection Handling
See `objection-tree.json` for full 40-branch tree.

Key objections for this lead:
{{key_objections}}

### 5. Close (30 sec)
{{close_attempt}}

## Call Outcome
- **Attempt:** {{attempt_number}}/3
- **Time:** {{call_time}} (prospect timezone: {{timezone}})
- **Duration:** {{duration_seconds}}s
- **Outcome:** {{outcome}} (pending | no-answer | busy | completed | interested | closed | dead | follow-up)
- **Deal Value:** ${{deal_value_usd}}
- **Recording:** {{recording_url}}

## Follow-Up
{{follow_up_notes}}
