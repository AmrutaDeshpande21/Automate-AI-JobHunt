from __future__ import annotations

from typing import Dict, Iterable, List

from .base import BaseScraper


class NaukriScraper(BaseScraper):
    """Placeholder for Phase 2.

    Naukri pages are often heavily dynamic and may require selectors and
    potentially browser automation. We'll implement once we confirm
    the target job-title query strategy.
    """

    def scrape(self, titles: Iterable[str]) -> List[Dict]:
        return []

