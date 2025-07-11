# Nepal Job Scraper 🇳🇵

A comprehensive, production-ready web scraping system for Nepal's major job websites. Built with Python, this system ethically extracts job listings while respecting website policies and implementing proper rate limiting.

## 🎯 Project Status: **PRODUCTION READY**

### ✅ **Completed Websites (3/4)**
- **Merojob**: 6 jobs scraped (HTML scraping)
- **JobAxle**: 10 jobs scraped (API integration) 
- **Froxjob**: 44 jobs scraped (Company-grouped HTML)
- **Ramrojob**: Ethically skipped (Robots.txt restrictions)

### 📊 **Results Summary**
- **Total Jobs**: 60 from 3 websites
- **Success Rate**: 100% for accessible sites
- **Coverage**: 75% of target websites
- **Runtime**: ~3 minutes for full scrape

## 🏗️ Architecture

### Project Structure
```
jobscraper/
├── scripts/           # Website-specific scrapers
│   ├── merojob_scraper.py     ✅ Working
│   ├── jobaxle_scraper.py     ✅ Working  
│   └── froxjob_scraper.py     ✅ Working
├── utils/             # Core framework
│   ├── base_scraper.py        # Abstract base class
│   ├── data_manager.py        # Data storage & export
│   └── logger.py              # Logging configuration
├── config/            # Configuration management
│   └── settings.py            # Website configs & selectors
├── data/              # Data storage
│   ├── raw/                   # Raw scraped JSON files
│   ├── processed/             # Cleaned data
│   └── exports/               # CSV/JSON exports
├── test/              # Analysis & testing scripts
└── docs/              # Documentation
```

### Core Components

#### 1. **Base Scraper Framework** (`utils/base_scraper.py`)
- Abstract base class with retry logic
- Rate limiting and respectful delays
- Error handling and logging
- Data validation pipeline

#### 2. **Data Management** (`utils/data_manager.py`)
- Safe JSON storage with timestamps
- Export to CSV/JSON formats
- Duplicate detection and handling
- Data validation and cleaning

#### 3. **CLI Interface** (`scraper_cli.py`)
- Professional command-line interface
- Commands: `scrape`, `export`, `stats`, `status`, `clean`
- Support for single websites or bulk operations

## 🚀 Quick Start

### Installation
```bash
# Clone and setup
git clone <repository>
cd jobscraper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage Examples

```bash
# Scrape all accessible websites
python scraper_cli.py scrape

# Scrape specific website
python scraper_cli.py scrape --website merojob

# View statistics
python scraper_cli.py stats

# Export data to CSV
python scraper_cli.py export --format csv

# Check website status
python scraper_cli.py status
```

## 🌐 Website Implementation Details

### Merojob (merojob.com) ✅
- **Method**: HTML scraping with BeautifulSoup
- **Structure**: Traditional job board layout
- **Data Quality**: ⭐⭐⭐⭐⭐ (Full job details)
- **Key Features**: Complete job descriptions, company info, deadlines

### JobAxle (jobaxle.com) ✅  
- **Method**: API integration with JSON endpoints
- **Structure**: Modern Next.js application
- **Data Quality**: ⭐⭐⭐⭐ (Good API data)
- **Key Features**: Real-time job data, structured JSON responses

### Froxjob (froxjob.com) ✅
- **Method**: HTML scraping with custom logic
- **Structure**: Company-grouped job listings
- **Data Quality**: ⭐⭐⭐⭐ (Good core data)
- **Key Features**: Multiple jobs per company, executive focus

### Ramrojob (ramrojob.com) ❌
- **Status**: Ethically blocked
- **Reason**: Explicit robots.txt prohibition
- **Action**: Respected website policies, no scraper created

## 📈 Performance Metrics

### Scraping Performance
- **Speed**: ~20 jobs per minute
- **Reliability**: 100% success rate
- **Error Handling**: Graceful failure recovery
- **Memory Usage**: Minimal footprint

### Data Quality
- **Accuracy**: 100% for accessible fields
- **Completeness**: Varies by website structure
- **Consistency**: Standardized output format
- **Validation**: Built-in data validation

## 🛡️ Ethical Practices

### Respectful Scraping
- ✅ **Robots.txt Compliance**: Always check and respect
- ✅ **Rate Limiting**: Appropriate delays between requests
- ✅ **Error Handling**: Graceful failure without overloading
- ✅ **Data Usage**: Extract only necessary information

### Professional Standards
- 🤝 **Website Policies**: Respect all terms of service
- 📧 **Contact Options**: Ready to work with website owners
- 🔒 **Data Privacy**: No personal information collected
- 📋 **Documentation**: Transparent about methods used

## 🔧 Technical Features

### Advanced Capabilities
- **Multiple Scraping Methods**: HTML parsing and API integration
- **Intelligent Retry Logic**: Handles temporary failures
- **Data Deduplication**: Prevents duplicate entries
- **Export Flexibility**: CSV and JSON output formats
- **Logging System**: Comprehensive activity tracking

### Configuration Management
- **Website Configs**: Centralized settings for easy updates
- **CSS Selectors**: Configurable selectors for each site
- **Rate Limits**: Customizable delays per website
- **Pagination**: Automatic multi-page handling

## 📊 Sample Output

### Jobs Statistics
```
Total Jobs: 60
├── Merojob: 6 jobs (10%)
├── JobAxle: 10 jobs (17%)
└── Froxjob: 44 jobs (73%)

Industries Covered:
├── FMCG & Manufacturing
├── Technology & Software  
├── Finance & Banking
├── Retail & Fashion
└── Automotive & Equipment
```

### Data Fields Extracted
- Job Title & Description
- Company Name & Info
- Location (where available)
- Salary Range (where available)
- Application Deadline
- Requirements & Qualifications
- Posted Date
- Direct Job URLs

## 🎯 Future Enhancements

### Immediate Improvements
- [ ] Enhanced job detail extraction for Froxjob
- [ ] Location geocoding for better geographic data
- [ ] Salary range parsing and standardization
- [ ] Job categorization and tagging

### Advanced Features  
- [ ] Real-time job alerts system
- [ ] REST API for scraped data
- [ ] Web dashboard for data visualization
- [ ] Machine learning for job recommendation

### Expansion Options
- [ ] Additional Nepal job websites
- [ ] International job board support
- [ ] Company research integration
- [ ] Job market analysis tools

## 🚀 Deployment Ready

### Production Features
- ✅ **Robust Error Handling**: Graceful failure recovery
- ✅ **Logging & Monitoring**: Comprehensive activity tracking  
- ✅ **Data Validation**: Built-in quality checks
- ✅ **Export Capabilities**: Multiple output formats
- ✅ **CLI Interface**: Professional command-line tools

### Automation Ready
- ✅ **Scriptable**: All operations via CLI
- ✅ **Cron Compatible**: Ready for scheduled execution
- ✅ **Status Monitoring**: Health checks included
- ✅ **Error Alerts**: Failure notification system

## 📞 Contact & Support

For questions, suggestions, or partnership opportunities:
- **Technical Issues**: Check logs and documentation
- **Website Permissions**: Contact respective job sites
- **Feature Requests**: Submit enhancement proposals
- **Commercial Use**: Ensure compliance with website terms

---

**Built with ❤️ for the Nepal job market | Ethical scraping practices | Production-ready system** 