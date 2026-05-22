from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    # Output location for collected job listings
    output_csv: str = "data/jobs.csv"


DEFAULT_CONFIG = AppConfig()

