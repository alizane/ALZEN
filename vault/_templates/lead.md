---
type: lead
id: "{{lead_id}}"
company: "{{company}}"
contact_name: "{{contact_name}}"
email: "{{email}}"
title: "{{title}}"
linkedin_url: "{{linkedin_url}}"
source: "{{source}}"
status: new
qual_score: 0
created: "{{date}}"
---

# {{company}} — {{contact_name}}

## Raw Intake
- **Company:** {{company}}
- **Contact:** {{contact_name}}, {{title}}
- **Email:** {{email}}
- **LinkedIn:** {{linkedin_url}}
- **Source:** {{source}} (web_scraper | public_apis | email_matcher | job_boards | funding)
- **Company Size:** {{company_size}}
- **Industry:** {{industry}}
- **Funding:** {{funding_stage}}

## Discovery Context
{{discovery_context}}

## Next Steps
- [ ] Qualify (ICP score 1-10)
- [ ] Enrich (3 pain points)
- [ ] Draft email (A/B variants)
