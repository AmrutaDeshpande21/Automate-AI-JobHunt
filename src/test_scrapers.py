"""
Test script for Job Scrapers
"""

from src.scrapers import NaukriScraper, RemoteOKScraper, WellfoundScraper
import os
from dotenv import load_dotenv

load_dotenv()

def test_remoteok():
    print("\n--- Testing RemoteOK Scraper ---")
    scraper = RemoteOKScraper()
    jobs = scraper.search_jobs(job_title="Python")
    print(f"RemoteOK: Found {len(jobs)} jobs")
    if jobs:
        print(f"First job: {jobs[0]['title']} at {jobs[0]['company']}")
    return len(jobs) > 0

def test_naukri():
    print("\n--- Testing Naukri Scraper ---")
    scraper = NaukriScraper()
    # Note: Naukri might block standard requests, so we expect some warnings if blocked
    jobs = scraper.search_jobs(job_title="Software Engineer", location="Bangalore")
    print(f"Naukri: Found {len(jobs)} jobs")
    if jobs:
        print(f"First job: {jobs[0]['title']} at {jobs[0]['company']}")
    return True # Success is getting the result, even if 0 due to blocks

def test_wellfound():
    print("\n--- Testing Wellfound Scraper ---")
    # Wellfound requires FIRECRAWL_API_KEY
    api_key = os.getenv('FIRECRAWL_API_KEY')
    if not api_key:
        print("Skipping Wellfound test: FIRECRAWL_API_KEY not found in environment")
        return True
    
    scraper = WellfoundScraper(firecrawl_api_key=api_key)
    jobs = scraper.search_jobs(job_title="Full Stack Developer")
    print(f"Wellfound: Found {len(jobs)} jobs")
    return True

if __name__ == "__main__":
    test_remoteok()
    test_naukri()
    test_wellfound()
