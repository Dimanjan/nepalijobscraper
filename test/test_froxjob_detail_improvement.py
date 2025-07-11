"""
Test script to improve Froxjob data extraction quality.

This script analyzes individual job detail pages from Froxjob to identify
additional data fields we can extract for better quality.
"""

import requests
from bs4 import BeautifulSoup
import json
import time


def test_froxjob_job_detail_quality():
    """Test job detail pages from Froxjob to find more extractable data."""
    print("🔍 Testing Froxjob job detail pages for quality improvement...\n")
    
    # Sample job URLs from our previous scraping
    test_job_urls = [
        "https://froxjob.com/area-sales-manager-122",
        "https://froxjob.com/factory-manager-9", 
        "https://froxjob.com/quality-control-officer-3",
        "https://froxjob.com/teller",
        "https://froxjob.com/brand-executive-1"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    all_extracted_data = []
    
    for i, job_url in enumerate(test_job_urls, 1):
        print(f"🧪 Testing job {i}/{len(test_job_urls)}: {job_url}")
        
        try:
            time.sleep(1.5)  # Be respectful
            response = requests.get(job_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract comprehensive data from the page
            job_data = {'url': job_url}
            
            # Basic info
            job_data['title'] = extract_field(soup, [
                'h1', '.job-title', '.title', '.post-title',
                '[class*="title"]', '.page-title'
            ])
            
            # Company information
            job_data['company'] = extract_field(soup, [
                '.company', '.company-name', '.employer',
                '[class*="company"]', '.organization'
            ])
            
            # Job details
            job_data['location'] = extract_field(soup, [
                '.location', '.address', '.job-location',
                '[class*="location"]', '.venue'
            ])
            
            job_data['salary'] = extract_field(soup, [
                '.salary', '.pay', '.wage', '.compensation',
                '[class*="salary"]', '.package'
            ])
            
            job_data['deadline'] = extract_field(soup, [
                '.deadline', '.expiry', '.apply-by', '.last-date',
                '[class*="deadline"]', '.expires'
            ])
            
            job_data['posted_date'] = extract_field(soup, [
                '.date', '.posted', '.published', '.created',
                '[class*="date"]', '.time'
            ])
            
            # Detailed information
            job_data['description'] = extract_field(soup, [
                '.description', '.content', '.job-description',
                '.job-content', '.details', '.summary'
            ])
            
            job_data['requirements'] = extract_field(soup, [
                '.requirements', '.qualifications', '.job-requirements',
                '.qualification', '.skills-required', '.criteria'
            ])
            
            job_data['benefits'] = extract_field(soup, [
                '.benefits', '.job-benefits', '.perks',
                '.advantages', '.package', '.offers'
            ])
            
            job_data['experience'] = extract_field(soup, [
                '.experience', '.experience-level', '.job-experience',
                '.years', '.exp', '.experience-required'
            ])
            
            job_data['education'] = extract_field(soup, [
                '.education', '.qualification', '.job-education',
                '.degree', '.academic', '.educational'
            ])
            
            job_data['job_type'] = extract_field(soup, [
                '.job-type', '.employment-type', '.type',
                '.category', '.nature', '.employment'
            ])
            
            job_data['skills'] = extract_field(soup, [
                '.skills', '.skill', '.technologies',
                '.tech-stack', '.abilities', '.competencies'
            ])
            
            # Contact information
            job_data['contact_email'] = extract_field(soup, [
                '.email', '.contact-email', '.apply-email',
                '[type="email"]', 'a[href^="mailto:"]'
            ])
            
            job_data['contact_phone'] = extract_field(soup, [
                '.phone', '.contact-phone', '.mobile',
                '.tel', 'a[href^="tel:"]'
            ])
            
            # Application information
            job_data['apply_url'] = extract_field(soup, [
                '.apply-link', '.application-link', '.apply-button',
                'a[href*="apply"]', '.apply'
            ])
            
            # Try to find any additional structured data
            job_data['json_ld'] = extract_json_ld(soup)
            job_data['meta_data'] = extract_meta_data(soup)
            
            all_extracted_data.append(job_data)
            
            # Show what we found
            print("📋 Extracted data:")
            for field, value in job_data.items():
                if value and field not in ['json_ld', 'meta_data']:
                    print(f"   {field}: {str(value)[:100]}...")
            
            if job_data['json_ld']:
                print(f"   📊 JSON-LD structured data found!")
            
            print()
            
        except Exception as e:
            print(f"❌ Error processing {job_url}: {e}\n")
    
    # Save all extracted data for analysis
    with open('test/froxjob_enhanced_extraction.json', 'w', encoding='utf-8') as f:
        json.dump(all_extracted_data, f, indent=2, ensure_ascii=False)
    
    print("💾 Saved enhanced extraction data to test/froxjob_enhanced_extraction.json")
    
    return all_extracted_data


def extract_field(soup, selectors):
    """Try multiple selectors to extract a field."""
    for selector in selectors:
        try:
            if selector.startswith('a[href^="mailto:"]'):
                element = soup.select_one(selector)
                if element:
                    return element.get('href', '').replace('mailto:', '')
            elif selector.startswith('a[href^="tel:"]'):
                element = soup.select_one(selector)
                if element:
                    return element.get('href', '').replace('tel:', '')
            elif selector.startswith('a[href*="apply"]'):
                element = soup.select_one(selector)
                if element:
                    return element.get('href', '')
            else:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text and len(text) > 2:  # Avoid empty or very short strings
                        return text
        except:
            continue
    return ''


def extract_json_ld(soup):
    """Extract JSON-LD structured data if available."""
    scripts = soup.find_all('script', type='application/ld+json')
    json_ld_data = []
    
    for script in scripts:
        try:
            data = json.loads(script.string)
            json_ld_data.append(data)
        except:
            continue
    
    return json_ld_data if json_ld_data else None


def extract_meta_data(soup):
    """Extract relevant meta tags."""
    meta_data = {}
    
    # Look for useful meta tags
    meta_tags = [
        'description', 'keywords', 'author', 'og:title',
        'og:description', 'twitter:title', 'twitter:description'
    ]
    
    for tag_name in meta_tags:
        tag = soup.find('meta', {'name': tag_name}) or soup.find('meta', {'property': tag_name})
        if tag:
            meta_data[tag_name] = tag.get('content', '')
    
    return meta_data if meta_data else None


def analyze_extraction_patterns(extracted_data):
    """Analyze patterns in extracted data to identify best selectors."""
    print("\n📊 ANALYZING EXTRACTION PATTERNS")
    print("="*50)
    
    # Count successful extractions by field
    field_success = {}
    
    for job_data in extracted_data:
        for field, value in job_data.items():
            if field not in ['url', 'json_ld', 'meta_data']:
                if field not in field_success:
                    field_success[field] = {'success': 0, 'total': 0}
                
                field_success[field]['total'] += 1
                if value and str(value).strip():
                    field_success[field]['success'] += 1
    
    # Sort by success rate
    sorted_fields = sorted(field_success.items(), 
                          key=lambda x: x[1]['success'] / x[1]['total'] if x[1]['total'] > 0 else 0, 
                          reverse=True)
    
    print("🎯 Field extraction success rates:")
    for field, stats in sorted_fields:
        success_rate = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
        print(f"   {field}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
    
    return field_success


def main():
    print("🧪 Froxjob Data Quality Improvement Test\n")
    
    # Test job detail extraction
    extracted_data = test_froxjob_job_detail_quality()
    
    # Analyze patterns
    if extracted_data:
        analyze_extraction_patterns(extracted_data)
        
        print("\n🎯 Recommendations for Froxjob scraper improvement:")
        print("1. Focus on fields with high success rates")
        print("2. Update selectors based on successful patterns")
        print("3. Add fallback selectors for important fields")
        print("4. Consider JSON-LD structured data if available")
    
    print("\n" + "="*50)
    print("🚀 Ready to update Froxjob scraper with enhanced extraction!")


if __name__ == "__main__":
    main() 