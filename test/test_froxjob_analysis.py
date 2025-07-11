"""
Test script to analyze Froxjob website structure.

This script helps understand the HTML structure and identify
the correct CSS selectors for scraping job data from Froxjob.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time


def analyze_froxjob_structure():
    """Analyze the structure of Froxjob website."""
    print("🔍 Analyzing Froxjob structure...")
    
    base_url = "https://froxjob.com"
    
    # Test different potential job listing URLs
    test_urls = [
        "https://froxjob.com",
        "https://froxjob.com/jobs",
        "https://froxjob.com/job",
        "https://froxjob.com/vacancy",
        "https://froxjob.com/search",
        "https://froxjob.com/listings",
        "https://froxjob.com/careers"
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
                
                if job_count >= 2 or 'job' in title.lower():
                    working_urls.append((test_url, title))
                    print(f"✅ Looks like a job-related page!")
                    
                    # Save this page for analysis
                    filename = test_url.replace('https://froxjob.com', '').replace('/', '_') or '_main'
                    with open(f'test/froxjob{filename}.html', 'w', encoding='utf-8') as f:
                        f.write(soup.prettify())
                    print(f"💾 Saved to test/froxjob{filename}.html")
                    
            else:
                print(f"❌ Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        time.sleep(1)  # Be respectful with requests
    
    return working_urls


def analyze_job_patterns(url):
    """Analyze job listing patterns on a specific page."""
    print(f"\n🔍 Analyzing job patterns on: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for common job listing patterns
        job_selectors = [
            '.job-card', '.job-item', '.job-listing', '.job', '.job-post',
            '.vacancy', '.position', '.card', '.list-item', '.listing',
            '[class*="job"]', '[class*="vacancy"]', '[class*="position"]',
            '.post', '.entry', '.item'
        ]
        
        print("📋 Looking for job containers:")
        found_containers = []
        
        for selector in job_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"  ✅ Found {len(elements)} elements with: {selector}")
                found_containers.append((selector, len(elements)))
                
                # Show sample content from first element
                if len(elements) > 0:
                    sample_text = elements[0].get_text(strip=True)[:100]
                    print(f"     Sample: {sample_text}...")
        
        # Look for job links
        print("\n🔗 Looking for job links:")
        link_patterns = [
            'a[href*="job"]', 'a[href*="vacancy"]', 'a[href*="position"]',
            'a[href*="detail"]', 'a[href*="view"]', '.job-title a', '.title a'
        ]
        
        found_links = []
        for pattern in link_patterns:
            links = soup.select(pattern)
            if links:
                print(f"  ✅ Found {len(links)} links with: {pattern}")
                for i, link in enumerate(links[:3]):  # Show first 3
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    if href:
                        full_url = urljoin(url, href)
                        found_links.append(full_url)
                        print(f"     Link {i+1}: {text[:40]}... -> {full_url}")
        
        # Look for pagination
        print("\n📄 Looking for pagination:")
        pagination_patterns = [
            '.pagination', '.page-numbers', '.pager', '.page-nav',
            '[class*="page"]', '.next', '.prev', '.more'
        ]
        
        for pattern in pagination_patterns:
            elements = soup.select(pattern)
            if elements:
                print(f"  ✅ Found pagination with: {pattern}")
                
        return found_containers, found_links
        
    except Exception as e:
        print(f"❌ Error analyzing patterns: {e}")
        return [], []


def test_job_detail_page(job_urls):
    """Test a job detail page structure."""
    if not job_urls:
        print("\n⚠️  No job URLs to test")
        return
    
    print(f"\n🔍 Testing job detail page: {job_urls[0]}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(job_urls[0], headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for job detail patterns
        detail_patterns = {
            'title': ['h1', '.job-title', '.title', '.post-title', '[class*="title"]'],
            'company': ['.company', '.company-name', '.employer', '[class*="company"]'],
            'location': ['.location', '.address', '.job-location', '[class*="location"]'],
            'description': ['.description', '.content', '.job-description', '.job-content', '.details'],
            'salary': ['.salary', '.pay', '.wage', '[class*="salary"]'],
            'deadline': ['.deadline', '.expiry', '.apply-by', '[class*="deadline"]'],
            'posted_date': ['.date', '.posted', '.published', '[class*="date"]']
        }
        
        print("📝 Testing job detail selectors:")
        job_data = {}
        
        for field, selectors in detail_patterns.items():
            print(f"\n  {field.upper()}:")
            found = False
            for selector in selectors:
                elements = soup.select(selector)
                if elements and not found:
                    text = elements[0].get_text(strip=True)[:150]
                    print(f"    ✅ {selector} -> {text}...")
                    job_data[field] = {
                        'selector': selector,
                        'text': text
                    }
                    found = True
        
        # Save job detail sample
        with open('test/froxjob_job_detail.json', 'w', encoding='utf-8') as f:
            json.dump(job_data, f, indent=2)
        print(f"\n💾 Saved job detail analysis to test/froxjob_job_detail.json")
        
        # Save job detail HTML
        with open('test/froxjob_job_detail.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"💾 Saved job detail HTML to test/froxjob_job_detail.html")
        
    except Exception as e:
        print(f"❌ Error testing job detail: {e}")


def main():
    print("🧪 Analyzing Froxjob Website Structure\n")
    
    # Step 1: Find working URLs
    working_urls = analyze_froxjob_structure()
    
    if not working_urls:
        print("\n❌ No working URLs found for Froxjob")
        print("🎯 Recommendations:")
        print("1. Check if the website is accessible")
        print("2. Try different URL patterns")
        print("3. Check robots.txt for restrictions")
        return
    
    print(f"\n✅ Found {len(working_urls)} working URLs:")
    for url, title in working_urls:
        print(f"   {url} -> {title}")
    
    # Step 2: Analyze the best URL for job patterns
    best_url = working_urls[0][0]  # Take the first working URL
    containers, job_links = analyze_job_patterns(best_url)
    
    # Step 3: Test job detail page if we found links
    if job_links:
        test_job_detail_page(job_links)
    
    print("\n" + "="*60)
    print("📊 FROXJOB ANALYSIS SUMMARY")
    print("="*60)
    
    if working_urls:
        print(f"✅ Working URLs: {len(working_urls)}")
        print(f"✅ Best URL for scraping: {best_url}")
    
    if containers:
        print(f"✅ Job containers found: {len(containers)}")
        print("   Top containers:")
        for selector, count in sorted(containers, key=lambda x: x[1], reverse=True)[:3]:
            print(f"   - {selector}: {count} elements")
    
    if job_links:
        print(f"✅ Job links found: {len(job_links)}")
    
    print("\n🎯 Next Steps:")
    print("1. Update config/settings.py with correct selectors")
    print("2. Create Froxjob scraper script")
    print("3. Test with limited pages")
    print("4. Deploy to production")
    print("="*60)


if __name__ == "__main__":
    main() 