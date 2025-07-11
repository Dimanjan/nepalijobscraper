"""
Configuration settings for Nepal Job Scraper.

Contains default settings, website configurations, and scraping parameters.
"""

from typing import Dict, Any
from pydantic_settings import BaseSettings


class ScraperSettings(BaseSettings):
    """Main configuration for the job scraper."""
    
    # General settings
    DEFAULT_DELAY: float = 1.0
    MAX_RETRIES: int = 3
    CONCURRENT_REQUESTS: int = 5
    
    # Data settings
    DATA_PATH: str = "data"
    BACKUP_ENABLED: bool = True
    EXPORT_FORMATS: list = ["json", "csv"]
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_RETENTION_DAYS: int = 30
    
    # Request settings
    REQUEST_TIMEOUT: int = 30
    USER_AGENT_ROTATION: bool = True
    RESPECT_ROBOTS_TXT: bool = True
    
    class Config:
        env_file = ".env"
        env_prefix = "SCRAPER_"


# Website configurations
WEBSITE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "merojob": {
        "name": "Merojob",
        "base_url": "https://merojob.com",
        "search_url": "https://merojob.com/search/",
        "delay": 1.5,
        "max_pages": 100,
        "selectors": {
            "job_links": ".job-card h1.text-primary a",
            "pagination": ".pagination a",
            "job_title": "h1[itemprop='title']",
            "company": ".text-dark",
            "location": "[itemprop='addressLocality']",
            "description": "[itemprop='description']",
            "salary": ".salary-info",
            "deadline": ".card-footer .text-primary",
            "posted_date": "[itemprop='datePosted']",
            "skills": "[itemprop='skills'] .badge",
            "employment_type": "[itemprop='employmentType']"
        },
        "rate_limit": {
            "requests_per_minute": 30,
            "burst_limit": 10
        }
    },
    
    "jobaxle": {
        "name": "JobAxle", 
        "base_url": "https://jobaxle.com",
        "search_url": "https://jobaxle.com/jobs",
        "delay": 1.0,
        "max_pages": 50,
        "selectors": {
            "job_links": ".job-card h3 a",
            "pagination": ".pagination a",
            "job_title": "h1",
            "company": ".company-info",
            "location": ".location",
            "description": ".job-content",
            "salary": ".salary",
            "deadline": ".deadline",
            "posted_date": ".published"
        },
        "rate_limit": {
            "requests_per_minute": 40,
            "burst_limit": 15
        }
    },
    
    "froxjob": {
        "name": "Froxjob",
        "base_url": "https://froxjob.com", 
        "search_url": "https://froxjob.com",
        "delay": 1.2,
        "max_pages": 30,
        "selectors": {
            "job_links": ".joblist li a",
            "company_cards": ".job-wrapper",
            "company_name": ".media-heading",
            "pagination": ".pagination",
            "job_title": "h1, .job-title",
            "company": ".company-name, .company",
            "location": ".location, .address",
            "description": ".description, .content, .job-content",
            "salary": ".salary, .salary-range",
            "deadline": ".deadline, .apply-deadline",
            "posted_date": ".date, .posted-date"
        },
        "rate_limit": {
            "requests_per_minute": 25,
            "burst_limit": 8
        }
    },
    
    "mustakbil": {
        "name": "Mustakbil Nepal",
        "base_url": "https://np.mustakbil.com",
        "search_url": "https://np.mustakbil.com/jobs/nepal",
        "delay": 1.0,
        "max_pages": 20,
        "selectors": {
            "job_links": "a[href*='job']",
            "job_containers": "[class*='job']",
            "pagination": "[class*='page']",
            "job_title": "h1, .job-title, .title",
            "company": ".company-name, .company, .employer",
            "location": ".location, .address, .job-location",
            "description": ".description, .content, .job-description",
            "salary": ".salary, .pay, .wage",
            "deadline": ".deadline, .expiry, .apply-by",
            "posted_date": ".date, .posted, .published"
        },
        "rate_limit": {
            "requests_per_minute": 40,
            "burst_limit": 15
        }
    },
    
    "hamrojobs": {
        "name": "HamroJobs",
        "base_url": "https://hamrojobs.com.np",
        "search_url": "https://hamrojobs.com.np",
        "delay": 1.5,
        "max_pages": 15,
        "selectors": {
            "job_links": "a[href*='jobpost']",
            "job_containers": "[class*='job']",
            "pagination": ".pagination",
            "job_title": "h1, .job-title, .title",
            "company": ".company-name, .company",
            "location": ".location, .address",
            "description": ".description, .content, .job-description",
            "salary": ".salary, .pay",
            "deadline": ".deadline, .expiry",
            "posted_date": ".date, .posted"
        },
        "rate_limit": {
            "requests_per_minute": 25,
            "burst_limit": 8
        }
    },
    
    "futurerojgar": {
        "name": "FutureRojgar",
        "base_url": "https://futurerojgar.com",
        "search_url": "https://futurerojgar.com",
        "delay": 1.5,
        "max_pages": 50,
        "selectors": {
            "job_links": ".job a, a[href*='classified']",
            "job_containers": ".job",
            "pagination": "[class*='page']",
            "job_title": "h1, .title, .job-title",
            "company": ".company, .company-name, .employer",
            "location": ".location, .address",
            "description": ".description, .content, .details",
            "salary": ".salary, .pay",
            "deadline": ".deadline, .expiry",
            "posted_date": ".date, .posted"
        },
        "rate_limit": {
            "requests_per_minute": 30,
            "burst_limit": 10
        }
    },
    
    "ramrojob": {
        "name": "Ramrojob",
        "base_url": "https://ramrojob.com",
        "search_url": "https://ramrojob.com/jobs",
        "delay": 2.0,
        "max_pages": 40,
        "selectors": {
            "job_links": ".job-item .title a",
            "pagination": ".pagination span",
            "job_title": "h1.title",
            "company": ".company-name",
            "location": ".job-location",
            "description": ".description",
            "salary": ".salary",
            "deadline": ".deadline-date",
            "posted_date": ".posted-on"
        },
        "rate_limit": {
            "requests_per_minute": 20,
            "burst_limit": 5
        }
    },
    
    "jobkunja": {
        "name": "JobKunja",
        "base_url": "https://jobkunja.com",
        "search_url": "https://jobkunja.com/jobs/search",
        "delay": 1.5,
        "max_pages": 10,
        "selectors": {
            "job_cards": ".card",
            "job_links": ".card a",
            "pagination": "[class*='page']",
            "job_title": "h1, h2, h3, strong",
            "company": ".company, [class*='company']",
            "location": ".location, [class*='location']",
            "description": ".description, .content",
            "salary": ".salary, [class*='salary']",
            "deadline": ".deadline, .expiry",
            "posted_date": ".date, .posted"
        },
        "rate_limit": {
            "requests_per_minute": 30,
            "burst_limit": 10
        }
    },
    
    "kantipurjob": {
        "name": "KantipurJob",
        "base_url": "https://kantipurjob.com",
        "search_url": "https://kantipurjob.com/jobs",
        "delay": 1.5,
        "max_pages": 15,
        "selectors": {
            "job_categories": "a[href*='category']",
            "job_links": ".job-item a, .job a",
            "pagination": "[class*='page']",
            "job_title": "h1, h2, h3, .title",
            "company": ".company, .employer, .organization",
            "location": ".location, .address",
            "description": ".description, .content, .details",
            "salary": ".salary, .pay",
            "deadline": ".deadline, .expiry",
            "posted_date": ".date, .posted"
        },
        "rate_limit": {
            "requests_per_minute": 20,
            "burst_limit": 5
        }
    }
}

# Common job data fields
STANDARD_FIELDS = [
    "id",
    "title", 
    "company",
    "location",
    "salary_min",
    "salary_max", 
    "job_type",
    "experience_required",
    "education_required",
    "description",
    "requirements",
    "benefits",
    "application_deadline",
    "posted_date",
    "contact_email",
    "contact_phone",
    "job_category",
    "industry",
    "url",
    "source_website",
    "scraped_at"
]

# Priority order for scraping
SCRAPING_PRIORITY = [
    "merojob",    # Largest user base
    "jobaxle",    # Good structure 
    "froxjob",    # Modern interface
    "ramrojob"    # Established portal
] 