"""
RemoteOK Job Scraper Module

This module contains functions to fetch job listings from RemoteOK.com
using their Public API.
"""

import requests
import pandas as pd
from datetime import datetime
import time

class RemoteOKScraper:
    """Scraper class for RemoteOK job listings using their API"""
    
    def __init__(self, api_url="https://remoteok.com/api"):
        """
        Initialize the RemoteOK scraper.
        
        Args:
            api_url (str): The base API URL for RemoteOK
        """
        self.api_url = api_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.jobs_data = []
    
    def search_jobs(self, job_title=None, job_type='all'):
        """
        Search for jobs on RemoteOK using their API.
        
        Args:
            job_title (str): The job title to filter by (optional)
            job_type (str): Type of job ('all', 'fulltime', 'freelance', 'parttime')
            
        Returns:
            list: List of job dictionaries
        """
        try:
            url = f"{self.api_url}"
            
            print(f"Fetching jobs from RemoteOK API...")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            jobs = response.json()
            
            # Filter jobs based on job_title if provided
            filtered_jobs = []
            for job in jobs:
                # Skip the first dict if it's metadata
                if isinstance(job, dict) and job.get('id') == 'remote-ok':
                    continue
                
                if job_title and job_title.lower() not in job.get('title', '').lower():
                    continue
                
                job_data = self._extract_job_info(job)
                if job_data:
                    filtered_jobs.append(job_data)
            
            self.jobs_data.extend(filtered_jobs)
            return filtered_jobs
        
        except requests.RequestException as e:
            print(f"Error fetching from RemoteOK API: {e}")
            return []
        except Exception as e:
            print(f"Error processing RemoteOK data: {e}")
            return []
    
    def _extract_job_info(self, job):
        """
        Extract job information from RemoteOK API response.
        
        Args:
            job (dict): Job data from the API
            
        Returns:
            dict: Dictionary containing job information
        """
        try:
            job_info = {
                'title': job.get('title', 'N/A'),
                'company': job.get('company', 'N/A'),
                'location': job.get('location', 'Remote'),
                'description': job.get('description', 'N/A'),
                'link': job.get('url', 'N/A'),
                'source': 'RemoteOK',
                'job_type': job.get('job_type', 'N/A'),
                'salary': job.get('salary', 'N/A'),
                'tags': job.get('tags', []),
                'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return job_info
        
        except Exception as e:
            print(f"Error extracting job info from RemoteOK: {e}")
            return None
