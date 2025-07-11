#!/usr/bin/env python3
"""
Comprehensive Data Visualization System for Nepal Job Market
Creates charts, graphs, and interactive visualizations for job market analytics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from datetime import datetime
from pathlib import Path
import base64
from io import BytesIO

class JobMarketVisualizer:
    """Advanced visualization system for job market data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Set style preferences
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Ensure output directory exists
        Path(self.config['output_dir']).mkdir(parents=True, exist_ok=True)
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for visualizations"""
        return {
            'output_dir': 'analytics/reports/visualizations',
            'figure_size': (12, 8),
            'dpi': 300,
            'color_palette': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            'font_size': 12,
            'title_font_size': 16,
            'export_formats': ['png', 'html'],
            'interactive_plots': True
        }
    
    def create_comprehensive_dashboard(self, jobs_data: List[Dict[str, Any]], 
                                     analysis_results: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Create a comprehensive dashboard with all visualizations
        
        Args:
            jobs_data: List of job dictionaries
            analysis_results: Pre-computed analysis results
            
        Returns:
            Dictionary of created visualization files
        """
        self.logger.info("Creating comprehensive job market dashboard")
        
        df = pd.DataFrame(jobs_data)
        created_files = {}
        
        # Create individual visualizations
        visualizations = [
            ('overview_stats', self.create_overview_dashboard),
            ('company_analysis', self.create_company_analysis),
            ('location_heatmap', self.create_location_heatmap),
            ('salary_analysis', self.create_salary_analysis),
            ('job_categories', self.create_job_category_analysis),
            ('skills_demand', self.create_skills_demand_chart),
            ('source_comparison', self.create_source_comparison),
            ('trends_analysis', self.create_trends_analysis)
        ]
        
        for viz_name, viz_function in visualizations:
            try:
                files = viz_function(df, analysis_results)
                created_files[viz_name] = files
                self.logger.info(f"Created {viz_name} visualization")
            except Exception as e:
                self.logger.error(f"Failed to create {viz_name}: {e}")
        
        # Create combined dashboard
        combined_dashboard = self.create_combined_dashboard(df, analysis_results)
        created_files['combined_dashboard'] = combined_dashboard
        
        self.logger.info(f"Dashboard creation completed. Created {len(created_files)} visualizations")
        return created_files
    
    def create_overview_dashboard(self, df: pd.DataFrame, 
                                analysis: Dict[str, Any] = None) -> Dict[str, str]:
        """Create overview statistics dashboard"""
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Job Distribution by Source', 'Top Companies', 
                          'Location Distribution', 'Job Categories'),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "pie"}]]
        )
        
        # Source distribution
        if 'source' in df.columns:
            source_counts = df['source'].value_counts()
            fig.add_trace(
                go.Pie(labels=source_counts.index, values=source_counts.values,
                      name="Sources"),
                row=1, col=1
            )
        
        # Top companies
        if 'company' in df.columns:
            company_counts = df['company'].value_counts().head(10)
            fig.add_trace(
                go.Bar(x=company_counts.values, y=company_counts.index,
                      orientation='h', name="Companies"),
                row=1, col=2
            )
        
        # Location distribution
        if 'location' in df.columns:
            location_counts = df['location'].value_counts().head(10)
            fig.add_trace(
                go.Bar(x=location_counts.index, y=location_counts.values,
                      name="Locations"),
                row=2, col=1
            )
        
        # Job categories (if we can derive them)
        if 'title' in df.columns:
            categories = self._extract_job_categories(df['title'])
            category_counts = pd.Series(categories).value_counts()
            fig.add_trace(
                go.Pie(labels=category_counts.index, values=category_counts.values,
                      name="Categories"),
                row=2, col=2
            )
        
        fig.update_layout(
            title_text="Nepal Job Market Overview Dashboard",
            showlegend=False,
            height=800
        )
        
        # Save the plot
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_file = f"{self.config['output_dir']}/overview_dashboard_{timestamp}.html"
        fig.write_html(html_file)
        
        return {'html': html_file}
    
    def create_company_analysis(self, df: pd.DataFrame, 
                              analysis: Dict[str, Any] = None) -> Dict[str, str]:
        """Create company hiring analysis visualization"""
        
        if 'company' not in df.columns:
            return {}
        
        # Top hiring companies
        company_counts = df['company'].value_counts().head(20)
        
        # Create interactive bar chart
        fig = go.Figure(data=[
            go.Bar(x=company_counts.index, y=company_counts.values,
                  text=company_counts.values, textposition='auto',
                  marker_color=self.config['color_palette'][0])
        ])
        
        fig.update_layout(
            title='Top 20 Hiring Companies in Nepal',
            xaxis_title='Company',
            yaxis_title='Number of Job Openings',
            xaxis_tickangle=-45,
            height=600
        )
        
        # Save the plot
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_file = f"{self.config['output_dir']}/company_analysis_{timestamp}.html"
        fig.write_html(html_file)
        
        # Also create static version
        plt.figure(figsize=self.config['figure_size'])
        plt.bar(range(len(company_counts)), company_counts.values)
        plt.xticks(range(len(company_counts)), company_counts.index, rotation=45, ha='right')
        plt.title('Top Hiring Companies in Nepal')
        plt.xlabel('Company')
        plt.ylabel('Number of Job Openings')
        plt.tight_layout()
        
        png_file = f"{self.config['output_dir']}/company_analysis_{timestamp}.png"
        plt.savefig(png_file, dpi=self.config['dpi'], bbox_inches='tight')
        plt.close()
        
        return {'html': html_file, 'png': png_file}
    
    def create_location_heatmap(self, df: pd.DataFrame, 
                              analysis: Dict[str, Any] = None) -> Dict[str, str]:
        """Create location-based job distribution heatmap"""
        
        if 'location' not in df.columns:
            return {}
        
        # Process location data
        location_counts = df['location'].value_counts().head(15)
        
        # Create heatmap-style visualization
        fig = go.Figure(data=go.Bar(
            x=location_counts.values,
            y=location_counts.index,
            orientation='h',
            marker=dict(
                color=location_counts.values,
                colorscale='Viridis',
                showscale=True
            )
        ))
        
        fig.update_layout(
            title='Job Distribution by Location',
            xaxis_title='Number of Jobs',
            yaxis_title='Location',
            height=600
        )
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_file = f"{self.config['output_dir']}/location_heatmap_{timestamp}.html"
        fig.write_html(html_file)
        
        return {'html': html_file}
    
    def create_salary_analysis(self, df: pd.DataFrame, 
                             analysis: Dict[str, Any] = None) -> Dict[str, str]:
        """Create salary analysis visualizations"""
        
        # Extract salary information
        salary_data = self._extract_salary_data(df)
        
        if salary_data.empty:
            return {}
        
        # Create subplot with multiple salary analyses
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Salary Distribution', 'Salary by Company', 
                          'Salary Trends', 'Salary Ranges'),
            specs=[[{"type": "histogram"}, {"type": "box"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # Salary distribution histogram
        fig.add_trace(
            go.Histogram(x=salary_data['salary'], nbinsx=20, name="Salary Distribution"),
            row=1, col=1
        )
        
        # Salary by top companies (box plot)
        if 'company' in df.columns:
            top_companies = df['company'].value_counts().head(10).index
            company_salary_data = []
            for company in top_companies:
                company_salaries = salary_data[salary_data['company'] == company]['salary']
                if len(company_salaries) > 0:
                    fig.add_trace(
                        go.Box(y=company_salaries, name=company),
                        row=1, col=2
                    )
        
        # Salary trends over time (if date available)
        if 'scraped_date' in df.columns:
            df['scraped_date'] = pd.to_datetime(df['scraped_date'], errors='coerce')
            daily_avg_salary = salary_data.groupby(salary_data['scraped_date'].dt.date)['salary'].mean()
            fig.add_trace(
                go.Scatter(x=daily_avg_salary.index, y=daily_avg_salary.values,
                         mode='lines+markers', name="Average Salary"),
                row=2, col=1
            )
        
        # Salary ranges
        salary_ranges = pd.cut(salary_data['salary'], bins=5).value_counts()
        fig.add_trace(
            go.Bar(x=[str(interval) for interval in salary_ranges.index], 
                  y=salary_ranges.values, name="Salary Ranges"),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="Salary Analysis Dashboard",
            showlegend=False,
            height=800
        )
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_file = f"{self.config['output_dir']}/salary_analysis_{timestamp}.html"
        fig.write_html(html_file)
        
        return {'html': html_file}
    
    def create_job_category_analysis(self, df: pd.DataFrame, 
                                   analysis: Dict[str, Any] = None) -> Dict[str, str]:
        """Create job category analysis visualization"""
        
        if 'title' not in df.columns:
            return {}
        
        # Extract job categories
        categories = self._extract_job_categories(df['title'])
        category_counts = pd.Series(categories).value_counts()
        
        # Create donut chart
        fig = go.Figure(data=[go.Pie(
            labels=category_counts.index, 
            values=category_counts.values,
            hole=.3
        )])
        
        fig.update_layout(
            title="Job Categories Distribution",
            annotations=[dict(text='Job<br>Categories', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_file = f"{self.config['output_dir']}/job_categories_{timestamp}.html"
        fig.write_html(html_file)
        
        return {'html': html_file}
    
    def create_skills_demand_chart(self, df: pd.DataFrame, 
                                 analysis: Dict[str, Any] = None) -> Dict[str, str]:
        """Create skills demand visualization"""
        
        # Extract skills from job titles and descriptions
        skills_data = self._extract_skills_data(df)
        
        if not skills_data:
            return {}
        
        # Create word cloud style bar chart
        skills_df = pd.DataFrame(list(skills_data.items()), columns=['Skill', 'Count'])
        skills_df = skills_df.head(20)  # Top 20 skills
        
        fig = go.Figure(data=[
            go.Bar(x=skills_df['Skill'], y=skills_df['Count'],
                  marker_color=px.colors.qualitative.Set3)
        ])
        
        fig.update_layout(
            title='Most In-Demand Skills in Nepal Job Market',
            xaxis_title='Skills',
            yaxis_title='Demand Count',
            xaxis_tickangle=-45
        )
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_file = f"{self.config['output_dir']}/skills_demand_{timestamp}.html"
        fig.write_html(html_file)
        
        return {'html': html_file}
    
    def create_source_comparison(self, df: pd.DataFrame, 
                               analysis: Dict[str, Any] = None) -> Dict[str, str]:
        """Create job source comparison visualization"""
        
        if 'source' not in df.columns:
            return {}
        
        # Source statistics
        source_stats = df.groupby('source').agg({
            'title': 'count',
            'company': lambda x: x.nunique(),
            'location': lambda x: x.nunique()
        }).rename(columns={
            'title': 'Job Count',
            'company': 'Unique Companies',
            'location': 'Unique Locations'
        })
        
        # Create grouped bar chart
        fig = go.Figure()
        
        for column in source_stats.columns:
            fig.add_trace(go.Bar(
                name=column,
                x=source_stats.index,
                y=source_stats[column]
            ))
        
        fig.update_layout(
            title='Job Source Comparison',
            xaxis_title='Job Source',
            yaxis_title='Count',
            barmode='group'
        )
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_file = f"{self.config['output_dir']}/source_comparison_{timestamp}.html"
        fig.write_html(html_file)
        
        return {'html': html_file}
    
    def create_trends_analysis(self, df: pd.DataFrame, 
                             analysis: Dict[str, Any] = None) -> Dict[str, str]:
        """Create trends analysis visualization"""
        
        # Daily posting trends
        if 'scraped_date' in df.columns:
            df['scraped_date'] = pd.to_datetime(df['scraped_date'], errors='coerce')
            daily_jobs = df.groupby(df['scraped_date'].dt.date).size()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_jobs.index,
                y=daily_jobs.values,
                mode='lines+markers',
                name='Daily Job Postings'
            ))
            
            fig.update_layout(
                title='Daily Job Posting Trends',
                xaxis_title='Date',
                yaxis_title='Number of Jobs Posted'
            )
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            html_file = f"{self.config['output_dir']}/trends_analysis_{timestamp}.html"
            fig.write_html(html_file)
            
            return {'html': html_file}
        
        return {}
    
    def create_combined_dashboard(self, df: pd.DataFrame, 
                                analysis: Dict[str, Any] = None) -> Dict[str, str]:
        """Create a comprehensive combined dashboard"""
        
        # Create a large subplot layout
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=('Source Distribution', 'Top Companies', 'Location Heatmap',
                          'Job Categories', 'Salary Distribution', 'Skills Demand',
                          'Daily Trends', 'Company vs Location', 'Summary Stats'),
            specs=[[{"type": "pie"}, {"type": "bar"}, {"type": "bar"}],
                   [{"type": "pie"}, {"type": "histogram"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "heatmap"}, {"type": "table"}]]
        )
        
        # Add all the plots (simplified versions)
        # Source distribution
        if 'source' in df.columns:
            source_counts = df['source'].value_counts()
            fig.add_trace(
                go.Pie(labels=source_counts.index, values=source_counts.values),
                row=1, col=1
            )
        
        # Top companies
        if 'company' in df.columns:
            company_counts = df['company'].value_counts().head(10)
            fig.add_trace(
                go.Bar(x=company_counts.index, y=company_counts.values),
                row=1, col=2
            )
        
        # Location distribution
        if 'location' in df.columns:
            location_counts = df['location'].value_counts().head(10)
            fig.add_trace(
                go.Bar(x=location_counts.index, y=location_counts.values),
                row=1, col=3
            )
        
        # Add more plots...
        
        fig.update_layout(
            title_text="Nepal Job Market Comprehensive Dashboard",
            showlegend=False,
            height=1200
        )
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_file = f"{self.config['output_dir']}/combined_dashboard_{timestamp}.html"
        fig.write_html(html_file)
        
        return {'html': html_file}
    
    def _extract_job_categories(self, titles: pd.Series) -> List[str]:
        """Extract job categories from titles"""
        categories = []
        
        category_keywords = {
            'Technology': ['developer', 'engineer', 'programmer', 'software', 'tech', 'python', 'java'],
            'Management': ['manager', 'director', 'head', 'lead', 'supervisor'],
            'Sales & Marketing': ['sales', 'marketing', 'business development', 'account'],
            'Finance': ['accountant', 'finance', 'banking', 'investment'],
            'Healthcare': ['doctor', 'nurse', 'medical', 'health'],
            'Education': ['teacher', 'instructor', 'professor', 'education'],
            'Customer Service': ['customer service', 'support', 'representative'],
            'Operations': ['operations', 'logistics', 'supply chain'],
            'Design': ['designer', 'creative', 'graphic', 'ui', 'ux']
        }
        
        for title in titles.fillna(''):
            title_lower = title.lower()
            categorized = False
            
            for category, keywords in category_keywords.items():
                if any(keyword in title_lower for keyword in keywords):
                    categories.append(category)
                    categorized = True
                    break
            
            if not categorized:
                categories.append('Other')
        
        return categories
    
    def _extract_salary_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract and clean salary data"""
        if 'salary' not in df.columns:
            return pd.DataFrame()
        
        salary_data = []
        
        for idx, row in df.iterrows():
            salary_str = str(row.get('salary', ''))
            
            # Extract numeric salary
            import re
            numbers = re.findall(r'\d+(?:,\d+)*', salary_str)
            
            if numbers:
                try:
                    salary = float(numbers[0].replace(',', ''))
                    
                    # Handle k/K notation
                    if 'k' in salary_str.lower() and salary < 1000:
                        salary *= 1000
                    
                    # Handle lakh notation
                    if 'lakh' in salary_str.lower():
                        salary *= 100000
                    
                    # Reasonable salary range
                    if 5000 <= salary <= 500000:
                        salary_data.append({
                            'salary': salary,
                            'company': row.get('company', ''),
                            'location': row.get('location', ''),
                            'title': row.get('title', ''),
                            'scraped_date': row.get('scraped_date', '')
                        })
                
                except ValueError:
                    continue
        
        return pd.DataFrame(salary_data)
    
    def _extract_skills_data(self, df: pd.DataFrame) -> Dict[str, int]:
        """Extract skills data from job titles and descriptions"""
        from collections import Counter
        
        skills_counter = Counter()
        
        # Common skills to look for
        skills_list = [
            'python', 'java', 'javascript', 'react', 'nodejs', 'angular', 'vue',
            'php', 'laravel', 'django', 'flask', 'sql', 'mysql', 'postgresql',
            'mongodb', 'html', 'css', 'bootstrap', 'git', 'docker', 'aws',
            'azure', 'linux', 'windows', 'excel', 'powerpoint', 'photoshop',
            'accounting', 'marketing', 'sales', 'management', 'leadership'
        ]
        
        # Search in titles
        for title in df.get('title', pd.Series()).fillna(''):
            title_lower = title.lower()
            for skill in skills_list:
                if skill in title_lower:
                    skills_counter[skill] += 1
        
        # Search in descriptions if available
        for desc in df.get('description', pd.Series()).fillna(''):
            desc_lower = desc.lower()
            for skill in skills_list:
                if skill in desc_lower:
                    skills_counter[skill] += 1
        
        return dict(skills_counter)
    
    def generate_report_summary(self, visualizations: Dict[str, Any]) -> str:
        """Generate a summary report of all visualizations"""
        
        summary = f"""
        # Nepal Job Market Visualization Report
        
        Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        ## Created Visualizations:
        
        """
        
        for viz_name, files in visualizations.items():
            summary += f"### {viz_name.replace('_', ' ').title()}\n"
            if isinstance(files, dict):
                for file_type, file_path in files.items():
                    summary += f"- {file_type.upper()}: {file_path}\n"
            summary += "\n"
        
        # Save summary
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = f"{self.config['output_dir']}/visualization_summary_{timestamp}.md"
        
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        return summary_file

def main():
    """Test the visualizer"""
    # Sample data for testing
    sample_jobs = [
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
    ] * 50  # Multiply to have more data points
    
    visualizer = JobMarketVisualizer()
    
    print("Creating comprehensive dashboard...")
    visualizations = visualizer.create_comprehensive_dashboard(sample_jobs)
    
    print("=== Created Visualizations ===")
    for viz_name, files in visualizations.items():
        print(f"{viz_name}: {files}")
    
    # Generate summary report
    summary_file = visualizer.generate_report_summary(visualizations)
    print(f"\nSummary report: {summary_file}")

if __name__ == "__main__":
    main() 