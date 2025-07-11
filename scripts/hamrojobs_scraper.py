"""
Scraper for HamroJobs (hamrojobs)

Auto-generated scraper template. Customize the selectors and logic
based on the actual website structure.
"""

import re
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from utils import BaseScraper


class HamroJobsScraper(BaseScraper):
    """Scraper for HamroJobs job website."""
    
    def __init__(self):
        super().__init__(
            website_name="hamrojobs",
            base_url="https://hamrojobs.com.np",
            delay=1.5
        )
        
        self.search_url = "https://hamrojobs.com.np"
        self.selectors = {
            "job_links": "a[href*='jobpost']",
            "job_containers": "[class*='job']",
            "pagination": ".pagination",
            "job_title": "h1, .job-title, .title",
            "company": ".company-name, .company",
            "location": ".location, .address",
            "description": ".description, .content, .job-description",
            "salary": ".salary, .pay",
            "deadline": ".deadline, .expiry",
            "posted_date": ".date, .posted"
}
        
    def get_job_links(self, page: int = 1) -> List[str]:
        """Get job links from a search results page."""
        # Construct search URL for the page
        search_url = f"{self.search_url}?page={page}"
        
        try:
            response = self.make_request(search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job links using configured selector
            job_elements = soup.select(self.selectors['job_links'])
            
            job_links = []
            for element in job_elements:
                href = element.get('href')
                if href:
                    # Convert relative URLs to absolute
                    job_url = urljoin(self.base_url, href)
                    job_links.append(job_url)
            
            self.logger.debug(f"Found {len(job_links)} jobs on page {page}")
            return job_links
            
        except Exception as e:
            self.logger.error(f"Error getting job links from page {page}: {str(e)}")
            return []
    
    def scrape_job_details(self, job_url: str) -> Dict[str, Any]:
        """Scrape detailed information from a job posting."""
        try:
            response = self.make_request(job_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_data = {'url': job_url}
            
            # Extract job title
            title_element = soup.select_one(self.selectors['job_title'])
            job_data['title'] = title_element.get_text(strip=True) if title_element else ''
            
            # Extract company name
            company_element = soup.select_one(self.selectors['company'])
            job_data['company'] = company_element.get_text(strip=True) if company_element else ''
            
            # Extract location
            location_element = soup.select_one(self.selectors['location'])
            job_data['location'] = location_element.get_text(strip=True) if location_element else ''
            
            # Extract description
            desc_element = soup.select_one(self.selectors['description'])
            job_data['description'] = desc_element.get_text(strip=True) if desc_element else ''
            
            # Extract salary (if available)
            salary_element = soup.select_one(self.selectors['salary'])
            if salary_element:
                salary_text = salary_element.get_text(strip=True)
                job_data['salary'] = salary_text
                # TODO: Parse salary range into min/max values
            
            # Extract deadline
            deadline_element = soup.select_one(self.selectors['deadline'])
            job_data['deadline'] = deadline_element.get_text(strip=True) if deadline_element else ''
            
            # Extract posted date
            posted_element = soup.select_one(self.selectors['posted_date'])
            job_data['posted_date'] = posted_element.get_text(strip=True) if posted_element else ''
            
            # TODO: Add more fields as needed
            # - job_type
            # - experience_required
            # - education_required
            # - requirements
            # - benefits
            # - contact_info
            
            return job_data
            
        except Exception as e:
            self.logger.error(f"Error scraping job details from {job_url}: {str(e)}")
            return {'url': job_url, 'error': str(e)}
    
    def get_total_pages(self) -> int:
        """Get the total number of pages available."""
        try:
            response = self.make_request(self.search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find pagination elements
            pagination_elements = soup.select(self.selectors['pagination'])
            
            if not pagination_elements:
                return 1
            
            # Extract page numbers and find the maximum
            page_numbers = []
            for element in pagination_elements:
                text = element.get_text(strip=True)
                if text.isdigit():
                    page_numbers.append(int(text))
            
            return max(page_numbers) if page_numbers else 1
            
        except Exception as e:
            self.logger.error(f"Error getting total pages: {str(e)}")
            return 1


def main():
    """Main function for testing the scraper."""
    scraper = HamroJobsScraper()
    
    # Test with first page only
    jobs = scraper.scrape_all(max_pages=1)
    print(f"Scraped {len(jobs)} jobs from {scraper.website_name}")


if __name__ == "__main__":
    main()
