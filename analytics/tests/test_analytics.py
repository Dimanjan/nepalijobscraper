#!/usr/bin/env python3
"""
Comprehensive Test Suite for Nepal Job Market Analytics
Tests all analytics components including duplicate detection, data analysis, and visualization
"""

import sys
import os
import unittest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from analytics.scripts.duplicate_detector import DuplicateDetector, DuplicateMatch
from analytics.scripts.data_analyzer import DataAnalyzer, MarketInsight
from analytics.scripts.visualizer import JobMarketVisualizer
from analytics.scripts.analytics_workflow import AnalyticsWorkflow, WorkflowConfig

class TestDuplicateDetector(unittest.TestCase):
    """Test cases for duplicate detection system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = DuplicateDetector()
        self.sample_jobs = [
            {
                'id': '1',
                'title': 'Software Engineer',
                'company': 'Tech Corp Pvt Ltd',
                'location': 'Kathmandu',
                'source': 'merojob'
            },
            {
                'id': '2',
                'title': 'Software Engineer',
                'company': 'Tech Corp',
                'location': 'Kathmandu',
                'source': 'jobaxle'
            },
            {
                'id': '3',
                'title': 'Senior Software Developer',
                'company': 'Tech Corporation',
                'location': 'Kathmandu',
                'source': 'froxjob'
            },
            {
                'id': '4',
                'title': 'Marketing Manager',
                'company': 'Marketing Plus',
                'location': 'Lalitpur',
                'source': 'merojob'
            }
        ]
    
    def test_detect_duplicates(self):
        """Test basic duplicate detection"""
        results = self.detector.detect_duplicates(self.sample_jobs)
        
        # Check that results contain expected keys
        self.assertIn('exact_duplicates', results)
        self.assertIn('fuzzy_duplicates', results)
        self.assertIn('summary', results)
        
        # Check summary structure
        summary = results['summary']
        self.assertIn('total_jobs', summary)
        self.assertIn('duplicate_pairs', summary)
        self.assertIn('duplicate_rate', summary)
        
        self.assertEqual(summary['total_jobs'], 4)
    
    def test_exact_duplicates(self):
        """Test exact duplicate detection"""
        # Create exact duplicates
        duplicate_jobs = [
            {'id': '1', 'title': 'Developer', 'company': 'TechCorp', 'location': 'KTM'},
            {'id': '2', 'title': 'Developer', 'company': 'TechCorp', 'location': 'KTM'}
        ]
        
        results = self.detector.detect_duplicates(duplicate_jobs)
        exact_duplicates = results['exact_duplicates']
        
        # Should find at least one exact duplicate pair
        self.assertGreater(len(exact_duplicates), 0)
    
    def test_fuzzy_duplicates(self):
        """Test fuzzy duplicate detection"""
        results = self.detector.detect_duplicates(self.sample_jobs)
        fuzzy_duplicates = results['fuzzy_duplicates']
        
        # Should be a list (may be empty)
        self.assertIsInstance(fuzzy_duplicates, list)
        
        # If duplicates found, check structure
        if fuzzy_duplicates:
            duplicate = fuzzy_duplicates[0]
            self.assertIsInstance(duplicate, DuplicateMatch)
            self.assertIsInstance(duplicate.similarity_score, float)
            self.assertGreaterEqual(duplicate.confidence, 0)
            self.assertLessEqual(duplicate.confidence, 1)
    
    def test_remove_duplicates(self):
        """Test duplicate removal functionality"""
        results = self.detector.detect_duplicates(self.sample_jobs)
        duplicates = results['consolidated_duplicates']
        
        cleaned_jobs = self.detector.remove_duplicates(
            self.sample_jobs, duplicates, strategy='keep_first'
        )
        
        # Cleaned jobs should be <= original jobs
        self.assertLessEqual(len(cleaned_jobs), len(self.sample_jobs))
        
        # All remaining jobs should have unique IDs
        job_ids = [job['id'] for job in cleaned_jobs]
        self.assertEqual(len(job_ids), len(set(job_ids)))

class TestDataAnalyzer(unittest.TestCase):
    """Test cases for data analysis system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = DataAnalyzer()
        self.sample_jobs = [
            {
                'id': '1',
                'title': 'Senior Software Engineer',
                'company': 'Tech Corp Pvt Ltd',
                'location': 'Kathmandu, Nepal',
                'salary': 'Rs. 80,000',
                'source': 'merojob',
                'scraped_date': '2024-01-15'
            },
            {
                'id': '2',
                'title': 'Marketing Manager',
                'company': 'Marketing Plus',
                'location': 'Lalitpur',
                'salary': 'Rs. 45,000',
                'source': 'jobaxle',
                'scraped_date': '2024-01-15'
            },
            {
                'id': '3',
                'title': 'Python Developer',
                'company': 'Tech Solutions',
                'location': 'Kathmandu',
                'salary': 'Rs. 60,000',
                'source': 'froxjob',
                'scraped_date': '2024-01-16'
            }
        ] * 20  # Multiply to have more data points
    
    def test_analyze_market(self):
        """Test market analysis functionality"""
        analysis = self.analyzer.analyze_market(self.sample_jobs)
        
        # Check main sections exist
        expected_sections = [
            'overview', 'companies', 'locations', 'job_types',
            'salaries', 'skills_demand', 'source_analysis',
            'market_trends', 'insights'
        ]
        
        for section in expected_sections:
            self.assertIn(section, analysis)
    
    def test_overview_analysis(self):
        """Test overview statistics"""
        analysis = self.analyzer.analyze_market(self.sample_jobs)
        overview = analysis['overview']
        
        # Check required metrics
        self.assertIn('total_jobs', overview)
        self.assertIn('unique_companies', overview)
        self.assertIn('unique_locations', overview)
        self.assertIn('data_quality_score', overview)
        
        # Verify values make sense
        self.assertEqual(overview['total_jobs'], len(self.sample_jobs))
        self.assertGreater(overview['unique_companies'], 0)
        self.assertGreaterEqual(overview['data_quality_score'], 0)
        self.assertLessEqual(overview['data_quality_score'], 1)
    
    def test_salary_analysis(self):
        """Test salary analysis"""
        analysis = self.analyzer.analyze_market(self.sample_jobs)
        salary_analysis = analysis['salaries']
        
        if 'salary_statistics' in salary_analysis:
            stats = salary_analysis['salary_statistics']
            self.assertIn('mean', stats)
            self.assertIn('median', stats)
            self.assertIn('min', stats)
            self.assertIn('max', stats)
            
            # Basic sanity checks
            self.assertGreaterEqual(stats['min'], 0)
            self.assertGreaterEqual(stats['max'], stats['min'])
    
    def test_insights_generation(self):
        """Test market insights generation"""
        analysis = self.analyzer.analyze_market(self.sample_jobs)
        insights = analysis['insights']
        
        # Should generate some insights
        self.assertIsInstance(insights, list)
        
        # If insights exist, check structure
        if insights:
            insight = insights[0]
            self.assertIsInstance(insight, dict)
            self.assertIn('category', insight)
            self.assertIn('description', insight)
            self.assertIn('confidence', insight)
    
    def test_export_analysis(self):
        """Test analysis export functionality"""
        analysis = self.analyzer.analyze_market(self.sample_jobs)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = f"{temp_dir}/test_analysis.json"
            exported_file = self.analyzer.export_analysis(analysis, output_file)
            
            # Check file was created
            self.assertTrue(os.path.exists(exported_file))
            
            # Check file content
            with open(exported_file, 'r') as f:
                exported_data = json.load(f)
            
            self.assertIn('overview', exported_data)

class TestJobMarketVisualizer(unittest.TestCase):
    """Test cases for visualization system"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock config to avoid file creation
        config = {
            'output_dir': tempfile.gettempdir(),
            'figure_size': (10, 6),
            'export_formats': ['html']
        }
        self.visualizer = JobMarketVisualizer(config)
        
        self.sample_jobs = [
            {
                'id': str(i),
                'title': f'Job {i}',
                'company': f'Company {i % 5}',
                'location': f'Location {i % 3}',
                'salary': f'Rs. {20000 + i * 1000}',
                'source': f'source{i % 2}'
            }
            for i in range(50)
        ]
    
    def test_create_overview_dashboard(self):
        """Test overview dashboard creation"""
        import pandas as pd
        df = pd.DataFrame(self.sample_jobs)
        
        # Mock the visualization creation to avoid file operations
        with patch.object(self.visualizer, '_extract_job_categories') as mock_categories:
            mock_categories.return_value = ['Tech'] * len(df)
            
            result = self.visualizer.create_overview_dashboard(df)
            
            # Should return dict with file paths
            self.assertIsInstance(result, dict)
    
    def test_extract_salary_data(self):
        """Test salary data extraction"""
        import pandas as pd
        df = pd.DataFrame(self.sample_jobs)
        
        salary_data = self.visualizer._extract_salary_data(df)
        
        # Should return DataFrame
        self.assertIsInstance(salary_data, pd.DataFrame)
        
        # If data exists, check structure
        if not salary_data.empty:
            self.assertIn('salary', salary_data.columns)
    
    def test_extract_job_categories(self):
        """Test job category extraction"""
        import pandas as pd
        
        titles = pd.Series([
            'Software Engineer',
            'Marketing Manager',
            'Data Scientist',
            'Sales Representative'
        ])
        
        categories = self.visualizer._extract_job_categories(titles)
        
        # Should return list of same length
        self.assertEqual(len(categories), len(titles))
        
        # Should contain valid categories
        valid_categories = ['Technology', 'Management', 'Sales & Marketing', 'Other']
        for category in categories:
            self.assertIn(category, valid_categories)

class TestAnalyticsWorkflow(unittest.TestCase):
    """Test cases for analytics workflow orchestrator"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create config with temporary directories
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config = WorkflowConfig(
            input_data_path=self.temp_dir.name,
            output_path=self.temp_dir.name,
            remove_duplicates=True,
            generate_visualizations=False  # Disable to speed up tests
        )
        self.workflow = AnalyticsWorkflow(self.config)
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.temp_dir.cleanup()
    
    def test_workflow_initialization(self):
        """Test workflow initialization"""
        self.assertIsNotNone(self.workflow.workflow_id)
        self.assertIsInstance(self.workflow.config, WorkflowConfig)
        self.assertIsNotNone(self.workflow.logger)
    
    def test_generate_workflow_id(self):
        """Test workflow ID generation"""
        workflow_id = self.workflow._generate_workflow_id()
        
        # Should be string starting with 'workflow_'
        self.assertIsInstance(workflow_id, str)
        self.assertTrue(workflow_id.startswith('workflow_'))
    
    def test_load_data_empty(self):
        """Test data loading with no data"""
        # Should return empty list when no data files exist
        data = self.workflow._load_data()
        self.assertIsInstance(data, list)
    
    def test_quick_analysis(self):
        """Test quick analysis functionality"""
        # Create sample data
        sample_jobs = [
            {'id': '1', 'title': 'Engineer', 'company': 'TechCorp', 'location': 'KTM'},
            {'id': '2', 'title': 'Manager', 'company': 'BizCorp', 'location': 'PKR'}
        ]
        
        quick_stats = self.workflow.run_quick_analysis(sample_jobs)
        
        # Check required fields
        self.assertIn('total_jobs', quick_stats)
        self.assertIn('unique_companies', quick_stats)
        self.assertIn('unique_locations', quick_stats)
        
        self.assertEqual(quick_stats['total_jobs'], 2)

class TestIntegration(unittest.TestCase):
    """Integration tests for the entire analytics system"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.sample_jobs = [
            {
                'id': '1',
                'title': 'Senior Software Engineer',
                'company': 'Tech Corp Pvt Ltd',
                'location': 'Kathmandu',
                'salary': 'Rs. 80,000',
                'source': 'merojob',
                'description': 'Python, Django, React',
                'scraped_date': '2024-01-15'
            },
            {
                'id': '2',
                'title': 'Software Engineer',
                'company': 'Tech Corp',
                'location': 'Kathmandu',
                'salary': 'Rs. 75,000',
                'source': 'jobaxle',
                'description': 'Java, Spring, Angular',
                'scraped_date': '2024-01-15'
            },
            {
                'id': '3',
                'title': 'Marketing Manager',
                'company': 'Marketing Solutions',
                'location': 'Lalitpur',
                'salary': 'Rs. 50,000',
                'source': 'froxjob',
                'description': 'Digital marketing, SEO',
                'scraped_date': '2024-01-16'
            }
        ] * 10  # Multiply for more realistic data size
    
    def test_full_analytics_pipeline(self):
        """Test the complete analytics pipeline"""
        # 1. Duplicate Detection
        detector = DuplicateDetector()
        duplicate_results = detector.detect_duplicates(self.sample_jobs)
        
        self.assertIn('summary', duplicate_results)
        self.assertGreaterEqual(duplicate_results['summary']['total_jobs'], 0)
        
        # 2. Data Analysis
        analyzer = DataAnalyzer()
        analysis_results = analyzer.analyze_market(self.sample_jobs)
        
        self.assertIn('overview', analysis_results)
        self.assertIn('insights', analysis_results)
        
        # 3. Check data flow between components
        total_jobs = len(self.sample_jobs)
        analyzed_jobs = analysis_results['overview']['total_jobs']
        
        self.assertEqual(total_jobs, analyzed_jobs)
    
    def test_data_quality_preservation(self):
        """Test that data quality is preserved through the pipeline"""
        # Start with known data
        original_job_count = len(self.sample_jobs)
        original_companies = set(job['company'] for job in self.sample_jobs)
        
        # Run through analysis
        analyzer = DataAnalyzer()
        analysis = analyzer.analyze_market(self.sample_jobs)
        
        # Check data integrity
        self.assertEqual(analysis['overview']['total_jobs'], original_job_count)
        self.assertLessEqual(analysis['overview']['unique_companies'], len(original_companies))
    
    def test_error_handling(self):
        """Test error handling with malformed data"""
        # Create malformed data
        bad_jobs = [
            {'id': '1'},  # Missing required fields
            {'title': 'Engineer'},  # Missing ID
            {'id': '2', 'title': None, 'company': ''}  # Null/empty values
        ]
        
        # Should not crash
        analyzer = DataAnalyzer()
        try:
            analysis = analyzer.analyze_market(bad_jobs)
            # Should complete without error
            self.assertIsInstance(analysis, dict)
        except Exception as e:
            self.fail(f"Analysis failed with malformed data: {e}")

def run_test_suite():
    """Run the complete test suite"""
    
    # Create test suite
    test_classes = [
        TestDuplicateDetector,
        TestDataAnalyzer,
        TestJobMarketVisualizer,
        TestAnalyticsWorkflow,
        TestIntegration
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()

def main():
    """Main function to run tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Nepal Job Analytics Test Suite')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--test', '-t', help='Run specific test class')
    
    args = parser.parse_args()
    
    if args.test:
        # Run specific test
        test_class = globals().get(args.test)
        if test_class and issubclass(test_class, unittest.TestCase):
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
            result = runner.run(suite)
            return result.wasSuccessful()
        else:
            print(f"Test class '{args.test}' not found")
            return False
    else:
        # Run all tests
        return run_test_suite()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 