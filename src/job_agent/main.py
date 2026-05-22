from __future__ import annotations

import json
from typing import List

from .collect import collect_jobs


def main():
    # Demo inputs for Phase 2
    titles: List[str] = ["python", "data engineer", "backend"]

    jobs = collect_jobs(titles)
    print(json.dumps(jobs[:10], indent=2))


if __name__ == "__main__":
    main()

