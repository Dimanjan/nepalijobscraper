#!/usr/bin/env python3
"""
KantipurJob Scraper - Extract jobs from kantipurjob.com
URL: https://kantipurjob.com
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, parse_qs, urlparse
from utils import BaseScraper

class KantipurJobScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            website_name="kantipurjob",
            base_url="https://kantipurjob.com",
            delay=1.5
        )
        self.name = "KantipurJob"
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
        Scrape jobs from KantipurJob
        """
        all_jobs = []
        
        try:
            # Get job categories first
            categories = self._get_job_categories()
            self.logger.info(f"Found {len(categories)} job categories")
            
            if not categories:
                # Fallback to main page scraping
                main_jobs = self._scrape_main_page()
                all_jobs.extend(main_jobs)
            else:
                # Scrape jobs from each category
                for category in categories[:10]:  # Limit to prevent too many requests
                    try:
                        self.logger.info(f"Scraping category: {category['name']}")
                        category_jobs = self._scrape_category(category)
                        all_jobs.extend(category_jobs)
                        time.sleep(self.delay)
                    except Exception as e:
                        self.logger.warning(f"Error scraping category {category['name']}: {e}")
                        continue
            
            # Remove duplicates
            unique_jobs = self._remove_duplicates(all_jobs)
            
            self.logger.info(f"Successfully scraped {len(unique_jobs)} unique jobs from {self.name}")
            return unique_jobs
            
        except Exception as e:
            self.logger.error(f"Error in scraping {self.name}: {e}")
            return []
    
    def _get_job_categories(self):
        """Get job categories from the main page"""
        categories = []
        
        try:
            response = self.make_request(self.base_url)
            if not response:
                return categories
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for category links with job counts
            category_links = soup.find_all('a', href=True)
            
            for link in category_links:
                text = link.get_text().strip()
                href = link.get('href', '')
                
                # Look for patterns like "Category Name (5)" indicating job count
                if '(' in text and ')' in text and any(char.isdigit() for char in text):
                    # Extract category name and count
                    match = re.match(r'^(.+?)\s*\((\d+)\)$', text)
                    if match:
                        category_name = match.group(1).strip()
                        job_count = int(match.group(2))
                        
                        if job_count > 0:  # Only include categories with jobs
                            categories.append({
                                'name': category_name,
                                'url': urljoin(self.base_url, href),
                                'count': job_count
                            })
            
            # Sort by job count (highest first)
            categories.sort(key=lambda x: x['count'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error getting job categories: {e}")
        
        return categories
    
    def _scrape_main_page(self):
        """Scrape jobs from the main page"""
        jobs = []
        
        try:
            response = self.make_request(self.base_url)
            if not response:
                return jobs
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for job listings
            job_elements = soup.select('.job-item, .job-card, .vacancy, .position, .job-listing')
            
            if not job_elements:
                # Try to find any elements that might contain job information
                job_elements = soup.find_all(['div', 'li'], class_=lambda x: x and any(word in x.lower() for word in ['job', 'vacancy', 'position']))
            
            self.logger.info(f"Found {len(job_elements)} potential job elements on main page")
            
            for element in job_elements:
                job = self._extract_job_from_element(element)
                if job:
                    jobs.append(job)
            
        except Exception as e:
            self.logger.error(f"Error scraping main page: {e}")
        
        return jobs
    
    def _scrape_category(self, category):
        """Scrape jobs from a specific category"""
        jobs = []
        
        try:
            response = self.make_request(category['url'])
            if not response:
                return jobs
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for job listings in category page
            job_elements = soup.select('.job-item, .job-card, .vacancy, .position, .job-listing, .job')
            
            if not job_elements:
                # Try alternative selectors
                job_elements = soup.find_all(['div', 'li', 'tr'], class_=lambda x: x and any(word in x.lower() for word in ['job', 'vacancy', 'position']))
            
            self.logger.info(f"Found {len(job_elements)} job elements in category {category['name']}")
            
            for element in job_elements:
                job = self._extract_job_from_element(element)
                if job:
                    job['category'] = category['name']
                    jobs.append(job)
            
        except Exception as e:
            self.logger.error(f"Error scraping category {category['name']}: {e}")
        
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
            
            # Skip if title is too generic or short
            if (not job.get('title') or 
                len(job['title']) < 3 or 
                job['title'].lower() in ['job', 'vacancy', 'position', 'career', 'apply']):
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
                    if (any(word in text.lower() for word in ['pvt', 'ltd', 'company', 'corp', 'inc', 'organization', 'institute']) and 
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
            
            # If no explicit location, look for location keywords
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
                r'(?:Rs\.?|NRS|NPR)?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|K|thousand|lakh)?(?:\s*-\s*(?:Rs\.?|NRS|NPR)?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|K|thousand|lakh)?)?'
            ]
            
            job['salary'] = 'Not specified'
            for pattern in salary_patterns:
                match = re.search(pattern, element_text, re.IGNORECASE)
                if match:
                    job['salary'] = match.group(0) if 'Salary:' in match.group(0) else match.group(0)
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
    scraper = KantipurJobScraper()
    jobs = scraper.scrape_jobs(max_pages=3)
    
    print(f"\n=== KantipurJob Scraper Results ===")
    print(f"Total jobs found: {len(jobs)}")
    
    if jobs:
        print("\nSample jobs:")
        for i, job in enumerate(jobs[:5]):
            print(f"\n{i+1}. {job.get('title', 'N/A')}")
            print(f"   Company: {job.get('company', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Category: {job.get('category', 'N/A')}")
            print(f"   URL: {job.get('job_url', 'N/A')}")
    
    return jobs

if __name__ == "__main__":
    main() 