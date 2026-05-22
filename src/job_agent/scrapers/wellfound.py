from __future__ import annotations

from typing import Dict, Iterable, List

from .base import BaseScraper


class WellfoundScraper(BaseScraper):
    """Placeholder for Phase 2.

    Intended to use Firecrawl for scraping. We'll implement once Firecrawl
    integration details (API key + endpoint) are available.
    """

    def scrape(self, titles: Iterable[str]) -> List[Dict]:
        return []

