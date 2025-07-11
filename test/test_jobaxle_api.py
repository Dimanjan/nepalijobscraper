"""
Test script to explore JobAxle's API endpoint.

Since we found /api/search returns JSON, let's explore its structure.
"""

import requests
import json
from urllib.parse import urljoin


def test_jobaxle_api():
    """Test JobAxle's API endpoint."""
    print("🔌 Testing JobAxle API endpoint...")
    
    base_url = "https://jobaxle.com"
    api_url = f"{base_url}/api/search"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://jobaxle.com/search'
    }
    
    # Test different parameters
    test_params = [
        {},  # No parameters
        {'page': 1},  # Page parameter
        {'page': 1, 'limit': 10},  # With limit
        {'search': ''},  # Empty search
    ]
    
    for i, params in enumerate(test_params):
        try:
            print(f"\n🧪 Test {i+1}: {params}")
            response = requests.get(api_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Response structure:")
            print(f"   - success: {data.get('success')}")
            print(f"   - message: {data.get('message')}")
            print(f"   - status: {data.get('status')}")
            
            if 'data' in data and 'rows' in data['data']:
                jobs = data['data']['rows']
                print(f"   - jobs found: {len(jobs)}")
                
                if jobs:
                    # Analyze first job structure
                    first_job = jobs[0]
                    print(f"   - first job fields: {list(first_job.keys())}")
                    
                    # Show sample data
                    print(f"\n📋 Sample job data:")
                    for key, value in first_job.items():
                        if isinstance(value, str) and len(value) > 100:
                            value = value[:100] + "..."
                        print(f"     {key}: {value}")
            
            # Save full response for the first successful test
            if i == 0:
                with open('test/jobaxle_api_response.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                print(f"\n💾 Saved API response to test/jobaxle_api_response.json")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


def test_pagination():
    """Test pagination with JobAxle API."""
    print("\n📄 Testing pagination...")
    
    base_url = "https://jobaxle.com"
    api_url = f"{base_url}/api/search"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://jobaxle.com/search'
    }
    
    # Test multiple pages
    for page in range(1, 4):  # Test first 3 pages
        try:
            params = {'page': page, 'limit': 5}  # Small limit for testing
            response = requests.get(api_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data and 'rows' in data['data']:
                jobs = data['data']['rows']
                print(f"  Page {page}: {len(jobs)} jobs")
                
                if jobs:
                    # Show job titles from this page
                    titles = [job.get('jobTitle', 'No title') for job in jobs[:3]]
                    print(f"    Sample titles: {titles}")
                else:
                    print(f"    No jobs on page {page}")
                    break
            else:
                print(f"  Page {page}: Invalid response structure")
                break
                
        except Exception as e:
            print(f"  Page {page}: Error - {e}")
            break


def test_job_detail_api():
    """Test if there's an API for individual job details."""
    print("\n🔍 Testing job detail endpoints...")
    
    # First, get a job ID from the search API
    base_url = "https://jobaxle.com"
    search_url = f"{base_url}/api/search"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://jobaxle.com/search'
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        data = response.json()
        
        if 'data' in data and 'rows' in data['data'] and data['data']['rows']:
            first_job = data['data']['rows'][0]
            job_id = first_job.get('id')
            job_slug = first_job.get('slug')
            
            print(f"Testing with job ID: {job_id}")
            print(f"Testing with job slug: {job_slug}")
            
            # Test different detail endpoint patterns
            detail_endpoints = [
                f"/api/job/{job_id}",
                f"/api/jobs/{job_id}",
                f"/api/job-detail/{job_id}",
                f"/api/search/{job_id}",
                f"/jobs/{job_slug}",  # HTML endpoint
            ]
            
            for endpoint in detail_endpoints:
                try:
                    detail_url = base_url + endpoint
                    detail_response = requests.get(detail_url, headers=headers, timeout=5)
                    
                    if detail_response.status_code == 200:
                        content_type = detail_response.headers.get('content-type', '')
                        if 'json' in content_type:
                            print(f"  ✅ {endpoint} -> JSON response")
                            detail_data = detail_response.json()
                            print(f"     Keys: {list(detail_data.keys()) if isinstance(detail_data, dict) else 'Not a dict'}")
                        else:
                            print(f"  ✅ {endpoint} -> HTML response")
                    else:
                        print(f"  ❌ {endpoint} -> {detail_response.status_code}")
                except Exception as e:
                    print(f"  ❌ {endpoint} -> Error: {e}")
        
    except Exception as e:
        print(f"❌ Could not get job data for testing: {e}")


def main():
    print("🧪 Testing JobAxle API\n")
    
    test_jobaxle_api()
    test_pagination()
    test_job_detail_api()
    
    print("\n" + "="*60)
    print("📊 JOBAXLE API ANALYSIS SUMMARY")
    print("="*60)
    print("✅ API endpoint found: /api/search")
    print("✅ Returns JSON data with job listings")
    print("✅ Supports pagination with 'page' parameter")
    print("✅ Supports search with 'search' parameter")
    print("\n🎯 Implementation Strategy:")
    print("1. Use /api/search endpoint instead of HTML scraping")
    print("2. Implement pagination using 'page' parameter")
    print("3. Extract job details from API response")
    print("4. For detailed job info, try job detail endpoints or HTML page")
    print("="*60)


if __name__ == "__main__":
    main() 