"""
Test script to analyze Merorojgari website structure.

Merorojgari appears to be another Nepal job portal.
This script will analyze their structure for potential scraping.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time


def analyze_merorojgari_structure():
    """Analyze Merorojgari website structure."""
    print("🔍 Analyzing Merorojgari structure...")
    
    base_url = "https://www.merorojgari.com"
    
    # Test different potential job listing URLs
    test_urls = [
        "https://www.merorojgari.com",
        "https://www.merorojgari.com/jobs",
        "https://www.merorojgari.com/job-search",
        "https://www.merorojgari.com/search",
        "https://www.merorojgari.com/latest-jobs",
        "https://www.merorojgari.com/browse-jobs",
        "https://www.merorojgari.com/job-listings"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    working_urls = []
    
    for test_url in test_urls:
        try:
            print(f"\n🧪 Testing: {test_url}")
            response = requests.get(test_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.title.get_text() if soup.title else 'No title'
                
                print(f"✅ Status: {response.status_code}")
                print(f"📄 Title: {title}")
                
                # Check if this looks like a job listing page
                job_indicators = ['job', 'vacancy', 'career', 'position', 'employment']
                content_text = soup.get_text().lower()
                
                job_count = sum(1 for indicator in job_indicators if indicator in content_text)
                print(f"🎯 Job relevance score: {job_count}/5")
                
                # Look for actual job listings on the page
                job_cards = soup.select('.job-card, .job-item, .job-listing, .job, .posting, .vacancy')
                if job_cards:
                    print(f"📋 Found {len(job_cards)} potential job cards")
                
                # Check for job links
                job_links = soup.select('a[href*="job"], a[href*="vacancy"], a[href*="position"]')
                if job_links:
                    print(f"🔗 Found {len(job_links)} potential job links")
                
                if job_count >= 2 or 'job' in title.lower() or job_cards or job_links:
                    working_urls.append((test_url, title))
                    print(f"✅ Looks like a job-related page!")
                    
                    # Save this page for analysis
                    filename = test_url.replace('https://www.merorojgari.com', '').replace('/', '_') or '_main'
                    with open(f'test/merorojgari{filename}.html', 'w', encoding='utf-8') as f:
                        f.write(soup.prettify())
                    print(f"💾 Saved to test/merorojgari{filename}.html")
                    
            else:
                print(f"❌ Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        time.sleep(1)  # Be respectful with requests
    
    return working_urls


def main():
    print("🧪 Analyzing Merorojgari Website Structure")
    print("🎯 Target: Nepal job portal\n")
    
    # Step 1: Find working URLs
    working_urls = analyze_merorojgari_structure()
    
    if not working_urls:
        print("\n❌ No working URLs found for Merorojgari")
        return
    
    print(f"\n✅ Found {len(working_urls)} working URLs:")
    for url, title in working_urls:
        print(f"   {url} -> {title}")
    
    print("\n🎯 Quick analysis shows potential for job scraping!")


if __name__ == "__main__":
    main() 