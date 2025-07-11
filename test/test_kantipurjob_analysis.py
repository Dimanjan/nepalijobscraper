#!/usr/bin/env python3
"""
Test analysis for KantipurJob.com
Goal: Understand structure and extract job information
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin

# Test KantipurJob.com structure
def analyze_kantipurjob():
    base_url = "https://kantipurjob.com"
    
    # Headers to mimic browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("🔍 Analyzing KantipurJob.com...")
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for job containers and patterns
        print(f"📄 Page title: {soup.title.text if soup.title else 'No title'}")
        print(f"📊 Page length: {len(response.content)} bytes")
        
        # Search for job-related elements
        job_selectors = [
            '.job-item', '.job-card', '.job-listing', '.job',
            '[data-job]', '.vacancy', '.position',
            '.featured-jobs', '.job-detail', '.job-post',
            '.job-list', '.jobs-item', '.card'
        ]
        
        for selector in job_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"✅ Found {len(elements)} elements with selector: {selector}")
                if len(elements) <= 3:  # Show details for few elements
                    for i, elem in enumerate(elements[:2]):
                        print(f"   Sample {i+1}: {elem.get_text()[:100]}...")
        
        # Look for specific text patterns
        text_content = soup.get_text().lower()
        
        # Check for job-related keywords
        keywords = ['job', 'vacancy', 'position', 'career', 'hiring', 'employment']
        for keyword in keywords:
            count = text_content.count(keyword)
            if count > 5:
                print(f"📝 Keyword '{keyword}': {count} occurrences")
        
        # Look for category/industry links
        industry_links = soup.find_all('a', href=True)
        job_categories = []
        for link in industry_links:
            href = link.get('href', '')
            text = link.get_text().strip()
            if '(' in text and ')' in text:  # Likely category with count like "IT (25)"
                job_categories.append({
                    'category': text,
                    'url': urljoin(base_url, href)
                })
        
        if job_categories:
            print(f"📂 Found {len(job_categories)} job categories:")
            for i, cat in enumerate(job_categories[:10]):
                print(f"   {i+1}. {cat['category']}")
        
        # Look for job statistics
        stats_elements = soup.find_all(['div', 'span', 'p'], text=lambda x: x and any(word in x.lower() for word in ['jobs', 'companies', 'employers']))
        if stats_elements:
            print(f"📊 Found statistics elements:")
            for elem in stats_elements[:5]:
                print(f"   - {elem.get_text().strip()}")
        
        # Check for pagination or navigation
        nav_elements = soup.find_all(['nav', 'div'], class_=lambda x: x and 'pag' in x.lower())
        if nav_elements:
            print(f"📄 Found pagination elements: {len(nav_elements)}")
        
        # Look for job numbers or statistics
        import re
        numbers = re.findall(r'\b(\d+)\s*(?:jobs?|vacancies|positions|companies)\b', text_content, re.IGNORECASE)
        if numbers:
            print(f"📊 Statistics found: {numbers}")
        
        return True
        
    except requests.RequestException as e:
        print(f"❌ Error accessing KantipurJob: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    analyze_kantipurjob() 