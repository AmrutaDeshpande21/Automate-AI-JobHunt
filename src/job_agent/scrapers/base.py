from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Iterable, List


class BaseScraper(ABC):
    @abstractmethod
    def scrape(self, titles: Iterable[str]) -> List[Dict]:
        """Return a list of job dicts."""
        raise NotImplementedError

