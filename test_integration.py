"""
Integration Test Script
Verifies that all three platforms (Naukri, RemoteOK, and Wellfound)
can be queried and parsed, and confirms that structured logging functions.
"""

import unittest
import os
import logging
from src.scrapers import NaukriSeleniumScraper, RemoteOKScraper, WellfoundScraper
from src.agent import JobAgent

class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        # Ensure log file path exists
        self.log_file = os.path.join("doc", "scraping.log")
        
    def test_remoteok_scraper_and_mapping(self):
        """Verify RemoteOK Scraper connects and correctly maps job position to title"""
        print("\n--- Testing RemoteOK Integration & Mapping ---")
        scraper = RemoteOKScraper()
        
        # Search for jobs
        jobs = scraper.search_jobs(job_title="Assistant")
        
        print(f"RemoteOK Scraper returned {len(jobs)} jobs.")
        
        if jobs:
            first_job = jobs[0]
            print(f"Sample RemoteOK job: {first_job}")
            
            # Check fields
            self.assertIn('title', first_job)
            self.assertNotEqual(first_job['title'], 'N/A') # Verifies position was mapped
            self.assertIn('company', first_job)
            self.assertIn('link', first_job)
            self.assertEqual(first_job['source'], 'RemoteOK')
            self.assertTrue(first_job['link'].startswith('http'))
        else:
            print("Warning: RemoteOK returned 0 jobs (could be due to API availability).")

    def test_naukri_scraper(self):
        """Verify Naukri Selenium Scraper loads and runs search without issues"""
        print("\n--- Testing Naukri Selenium Integration ---")
        scraper = NaukriSeleniumScraper(headless=True)
        
        # Run a small search (limit to 1 page)
        jobs = scraper.search_jobs(job_title="Software Engineer", location="Bangalore", pages=1)
        
        print(f"Naukri Scraper returned {len(jobs)} jobs.")
        if jobs:
            first_job = jobs[0]
            print(f"Sample Naukri job: {first_job['title']} at {first_job['company']}")
            self.assertIn('title', first_job)
            self.assertIn('company', first_job)
            self.assertIn('link', first_job)
            self.assertEqual(first_job['source'], 'Naukri')
        else:
            print("Naukri Scraper returned 0 jobs.")

    def test_wellfound_scraper_fallback(self):
        """Verify Wellfound Scraper behaves gracefully when API key is missing or set"""
        print("\n--- Testing Wellfound Scraper Behavior ---")
        scraper = WellfoundScraper()
        
        if not scraper.firecrawl_api_key:
            print("Firecrawl API key not set. Verifying scraper exits gracefully.")
            jobs = scraper.search_jobs(job_title="React Developer")
            self.assertEqual(len(jobs), 0)
        else:
            print("Firecrawl API key is set. Running Wellfound search integration.")
            jobs = scraper.search_jobs(job_title="React Developer", location="Remote")
            print(f"Wellfound returned {len(jobs)} jobs.")

    def test_logging_system(self):
        """Verify that log outputs are successfully written to doc/scraping.log"""
        print("\n--- Testing Logging Outputs ---")
        from src.utils.logger import logger
        
        test_message = "INTEGRATION TEST AUDIT ENTRY"
        logger.info(test_message)
        
        self.assertTrue(os.path.exists(self.log_file))
        
        # Read log file and verify entry
        with open(self.log_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.assertIn(test_message, content)
        print("Logging integration verified successfully!")

if __name__ == "__main__":
    unittest.main()
