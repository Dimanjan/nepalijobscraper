#!/usr/bin/env python3
"""
Robust Duplicate Detection System for Job Listings
Implements multiple algorithms for detecting duplicate jobs with high accuracy
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Set, Any
import re
from difflib import SequenceMatcher
from collections import defaultdict
import hashlib
import logging
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from datetime import datetime

@dataclass
class DuplicateMatch:
    """Represents a duplicate match between two jobs"""
    job1_id: str
    job2_id: str
    similarity_score: float
    match_type: str
    reasons: List[str]
    confidence: float

class DuplicateDetector:
    """Advanced duplicate detection system for job listings"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2)
        )
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for duplicate detection"""
        return {
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
            },
            'fuzzy_threshold': 0.8,
            'min_confidence': 0.6,
            'enable_advanced_matching': True
        }
    
    def detect_duplicates(self, jobs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main function to detect duplicates in job listings
        
        Args:
            jobs_data: List of job dictionaries
            
        Returns:
            Dictionary containing duplicate analysis results
        """
        self.logger.info(f"Starting duplicate detection for {len(jobs_data)} jobs")
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(jobs_data)
        
        # Preprocess data
        df = self._preprocess_data(df)
        
        # Multiple detection strategies
        results = {
            'exact_duplicates': self._find_exact_duplicates(df),
            'fuzzy_duplicates': self._find_fuzzy_duplicates(df),
            'semantic_duplicates': self._find_semantic_duplicates(df),
            'cross_source_duplicates': self._find_cross_source_duplicates(df),
            'summary': {}
        }
        
        # Consolidate results
        all_duplicates = self._consolidate_duplicates(results)
        
        # Generate summary
        results['summary'] = self._generate_summary(df, all_duplicates)
        results['consolidated_duplicates'] = all_duplicates
        
        self.logger.info(f"Duplicate detection completed. Found {len(all_duplicates)} duplicate pairs")
        
        return results
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess job data for better duplicate detection"""
        
        # Add unique ID if not present
        if 'id' not in df.columns:
            df['id'] = df.index.astype(str)
        
        # Clean and normalize text fields
        text_fields = ['title', 'company', 'location', 'description']
        
        for field in text_fields:
            if field in df.columns:
                df[f'{field}_clean'] = df[field].fillna('').apply(self._clean_text)
                df[f'{field}_normalized'] = df[f'{field}_clean'].apply(self._normalize_text)
        
        # Extract features for comparison
        df['title_words'] = df['title_clean'].apply(lambda x: set(x.split()) if x else set())
        df['company_normalized'] = df['company_clean'].apply(self._normalize_company_name)
        
        # Generate fingerprints
        df['fingerprint'] = df.apply(self._generate_fingerprint, axis=1)
        
        return df
    
    def _clean_text(self, text: str) -> str:
        """Clean text for comparison"""
        if pd.isna(text) or not text:
            return ""
        
        # Convert to lowercase
        text = str(text).lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^\w\s-]', ' ', text)
        
        return text
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for better matching"""
        if not text:
            return ""
        
        # Remove common job-related words that add noise
        noise_words = {'job', 'position', 'role', 'vacancy', 'opportunity', 'career'}
        words = text.split()
        words = [w for w in words if w not in noise_words]
        
        return ' '.join(words)
    
    def _normalize_company_name(self, company: str) -> str:
        """Normalize company names for better matching"""
        if not company:
            return ""
        
        # Remove common company suffixes
        suffixes = [
            'pvt ltd', 'private limited', 'ltd', 'inc', 'corp', 'corporation',
            'company', 'co', 'limited', 'llc', 'plc'
        ]
        
        normalized = company.lower()
        for suffix in suffixes:
            normalized = re.sub(rf'\b{suffix}\b', '', normalized)
        
        return normalized.strip()
    
    def _generate_fingerprint(self, row: pd.Series) -> str:
        """Generate a fingerprint for a job listing"""
        # Combine key fields to create a unique fingerprint
        fields = [
            row.get('title_normalized', ''),
            row.get('company_normalized', ''),
            row.get('location_clean', '')
        ]
        
        combined = '|'.join(fields)
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _find_exact_duplicates(self, df: pd.DataFrame) -> List[DuplicateMatch]:
        """Find exact duplicates based on fingerprints"""
        duplicates = []
        
        # Group by fingerprint
        fingerprint_groups = df.groupby('fingerprint')
        
        for fingerprint, group in fingerprint_groups:
            if len(group) > 1:
                # All jobs in this group are exact duplicates
                job_ids = group['id'].tolist()
                for i in range(len(job_ids)):
                    for j in range(i + 1, len(job_ids)):
                        duplicates.append(DuplicateMatch(
                            job1_id=job_ids[i],
                            job2_id=job_ids[j],
                            similarity_score=1.0,
                            match_type='exact',
                            reasons=['identical_fingerprint'],
                            confidence=1.0
                        ))
        
        return duplicates
    
    def _find_fuzzy_duplicates(self, df: pd.DataFrame) -> List[DuplicateMatch]:
        """Find fuzzy duplicates using string similarity"""
        duplicates = []
        threshold = self.config['fuzzy_threshold']
        
        # Compare all pairs (this can be optimized for large datasets)
        for i in range(len(df)):
            for j in range(i + 1, len(df)):
                similarity = self._calculate_fuzzy_similarity(df.iloc[i], df.iloc[j])
                
                if similarity >= threshold:
                    reasons = self._get_similarity_reasons(df.iloc[i], df.iloc[j])
                    confidence = min(similarity, 0.95)  # Cap confidence for fuzzy matches
                    
                    duplicates.append(DuplicateMatch(
                        job1_id=df.iloc[i]['id'],
                        job2_id=df.iloc[j]['id'],
                        similarity_score=similarity,
                        match_type='fuzzy',
                        reasons=reasons,
                        confidence=confidence
                    ))
        
        return duplicates
    
    def _calculate_fuzzy_similarity(self, job1: pd.Series, job2: pd.Series) -> float:
        """Calculate fuzzy similarity between two jobs"""
        weights = self.config['weights']
        total_similarity = 0
        total_weight = 0
        
        # Title similarity
        if 'title_clean' in job1 and 'title_clean' in job2:
            title_sim = SequenceMatcher(None, job1['title_clean'], job2['title_clean']).ratio()
            total_similarity += title_sim * weights['title']
            total_weight += weights['title']
        
        # Company similarity
        if 'company_normalized' in job1 and 'company_normalized' in job2:
            company_sim = SequenceMatcher(None, job1['company_normalized'], job2['company_normalized']).ratio()
            total_similarity += company_sim * weights['company']
            total_weight += weights['company']
        
        # Location similarity
        if 'location_clean' in job1 and 'location_clean' in job2:
            location_sim = SequenceMatcher(None, job1['location_clean'], job2['location_clean']).ratio()
            total_similarity += location_sim * weights['location']
            total_weight += weights['location']
        
        # Description similarity (if available)
        if 'description_clean' in job1 and 'description_clean' in job2:
            desc_sim = SequenceMatcher(None, job1['description_clean'], job2['description_clean']).ratio()
            total_similarity += desc_sim * weights['description']
            total_weight += weights['description']
        
        return total_similarity / total_weight if total_weight > 0 else 0
    
    def _find_semantic_duplicates(self, df: pd.DataFrame) -> List[DuplicateMatch]:
        """Find semantic duplicates using TF-IDF and cosine similarity"""
        if not self.config['enable_advanced_matching']:
            return []
        
        duplicates = []
        
        # Combine title and description for semantic analysis
        texts = []
        for _, row in df.iterrows():
            combined_text = f"{row.get('title_clean', '')} {row.get('description_clean', '')}"
            texts.append(combined_text)
        
        if not any(texts):  # No text to analyze
            return duplicates
        
        try:
            # Create TF-IDF matrix
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Calculate cosine similarities
            similarities = cosine_similarity(tfidf_matrix)
            
            # Find similar pairs
            threshold = self.config['similarity_thresholds']['medium_similarity']
            
            for i in range(len(similarities)):
                for j in range(i + 1, len(similarities)):
                    if similarities[i][j] >= threshold:
                        duplicates.append(DuplicateMatch(
                            job1_id=df.iloc[i]['id'],
                            job2_id=df.iloc[j]['id'],
                            similarity_score=similarities[i][j],
                            match_type='semantic',
                            reasons=['semantic_similarity'],
                            confidence=similarities[i][j] * 0.8  # Lower confidence for semantic matches
                        ))
        
        except Exception as e:
            self.logger.warning(f"Semantic analysis failed: {e}")
        
        return duplicates
    
    def _find_cross_source_duplicates(self, df: pd.DataFrame) -> List[DuplicateMatch]:
        """Find duplicates across different job sources"""
        duplicates = []
        
        if 'source' not in df.columns:
            return duplicates
        
        # Group by source and compare across sources
        sources = df['source'].unique()
        
        for i, source1 in enumerate(sources):
            for source2 in sources[i + 1:]:
                df1 = df[df['source'] == source1]
                df2 = df[df['source'] == source2]
                
                # Compare jobs between different sources
                for _, job1 in df1.iterrows():
                    for _, job2 in df2.iterrows():
                        similarity = self._calculate_cross_source_similarity(job1, job2)
                        
                        if similarity >= self.config['similarity_thresholds']['high_similarity']:
                            duplicates.append(DuplicateMatch(
                                job1_id=job1['id'],
                                job2_id=job2['id'],
                                similarity_score=similarity,
                                match_type='cross_source',
                                reasons=[f'cross_source_{source1}_{source2}'],
                                confidence=similarity * 0.9
                            ))
        
        return duplicates
    
    def _calculate_cross_source_similarity(self, job1: pd.Series, job2: pd.Series) -> float:
        """Calculate similarity specifically for cross-source comparison"""
        # For cross-source, focus more on title and company
        weights = {'title': 0.6, 'company': 0.4}
        total_similarity = 0
        total_weight = 0
        
        # Title similarity
        if 'title_clean' in job1 and 'title_clean' in job2:
            title_sim = SequenceMatcher(None, job1['title_clean'], job2['title_clean']).ratio()
            total_similarity += title_sim * weights['title']
            total_weight += weights['title']
        
        # Company similarity
        if 'company_normalized' in job1 and 'company_normalized' in job2:
            company_sim = SequenceMatcher(None, job1['company_normalized'], job2['company_normalized']).ratio()
            total_similarity += company_sim * weights['company']
            total_weight += weights['company']
        
        return total_similarity / total_weight if total_weight > 0 else 0
    
    def _get_similarity_reasons(self, job1: pd.Series, job2: pd.Series) -> List[str]:
        """Get specific reasons why two jobs are considered similar"""
        reasons = []
        
        # Check title similarity
        if 'title_clean' in job1 and 'title_clean' in job2:
            title_sim = SequenceMatcher(None, job1['title_clean'], job2['title_clean']).ratio()
            if title_sim > 0.9:
                reasons.append('very_similar_titles')
            elif title_sim > 0.7:
                reasons.append('similar_titles')
        
        # Check company similarity
        if 'company_normalized' in job1 and 'company_normalized' in job2:
            company_sim = SequenceMatcher(None, job1['company_normalized'], job2['company_normalized']).ratio()
            if company_sim > 0.9:
                reasons.append('same_company')
            elif company_sim > 0.7:
                reasons.append('similar_company')
        
        # Check location similarity
        if 'location_clean' in job1 and 'location_clean' in job2:
            location_sim = SequenceMatcher(None, job1['location_clean'], job2['location_clean']).ratio()
            if location_sim > 0.9:
                reasons.append('same_location')
        
        return reasons
    
    def _consolidate_duplicates(self, results: Dict[str, List[DuplicateMatch]]) -> List[DuplicateMatch]:
        """Consolidate duplicates from different detection methods"""
        all_duplicates = []
        seen_pairs = set()
        
        # Combine all duplicate matches
        for method, duplicates in results.items():
            if method == 'summary':
                continue
                
            for duplicate in duplicates:
                # Create a unique key for the pair
                pair_key = tuple(sorted([duplicate.job1_id, duplicate.job2_id]))
                
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    all_duplicates.append(duplicate)
                else:
                    # If we've seen this pair before, update with highest confidence
                    existing_idx = next(
                        i for i, d in enumerate(all_duplicates)
                        if tuple(sorted([d.job1_id, d.job2_id])) == pair_key
                    )
                    
                    if duplicate.confidence > all_duplicates[existing_idx].confidence:
                        all_duplicates[existing_idx] = duplicate
        
        # Sort by confidence
        all_duplicates.sort(key=lambda x: x.confidence, reverse=True)
        
        return all_duplicates
    
    def _generate_summary(self, df: pd.DataFrame, duplicates: List[DuplicateMatch]) -> Dict[str, Any]:
        """Generate summary statistics"""
        total_jobs = len(df)
        unique_jobs_in_duplicates = set()
        
        for dup in duplicates:
            unique_jobs_in_duplicates.add(dup.job1_id)
            unique_jobs_in_duplicates.add(dup.job2_id)
        
        # Calculate statistics by source
        source_stats = {}
        if 'source' in df.columns:
            for source in df['source'].unique():
                source_jobs = df[df['source'] == source]
                source_duplicates = [
                    d for d in duplicates
                    if df[df['id'] == d.job1_id]['source'].iloc[0] == source or
                       df[df['id'] == d.job2_id]['source'].iloc[0] == source
                ]
                
                source_stats[source] = {
                    'total_jobs': len(source_jobs),
                    'duplicate_pairs': len(source_duplicates),
                    'unique_jobs_affected': len(set([d.job1_id for d in source_duplicates] + [d.job2_id for d in source_duplicates]))
                }
        
        return {
            'total_jobs': total_jobs,
            'duplicate_pairs': len(duplicates),
            'unique_jobs_affected': len(unique_jobs_in_duplicates),
            'duplicate_rate': len(unique_jobs_in_duplicates) / total_jobs if total_jobs > 0 else 0,
            'estimated_unique_jobs': total_jobs - len(unique_jobs_in_duplicates) + len(duplicates),
            'source_statistics': source_stats,
            'confidence_distribution': self._get_confidence_distribution(duplicates),
            'match_type_distribution': self._get_match_type_distribution(duplicates)
        }
    
    def _get_confidence_distribution(self, duplicates: List[DuplicateMatch]) -> Dict[str, int]:
        """Get distribution of confidence levels"""
        distribution = {'high': 0, 'medium': 0, 'low': 0}
        
        for dup in duplicates:
            if dup.confidence >= 0.8:
                distribution['high'] += 1
            elif dup.confidence >= 0.6:
                distribution['medium'] += 1
            else:
                distribution['low'] += 1
        
        return distribution
    
    def _get_match_type_distribution(self, duplicates: List[DuplicateMatch]) -> Dict[str, int]:
        """Get distribution of match types"""
        distribution = defaultdict(int)
        
        for dup in duplicates:
            distribution[dup.match_type] += 1
        
        return dict(distribution)
    
    def remove_duplicates(self, jobs_data: List[Dict[str, Any]], 
                         duplicates: List[DuplicateMatch],
                         strategy: str = 'keep_first') -> List[Dict[str, Any]]:
        """
        Remove duplicates from job data
        
        Args:
            jobs_data: List of job dictionaries
            duplicates: List of duplicate matches
            strategy: 'keep_first', 'keep_best_source', 'keep_most_complete'
        """
        # Create a set of job IDs to remove
        jobs_to_remove = set()
        
        for dup in duplicates:
            if dup.confidence >= self.config['min_confidence']:
                if strategy == 'keep_first':
                    # Keep the first job, remove the second
                    jobs_to_remove.add(dup.job2_id)
                elif strategy == 'keep_best_source':
                    # Implement source priority logic
                    job1 = next(job for job in jobs_data if str(job.get('id', '')) == dup.job1_id)
                    job2 = next(job for job in jobs_data if str(job.get('id', '')) == dup.job2_id)
                    
                    source_priority = {'merojob': 1, 'jobaxle': 2, 'froxjob': 3, 'hamrojobs': 4}
                    
                    source1_priority = source_priority.get(job1.get('source', ''), 999)
                    source2_priority = source_priority.get(job2.get('source', ''), 999)
                    
                    if source1_priority <= source2_priority:
                        jobs_to_remove.add(dup.job2_id)
                    else:
                        jobs_to_remove.add(dup.job1_id)
        
        # Filter out jobs to remove
        cleaned_jobs = [
            job for job in jobs_data
            if str(job.get('id', '')) not in jobs_to_remove
        ]
        
        return cleaned_jobs
    
    def export_duplicate_report(self, results: Dict[str, Any], 
                               output_file: str = None) -> str:
        """Export duplicate analysis report"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'analytics/reports/duplicate_analysis_{timestamp}.json'
        
        # Convert DuplicateMatch objects to dictionaries for JSON serialization
        serializable_results = {}
        
        for key, value in results.items():
            if isinstance(value, list) and value and isinstance(value[0], DuplicateMatch):
                serializable_results[key] = [
                    {
                        'job1_id': dup.job1_id,
                        'job2_id': dup.job2_id,
                        'similarity_score': dup.similarity_score,
                        'match_type': dup.match_type,
                        'reasons': dup.reasons,
                        'confidence': dup.confidence
                    }
                    for dup in value
                ]
            else:
                serializable_results[key] = value
        
        with open(output_file, 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)
        
        return output_file

def main():
    """Test the duplicate detector"""
    # Sample data for testing
    sample_jobs = [
        {'id': '1', 'title': 'Software Engineer', 'company': 'Tech Corp Pvt Ltd', 'location': 'Kathmandu', 'source': 'merojob'},
        {'id': '2', 'title': 'Software Engineer', 'company': 'Tech Corp', 'location': 'Kathmandu', 'source': 'jobaxle'},
        {'id': '3', 'title': 'Senior Software Developer', 'company': 'Tech Corporation', 'location': 'Kathmandu', 'source': 'froxjob'},
        {'id': '4', 'title': 'Marketing Manager', 'company': 'Marketing Plus', 'location': 'Lalitpur', 'source': 'merojob'},
        {'id': '5', 'title': 'Software Engineer', 'company': 'Tech Corp Private Limited', 'location': 'Kathmandu, Nepal', 'source': 'hamrojobs'},
    ]
    
    detector = DuplicateDetector()
    results = detector.detect_duplicates(sample_jobs)
    
    print("=== Duplicate Detection Results ===")
    print(f"Total jobs: {results['summary']['total_jobs']}")
    print(f"Duplicate pairs found: {results['summary']['duplicate_pairs']}")
    print(f"Duplicate rate: {results['summary']['duplicate_rate']:.2%}")
    
    print("\n=== Duplicate Pairs ===")
    for dup in results['consolidated_duplicates']:
        print(f"Jobs {dup.job1_id} <-> {dup.job2_id}: "
              f"Score={dup.similarity_score:.3f}, "
              f"Type={dup.match_type}, "
              f"Confidence={dup.confidence:.3f}")

if __name__ == "__main__":
    main() 