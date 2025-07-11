"""
Test script to find the correct JobAxle URLs and structure.

Since the /jobs URL didn't work, let's try different approaches.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def test_jobaxle_main():
    """Test JobAxle main page to find job listing URLs."""
    print("🔍 Testing JobAxle main page...")
    
    base_url = "https://jobaxle.com"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"✅ Successfully connected to {base_url}")
        print(f"Page title: {soup.title.get_text() if soup.title else 'No title'}")
        
        # Look for navigation links that might lead to jobs
        nav_links = soup.find_all('a')
        job_related_links = []
        
        print("\n🔗 Looking for job-related links:")
        for link in nav_links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()
            
            if any(keyword in href.lower() or keyword in text for keyword in 
                   ['job', 'vacancy', 'career', 'position', 'hiring']):
                full_url = urljoin(base_url, href)
                job_related_links.append((text, full_url))
                print(f"  ✅ Found: {text} -> {full_url}")
        
        # Try common job listing URLs
        test_urls = [
            "/jobs",
            "/job",
            "/careers",
            "/vacancies", 
            "/listings",
            "/search",
            "/browse",
            "/job-listing",
            "/all-jobs"
        ]
        
        print(f"\n🧪 Testing common job listing URLs:")
        working_urls = []
        for url_path in test_urls:
            test_url = base_url + url_path
            try:
                test_response = requests.get(test_url, headers=headers, timeout=5)
                if test_response.status_code == 200:
                    test_soup = BeautifulSoup(test_response.content, 'html.parser')
                    title = test_soup.title.get_text() if test_soup.title else 'No title'
                    
                    # Check if this looks like a job listing page
                    if 'undefined' not in title.lower() and 'error' not in title.lower():
                        working_urls.append((url_path, title))
                        print(f"  ✅ {url_path} -> {title}")
                    else:
                        print(f"  ⚠️  {url_path} -> Possible error page")
                else:
                    print(f"  ❌ {url_path} -> {test_response.status_code}")
            except:
                print(f"  ❌ {url_path} -> Connection failed")
        
        # Save main page HTML
        with open('test/jobaxle_main.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"\n💾 Saved main page HTML to test/jobaxle_main.html")
        
        return job_related_links, working_urls
        
    except Exception as e:
        print(f"❌ Error testing main page: {e}")
        return [], []


def test_api_endpoints():
    """Test for API endpoints that might return job data."""
    print("\n🔌 Testing potential API endpoints...")
    
    base_url = "https://jobaxle.com"
    api_endpoints = [
        "/api/jobs",
        "/api/job",
        "/api/search",
        "/api/listings",
        "/jobs/api",
        "/search/api",
        "/_next/data",  # Next.js data endpoints
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }
    
    for endpoint in api_endpoints:
        try:
            response = requests.get(base_url + endpoint, headers=headers, timeout=5)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'json' in content_type:
                    print(f"  ✅ {endpoint} -> JSON API found!")
                    try:
                        data = response.json()
                        print(f"     Sample data: {str(data)[:200]}...")
                    except:
                        print(f"     Response: {response.text[:200]}...")
                else:
                    print(f"  ✅ {endpoint} -> HTML response")
            else:
                print(f"  ❌ {endpoint} -> {response.status_code}")
        except:
            print(f"  ❌ {endpoint} -> Failed")


def main():
    print("🧪 Testing JobAxle Website Structure\n")
    
    job_links, working_urls = test_jobaxle_main()
    test_api_endpoints()
    
    print("\n" + "="*60)
    print("📊 JOBAXLE ANALYSIS SUMMARY")
    print("="*60)
    
    if job_links:
        print("✅ Found job-related links:")
        for text, url in job_links:
            print(f"   {text} -> {url}")
    
    if working_urls:
        print("✅ Working URLs found:")
        for path, title in working_urls:
            print(f"   {path} -> {title}")
    
    if not job_links and not working_urls:
        print("❌ No job listings found - JobAxle might:")
        print("   - Use JavaScript to load content dynamically")
        print("   - Require authentication")
        print("   - Have changed their URL structure")
        print("   - Block automated requests")
    
    print("\n🎯 Recommendations:")
    print("1. Check test/jobaxle_main.html for manual inspection")
    print("2. Try using Selenium for JavaScript-heavy sites")
    print("3. Look for alternative job listing pages")
    print("4. Consider contacting JobAxle for API access")
    print("="*60)


if __name__ == "__main__":
    main() 