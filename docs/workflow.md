# Nepal Job Scraper - Development Workflow

This document outlines the step-by-step workflow for developing, testing, and maintaining job scrapers for Nepal.

## 🎯 Overall Workflow

### Phase 1: Research & Discovery
1. **Identify Target Website**
   - Add website to `config/settings.py` if not already present
   - Research website structure and job listing patterns
   - Check robots.txt and scraping policies

2. **Initial Testing**
   - Create test scripts in `test/` folder
   - Test basic connectivity and page structure
   - Identify CSS selectors for job data
   - Document findings

### Phase 2: Script Development
3. **Generate Script Template**
   ```bash
   python scraper_cli.py create-script <website>
   ```

4. **Customize Selectors**
   - Update selectors in the generated script
   - Test data extraction with sample pages
   - Handle edge cases and missing data

5. **Test Script**
   ```bash
   python scraper_cli.py test-script <website>
   ```

### Phase 3: Validation & Deployment
6. **Validate Output**
   - Check scraped data quality
   - Ensure all required fields are captured
   - Test with multiple pages

7. **Update Status**
   - Mark script as complete in `docs/website_status.md`
   - Document any special considerations

8. **Run Production Scraping**
   ```bash
   python scraper_cli.py scrape <website> --max-pages 5
   ```

## 🔧 Detailed Steps

### Step 1: Research Website Structure

1. **Manual Exploration**
   - Visit the website in a browser
   - Navigate through job listings
   - Identify patterns in URLs, pagination, and data layout
   - Note any anti-bot measures (CAPTCHA, rate limiting)

2. **Run Analysis Script**
   ```bash
   cd test/
   python sample_test.py
   ```

3. **Document Findings**
   - Update CSS selectors in `config/settings.py`
   - Note any special handling required
   - Identify data quality issues

### Step 2: Create Scraper Script

1. **Generate Template**
   ```bash
   python scraper_cli.py create-script merojob
   ```

2. **Customize the Script**
   - Update `get_job_links()` method for pagination
   - Customize `scrape_job_details()` for data extraction
   - Adjust `get_total_pages()` for website's pagination style

3. **Test Individual Methods**
   ```python
   # In test folder
   from scripts.merojob_scraper import MerojobScraper
   
   scraper = MerojobScraper()
   
   # Test getting job links
   links = scraper.get_job_links(page=1)
   print(f"Found {len(links)} job links")
   
   # Test scraping a single job
   if links:
       job_data = scraper.scrape_job_details(links[0])
       print(job_data)
   ```

### Step 3: Test and Validate

1. **Limited Test Run**
   ```bash
   python scraper_cli.py scrape merojob --test-mode --max-pages 2
   ```

2. **Check Output Quality**
   ```bash
   python scraper_cli.py stats
   ```

3. **Export and Review**
   ```bash
   python scraper_cli.py export --website merojob --format csv
   ```

4. **Clean Duplicates**
   ```bash
   python scraper_cli.py clean
   ```

### Step 4: Production Deployment

1. **Full Scrape**
   ```bash
   python scraper_cli.py scrape merojob --max-pages 10
   ```

2. **Monitor Logs**
   ```bash
   tail -f logs/scraper_$(date +%Y%m%d).log
   ```

3. **Update Status**
   - Mark website as ✅ Complete in `docs/website_status.md`
   - Add notes about any special handling

## 🧪 Testing Workflow

### Creating Test Scripts

1. **Create in test/ folder**
   ```python
   # test/test_merojob_analysis.py
   import requests
   from bs4 import BeautifulSoup
   
   def analyze_merojob():
       # Your analysis code here
       pass
   ```

2. **Run and Iterate**
   - Test different approaches
   - Save HTML samples for offline analysis
   - Document what works and what doesn't

3. **Clean Up**
   ```python
   # When done testing
   from test.sample_test import clean_test_files
   clean_test_files()
   ```

### Test Script Best Practices

- **Start Small**: Test with single pages before full scraping
- **Save Samples**: Save HTML for offline analysis
- **Document Issues**: Keep notes about anti-bot measures
- **Respect Limits**: Use delays and respect robots.txt
- **Clean Up**: Remove test files when done

## 📊 Data Management Workflow

### Regular Data Operations

1. **Export Data**
   ```bash
   # Export all data
   python scraper_cli.py export --format csv
   
   # Export specific website
   python scraper_cli.py export --website merojob --format json
   ```

2. **Clean Duplicates**
   ```bash
   python scraper_cli.py clean
   ```

3. **Check Statistics**
   ```bash
   python scraper_cli.py stats
   ```

### Data Quality Checks

1. **Validate Required Fields**
   - Check that title, company, and URL are present
   - Verify data completeness

2. **Check for Duplicates**
   - Same job posted multiple times
   - Different URLs for same job

3. **Data Consistency**
   - Consistent date formats
   - Proper salary parsing
   - Location standardization

## 🔄 Maintenance Workflow

### Regular Tasks

1. **Weekly Health Check**
   ```bash
   python scraper_cli.py status
   ```

2. **Monthly Data Export**
   ```bash
   python scraper_cli.py export --format csv
   ```

3. **Quarterly Scraper Updates**
   - Check if website structure changed
   - Update selectors if needed
   - Test all scrapers

### Handling Failures

1. **Script Stopped Working**
   - Check if website structure changed
   - Look at error logs
   - Test with sample pages
   - Update selectors if needed

2. **Rate Limiting Issues**
   - Increase delays in config
   - Implement better session management
   - Add user agent rotation

3. **Data Quality Issues**
   - Review validation rules
   - Update cleaning logic
   - Check for new data fields

## 📋 Checklist for New Website

- [ ] Research website structure
- [ ] Check robots.txt
- [ ] Add configuration to `config/settings.py`
- [ ] Create and test scraper script
- [ ] Validate data quality
- [ ] Run limited production test
- [ ] Update status documentation
- [ ] Schedule regular scraping

## 🎯 Success Metrics

- **Coverage**: Number of websites successfully scraped
- **Data Quality**: Percentage of jobs with complete data
- **Reliability**: Uptime and success rate of scrapers
- **Freshness**: How current the job data is
- **Volume**: Number of jobs scraped per day/week

---

*This workflow ensures systematic development, testing, and maintenance of job scrapers while maintaining data quality and respecting website policies.* 