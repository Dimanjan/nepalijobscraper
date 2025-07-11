#!/usr/bin/env python3
"""
Nepal Job Scraper CLI

Command-line interface for managing job scraping operations,
testing scripts, and data management.
"""

import click
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from utils import DataManager, setup_logger
from config.settings import WEBSITE_CONFIGS, SCRAPING_PRIORITY


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, verbose):
    """Nepal Job Scraper - Manage job scraping operations."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    ctx.obj['logger'] = setup_logger("cli", log_level)


@cli.command()
@click.argument('website', required=False)
@click.option('--max-pages', '-p', type=int, help='Maximum pages to scrape')
@click.option('--test-mode', '-t', is_flag=True, help='Run in test mode (limited scraping)')
@click.pass_context
def scrape(ctx, website, max_pages, test_mode):
    """Start scraping jobs from specified website or all websites."""
    logger = ctx.obj['logger']
    
    if test_mode:
        max_pages = max_pages or 2
        logger.info("Running in test mode - limited to 2 pages per website")
    
    if website:
        if website not in WEBSITE_CONFIGS:
            logger.error(f"Unknown website: {website}")
            logger.info(f"Available websites: {', '.join(WEBSITE_CONFIGS.keys())}")
            return
        
        websites_to_scrape = [website]
    else:
        websites_to_scrape = SCRAPING_PRIORITY
    
    logger.info(f"Starting scrape for: {', '.join(websites_to_scrape)}")
    
    for site in websites_to_scrape:
        logger.info(f"Scraping {site}...")
        
        # Check if script exists
        script_path = Path(f"scripts/{site}_scraper.py")
        if not script_path.exists():
            logger.warning(f"No script found for {site} at {script_path}")
            logger.info(f"Create the script first with: python scraper_cli.py create-script {site}")
            continue
        
        # TODO: Import and run the actual scraper
        logger.info(f"Would run scraper for {site} (script execution not implemented yet)")


@cli.command()
@click.argument('website')
@click.pass_context
def create_script(ctx, website):
    """Create a new scraper script for a website."""
    logger = ctx.obj['logger']
    
    if website not in WEBSITE_CONFIGS:
        logger.error(f"Unknown website: {website}")
        logger.info(f"Available websites: {', '.join(WEBSITE_CONFIGS.keys())}")
        return
    
    config = WEBSITE_CONFIGS[website]
    script_path = Path(f"scripts/{website}_scraper.py")
    
    if script_path.exists():
        if not click.confirm(f"Script for {website} already exists. Overwrite?"):
            return
    
    # Generate script template
    template = generate_scraper_template(website, config)
    
    script_path.write_text(template, encoding='utf-8')
    logger.info(f"Created scraper script: {script_path}")
    
    # Update status
    update_website_status(website, "🔧", "Script template created")


@cli.command()
@click.argument('website')
@click.pass_context
def test_script(ctx, website):
    """Test a scraper script with limited pages."""
    logger = ctx.obj['logger']
    
    script_path = Path(f"scripts/{website}_scraper.py")
    if not script_path.exists():
        logger.error(f"No script found for {website}")
        return
    
    # Create a test version in test/ folder
    test_path = Path(f"test/test_{website}_scraper.py")
    
    # Copy script to test folder with modifications for testing
    script_content = script_path.read_text()
    test_content = script_content.replace(
        "max_pages: Optional[int] = None",
        "max_pages: Optional[int] = 2"
    )
    
    test_path.write_text(test_content, encoding='utf-8')
    logger.info(f"Created test script: {test_path}")
    logger.info("Run the test manually to verify functionality")


@cli.command()
@click.option('--website', '-w', help='Filter by website')
@click.option('--format', '-f', type=click.Choice(['json', 'csv']), default='json')
@click.pass_context
def export(ctx, website, format):
    """Export scraped data to specified format."""
    logger = ctx.obj['logger']
    data_manager = DataManager()
    
    try:
        if format == 'csv':
            file_path = data_manager.export_to_csv(website)
        else:
            file_path = data_manager.export_to_json(website)
        
        logger.info(f"Data exported to: {file_path}")
        
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")


@cli.command()
@click.pass_context
def stats(ctx):
    """Show statistics about scraped data."""
    logger = ctx.obj['logger']
    data_manager = DataManager()
    
    stats = data_manager.get_stats()
    
    logger.info("=== Scraping Statistics ===")
    logger.info(f"Total files: {stats['total_files']}")
    logger.info(f"Total jobs: {stats['total_jobs']}")
    
    if stats['websites']:
        logger.info("\nJobs by website:")
        for website, count in stats['websites'].items():
            logger.info(f"  {website}: {count}")
    
    if stats['date_range']['earliest']:
        logger.info(f"\nDate range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")


@cli.command()
@click.pass_context
def status(ctx):
    """Show status of all website scrapers."""
    logger = ctx.obj['logger']
    
    logger.info("=== Website Scraper Status ===")
    
    for website in WEBSITE_CONFIGS:
        script_path = Path(f"scripts/{website}_scraper.py")
        status_icon = "✅" if script_path.exists() else "❌"
        
        config = WEBSITE_CONFIGS[website]
        logger.info(f"{status_icon} {config['name']} ({website})")
        logger.info(f"    Script: {'exists' if script_path.exists() else 'missing'}")
        logger.info(f"    URL: {config['base_url']}")


@cli.command()
@click.pass_context
def clean(ctx):
    """Clean duplicate entries from scraped data."""
    logger = ctx.obj['logger']
    data_manager = DataManager()
    
    duplicates_removed = data_manager.clean_duplicates()
    logger.info(f"Removed {duplicates_removed} duplicate entries")


def generate_scraper_template(website: str, config: dict) -> str:
    """Generate a scraper script template for a website."""
    
    template = f'''"""
Scraper for {config['name']} ({website})

Auto-generated scraper template. Customize the selectors and logic
based on the actual website structure.
"""

import re
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from utils import BaseScraper


class {config['name'].replace(' ', '')}Scraper(BaseScraper):
    """Scraper for {config['name']} job website."""
    
    def __init__(self):
        super().__init__(
            website_name="{website}",
            base_url="{config['base_url']}",
            delay={config['delay']}
        )
        
        self.search_url = "{config['search_url']}"
        self.selectors = {json.dumps(config['selectors'], indent=12)}
        
    def get_job_links(self, page: int = 1) -> List[str]:
        """Get job links from a search results page."""
        # Construct search URL for the page
        search_url = f"{{self.search_url}}?page={{page}}"
        
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
            
            self.logger.debug(f"Found {{len(job_links)}} jobs on page {{page}}")
            return job_links
            
        except Exception as e:
            self.logger.error(f"Error getting job links from page {{page}}: {{str(e)}}")
            return []
    
    def scrape_job_details(self, job_url: str) -> Dict[str, Any]:
        """Scrape detailed information from a job posting."""
        try:
            response = self.make_request(job_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_data = {{'url': job_url}}
            
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
            self.logger.error(f"Error scraping job details from {{job_url}}: {{str(e)}}")
            return {{'url': job_url, 'error': str(e)}}
    
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
            self.logger.error(f"Error getting total pages: {{str(e)}}")
            return 1


def main():
    """Main function for testing the scraper."""
    scraper = {config['name'].replace(' ', '')}Scraper()
    
    # Test with first page only
    jobs = scraper.scrape_all(max_pages=1)
    print(f"Scraped {{len(jobs)}} jobs from {{scraper.website_name}}")


if __name__ == "__main__":
    main()
'''
    
    return template


def update_website_status(website: str, status: str, notes: str):
    """Update the status of a website in the tracking document."""
    status_file = Path("docs/website_status.md")
    
    if not status_file.exists():
        return
    
    content = status_file.read_text()
    
    # Update the status in the table
    # This is a simple implementation - could be improved with proper markdown parsing
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if f"| {website.title()}" in line or f"| {WEBSITE_CONFIGS[website]['name']}" in line:
            # Replace the status column
            parts = line.split('|')
            if len(parts) >= 4:
                parts[3] = f" {status} "
                parts[4] = f" {datetime.now().strftime('%Y-%m-%d')} "
                parts[5] = f" {notes} "
                lines[i] = '|'.join(parts)
            break
    
    # Write back to file
    status_file.write_text('\n'.join(lines))


if __name__ == "__main__":
    cli() 