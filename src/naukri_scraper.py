"""
Naukri Job Scraper Module

This module contains functions to scrape job listings from Naukri.com
using HTML parsing with BeautifulSoup.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

class NaukriScraper:
    """Scraper class for Naukri.com job listings"""
    
    def __init__(self, base_url="https://www.naukri.com"):
        """
        Initialize the Naukri scraper.
        
        Args:
            base_url (str): The base URL for Naukri.com
        """
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.jobs_data = []
    
    def search_jobs(self, job_title, location=None, pages=1):
        """
        Search for jobs on Naukri.com
        
        Args:
            job_title (str): The job title to search for
            location (str): The location to search in (optional)
            pages (int): Number of pages to scrape
            
        Returns:
            list: List of job dictionaries
        """
        try:
            for page in range(pages):
                search_url = f"{self.base_url}/jobs/{job_title}-jobs"
                if location:
                    search_url += f"-in-{location}"
                
                search_url += f"?pageNo={page + 1}"
                
                print(f"Scraping page {page + 1} from Naukri...")
                self._scrape_page(search_url)
                time.sleep(2)  # Be respectful to the server
            
            return self.jobs_data
        
        except Exception as e:
            print(f"Error during Naukri scraping: {e}")
            return []
    
    def _scrape_page(self, url):
        """
        Scrape a single page from Naukri.
        
        Args:
            url (str): The URL to scrape
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            job_cards = soup.find_all('article', class_='jobTuple')
            
            for card in job_cards:
                job_data = self._extract_job_info(card)
                if job_data:
                    self.jobs_data.append(job_data)
        
        except requests.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
    
    def _extract_job_info(self, card):
        """
        Extract job information from a job card.
        
        Args:
            card: BeautifulSoup element representing a job card
            
        Returns:
            dict: Dictionary containing job information
        """
        try:
            job_title = card.find('a', class_='titleAnc')
            company_name = card.find('a', class_='comp-name')
            job_location = card.find('span', class_='locSpan')
            job_description = card.find('span', class_='job-desc')
            
            if not all([job_title, company_name, job_location]):
                return None
            
            job_info = {
                'title': job_title.get_text(strip=True),
                'company': company_name.get_text(strip=True),
                'location': job_location.get_text(strip=True),
                'description': job_description.get_text(strip=True) if job_description else 'N/A',
                'link': job_title.get('href') if job_title else 'N/A',
                'source': 'Naukri',
                'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return job_info
        
        except Exception as e:
            print(f"Error extracting job info: {e}")
            return None
