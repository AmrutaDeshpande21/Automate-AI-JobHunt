"""
Wellfound Job Scraper Module

This module contains the scraper for job listings from Wellfound.com
using Firecrawl for intelligent web scraping.
"""

import requests
from typing import List, Dict, Optional
import os
from .base import BaseScraper

class WellfoundScraper(BaseScraper):
    """Scraper class for Wellfound job listings using Firecrawl"""
    
    def __init__(self, firecrawl_api_key: Optional[str] = None):
        """
        Initialize the Wellfound scraper with Firecrawl.
        
        Args:
            firecrawl_api_key (str): API key for Firecrawl (from environment or parameter)
        """
        super().__init__(source_name="Wellfound")
        self.firecrawl_api_key = firecrawl_api_key or self._get_api_key()
        self.firecrawl_api_url = "https://api.firecrawl.dev/v1"
        self.base_url = "https://wellfound.com"
    
    def _get_api_key(self) -> Optional[str]:
        """
        Get Firecrawl API key from environment variables.
        
        Returns:
            str: API key or None if not found
        """
        return os.getenv('FIRECRAWL_API_KEY') or "fc-4703c6f3222a452fb5ef2303878aaaea"
    
    def search_jobs(self, job_title: str, location: Optional[str] = None) -> List[Dict]:
        """
        Search for jobs on Wellfound using Firecrawl.
        
        Args:
            job_title (str): The job title to search for
            location (str): The location to search in (optional)
            
        Returns:
            List[Dict]: List of job dictionaries
        """
        if not self.firecrawl_api_key:
            print("Warning: Firecrawl API key not set. Please set FIRECRAWL_API_KEY environment variable.")
            return []
        
        try:
            # Format title and location as URL slugs
            role_slug = job_title.lower().strip().replace(' ', '-')
            role_slug = ''.join(c for c in role_slug if c.isalnum() or c == '-')
            
            if location:
                loc_slug = location.lower().strip().replace(' ', '-')
                loc_slug = ''.join(c for c in loc_slug if c.isalnum() or c == '-')
                search_url_with_params = f"{self.base_url}/role/l/{role_slug}/{loc_slug}"
            else:
                search_url_with_params = f"{self.base_url}/role/{role_slug}"
            
            print(f"Scraping Wellfound jobs for '{job_title}' using Firecrawl...")
            
            # Use Firecrawl to scrape the page
            jobs = self._scrape_with_firecrawl(search_url_with_params)
            
            self.jobs_data.extend(jobs)
            print(f"Found {len(self.jobs_data)} jobs from Wellfound")
            return jobs
        
        except Exception as e:
            print(f"Error during Wellfound scraping: {e}")
            return []
    
    def _scrape_with_firecrawl(self, url: str) -> List[Dict]:
        """
        Scrape a URL using Firecrawl API.
        
        Args:
            url (str): The URL to scrape
            
        Returns:
            List[Dict]: List of extracted job data
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
    
    def _parse_wellfound_jobs(self, scraped_data: Dict) -> List[Dict]:
        """
        Parse job listings from Firecrawl scraped data.
        
        Args:
            scraped_data (Dict): Data returned from Firecrawl
            
        Returns:
            List[Dict]: List of parsed job dictionaries
        """
        jobs = []
        
        try:
            # Firecrawl v1 response structure: {'success': True, 'data': {...}}
            data = scraped_data.get('data', {})
            content = data.get('markdown', data.get('html', ''))
            
            if not content:
                print("No content found in Firecrawl response")
                return []
                
            import re
            
            # Split by company logo markdown card start
            company_blocks = re.split(r'\n(?=\[!\[)', content)
            for block in company_blocks:
                comp_match = re.search(r'\[\*\*(.*?)\*\*\]', block)
                if not comp_match:
                    continue
                company = comp_match.group(1).strip()
                
                # Extract job links
                job_matches = re.finditer(r'\[(.*?)\]\((https://wellfound\.com/jobs/\d+-[a-zA-Z0-9-]+)\)', block)
                
                # Locate location line
                location = 'Remote'
                loc_lines = [line.strip() for line in block.split('\n') if any(word in line.lower() for word in ['remote', 'india', 'bengaluru', 'bangalore', 'hybrid'])]
                if loc_lines:
                    filtered_locs = [l for l in loc_lines if not l.startswith('[') and not l.startswith('!') and not l.startswith('-')]
                    if filtered_locs:
                        location = filtered_locs[0].strip()
                    
                for match in job_matches:
                    title = match.group(1).strip()
                    link = match.group(2).strip()
                    desc = block[:200].strip()
                    
                    job_info = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'description': desc,
                        'link': link
                    }
                    if self._validate_job_data(job_info):
                        jobs.append(self._add_metadata(job_info))
                        
            return jobs
            
        except Exception as e:
            print(f"Error parsing Wellfound jobs: {e}")
            return []
