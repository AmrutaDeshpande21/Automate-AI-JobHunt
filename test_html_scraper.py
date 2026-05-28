"""
HTML Scraper Browser Test Script
This script tests the Naukri HTML scraping mechanism.
It opens the corresponding search page in the user's default web browser
and performs a scrape to retrieve matching jobs.
"""

import argparse
import sys
import webbrowser
import time
from src.agent import JobAgent
from src.scrapers import NaukriScraper, NaukriSeleniumScraper
from src.processors.cleaner import DataCleaner

def main():
    parser = argparse.ArgumentParser(
        description="Test the Naukri HTML Scraper and open the search page in the browser."
    )
    parser.add_argument(
        '--job-title',
        type=str,
        default="Frontend Developer",
        help="Job title to search for (default: 'Frontend Developer')"
    )
    parser.add_argument(
        '--location',
        type=str,
        default="Bangalore",
        help="Location to search in (default: 'Bangalore')"
    )
    parser.add_argument(
        '--use-selenium',
        action='store_true',
        help="Use Selenium scraper instead of requests-based scraper"
    )
    parser.add_argument(
        '--non-headless',
        action='store_true',
        help="Run Selenium in non-headless mode (opens browser window during scraping)"
    )

    args = parser.parse_args()

    # Clean and normalize job title and location
    cleaner = DataCleaner()
    normalized_loc = cleaner._normalize_location(args.location)
    
    print("\n" + "="*80)
    print("HTML SCRAPER BROWSER TEST")
    print("="*80)
    print(f"Target Job Title: {args.job_title}")
    print(f"Target Location:  {args.location} (Normalized: {normalized_loc})")
    print("="*80 + "\n")

    # Construct the Naukri search URL
    search_title_url = args.job_title.lower().replace(' ', '-')
    search_loc_url = normalized_loc.lower().replace(' ', '-')
    
    # Base URL for Naukri
    base_url = "https://www.naukri.com"
    if search_loc_url:
        search_url = f"{base_url}/{search_title_url}-jobs-in-{search_loc_url}-1"
    else:
        search_url = f"{base_url}/{search_title_url}-jobs-1"

    print(f"[INFO] Opening search page in default web browser...")
    print(f"[URL]  {search_url}\n")
    
    # Open browser
    try:
        webbrowser.open(search_url)
        print("[SUCCESS] Browser opened successfully!\n")
    except Exception as e:
        print(f"[WARNING] Failed to open browser automatically: {e}\n")

    print("="*80)
    print("RUNNING SCRAPING TEST")
    print("="*80)

    if args.use_selenium or args.non_headless:
        print(f"[INFO] Initializing Naukri Selenium Scraper (Headless: {not args.non_headless})...")
        scraper = NaukriSeleniumScraper(headless=not args.non_headless)
    else:
        print("[INFO] Initializing Naukri Requests-based HTML Scraper...")
        scraper = NaukriScraper()

    print(f"[INFO] Searching jobs for '{args.job_title}' in '{normalized_loc}'...")
    jobs = scraper.search_jobs(job_title=args.job_title, location=normalized_loc, pages=1)

    print(f"\n[INFO] Scraper returned {len(jobs)} raw jobs.")

    if jobs:
        # Process jobs to verify Phase 3 logic
        print("\n[INFO] Processing scraped jobs through Phase 3 cleaner and validator...")
        agent = JobAgent()
        agent.all_jobs = jobs
        processed_df, stats = agent.process_jobs(clean=True, validate=True, remove_duplicates=True)
        
        if not processed_df.empty:
            print("\n--- SAMPLE SCRAPED & PROCESSED JOBS ---")
            print(processed_df[['title', 'company', 'location', 'source']].head(10))
            
            # Save test output
            test_csv = "test_naukri_jobs.csv"
            filepath = agent.save_to_csv(filename=test_csv, append=False)
            print(f"\n[SUCCESS] Scraped jobs processed and saved to {filepath}")
        else:
            print("[INFO] Processing filtered out all scraped jobs (possibly due to title/location mismatches).")
    else:
        print("[INFO] Scraper returned 0 results. (Note: requests-based scraper might be blocked, try --use-selenium)")

    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
