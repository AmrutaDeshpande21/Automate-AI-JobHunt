"""
Wellfound Job Scraper Module

This module contains functions to scrape job listings from Wellfound.com
using Firecrawl for intelligent web scraping.
"""

import requests
import pandas as pd
from datetime import datetime
import json

class WellfoundScraper:
    """Scraper class for Wellfound job listings using Firecrawl"""
    
    def __init__(self, firecrawl_api_key=None):
        """
        Initialize the Wellfound scraper with Firecrawl.
        
        Args:
            firecrawl_api_key (str): API key for Firecrawl (from environment or parameter)
        """
        self.firecrawl_api_key = firecrawl_api_key or self._get_api_key()
        self.firecrawl_api_url = "https://api.firecrawl.dev/v1"
        self.base_url = "https://wellfound.com"
        self.jobs_data = []
    
    def _get_api_key(self):
        """
        Get Firecrawl API key from environment variables.
        
        Returns:
            str: API key or None if not found
        """
        import os
        return os.getenv('FIRECRAWL_API_KEY')
    
    def search_jobs(self, job_title, location=None):
        """
        Search for jobs on Wellfound using Firecrawl.
        
        Args:
            job_title (str): The job title to search for
            location (str): The location to search in (optional)
            
        Returns:
            list: List of job dictionaries
        """
        if not self.firecrawl_api_key:
            print("Warning: Firecrawl API key not set. Please set FIRECRAWL_API_KEY environment variable.")
            return []
        
        try:
            # Build search URL
            search_url = f"{self.base_url}/jobs"
            params = {'q': job_title}
            if location:
                params['l'] = location
            
            # Construct full URL with parameters
            search_url_with_params = search_url + '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
            
            print(f"Scraping Wellfound jobs for '{job_title}' using Firecrawl...")
            
            # Use Firecrawl to scrape the page
            jobs = self._scrape_with_firecrawl(search_url_with_params)
            
            self.jobs_data.extend(jobs)
            return jobs
        
        except Exception as e:
            print(f"Error during Wellfound scraping: {e}")
            return []
    
    def _scrape_with_firecrawl(self, url):
        """
        Scrape a URL using Firecrawl API.
        
        Args:
            url (str): The URL to scrape
            
        Returns:
            list: List of extracted job data
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.firecrawl_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'url': url,
                'formats': ['markdown', 'html'],
                'onlyMainContent': True
            }
            
            response = requests.post(
                f"{self.firecrawl_api_url}/scrape",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            
            data = response.json()
            
            # Extract jobs from the scraped content
            jobs = self._parse_wellfound_jobs(data)
            
            return jobs
        
        except requests.RequestException as e:
            print(f"Error with Firecrawl API request: {e}")
            return []
        except Exception as e:
            print(f"Error processing Firecrawl response: {e}")
            return []
    
    def _parse_wellfound_jobs(self, scraped_data):
        """
        Parse job listings from Firecrawl scraped data.
        
        Args:
            scraped_data (dict): Data returned from Firecrawl
            
        Returns:
            list: List of parsed job dictionaries
        """
        jobs = []
        
        try:
            # The structure depends on Firecrawl's response format
            # This is a basic template that should be adjusted based on actual response
            
            content = scraped_data.get('markdown', scraped_data.get('html', ''))
            
            # Parse the content to extract job listings
            # This is a simplified version - actual implementation depends on page structure
            job_info = {
                'title': 'Job Title',
                'company': 'Company Name',
                'location': 'Location',
                'description': 'Job Description',
                'link': scraped_data.get('url', 'N/A'),
                'source': 'Wellfound',
                'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Note: Actual parsing logic should be implemented based on Wellfound's page structure
            
            return jobs
        
        except Exception as e:
            print(f"Error parsing Wellfound jobs: {e}")
            return []
