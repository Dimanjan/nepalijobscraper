"""
Base scraper class for Nepal job websites.

Provides common functionality like session management, error handling,
rate limiting, and data validation.
"""

import time
import json
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from .logger_config import setup_logger
from .data_manager import DataManager


class BaseScraper(ABC):
    """Base class for all job website scrapers."""
    
    def __init__(self, 
                 website_name: str,
                 base_url: str,
                 delay: float = 1.0,
                 max_retries: int = 3):
        """
        Initialize the base scraper.
        
        Args:
            website_name: Name of the website being scraped
            base_url: Base URL of the website
            delay: Delay between requests in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.website_name = website_name
        self.base_url = base_url
        self.delay = delay
        self.max_retries = max_retries
        
        # Setup logging
        self.logger = setup_logger(f"scraper_{website_name}")
        
        # Setup session with common headers
        self.session = requests.Session()
        self.ua = UserAgent()
        self._update_headers()
        
        # Data manager for storing results
        self.data_manager = DataManager()
        
        # Statistics
        self.stats = {
            'jobs_scraped': 0,
            'pages_scraped': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        
    def _update_headers(self):
        """Update session headers with random user agent."""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def make_request(self, url: str, **kwargs) -> requests.Response:
        """
        Make a HTTP request with retry logic and rate limiting.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        try:
            # Rate limiting
            time.sleep(self.delay)
            
            # Make request
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            
            self.logger.debug(f"Successfully fetched: {url}")
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {url}: {str(e)}")
            self.stats['errors'] += 1
            raise
    
    @abstractmethod
    def get_job_links(self, page: int = 1) -> List[str]:
        """
        Get list of job links from a search page.
        
        Args:
            page: Page number to scrape
            
        Returns:
            List of job URLs
        """
        pass
    
    @abstractmethod
    def scrape_job_details(self, job_url: str) -> Dict[str, Any]:
        """
        Scrape detailed information from a job posting.
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Dictionary containing job details
        """
        pass
    
    @abstractmethod
    def get_total_pages(self) -> int:
        """
        Get the total number of pages available.
        
        Returns:
            Total number of pages
        """
        pass
    
    def validate_job_data(self, job_data: Dict[str, Any]) -> bool:
        """
        Validate scraped job data.
        
        Args:
            job_data: Job data dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['title', 'company', 'url']
        
        for field in required_fields:
            if not job_data.get(field):
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        return True
    
    def clean_job_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and standardize job data.
        
        Args:
            job_data: Raw job data
            
        Returns:
            Cleaned job data
        """
        # Add metadata
        job_data['source_website'] = self.website_name
        job_data['scraped_at'] = datetime.now().isoformat()
        
        # Clean text fields
        text_fields = ['title', 'company', 'location', 'description']
        for field in text_fields:
            if job_data.get(field):
                job_data[field] = job_data[field].strip()
        
        return job_data
    
    def scrape_all(self, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Scrape all jobs from the website.
        
        Args:
            max_pages: Maximum number of pages to scrape (None for all)
            
        Returns:
            List of job dictionaries
        """
        self.logger.info(f"Starting scrape of {self.website_name}")
        self.stats['start_time'] = datetime.now()
        
        all_jobs = []
        
        try:
            # Get total pages
            total_pages = self.get_total_pages()
            if max_pages:
                total_pages = min(total_pages, max_pages)
            
            self.logger.info(f"Scraping {total_pages} pages")
            
            # Scrape each page
            for page in range(1, total_pages + 1):
                self.logger.info(f"Scraping page {page}/{total_pages}")
                
                try:
                    # Get job links from this page
                    job_links = self.get_job_links(page)
                    self.stats['pages_scraped'] += 1
                    
                    # Scrape each job
                    for job_url in job_links:
                        try:
                            job_data = self.scrape_job_details(job_url)
                            
                            if self.validate_job_data(job_data):
                                job_data = self.clean_job_data(job_data)
                                all_jobs.append(job_data)
                                self.stats['jobs_scraped'] += 1
                                
                                # Save job immediately
                                self.data_manager.save_job(job_data, self.website_name)
                                
                        except Exception as e:
                            self.logger.error(f"Error scraping job {job_url}: {str(e)}")
                            self.stats['errors'] += 1
                            continue
                    
                except Exception as e:
                    self.logger.error(f"Error scraping page {page}: {str(e)}")
                    self.stats['errors'] += 1
                    continue
        
        except Exception as e:
            self.logger.error(f"Fatal error during scraping: {str(e)}")
            raise
        
        finally:
            self.stats['end_time'] = datetime.now()
            self._log_stats()
        
        return all_jobs
    
    def _log_stats(self):
        """Log scraping statistics."""
        duration = None
        if self.stats['start_time'] and self.stats['end_time']:
            duration = self.stats['end_time'] - self.stats['start_time']
        
        self.logger.info(f"""
        Scraping completed for {self.website_name}:
        - Jobs scraped: {self.stats['jobs_scraped']}
        - Pages scraped: {self.stats['pages_scraped']}
        - Errors: {self.stats['errors']}
        - Duration: {duration}
        """) 