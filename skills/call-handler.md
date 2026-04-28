---
name: call-handler
description: Reply classification + routing. 5-category. INTERESTED→immediate voice call creation.
trigger: Mailgun webhook / Every 5min Paperclip routine
module: modules/reply-handler/
db: emails (reply_sentiment, replied), voice_calls
---
# Reply Handler Skill
Classifies email replies within 5 minutes of Mailgun webhook: INTERESTED, OBJECTION, NOT_NOW, NO_FIT, AUTOMATED. INTERESTED + ICP≥7 = immediate voice_calls record creation. Batch classification: 50 replies = 1 DeepSeek call.
