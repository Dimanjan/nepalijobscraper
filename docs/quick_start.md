# Quick Start Guide - Nepal Job Scraper

Get up and running with the Nepal job scraper in 5 minutes!

## 🚀 Installation

### Step 1: Setup Environment
```bash
# Navigate to project directory
cd jobscraper

# Run automated setup
python3 setup.py
```

The setup script will:
- ✅ Check Python version (3.8+ required)
- 📁 Create directory structure
- 📦 Install all dependencies
- 🔧 Configure CLI tools

### Step 2: Verify Installation
```bash
# Check if everything is working
python3 scraper_cli.py --help
```

You should see the available commands for the scraper.

## 🧪 First Test

### Test Website Connectivity
```bash
# Run sample connectivity tests
python3 test/sample_test.py
```

This will:
- Test connections to Nepal job websites
- Check robots.txt files
- Save sample HTML for analysis

### Check Status
```bash
# See which scrapers are available
python3 scraper_cli.py status
```

## 🔧 Create Your First Scraper

### Step 1: Generate Scraper Template
```bash
# Create a scraper for Merojob (most popular site)
python3 scraper_cli.py create-script merojob
```

This creates a template script at `scripts/merojob_scraper.py`

### Step 2: Test the Scraper
```bash
# Run a limited test (2 pages only)
python3 scraper_cli.py scrape merojob --test-mode
```

### Step 3: Check Results
```bash
# View scraping statistics
python3 scraper_cli.py stats

# Export data to CSV
python3 scraper_cli.py export --website merojob --format csv
```

## 📊 Common Commands

### Scraping Operations
```bash
# Scrape specific website
python3 scraper_cli.py scrape merojob --max-pages 5

# Scrape all configured websites
python3 scraper_cli.py scrape --test-mode

# Test mode (limited pages)
python3 scraper_cli.py scrape merojob --test-mode
```

### Data Management
```bash
# View statistics
python3 scraper_cli.py stats

# Export all data
python3 scraper_cli.py export --format csv

# Clean duplicates
python3 scraper_cli.py clean

# Check scraper status
python3 scraper_cli.py status
```

### Development Workflow
```bash
# Create new scraper
python3 scraper_cli.py create-script <website>

# Test scraper in development
python3 scraper_cli.py test-script <website>

# Copy to test folder for experimentation
python3 scraper_cli.py test-script merojob
```

## 🎯 Target Websites

The scraper is pre-configured for these Nepal job websites:

| Website | Priority | Status |
|---------|----------|--------|
| Merojob | High | 🔍 Research |
| JobAxle | High | 🔍 Research | 
| Froxjob | Medium | 🔍 Research |
| Ramrojob | Medium | 🔍 Research |

## 📁 Project Structure

```
jobscraper/
├── scripts/           # Production scrapers
├── test/             # Testing and experimentation  
├── data/             # Scraped data (safe storage)
│   ├── raw/          # Raw scraped data
│   ├── processed/    # Cleaned data
│   └── exports/      # CSV/JSON exports
├── config/           # Configuration files
├── utils/            # Utility classes
└── docs/             # Documentation
```

## 🔧 Configuration

### Website Settings
Edit `config/settings.py` to customize:
- Website URLs and selectors
- Rate limiting and delays
- Data fields to extract
- Priority order for scraping

### Environment Variables
Create `.env` file for sensitive settings:
```bash
SCRAPER_LOG_LEVEL=INFO
SCRAPER_DEFAULT_DELAY=1.0
SCRAPER_MAX_RETRIES=3
```

## 🛠️ Troubleshooting

### Common Issues

**"ModuleNotFoundError"**
```bash
# Install dependencies manually
pip3 install -r requirements.txt
```

**"Permission denied"**
```bash
# Make scripts executable
chmod +x scraper_cli.py setup.py
```

**"No jobs found"**
- Check if website structure changed
- Update selectors in configuration
- Test with sample_test.py first

**"Rate limited"**
- Increase delays in config/settings.py
- Check robots.txt compliance
- Use test mode for development

### Getting Help

1. **Read the documentation**: `docs/workflow.md`
2. **Check logs**: `logs/scraper_YYYYMMDD.log`  
3. **Test connectivity**: `python3 test/sample_test.py`
4. **View CLI help**: `python3 scraper_cli.py --help`

## 🎉 Next Steps

1. **Start with Merojob**: Most popular, good for learning
2. **Research other sites**: Use test scripts to understand structure  
3. **Customize selectors**: Update based on actual website HTML
4. **Scale up**: Once working, increase page limits
5. **Automate**: Set up scheduling for regular scraping

---

📖 **For detailed workflow**: See `docs/workflow.md`  
🔧 **For configuration**: See `config/settings.py`  
📊 **For website tracking**: See `docs/website_status.md` 