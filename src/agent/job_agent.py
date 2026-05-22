"""
Job Agent Module

This module orchestrates the job scraping process across multiple platforms
and handles data aggregation and storage.
"""

import pandas as pd
from datetime import datetime
import os
from typing import List, Optional, Union
from ..scrapers import NaukriScraper, RemoteOKScraper, WellfoundScraper
from ..processors import DataProcessor

class JobAgent:
    """Main Job Agent class to coordinate job scraping across platforms"""
    
    def __init__(self, output_dir: str = 'data'):
        """
        Initialize the Job Agent with scrapers for all platforms.
        
        Args:
            output_dir (str): Directory to store output CSV files
        """
        self.naukri_scraper = NaukriScraper()
        self.remoteok_scraper = RemoteOKScraper()
        self.wellfound_scraper = WellfoundScraper()
        self.data_processor = DataProcessor()
        self.all_jobs = []
        self.processed_jobs = []
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def search_jobs(
        self, 
        job_title: str, 
        location: Optional[str] = None, 
        platforms: Union[str, List[str]] = 'all'
    ) -> pd.DataFrame:
        """
        Search for jobs across specified platforms.
        
        Args:
            job_title (str): The job title to search for
            location (str): The location to search in (optional)
            platforms (str or list): Platforms to search ('all', 'naukri', 'remoteok', 'wellfound')
            
        Returns:
            pd.DataFrame: Aggregated job listings
        """
        jobs = []
        
        # Normalize platforms input
        if isinstance(platforms, str):
            if platforms.lower() == 'all':
                platforms_list = ['naukri', 'remoteok', 'wellfound']
            else:
                platforms_list = [platforms.lower()]
        else:
            platforms_list = [p.lower() for p in platforms]
        
        if 'naukri' in platforms_list:
            print("\n--- Searching Naukri ---")
            naukri_jobs = self.naukri_scraper.search_jobs(job_title, location, pages=1)
            jobs.extend(naukri_jobs)
        
        if 'remoteok' in platforms_list:
            print("\n--- Searching RemoteOK ---")
            remoteok_jobs = self.remoteok_scraper.search_jobs(job_title)
            jobs.extend(remoteok_jobs)
        
        if 'wellfound' in platforms_list:
            print("\n--- Searching Wellfound ---")
            wellfound_jobs = self.wellfound_scraper.search_jobs(job_title, location)
            jobs.extend(wellfound_jobs)
        
        self.all_jobs = jobs
        return self._create_dataframe(jobs)
    
    def process_jobs(
        self,
        clean: bool = True,
        validate: bool = True,
        remove_duplicates: bool = True
    ) -> tuple:
        """
        Process collected jobs through cleaning and validation pipeline.
        
        Args:
            clean (bool): Whether to clean data
            validate (bool): Whether to validate data
            remove_duplicates (bool): Whether to remove duplicates
            
        Returns:
            tuple: (processed_jobs_dataframe, statistics_dict)
        """
        if not self.all_jobs:
            print("No jobs to process. Run search_jobs() first.")
            return pd.DataFrame(), {}
        
        self.processed_jobs, stats = self.data_processor.process(
            self.all_jobs,
            clean=clean,
            validate=validate,
            remove_duplicates=remove_duplicates
        )
        
        print(self.data_processor.get_processing_report(stats))
        
        return self._create_dataframe(self.processed_jobs), stats
    
    def filter_jobs(
        self,
        title_keywords: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        job_types: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Filter processed jobs based on criteria.
        
        Args:
            title_keywords (List[str]): Keywords to filter by job title
            locations (List[str]): Locations to filter by
            sources (List[str]): Sources to filter by
            job_types (List[str]): Job types to filter by
            
        Returns:
            pd.DataFrame: Filtered jobs
        """
        if not self.processed_jobs:
            print("No processed jobs available. Run process_jobs() first.")
            return pd.DataFrame()
        
        filtered_jobs = self.processed_jobs.copy()
        
        if title_keywords:
            print(f"\nFiltering by title keywords: {title_keywords}")
            filtered_jobs = self.data_processor.filter.filter_by_title(filtered_jobs, title_keywords)
        
        if locations:
            print(f"Filtering by locations: {locations}")
            filtered_jobs = self.data_processor.filter.filter_by_location(filtered_jobs, locations)
        
        if sources:
            print(f"Filtering by sources: {sources}")
            filtered_jobs = self.data_processor.filter.filter_by_source(filtered_jobs, sources)
        
        if job_types:
            print(f"Filtering by job types: {job_types}")
            filtered_jobs = self.data_processor.filter.filter_by_job_type(filtered_jobs, job_types)
        
        print(f"Jobs after filtering: {len(filtered_jobs)}\n")
        
        return self._create_dataframe(filtered_jobs)
    
    def _create_dataframe(self, jobs: List[dict]) -> pd.DataFrame:
        """
        Create a DataFrame from job listings.
        
        Args:
            jobs (list): List of job dictionaries
            
        Returns:
            pd.DataFrame: Pandas DataFrame with job listings
        """
        if not jobs:
            print("No jobs found.")
            return pd.DataFrame()
        
        df = pd.DataFrame(jobs)
        
        # Ensure all expected columns are present
        expected_columns = [
            'title', 'company', 'location', 'description',
            'link', 'source', 'scraped_date'
        ]
        
        for col in expected_columns:
            if col not in df.columns:
                df[col] = 'N/A'
        
        # Reorder columns
        df = df[expected_columns + [col for col in df.columns if col not in expected_columns]]
        
        return df
    
    def save_to_csv(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Save job listings to a CSV file.
        
        Args:
            filename (str): Output filename (optional, default: jobs_YYYY-MM-DD_HH-MM-SS.csv)
            
        Returns:
            str: Path to the saved file or None if no jobs to save
        """
        if not self.all_jobs:
            print("No jobs to save. Run search_jobs() first.")
            return None
        
        df = self._create_dataframe(self.all_jobs)
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'jobs_{timestamp}.csv'
        
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False)
        
        print(f"\nJobs saved to: {filepath}")
        print(f"Total jobs found: {len(df)}")
        
        return filepath
    
    def display_summary(self) -> None:
        """Display a summary of the scraped jobs"""
        if not self.all_jobs:
            print("No jobs available. Run search_jobs() first.")
            return
        
        df = self._create_dataframe(self.all_jobs)
        
        print("\n" + "="*80)
        print("JOB SCRAPING SUMMARY")
        print("="*80)
        print(f"\nTotal Jobs Found: {len(df)}")
        print(f"\nJobs by Source:")
        print(df['source'].value_counts())
        print(f"\nTop Locations:")
        print(df['location'].value_counts().head(10))
        print("\n" + "="*80)
