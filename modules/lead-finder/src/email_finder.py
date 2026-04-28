"""
Lead Finder — Email Pattern Matcher (Phase 17)
Discovers email addresses via pattern matching.
Accuracy: ~70% (vs 95% with paid tools like Hunter.io).
"""
import re
from dataclasses import dataclass
from pathlib import Path

VAULT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "vault"


@dataclass
class EmailMatch:
    email: str
    confidence: float  # 0.0 to 1.0
    pattern: str
    source: str = "email_matcher"


class EmailMatcher:
    """Discovers email addresses using common corporate patterns."""

    PATTERNS = [
        # (pattern_template, weight)
        ("{first}.{last}@{domain}", 0.85),
        ("{first}{last}@{domain}", 0.70),
        ("{f}.{last}@{domain}", 0.80),
        ("{first}.{l}@{domain}", 0.60),
        ("{first}_{last}@{domain}", 0.55),
        ("{first}@{domain}", 0.35),
        ("{last}@{domain}", 0.30),
        ("{first}{l}@{domain}", 0.50),
        ("{f}{last}@{domain}", 0.65),
    ]

    def __init__(self):
        self._verified_domains: dict[str, str] = {}  # domain → pattern

    def generate_candidates(self, first_name: str, last_name: str, domain: str) -> list[EmailMatch]:
        """Generate all candidate email addresses for a person."""
        first = first_name.lower().replace(" ", "").replace("-", "")
        last = last_name.lower().replace(" ", "").replace("-", "")
        f = first[0] if first else ""
        l = last[0] if last else ""

        candidates: list[EmailMatch] = []
        for template, weight in self.PATTERNS:
            email = template.format(first=first, last=last, f=f, l=l, domain=domain)
            candidates.append(EmailMatch(email=email, confidence=weight, pattern=template))

        # Boost confidence if we've verified this domain's pattern before
        known_pattern = self._verified_domains.get(domain)
        for c in candidates:
            if known_pattern and c.pattern == known_pattern:
                c.confidence = min(1.0, c.confidence + 0.10)

        return sorted(candidates, key=lambda x: x.confidence, reverse=True)

    def extract_from_webpage(self, html: str, domain: str) -> list[EmailMatch]:
        """Extract actual email addresses from webpage HTML."""
        pattern = re.compile(
            r'[a-zA-Z0-9._%+-]+@' + re.escape(domain),
            re.IGNORECASE
        )
        matches = list(set(pattern.findall(html)))
        return [EmailMatch(email=m, confidence=1.0, pattern="extracted", source="email_matcher")
                for m in matches]

    def verify_pattern(self, domain: str, confirmed_email: str) -> None:
        """Learn a domain's email pattern from a verified email."""
        local_part = confirmed_email.split("@")[0]
        # Try to reverse-engineer the pattern
        if "." in local_part:
            parts = local_part.split(".")
            if len(parts) == 2 and len(parts[0]) == 1:
                self._verified_domains[domain] = "{f}.{last}@{domain}"
            elif len(parts) == 2:
                self._verified_domains[domain] = "{first}.{last}@{domain}"
        elif "_" in local_part:
            self._verified_domains[domain] = "{first}_{last}@{domain}"
        elif len(local_part) <= 7 and local_part.isalpha():
            self._verified_domains[domain] = "{first}{l}@{domain}"

    def find_best_email(self, first_name: str, last_name: str,
                        domain: str, html_hints: str | None = None) -> EmailMatch | None:
        """Find the best email match for a person."""
        candidates = self.generate_candidates(first_name, last_name, domain)

        # If we have HTML from the company website, check for verified emails
        if html_hints:
            extracted = self.extract_from_webpage(html_hints, domain)
            extracted_addrs = {e.email for e in extracted}

            # Boost candidates that match extracted patterns
            for c in candidates:
                if c.email in extracted_addrs:
                    c.confidence = 1.0  # Verified match
                else:
                    # Check if the extracted emails follow a pattern
                    for ex in extracted:
                        self.verify_pattern(domain, ex.email)

        return candidates[0] if candidates and candidates[0].confidence >= 0.5 else None
