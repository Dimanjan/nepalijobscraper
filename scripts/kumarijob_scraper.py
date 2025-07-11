#!/usr/bin/env python3
"""
KumariJob Scraper - Extract jobs from kumarijob.com
URL: https://www.kumarijob.com
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
from utils import BaseScraper

class KumariJobScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            website_name="kumarijob",
            base_url="https://www.kumarijob.com",
            delay=2.0  # Slightly longer delay due to connection issues
        )
        self.name = "KumariJob"
        self.source_url = self.base_url
        self.max_retries = 3
    
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
        Scrape jobs from KumariJob with retry logic
        """
        all_jobs = []
        
        try:
            # Start with main page
            main_page_jobs = self._scrape_main_page_with_retry()
            all_jobs.extend(main_page_jobs)
            
            # Try job listing pages
            job_listing_urls = [
                f"{self.base_url}/jobs",
                f"{self.base_url}/search",
                f"{self.base_url}/job-search",
                f"{self.base_url}/vacancy"
            ]
            
            for url in job_listing_urls:
                try:
                    self.logger.info(f"Trying job listing page: {url}")
                    page_jobs = self._scrape_page_with_retry(url)
                    all_jobs.extend(page_jobs)
                    time.sleep(self.delay)
                except Exception as e:
                    self.logger.warning(f"Error scraping {url}: {e}")
                    continue
            
            # Remove duplicates
            unique_jobs = self._remove_duplicates(all_jobs)
            
            self.logger.info(f"Successfully scraped {len(unique_jobs)} unique jobs from {self.name}")
            return unique_jobs
            
        except Exception as e:
            self.logger.error(f"Error in scraping {self.name}: {e}")
            return []
    
    def _scrape_main_page_with_retry(self):
        """Scrape jobs from the main page with retry logic"""
        jobs = []
        
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Attempt {attempt + 1} to scrape main page")
                response = self.make_request(self.base_url)
                if not response:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for job elements
                job_selectors = [
                    '.job-item', '.job-card', '.job-listing', '.job',
                    '.featured-job', '.vacancy', '.position',
                    '[data-job]', '.job-post'
                ]
                
                job_elements = []
                for selector in job_selectors:
                    elements = soup.select(selector)
                    if elements:
                        job_elements = elements
                        self.logger.info(f"Found {len(elements)} job elements with selector: {selector}")
                        break
                
                # If no specific job selectors work, look for company/job related elements
                if not job_elements:
                    job_elements = soup.find_all(['div', 'li'], class_=lambda x: x and any(
                        word in x.lower() for word in ['job', 'vacancy', 'company', 'position']
                    ))
                    self.logger.info(f"Found {len(job_elements)} potential job elements")
                
                for element in job_elements:
                    job = self._extract_job_from_element(element)
                    if job:
                        jobs.append(job)
                
                if jobs:
                    self.logger.info(f"Successfully extracted {len(jobs)} jobs from main page")
                    break
                else:
                    self.logger.warning(f"No jobs found on attempt {attempt + 1}")
                    time.sleep(2 ** attempt)
                
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    self.logger.error(f"All {self.max_retries} attempts failed for main page")
        
        return jobs
    
    def _scrape_page_with_retry(self, url):
        """Scrape a specific page with retry logic"""
        jobs = []
        
        for attempt in range(self.max_retries):
            try:
                response = self.make_request(url)
                if not response:
                    time.sleep(2 ** attempt)
                    continue
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for job elements
                job_elements = soup.select('.job-item, .job-card, .job-listing, .job, .vacancy')
                
                if not job_elements:
                    job_elements = soup.find_all(['div', 'li'], class_=lambda x: x and any(
                        word in x.lower() for word in ['job', 'vacancy', 'position']
                    ))
                
                self.logger.info(f"Found {len(job_elements)} job elements on {url}")
                
                for element in job_elements:
                    job = self._extract_job_from_element(element)
                    if job:
                        jobs.append(job)
                
                break  # Success, exit retry loop
                
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
        
        return jobs
    
    def _extract_job_from_element(self, element):
        """Extract job information from an element"""
        try:
            job = {}
            
            # Extract job title
            title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'b', 'a'])
            if title_elem:
                job['title'] = title_elem.get_text().strip()
            else:
                # Try to get meaningful text
                texts = [text.strip() for text in element.stripped_strings if len(text.strip()) > 5]
                if texts:
                    job['title'] = texts[0]
                else:
                    return None
            
            # Skip if title is too generic
            if (not job.get('title') or 
                len(job['title']) < 3 or 
                job['title'].lower() in ['job', 'vacancy', 'position', 'career', 'apply', 'view', 'more']):
                return None
            
            # Extract company name
            element_text = element.get_text()
            texts = list(element.stripped_strings)
            
            # Look for company patterns
            company_patterns = [
                r'Company:\s*([^\n\r]+)',
                r'Employer:\s*([^\n\r]+)',
                r'Organization:\s*([^\n\r]+)'
            ]
            
            job['company'] = 'Not specified'
            for pattern in company_patterns:
                match = re.search(pattern, element_text, re.IGNORECASE)
                if match:
                    job['company'] = match.group(1).strip()
                    break
            
            # If no explicit company found, look for company-like text
            if job['company'] == 'Not specified':
                for text in texts:
                    if (any(word in text.lower() for word in ['pvt', 'ltd', 'company', 'corp', 'inc', 'organization', 'institute', 'bank', 'hospital']) and 
                        text != job['title'] and len(text) > 3):
                        job['company'] = text.strip()
                        break
            
            # Extract location
            location_patterns = [
                r'Location:\s*([^\n\r]+)',
                r'Place:\s*([^\n\r]+)',
                r'Address:\s*([^\n\r]+)'
            ]
            
            job['location'] = 'Nepal'
            for pattern in location_patterns:
                match = re.search(pattern, element_text, re.IGNORECASE)
                if match:
                    job['location'] = match.group(1).strip()
                    break
            
            # Look for Nepal location keywords
            if job['location'] == 'Nepal':
                location_match = re.search(r'(Kathmandu|Lalitpur|Bhaktapur|Pokhara|[A-Za-z\s]+,\s*Nepal)', element_text, re.IGNORECASE)
                if location_match:
                    job['location'] = location_match.group(1)
            
            # Look for job link
            link_elem = element.find('a', href=True)
            if link_elem and link_elem.get('href'):
                href = link_elem['href']
                if href.startswith('http'):
                    job['job_url'] = href
                else:
                    job['job_url'] = urljoin(self.base_url, href)
            
            # Extract job type
            if any(word in element_text.lower() for word in ['full time', 'full-time']):
                job['job_type'] = 'Full Time'
            elif any(word in element_text.lower() for word in ['part time', 'part-time']):
                job['job_type'] = 'Part Time'
            elif any(word in element_text.lower() for word in ['contract']):
                job['job_type'] = 'Contract'
            else:
                job['job_type'] = 'Not specified'
            
            # Look for salary
            salary_patterns = [
                r'Salary:\s*([^\n\r]+)',
                r'Pay:\s*([^\n\r]+)',
                r'(?:Rs\.?|NRS|NPR)\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|K|thousand|lakh)?(?:\s*-\s*(?:Rs\.?|NRS|NPR)?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|K|thousand|lakh)?)?'
            ]
            
            job['salary'] = 'Not specified'
            for pattern in salary_patterns:
                match = re.search(pattern, element_text, re.IGNORECASE)
                if match:
                    job['salary'] = match.group(0)
                    break
            
            # Add metadata
            job['source'] = self.name
            job['source_url'] = self.source_url
            from datetime import datetime
            job['scraped_date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Clean up title
            job['title'] = re.sub(r'\s+', ' ', job['title']).strip()
            
            return job
            
        except Exception as e:
            self.logger.warning(f"Error extracting job from element: {e}")
            return None
    
    def _remove_duplicates(self, jobs):
        """Remove duplicate jobs"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = (job.get('title', '').lower().strip(), job.get('company', '').lower().strip())
            if key not in seen and key[0]:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs

def main():
    """Test the scraper"""
    scraper = KumariJobScraper()
    jobs = scraper.scrape_jobs(max_pages=3)
    
    print(f"\n=== KumariJob Scraper Results ===")
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