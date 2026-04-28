---
name: call-campaign-manager
description: Voice call campaign rules — timezone windows, retry schedules, daily limits, priority queue
trigger: Voice Call Scheduler routine (every 30min)
---
# Call Campaign Manager Skill
Enforces: 9am-6pm prospect timezone, max 3 attempts, 50 calls/day, INTERESTED priority queue. Retry: no-answer→next day, busy→4hr, voicemail→7-day pause.
