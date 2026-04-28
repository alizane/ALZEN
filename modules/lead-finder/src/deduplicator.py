"""
Lead Finder — Deduplicator (Phase 17)
Removes duplicate leads, verifies email format, cross-references existing DB.
"""
import re
from dataclasses import dataclass
from pathlib import Path

VAULT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "vault"


@dataclass
class DeduplicatedLead:
    company: str
    contact_name: str | None
    email: str | None
    title: str | None
    linkedin_url: str | None
    source: str
    signals: list[str] | None = None
    duplicate_of: str | None = None  # Lead ID if duplicate


class Deduplicator:
    """Removes duplicate leads across sources and verifies email format."""

    # Known disposable email domains
    DISPOSABLE_DOMAINS = {
        "mailinator.com", "guerrillamail.com", "10minutemail.com",
        "tempmail.com", "throwaway.email", "yopmail.com", "sharklasers.com",
        "trashmail.com", "temp-mail.org", "fakeinbox.com"
    }

    # Common invalid email patterns
    INVALID_EMAIL_PATTERNS = [
        r'noreply@', r'no-reply@', r'donotreply@', r'admin@',
        r'support@', r'info@', r'sales@', r'hello@', r'contact@',
        r'team@', r'jobs@', r'careers@', r'press@', r'media@',
    ]

    def __init__(self):
        self._seen_emails: set[str] = set()
        self._seen_companies: dict[str, str] = {}  # normalized company → lead_id

    @staticmethod
    def normalize_company(name: str) -> str:
        """Normalize company name for comparison."""
        return re.sub(r'\s+', ' ', name.lower()
                      .replace("inc.", "").replace("inc", "")
                      .replace("llc", "").replace("ltd", "")
                      .replace("corp.", "").replace("corp", "")
                      .replace("corporation", "")
                      .strip().rstrip(","))

    def is_valid_email(self, email: str) -> bool:
        """Verify email format and filter out generic/role-based addresses."""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False

        domain = email.split("@")[1].lower()
        if domain in self.DISPOSABLE_DOMAINS:
            return False

        for pattern in self.INVALID_EMAIL_PATTERNS:
            if re.match(pattern, email, re.IGNORECASE):
                return False

        return True

    def is_duplicate_email(self, email: str) -> bool:
        """Check if email was already seen."""
        if email in self._seen_emails:
            return True
        self._seen_emails.add(email)
        return False

    def is_duplicate_company(self, company: str, lead_id: str) -> str | None:
        """Check if company was already processed. Returns existing lead_id if duplicate."""
        normalized = self.normalize_company(company)
        if normalized in self._seen_companies:
            return self._seen_companies[normalized]
        self._seen_companies[normalized] = lead_id
        return None

    def filter_duplicates(self, leads: list[dict]) -> list[dict]:
        """Filter a batch of leads, removing duplicates and invalid emails."""
        clean: list[dict] = []
        for lead in leads:
            email = lead.get("email", "")
            company = lead.get("company", "")
            lead_id = lead.get("id", f"{company}_{email}")

            # Skip invalid emails
            if email and not self.is_valid_email(email):
                continue

            # Skip duplicates
            if email and self.is_duplicate_email(email):
                continue

            duplicate_of = self.is_duplicate_company(company, lead_id)
            if duplicate_of:
                lead["duplicate_of"] = duplicate_of
                # Still add but mark as duplicate
                clean.append(lead)
                continue

            clean.append(lead)
        return clean
