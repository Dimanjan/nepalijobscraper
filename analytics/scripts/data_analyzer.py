#!/usr/bin/env python3
"""
Comprehensive Data Analysis Engine for Nepal Job Market
Provides deep insights, statistics, and market analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re
from dataclasses import dataclass
from pathlib import Path

@dataclass
class MarketInsight:
    """Represents a market insight"""
    category: str
    metric: str
    value: Any
    trend: Optional[str]
    description: str
    confidence: float

class DataAnalyzer:
    """Advanced data analysis engine for job market data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for data analysis"""
        return {
            'salary_ranges': {
                'entry_level': (0, 25000),
                'mid_level': (25000, 50000),
                'senior_level': (50000, 100000),
                'executive': (100000, float('inf'))
            },
            'major_cities': ['kathmandu', 'lalitpur', 'bhaktapur', 'pokhara'],
            'tech_keywords': [
                'python', 'java', 'javascript', 'react', 'node', 'django',
                'developer', 'engineer', 'programmer', 'software', 'web',
                'mobile', 'app', 'database', 'sql', 'nosql'
            ],
            'business_keywords': [
                'manager', 'executive', 'director', 'analyst', 'coordinator',
                'sales', 'marketing', 'finance', 'accounting', 'hr'
            ],
            'min_salary_for_analysis': 5000,
            'max_salary_for_analysis': 500000
        }
    
    def analyze_market(self, jobs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Comprehensive market analysis
        
        Args:
            jobs_data: List of job dictionaries
            
        Returns:
            Dictionary containing comprehensive market analysis
        """
        self.logger.info(f"Starting market analysis for {len(jobs_data)} jobs")
        
        # Convert to DataFrame
        df = self._prepare_data(jobs_data)
        
        analysis = {
            'overview': self._analyze_overview(df),
            'companies': self._analyze_companies(df),
            'locations': self._analyze_locations(df),
            'job_types': self._analyze_job_types(df),
            'salaries': self._analyze_salaries(df),
            'skills_demand': self._analyze_skills_demand(df),
            'source_analysis': self._analyze_sources(df),
            'market_trends': self._analyze_trends(df),
            'competitive_landscape': self._analyze_competition(df),
            'opportunities': self._identify_opportunities(df),
            'insights': []
        }
        
        # Generate key insights
        analysis['insights'] = self._generate_insights(df, analysis)
        
        self.logger.info("Market analysis completed")
        return analysis
    
    def _prepare_data(self, jobs_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prepare and clean data for analysis"""
        df = pd.DataFrame(jobs_data)
        
        # Ensure we have an ID column
        if 'id' not in df.columns:
            df['id'] = df.index.astype(str)
        
        # Clean and standardize text fields
        text_fields = ['title', 'company', 'location', 'description']
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].fillna('').astype(str)
                df[f'{field}_clean'] = df[field].apply(self._clean_text)
        
        # Extract and standardize salary information
        if 'salary' in df.columns:
            df['salary_numeric'] = df['salary'].apply(self._extract_salary_numeric)
            df['salary_range'] = df['salary_numeric'].apply(self._categorize_salary)
        
        # Standardize locations
        if 'location' in df.columns:
            df['location_standardized'] = df['location_clean'].apply(self._standardize_location)
            df['is_major_city'] = df['location_standardized'].apply(self._is_major_city)
        
        # Extract job categories
        if 'title' in df.columns:
            df['job_category'] = df['title_clean'].apply(self._categorize_job)
            df['seniority_level'] = df['title_clean'].apply(self._extract_seniority)
        
        # Parse dates
        if 'scraped_date' in df.columns:
            df['scraped_date'] = pd.to_datetime(df['scraped_date'], errors='coerce')
        
        return df
    
    def _clean_text(self, text: str) -> str:
        """Clean and standardize text"""
        if not text or pd.isna(text):
            return ""
        
        text = str(text).lower().strip()
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _extract_salary_numeric(self, salary_str: str) -> Optional[float]:
        """Extract numeric salary from salary string"""
        if not salary_str or pd.isna(salary_str):
            return None
        
        salary_str = str(salary_str).lower()
        
        # Remove currency symbols and common words
        salary_str = re.sub(r'[rs\.\,rupees]', '', salary_str)
        salary_str = re.sub(r'(per month|monthly|per year|yearly|annually)', '', salary_str)
        
        # Look for numeric patterns
        numbers = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', salary_str)
        if not numbers:
            return None
        
        # Convert to float and handle thousands/lakhs
        try:
            value = float(numbers[0].replace(',', ''))
            
            # Handle k/K (thousands)
            if 'k' in salary_str and value < 1000:
                value *= 1000
            
            # Handle lakh
            if 'lakh' in salary_str:
                value *= 100000
            
            # Sanity check
            if self.config['min_salary_for_analysis'] <= value <= self.config['max_salary_for_analysis']:
                return value
        
        except ValueError:
            pass
        
        return None
    
    def _categorize_salary(self, salary: Optional[float]) -> str:
        """Categorize salary into ranges"""
        if salary is None:
            return 'not_specified'
        
        for category, (min_val, max_val) in self.config['salary_ranges'].items():
            if min_val <= salary < max_val:
                return category
        
        return 'unknown'
    
    def _standardize_location(self, location: str) -> str:
        """Standardize location names"""
        if not location:
            return 'unknown'
        
        location = location.lower()
        
        # Map common variations
        location_map = {
            'ktm': 'kathmandu',
            'kathmandu valley': 'kathmandu',
            'bhaktapur': 'bhaktapur',
            'lalitpur': 'lalitpur',
            'patan': 'lalitpur',
            'pokhara': 'pokhara'
        }
        
        for key, standard in location_map.items():
            if key in location:
                return standard
        
        # Extract city name if location contains "Nepal"
        if 'nepal' in location:
            parts = location.replace('nepal', '').replace(',', '').strip().split()
            if parts:
                return parts[0]
        
        return location.split(',')[0].strip() if ',' in location else location
    
    def _is_major_city(self, location: str) -> bool:
        """Check if location is a major city"""
        return location in self.config['major_cities']
    
    def _categorize_job(self, title: str) -> str:
        """Categorize job based on title"""
        if not title:
            return 'other'
        
        title = title.lower()
        
        # Technology jobs
        if any(keyword in title for keyword in self.config['tech_keywords']):
            return 'technology'
        
        # Business jobs
        if any(keyword in title for keyword in self.config['business_keywords']):
            return 'business'
        
        # Other categories
        categories = {
            'healthcare': ['doctor', 'nurse', 'medical', 'health', 'pharmacy'],
            'education': ['teacher', 'professor', 'instructor', 'education', 'academic'],
            'finance': ['accountant', 'finance', 'banking', 'investment'],
            'sales': ['sales', 'business development', 'account executive'],
            'marketing': ['marketing', 'digital marketing', 'content', 'social media'],
            'operations': ['operations', 'logistics', 'supply chain', 'procurement'],
            'customer_service': ['customer service', 'support', 'help desk'],
            'design': ['designer', 'creative', 'graphic', 'ui', 'ux']
        }
        
        for category, keywords in categories.items():
            if any(keyword in title for keyword in keywords):
                return category
        
        return 'other'
    
    def _extract_seniority(self, title: str) -> str:
        """Extract seniority level from job title"""
        if not title:
            return 'unknown'
        
        title = title.lower()
        
        senior_keywords = ['senior', 'sr', 'lead', 'principal', 'chief', 'head', 'director']
        junior_keywords = ['junior', 'jr', 'intern', 'trainee', 'assistant', 'entry']
        mid_keywords = ['manager', 'supervisor', 'coordinator']
        
        if any(keyword in title for keyword in senior_keywords):
            return 'senior'
        elif any(keyword in title for keyword in junior_keywords):
            return 'junior'
        elif any(keyword in title for keyword in mid_keywords):
            return 'mid'
        else:
            return 'mid'  # Default to mid-level
    
    def _analyze_overview(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate overview statistics"""
        return {
            'total_jobs': len(df),
            'unique_companies': df['company'].nunique() if 'company' in df.columns else 0,
            'unique_locations': df['location_standardized'].nunique() if 'location_standardized' in df.columns else 0,
            'jobs_with_salary': df['salary_numeric'].notna().sum() if 'salary_numeric' in df.columns else 0,
            'avg_jobs_per_company': len(df) / df['company'].nunique() if 'company' in df.columns and df['company'].nunique() > 0 else 0,
            'data_quality_score': self._calculate_data_quality_score(df)
        }
    
    def _analyze_companies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze company-related metrics"""
        if 'company' not in df.columns:
            return {}
        
        company_stats = df['company'].value_counts().head(20)
        
        return {
            'top_hiring_companies': company_stats.to_dict(),
            'total_companies': df['company'].nunique(),
            'companies_with_multiple_jobs': (company_stats > 1).sum(),
            'avg_jobs_per_company': company_stats.mean(),
            'median_jobs_per_company': company_stats.median(),
            'company_diversity_index': self._calculate_diversity_index(company_stats)
        }
    
    def _analyze_locations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze location-related metrics"""
        if 'location_standardized' not in df.columns:
            return {}
        
        location_stats = df['location_standardized'].value_counts()
        
        analysis = {
            'job_distribution_by_location': location_stats.head(20).to_dict(),
            'total_locations': len(location_stats),
            'major_city_percentage': (df['is_major_city'].sum() / len(df) * 100) if 'is_major_city' in df.columns else 0,
            'location_diversity_index': self._calculate_diversity_index(location_stats)
        }
        
        # Major city breakdown
        if 'is_major_city' in df.columns:
            major_cities = df[df['is_major_city']]['location_standardized'].value_counts()
            analysis['major_city_breakdown'] = major_cities.to_dict()
        
        return analysis
    
    def _analyze_job_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze job types and categories"""
        analysis = {}
        
        if 'job_category' in df.columns:
            category_stats = df['job_category'].value_counts()
            analysis['category_distribution'] = category_stats.to_dict()
            analysis['most_in_demand_category'] = category_stats.index[0] if len(category_stats) > 0 else None
        
        if 'seniority_level' in df.columns:
            seniority_stats = df['seniority_level'].value_counts()
            analysis['seniority_distribution'] = seniority_stats.to_dict()
        
        if 'job_type' in df.columns:
            type_stats = df['job_type'].value_counts()
            analysis['employment_type_distribution'] = type_stats.to_dict()
        
        return analysis
    
    def _analyze_salaries(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze salary-related metrics"""
        if 'salary_numeric' not in df.columns:
            return {}
        
        salary_data = df['salary_numeric'].dropna()
        
        if len(salary_data) == 0:
            return {'message': 'No salary data available'}
        
        analysis = {
            'salary_statistics': {
                'mean': salary_data.mean(),
                'median': salary_data.median(),
                'std': salary_data.std(),
                'min': salary_data.min(),
                'max': salary_data.max(),
                'q25': salary_data.quantile(0.25),
                'q75': salary_data.quantile(0.75)
            },
            'salary_range_distribution': df['salary_range'].value_counts().to_dict() if 'salary_range' in df.columns else {},
            'jobs_with_salary_info': len(salary_data),
            'salary_transparency_rate': len(salary_data) / len(df) * 100
        }
        
        # Salary by category
        if 'job_category' in df.columns:
            category_salaries = df.groupby('job_category')['salary_numeric'].agg(['mean', 'median', 'count']).round(2)
            analysis['salary_by_category'] = category_salaries.to_dict('index')
        
        # Salary by location
        if 'location_standardized' in df.columns:
            location_salaries = df.groupby('location_standardized')['salary_numeric'].agg(['mean', 'median', 'count']).round(2)
            analysis['salary_by_location'] = location_salaries.head(10).to_dict('index')
        
        return analysis
    
    def _analyze_skills_demand(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze skills demand from job titles and descriptions"""
        skills_counter = Counter()
        
        # Analyze titles
        if 'title' in df.columns:
            for title in df['title'].fillna(''):
                skills_counter.update(self._extract_skills(title))
        
        # Analyze descriptions if available
        if 'description' in df.columns:
            for desc in df['description'].fillna(''):
                skills_counter.update(self._extract_skills(desc))
        
        # Get top skills
        top_skills = dict(skills_counter.most_common(50))
        
        # Categorize skills
        tech_skills = {skill: count for skill, count in top_skills.items() 
                      if skill in self.config['tech_keywords']}
        
        return {
            'top_skills': top_skills,
            'tech_skills_demand': tech_skills,
            'total_unique_skills': len(skills_counter),
            'most_demanded_skill': skills_counter.most_common(1)[0] if skills_counter else None
        }
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        if not text:
            return []
        
        text = text.lower()
        skills = []
        
        # Common skills and technologies
        skill_patterns = [
            r'\bpython\b', r'\bjava\b', r'\bjavascript\b', r'\breact\b', r'\bnode\.?js\b',
            r'\bdjango\b', r'\bflask\b', r'\bsql\b', r'\bmysql\b', r'\bpostgresql\b',
            r'\bmongodb\b', r'\bhtml\b', r'\bcss\b', r'\bbootstrap\b', r'\bjquery\b',
            r'\bangular\b', r'\bvue\.?js\b', r'\bphp\b', r'\blaravel\b', r'\bwordpress\b',
            r'\bgit\b', r'\bdocker\b', r'\baws\b', r'\bazure\b', r'\blinux\b'
        ]
        
        for pattern in skill_patterns:
            if re.search(pattern, text):
                skill = re.search(pattern, text).group().replace('.', '')
                skills.append(skill)
        
        return skills
    
    def _analyze_sources(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze job sources"""
        if 'source' not in df.columns:
            return {}
        
        source_stats = df['source'].value_counts()
        
        analysis = {
            'jobs_by_source': source_stats.to_dict(),
            'source_diversity': len(source_stats),
            'largest_source': source_stats.index[0] if len(source_stats) > 0 else None,
            'source_market_share': (source_stats / len(df) * 100).round(2).to_dict()
        }
        
        # Quality analysis by source
        if 'salary_numeric' in df.columns:
            source_quality = df.groupby('source').agg({
                'salary_numeric': lambda x: x.notna().sum() / len(x) * 100,  # Salary info rate
                'title': lambda x: x.str.len().mean(),  # Average title length
                'company': lambda x: x.notna().sum() / len(x) * 100  # Company info rate
            }).round(2)
            
            analysis['data_quality_by_source'] = source_quality.to_dict('index')
        
        return analysis
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market trends"""
        trends = {}
        
        if 'scraped_date' in df.columns and df['scraped_date'].notna().any():
            # Daily job posting trends
            daily_jobs = df.groupby(df['scraped_date'].dt.date).size()
            trends['daily_posting_trend'] = daily_jobs.to_dict()
            
            # Recent activity
            last_week = datetime.now() - timedelta(days=7)
            recent_jobs = df[df['scraped_date'] > last_week]
            trends['jobs_last_week'] = len(recent_jobs)
            trends['daily_average_last_week'] = len(recent_jobs) / 7
        
        # Category growth patterns
        if 'job_category' in df.columns:
            category_trends = df['job_category'].value_counts()
            trends['growing_categories'] = category_trends.head(5).to_dict()
        
        return trends
    
    def _analyze_competition(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        competition = {}
        
        if 'company' in df.columns:
            # Companies with most job openings (indicating growth/hiring spree)
            top_hiring = df['company'].value_counts().head(10)
            competition['most_active_hirers'] = top_hiring.to_dict()
            
            # Competition by category
            if 'job_category' in df.columns:
                category_competition = df.groupby('job_category')['company'].nunique().sort_values(ascending=False)
                competition['competition_by_category'] = category_competition.to_dict()
        
        return competition
    
    def _identify_opportunities(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify market opportunities"""
        opportunities = {}
        
        # High-demand, low-supply areas
        if 'job_category' in df.columns and 'location_standardized' in df.columns:
            location_category = df.groupby(['location_standardized', 'job_category']).size().unstack(fill_value=0)
            
            # Find categories with high demand in specific locations
            opportunities['location_category_opportunities'] = {}
            for location in location_category.index:
                top_categories = location_category.loc[location].nlargest(3)
                opportunities['location_category_opportunities'][location] = top_categories.to_dict()
        
        # Salary gaps (categories with wide salary ranges)
        if 'salary_numeric' in df.columns and 'job_category' in df.columns:
            salary_stats = df.groupby('job_category')['salary_numeric'].agg(['min', 'max', 'std']).dropna()
            salary_stats['range'] = salary_stats['max'] - salary_stats['min']
            high_variance = salary_stats.nlargest(5, 'range')
            opportunities['high_salary_variance_categories'] = high_variance.to_dict('index')
        
        return opportunities
    
    def _generate_insights(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> List[MarketInsight]:
        """Generate key market insights"""
        insights = []
        
        # Job market size insight
        insights.append(MarketInsight(
            category='market_size',
            metric='total_jobs',
            value=len(df),
            trend=None,
            description=f"Nepal job market has {len(df)} active job listings across {df['source'].nunique() if 'source' in df.columns else 'multiple'} platforms",
            confidence=0.9
        ))
        
        # Top hiring company insight
        if 'companies' in analysis and 'top_hiring_companies' in analysis['companies']:
            top_company = list(analysis['companies']['top_hiring_companies'].keys())[0]
            job_count = list(analysis['companies']['top_hiring_companies'].values())[0]
            insights.append(MarketInsight(
                category='hiring_activity',
                metric='top_hirer',
                value=top_company,
                trend='high',
                description=f"{top_company} is the most active hirer with {job_count} job openings",
                confidence=0.8
            ))
        
        # Salary transparency insight
        if 'salaries' in analysis and 'salary_transparency_rate' in analysis['salaries']:
            transparency_rate = analysis['salaries']['salary_transparency_rate']
            insights.append(MarketInsight(
                category='salary_transparency',
                metric='transparency_rate',
                value=f"{transparency_rate:.1f}%",
                trend='low' if transparency_rate < 30 else 'medium' if transparency_rate < 60 else 'high',
                description=f"Only {transparency_rate:.1f}% of jobs provide salary information",
                confidence=0.9
            ))
        
        # Location concentration insight
        if 'locations' in analysis and 'major_city_percentage' in analysis['locations']:
            city_percentage = analysis['locations']['major_city_percentage']
            insights.append(MarketInsight(
                category='geographic_distribution',
                metric='city_concentration',
                value=f"{city_percentage:.1f}%",
                trend='high' if city_percentage > 70 else 'medium',
                description=f"{city_percentage:.1f}% of jobs are concentrated in major cities",
                confidence=0.8
            ))
        
        return insights
    
    def _calculate_data_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate overall data quality score"""
        scores = []
        
        # Title completeness
        if 'title' in df.columns:
            title_score = df['title'].notna().sum() / len(df)
            scores.append(title_score)
        
        # Company completeness
        if 'company' in df.columns:
            company_score = df['company'].notna().sum() / len(df)
            scores.append(company_score)
        
        # Location completeness
        if 'location' in df.columns:
            location_score = df['location'].notna().sum() / len(df)
            scores.append(location_score)
        
        # Salary completeness (weighted less as it's often missing)
        if 'salary_numeric' in df.columns:
            salary_score = df['salary_numeric'].notna().sum() / len(df) * 0.5
            scores.append(salary_score)
        
        return np.mean(scores) if scores else 0.0
    
    def _calculate_diversity_index(self, value_counts: pd.Series) -> float:
        """Calculate diversity index (Shannon entropy)"""
        if len(value_counts) == 0:
            return 0.0
        
        proportions = value_counts / value_counts.sum()
        entropy = -np.sum(proportions * np.log(proportions + 1e-10))  # Add small value to avoid log(0)
        max_entropy = np.log(len(proportions))
        
        return entropy / max_entropy if max_entropy > 0 else 0.0
    
    def export_analysis(self, analysis: Dict[str, Any], output_file: str = None) -> str:
        """Export analysis results"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'analytics/reports/market_analysis_{timestamp}.json'
        
        # Convert MarketInsight objects to dictionaries for JSON serialization
        if 'insights' in analysis:
            analysis['insights'] = [
                {
                    'category': insight.category,
                    'metric': insight.metric,
                    'value': insight.value,
                    'trend': insight.trend,
                    'description': insight.description,
                    'confidence': insight.confidence
                }
                for insight in analysis['insights']
            ]
        
        # Ensure directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        return output_file

def main():
    """Test the data analyzer"""
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
    ]
    
    analyzer = DataAnalyzer()
    analysis = analyzer.analyze_market(sample_jobs)
    
    print("=== Market Analysis Results ===")
    print(f"Total jobs analyzed: {analysis['overview']['total_jobs']}")
    print(f"Unique companies: {analysis['overview']['unique_companies']}")
    print(f"Data quality score: {analysis['overview']['data_quality_score']:.2f}")
    
    print("\n=== Key Insights ===")
    for insight in analysis['insights']:
        print(f"- {insight['description']} (Confidence: {insight['confidence']:.1f})")

if __name__ == "__main__":
    main() 