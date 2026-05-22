from __future__ import annotations

from typing import Dict, Iterable, List

from .config import DEFAULT_CONFIG, AppConfig
from .scrapers.base import BaseScraper
from .scrapers.naukri import NaukriScraper
from .scrapers.remoteok import RemoteOKScraper
from .scrapers.wellfound import WellfoundScraper


def collect_jobs(titles: Iterable[str], config: AppConfig = DEFAULT_CONFIG) -> List[Dict]:
    scrapers: List[BaseScraper] = [
        RemoteOKScraper(),
        NaukriScraper(),
        WellfoundScraper(),
    ]

    all_jobs: List[Dict] = []
    for scraper in scrapers:
        all_jobs.extend(scraper.scrape(titles))

    return all_jobs

