"""
Naukri Job Scraper Module

This module contains the scraper for job listings from Naukri.com
using HTML parsing with BeautifulSoup.
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Optional
from .base import BaseScraper
from ..utils.logger import logger

class NaukriScraper(BaseScraper):
    """Scraper class for Naukri.com job listings"""
    
    def __init__(self, base_url: str = "https://www.naukri.com"):
        """
        Initialize the Naukri scraper.
        
        Args:
            base_url (str): The base URL for Naukri.com
        """
        super().__init__(source_name="Naukri")
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
    
    def search_jobs(self, job_title: str, location: Optional[str] = None, pages: int = 1) -> List[Dict]:
        """
        Search for jobs on Naukri.com
        
        Args:
            job_title (str): The job title to search for
            location (str): The location to search in (optional)
            pages (int): Number of pages to scrape
            
        Returns:
            List[Dict]: List of job dictionaries
        """
        try:
            # Clean job title and location for URL
            search_title = job_title.lower().replace(' ', '-')
            search_loc = location.lower().replace(' ', '-') if location else ""
            
            for page in range(pages):
                if search_loc:
                    search_url = f"{self.base_url}/{search_title}-jobs-in-{search_loc}-{page + 1}"
                else:
                    search_url = f"{self.base_url}/{search_title}-jobs-{page + 1}"
                
                logger.info(f"Scraping page {page + 1} from Naukri: {search_url}")
                self._scrape_page(search_url)
                time.sleep(3)  # Increased delay for Naukri
            
            logger.info(f"Found {len(self.jobs_data)} jobs from Naukri")
            return self.jobs_data
        
        except Exception as e:
            logger.error(f"Error during Naukri scraping: {e}")
            return []
    
    def _scrape_page(self, url: str) -> None:
        """
        Scrape a single page from Naukri.
        
        Args:
            url (str): The URL to scrape
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 403:
                logger.warning("Warning: Naukri access blocked (403). Consider using Selenium or a proxy.")
                return

            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            # Naukri often changes classes. Common ones are 'cust-job-tuple' or 'jobTuple'
            job_cards = soup.find_all(['div', 'article'], class_=lambda x: x and ('jobTuple' in x or 'cust-job-tuple' in x))
            
            if not job_cards:
                # Fallback: look for any links with 'job-description' in them
                job_cards = soup.find_all('a', href=lambda x: x and 'job-description' in x)
            
            for card in job_cards:
                job_data = self._extract_job_info(card)
                if job_data and self._validate_job_data(job_data):
                    job_data = self._add_metadata(job_data)
                    self.jobs_data.append(job_data)
        
        except requests.RequestException as e:
            logger.error(f"Error fetching URL {url}: {e}")
    
    def _extract_job_info(self, card) -> Optional[Dict]:
        """
        Extract job information from a job card.
        """
        try:
            # Try multiple selector variations for Naukri's dynamic layout
            title_elem = card.find('a', class_=lambda x: x and ('title' in x.lower() or 'job-title' in x.lower()))
            comp_elem = card.find(['a', 'span', 'div'], class_=lambda x: x and ('comp-name' in x.lower() or 'company' in x.lower()))
            loc_elem = card.find('span', class_=lambda x: x and ('loc' in x.lower() or 'location' in x.lower()))
            desc_elem = card.find(['span', 'div'], class_=lambda x: x and ('desc' in x.lower() or 'job-description' in x.lower()))
            
            if not title_elem:
                return None
            
            job_info = {
                'title': title_elem.get_text(strip=True),
                'company': comp_elem.get_text(strip=True) if comp_elem else 'Confidential',
                'location': loc_elem.get_text(strip=True) if loc_elem else 'India',
                'description': desc_elem.get_text(strip=True) if desc_elem else 'N/A',
                'link': title_elem.get('href') if title_elem.has_attr('href') else 'N/A',
            }
            
            # Absolute URL check
            if job_info['link'].startswith('/'):
                job_info['link'] = self.base_url + job_info['link']
                
            return job_info
        
        except Exception as e:
            logger.error(f"Error extracting job info from card: {e}")
            return None

class NaukriSeleniumScraper(NaukriScraper):
    """
    Experimental Selenium-based scraper for Naukri to handle dynamic content
    Requires selenium and webdriver-manager
    """
    
    def __init__(self, base_url: str = "https://www.naukri.com", headless: bool = True):
        super().__init__(base_url)
        self.headless = headless
        self.driver = None
    
    def _init_driver(self):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except ImportError:
            logger.error("Error: Selenium or webdriver-manager not installed. Run 'pip install selenium webdriver-manager'")
            raise
    
    def search_jobs(self, job_title: str, location: Optional[str] = None, pages: int = 1) -> List[Dict]:
        """Search jobs using Selenium"""
        try:
            self._init_driver()
            search_title = job_title.lower().replace(' ', '-')
            search_loc = location.lower().replace(' ', '-') if location else ""
            
            for page in range(pages):
                if search_loc:
                    search_url = f"{self.base_url}/{search_title}-jobs-in-{search_loc}-{page + 1}"
                else:
                    search_url = f"{self.base_url}/{search_title}-jobs-{page + 1}"
                
                logger.info(f"Scraping page {page + 1} from Naukri using Selenium: {search_url}")
                self.driver.get(search_url)
                time.sleep(8)  # Wait for dynamic content
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                job_cards = soup.find_all(['div', 'article'], class_=lambda x: x and ('jobTuple' in x or 'cust-job-tuple' in x))
                
                for card in job_cards:
                    job_data = self._extract_job_info(card)
                    if job_data and self._validate_job_data(job_data):
                        job_data = self._add_metadata(job_data)
                        self.jobs_data.append(job_data)
            
            return self.jobs_data
        except Exception as e:
            logger.error(f"Selenium error: {e}")
            return self.jobs_data
        finally:
            if self.driver:
                self.driver.quit()
