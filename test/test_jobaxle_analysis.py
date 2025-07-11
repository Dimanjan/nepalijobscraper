"""
Test script to analyze JobAxle website structure.

This script helps understand the HTML structure and identify
the correct CSS selectors for scraping job data.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json


def analyze_jobaxle_structure():
    """Analyze the structure of JobAxle website."""
    print("🔍 Analyzing JobAxle structure...")
    
    base_url = "https://jobaxle.com"
    search_url = "https://jobaxle.com/jobs"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"✅ Successfully connected to {search_url}")
        print(f"Page title: {soup.title.get_text() if soup.title else 'No title'}")
        
        # Look for job listing patterns
        potential_job_selectors = [
            '.job-card',
            '.job-item',
            '.job-listing',
            '.job',
            '[class*="job"]',
            '.card',
            '.list-group-item',
            '.vacancy',
            '.position'
        ]
        
        print("\n📋 Looking for job listing containers:")
        found_job_selectors = []
        for selector in potential_job_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"  ✅ Found {len(elements)} elements with selector: {selector}")
                found_job_selectors.append(selector)
                
                # Show first element structure
                if len(elements) > 0:
                    first_element = elements[0]
                    print(f"     Sample structure: {str(first_element)[:200]}...")
        
        # Look for job links
        potential_link_selectors = [
            'a[href*="job"]',
            'a[href*="vacancy"]',
            'a[href*="position"]',
            '.job-title a',
            '.title a',
            'h1 a',
            'h2 a',
            'h3 a'
        ]
        
        print("\n🔗 Looking for job link patterns:")
        found_links = []
        for selector in potential_link_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"  ✅ Found {len(elements)} links with selector: {selector}")
                for i, element in enumerate(elements[:3]):  # Show first 3
                    href = element.get('href')
                    title = element.get_text(strip=True)
                    if href:
                        full_url = urljoin(base_url, href)
                        found_links.append(full_url)
                        print(f"     Link {i+1}: {title[:50]}... -> {full_url}")
        
        # Look for pagination
        pagination_selectors = [
            '.pagination',
            '.page-numbers',
            '[class*="page"]',
            '.next',
            '.previous',
            '.pager'
        ]
        
        print("\n📄 Looking for pagination:")
        for selector in pagination_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"  ✅ Found {len(elements)} elements with selector: {selector}")
        
        # Save HTML for manual inspection
        with open('test/jobaxle_sample.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"\n💾 Saved HTML structure to test/jobaxle_sample.html")
        
        # Test a job detail page if we found links
        if found_links:
            print(f"\n🔍 Testing job detail page: {found_links[0]}")
            test_job_detail_page(found_links[0])
        
        return found_job_selectors, found_links
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to {search_url}: {e}")
        return [], []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return [], []


def test_job_detail_page(job_url):
    """Test scraping a job detail page."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(job_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for common job detail patterns
        detail_selectors = {
            'title': ['h1', '.job-title', '.title', '[class*="title"]'],
            'company': ['.company', '.company-name', '[class*="company"]', '.employer'],
            'location': ['.location', '.job-location', '[class*="location"]', '.address'],
            'description': ['.description', '.job-description', '.content', '.details'],
            'salary': ['.salary', '.salary-range', '[class*="salary"]', '.pay'],
            'deadline': ['.deadline', '.apply-by', '[class*="deadline"]', '.expiry']
        }
        
        print("  📝 Testing job detail selectors:")
        job_data = {}
        for field, selectors in detail_selectors.items():
            print(f"\n  {field.upper()}:")
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    text = elements[0].get_text(strip=True)[:100]
                    print(f"    ✅ {selector} -> {text}...")
                    if field not in job_data:
                        job_data[field] = {
                            'selector': selector,
                            'text': text
                        }
        
        # Save sample job data
        with open('test/jobaxle_job_sample.json', 'w', encoding='utf-8') as f:
            json.dump(job_data, f, indent=2)
        print(f"\n  💾 Saved job detail sample to test/jobaxle_job_sample.json")
        
    except Exception as e:
        print(f"  ❌ Error testing job detail page: {e}")


def main():
    print("🧪 Analyzing JobAxle Website Structure\n")
    
    job_selectors, job_links = analyze_jobaxle_structure()
    
    print("\n" + "="*60)
    print("📊 ANALYSIS SUMMARY")
    print("="*60)
    
    if job_selectors:
        print(f"✅ Found job listing selectors: {job_selectors}")
    else:
        print("❌ No job listing selectors found")
    
    if job_links:
        print(f"✅ Found {len(job_links)} job links")
    else:
        print("❌ No job links found")
    
    print("\n🎯 Next Steps:")
    print("1. Examine saved HTML files to understand structure")
    print("2. Update selectors in config/settings.py for jobaxle")
    print("3. Test updated selectors")
    print("4. Run production scraper")
    print("="*60)


if __name__ == "__main__":
    main() 