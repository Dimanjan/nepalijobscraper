#!/usr/bin/env python3
"""
Web Dashboard for Nepal Job Market Analytics
Provides a web interface to view analytics results, visualizations, and reports
"""

import sys
import os
from pathlib import Path
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for
import pandas as pd
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from analytics.scripts.analytics_workflow import AnalyticsWorkflow, WorkflowConfig

app = Flask(__name__)
app.secret_key = 'nepal_job_analytics_dashboard_2024'

class AnalyticsDashboard:
    """Web dashboard for job market analytics"""
    
    def __init__(self):
        self.workflow = AnalyticsWorkflow()
        self.logger = logging.getLogger(__name__)
        
        # Cache for frequently accessed data
        self._cache = {}
        self._cache_expiry = {}
        self.cache_duration = timedelta(minutes=30)
        
    def get_latest_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get the latest analytics data with caching"""
        
        cache_key = 'latest_data'
        now = datetime.now()
        
        # Check cache
        if (not force_refresh and 
            cache_key in self._cache and 
            cache_key in self._cache_expiry and 
            now < self._cache_expiry[cache_key]):
            return self._cache[cache_key]
        
        try:
            # Load latest summary
            summary_file = Path("analytics/reports/latest_summary.json")
            if summary_file.exists():
                with open(summary_file, 'r') as f:
                    latest_summary = json.load(f)
                
                # Load detailed results
                workflow_file = latest_summary.get('files')
                if workflow_file and Path(workflow_file).exists():
                    with open(workflow_file, 'r') as f:
                        detailed_results = json.load(f)
                    
                    data = {
                        'summary': latest_summary,
                        'details': detailed_results,
                        'last_updated': latest_summary.get('timestamp'),
                        'status': latest_summary.get('status', 'unknown')
                    }
                    
                    # Cache the data
                    self._cache[cache_key] = data
                    self._cache_expiry[cache_key] = now + self.cache_duration
                    
                    return data
        
        except Exception as e:
            self.logger.error(f"Failed to load latest data: {e}")
        
        return {'error': 'No data available', 'status': 'error'}
    
    def get_quick_stats(self) -> Dict[str, Any]:
        """Get quick statistics for dashboard overview"""
        
        try:
            quick_stats = self.workflow.run_quick_analysis()
            return quick_stats
        except Exception as e:
            self.logger.error(f"Failed to get quick stats: {e}")
            return {'error': str(e)}
    
    def get_visualization_files(self) -> List[Dict[str, str]]:
        """Get list of available visualization files"""
        
        viz_dir = Path("analytics/reports/visualizations")
        visualizations = []
        
        if viz_dir.exists():
            for file_path in viz_dir.glob("*.html"):
                visualizations.append({
                    'name': file_path.stem.replace('_', ' ').title(),
                    'file': file_path.name,
                    'path': str(file_path),
                    'created': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                })
        
        # Sort by creation time (newest first)
        visualizations.sort(key=lambda x: x['created'], reverse=True)
        return visualizations
    
    def get_reports(self) -> List[Dict[str, str]]:
        """Get list of available reports"""
        
        reports_dir = Path("analytics/reports")
        reports = []
        
        if reports_dir.exists():
            for file_path in reports_dir.glob("*.html"):
                if 'visualization' not in file_path.name:  # Exclude visualization files
                    reports.append({
                        'name': file_path.stem.replace('_', ' ').title(),
                        'file': file_path.name,
                        'path': str(file_path),
                        'created': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                    })
        
        reports.sort(key=lambda x: x['created'], reverse=True)
        return reports

# Initialize dashboard
dashboard = AnalyticsDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    
    try:
        # Get quick stats
        quick_stats = dashboard.get_quick_stats()
        
        # Get latest analysis data
        latest_data = dashboard.get_latest_data()
        
        # Get available visualizations
        visualizations = dashboard.get_visualization_files()
        
        return render_template('dashboard.html',
                             quick_stats=quick_stats,
                             latest_data=latest_data,
                             visualizations=visualizations[:6])  # Show latest 6
    
    except Exception as e:
        app.logger.error(f"Dashboard error: {e}")
        return render_template('error.html', error=str(e))

@app.route('/api/stats')
def api_stats():
    """API endpoint for quick statistics"""
    
    try:
        stats = dashboard.get_quick_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/latest')
def api_latest():
    """API endpoint for latest analysis data"""
    
    try:
        data = dashboard.get_latest_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/visualizations')
def visualizations():
    """Visualizations gallery page"""
    
    try:
        viz_files = dashboard.get_visualization_files()
        return render_template('visualizations.html', visualizations=viz_files)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/visualization/<filename>')
def view_visualization(filename):
    """View specific visualization"""
    
    try:
        viz_path = Path("analytics/reports/visualizations") / filename
        if viz_path.exists() and viz_path.suffix == '.html':
            return send_file(viz_path)
        else:
            return "Visualization not found", 404
    except Exception as e:
        return f"Error loading visualization: {e}", 500

@app.route('/reports')
def reports():
    """Reports page"""
    
    try:
        report_files = dashboard.get_reports()
        return render_template('reports.html', reports=report_files)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/report/<filename>')
def view_report(filename):
    """View specific report"""
    
    try:
        report_path = Path("analytics/reports") / filename
        if report_path.exists() and report_path.suffix == '.html':
            return send_file(report_path)
        else:
            return "Report not found", 404
    except Exception as e:
        return f"Error loading report: {e}", 500

@app.route('/analysis')
def analysis():
    """Detailed analysis page"""
    
    try:
        latest_data = dashboard.get_latest_data()
        
        # Extract analysis details
        analysis_data = {}
        if 'details' in latest_data and 'market_analysis' in latest_data['details']:
            analysis_data = latest_data['details']['market_analysis']
        
        return render_template('analysis.html', analysis=analysis_data)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/run_analysis')
def run_analysis():
    """Trigger new analysis"""
    
    try:
        # Run quick analysis
        results = dashboard.workflow.run_complete_workflow()
        
        if results['status'] == 'completed':
            # Clear cache to force refresh
            dashboard._cache.clear()
            dashboard._cache_expiry.clear()
            
            return jsonify({
                'status': 'success',
                'message': 'Analysis completed successfully',
                'workflow_id': results['workflow_id']
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f"Analysis failed: {results.get('error', 'Unknown error')}"
            }), 500
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"Failed to run analysis: {e}"
        }), 500

@app.route('/api/refresh')
def api_refresh():
    """API endpoint to refresh data"""
    
    try:
        latest_data = dashboard.get_latest_data(force_refresh=True)
        return jsonify({'status': 'success', 'data': latest_data})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

# Create templates directory and basic templates
def create_templates():
    """Create basic HTML templates for the dashboard"""
    
    templates_dir = Path("analytics/dashboards/templates")
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # Base template
    base_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Nepal Job Market Analytics{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
        }
        .navbar-brand {
            font-weight: bold;
        }
        .sidebar {
            min-height: 100vh;
            background-color: #f8f9fa;
        }
        .main-content {
            padding: 20px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="fas fa-chart-line"></i> Nepal Job Analytics
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link" href="/visualizations">Charts</a>
                <a class="nav-link" href="/analysis">Analysis</a>
                <a class="nav-link" href="/reports">Reports</a>
            </div>
        </div>
    </nav>
    
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-12 main-content">
                {% block content %}{% endblock %}
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
"""
    
    # Dashboard template
    dashboard_template = """
{% extends "base.html" %}

{% block title %}Dashboard - Nepal Job Analytics{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1 class="mb-4">
            <i class="fas fa-tachometer-alt"></i> Nepal Job Market Dashboard
        </h1>
    </div>
</div>

<!-- Quick Stats -->
<div class="row">
    <div class="col-md-3">
        <div class="metric-card">
            <h3>{{ quick_stats.total_jobs or 0 }}</h3>
            <p><i class="fas fa-briefcase"></i> Total Jobs</p>
        </div>
    </div>
    <div class="col-md-3">
        <div class="metric-card">
            <h3>{{ quick_stats.unique_companies or 0 }}</h3>
            <p><i class="fas fa-building"></i> Companies</p>
        </div>
    </div>
    <div class="col-md-3">
        <div class="metric-card">
            <h3>{{ quick_stats.unique_locations or 0 }}</h3>
            <p><i class="fas fa-map-marker-alt"></i> Locations</p>
        </div>
    </div>
    <div class="col-md-3">
        <div class="metric-card">
            <h3>{{ latest_data.status or 'Unknown' }}</h3>
            <p><i class="fas fa-signal"></i> Status</p>
        </div>
    </div>
</div>

<!-- Latest Analysis -->
{% if latest_data.last_updated %}
<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-clock"></i> Latest Analysis</h5>
            </div>
            <div class="card-body">
                <p><strong>Last Updated:</strong> {{ latest_data.last_updated }}</p>
                <p><strong>Status:</strong> 
                    <span class="badge bg-{% if latest_data.status == 'completed' %}success{% else %}warning{% endif %}">
                        {{ latest_data.status }}
                    </span>
                </p>
                <button class="btn btn-primary" onclick="runAnalysis()">
                    <i class="fas fa-sync"></i> Run New Analysis
                </button>
            </div>
        </div>
    </div>
</div>
{% endif %}

<!-- Recent Visualizations -->
{% if visualizations %}
<div class="row mt-4">
    <div class="col-12">
        <h3><i class="fas fa-chart-bar"></i> Recent Visualizations</h3>
        <div class="row">
            {% for viz in visualizations %}
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h6 class="card-title">{{ viz.name }}</h6>
                        <p class="card-text"><small class="text-muted">{{ viz.created }}</small></p>
                        <a href="/visualization/{{ viz.file }}" class="btn btn-sm btn-outline-primary" target="_blank">
                            <i class="fas fa-eye"></i> View
                        </a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        <a href="/visualizations" class="btn btn-primary">View All Visualizations</a>
    </div>
</div>
{% endif %}
{% endblock %}

{% block scripts %}
<script>
function runAnalysis() {
    const btn = event.target;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';
    btn.disabled = true;
    
    fetch('/run_analysis')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Analysis completed successfully!');
                location.reload();
            } else {
                alert('Analysis failed: ' + data.message);
            }
        })
        .catch(error => {
            alert('Error: ' + error);
        })
        .finally(() => {
            btn.innerHTML = '<i class="fas fa-sync"></i> Run New Analysis';
            btn.disabled = false;
        });
}
</script>
{% endblock %}
"""
    
    # Save templates
    with open(templates_dir / "base.html", 'w') as f:
        f.write(base_template)
    
    with open(templates_dir / "dashboard.html", 'w') as f:
        f.write(dashboard_template)
    
    # Create simple error template
    error_template = """
{% extends "base.html" %}
{% block content %}
<div class="alert alert-danger">
    <h4><i class="fas fa-exclamation-triangle"></i> Error</h4>
    <p>{{ error }}</p>
    <a href="/" class="btn btn-primary">Return to Dashboard</a>
</div>
{% endblock %}
"""
    
    with open(templates_dir / "error.html", 'w') as f:
        f.write(error_template)
    
    # Create visualizations template
    viz_template = """
{% extends "base.html" %}
{% block title %}Visualizations - Nepal Job Analytics{% endblock %}
{% block content %}
<h1><i class="fas fa-chart-line"></i> Visualizations</h1>
<div class="row">
    {% for viz in visualizations %}
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">{{ viz.name }}</h5>
                <p class="card-text"><small class="text-muted">Created: {{ viz.created }}</small></p>
                <a href="/visualization/{{ viz.file }}" class="btn btn-primary" target="_blank">
                    <i class="fas fa-external-link-alt"></i> Open
                </a>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
"""
    
    with open(templates_dir / "visualizations.html", 'w') as f:
        f.write(viz_template)

def run_dashboard(host='127.0.0.1', port=5000, debug=False):
    """Run the dashboard web server"""
    
    # Create templates
    create_templates()
    
    # Set template folder
    app.template_folder = str(Path("analytics/dashboards/templates"))
    
    print(f"""
    =================================
    Nepal Job Market Analytics Dashboard
    =================================
    
    Dashboard URL: http://{host}:{port}
    
    Available endpoints:
    • /                  - Main dashboard
    • /visualizations    - Charts gallery
    • /analysis         - Detailed analysis
    • /reports          - Reports
    • /api/stats        - API for statistics
    • /api/latest       - API for latest data
    
    Press Ctrl+C to stop the server
    =================================
    """)
    
    app.run(host=host, port=port, debug=debug)

def main():
    """Main function to run the dashboard"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Nepal Job Market Analytics Dashboard')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    run_dashboard(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main() 