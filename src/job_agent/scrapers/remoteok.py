from __future__ import annotations

from typing import Dict, Iterable, List

import requests

from .base import BaseScraper


class RemoteOKScraper(BaseScraper):
    """Minimal Phase-2 implementation for RemoteOK.

    Note: RemoteOK has a simple endpoint that returns job postings.
    This implementation keeps it robust and testable.
    """

    BASE_URL = "https://remoteok.com/api"

    def scrape(self, titles: Iterable[str]) -> List[Dict]:
        title_set = {t.strip().lower() for t in titles if t and t.strip()}

        # Example payload format:
        # GET https://remoteok.com/api
        resp = requests.get(self.BASE_URL, timeout=30)
        resp.raise_for_status()
        jobs = resp.json() or []

        results: List[Dict] = []
        for job in jobs:
            # RemoteOK job objects typically contain keys like: title, company, location, url, description
            job_title = (job.get("title") or "").lower()
            if title_set and not any(t in job_title for t in title_set):
                continue

            results.append(
                {
                    "title": job.get("title"),
                    "location": job.get("location"),
                    "company": job.get("company"),
                    "description": job.get("description"),
                    "application_link": job.get("url") or job.get("company_url"),
                    "source": "remoteok",
                }
            )

        return results

