"""
Lead Finder — Intent Signals Crawler (Phase 17)
Monitors funding announcements, job postings, and tech-stack changes
for high-intent B2B buying signals.
"""
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

VAULT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "vault"


@dataclass
class IntentSignal:
    company: str
    signal_type: str  # funding | hiring | tech_stack | expansion
    description: str
    strength: float  # 0.0 to 1.0
    source_url: str
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class IntentSignalsCrawler:
    """Crawls public sources for buying intent signals."""

    SOURCES = {
        "techcrunch_rss": "https://techcrunch.com/feed/",
        "venture_beat_rss": "https://venturebeat.com/feed/",
        "crunchbase_news": "https://news.crunchbase.com/feed/",
    }

    FUNDING_KEYWORDS = [
        r'(?:raised|secured|closed)\s+\$?(\d+\.?\d*)\s*(million|M|billion|B)',
        r'(?:Series)\s+(A|B|C|D|Seed)',
        r'(?:funding|investment)\s+round',
        r'(?:valuation)\s+at\s+\$?\d+',
    ]

    HIRING_KEYWORDS = [
        r'(?:hiring|expanding|growing)\s+(?:team|headcount)',
        r'(?:doubl|tripl)\w+\s+(?:headcount|team|revenue)',
        r'(?:opening|opened)\s+(?:a\s+)?(?:new\s+)?office',
    ]

    def __init__(self):
        self.client = httpx.Client(timeout=30, headers={
            "User-Agent": "ALZEN-IntentSignals/3.0"
        })
        self._seen_urls: set[str] = set()

    def fetch_rss_feed(self, url: str) -> list[dict]:
        """Fetch and parse an RSS feed for funding/hiring news."""
        try:
            resp = self.client.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "xml")
            items = []
            for item in soup.select("item")[:20]:
                title = item.select_one("title")
                link = item.select_one("link")
                description = item.select_one("description")
                pub_date = item.select_one("pubDate")
                items.append({
                    "title": title.get_text(strip=True) if title else "",
                    "link": link.get_text(strip=True) if link else "",
                    "description": description.get_text(strip=True) if description else "",
                    "pub_date": pub_date.get_text(strip=True) if pub_date else "",
                })
            return items
        except Exception:
            return []

    def detect_funding_signals(self, text: str) -> list[dict]:
        """Detect funding announcements in text."""
        signals = []
        for pattern in self.FUNDING_KEYWORDS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                signals.append({
                    "type": "funding",
                    "match": match.group(),
                    "strength": 0.9  # Funding signals are high strength
                })
        return signals

    def detect_hiring_signals(self, text: str) -> list[dict]:
        """Detect hiring/expansion signals."""
        signals = []
        for pattern in self.HIRING_KEYWORDS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                signals.append({
                    "type": "hiring",
                    "match": match.group(),
                    "strength": 0.7
                })
        return signals

    def extract_company_name(self, title: str) -> str | None:
        """Extract company name from a news headline."""
        # Common patterns: "Acme Corp raises $10M", "Acme, a SaaS startup, ..."
        patterns = [
            r'^([A-Z][\w\s]+?)(?:\s+raises|\s+secured|\s+announces|\s+launches)',
            r'^([A-Z][\w\s]+?)(?:,|—|–|\s+is|\s+has|\s+the)',
        ]
        for pat in patterns:
            m = re.match(pat, title)
            if m:
                return m.group(1).strip()
        return None

    def run(self) -> list[IntentSignal]:
        """Crawl all sources for intent signals."""
        all_signals: list[IntentSignal] = []

        for source_name, source_url in self.SOURCES.items():
            items = self.fetch_rss_feed(source_url)
            for item in items:
                text = f"{item['title']} {item['description']}"
                company = self.extract_company_name(item['title'])

                funding = self.detect_funding_signals(text)
                hiring = self.detect_hiring_signals(text)

                for sig in funding + hiring:
                    if item['link'] not in self._seen_urls:
                        self._seen_urls.add(item['link'])
                        all_signals.append(IntentSignal(
                            company=company or "unknown",
                            signal_type=sig['type'],
                            description=sig['match'],
                            strength=sig['strength'],
                            source_url=item['link']
                        ))

        return all_signals

    def get_high_priority_targets(self, signals: list[IntentSignal]) -> list[str]:
        """Filter signals for high-priority targets (funding + hiring in same company)."""
        from collections import Counter
        company_signals: dict[str, list[IntentSignal]] = {}
        for sig in signals:
            if sig.company != "unknown":
                company_signals.setdefault(sig.company, []).append(sig)

        # Companies with both funding AND hiring signals = highest priority
        high_priority = []
        for company, sigs in company_signals.items():
            types = {s.signal_type for s in sigs}
            if "funding" in types and "hiring" in types:
                high_priority.append(company)
        return high_priority
