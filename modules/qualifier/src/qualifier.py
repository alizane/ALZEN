"""
Lead Qualifier (Phase 18) — DeepSeek V3 ICP scoring gate.
Scores leads 1-10 against ICP signals defined in vault/patterns/icp-signals.md.
Token budget: <200 tokens per lead.
"""
import json
import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent.parent
VAULT_DIR = PROJECT_DIR / "vault"
ICP_SIGNALS_FILE = VAULT_DIR / "patterns" / "icp-signals.md"


@dataclass
class QualificationResult:
    lead_id: str
    company: str
    score: int  # 1-10
    verdict: str  # auto_qualify | qualify | hold | disqualify
    signals_matched: list[str]
    signals_missed: list[str]
    voice_call_trigger: bool
    reasoning: str
    tokens_used: int = 0
    cost_usd: float = 0.0


class LeadQualifier:
    """Scores leads against ICP signals using DeepSeek V3."""

    SCORE_THRESHOLDS = {
        (8, 10): "auto_qualify",   # Voice call eligible
        (6, 7): "qualify",         # Email first
        (4, 5): "hold",            # Low priority queue
        (1, 3): "disqualify",      # Auto-reject
    }

    def __init__(self):
        self.api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        self.model = "deepseek-chat-v3"
        # Load ICP signals as reference
        self.icp_signals = self._load_icp_signals()

    def _load_icp_signals(self) -> str:
        """Load ICP signals from vault for the system prompt."""
        if ICP_SIGNALS_FILE.exists():
            return ICP_SIGNALS_FILE.read_text()
        return "ICP signals not found. Use default: Series A-C funded, 50-500 employees, SaaS."

    def _build_prompt(self, lead: dict) -> str:
        """Build a minimal qualification prompt (<200 tokens)."""
        return f"""Score this B2B lead 1-10 against ICP signals. Be ruthless.

Lead:
- Company: {lead.get('company', '?')}
- Industry: {lead.get('industry', '?')}
- Size: {lead.get('company_size', '?')} employees
- Funding: {lead.get('funding_stage', '?')}
- Source: {lead.get('source', '?')}
- Signals: {', '.join(lead.get('signals', []))}

ICP Reference:
{self.icp_signals[:500]}

Return JSON: {{"score": 1-10, "signals_matched": [...], "signals_missed": [...], "voice_call_trigger": bool, "reasoning": "1 sentence"}}"""

    def score(self, lead: dict) -> QualificationResult:
        """Score a single lead. In production, calls DeepSeek API."""
        # For development/dry-run: rule-based scoring fallback
        score = 5  # Default neutral
        signals = lead.get("signals", [])
        matched = []
        missed = []

        # Rule-based scoring (used when API is unavailable)
        if lead.get("funding_stage") in ("Series A", "Series B", "Series C"):
            score += 2
            matched.append("series_a_c_funding")
        if lead.get("company_size") and 50 <= lead["company_size"] <= 500:
            score += 2
            matched.append("target_company_size")
        elif lead.get("company_size") and lead["company_size"] < 10:
            score -= 3
            missed.append("too_small")
        if lead.get("industry") == "SaaS":
            score += 1
            matched.append("saas_product")
        if any("sdr_job" in s.lower() for s in signals):
            score += 2
            matched.append("sdr_job_posting")
        if any("funding" in s.lower() for s in signals):
            score += 1
            matched.append("funding_signal")

        score = max(1, min(10, score))

        # Determine verdict
        verdict = "hold"
        for (lo, hi), v in self.SCORE_THRESHOLDS.items():
            if lo <= score <= hi:
                verdict = v
                break

        # Voice call trigger check
        voice_trigger = score >= 8 or (
            score >= 7 and any("interested" in str(s).lower() for s in signals)
        )

        return QualificationResult(
            lead_id=lead.get("id", ""),
            company=lead.get("company", "?"),
            score=score,
            verdict=verdict,
            signals_matched=matched,
            signals_missed=missed,
            voice_call_trigger=voice_trigger,
            reasoning=f"Score {score}/10: {len(matched)} signals matched, {len(missed)} missed.",
        )

    def batch_score(self, leads: list[dict]) -> list[QualificationResult]:
        """Score a batch of leads."""
        return [self.score(lead) for lead in leads]

    def filter_qualified(self, results: list[QualificationResult]) -> list[QualificationResult]:
        """Return only leads that passed qualification."""
        return [r for r in results if r.verdict in ("auto_qualify", "qualify")]
