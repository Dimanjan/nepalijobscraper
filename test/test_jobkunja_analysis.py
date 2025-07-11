#!/usr/bin/env python3
"""
Test analysis for JobKunja.com
Goal: Understand structure and extract job information
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin

# Test JobKunja.com structure
def analyze_jobkunja():
    base_url = "https://jobkunja.com"
    
    # Headers to mimic browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("🔍 Analyzing JobKunja.com...")
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
            '.job-list', '.jobs-item', '.card', '.job-container'
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
        
        # Look for job titles and company names in the page
        title_elements = soup.find_all(['h1', 'h2', 'h3', 'h4'], text=lambda x: x and len(x.strip()) > 5)
        job_titles = []
        for elem in title_elements:
            text = elem.get_text().strip()
            if any(word in text.lower() for word in ['job', 'vacancy', 'position', 'officer', 'manager', 'assistant']):
                job_titles.append(text)
        
        if job_titles:
            print(f"📋 Found potential job titles:")
            for i, title in enumerate(job_titles[:5]):
                print(f"   {i+1}. {title}")
        
        # Look for links that might be job postings
        links = soup.find_all('a', href=True)
        job_links = []
        for link in links:
            href = link.get('href', '')
            text = link.get_text().strip()
            # Check if link text looks like a job title or company name
            if len(text) > 5 and any(word in text.lower() for word in ['job', 'vacancy', 'position', 'apply', 'view']):
                full_url = urljoin(base_url, href)
                job_links.append({
                    'url': full_url,
                    'text': text[:50],
                    'href': href
                })
        
        print(f"🔗 Found {len(job_links)} potential job-related links")
        if job_links:
            for i, link in enumerate(job_links[:5]):
                print(f"   {i+1}. {link['text']} -> {link['url']}")
        
        # Look for job numbers or statistics
        import re
        numbers = re.findall(r'\b(\d+)\s*(?:jobs?|vacancies|positions|companies)\b', text_content, re.IGNORECASE)
        if numbers:
            print(f"📊 Statistics found: {numbers}")
        
        # Check for tables that might contain job listings
        tables = soup.find_all('table')
        if tables:
            print(f"📊 Found {len(tables)} tables that might contain job data")
        
        return True
        
    except requests.RequestException as e:
        print(f"❌ Error accessing JobKunja: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    analyze_jobkunja() 