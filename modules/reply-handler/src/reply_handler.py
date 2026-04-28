"""
Reply Handler (Phase 23) — Mailgun webhook reply classifier.
5-category classification: INTERESTED, OBJECTION, NOT_NOW, NO_FIT, AUTOMATED.
5-minute SLA. INTERESTED replies trigger immediate voice call creation.
"""
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent.parent


@dataclass
class ReplyClassification:
    lead_id: str
    email_id: str
    reply_text: str
    sentiment: str  # INTERESTED|OBJECTION|NOT_NOW|NO_FIT|AUTOMATED
    confidence: float
    requires_voice_call: bool
    requires_escalation: bool
    classified_at: str = ""


class ReplyHandler:
    """Classifies email replies within 5 minutes of receipt."""

    SENTIMENT_PATTERNS = {
        "INTERESTED": {
            "keywords": [
                "interested", "tell me more", "demo", "pricing", "trial",
                "when can we talk", "let's chat", "sounds good", "how does it work",
                "set up a call", "schedule", "available", "free for a call",
                "yes", "great", "love to learn more", "send details"
            ],
            "weight": 1.0,
            "voice_call_trigger": True
        },
        "OBJECTION": {
            "keywords": [
                "too expensive", "not sure", "need to think", "budget",
                "not convinced", "what's the catch", "competitor",
                "already using", "under contract", "timing"
            ],
            "weight": 0.8,
            "voice_call_trigger": False
        },
        "NOT_NOW": {
            "keywords": [
                "not now", "later", "next quarter", "next month",
                "revisit", "down the road", "future", "maybe next year",
                "not a priority", "busy right now"
            ],
            "weight": 0.7,
            "voice_call_trigger": False
        },
        "NO_FIT": {
            "keywords": [
                "not interested", "remove me", "unsubscribe", "stop emailing",
                "not a fit", "wrong person", "don't contact", "no thanks",
                "not relevant", "different industry"
            ],
            "weight": 0.9,
            "voice_call_trigger": False
        },
        "AUTOMATED": {
            "keywords": [
                "out of office", "vacation", "automatic reply", "no longer with",
                "left the company", "maternity leave", "medical leave",
                "OOO", "auto-reply", "on leave"
            ],
            "weight": 0.95,
            "voice_call_trigger": False
        }
    }

    def __init__(self):
        self.classified_count = 0
        self.sla_violations = 0

    def classify(self, reply_text: str) -> ReplyClassification:
        """Classify a single email reply. Production: DeepSeek V3 batch classification."""
        reply_lower = reply_text.lower().strip()
        scores = {}

        for sentiment, config in self.SENTIMENT_PATTERNS.items():
            score = 0
            matched = []
            for kw in config["keywords"]:
                if kw.lower() in reply_lower:
                    score += 1
                    matched.append(kw)
            if matched:
                scores[sentiment] = {
                    "score": score,
                    "weight": config["weight"],
                    "matched": matched,
                    "voice_call_trigger": config["voice_call_trigger"]
                }

        if not scores:
            # Default: treat as OBJECTION if can't classify
            return ReplyClassification(
                lead_id="", email_id="",
                reply_text=reply_text[:200],
                sentiment="OBJECTION",
                confidence=0.3,
                requires_voice_call=False,
                requires_escalation=False,
                classified_at=datetime.now(timezone.utc).isoformat()
            )

        # Pick highest combined score
        best = max(scores.items(), key=lambda x: x[1]["score"] * x[1]["weight"])
        sentiment = best[0]
        info = best[1]

        return ReplyClassification(
            lead_id="", email_id="",
            reply_text=reply_text[:200],
            sentiment=sentiment,
            confidence=min(0.95, info["score"] / 5 * info["weight"]),
            requires_voice_call=info["voice_call_trigger"],
            requires_escalation=sentiment in ("INTERESTED", "OBJECTION"),
            classified_at=datetime.now(timezone.utc).isoformat()
        )

    def batch_classify(self, replies: list[dict]) -> list[ReplyClassification]:
        """Batch classify replies. Production: 1 DeepSeek call for 50 replies."""
        results = []
        for reply in replies:
            classification = self.classify(reply.get("body", ""))
            classification.lead_id = reply.get("lead_id", "")
            classification.email_id = reply.get("email_id", "")
            results.append(classification)
        return results

    def get_voice_call_queue(self, classifications: list[ReplyClassification]) -> list[str]:
        """Return lead_ids that need immediate voice calls."""
        return [c.lead_id for c in classifications
                if c.requires_voice_call and c.sentiment == "INTERESTED"]

    def handle_webhook(self, mailgun_payload: dict) -> ReplyClassification | None:
        """Process incoming Mailgun webhook."""
        try:
            reply_text = mailgun_payload.get("stripped-text") or mailgun_payload.get("body-plain", "")
            message_id = mailgun_payload.get("Message-Id", "")
            recipient = mailgun_payload.get("recipient", "")

            # Find lead by email
            classification = self.classify(reply_text)
            classification.email_id = message_id

            self.classified_count += 1
            return classification
        except Exception:
            return None
