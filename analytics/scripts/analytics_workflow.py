#!/usr/bin/env python3
"""
Analytics Workflow Orchestrator for Nepal Job Scraper
Coordinates data processing, analysis, visualization, and reporting
"""

import sys
import os
from pathlib import Path
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from analytics.scripts.duplicate_detector import DuplicateDetector
from analytics.scripts.data_analyzer import DataAnalyzer
from analytics.scripts.visualizer import JobMarketVisualizer
from utils.data_manager import DataManager

@dataclass
class WorkflowConfig:
    """Configuration for analytics workflow"""
    input_data_path: str = "data/processed"
    output_path: str = "analytics/reports"
    remove_duplicates: bool = True
    duplicate_strategy: str = "keep_best_source"
    min_duplicate_confidence: float = 0.7
    generate_visualizations: bool = True
    export_formats: List[str] = None
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ["json", "csv", "html"]

class AnalyticsWorkflow:
    """Main analytics workflow orchestrator"""
    
    def __init__(self, config: WorkflowConfig = None):
        self.config = config or WorkflowConfig()
        self.logger = self._setup_logging()
        
        # Initialize components
        self.data_manager = DataManager()
        self.duplicate_detector = DuplicateDetector()
        self.data_analyzer = DataAnalyzer()
        self.visualizer = JobMarketVisualizer()
        
        # Ensure output directories exist
        self._setup_directories()
        
        # Workflow state
        self.workflow_id = self._generate_workflow_id()
        self.results = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the workflow"""
        logger = logging.getLogger('analytics_workflow')
        logger.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create file handler
        log_dir = Path(self.config.output_path) / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"analytics_workflow_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # Add handlers
        if not logger.handlers:
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
        
        return logger
    
    def _setup_directories(self):
        """Setup required directories"""
        directories = [
            self.config.output_path,
            f"{self.config.output_path}/data",
            f"{self.config.output_path}/visualizations",
            f"{self.config.output_path}/reports",
            f"{self.config.output_path}/logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _generate_workflow_id(self) -> str:
        """Generate unique workflow ID"""
        return f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def run_complete_workflow(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Run the complete analytics workflow
        
        Args:
            force_reload: Force reload data from raw files
            
        Returns:
            Dictionary containing workflow results
        """
        self.logger.info(f"Starting complete analytics workflow: {self.workflow_id}")
        
        workflow_results = {
            'workflow_id': self.workflow_id,
            'started_at': datetime.now().isoformat(),
            'config': self.config.__dict__,
            'steps': {},
            'summary': {}
        }
        
        try:
            # Step 1: Load and validate data
            self.logger.info("Step 1: Loading and validating data")
            raw_data = self._load_data(force_reload)
            workflow_results['steps']['data_loading'] = {
                'status': 'completed',
                'total_jobs': len(raw_data),
                'message': f"Loaded {len(raw_data)} job records"
            }
            
            # Step 2: Detect and handle duplicates
            if self.config.remove_duplicates:
                self.logger.info("Step 2: Detecting and removing duplicates")
                cleaned_data, duplicate_analysis = self._handle_duplicates(raw_data)
                workflow_results['steps']['duplicate_detection'] = {
                    'status': 'completed',
                    'duplicates_found': duplicate_analysis['summary']['duplicate_pairs'],
                    'jobs_after_cleaning': len(cleaned_data),
                    'duplicate_rate': duplicate_analysis['summary']['duplicate_rate']
                }
                self.results['duplicate_analysis'] = duplicate_analysis
            else:
                cleaned_data = raw_data
                workflow_results['steps']['duplicate_detection'] = {
                    'status': 'skipped',
                    'message': 'Duplicate detection disabled'
                }
            
            # Step 3: Comprehensive market analysis
            self.logger.info("Step 3: Performing market analysis")
            market_analysis = self._perform_market_analysis(cleaned_data)
            workflow_results['steps']['market_analysis'] = {
                'status': 'completed',
                'total_insights': len(market_analysis.get('insights', [])),
                'companies_analyzed': market_analysis['overview']['unique_companies'],
                'locations_analyzed': market_analysis['overview']['unique_locations']
            }
            self.results['market_analysis'] = market_analysis
            
            # Step 4: Generate visualizations
            if self.config.generate_visualizations:
                self.logger.info("Step 4: Generating visualizations")
                visualizations = self._generate_visualizations(cleaned_data, market_analysis)
                workflow_results['steps']['visualizations'] = {
                    'status': 'completed',
                    'charts_created': len(visualizations),
                    'visualization_files': visualizations
                }
                self.results['visualizations'] = visualizations
            else:
                workflow_results['steps']['visualizations'] = {
                    'status': 'skipped',
                    'message': 'Visualization generation disabled'
                }
            
            # Step 5: Export results
            self.logger.info("Step 5: Exporting results")
            exported_files = self._export_results(cleaned_data, workflow_results)
            workflow_results['steps']['export'] = {
                'status': 'completed',
                'exported_files': exported_files
            }
            
            # Step 6: Generate executive summary
            self.logger.info("Step 6: Generating executive summary")
            executive_summary = self._generate_executive_summary(workflow_results)
            workflow_results['summary'] = executive_summary
            
            workflow_results['status'] = 'completed'
            workflow_results['completed_at'] = datetime.now().isoformat()
            
            self.logger.info(f"Analytics workflow completed successfully: {self.workflow_id}")
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            workflow_results['status'] = 'failed'
            workflow_results['error'] = str(e)
            workflow_results['failed_at'] = datetime.now().isoformat()
        
        # Save workflow results
        self._save_workflow_results(workflow_results)
        
        return workflow_results
    
    def _load_data(self, force_reload: bool = False) -> List[Dict[str, Any]]:
        """Load job data from various sources"""
        
        # Try to load from processed data first
        if not force_reload:
            try:
                processed_data = self.data_manager.load_processed_data()
                if processed_data:
                    self.logger.info(f"Loaded {len(processed_data)} jobs from processed data")
                    return processed_data
            except Exception as e:
                self.logger.warning(f"Failed to load processed data: {e}")
        
        # Load from raw data files
        self.logger.info("Loading data from raw sources")
        all_jobs = []
        
        # Load from individual scraper outputs
        data_dir = Path("data/raw")
        if data_dir.exists():
            for file_path in data_dir.glob("*.json"):
                try:
                    with open(file_path, 'r') as f:
                        jobs = json.load(f)
                        if isinstance(jobs, list):
                            all_jobs.extend(jobs)
                        elif isinstance(jobs, dict) and 'jobs' in jobs:
                            all_jobs.extend(jobs['jobs'])
                    self.logger.info(f"Loaded {len(jobs)} jobs from {file_path.name}")
                except Exception as e:
                    self.logger.warning(f"Failed to load {file_path}: {e}")
        
        # Add unique IDs if not present
        for i, job in enumerate(all_jobs):
            if 'id' not in job:
                job['id'] = f"job_{i:06d}"
        
        self.logger.info(f"Total jobs loaded: {len(all_jobs)}")
        return all_jobs
    
    def _handle_duplicates(self, jobs_data: List[Dict[str, Any]]) -> tuple:
        """Detect and remove duplicates"""
        
        # Detect duplicates
        duplicate_analysis = self.duplicate_detector.detect_duplicates(jobs_data)
        
        # Remove duplicates based on configuration
        cleaned_jobs = self.duplicate_detector.remove_duplicates(
            jobs_data,
            duplicate_analysis['consolidated_duplicates'],
            strategy=self.config.duplicate_strategy
        )
        
        self.logger.info(
            f"Duplicate detection: {duplicate_analysis['summary']['duplicate_pairs']} pairs found, "
            f"{len(jobs_data) - len(cleaned_jobs)} jobs removed"
        )
        
        return cleaned_jobs, duplicate_analysis
    
    def _perform_market_analysis(self, jobs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive market analysis"""
        
        analysis = self.data_analyzer.analyze_market(jobs_data)
        
        self.logger.info(
            f"Market analysis completed: {len(analysis.get('insights', []))} insights generated"
        )
        
        return analysis
    
    def _generate_visualizations(self, jobs_data: List[Dict[str, Any]], 
                               analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all visualizations"""
        
        visualizations = self.visualizer.create_comprehensive_dashboard(jobs_data, analysis)
        
        self.logger.info(f"Generated {len(visualizations)} visualization sets")
        
        return visualizations
    
    def _export_results(self, jobs_data: List[Dict[str, Any]], 
                       workflow_results: Dict[str, Any]) -> Dict[str, str]:
        """Export all results in various formats"""
        
        exported_files = {}
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export cleaned job data
        if 'csv' in self.config.export_formats:
            csv_file = f"{self.config.output_path}/data/cleaned_jobs_{timestamp}.csv"
            df = pd.DataFrame(jobs_data)
            df.to_csv(csv_file, index=False)
            exported_files['cleaned_data_csv'] = csv_file
        
        if 'json' in self.config.export_formats:
            json_file = f"{self.config.output_path}/data/cleaned_jobs_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump(jobs_data, f, indent=2, default=str)
            exported_files['cleaned_data_json'] = json_file
        
        # Export analysis results
        if hasattr(self, 'results'):
            if 'market_analysis' in self.results:
                analysis_file = f"{self.config.output_path}/reports/market_analysis_{timestamp}.json"
                with open(analysis_file, 'w') as f:
                    json.dump(self.results['market_analysis'], f, indent=2, default=str)
                exported_files['market_analysis'] = analysis_file
            
            if 'duplicate_analysis' in self.results:
                duplicate_file = f"{self.config.output_path}/reports/duplicate_analysis_{timestamp}.json"
                with open(duplicate_file, 'w') as f:
                    json.dump(self.results['duplicate_analysis'], f, indent=2, default=str)
                exported_files['duplicate_analysis'] = duplicate_file
        
        # Export workflow results
        workflow_file = f"{self.config.output_path}/reports/workflow_results_{timestamp}.json"
        with open(workflow_file, 'w') as f:
            json.dump(workflow_results, f, indent=2, default=str)
        exported_files['workflow_results'] = workflow_file
        
        return exported_files
    
    def _generate_executive_summary(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of the analysis"""
        
        summary = {
            'overview': {
                'total_jobs_analyzed': 0,
                'unique_companies': 0,
                'unique_locations': 0,
                'data_quality_score': 0
            },
            'key_findings': [],
            'recommendations': [],
            'market_insights': []
        }
        
        # Extract overview data
        if 'market_analysis' in self.results:
            analysis = self.results['market_analysis']
            if 'overview' in analysis:
                summary['overview'].update(analysis['overview'])
            
            # Extract key insights
            if 'insights' in analysis:
                summary['market_insights'] = [
                    {
                        'category': insight['category'],
                        'description': insight['description'],
                        'confidence': insight['confidence']
                    }
                    for insight in analysis['insights']
                ]
        
        # Generate key findings
        if 'duplicate_analysis' in self.results:
            dup_analysis = self.results['duplicate_analysis']
            summary['key_findings'].append(
                f"Found {dup_analysis['summary']['duplicate_pairs']} duplicate job pairs "
                f"({dup_analysis['summary']['duplicate_rate']:.1%} duplicate rate)"
            )
        
        # Generate recommendations
        summary['recommendations'] = self._generate_recommendations()
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        if 'market_analysis' in self.results:
            analysis = self.results['market_analysis']
            
            # Salary transparency recommendation
            if 'salaries' in analysis and 'salary_transparency_rate' in analysis['salaries']:
                transparency_rate = analysis['salaries']['salary_transparency_rate']
                if transparency_rate < 30:
                    recommendations.append(
                        "Improve salary transparency: Only {:.1f}% of jobs include salary information. "
                        "Encouraging salary disclosure could improve job seeker experience.".format(transparency_rate)
                    )
            
            # Geographic diversity recommendation
            if 'locations' in analysis and 'major_city_percentage' in analysis['locations']:
                city_percentage = analysis['locations']['major_city_percentage']
                if city_percentage > 80:
                    recommendations.append(
                        "Promote job opportunities outside major cities: {:.1f}% of jobs are concentrated "
                        "in major cities. Consider promoting remote work or regional development.".format(city_percentage)
                    )
            
            # Data quality recommendation
            if 'overview' in analysis and 'data_quality_score' in analysis['overview']:
                quality_score = analysis['overview']['data_quality_score']
                if quality_score < 0.7:
                    recommendations.append(
                        f"Improve data collection: Data quality score is {quality_score:.2f}. "
                        "Consider standardizing job posting requirements across platforms."
                    )
        
        return recommendations
    
    def _save_workflow_results(self, workflow_results: Dict[str, Any]):
        """Save workflow results"""
        
        # Save detailed results
        results_file = f"{self.config.output_path}/workflow_results_{self.workflow_id}.json"
        with open(results_file, 'w') as f:
            json.dump(workflow_results, f, indent=2, default=str)
        
        # Save summary for quick access
        summary_file = f"{self.config.output_path}/latest_summary.json"
        summary = {
            'workflow_id': workflow_results['workflow_id'],
            'status': workflow_results['status'],
            'timestamp': workflow_results.get('completed_at', workflow_results.get('failed_at')),
            'summary': workflow_results.get('summary', {}),
            'files': results_file
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.logger.info(f"Workflow results saved: {results_file}")
    
    def run_quick_analysis(self, jobs_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run a quick analysis without full workflow"""
        
        if jobs_data is None:
            jobs_data = self._load_data()
        
        self.logger.info("Running quick analysis")
        
        # Quick stats
        df = pd.DataFrame(jobs_data)
        
        quick_stats = {
            'total_jobs': len(df),
            'unique_companies': df['company'].nunique() if 'company' in df.columns else 0,
            'unique_locations': df['location'].nunique() if 'location' in df.columns else 0,
            'sources': df['source'].value_counts().to_dict() if 'source' in df.columns else {},
            'top_companies': df['company'].value_counts().head(10).to_dict() if 'company' in df.columns else {},
            'top_locations': df['location'].value_counts().head(10).to_dict() if 'location' in df.columns else {},
        }
        
        return quick_stats
    
    def generate_report(self, template: str = "standard") -> str:
        """Generate a formatted report"""
        
        if not hasattr(self, 'results') or not self.results:
            raise ValueError("No analysis results available. Run workflow first.")
        
        # Generate HTML report
        html_content = self._generate_html_report(template)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"{self.config.output_path}/reports/nepal_job_market_report_{timestamp}.html"
        
        with open(report_file, 'w') as f:
            f.write(html_content)
        
        self.logger.info(f"Report generated: {report_file}")
        return report_file
    
    def _generate_html_report(self, template: str) -> str:
        """Generate HTML report content"""
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Nepal Job Market Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                .summary {{ background-color: #ecf0f1; padding: 20px; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background-color: #3498db; color: white; border-radius: 5px; }}
                .insight {{ margin: 10px 0; padding: 10px; border-left: 4px solid #e74c3c; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Nepal Job Market Analysis Report</h1>
            <p>Generated on: {timestamp}</p>
            
            <div class="summary">
                <h2>Executive Summary</h2>
                {executive_summary}
            </div>
            
            <h2>Key Metrics</h2>
            {key_metrics}
            
            <h2>Market Insights</h2>
            {market_insights}
            
            <h2>Recommendations</h2>
            {recommendations}
            
        </body>
        </html>
        """
        
        # Populate template with actual data
        executive_summary = "Nepal job market analysis completed successfully."
        key_metrics = ""
        market_insights = ""
        recommendations = ""
        
        if 'market_analysis' in self.results:
            analysis = self.results['market_analysis']
            
            # Key metrics
            if 'overview' in analysis:
                overview = analysis['overview']
                key_metrics = f"""
                <div class="metric">Total Jobs: {overview.get('total_jobs', 0)}</div>
                <div class="metric">Companies: {overview.get('unique_companies', 0)}</div>
                <div class="metric">Locations: {overview.get('unique_locations', 0)}</div>
                <div class="metric">Quality Score: {overview.get('data_quality_score', 0):.2f}</div>
                """
            
            # Market insights
            if 'insights' in analysis:
                insights_html = ""
                for insight in analysis['insights']:
                    insights_html += f'<div class="insight">{insight["description"]}</div>'
                market_insights = insights_html
        
        return html_template.format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            executive_summary=executive_summary,
            key_metrics=key_metrics,
            market_insights=market_insights,
            recommendations=recommendations
        )

def main():
    """Main function for testing the workflow"""
    
    # Create workflow with custom config
    config = WorkflowConfig(
        remove_duplicates=True,
        generate_visualizations=True,
        export_formats=["json", "csv"]
    )
    
    workflow = AnalyticsWorkflow(config)
    
    print("=== Nepal Job Market Analytics Workflow ===")
    print(f"Workflow ID: {workflow.workflow_id}")
    
    # Run complete workflow
    results = workflow.run_complete_workflow()
    
    print(f"\nWorkflow Status: {results['status']}")
    
    if results['status'] == 'completed':
        print("\n=== Workflow Summary ===")
        for step_name, step_result in results['steps'].items():
            print(f"{step_name}: {step_result['status']}")
            if 'message' in step_result:
                print(f"  - {step_result['message']}")
        
        # Generate report
        try:
            report_file = workflow.generate_report()
            print(f"\nReport generated: {report_file}")
        except Exception as e:
            print(f"Report generation failed: {e}")
    
    else:
        print(f"Workflow failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 