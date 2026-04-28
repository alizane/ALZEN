"""
Deal Export (Phase 33) — HubSpot-compatible JSON export.
Exports closed deals as JSON for manual CRM upload.
"""
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent.parent
EXPORT_DIR = PROJECT_DIR / "exports"


@dataclass
class ClosedDeal:
    lead_id: str
    company: str
    contact_name: str
    email: str
    deal_value_usd: float
    deal_stage: str = "closed_won"
    close_date: str = ""
    deal_source: str = "ALZEN_outbound"
    products: str = "AI Sales Automation"
    notes: str = ""


class DealExporter:
    """Exports closed deals to HubSpot-compatible JSON."""

    def export_deal(self, lead: dict, voice_call: dict) -> dict:
        """Format a single deal for HubSpot JSON import."""
        return {
            "properties": [
                {"property": "dealname", "value": f"{lead.get('company', 'Unknown')} — ALZEN"},
                {"property": "amount", "value": str(voice_call.get("deal_value_usd", 0))},
                {"property": "dealstage", "value": "closedwon"},
                {"property": "closedate", "value": datetime.now(timezone.utc).strftime("%Y-%m-%d")},
                {"property": "dealtype", "value": "new_business"},
                {"property": "pipeline", "value": "ALZEN Outbound"},
                {"property": "hubspot_owner_id", "value": ""},
                {"property": "contact_email", "value": lead.get("email", "")},
                {"property": "company_name", "value": lead.get("company", "")},
                {"property": "description", "value": f"Closed via ALZEN autonomous pipeline. "
                    f"Source: {lead.get('source', 'unknown')}. "
                    f"ICP Score: {lead.get('qual_score', '?')}/10."}
            ]
        }

    def export_batch(self, deals: list[dict]) -> Path:
        """Export multiple deals as HubSpot-compatible JSON."""
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out_file = EXPORT_DIR / f"hubspot-deals-{timestamp}.json"

        with open(out_file, "w") as f:
            json.dump({"deals": deals}, f, indent=2)

        return out_file

    def export_csv(self, deals: list[dict]) -> Path:
        """Export deals as CSV for manual spreadsheet import."""
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out_file = EXPORT_DIR / f"deals-{timestamp}.csv"

        with open(out_file, "w") as f:
            f.write("company,contact,email,deal_value,close_date,source,icp_score\n")
            for d in deals:
                lead = d.get("lead", {})
                vc = d.get("voice_call", {})
                f.write(f"{lead.get('company','')},{lead.get('contact_name','')},{lead.get('email','')},"
                        f"{vc.get('deal_value_usd',0)},{d.get('close_date','')},{lead.get('source','')},"
                        f"{lead.get('qual_score','')}\n")
        return out_file
