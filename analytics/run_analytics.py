#!/usr/bin/env python3
"""
Nepal Job Market Analytics Runner
Main entry point for running analytics workflows, tests, and dashboard
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from analytics.scripts.analytics_workflow import AnalyticsWorkflow, WorkflowConfig
from analytics.dashboards.web_dashboard import run_dashboard

def setup_logging(log_level='INFO'):
    """Setup logging configuration"""
    
    log_dir = Path("analytics/reports/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"analytics_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def run_workflow(args):
    """Run analytics workflow"""
    
    logger = setup_logging(args.log_level)
    logger.info("Starting Nepal Job Market Analytics")
    
    # Create configuration
    config = WorkflowConfig(
        remove_duplicates=not args.keep_duplicates,
        duplicate_strategy=args.duplicate_strategy,
        generate_visualizations=not args.no_viz,
        export_formats=args.export_formats
    )
    
    # Initialize and run workflow
    workflow = AnalyticsWorkflow(config)
    
    try:
        if args.quick:
            logger.info("Running quick analysis")
            results = workflow.run_quick_analysis()
            
            print("\n" + "="*50)
            print("QUICK ANALYSIS RESULTS")
            print("="*50)
            print(f"Total Jobs: {results.get('total_jobs', 0)}")
            print(f"Unique Companies: {results.get('unique_companies', 0)}")
            print(f"Unique Locations: {results.get('unique_locations', 0)}")
            
            if 'sources' in results:
                print(f"\nJobs by Source:")
                for source, count in results['sources'].items():
                    print(f"  {source}: {count}")
            
        else:
            logger.info("Running complete workflow")
            results = workflow.run_complete_workflow(force_reload=args.force_reload)
            
            print("\n" + "="*50)
            print("WORKFLOW RESULTS")
            print("="*50)
            print(f"Workflow ID: {results['workflow_id']}")
            print(f"Status: {results['status']}")
            
            if results['status'] == 'completed':
                print(f"Started: {results['started_at']}")
                print(f"Completed: {results['completed_at']}")
                
                print(f"\nSteps Completed:")
                for step_name, step_result in results['steps'].items():
                    status_icon = "✅" if step_result['status'] == 'completed' else "⏭️"
                    print(f"  {status_icon} {step_name}: {step_result['status']}")
                
                # Show summary if available
                if 'summary' in results:
                    summary = results['summary']
                    if 'overview' in summary:
                        overview = summary['overview']
                        print(f"\nMarket Overview:")
                        print(f"  Total Jobs: {overview.get('total_jobs', 0)}")
                        print(f"  Companies: {overview.get('unique_companies', 0)}")
                        print(f"  Locations: {overview.get('unique_locations', 0)}")
                        print(f"  Data Quality: {overview.get('data_quality_score', 0):.2f}")
                
                # Generate report if requested
                if args.generate_report:
                    logger.info("Generating report")
                    report_file = workflow.generate_report()
                    print(f"\n📄 Report generated: {report_file}")
            
            else:
                print(f"❌ Workflow failed: {results.get('error', 'Unknown error')}")
                return False
    
    except Exception as e:
        logger.error(f"Analytics failed: {e}")
        print(f"❌ Error: {e}")
        return False
    
    return True

def run_tests(args):
    """Run analytics tests"""
    
    logger = setup_logging(args.log_level)
    logger.info("Running analytics tests")
    
    try:
        from analytics.tests.test_analytics import main as test_main
        
        # Set up test arguments
        test_args = []
        if args.verbose:
            test_args.append('--verbose')
        if args.test_class:
            test_args.extend(['--test', args.test_class])
        
        # Run tests
        sys.argv = ['test_analytics.py'] + test_args
        success = test_main()
        
        if success:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed!")
            return False
    
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"❌ Test error: {e}")
        return False

def run_dashboard_server(args):
    """Run the web dashboard"""
    
    logger = setup_logging(args.log_level)
    logger.info("Starting analytics dashboard")
    
    try:
        run_dashboard(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")
    except Exception as e:
        logger.error(f"Dashboard failed: {e}")
        print(f"❌ Dashboard error: {e}")
        return False

def show_status(args):
    """Show current analytics status"""
    
    logger = setup_logging(args.log_level)
    
    print("="*50)
    print("NEPAL JOB MARKET ANALYTICS STATUS")
    print("="*50)
    
    # Check for latest summary
    summary_file = Path("analytics/reports/latest_summary.json")
    if summary_file.exists():
        import json
        with open(summary_file, 'r') as f:
            latest = json.load(f)
        
        print(f"Last Analysis: {latest.get('timestamp', 'Unknown')}")
        print(f"Status: {latest.get('status', 'Unknown')}")
        print(f"Workflow ID: {latest.get('workflow_id', 'Unknown')}")
        
    else:
        print("❌ No analysis results found")
        print("Run: python analytics/run_analytics.py workflow --quick")
    
    # Check data directories
    data_dirs = [
        ("Raw Data", "data/raw"),
        ("Processed Data", "data/processed"),
        ("Analytics Reports", "analytics/reports"),
        ("Visualizations", "analytics/reports/visualizations")
    ]
    
    print(f"\nDirectory Status:")
    for name, path in data_dirs:
        dir_path = Path(path)
        if dir_path.exists():
            file_count = len(list(dir_path.glob("*")))
            print(f"  ✅ {name}: {file_count} files")
        else:
            print(f"  ❌ {name}: Not found")
    
    # Check scraped data
    workflow = AnalyticsWorkflow()
    try:
        quick_stats = workflow.run_quick_analysis()
        print(f"\nQuick Stats:")
        print(f"  Jobs Available: {quick_stats.get('total_jobs', 0)}")
        print(f"  Companies: {quick_stats.get('unique_companies', 0)}")
        print(f"  Locations: {quick_stats.get('unique_locations', 0)}")
    except Exception as e:
        print(f"  ❌ Error getting stats: {e}")

def clean_analytics(args):
    """Clean analytics data and reports"""
    
    logger = setup_logging(args.log_level)
    logger.info("Cleaning analytics data")
    
    import shutil
    
    paths_to_clean = [
        "analytics/reports/visualizations",
        "analytics/reports/workflow_results_*.json",
        "analytics/reports/market_analysis_*.json",
        "analytics/reports/duplicate_analysis_*.json"
    ]
    
    if args.all:
        paths_to_clean.extend([
            "analytics/reports",
            "analytics/dashboards/templates"
        ])
    
    cleaned_count = 0
    
    for path_pattern in paths_to_clean:
        path = Path(path_pattern)
        
        if '*' in str(path):
            # Handle glob patterns
            parent = path.parent
            pattern = path.name
            if parent.exists():
                for file_path in parent.glob(pattern):
                    if file_path.is_file():
                        file_path.unlink()
                        cleaned_count += 1
                        print(f"🗑️  Removed: {file_path}")
        else:
            # Handle direct paths
            if path.exists():
                if path.is_file():
                    path.unlink()
                    cleaned_count += 1
                    print(f"🗑️  Removed: {path}")
                elif path.is_dir() and args.all:
                    shutil.rmtree(path)
                    cleaned_count += 1
                    print(f"🗑️  Removed directory: {path}")
    
    print(f"\n✅ Cleaned {cleaned_count} files/directories")

def main():
    """Main function with CLI interface"""
    
    parser = argparse.ArgumentParser(
        description='Nepal Job Market Analytics System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run quick analysis
  python analytics/run_analytics.py workflow --quick
  
  # Run complete analysis with reports
  python analytics/run_analytics.py workflow --generate-report
  
  # Start web dashboard
  python analytics/run_analytics.py dashboard
  
  # Run tests
  python analytics/run_analytics.py test
  
  # Check status
  python analytics/run_analytics.py status
        """
    )
    
    # Global arguments
    parser.add_argument('--log-level', default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Run analytics workflow')
    workflow_parser.add_argument('--quick', action='store_true',
                                help='Run quick analysis only')
    workflow_parser.add_argument('--force-reload', action='store_true',
                                help='Force reload data from raw sources')
    workflow_parser.add_argument('--keep-duplicates', action='store_true',
                                help='Keep duplicate jobs (skip deduplication)')
    workflow_parser.add_argument('--duplicate-strategy', default='keep_best_source',
                                choices=['keep_first', 'keep_best_source', 'keep_most_complete'],
                                help='Strategy for handling duplicates')
    workflow_parser.add_argument('--no-viz', action='store_true',
                                help='Skip visualization generation')
    workflow_parser.add_argument('--export-formats', nargs='+', 
                                default=['json', 'csv'],
                                choices=['json', 'csv', 'html'],
                                help='Export formats')
    workflow_parser.add_argument('--generate-report', action='store_true',
                                help='Generate HTML report')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run analytics tests')
    test_parser.add_argument('--verbose', '-v', action='store_true',
                            help='Verbose test output')
    test_parser.add_argument('--test-class', help='Run specific test class')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Start web dashboard')
    dashboard_parser.add_argument('--host', default='127.0.0.1',
                                 help='Host to bind to')
    dashboard_parser.add_argument('--port', type=int, default=5000,
                                 help='Port to bind to')
    dashboard_parser.add_argument('--debug', action='store_true',
                                 help='Enable debug mode')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show analytics status')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean analytics data')
    clean_parser.add_argument('--all', action='store_true',
                             help='Clean all analytics data (destructive)')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to appropriate function
    if args.command == 'workflow':
        success = run_workflow(args)
        return 0 if success else 1
    
    elif args.command == 'test':
        success = run_tests(args)
        return 0 if success else 1
    
    elif args.command == 'dashboard':
        run_dashboard_server(args)
        return 0
    
    elif args.command == 'status':
        show_status(args)
        return 0
    
    elif args.command == 'clean':
        clean_analytics(args)
        return 0
    
    else:
        print(f"Unknown command: {args.command}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 