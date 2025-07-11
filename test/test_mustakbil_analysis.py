"""
Test script to analyze Mustakbil Nepal website structure.

Mustakbil Nepal appears to be an AI-powered job portal with modern features.
This script will analyze their structure for potential scraping.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time


def analyze_mustakbil_structure():
    """Analyze Mustakbil Nepal website structure."""
    print("🔍 Analyzing Mustakbil Nepal structure...")
    
    base_url = "https://np.mustakbil.com"
    
    # Test different potential job listing URLs
    test_urls = [
        "https://np.mustakbil.com",
        "https://np.mustakbil.com/jobs",
        "https://np.mustakbil.com/job-search",
        "https://np.mustakbil.com/search",
        "https://np.mustakbil.com/latest-jobs",
        "https://np.mustakbil.com/browse-jobs",
        "https://np.mustakbil.com/jobs/kathmandu",
        "https://np.mustakbil.com/jobs/nepal"
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
                    filename = test_url.replace('https://np.mustakbil.com', '').replace('/', '_') or '_main'
                    with open(f'test/mustakbil{filename}.html', 'w', encoding='utf-8') as f:
                        f.write(soup.prettify())
                    print(f"💾 Saved to test/mustakbil{filename}.html")
                    
            else:
                print(f"❌ Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        time.sleep(1)  # Be respectful with requests
    
    return working_urls


def analyze_job_patterns(url):
    """Analyze job listing patterns on Mustakbil."""
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
            '.vacancy', '.position', '.card', '.listing', '.posting',
            '[class*="job"]', '[class*="vacancy"]', '[class*="position"]',
            '.post', '.entry', '.item', '.result'
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
            'a[href*="detail"]', 'a[href*="view"]', '.job-title a', '.title a',
            'a[href*="posting"]', 'a[href*="career"]'
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
            '[class*="page"]', '.next', '.prev', '.more', '.load-more'
        ]
        
        for pattern in pagination_patterns:
            elements = soup.select(pattern)
            if elements:
                print(f"  ✅ Found pagination with: {pattern}")
        
        # Look for job counts or statistics
        print("\n📊 Looking for job statistics:")
        stats_patterns = [
            '.job-count', '.total-jobs', '.stats', '.count',
            '[class*="count"]', '[class*="total"]', '.results'
        ]
        
        for pattern in stats_patterns:
            elements = soup.select(pattern)
            if elements:
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if any(char.isdigit() for char in text):
                        print(f"  📊 Found stats: {text}")
        
        # Check for AI-powered features
        print("\n🤖 Looking for AI features:")
        ai_indicators = soup.get_text().lower()
        ai_features = ['ai', 'artificial intelligence', 'machine learning', 'recommendation', 'smart']
        for feature in ai_features:
            if feature in ai_indicators:
                print(f"  🤖 Found AI feature mention: {feature}")
                
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
        with open('test/mustakbil_job_detail.json', 'w', encoding='utf-8') as f:
            json.dump(job_data, f, indent=2)
        print(f"\n💾 Saved job detail analysis to test/mustakbil_job_detail.json")
        
    except Exception as e:
        print(f"❌ Error testing job detail: {e}")


def main():
    print("🧪 Analyzing Mustakbil Nepal Website Structure")
    print("🎯 Target: AI-powered job portal\n")
    
    # Step 1: Find working URLs
    working_urls = analyze_mustakbil_structure()
    
    if not working_urls:
        print("\n❌ No working URLs found for Mustakbil Nepal")
        print("🎯 Recommendations:")
        print("1. Check if the website is accessible")
        print("2. Try different URL patterns")
        print("3. Check for API endpoints")
        print("4. Verify domain and SSL certificate")
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
    print("📊 MUSTAKBIL NEPAL ANALYSIS SUMMARY")
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
    print("1. Update config/settings.py with Mustakbil selectors")
    print("2. Create Mustakbil scraper script")
    print("3. Test with AI-powered features")
    print("4. Scale to collect more jobs")
    print("="*60)


if __name__ == "__main__":
    main() 