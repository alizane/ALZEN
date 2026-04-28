---
type: audit-log
agent: "{{agent_name}}"
event: "{{event_type}}"
task_id: "{{task_id}}"
model: deepseek-chat-v3
tokens_used: 0
cost_usd: 0
outcome: "{{outcome}}"
created: "{{date}}"
---

# Agent Audit: {{agent_name}} — {{event_type}}

## Event
- **Agent:** {{agent_name}}
- **Event:** {{event_type}}
- **Task:** {{task_id}}
- **Outcome:** {{outcome}} (success | failed | blocked)

## Decision Log
{{decision_log}}

## Graph Context
- Community: {{community_id}}
- God Nodes Consulted: {{god_nodes}}
- Query: {{graph_query}}

## Cost
- Tokens: {{tokens_used}} (input: {{input_tokens}}, output: {{output_tokens}})
- Cost: ${{cost_usd}}

## Errors
{{error_details}}

## Approval Gates Passed
{{approval_gates}}
