"""
Base Scraper Module

This module defines the abstract base class for all job scrapers.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional

class BaseScraper(ABC):
    """Abstract base class for job scrapers"""
    
    def __init__(self, source_name: str):
        """
        Initialize the base scraper.
        
        Args:
            source_name (str): Name of the job source (e.g., 'Naukri', 'RemoteOK')
        """
        self.source_name = source_name
        self.jobs_data = []
    
    @abstractmethod
    def search_jobs(self, job_title: str, **kwargs) -> List[Dict]:
        """
        Search for jobs.
        
        Args:
            job_title (str): The job title to search for
            **kwargs: Additional arguments specific to each scraper
            
        Returns:
            List[Dict]: List of job dictionaries
        """
        pass
    
    def _add_metadata(self, job_data: Dict) -> Dict:
        """
        Add common metadata to job data.
        
        Args:
            job_data (Dict): Job information dictionary
            
        Returns:
            Dict: Job data with metadata
        """
        job_data['source'] = self.source_name
        job_data['scraped_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return job_data
    
    def _validate_job_data(self, job_data: Dict) -> bool:
        """
        Validate if job data has required fields.
        
        Args:
            job_data (Dict): Job information dictionary
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['title', 'company', 'location', 'link']
        return all(field in job_data and job_data[field] for field in required_fields)
