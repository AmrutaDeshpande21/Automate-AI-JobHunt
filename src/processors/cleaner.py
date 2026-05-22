"""
Data Cleaner Module

This module cleans and normalizes job data for consistency.
"""

from typing import Dict, List
import re
from datetime import datetime

class DataCleaner:
    """Class to clean and normalize job data"""
    
    def __init__(self):
        """Initialize the cleaner"""
        self.common_location_mappings = {
            'delhi': 'Delhi',
            'mumbai': 'Mumbai',
            'bangalore': 'Bangalore',
            'hyderabad': 'Hyderabad',
            'pune': 'Pune',
            'remote': 'Remote',
            'work from home': 'Remote',
            'wfh': 'Remote',
        }
    
    def clean_job(self, job: Dict) -> Dict:
        """
        Clean a single job record.
        
        Args:
            job (Dict): Job data to clean
            
        Returns:
            Dict: Cleaned job data
        """
        cleaned_job = job.copy()
        
        # Clean string fields
        for field in ['title', 'company', 'location', 'description']:
            if field in cleaned_job:
                cleaned_job[field] = self._clean_text(cleaned_job[field])
        
        # Normalize location
        if 'location' in cleaned_job:
            cleaned_job['location'] = self._normalize_location(cleaned_job['location'])
        
        # Clean URL
        if 'link' in cleaned_job:
            cleaned_job['link'] = self._clean_url(cleaned_job['link'])
        
        # Standardize source
        if 'source' in cleaned_job:
            cleaned_job['source'] = self._standardize_source(cleaned_job['source'])
        
        # Handle missing descriptions
        if 'description' not in cleaned_job or not cleaned_job['description']:
            cleaned_job['description'] = 'Not provided'
        
        return cleaned_job
    
    def clean_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Clean multiple job records.
        
        Args:
            jobs (List[Dict]): List of job data to clean
            
        Returns:
            List[Dict]: List of cleaned job data
        """
        return [self.clean_job(job) for job in jobs]
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text (str): Text to clean
            
        Returns:
            str: Cleaned text
        """
        if not isinstance(text, str):
            return str(text) if text else ''
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove HTML tags if any
        text = re.sub(r'<[^>]+>', '', text)
        
        # Trim to reasonable length
        if len(text) > 5000:
            text = text[:5000] + '...'
        
        return text.strip()
    
    def _normalize_location(self, location: str) -> str:
        """
        Normalize location names.
        
        Args:
            location (str): Location to normalize
            
        Returns:
            str: Normalized location
        """
        location = self._clean_text(location)
        location_lower = location.lower()
        
        # Check common mappings
        for key, value in self.common_location_mappings.items():
            if key in location_lower:
                return value
        
        # Default: return cleaned location with proper capitalization
        return location.title() if location else 'Unknown'
    
    @staticmethod
    def _clean_url(url: str) -> str:
        """
        Clean and normalize URL.
        
        Args:
            url (str): URL to clean
            
        Returns:
            str: Cleaned URL
        """
        url = str(url).strip()
        
        # Add http if not present
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url if url != 'https://' else ''
    
    @staticmethod
    def _standardize_source(source: str) -> str:
        """
        Standardize source platform name.
        
        Args:
            source (str): Source name to standardize
            
        Returns:
            str: Standardized source name
        """
        source_mapping = {
            'naukri': 'Naukri',
            'remoteok': 'RemoteOK',
            'wellfound': 'Wellfound',
        }
        
        source_lower = str(source).lower().strip()
        return source_mapping.get(source_lower, source.strip())
