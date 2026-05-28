"""
RemoteOK Job Scraper Module

This module contains the scraper for job listings from RemoteOK.com
using their Public API.
"""

import requests
from typing import List, Dict, Optional
from .base import BaseScraper
from ..utils.logger import logger

class RemoteOKScraper(BaseScraper):
    """Scraper class for RemoteOK job listings using their API"""
    
    def __init__(self, api_url: str = "https://remoteok.com/api"):
        """
        Initialize the RemoteOK scraper.
        
        Args:
            api_url (str): The base API URL for RemoteOK
        """
        super().__init__(source_name="RemoteOK")
        self.api_url = api_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def search_jobs(self, job_title: Optional[str] = None, job_type: str = 'all') -> List[Dict]:
        """
        Search for jobs on RemoteOK using their API.
        
        Args:
            job_title (str): The job title to filter by (optional)
            job_type (str): Type of job ('all', 'fulltime', 'freelance', 'parttime')
            
        Returns:
            List[Dict]: List of job dictionaries
        """
        try:
            url = f"{self.api_url}"
            
            logger.info("Fetching jobs from RemoteOK API...")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            jobs = response.json()
            
            # Filter jobs based on job_title if provided
            for job in jobs:
                # Skip the first dict if it's metadata
                if isinstance(job, dict) and job.get('id') == 'remote-ok':
                    continue
                
                # Check position field which represents the job title in RemoteOK API
                pos = job.get('position', '') if isinstance(job, dict) else ''
                if not pos:
                    continue
                    
                if job_title and job_title.lower() not in pos.lower():
                    continue
                
                job_data = self._extract_job_info(job)
                if job_data and self._validate_job_data(job_data):
                    job_data = self._add_metadata(job_data)
                    self.jobs_data.append(job_data)
            
            logger.info(f"Found {len(self.jobs_data)} matching jobs from RemoteOK")
            return self.jobs_data
        
        except requests.RequestException as e:
            logger.error(f"Error fetching from RemoteOK API: {e}")
            return []
        except Exception as e:
            logger.error(f"Error processing RemoteOK data: {e}")
            return []
    
    def _extract_job_info(self, job: Dict) -> Optional[Dict]:
        """
        Extract job information from RemoteOK API response.
        
        Args:
            job (Dict): Job data from the API
            
        Returns:
            Dict: Dictionary containing job information or None
        """
        try:
            job_info = {
                'title': job.get('position', 'N/A'),
                'company': job.get('company', 'N/A'),
                'location': job.get('location', 'Remote'),
                'description': job.get('description', 'N/A'),
                'link': job.get('url', 'N/A'),
                'job_type': job.get('job_type', 'N/A'),
                'salary': job.get('salary', 'N/A'),
            }
            
            return job_info
        
        except Exception as e:
            logger.error(f"Error extracting job info from RemoteOK: {e}")
            return None
