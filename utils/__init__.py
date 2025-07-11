"""
Utilities for Nepal Job Scraper

This package contains base classes, utilities, and common functionality
for scraping job websites in Nepal.
"""

from .base_scraper import BaseScraper
from .data_manager import DataManager
from .logger_config import setup_logger

__all__ = ['BaseScraper', 'DataManager', 'setup_logger'] 