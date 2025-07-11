"""
Scraper for Merojob (merojob)

Auto-generated scraper template. Customize the selectors and logic
based on the actual website structure.
"""

import re
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from utils import BaseScraper


class MerojobScraper(BaseScraper):
    """Scraper for Merojob job website."""
    
    def __init__(self):
        super().__init__(
            website_name="merojob",
            base_url="https://merojob.com",
            delay=1.5
        )
        
        self.search_url = "https://merojob.com/search/"
        self.selectors = {
            "job_links": ".job-card h1.text-primary a",
            "pagination": ".pagination a",
            "job_title": "h1[itemprop='title']",
            "company": ".text-dark",
            "location": "[itemprop='addressLocality']",
            "description": "[itemprop='description']",
            "salary": ".salary-info",
            "deadline": ".card-footer .text-primary",
            "posted_date": "[itemprop='datePosted']",
            "skills": "[itemprop='skills'] .badge",
            "employment_type": "[itemprop='employmentType']"
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
            if title_element:
                # Remove extra content and clean title
                title_text = title_element.get_text(strip=True)
                job_data['title'] = title_text
            else:
                # Fallback to h1 with text-primary class
                title_element = soup.select_one('h1.text-primary')
                job_data['title'] = title_element.get_text(strip=True) if title_element else ''
            
            # Extract company name - try multiple selectors
            company_element = soup.select_one('.text-dark')
            if not company_element:
                company_element = soup.select_one('[itemprop="hiringOrganization"] [itemprop="name"]')
            if company_element:
                job_data['company'] = company_element.get_text(strip=True)
            else:
                job_data['company'] = ''
            
            # Extract location
            location_element = soup.select_one(self.selectors['location'])
            job_data['location'] = location_element.get_text(strip=True) if location_element else ''
            
            # Extract description
            desc_element = soup.select_one(self.selectors['description'])
            if desc_element:
                job_data['description'] = desc_element.get('content', desc_element.get_text(strip=True))
            else:
                job_data['description'] = ''
            
            # Extract employment type
            employment_element = soup.select_one(self.selectors['employment_type'])
            if employment_element:
                job_data['job_type'] = employment_element.get('content', employment_element.get_text(strip=True))
            else:
                job_data['job_type'] = ''
            
            # Extract skills
            skill_elements = soup.select(self.selectors['skills'])
            skills = [skill.get_text(strip=True) for skill in skill_elements]
            job_data['skills'] = ', '.join(skills) if skills else ''
            
            # Extract salary (if available)
            salary_element = soup.select_one(self.selectors['salary'])
            if salary_element:
                salary_text = salary_element.get_text(strip=True)
                job_data['salary'] = salary_text
            else:
                job_data['salary'] = ''
            
            # Extract deadline - clean up the text
            deadline_element = soup.select_one(self.selectors['deadline'])
            if deadline_element:
                deadline_text = deadline_element.get_text(strip=True)
                # Extract just the date part
                if 'Apply Before:' in deadline_text:
                    deadline_text = deadline_text.replace('Apply Before:', '').strip()
                job_data['deadline'] = deadline_text
            else:
                job_data['deadline'] = ''
            
            # Extract posted date
            posted_element = soup.select_one(self.selectors['posted_date'])
            if posted_element:
                posted_date = posted_element.get('content', posted_element.get_text(strip=True))
                job_data['posted_date'] = posted_date
            else:
                job_data['posted_date'] = ''
            
            # Try to extract additional information from job detail page
            # Look for job requirements, qualifications, etc.
            requirements_element = soup.select_one('.job-requirement, .requirements, .qualification')
            if requirements_element:
                job_data['requirements'] = requirements_element.get_text(strip=True)
            else:
                job_data['requirements'] = ''
            
            # Extract contact information if available
            contact_element = soup.select_one('.contact-info, .contact')
            if contact_element:
                job_data['contact_info'] = contact_element.get_text(strip=True)
            else:
                job_data['contact_info'] = ''
            
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
    scraper = MerojobScraper()
    
    # Scrape more pages to collect more job data
    jobs = scraper.scrape_all(max_pages=10)
    print(f"Scraped {len(jobs)} jobs from {scraper.website_name}")


if __name__ == "__main__":
    main()
