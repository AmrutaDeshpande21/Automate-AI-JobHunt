"""
Job Agent Module

This module orchestrates the job scraping process across multiple platforms
and handles data aggregation and storage.
"""

import pandas as pd
from datetime import datetime
import os
import time
from typing import List, Optional, Union
from ..scrapers import NaukriScraper, NaukriSeleniumScraper, RemoteOKScraper, WellfoundScraper
from ..processors import DataProcessor
from ..utils.logger import logger

class JobAgent:
    """Main Job Agent class to coordinate job scraping across platforms"""
    
    def __init__(self, output_dir: str = 'doc'):
        """
        Initialize the Job Agent with scrapers for all platforms.
        
        Args:
            output_dir (str): Directory to store output CSV files
        """
        self.naukri_scraper = NaukriSeleniumScraper(headless=True)
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
            logger.info("--- Searching Naukri ---")
            naukri_jobs = self.naukri_scraper.search_jobs(job_title, location, pages=1)
            jobs.extend(naukri_jobs)
        
        if 'remoteok' in platforms_list:
            logger.info("--- Searching RemoteOK ---")
            remoteok_jobs = self.remoteok_scraper.search_jobs(job_title)
            jobs.extend(remoteok_jobs)
        
        if 'wellfound' in platforms_list:
            logger.info("--- Searching Wellfound ---")
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
            logger.warning("No jobs to process. Run search_jobs() first.")
            return pd.DataFrame(), {}
        
        self.processed_jobs, stats = self.data_processor.process(
            self.all_jobs,
            clean=clean,
            validate=validate,
            remove_duplicates=remove_duplicates
        )
        
        logger.info(self.data_processor.get_processing_report(stats))
        
        return self._create_dataframe(self.processed_jobs), stats
    
    def filter_jobs(
        self,
        title_keywords: Optional[List[str]] = None,
        exclude_keywords: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        job_types: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Filter processed jobs based on criteria.
        
        Args:
            title_keywords (List[str]): Keywords to filter by job title
            exclude_keywords (List[str]): Keywords to exclude from job title
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
        
        if title_keywords or exclude_keywords:
            logger.info(f"Filtering by titles (Include: {title_keywords}, Exclude: {exclude_keywords})")
            filtered_jobs = self.data_processor.filter.filter_by_title(
                filtered_jobs, 
                title_keywords or [], 
                exclude_keywords=exclude_keywords
            )
        
        if locations:
            logger.info(f"Filtering by locations: {locations}")
            filtered_jobs = self.data_processor.filter.filter_by_location(filtered_jobs, locations)
        
        if sources:
            logger.info(f"Filtering by sources: {sources}")
            filtered_jobs = self.data_processor.filter.filter_by_source(filtered_jobs, sources)
        
        if job_types:
            logger.info(f"Filtering by job types: {job_types}")
            filtered_jobs = self.data_processor.filter.filter_by_job_type(filtered_jobs, job_types)
        
        logger.info(f"Jobs after filtering: {len(filtered_jobs)}")
        
        self.processed_jobs = filtered_jobs
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
            logger.info("No jobs found.")
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
            else:
                df[col] = df[col].fillna('N/A').astype(str)
        
        # Keep ONLY expected columns and in that exact order
        df = df[expected_columns]
        
        return df
    
    def save_to_csv(self, filename: Optional[str] = None, append: bool = False) -> Optional[str]:
        """
        Save job listings to a CSV file.
        
        Args:
            filename (str): Output filename
            append (bool): If True, append to existing file instead of creating unique timestamped file
            
        Returns:
            str: Path to the saved file or None if no jobs to save
        """
        if not self.processed_jobs and not self.all_jobs:
            print("No jobs to save. Run search_jobs() and process_jobs() first.")
            return None
        
        # Prefer processed jobs if available
        jobs_to_save = self.processed_jobs if self.processed_jobs else self.all_jobs
        df = self._create_dataframe(jobs_to_save)
        
        if filename is None:
            if append:
                filename = 'master_jobs.csv'
            else:
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                filename = f'jobs_{timestamp}.csv'
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        filepath = os.path.join(self.output_dir, filename)
        
        expected_columns = [
            'title', 'company', 'location', 'description',
            'link', 'source', 'scraped_date'
        ]
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                if append and os.path.exists(filepath):
                    try:
                        existing_df = pd.read_csv(filepath)
                    except Exception as read_err:
                        logger.warning(f"Warning: Could not read existing file {filepath} ({read_err}). Overwriting instead.")
                        existing_df = pd.DataFrame()
                    
                    if not existing_df.empty:
                        # Align schema of existing to be safe
                        for col in expected_columns:
                            if col not in existing_df.columns:
                                existing_df[col] = 'N/A'
                            else:
                                existing_df[col] = existing_df[col].fillna('N/A').astype(str)
                        existing_df = existing_df[expected_columns]
                        
                        combined_df = pd.concat([existing_df, df], ignore_index=True)
                    else:
                        combined_df = df
                        
                    # Deduplicate based on title, company, location
                    combined_df = combined_df.drop_duplicates(subset=['title', 'company', 'location'])
                    combined_df.to_csv(filepath, index=False)
                    logger.info(f"Appended and deduplicated jobs in: {filepath}")
                else:
                    df.to_csv(filepath, index=False)
                    logger.info(f"Jobs saved to: {filepath}")
                
                # Successful write, break the retry loop
                break
                
            except PermissionError as perm_err:
                logger.error(f"Error: Permission denied when writing to {filepath}. File might be open in Excel or another program.")
                if attempt < max_retries - 1:
                    logger.warning(f"Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    # Final attempt failed, save to backup file
                    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                    backup_filename = f"backup_{timestamp}_{filename}"
                    backup_filepath = os.path.join(self.output_dir, backup_filename)
                    logger.critical(f"Critical: Failed to write to {filepath} after {max_retries} attempts.")
                    logger.info(f"Saving data to fallback file: {backup_filepath} to prevent data loss.")
                    try:
                        df.to_csv(backup_filepath, index=False)
                        filepath = backup_filepath
                    except Exception as fallback_err:
                        logger.error(f"Failed to write to fallback file: {fallback_err}")
                        raise perm_err
            except Exception as e:
                logger.error(f"Unexpected error writing to file {filepath}: {e}")
                raise e
        
        return filepath
    
    def display_summary(self) -> None:
        """Display a summary of the scraped jobs"""
        import sys
        if not self.all_jobs:
            print("No jobs available. Run search_jobs() first.")
            return
        
        df = self._create_dataframe(self.processed_jobs if self.processed_jobs else self.all_jobs)
        
        encoding = sys.stdout.encoding or 'utf-8'
        
        def safe_print(text: str) -> None:
            try:
                print(text)
            except UnicodeEncodeError:
                print(text.encode(encoding, errors='replace').decode(encoding))
                
        safe_print("\n" + "="*80)
        safe_print("JOB SCRAPING SUMMARY")
        safe_print("="*80)
        safe_print(f"\nTotal Jobs Found: {len(df)}")
        safe_print(f"\nJobs by Source:")
        safe_print(str(df['source'].value_counts()))
        safe_print(f"\nTop Locations:")
        safe_print(str(df['location'].value_counts().head(10)))
        safe_print("\n" + "="*80)
