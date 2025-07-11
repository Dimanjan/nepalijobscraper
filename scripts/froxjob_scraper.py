"""
Scraper for Froxjob (froxjob)

Auto-generated scraper template. Customize the selectors and logic
based on the actual website structure.
"""

import re
import json
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from utils import BaseScraper


class FroxjobScraper(BaseScraper):
    """Scraper for Froxjob job website."""
    
    def __init__(self):
        super().__init__(
            website_name="froxjob",
            base_url="https://froxjob.com",
            delay=1.2
        )
        
        self.search_url = "https://froxjob.com"
        self.selectors = {
            "job_links": ".joblist li a",
            "company_cards": ".job-wrapper",
            "company_name": ".media-heading",
            "pagination": ".pagination",
            "job_title": "h1, .job-title",
            "company": ".company-name, .company",
            "location": ".location, .address",
            "description": ".description, .content, .job-content",
            "salary": ".salary, .salary-range",
            "deadline": ".deadline, .apply-deadline",
            "posted_date": ".date, .posted-date"
}
        
    def get_job_links(self, page: int = 1) -> List[str]:
        """Get job links from Froxjob main page (no pagination)."""
        # Froxjob shows all jobs on the main page
        if page > 1:
            return []  # No pagination, return empty for pages > 1
        
        try:
            response = self.make_request(self.search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job links using configured selector
            job_elements = soup.select(self.selectors['job_links'])
            
            job_links = []
            company_data = {}
            
            # Also extract company information for each job
            company_cards = soup.select(self.selectors['company_cards'])
            
            for card in company_cards:
                # Extract company name
                company_name_element = card.select_one(self.selectors['company_name'])
                company_name = company_name_element.get_text(strip=True) if company_name_element else 'Unknown Company'
                
                # Find all job links within this company card
                job_links_in_card = card.select(self.selectors['job_links'])
                
                for link in job_links_in_card:
                    href = link.get('href')
                    if href:
                        # Convert relative URLs to absolute
                        job_url = urljoin(self.base_url, href)
                        job_links.append(job_url)
                        
                        # Store company data for later use
                        company_data[job_url] = {
                            'company_name': company_name,
                            'job_title': link.get_text(strip=True)
                        }
            
            # Store company data for use in scrape_job_details
            self._company_data = company_data
            
            self.logger.debug(f"Found {len(job_links)} jobs from {len(company_cards)} companies")
            return job_links
            
        except Exception as e:
            self.logger.error(f"Error getting job links: {str(e)}")
            return []
    
    def scrape_job_details(self, job_url: str) -> Dict[str, Any]:
        """Scrape detailed information from a Froxjob posting."""
        try:
            # Start with stored company data if available
            job_data = {'url': job_url}
            
            if hasattr(self, '_company_data') and job_url in self._company_data:
                stored_data = self._company_data[job_url]
                job_data['title'] = stored_data['job_title']
                job_data['company'] = stored_data['company_name']
            
            # Get detailed information from job detail page
            response = self.make_request(job_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract or update job title
            title_element = soup.select_one(self.selectors['job_title'])
            if title_element:
                job_data['title'] = title_element.get_text(strip=True)
            
            # Extract or update company name
            company_element = soup.select_one(self.selectors['company'])
            if company_element:
                job_data['company'] = company_element.get_text(strip=True)
            
            # Extract location
            location_element = soup.select_one(self.selectors['location'])
            job_data['location'] = location_element.get_text(strip=True) if location_element else ''
            
            # Extract description
            desc_element = soup.select_one(self.selectors['description'])
            job_data['description'] = desc_element.get_text(strip=True) if desc_element else ''
            
            # Extract salary
            salary_element = soup.select_one(self.selectors['salary'])
            if salary_element:
                job_data['salary'] = salary_element.get_text(strip=True)
            else:
                job_data['salary'] = ''
            
            # Extract deadline
            deadline_element = soup.select_one(self.selectors['deadline'])
            job_data['deadline'] = deadline_element.get_text(strip=True) if deadline_element else ''
            
            # Extract posted date
            posted_element = soup.select_one(self.selectors['posted_date'])
            job_data['posted_date'] = posted_element.get_text(strip=True) if posted_element else ''
            
            # Extract enhanced contact information
            contact_email_element = soup.select_one('a[href^="mailto:"]')
            if contact_email_element:
                job_data['contact_email'] = contact_email_element.get('href', '').replace('mailto:', '')
            else:
                job_data['contact_email'] = ''
            
            contact_phone_element = soup.select_one('a[href^="tel:"]')
            if contact_phone_element:
                job_data['contact_phone'] = contact_phone_element.get('href', '').replace('tel:', '')
            else:
                job_data['contact_phone'] = ''
            
            # Extract apply URL
            apply_element = soup.select_one('a[href*="apply"], .apply-button, .apply-link')
            if apply_element:
                job_data['apply_url'] = apply_element.get('href', '')
            else:
                job_data['apply_url'] = ''
            
            # Try to extract JSON-LD structured data for enhanced information
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'JobPosting':
                        # Extract structured job data
                        if data.get('title') and not job_data.get('title'):
                            job_data['title'] = data['title']
                        if data.get('hiringOrganization', {}).get('name') and not job_data.get('company'):
                            job_data['company'] = data['hiringOrganization']['name']
                        if data.get('jobLocation', {}).get('address'):
                            job_data['location'] = str(data['jobLocation']['address'])
                        if data.get('baseSalary', {}).get('value'):
                            job_data['salary'] = str(data['baseSalary']['value'])
                        if data.get('datePosted'):
                            job_data['posted_date'] = data['datePosted']
                        if data.get('validThrough'):
                            job_data['deadline'] = data['validThrough']
                        if data.get('description'):
                            job_data['description'] = data['description']
                        if data.get('qualifications'):
                            job_data['requirements'] = data['qualifications']
                        if data.get('benefits'):
                            job_data['benefits'] = data['benefits']
                        if data.get('experienceRequirements'):
                            job_data['experience_required'] = data['experienceRequirements']
                        if data.get('educationRequirements'):
                            job_data['education_required'] = data['educationRequirements']
                        break
                except:
                    continue
            
            # Try to extract additional details commonly found on job pages
            # Look for requirements, qualifications, etc.
            requirements_element = soup.select_one('.requirements, .qualifications, .job-requirements')
            if requirements_element and not job_data.get('requirements'):
                job_data['requirements'] = requirements_element.get_text(strip=True)
            elif not job_data.get('requirements'):
                job_data['requirements'] = ''
            
            # Look for benefits
            benefits_element = soup.select_one('.benefits, .job-benefits, .perks')
            if benefits_element and not job_data.get('benefits'):
                job_data['benefits'] = benefits_element.get_text(strip=True)
            elif not job_data.get('benefits'):
                job_data['benefits'] = ''
            
            # Extract experience level if available
            experience_element = soup.select_one('.experience, .experience-level, .job-experience')
            if experience_element and not job_data.get('experience_required'):
                job_data['experience_required'] = experience_element.get_text(strip=True)
            elif not job_data.get('experience_required'):
                job_data['experience_required'] = ''
            
            # Extract education requirements if available
            education_element = soup.select_one('.education, .qualification, .job-education')
            if education_element and not job_data.get('education_required'):
                job_data['education_required'] = education_element.get_text(strip=True)
            elif not job_data.get('education_required'):
                job_data['education_required'] = ''
            
            return job_data
            
        except Exception as e:
            self.logger.error(f"Error scraping job details from {job_url}: {str(e)}")
            return {'url': job_url, 'error': str(e)}
    
    def get_total_pages(self) -> int:
        """Get the total number of pages available."""
        # Froxjob shows all jobs on one page, so always return 1
        return 1


def main():
    """Main function for testing the scraper."""
    scraper = FroxjobScraper()
    
    # Test with multiple pages
    jobs = scraper.scrape_all(max_pages=10)
    print(f"Scraped {len(jobs)} jobs from {scraper.website_name}")


if __name__ == "__main__":
    main()
