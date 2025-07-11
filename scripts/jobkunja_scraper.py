#!/usr/bin/env python3
"""
JobKunja Scraper - Extract jobs from jobkunja.com
URL: https://jobkunja.com
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
from utils import BaseScraper

class JobKunjaScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            website_name="jobkunja",
            base_url="https://jobkunja.com",
            delay=1.5
        )
        self.name = "JobKunja"
        self.source_url = self.base_url
    
    def get_job_links(self, page_num: int = 1) -> List[str]:
        """Get job links from the page"""
        return []
    
    def get_total_pages(self) -> int:
        """Get total number of pages"""
        return 5
    
    def scrape_job_details(self, job_url: str) -> Dict[str, Any]:
        """Scrape job details from URL"""
        return {}

    def scrape_jobs(self, max_pages=5):
        """
        Scrape jobs from JobKunja
        """
        all_jobs = []
        
        try:
            # Start with main page to find job listings
            main_page_jobs = self._scrape_main_page()
            all_jobs.extend(main_page_jobs)
            
            # Try to find dedicated job listing pages
            job_listing_pages = [
                f"{self.base_url}/jobs/search",
                f"{self.base_url}/job_type/top_job",
                f"{self.base_url}/job_type/hot_job"
            ]
            
            for page_url in job_listing_pages:
                try:
                    self.logger.info(f"Scraping page: {page_url}")
                    page_jobs = self._scrape_job_listing_page(page_url)
                    all_jobs.extend(page_jobs)
                    time.sleep(self.delay)
                except Exception as e:
                    self.logger.warning(f"Error scraping {page_url}: {e}")
                    continue
            
            # Remove duplicates based on job title and company
            unique_jobs = self._remove_duplicates(all_jobs)
            
            self.logger.info(f"Successfully scraped {len(unique_jobs)} unique jobs from {self.name}")
            return unique_jobs
            
        except Exception as e:
            self.logger.error(f"Error in scraping {self.name}: {e}")
            return []
    
    def _scrape_main_page(self):
        """Scrape jobs from the main homepage"""
        jobs = []
        
        try:
            response = self.make_request(self.base_url)
            if not response:
                return jobs
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for job cards
            job_cards = soup.select('.card')
            self.logger.info(f"Found {len(job_cards)} job cards on main page")
            
            for card in job_cards:
                job = self._extract_job_from_card(card)
                if job:
                    jobs.append(job)
            
        except Exception as e:
            self.logger.error(f"Error scraping main page: {e}")
        
        return jobs
    
    def _scrape_job_listing_page(self, url):
        """Scrape jobs from a specific job listing page"""
        jobs = []
        
        try:
            response = self.make_request(url)
            if not response:
                return jobs
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for job listings with various selectors
            job_elements = soup.select('.card, .job-item, .vacancy, .job-listing')
            self.logger.info(f"Found {len(job_elements)} job elements on {url}")
            
            for element in job_elements:
                job = self._extract_job_from_element(element)
                if job:
                    jobs.append(job)
            
        except Exception as e:
            self.logger.error(f"Error scraping job listing page {url}: {e}")
        
        return jobs
    
    def _extract_job_from_card(self, card):
        """Extract job information from a card element"""
        try:
            job = {}
            
            # Extract job title (look for headings or strong text)
            title_elem = card.find(['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'b'])
            if title_elem:
                job['title'] = title_elem.get_text().strip()
            else:
                # Try to get first meaningful text
                texts = [text.strip() for text in card.stripped_strings if len(text.strip()) > 3]
                if texts:
                    job['title'] = texts[0]
                else:
                    return None
            
            # Extract company name (usually appears after title)
            company_elem = card.find(['span', 'div', 'p'], class_=lambda x: x and 'company' in x.lower())
            if company_elem:
                job['company'] = company_elem.get_text().strip()
            else:
                # Try to find company in text patterns
                texts = list(card.stripped_strings)
                for i, text in enumerate(texts):
                    if 'pvt' in text.lower() or 'ltd' in text.lower() or 'company' in text.lower():
                        job['company'] = text.strip()
                        break
                if 'company' not in job and len(texts) > 1:
                    job['company'] = texts[1] if texts[1] != job.get('title') else 'Not specified'
            
            # Extract location
            location_elem = card.find(['span', 'div', 'p'], class_=lambda x: x and 'location' in x.lower())
            if location_elem:
                job['location'] = location_elem.get_text().strip()
            else:
                # Look for location patterns in text
                text_content = card.get_text()
                location_match = re.search(r'(Kathmandu|Lalitpur|Bhaktapur|Pokhara|[A-Za-z\s]+,\s*Nepal)', text_content, re.IGNORECASE)
                if location_match:
                    job['location'] = location_match.group(1)
                else:
                    job['location'] = 'Nepal'
            
            # Look for job link
            link_elem = card.find('a', href=True)
            if link_elem:
                job['job_url'] = urljoin(self.base_url, link_elem['href'])
            
            # Extract other details from text
            card_text = card.get_text()
            
            # Look for job type
            if any(word in card_text.lower() for word in ['full time', 'full-time']):
                job['job_type'] = 'Full Time'
            elif any(word in card_text.lower() for word in ['part time', 'part-time']):
                job['job_type'] = 'Part Time'
            else:
                job['job_type'] = 'Not specified'
            
            # Look for salary information
            salary_match = re.search(r'(?:Rs\.?|NRS|NPR)?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|K|thousand|lakh)?(?:\s*-\s*(?:Rs\.?|NRS|NPR)?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|K|thousand|lakh)?)?', card_text)
            if salary_match:
                job['salary'] = salary_match.group(0)
            else:
                job['salary'] = 'Not specified'
            
            # Add metadata
            job['source'] = self.name
            job['source_url'] = self.source_url
            from datetime import datetime
            job['scraped_date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Validate required fields
            if not job.get('title') or len(job['title']) < 3:
                return None
            
            # Clean up title
            job['title'] = re.sub(r'\s+', ' ', job['title']).strip()
            
            return job
            
        except Exception as e:
            self.logger.warning(f"Error extracting job from card: {e}")
            return None
    
    def _extract_job_from_element(self, element):
        """Extract job from generic element (fallback method)"""
        return self._extract_job_from_card(element)
    
    def _remove_duplicates(self, jobs):
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Create a key based on title and company (case-insensitive)
            key = (job.get('title', '').lower().strip(), job.get('company', '').lower().strip())
            if key not in seen and key[0]:  # Ensure title is not empty
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs

def main():
    """Test the scraper"""
    scraper = JobKunjaScraper()
    jobs = scraper.scrape_jobs(max_pages=3)
    
    print(f"\n=== JobKunja Scraper Results ===")
    print(f"Total jobs found: {len(jobs)}")
    
    if jobs:
        print("\nSample jobs:")
        for i, job in enumerate(jobs[:5]):
            print(f"\n{i+1}. {job.get('title', 'N/A')}")
            print(f"   Company: {job.get('company', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Type: {job.get('job_type', 'N/A')}")
            print(f"   URL: {job.get('job_url', 'N/A')}")
    
    return jobs

if __name__ == "__main__":
    main() 