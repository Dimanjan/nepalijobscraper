"""
Data Manager for Nepal Job Scraper.

Handles data storage, validation, and export functionality.
Ensures data safety and provides easy access to scraped information.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from .logger_config import setup_logger


class DataManager:
    """Manages data storage and retrieval for scraped job data."""
    
    def __init__(self, base_path: str = "data"):
        """
        Initialize the data manager.
        
        Args:
            base_path: Base directory for data storage
        """
        self.base_path = Path(base_path)
        self.raw_path = self.base_path / "raw"
        self.processed_path = self.base_path / "processed"
        self.exports_path = self.base_path / "exports"
        
        # Create directories if they don't exist
        for path in [self.raw_path, self.processed_path, self.exports_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        self.logger = setup_logger("data_manager")
    
    def save_job(self, job_data: Dict[str, Any], website_name: str) -> str:
        """
        Save a single job to raw data storage.
        
        Args:
            job_data: Job data dictionary
            website_name: Name of the source website
            
        Returns:
            Path to saved file
        """
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_id = job_data.get('id', f"job_{timestamp}")
        filename = f"{website_name}_{job_id}_{timestamp}.json"
        
        file_path = self.raw_path / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Saved job to {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Error saving job data: {str(e)}")
            raise
    
    def save_batch(self, jobs: List[Dict[str, Any]], website_name: str) -> str:
        """
        Save a batch of jobs to a single file.
        
        Args:
            jobs: List of job dictionaries
            website_name: Name of the source website
            
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{website_name}_batch_{timestamp}.json"
        file_path = self.raw_path / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(jobs)} jobs to {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Error saving batch data: {str(e)}")
            raise
    
    def load_jobs(self, website_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load jobs from raw data storage.
        
        Args:
            website_name: Filter by website name (None for all)
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        # Find all JSON files
        pattern = f"{website_name}_*.json" if website_name else "*.json"
        
        for file_path in self.raw_path.glob(pattern):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle both single jobs and batches
                if isinstance(data, list):
                    jobs.extend(data)
                else:
                    jobs.append(data)
                    
            except Exception as e:
                self.logger.error(f"Error loading {file_path}: {str(e)}")
                continue
        
        self.logger.info(f"Loaded {len(jobs)} jobs")
        return jobs
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored data.
        
        Returns:
            Dictionary with data statistics
        """
        stats = {
            'total_files': 0,
            'total_jobs': 0,
            'websites': {},
            'date_range': {'earliest': None, 'latest': None}
        }
        
        for file_path in self.raw_path.glob("*.json"):
            stats['total_files'] += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle both single jobs and batches
                if isinstance(data, list):
                    job_count = len(data)
                    jobs = data
                else:
                    job_count = 1
                    jobs = [data]
                
                stats['total_jobs'] += job_count
                
                # Extract website info
                for job in jobs:
                    website = job.get('source_website', 'unknown')
                    if website not in stats['websites']:
                        stats['websites'][website] = 0
                    stats['websites'][website] += 1
                    
                    # Track date range
                    scraped_at = job.get('scraped_at')
                    if scraped_at:
                        if not stats['date_range']['earliest'] or scraped_at < stats['date_range']['earliest']:
                            stats['date_range']['earliest'] = scraped_at
                        if not stats['date_range']['latest'] or scraped_at > stats['date_range']['latest']:
                            stats['date_range']['latest'] = scraped_at
                            
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {str(e)}")
                continue
        
        return stats
    
    def export_to_csv(self, website_name: Optional[str] = None, 
                      filename: Optional[str] = None) -> str:
        """
        Export jobs to CSV format.
        
        Args:
            website_name: Filter by website name (None for all)
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported CSV file
        """
        jobs = self.load_jobs(website_name)
        
        if not jobs:
            raise ValueError("No jobs found to export")
        
        # Create DataFrame
        df = pd.DataFrame(jobs)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            website_part = f"{website_name}_" if website_name else "all_"
            filename = f"{website_part}jobs_{timestamp}.csv"
        
        file_path = self.exports_path / filename
        
        try:
            df.to_csv(file_path, index=False, encoding='utf-8')
            self.logger.info(f"Exported {len(jobs)} jobs to {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {str(e)}")
            raise
    
    def export_to_json(self, website_name: Optional[str] = None,
                       filename: Optional[str] = None) -> str:
        """
        Export jobs to JSON format.
        
        Args:
            website_name: Filter by website name (None for all)
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported JSON file
        """
        jobs = self.load_jobs(website_name)
        
        if not jobs:
            raise ValueError("No jobs found to export")
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            website_part = f"{website_name}_" if website_name else "all_"
            filename = f"{website_part}jobs_{timestamp}.json"
        
        file_path = self.exports_path / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported {len(jobs)} jobs to {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {str(e)}")
            raise
    
    def clean_duplicates(self) -> int:
        """
        Remove duplicate jobs based on title, company, and URL.
        
        Returns:
            Number of duplicates removed
        """
        jobs = self.load_jobs()
        
        if not jobs:
            return 0
        
        # Create DataFrame for duplicate detection
        df = pd.DataFrame(jobs)
        
        # Remove duplicates based on key fields
        duplicate_cols = ['title', 'company', 'url']
        available_cols = [col for col in duplicate_cols if col in df.columns]
        
        if not available_cols:
            self.logger.warning("No suitable columns for duplicate detection")
            return 0
        
        initial_count = len(df)
        df_clean = df.drop_duplicates(subset=available_cols, keep='first')
        duplicates_removed = initial_count - len(df_clean)
        
        if duplicates_removed > 0:
            # Save cleaned data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cleaned_file = self.processed_path / f"cleaned_jobs_{timestamp}.json"
            
            df_clean.to_json(cleaned_file, orient='records', indent=2)
            self.logger.info(f"Removed {duplicates_removed} duplicates, saved to {cleaned_file}")
        
        return duplicates_removed 