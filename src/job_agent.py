"""
Main Job Agent Module

This module orchestrates the job scraping process across multiple platforms
and handles data aggregation and storage.
"""

from src.naukri_scraper import NaukriScraper
from src.remoteok_scraper import RemoteOKScraper
from src.wellfound_scraper import WellfoundScraper
import pandas as pd
from datetime import datetime
import os

class JobAgent:
    """Main Job Agent class to coordinate job scraping across platforms"""
    
    def __init__(self):
        """Initialize the Job Agent with scrapers for all platforms"""
        self.naukri_scraper = NaukriScraper()
        self.remoteok_scraper = RemoteOKScraper()
        self.wellfound_scraper = WellfoundScraper()
        self.all_jobs = []
        self.output_dir = 'data'
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def search_jobs(self, job_title, location=None, platforms='all'):
        """
        Search for jobs across specified platforms.
        
        Args:
            job_title (str): The job title to search for
            location (str): The location to search in (optional)
            platforms (str or list): Platforms to search ('all', 'naukri', 'remoteok', 'wellfound')
            
        Returns:
            DataFrame: Aggregated job listings
        """
        jobs = []
        
        if platforms == 'all' or 'naukri' in str(platforms).lower():
            print("\n--- Searching Naukri ---")
            naukri_jobs = self.naukri_scraper.search_jobs(job_title, location, pages=1)
            jobs.extend(naukri_jobs)
        
        if platforms == 'all' or 'remoteok' in str(platforms).lower():
            print("\n--- Searching RemoteOK ---")
            remoteok_jobs = self.remoteok_scraper.search_jobs(job_title)
            jobs.extend(remoteok_jobs)
        
        if platforms == 'all' or 'wellfound' in str(platforms).lower():
            print("\n--- Searching Wellfound ---")
            wellfound_jobs = self.wellfound_scraper.search_jobs(job_title, location)
            jobs.extend(wellfound_jobs)
        
        self.all_jobs = jobs
        return self._create_dataframe(jobs)
    
    def _create_dataframe(self, jobs):
        """
        Create a DataFrame from job listings.
        
        Args:
            jobs (list): List of job dictionaries
            
        Returns:
            DataFrame: Pandas DataFrame with job listings
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
    
    def save_to_csv(self, filename=None):
        """
        Save job listings to a CSV file.
        
        Args:
            filename (str): Output filename (optional, default: jobs_YYYY-MM-DD.csv)
            
        Returns:
            str: Path to the saved file
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
    
    def display_summary(self):
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
        print(f"\nJobs by Location:")
        print(df['location'].value_counts().head(10))
        print("\n" + "="*80)
