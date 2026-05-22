"""
Data Validator Module

This module validates job data for completeness and correctness.
"""

from typing import Dict, List, Tuple
import re

class DataValidator:
    """Class to validate job data"""
    
    def __init__(self):
        """Initialize the validator"""
        self.required_fields = ['title', 'company', 'location', 'link']
        self.optional_fields = ['description', 'source', 'scraped_date', 'job_type', 'salary']
    
    def validate_job(self, job: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a single job record.
        
        Args:
            job (Dict): Job data to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for required fields
        for field in self.required_fields:
            if field not in job or not job[field]:
                errors.append(f"Missing or empty required field: {field}")
        
        # Check field types and formats
        if 'title' in job and job['title']:
            if not isinstance(job['title'], str) or len(job['title'].strip()) < 2:
                errors.append("Job title must be a non-empty string with at least 2 characters")
        
        if 'company' in job and job['company']:
            if not isinstance(job['company'], str) or len(job['company'].strip()) < 2:
                errors.append("Company name must be a non-empty string with at least 2 characters")
        
        if 'link' in job and job['link']:
            if not self._is_valid_url(job['link']):
                errors.append(f"Invalid URL format: {job['link']}")
        
        if 'location' in job and job['location']:
            if not isinstance(job['location'], str):
                errors.append("Location must be a string")
        
        return len(errors) == 0, errors
    
    def validate_jobs(self, jobs: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate multiple job records.
        
        Args:
            jobs (List[Dict]): List of job data to validate
            
        Returns:
            Tuple[List[Dict], List[Dict]]: (valid_jobs, invalid_jobs)
        """
        valid_jobs = []
        invalid_jobs = []
        
        for job in jobs:
            is_valid, errors = self.validate_job(job)
            if is_valid:
                valid_jobs.append(job)
            else:
                job_copy = job.copy()
                job_copy['validation_errors'] = errors
                invalid_jobs.append(job_copy)
        
        return valid_jobs, invalid_jobs
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """
        Check if a URL is valid.
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid URL, False otherwise
        """
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(url_pattern, str(url)) is not None
