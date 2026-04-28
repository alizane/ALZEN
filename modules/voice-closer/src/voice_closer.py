"""
Voice Closer (Phase 21) — Asterisk SIP + Google Cloud TTS call agent.
Calls INTERESTED prospects. Harvey Specter confidence + Andrew Tate directness.
Pre-generated scripts via DeepSeek V3. 40-branch objection tree.
"""
import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent.parent
SCRIPTS_DIR = PROJECT_DIR / "modules" / "voice-closer" / "scripts"


@dataclass
class CallResult:
    lead_id: str
    company: str
    phone_number: str
    asterisk_call_id: str | None = None
    duration_seconds: int = 0
    outcome: str = "pending"  # pending|no-answer|busy|completed|interested|closed|dead|follow-up
    objections_hit: list[str] = field(default_factory=list)
    close_attempted: bool = False
    deal_value_usd: float | None = None
    recording_url: str | None = None
    transcript: str | None = None
    sentiment: str | None = None


class VoiceCloser:
    """Asterisk-based outbound voice closer with Google TTS."""

    CALL_WINDOW = (9, 18)  # 9am-6pm prospect local time
    MAX_ATTEMPTS = 3
    RETRY_SCHEDULE = [1, 3, 7]  # Day 1, Day 3, Day 7
    MAX_DAILY_CALLS = 50

    def __init__(self):
        self.asterisk_ami_host = os.environ.get("ASTERISK_AMI_HOST", "localhost")
        self.asterisk_ami_port = int(os.environ.get("ASTERISK_AMI_PORT", "5038"))
        self.asterisk_ami_user = os.environ.get("ASTERISK_AMI_USER", "admin")
        self.asterisk_ami_password = os.environ.get("ASTERISK_AMI_PASSWORD", "")
        self.google_tts_key = os.environ.get("GOOGLE_TTS_API_KEY", "")
        self.google_tts_voice = os.environ.get("GOOGLE_TTS_VOICE", "en-US-Neural2-C")
        self.calls_today = 0
        self.daily_limit = self.MAX_DAILY_CALLS

    def is_in_call_window(self, prospect_timezone: str = "America/New_York") -> bool:
        """Check if current time is within 9am-6pm in prospect's timezone."""
        # Simplified check — production would use pytz
        hour = datetime.now().hour
        return self.CALL_WINDOW[0] <= hour < self.CALL_WINDOW[1]

    def can_call_today(self) -> bool:
        return self.calls_today < self.daily_limit

    def lookup_phone(self, lead: dict) -> str | None:
        """Look up phone number from lead data or enrichment."""
        return lead.get("phone_number") or lead.get("phone")

    def generate_script(self, lead: dict, enrichment: dict) -> str:
        """Generate a call script from the closer persona template."""
        script_file = SCRIPTS_DIR / "call-script-generator.md"
        template = script_file.read_text() if script_file.exists() else ""
        company = lead.get("company", "[Company]")
        contact = lead.get("contact_name", "there")
        pain_points = enrichment.get("pain_points", [])
        first_pain = pain_points[0]["point"] if pain_points else "growth"

        return f"""CALL SCRIPT: {company}
CONTACT: {contact}
PAIN POINT: {first_pain}

OPENING (15 sec):
"Hi {contact}, this is Alex. I know you weren't expecting my call — I'll be brief."

HOOK (30 sec):
"I've been looking at {company}'s growth. Most teams at your stage are dealing with {first_pain}. Is that something on your radar right now?"

VALUE (45 sec):
[If YES]: "The reason I'm calling specifically — we built a system that handles this autonomously. Our clients typically see [specific metric] within [timeframe]."

OBJECTION HANDLING:
[See objection-tree.json — 40 branches]

CLOSE (30 sec):
"Based on what you've told me, this is exactly what we solve. Does Tuesday or Wednesday work better for a 15-minute follow-up?"
"""

    def initiate_call(self, lead: dict, script: str) -> CallResult:
        """Initiate an outbound call via Asterisk AMI."""
        phone = self.lookup_phone(lead)
        if not phone:
            return CallResult(
                lead_id=lead.get("id", ""),
                company=lead.get("company", "?"),
                phone_number="",
                outcome="dead"
            )

        if not self.can_call_today():
            return CallResult(
                lead_id=lead.get("id", ""),
                company=lead.get("company", "?"),
                phone_number=phone,
                outcome="pending"
            )

        self.calls_today += 1

        # Production: Asterisk AMI Originate action
        # For now, return structured result
        return CallResult(
            lead_id=lead.get("id", ""),
            company=lead.get("company", "?"),
            phone_number=phone,
            asterisk_call_id=f"call-{int(time.time())}",
            duration_seconds=0,
            outcome="pending",
            recording_url=None
        )

    def handle_outcome(self, result: CallResult, outcome: str, **kwargs) -> CallResult:
        """Update call result based on outcome."""
        result.outcome = outcome
        if outcome == "closed":
            result.close_attempted = True
            result.deal_value_usd = kwargs.get("deal_value", 0)
        elif outcome == "interested":
            result.outcome = "interested"
        elif outcome == "no-answer":
            result.outcome = "no-answer"
        elif outcome == "dead":
            result.outcome = "dead"
        return result

    def should_retry(self, result: CallResult, attempt: int) -> bool:
        """Determine if call should be retried."""
        if result.outcome in ("closed", "dead"):
            return False
        if attempt >= self.MAX_ATTEMPTS:
            return False
        if result.outcome == "no-answer":
            return attempt < 3  # Retry twice after no-answer
        if result.outcome == "busy":
            return True  # Retry in 4 hours
        return False
