"""
Scraper for JobAxle (jobaxle)

Uses JobAxle's API endpoints for efficient job data extraction.
JobAxle provides JSON APIs that are much more reliable than HTML scraping.
"""

import re
import json
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
from datetime import datetime

from utils import BaseScraper


class JobAxleScraper(BaseScraper):
    """Scraper for JobAxle job website using API endpoints."""
    
    def __init__(self):
        super().__init__(
            website_name="jobaxle",
            base_url="https://jobaxle.com",
            delay=1.0
        )
        
        # API endpoints
        self.search_api_url = "https://jobaxle.com/api/search"
        self.job_detail_api_url = "https://jobaxle.com/api/jobs"
        
        # Update headers for API requests
        self.session.headers.update({
            'Accept': 'application/json',
            'Referer': 'https://jobaxle.com/search'
        })
        
    def get_job_links(self, page: int = 1) -> List[str]:
        """Get job data from JobAxle's API for a specific page."""
        params = {'page': page}
        
        try:
            response = self.make_request(self.search_api_url, params=params)
            data = response.json()
            
            if not data.get('success') or data.get('status') != 200:
                self.logger.warning(f"API returned error: {data.get('message', 'Unknown error')}")
                return []
            
            jobs_data = data.get('data', {}).get('rows', [])
            
            # Instead of returning URLs, we'll return job IDs that can be used for detailed scraping
            job_ids = [job.get('id') for job in jobs_data if job.get('id')]
            
            self.logger.debug(f"Found {len(job_ids)} jobs on page {page}")
            
            # Store the job data for later use in scrape_job_details
            if not hasattr(self, '_page_job_data'):
                self._page_job_data = {}
            self._page_job_data[page] = jobs_data
            
            # Return job URLs for compatibility with base class
            job_urls = []
            for job in jobs_data:
                if job.get('slug'):
                    job_url = f"https://jobaxle.com/jobs/{job['slug']}"
                    job_urls.append(job_url)
            
            return job_urls
            
        except Exception as e:
            self.logger.error(f"Error getting jobs from API page {page}: {str(e)}")
            return []
    
    def scrape_job_details(self, job_url: str) -> Dict[str, Any]:
        """Extract job details using JobAxle's API and stored job data."""
        try:
            # Extract job ID or slug from URL
            job_slug = job_url.split('/')[-1] if job_url else ''
            
            # First, try to find job data from our stored page data
            job_data = None
            if hasattr(self, '_page_job_data'):
                for page_data in self._page_job_data.values():
                    for job in page_data:
                        if job.get('slug') == job_slug:
                            job_data = job
                            break
                    if job_data:
                        break
            
            if not job_data:
                self.logger.warning(f"Could not find job data for {job_url}")
                return {'url': job_url, 'error': 'Job data not found'}
            
            # Extract job information from API data
            result = {'url': job_url}
            
            # Basic job information
            result['title'] = job_data.get('jobTitle', '').strip()
            result['job_type'] = job_data.get('workNature', '')  # on-site, remote, hybrid
            result['posted_date'] = job_data.get('createdAt', '')
            result['deadline'] = job_data.get('deadlineEndDate', '')
            
            # Company information
            member = job_data.get('member', {})
            result['company'] = member.get('fullName', '') if member else ''
            
            # Try to get additional details from job detail API
            job_id = job_data.get('id')
            if job_id:
                try:
                    detail_url = f"{self.job_detail_api_url}/{job_id}"
                    detail_response = self.make_request(detail_url)
                    detail_data = detail_response.json()
                    
                    if detail_data.get('success') and detail_data.get('data'):
                        job_detail = detail_data['data']
                        
                        # Extract additional details
                        result['description'] = job_detail.get('description', '')
                        result['location'] = job_detail.get('location', '')
                        result['salary'] = job_detail.get('salaryRange', '')
                        result['experience_required'] = job_detail.get('experience', '')
                        result['education_required'] = job_detail.get('education', '')
                        result['requirements'] = job_detail.get('requirements', '')
                        result['benefits'] = job_detail.get('benefits', '')
                        result['skills'] = job_detail.get('skills', '')
                        
                        # Job category and industry
                        if 'jobCategory' in job_detail:
                            category = job_detail['jobCategory']
                            result['job_category'] = category.get('categoryName', '') if category else ''
                        
                        # Employment details
                        result['employment_type'] = job_detail.get('employmentType', '')
                        result['job_level'] = job_detail.get('jobLevel', '')
                        
                except Exception as e:
                    self.logger.warning(f"Could not fetch detailed job info for {job_id}: {str(e)}")
            
            # Format dates
            for date_field in ['posted_date', 'deadline']:
                if result.get(date_field):
                    try:
                        # Parse ISO date and format it nicely
                        date_obj = datetime.fromisoformat(result[date_field].replace('Z', '+00:00'))
                        result[date_field] = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass  # Keep original format if parsing fails
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error scraping job details from {job_url}: {str(e)}")
            return {'url': job_url, 'error': str(e)}
    
    def get_total_pages(self) -> int:
        """Get the total number of pages available from JobAxle API."""
        try:
            # Test multiple pages to find the limit
            # JobAxle API seems to return 10 jobs per page
            page = 1
            max_pages = 1
            
            while page <= 50:  # Safety limit
                params = {'page': page}
                response = self.make_request(self.search_api_url, params=params)
                data = response.json()
                
                if not data.get('success') or data.get('status') != 200:
                    break
                
                jobs = data.get('data', {}).get('rows', [])
                if not jobs:  # No more jobs on this page
                    break
                
                max_pages = page
                page += 1
                
                # If we get less than 10 jobs, this is likely the last page
                if len(jobs) < 10:
                    break
            
            self.logger.debug(f"Found {max_pages} total pages")
            return max_pages
            
        except Exception as e:
            self.logger.error(f"Error getting total pages: {str(e)}")
            return 1


def main():
    """Main function for testing the scraper."""
    scraper = JobAxleScraper()
    
    # Scrape more pages to collect more job data
    jobs = scraper.scrape_all(max_pages=10)
    print(f"Scraped {len(jobs)} jobs from {scraper.website_name}")


if __name__ == "__main__":
    main()
