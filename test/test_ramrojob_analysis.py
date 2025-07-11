"""
Test script to analyze Ramrojob website structure.

NOTE: Ramrojob has restrictive robots.txt policies that may limit automated access.
This script will be respectful and check their policies before proceeding.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time


def check_robots_txt():
    """Check Ramrojob's robots.txt to understand scraping policies."""
    print("🤖 Checking Ramrojob robots.txt...")
    
    try:
        response = requests.get("https://ramrojob.com/robots.txt", timeout=10)
        
        if response.status_code == 200:
            print("✅ Found robots.txt:")
            lines = response.text.split('\n')
            
            for line in lines[:20]:  # Show first 20 lines
                if line.strip():
                    print(f"   {line}")
            
            if len(lines) > 20:
                print("   ... (truncated)")
            
            # Check for specific restrictions
            content = response.text.lower()
            if 'disallow: /' in content:
                print("\n⚠️  WARNING: Robots.txt contains 'Disallow: /' - scraping may be prohibited")
                return False
            
            if 'scrape' in content or 'bot' in content:
                print("\n⚠️  WARNING: Robots.txt mentions scraping/bot restrictions")
                return False
            
            return True
        else:
            print(f"❌ Could not access robots.txt: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking robots.txt: {e}")
        return False


def analyze_ramrojob_structure():
    """Analyze Ramrojob website structure with caution."""
    print("\n🔍 Analyzing Ramrojob structure...")
    
    base_url = "https://ramrojob.com"
    
    # Test different potential job listing URLs
    test_urls = [
        "https://ramrojob.com",
        "https://ramrojob.com/jobs", 
        "https://ramrojob.com/job",
        "https://ramrojob.com/vacancy",
        "https://ramrojob.com/search",
        "https://ramrojob.com/listings",
        "https://ramrojob.com/careers"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    working_urls = []
    
    print("⚠️  Being extra respectful due to restrictive robots.txt")
    
    for test_url in test_urls:
        try:
            print(f"\n🧪 Testing: {test_url}")
            
            # Add extra delay to be respectful
            time.sleep(2)
            
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
                    filename = test_url.replace('https://ramrojob.com', '').replace('/', '_') or '_main'
                    with open(f'test/ramrojob{filename}.html', 'w', encoding='utf-8') as f:
                        f.write(soup.prettify())
                    print(f"💾 Saved to test/ramrojob{filename}.html")
                    
            elif response.status_code == 403:
                print(f"⛔ Status: {response.status_code} - Access forbidden (expected due to robots.txt)")
            elif response.status_code == 429:
                print(f"⛔ Status: {response.status_code} - Rate limited")
                print("⏸️  Stopping analysis to respect rate limits")
                break
            else:
                print(f"❌ Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    return working_urls


def analyze_job_patterns(url):
    """Analyze job listing patterns on Ramrojob page."""
    print(f"\n🔍 Analyzing job patterns on: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        # Extra respectful delay
        time.sleep(3)
        
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


def main():
    print("🧪 Analyzing Ramrojob Website Structure")
    print("⚠️  NOTE: Ramrojob has restrictive robots.txt - proceeding with caution\n")
    
    # Step 1: Check robots.txt
    robots_ok = check_robots_txt()
    
    if not robots_ok:
        print("\n❌ Robots.txt indicates scraping restrictions")
        print("🎯 Recommendations:")
        print("1. Respect the website's robots.txt policies")
        print("2. Contact Ramrojob for permission or API access")
        print("3. Consider alternative approaches")
        print("4. Skip this website for now")
        
        # Ask if we should continue anyway (for educational purposes)
        print("\n⚠️  This analysis is for educational purposes only")
        print("Continue with minimal, respectful testing? (y/n)")
        
        # For automation, we'll skip if robots.txt is restrictive
        print("🛑 Skipping Ramrojob analysis due to robots.txt restrictions")
        return
    
    # Step 2: Find working URLs (only if robots.txt allows)
    working_urls = analyze_ramrojob_structure()
    
    if not working_urls:
        print("\n❌ No accessible URLs found for Ramrojob")
        return
    
    # Step 3: Analyze patterns (with extra caution)
    print(f"\n✅ Found {len(working_urls)} working URLs:")
    for url, title in working_urls:
        print(f"   {url} -> {title}")
    
    if working_urls:
        best_url = working_urls[0][0]
        containers, job_links = analyze_job_patterns(best_url)
    
    print("\n" + "="*60)
    print("📊 RAMROJOB ANALYSIS SUMMARY")
    print("="*60)
    
    if working_urls:
        print(f"✅ Accessible URLs: {len(working_urls)}")
    else:
        print("❌ No accessible URLs due to restrictions")
    
    print("\n🎯 Recommendations:")
    print("1. Respect Ramrojob's robots.txt policies")
    print("2. Consider contacting them for permission")
    print("3. Focus on other websites that allow scraping")
    print("4. Use this as a learning example for handling restrictions")
    print("="*60)


if __name__ == "__main__":
    main() 