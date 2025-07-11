"""
Sample test script for Nepal Job Scraper.

This demonstrates how to create and test scraping logic
before finalizing scripts. Scripts in this folder can be
created and destroyed as needed for experimentation.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time


def test_merojob_structure():
    """Test the structure of Merojob website to understand selectors."""
    print("Testing Merojob structure...")
    
    base_url = "https://merojob.com"
    search_url = "https://merojob.com/search/"
    
    try:
        # Test with a simple request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"✅ Successfully connected to {search_url}")
        print(f"Page title: {soup.title.get_text() if soup.title else 'No title'}")
        
        # Look for common job listing patterns
        potential_selectors = [
            '.job-list',
            '.job-item',
            '.job-card',
            '.job-listing',
            '[class*="job"]',
            '.list-group-item',
            '.card'
        ]
        
        print("\nLooking for job listing containers:")
        for selector in potential_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"  Found {len(elements)} elements with selector: {selector}")
        
        # Look for pagination
        pagination_selectors = [
            '.pagination',
            '.page-numbers',
            '[class*="page"]',
            '.next',
            '.previous'
        ]
        
        print("\nLooking for pagination:")
        for selector in pagination_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"  Found {len(elements)} elements with selector: {selector}")
        
        # Save the HTML for manual inspection
        with open('test/merojob_sample.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("\n💾 Saved HTML structure to test/merojob_sample.html")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to {search_url}: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def test_job_detail_page():
    """Test scraping a single job detail page."""
    print("\nTesting job detail page structure...")
    
    # This would be a real job URL - replace with actual URL when testing
    test_url = "https://merojob.com/job/sample-job-posting"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(test_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for common job detail patterns
        detail_selectors = {
            'title': ['h1', '.job-title', '[class*="title"]'],
            'company': ['.company', '.company-name', '[class*="company"]'],
            'location': ['.location', '.job-location', '[class*="location"]'],
            'description': ['.description', '.job-description', '.content'],
            'salary': ['.salary', '.salary-range', '[class*="salary"]'],
            'deadline': ['.deadline', '.apply-by', '[class*="deadline"]']
        }
        
        print("Testing job detail selectors:")
        for field, selectors in detail_selectors.items():
            print(f"\n{field}:")
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"  ✅ {selector} -> {len(elements)} elements")
                    # Show first element text (truncated)
                    text = elements[0].get_text(strip=True)[:100]
                    print(f"     Preview: {text}...")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: Could not test job detail page: {e}")
        print("ℹ️  Replace test_url with a real job posting URL to test")


def test_robots_txt():
    """Check robots.txt for scraping guidelines."""
    print("\nChecking robots.txt...")
    
    websites = [
        "https://merojob.com",
        "https://jobaxle.com", 
        "https://froxjob.com",
        "https://ramrojob.com"
    ]
    
    for base_url in websites:
        try:
            robots_url = f"{base_url}/robots.txt"
            response = requests.get(robots_url, timeout=5)
            
            if response.status_code == 200:
                print(f"\n🤖 {base_url}/robots.txt:")
                lines = response.text.split('\n')[:10]  # First 10 lines
                for line in lines:
                    if line.strip():
                        print(f"  {line}")
                if len(response.text.split('\n')) > 10:
                    print("  ... (truncated)")
            else:
                print(f"⚠️  {base_url}: No robots.txt found")
                
        except Exception as e:
            print(f"❌ {base_url}: Error checking robots.txt: {e}")


def clean_test_files():
    """Clean up test files when done experimenting."""
    import os
    
    test_files = [
        'test/merojob_sample.html',
        'test/jobaxle_sample.html',
        'test/debug_output.json'
    ]
    
    print("\nCleaning up test files...")
    for file_path in test_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️  Removed {file_path}")
    
    print("✅ Test cleanup complete")


if __name__ == "__main__":
    print("🧪 Running sample tests for Nepal Job Scraper\n")
    
    # Run tests
    test_merojob_structure()
    test_job_detail_page()
    test_robots_txt()
    
    print("\n" + "="*50)
    print("🎯 Next Steps:")
    print("1. Examine the saved HTML files to understand structure")
    print("2. Update selectors in config/settings.py based on findings")
    print("3. Create actual scraper scripts using: python scraper_cli.py create-script <website>")
    print("4. Test scrapers with: python scraper_cli.py test-script <website>")
    print("5. Run cleanup when done: clean_test_files()")
    print("="*50) 