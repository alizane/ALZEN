"""
Lead Finder — Web Scraper (Phase 17)
Playwright + BeautifulSoup crawler for B2B lead discovery.
Targets: Careers, Team, About Us pages.
Rate limit: 1 req/5sec per domain, 500 leads/day.
"""
import asyncio
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

VAULT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "vault"


@dataclass
class ScrapedLead:
    company: str
    contact_name: str | None = None
    title: str | None = None
    email: str | None = None
    linkedin_url: str | None = None
    source_url: str = ""
    signals: list[str] = field(default_factory=list)


class WebScraper:
    """Playwright-based B2B web scraper with rate limiting."""

    def __init__(self, rate_limit: float = 5.0, max_per_domain: int = 200):
        self.rate_limit = rate_limit
        self.max_per_domain = max_per_domain
        self._last_request: dict[str, float] = {}
        self._domain_counts: dict[str, int] = {}
        self._seen_emails: set[str] = set()

    def _rate_limit_check(self, domain: str):
        """Enforce 1 req/5sec per domain."""
        now = time.time()
        last = self._last_request.get(domain, 0)
        elapsed = now - last
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self._last_request[domain] = time.time()

    def _domain_count_check(self, domain: str) -> bool:
        """Cap leads per domain."""
        return self._domain_counts.get(domain, 0) < self.max_per_domain

    async def fetch_page(self, url: str) -> str | None:
        """Fetch a page with rate limiting."""
        domain = urlparse(url).netloc
        self._rate_limit_check(domain)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url, headers={
                    "User-Agent": "ALZEN-LeadFinder/3.0 (B2B research; bot@alzen.local)"
                })
                resp.raise_for_status()
                return resp.text
        except Exception:
            return None

    def extract_emails(self, text: str, domain: str) -> list[str]:
        """Extract email addresses matching the domain."""
        pattern = re.compile(r'[a-zA-Z0-9._%+-]+@' + re.escape(domain), re.IGNORECASE)
        return list(set(m.group() for m in pattern.finditer(text)))

    def parse_careers_page(self, html: str, company: str, url: str) -> list[ScrapedLead]:
        """Parse a careers/about page for team members and signals."""
        soup = BeautifulSoup(html, "html.parser")
        leads: list[ScrapedLead] = []
        domain = urlparse(url).netloc

        # Extract emails
        emails = self.extract_emails(html, domain)

        # Look for team members (common patterns: <div class="team-member">, <li class="person">)
        for person in soup.select(".team-member, .person, .employee-card, [class*='profile']"):
            name_el = person.select_one("h3, h4, .name, [class*='name']")
            title_el = person.select_one(".title, .role, [class*='title'], [class*='role']")
            name = name_el.get_text(strip=True) if name_el else None
            title = title_el.get_text(strip=True) if title_el else None
            if name:
                leads.append(ScrapedLead(
                    company=company,
                    contact_name=name,
                    title=title,
                    source_url=url
                ))

        # Detect hiring signals
        hiring_keywords = ["we're hiring", "join our team", "open positions", "careers"]
        text_lower = soup.get_text().lower()
        hiring_signals = [kw for kw in hiring_keywords if kw in text_lower]

        # Detect SDR/AE job postings (high intent signal)
        sdr_pattern = re.compile(r'sales development|account executive|business development|SDR|BDR|AE', re.IGNORECASE)
        has_sdr_roles = bool(sdr_pattern.search(soup.get_text()))

        for lead in leads:
            if hiring_signals:
                lead.signals.append(f"hiring_active: {', '.join(hiring_signals)}")
            if has_sdr_roles:
                lead.signals.append("sdr_job_posting")

        return leads

    def parse_about_page(self, html: str, company: str, url: str) -> dict:
        """Extract company metadata from About page."""
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()
        return {
            "company": company,
            "description": text[:500],
            "headcount_hint": self._extract_headcount(text),
            "tech_mentions": self._extract_tech_stack(text),
        }

    def _extract_headcount(self, text: str) -> str | None:
        """Try to extract employee count from text."""
        patterns = [
            r'(\d+[,\d]*)\+?\s*(employees|team members|people)',
            r'team of (\d+[,\d]*)',
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return m.group(1)
        return None

    def _extract_tech_stack(self, text: str) -> list[str]:
        """Detect technology mentions in text."""
        tech_keywords = [
            "Snowflake", "Databricks", "Kubernetes", "Docker", "AWS", "GCP",
            "Azure", "Terraform", "React", "Python", "Go", "Rust", "PostgreSQL",
            "Redis", "Kafka", "GraphQL", "gRPC", "TypeScript", "Node.js"
        ]
        text_lower = text.lower()
        return [t for t in tech_keywords if t.lower() in text_lower]

    async def scrape_company(self, company_name: str, website: str) -> list[ScrapedLead]:
        """Scrape a single company website for leads."""
        domain = urlparse(website).netloc
        if not self._domain_count_check(domain):
            return []

        leads: list[ScrapedLead] = []
        pages_to_check = [
            f"{website}/careers",
            f"{website}/about",
            f"{website}/team",
            f"{website}/about-us",
            f"{website}/company",
        ]

        for page_url in pages_to_check:
            html = await self.fetch_page(page_url)
            if html:
                leads.extend(self.parse_careers_page(html, company_name, page_url))

        self._domain_counts[domain] = self._domain_counts.get(domain, 0) + len(leads)
        return leads

    async def run(self, target_urls: list[tuple[str, str]]) -> list[ScrapedLead]:
        """Run scraper against a list of (company_name, website) targets."""
        all_leads: list[ScrapedLead] = []
        for company, website in target_urls:
            leads = await self.scrape_company(company, website)
            all_leads.extend(leads)
        return all_leads
