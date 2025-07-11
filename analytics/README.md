# Nepal Job Market Analytics System

A comprehensive analytics platform for analyzing the Nepal job market with advanced duplicate detection, market insights, visualizations, and reporting capabilities.

## 🚀 Features

### Core Analytics
- **Duplicate Detection**: Advanced multi-algorithm duplicate detection with fuzzy matching and semantic analysis
- **Market Analysis**: Comprehensive job market insights including company analysis, location trends, and salary statistics
- **Data Visualization**: Interactive charts, graphs, and dashboards for market visualization
- **Report Generation**: Automated HTML reports with executive summaries and recommendations

### Advanced Capabilities
- **Multi-Source Analysis**: Analyze jobs from multiple job portals simultaneously
- **Cross-Source Duplicate Detection**: Find duplicates across different job platforms
- **Robust Data Quality Assessment**: Comprehensive data quality scoring and validation
- **Web Dashboard**: Professional web interface for viewing analytics
- **API Integration**: RESTful API for accessing analytics data

## 📁 Project Structure

```
analytics/
├── scripts/                    # Core analytics scripts
│   ├── duplicate_detector.py   # Advanced duplicate detection system
│   ├── data_analyzer.py       # Market analysis engine
│   ├── visualizer.py          # Data visualization system
│   └── analytics_workflow.py  # Workflow orchestrator
├── dashboards/                # Web dashboard components
│   ├── web_dashboard.py       # Flask web application
│   └── templates/             # HTML templates
├── tests/                     # Test suite
│   └── test_analytics.py      # Comprehensive tests
├── workflows/                 # Workflow definitions
├── reports/                   # Generated reports and outputs
│   ├── data/                  # Processed data exports
│   ├── visualizations/        # Chart and graph outputs
│   └── logs/                  # System logs
└── run_analytics.py          # Main CLI interface
```

## 🛠 Installation & Setup

### Prerequisites
```bash
# Python packages (install in virtual environment)
pip install pandas numpy matplotlib seaborn plotly
pip install scikit-learn flask beautifulsoup4 requests
pip install pydantic-settings
```

### Quick Start
```bash
# 1. Run quick analysis
python analytics/run_analytics.py workflow --quick

# 2. Start web dashboard
python analytics/run_analytics.py dashboard

# 3. Run comprehensive analysis
python analytics/run_analytics.py workflow --generate-report
```

## 📊 Analytics Components

### 1. Duplicate Detection (`duplicate_detector.py`)

Advanced duplicate detection system with multiple algorithms:

#### Detection Methods
- **Exact Duplicates**: Fingerprint-based exact matching
- **Fuzzy Duplicates**: String similarity using sequence matching
- **Semantic Duplicates**: TF-IDF and cosine similarity analysis
- **Cross-Source Duplicates**: Inter-platform duplicate detection

#### Configuration
```python
config = {
    'similarity_thresholds': {
        'exact_match': 1.0,
        'high_similarity': 0.9,
        'medium_similarity': 0.7,
        'low_similarity': 0.5
    },
    'weights': {
        'title': 0.4,
        'company': 0.3,
        'location': 0.15,
        'description': 0.1,
        'salary': 0.05
    }
}
```

#### Usage
```python
from analytics.scripts.duplicate_detector import DuplicateDetector

detector = DuplicateDetector()
results = detector.detect_duplicates(jobs_data)

# Remove duplicates
cleaned_jobs = detector.remove_duplicates(
    jobs_data, 
    results['consolidated_duplicates'],
    strategy='keep_best_source'
)
```

### 2. Market Analysis (`data_analyzer.py`)

Comprehensive market analysis engine providing:

#### Analysis Categories
- **Overview Statistics**: Job counts, companies, locations, data quality
- **Company Analysis**: Top hirers, hiring patterns, company diversity
- **Location Analysis**: Geographic distribution, city concentration
- **Salary Analysis**: Salary statistics, ranges, transparency rates
- **Skills Demand**: Most in-demand skills and technologies
- **Market Trends**: Posting trends and growth patterns

#### Usage
```python
from analytics.scripts.data_analyzer import DataAnalyzer

analyzer = DataAnalyzer()
analysis = analyzer.analyze_market(jobs_data)

# Export results
analyzer.export_analysis(analysis, 'market_analysis.json')
```

### 3. Visualization System (`visualizer.py`)

Interactive visualization system creating:

#### Visualization Types
- **Overview Dashboards**: Multi-panel overview charts
- **Company Analysis**: Hiring company rankings and trends
- **Location Heatmaps**: Geographic job distribution
- **Salary Analysis**: Salary distribution and comparisons
- **Skills Demand Charts**: Most requested skills
- **Source Comparisons**: Job portal comparisons

#### Usage
```python
from analytics.scripts.visualizer import JobMarketVisualizer

visualizer = JobMarketVisualizer()
charts = visualizer.create_comprehensive_dashboard(jobs_data, analysis)
```

### 4. Workflow Orchestrator (`analytics_workflow.py`)

Main workflow coordinator managing:

#### Workflow Steps
1. **Data Loading**: Load and validate job data
2. **Duplicate Detection**: Find and remove duplicates
3. **Market Analysis**: Comprehensive market analysis
4. **Visualization**: Generate charts and graphs
5. **Export**: Export results in multiple formats
6. **Reporting**: Generate executive summaries

#### Configuration
```python
config = WorkflowConfig(
    remove_duplicates=True,
    duplicate_strategy='keep_best_source',
    generate_visualizations=True,
    export_formats=['json', 'csv', 'html']
)
```

## 🌐 Web Dashboard

Professional web interface providing:

### Dashboard Features
- **Real-time Analytics**: Live job market statistics
- **Interactive Charts**: Clickable and filterable visualizations
- **Report Gallery**: Access to all generated reports
- **API Endpoints**: RESTful API for data access
- **Responsive Design**: Mobile-friendly interface

### Starting the Dashboard
```bash
# Start on default port (5000)
python analytics/run_analytics.py dashboard

# Custom host and port
python analytics/run_analytics.py dashboard --host 0.0.0.0 --port 8080

# Debug mode
python analytics/run_analytics.py dashboard --debug
```

### Dashboard URLs
- **Main Dashboard**: http://localhost:5000/
- **Visualizations**: http://localhost:5000/visualizations
- **Analysis**: http://localhost:5000/analysis
- **Reports**: http://localhost:5000/reports
- **API Stats**: http://localhost:5000/api/stats

## 🧪 Testing

Comprehensive test suite covering all components:

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Data Quality Tests**: Data validation and integrity
- **Performance Tests**: System performance validation

### Running Tests
```bash
# Run all tests
python analytics/run_analytics.py test

# Run specific test class
python analytics/run_analytics.py test --test-class TestDuplicateDetector

# Verbose output
python analytics/run_analytics.py test --verbose
```

## 📋 CLI Usage

Complete command-line interface for all analytics operations:

### Available Commands

#### Workflow Operations
```bash
# Quick analysis (fast overview)
python analytics/run_analytics.py workflow --quick

# Complete analysis
python analytics/run_analytics.py workflow

# Force data reload
python analytics/run_analytics.py workflow --force-reload

# Skip visualizations (faster)
python analytics/run_analytics.py workflow --no-viz

# Keep duplicates
python analytics/run_analytics.py workflow --keep-duplicates

# Generate HTML report
python analytics/run_analytics.py workflow --generate-report
```

#### Dashboard Operations
```bash
# Start dashboard
python analytics/run_analytics.py dashboard

# Custom configuration
python analytics/run_analytics.py dashboard --host 0.0.0.0 --port 8080 --debug
```

#### Testing Operations
```bash
# Run all tests
python analytics/run_analytics.py test

# Specific test class
python analytics/run_analytics.py test --test-class TestDataAnalyzer

# Verbose testing
python analytics/run_analytics.py test --verbose
```

#### System Operations
```bash
# Check system status
python analytics/run_analytics.py status

# Clean analytics data
python analytics/run_analytics.py clean

# Clean all data (destructive)
python analytics/run_analytics.py clean --all
```

## 📈 Sample Outputs

### Quick Analysis Output
```
==================================================
QUICK ANALYSIS RESULTS
==================================================
Total Jobs: 347
Unique Companies: 89
Unique Locations: 23

Jobs by Source:
  jobkunja: 108
  merojob: 78
  jobaxle: 52
  hamrojobs: 48
  kantipurjob: 45
  froxjob: 44
  mustakbil: 3
```

### Duplicate Detection Results
```
Duplicate Detection Results:
- Total jobs: 347
- Duplicate pairs found: 12
- Duplicate rate: 6.9%
- Estimated unique jobs: 335

Confidence Distribution:
- High confidence: 8 pairs
- Medium confidence: 3 pairs
- Low confidence: 1 pair
```

### Market Insights
```
Key Market Insights:
- Nepal job market has 347 active job listings across 7 platforms
- Tech Corp is the most active hirer with 8 job openings
- Only 23.5% of jobs provide salary information
- 78.4% of jobs are concentrated in major cities
```

## 🔧 Configuration

### Duplicate Detection Configuration
```python
duplicate_config = {
    'similarity_thresholds': {
        'exact_match': 1.0,
        'high_similarity': 0.9,
        'medium_similarity': 0.7
    },
    'weights': {
        'title': 0.4,
        'company': 0.3,
        'location': 0.15,
        'description': 0.1
    },
    'min_confidence': 0.6
}
```

### Visualization Configuration
```python
viz_config = {
    'output_dir': 'analytics/reports/visualizations',
    'figure_size': (12, 8),
    'color_palette': ['#1f77b4', '#ff7f0e', '#2ca02c'],
    'export_formats': ['png', 'html']
}
```

### Workflow Configuration
```python
workflow_config = WorkflowConfig(
    input_data_path="data/processed",
    output_path="analytics/reports",
    remove_duplicates=True,
    duplicate_strategy="keep_best_source",
    generate_visualizations=True,
    export_formats=["json", "csv", "html"]
)
```

## 📊 Data Quality

The analytics system includes comprehensive data quality assessment:

### Quality Metrics
- **Completeness**: Percentage of filled fields
- **Consistency**: Data format standardization
- **Accuracy**: Validation against expected patterns
- **Uniqueness**: Duplicate detection and handling
- **Timeliness**: Data freshness indicators

### Quality Score Calculation
```python
quality_score = (
    title_completeness * 0.3 +
    company_completeness * 0.3 +
    location_completeness * 0.2 +
    salary_completeness * 0.1 +
    description_completeness * 0.1
)
```

## 🚀 Performance Optimization

### Optimization Features
- **Caching**: Intelligent caching for repeated operations
- **Parallel Processing**: Multi-threaded analysis where possible
- **Memory Management**: Efficient memory usage for large datasets
- **Incremental Updates**: Process only new/changed data

### Performance Tips
```bash
# For large datasets, disable visualizations initially
python analytics/run_analytics.py workflow --no-viz

# Use quick analysis for rapid insights
python analytics/run_analytics.py workflow --quick

# Clean old data regularly
python analytics/run_analytics.py clean
```

## 📝 API Documentation

### REST API Endpoints

#### GET /api/stats
Returns quick statistics about the job market.

**Response:**
```json
{
  "total_jobs": 347,
  "unique_companies": 89,
  "unique_locations": 23,
  "sources": {
    "jobkunja": 108,
    "merojob": 78
  }
}
```

#### GET /api/latest
Returns the latest complete analysis results.

**Response:**
```json
{
  "status": "success",
  "data": {
    "summary": {...},
    "details": {...},
    "last_updated": "2024-01-15T10:30:00Z"
  }
}
```

## 🐛 Troubleshooting

### Common Issues

#### "No data available" Error
```bash
# Solution: Run scrapers first to collect data
python scraper_cli.py scrape --max-pages 5

# Then run analytics
python analytics/run_analytics.py workflow --quick
```

#### Dashboard Not Loading
```bash
# Check if Flask is installed
pip install flask

# Verify templates are created
python analytics/run_analytics.py dashboard --debug
```

#### Memory Issues with Large Datasets
```bash
# Use quick analysis
python analytics/run_analytics.py workflow --quick --no-viz

# Or clean old data
python analytics/run_analytics.py clean
```

### Debug Mode
```bash
# Enable debug logging
python analytics/run_analytics.py workflow --log-level DEBUG

# Check system status
python analytics/run_analytics.py status
```

## 🔮 Future Enhancements

### Planned Features
- **Machine Learning Integration**: Predictive job market analysis
- **Real-time Monitoring**: Live job market monitoring
- **Advanced NLP**: Job description analysis and skill extraction
- **Recommendation Engine**: Job and candidate matching
- **Mobile Dashboard**: Mobile-optimized analytics interface

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📞 Support

For support and questions:
- Check the troubleshooting section above
- Run system diagnostics: `python analytics/run_analytics.py status`
- Review logs in `analytics/reports/logs/`
- Create an issue in the project repository

---

**Nepal Job Market Analytics System** - Comprehensive job market intelligence for informed decision-making. 