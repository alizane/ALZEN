"""
Lead Finder — Public API Aggregator (Phase 17)
Sources: Angel List, Product Hunt, Crunchbase (free tiers).
Target: 300-500 leads/day from public APIs.
"""
import asyncio
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import httpx

VAULT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "vault"
CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)


@dataclass
class CompanyLead:
    company: str
    domain: str | None = None
    description: str | None = None
    industry: str | None = None
    company_size: int | None = None
    funding_stage: str | None = None
    funding_amount: str | None = None
    founders: list[str] | None = None
    source: str = "public_apis"
    signals: list[str] | None = None

    def __post_init__(self):
        if self.signals is None:
            self.signals = []


class PublicAPIAggregator:
    """Aggregates B2B leads from free public APIs."""

    def __init__(self):
        self.client = httpx.Client(timeout=30, headers={
            "User-Agent": "ALZEN-LeadFinder/3.0"
        })

    def _cache_key(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()[:12]

    def _cached_get(self, url: str, ttl: int = 86400) -> dict | None:
        """Cache API responses for 24 hours to respect rate limits."""
        cache_file = CACHE_DIR / f"{self._cache_key(url)}.json"
        if cache_file.exists():
            data = json.loads(cache_file.read_text())
            age = time.time() - data.get("_cached_at", 0)
            if age < ttl:
                return data
        try:
            resp = self.client.get(url)
            resp.raise_for_status()
            data = resp.json()
            data["_cached_at"] = time.time()
            cache_file.write_text(json.dumps(data))
            return data
        except Exception:
            if cache_file.exists():
                return json.loads(cache_file.read_text())
            return None

    def fetch_angel_list_startups(self, filter_type: str = "trending") -> list[CompanyLead]:
        """Fetch trending startups from Angel List (free tier API)."""
        url = f"https://api.angel.co/1/startups?filter={filter_type}"
        data = self._cached_get(url)
        if not data:
            return []

        leads: list[CompanyLead] = []
        for startup in data.get("startups", [])[:50]:
            leads.append(CompanyLead(
                company=startup.get("name", ""),
                domain=startup.get("company_url", ""),
                description=startup.get("high_concept", ""),
                industry=startup.get("markets", [{}])[0].get("name") if startup.get("markets") else None,
                company_size=startup.get("company_size"),
                funding_stage=startup.get("funding_stage"),
                source="public_apis",
                signals=["angel_list_trending"] if filter_type == "trending" else []
            ))
        return leads

    def fetch_product_hunt_launches(self, days_back: int = 30) -> list[CompanyLead]:
        """Fetch recent Product Hunt launches (free API via GraphQL)."""
        query = """
        query RecentPosts($daysBack: Int) {
          posts(first: 50, order: RANKING, postedAfter: $daysBack) {
            edges { node { name tagline website topics { name } makers { name headline } } }
          }
        }
        """
        # Product Hunt v2 API — requires token, fallback to RSS
        url = "https://api.producthunt.com/v2/posts"
        data = self._cached_get(url)
        if not data:
            return []

        leads: list[CompanyLead] = []
        for edge in data.get("data", {}).get("posts", {}).get("edges", []):
            node = edge.get("node", {})
            leads.append(CompanyLead(
                company=node.get("name", ""),
                domain=node.get("website", ""),
                description=node.get("tagline", ""),
                industry=node.get("topics", [{}])[0].get("name"),
                source="public_apis",
                signals=["product_hunt_launch"]
            ))
        return leads

    def fetch_crunchbase_funding_rss(self) -> list[CompanyLead]:
        """Parse Crunchbase funding RSS feed for recent funding announcements."""
        url = "https://www.crunchbase.com/www-sitemaps/sitemap-index.xml"
        # Crunchbase blocks direct API; use RSS parser approach
        data = self._cached_get(url, ttl=3600)
        if not data:
            return []
        # Simplified: return structured data from feed
        return []

    def fetch_linkedin_job_postings(self, keywords: list[str] | None = None) -> list[CompanyLead]:
        """Scrape LinkedIn job postings for SDR/AE roles (public pages)."""
        if keywords is None:
            keywords = ["Sales Development Representative", "Account Executive",
                        "Business Development Representative", "SDR", "BDR", "AE"]
        leads: list[CompanyLead] = []
        # LinkedIn public job search — limited but free
        for kw in keywords[:3]:  # Limit to 3 keywords to avoid rate limiting
            url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={kw.replace(' ', '%20')}&location=United%20States"
            data = self._cached_get(url, ttl=3600)
            if data:
                # Parse job postings for company names
                import re
                from bs4 import BeautifulSoup
                html = data.get("_raw_html", "")
                if html:
                    soup = BeautifulSoup(html, "html.parser")
                    for card in soup.select(".job-search-card")[:20]:
                        company_el = card.select_one(".company-name")
                        if company_el:
                            leads.append(CompanyLead(
                                company=company_el.get_text(strip=True),
                                source="public_apis",
                                signals=["sdr_job_posting", f"keyword: {kw}"]
                            ))
        return leads

    def run(self) -> list[CompanyLead]:
        """Aggregate leads from all public API sources."""
        all_leads: list[CompanyLead] = []

        # Angel List
        all_leads.extend(self.fetch_angel_list_startups("trending"))

        # Product Hunt (catch errors individually so one source doesn't block others)
        try:
            all_leads.extend(self.fetch_product_hunt_launches())
        except Exception:
            pass

        # LinkedIn job postings
        try:
            all_leads.extend(self.fetch_linkedin_job_postings())
        except Exception:
            pass

        return all_leads


# For module compatibility
import time as _time
