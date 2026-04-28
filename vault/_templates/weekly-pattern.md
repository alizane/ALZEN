---
type: pattern-report
period: "{{week_start}} → {{week_end}}"
analyst: MemoryManager
model: deepseek-chat-v3
tokens_used: 0
cost_usd: 0
created: "{{date}}"
---

# Weekly Memory Analysis — {{week_start}} to {{week_end}}

## Pipeline Summary
| Stage | Count | Change |
|-------|-------|--------|
| New Leads | {{new_leads}} | {{delta}} |
| Qualified | {{qualified}} | {{delta}} |
| Enriched | {{enriched}} | {{delta}} |
| Emailed | {{emailed}} | {{delta}} |
| Called | {{called}} | {{delta}} |
| Closed | {{closed}} | {{delta}} |

## ICP Signal Evolution
### Signals That Worked
{{winning_signals}}

### Signals That Failed
{{failing_signals}}

### New Signals to Test
{{new_signals}}

## Email Performance
| Variant | Sent | Opened | Replied | Reply Rate |
|---------|------|--------|---------|------------|
| A | {{a_sent}} | {{a_opened}} | {{a_replied}} | {{a_rate}}% |
| B | {{b_sent}} | {{b_opened}} | {{b_replied}} | {{b_rate}}% |

### Top 3 Subjects
{{top_subjects}}

## Call Performance
- Total Calls: {{total_calls}}
- Connected: {{connected}} ({{connect_rate}}%)
- Interested: {{interested}}
- Closed: {{closed_deals}} — ${{total_deal_value}}
- Avg Duration: {{avg_duration}}s
- Top Objection: {{top_objection}}

## Cost Report
- DeepSeek API: ${{api_cost}}
- Infrastructure: $0.00
- **Total:** ${{total_cost}}

## Learnings
{{learnings}}

## Actions for Next Week
{{actions}}
