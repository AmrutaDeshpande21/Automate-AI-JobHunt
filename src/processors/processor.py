"""
Data Processor Module

This module coordinates data cleaning, validation, and filtering.
"""

from typing import List, Dict, Optional, Tuple
from .cleaner import DataCleaner
from .validator import DataValidator
from .filter import JobFilter

class DataProcessor:
    """Main class to coordinate data processing"""
    
    def __init__(self):
        """Initialize the data processor with all sub-processors"""
        self.cleaner = DataCleaner()
        self.validator = DataValidator()
        self.filter = JobFilter()
    
    def process(
        self, 
        jobs: List[Dict],
        clean: bool = True,
        validate: bool = True,
        remove_duplicates: bool = True
    ) -> Tuple[List[Dict], Dict]:
        """
        Process jobs through cleaning and validation pipeline.
        
        Args:
            jobs (List[Dict]): Raw job data
            clean (bool): Whether to clean data
            validate (bool): Whether to validate data
            remove_duplicates (bool): Whether to remove duplicates
            
        Returns:
            Tuple[List[Dict], Dict]: (processed_jobs, processing_stats)
        """
        stats = {
            'raw_count': len(jobs),
            'cleaned_count': 0,
            'valid_count': 0,
            'invalid_count': 0,
            'duplicates_removed': 0,
            'final_count': 0,
        }
        
        processed_jobs = jobs.copy()
        
        # Step 1: Clean data
        if clean:
            processed_jobs = self.cleaner.clean_jobs(processed_jobs)
            stats['cleaned_count'] = len(processed_jobs)
        
        # Step 2: Validate data
        if validate:
            valid_jobs, invalid_jobs = self.validator.validate_jobs(processed_jobs)
            stats['valid_count'] = len(valid_jobs)
            stats['invalid_count'] = len(invalid_jobs)
            processed_jobs = valid_jobs
        
        # Step 3: Remove duplicates
        if remove_duplicates:
            duplicates_count = len(processed_jobs)
            processed_jobs = self.filter.remove_duplicates(processed_jobs)
            stats['duplicates_removed'] = duplicates_count - len(processed_jobs)
        
        stats['final_count'] = len(processed_jobs)
        
        return processed_jobs, stats
    
    def process_and_filter(
        self,
        jobs: List[Dict],
        title_keywords: Optional[List[str]] = None,
        exclude_keywords: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        job_types: Optional[List[str]] = None,
        clean: bool = True,
        validate: bool = True,
        remove_duplicates: bool = True
    ) -> Tuple[List[Dict], Dict]:
        """
        Process jobs with cleaning/validation and apply filters.
        
        Args:
            jobs (List[Dict]): Raw job data
            title_keywords (List[str]): Keywords to filter by job title
            exclude_keywords (List[str]): Keywords to exclude from job title
            locations (List[str]): Locations to filter by
            sources (List[str]): Sources to filter by
            job_types (List[str]): Job types to filter by
            clean (bool): Whether to clean data
            validate (bool): Whether to validate data
            remove_duplicates (bool): Whether to remove duplicates
            
        Returns:
            Tuple[List[Dict], Dict]: (filtered_jobs, stats)
        """
        # First process the data
        processed_jobs, stats = self.process(
            jobs,
            clean=clean,
            validate=validate,
            remove_duplicates=remove_duplicates
        )
        
        # Then apply filters
        filtered_jobs = processed_jobs
        
        if title_keywords or exclude_keywords:
            filtered_jobs = self.filter.filter_by_title(filtered_jobs, title_keywords or [], exclude_keywords=exclude_keywords)
        
        if locations:
            filtered_jobs = self.filter.filter_by_location(filtered_jobs, locations)
        
        if sources:
            filtered_jobs = self.filter.filter_by_source(filtered_jobs, sources)
        
        if job_types:
            filtered_jobs = self.filter.filter_by_job_type(filtered_jobs, job_types)
        
        stats['filtered_count'] = len(filtered_jobs)
        
        return filtered_jobs, stats
    
    def get_processing_report(self, stats: Dict) -> str:
        """
        Generate a processing report.
        
        Args:
            stats (Dict): Processing statistics
            
        Returns:
            str: Formatted report
        """
        report = "\n" + "="*80 + "\n"
        report += "DATA PROCESSING REPORT\n"
        report += "="*80 + "\n\n"
        
        report += f"Raw Jobs Count:        {stats.get('raw_count', 0)}\n"
        report += f"Cleaned Jobs Count:    {stats.get('cleaned_count', 0)}\n"
        report += f"Valid Jobs Count:      {stats.get('valid_count', 0)}\n"
        report += f"Invalid Jobs Count:    {stats.get('invalid_count', 0)}\n"
        report += f"Duplicates Removed:    {stats.get('duplicates_removed', 0)}\n"
        report += f"Filtered Count:        {stats.get('filtered_count', '-')}\n"
        report += f"\nFinal Jobs Count:      {stats.get('final_count', 0)}\n"
        report += "="*80 + "\n"
        
        return report
