---
name: voice-closer
description: Asterisk SIP + Google TTS outbound closer. Harvey+Tate persona. 40 objection branches.
trigger: INTERESTED reply detected / Paperclip routine "Voice Call Scheduler" (every 30min)
module: modules/voice-closer/
db: voice_calls, leads (voice_call_status, status)
---
# Voice Closer Skill
Initiates Asterisk SIP calls to INTERESTED prospects. Google TTS free tier (100k chars/mo). Persona: "Alex" — confident, never apologizes, closes with binary choices. Max 3 attempts (Day 1/3/7). Window: 9am-6pm prospect local time. 50 calls/day capacity.
