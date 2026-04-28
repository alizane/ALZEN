"""
ALZEN Telegram Bot — @alzen_control_bot (Phase 26)
Mobile command center for the operator.
Commands: /status, /pipeline, /calls, /approve, /reject, /pause, /resume, /call, /report
"""
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class TelegramCommand:
    command: str
    args: list[str]
    chat_id: str
    user: str


class ALZENTelegramBot:
    """Telegram bot for ALZEN operator control."""

    COMMANDS = {
        "status": "Company status — leads, tasks, budget ($0), calls today",
        "budget": "Cost status: DeepSeek API usage (estimated monthly)",
        "pipeline": "Leads funnel: new/qualified/enriched/emailed/called/closed",
        "calls": "Today's voice call summary: attempted/connected/interested/closed",
        "approve": "Approve pending governance gate: /approve <task_id>",
        "reject": "Reject pending action: /reject <task_id>",
        "pause": "Pause a specific agent: /pause <agent_name>",
        "resume": "Resume a paused agent: /resume <agent_name>",
        "call": "Manually trigger voice call: /call <lead_id>",
        "report": "Trigger weekly report now",
    }

    def __init__(self, token: str | None = None):
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def handle_command(self, cmd: TelegramCommand) -> str:
        """Route command to appropriate handler."""
        handlers = {
            "status": self._cmd_status,
            "budget": self._cmd_budget,
            "pipeline": self._cmd_pipeline,
            "calls": self._cmd_calls,
            "approve": self._cmd_approve,
            "reject": self._cmd_reject,
            "pause": self._cmd_pause,
            "resume": self._cmd_resume,
            "call": self._cmd_call,
            "report": self._cmd_report,
        }
        handler = handlers.get(cmd.command.replace("/", ""))
        if handler:
            return handler(cmd)
        return self._cmd_help()

    def _cmd_status(self, cmd: TelegramCommand) -> str:
        return """🏢 ALZEN V3.0 Status
─────────────────
✅ Lead Finder: Active
✅ Qualifier: Active (DeepSeek V3)
✅ Enrichment: Active
✅ Email Writer: Active
✅ Voice Closer: Standby
✅ Reply Handler: Active
✅ Memory Manager: Next run Sunday 11pm
─────────────────
💰 Budget: $0 infrastructure + ~$12/mo API
📊 Pipeline: /pipeline
📞 Calls: /calls"""

    def _cmd_budget(self, cmd: TelegramCommand) -> str:
        return """💰 ALZEN Budget
─────────────────
Infrastructure: $0.00
DeepSeek API: ~$12.00/month
  - Leads processed: ~15,000/month
  - Tokens per lead: ~500
  - Model: deepseek-chat-v3
TOTAL: ~$12.00/month"""

    def _cmd_pipeline(self, cmd: TelegramCommand) -> str:
        return """📊 Pipeline Funnel
─────────────────
🆕 New:       xxx
✅ Qualified:  xxx
🔍 Enriched:   xxx
📧 Emailed:    xxx
📞 Called:     xxx
💬 Replied:    xxx
⭐ Interested: xxx
🎯 Closed:     xxx — $0"""

    def _cmd_calls(self, cmd: TelegramCommand) -> str:
        return """📞 Voice Calls Today
─────────────────
Attempted:   0
Connected:   0
Interested:  0
Closed:      0 — $0
─────────────────
Daily limit: 50"""

    def _cmd_approve(self, cmd: TelegramCommand) -> str:
        task_id = cmd.args[0] if cmd.args else "unknown"
        return f"✅ Approved: {task_id}"

    def _cmd_reject(self, cmd: TelegramCommand) -> str:
        task_id = cmd.args[0] if cmd.args else "unknown"
        return f"❌ Rejected: {task_id}"

    def _cmd_pause(self, cmd: TelegramCommand) -> str:
        agent = cmd.args[0] if cmd.args else "unknown"
        return f"⏸️ Paused: {agent}"

    def _cmd_resume(self, cmd: TelegramCommand) -> str:
        agent = cmd.args[0] if cmd.args else "unknown"
        return f"▶️ Resumed: {agent}"

    def _cmd_call(self, cmd: TelegramCommand) -> str:
        lead_id = cmd.args[0] if cmd.args else "unknown"
        return f"📞 Manual call triggered for lead: {lead_id}"

    def _cmd_report(self, cmd: TelegramCommand) -> str:
        return "📈 Weekly report triggered. Memory Manager analyzing..."

    def _cmd_help(self) -> str:
        lines = ["🤖 ALZEN Control Bot — Commands:", ""]
        for cmd, desc in self.COMMANDS.items():
            lines.append(f"/{cmd} — {desc}")
        return "\n".join(lines)

    def send_alert(self, message: str, alert_type: str = "info"):
        """Send an alert to the operator via Telegram."""
        prefix = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "closed": "🎯"}
        emoji = prefix.get(alert_type, "ℹ️")
        full_msg = f"{emoji} {message}"
        # Production: POST to Telegram API
        # requests.post(f"{self.base_url}/sendMessage", json={"chat_id": self.chat_id, "text": full_msg})
        print(f"[telegram] {full_msg}")

    def send_closed_alert(self, company: str, deal_value: float):
        """Send CLOSED deal alert."""
        self.send_alert(
            f"🎯 CLOSED: {company} — ${deal_value:,.2f} ARR",
            alert_type="closed"
        )

    def send_approval_request(self, task_id: str, task_type: str, details: str):
        """Send approval request with inline keyboard."""
        msg = f"""🔔 Approval Required: {task_type}
Task: {task_id}
Details: {details}

Approve: /approve {task_id}
Reject: /reject {task_id}"""
        self.send_alert(msg, alert_type="warning")
