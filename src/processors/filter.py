"""
Job Filter Module

This module filters job listings based on various criteria.
"""

from typing import List, Dict, Optional, Callable
import re

class JobFilter:
    """Class to filter job listings"""
    
    def __init__(self):
        """Initialize the filter"""
        pass
    
    def filter_by_title(self, jobs: List[Dict], title_keywords: List[str], exact_match: bool = False) -> List[Dict]:
        """
        Filter jobs by title keywords.
        
        Args:
            jobs (List[Dict]): List of jobs to filter
            title_keywords (List[str]): Keywords to match in job title
            exact_match (bool): If True, match entire title; if False, match any keyword
            
        Returns:
            List[Dict]: Filtered jobs
        """
        if not title_keywords:
            return jobs
        
        filtered_jobs = []
        
        for job in jobs:
            title = job.get('title', '').lower()
            
            if exact_match:
                # Match entire title
                if title in [kw.lower() for kw in title_keywords]:
                    filtered_jobs.append(job)
            else:
                # Match any keyword
                if any(kw.lower() in title for kw in title_keywords):
                    filtered_jobs.append(job)
        
        return filtered_jobs
    
    def filter_by_location(self, jobs: List[Dict], locations: List[str]) -> List[Dict]:
        """
        Filter jobs by location.
        
        Args:
            jobs (List[Dict]): List of jobs to filter
            locations (List[str]): Locations to match
            
        Returns:
            List[Dict]: Filtered jobs
        """
        if not locations:
            return jobs
        
        filtered_jobs = []
        locations_lower = [loc.lower() for loc in locations]
        
        for job in jobs:
            location = job.get('location', '').lower()
            if any(loc in location for loc in locations_lower):
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def filter_by_source(self, jobs: List[Dict], sources: List[str]) -> List[Dict]:
        """
        Filter jobs by source platform.
        
        Args:
            jobs (List[Dict]): List of jobs to filter
            sources (List[str]): Source platforms to include
            
        Returns:
            List[Dict]: Filtered jobs
        """
        if not sources:
            return jobs
        
        filtered_jobs = []
        sources_lower = [src.lower() for src in sources]
        
        for job in jobs:
            source = job.get('source', '').lower()
            if source in sources_lower:
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def filter_by_salary_range(self, jobs: List[Dict], min_salary: Optional[float] = None, max_salary: Optional[float] = None) -> List[Dict]:
        """
        Filter jobs by salary range.
        
        Args:
            jobs (List[Dict]): List of jobs to filter
            min_salary (float): Minimum salary (optional)
            max_salary (float): Maximum salary (optional)
            
        Returns:
            List[Dict]: Filtered jobs
        """
        filtered_jobs = []
        
        for job in jobs:
            salary = job.get('salary')
            
            # Skip if salary is not provided
            if not salary or salary == 'N/A':
                continue
            
            try:
                # Extract numeric value from salary
                salary_value = self._extract_salary_value(salary)
                
                if salary_value is None:
                    continue
                
                if min_salary and salary_value < min_salary:
                    continue
                
                if max_salary and salary_value > max_salary:
                    continue
                
                filtered_jobs.append(job)
            
            except Exception:
                # Skip jobs with invalid salary format
                continue
        
        return filtered_jobs
    
    def filter_by_job_type(self, jobs: List[Dict], job_types: List[str]) -> List[Dict]:
        """
        Filter jobs by job type (fulltime, freelance, parttime, etc.).
        
        Args:
            jobs (List[Dict]): List of jobs to filter
            job_types (List[str]): Job types to include
            
        Returns:
            List[Dict]: Filtered jobs
        """
        if not job_types:
            return jobs
        
        filtered_jobs = []
        job_types_lower = [jt.lower() for jt in job_types]
        
        for job in jobs:
            job_type = job.get('job_type', '').lower()
            if job_type in job_types_lower:
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def filter_by_custom_criteria(self, jobs: List[Dict], criteria_func: Callable[[Dict], bool]) -> List[Dict]:
        """
        Filter jobs using a custom filter function.
        
        Args:
            jobs (List[Dict]): List of jobs to filter
            criteria_func (Callable): Function that returns True if job matches criteria
            
        Returns:
            List[Dict]: Filtered jobs
        """
        return [job for job in jobs if criteria_func(job)]
    
    def remove_duplicates(self, jobs: List[Dict], key_fields: Optional[List[str]] = None) -> List[Dict]:
        """
        Remove duplicate jobs based on specific fields.
        
        Args:
            jobs (List[Dict]): List of jobs to deduplicate
            key_fields (List[str]): Fields to use for duplicate detection
            
        Returns:
            List[Dict]: Deduplicated jobs
        """
        if key_fields is None:
            key_fields = ['title', 'company', 'location']
        
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Create a tuple of key field values
            key = tuple(str(job.get(field, '')).lower() for field in key_fields)
            
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    @staticmethod
    def _extract_salary_value(salary_str: str) -> Optional[float]:
        """
        Extract numeric salary value from salary string.
        
        Args:
            salary_str (str): Salary string
            
        Returns:
            float: Extracted salary value or None
        """
        # Remove common currency symbols and text
        salary_str = str(salary_str).lower()
        salary_str = re.sub(r'[^\d.,]', '', salary_str)
        
        if not salary_str:
            return None
        
        try:
            # Handle comma as thousand separator
            salary_str = salary_str.replace(',', '')
            return float(salary_str)
        except ValueError:
            return None
