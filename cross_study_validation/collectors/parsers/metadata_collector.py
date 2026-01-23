"""
Metadata collection for study characteristics.

This module infers study metadata from directory structure and query files.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MetadataCollector:
    """Collect metadata about a systematic review study."""
    
    # Domain keywords for heuristic classification
    DOMAIN_KEYWORDS = {
        'sleep medicine': ['sleep', 'apnea', 'insomnia', 'circadian', 'somnolence'],
        'nutrition': ['diet', 'food', 'nutrition', 'mediterranean', 'fruit', 'vegetable'],
        'artificial intelligence': ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural network'],
        'cardiology': ['cardiac', 'heart', 'cardiovascular', 'coronary', 'myocardial'],
        'oncology': ['cancer', 'tumor', 'neoplasm', 'carcinoma', 'oncology'],
        'neurology': ['brain', 'neural', 'cognitive', 'alzheimer', 'parkinson'],
        'microbiome': ['microbiome', 'microbiota', 'gut', 'bacteria', 'microbial']
    }
    
    def __init__(self, study_dir: Path):
        """
        Initialize collector with study directory.
        
        Args:
            study_dir: Path to studies/<study_id>/ directory
        """
        self.study_dir = Path(study_dir)
        if not self.study_dir.exists():
            raise FileNotFoundError(f"Study directory not found: {study_dir}")
        
        self.study_id = self.study_dir.name
    
    def collect(self) -> Dict:
        """
        Collect all metadata for the study.
        
        Returns:
            Dict with keys:
                - domain: str (inferred domain)
                - databases: List[str] (databases used)
                - num_queries: int (total queries)
                - date_range: Dict (start/end dates if found)
                - has_embase: bool (whether Embase data exists)
        """
        metadata = {
            'domain': self._infer_domain(),
            'databases': self._detect_databases(),
            'num_queries': self._count_queries(),
            'date_range': self._extract_date_range(),
            'has_embase': self._check_embase()
        }
        
        logger.info(f"Collected metadata for {self.study_id}")
        logger.info(f"  Domain: {metadata['domain']}")
        logger.info(f"  Databases: {metadata['databases']}")
        logger.info(f"  Queries: {metadata['num_queries']}")
        logger.info(f"  Has Embase: {metadata['has_embase']}")
        
        return metadata
    
    def _detect_databases(self) -> List[str]:
        """Detect which databases were queried based on query files."""
        databases = []
        
        # Check for database-specific query files
        if (self.study_dir / 'queries.txt').exists():
            databases.append('pubmed')
        if (self.study_dir / 'queries_scopus.txt').exists():
            databases.append('scopus')
        if (self.study_dir / 'queries_wos.txt').exists():
            databases.append('wos')
        if (self.study_dir / 'queries_embase.txt').exists() or self._check_embase():
            databases.append('embase')
        
        return databases
    
    def _count_queries(self) -> int:
        """Count total number of queries across all databases."""
        query_file = self.study_dir / 'queries.txt'
        if not query_file.exists():
            logger.warning(f"No queries.txt found in {self.study_dir}")
            return 0
        
        # Count non-empty lines in queries.txt
        with open(query_file, 'r', encoding='utf-8') as f:
            queries = [line.strip() for line in f if line.strip()]
        
        return len(queries)
    
    def _extract_date_range(self) -> Optional[Dict[str, str]]:
        """Extract date range from query strings if present."""
        query_file = self.study_dir / 'queries.txt'
        if not query_file.exists():
            return None
        
        with open(query_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern for PubMed date filters: "YYYY/MM/DD"[Date - Publication] : "YYYY/MM/DD"[Date - Publication]
        date_pattern = r'"(\d{4})/(\d{2})/(\d{2})"\[Date - Publication\]\s*:\s*"(\d{4})/(\d{2})/(\d{2})"\[Date - Publication\]'
        match = re.search(date_pattern, content)
        
        if match:
            start_year, start_month, start_day = match.groups()[:3]
            end_year, end_month, end_day = match.groups()[3:]
            return {
                'start': f"{start_year}-{start_month}-{start_day}",
                'end': f"{end_year}-{end_month}-{end_day}"
            }
        
        # Alternative pattern: AND (YYYY:YYYY[edat])
        alt_pattern = r'\((\d{4}):(\d{4})\[edat\]\)'
        match = re.search(alt_pattern, content)
        if match:
            start_year, end_year = match.groups()
            return {
                'start': f"{start_year}-01-01",
                'end': f"{end_year}-12-31"
            }
        
        logger.warning(f"Could not extract date range from queries for {self.study_id}")
        return None
    
    def _infer_domain(self) -> str:
        """
        Infer study domain from query content and study name.
        
        Uses keyword matching heuristics. Can be manually corrected later.
        """
        # First check study name
        study_name_lower = self.study_id.lower()
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(keyword in study_name_lower for keyword in keywords):
                return domain
        
        # Check query content
        query_file = self.study_dir / 'queries.txt'
        if query_file.exists():
            with open(query_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            domain_scores = {}
            for domain, keywords in self.DOMAIN_KEYWORDS.items():
                score = sum(content.count(keyword) for keyword in keywords)
                if score > 0:
                    domain_scores[domain] = score
            
            if domain_scores:
                best_domain = max(domain_scores, key=domain_scores.get)
                logger.info(f"Inferred domain '{best_domain}' with confidence score {domain_scores[best_domain]}")
                return best_domain
        
        # Check for guidelines or search strategy files
        for doc_file in ['guidelines.md', 'general_guidelines.md', 'search_strategy.md', 'prospero*.md']:
            for file_path in self.study_dir.glob(doc_file):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                for domain, keywords in self.DOMAIN_KEYWORDS.items():
                    if any(keyword in content for keyword in keywords):
                        logger.info(f"Inferred domain '{domain}' from {file_path.name}")
                        return domain
        
        logger.warning(f"Could not infer domain for {self.study_id}, using 'general medicine'")
        return 'general medicine'
    
    def _check_embase(self) -> bool:
        """Check if Embase data is available."""
        embase_dir = self.study_dir / 'embase_manual_queries'
        if not embase_dir.exists():
            return False
        
        # Check if directory has CSV files
        csv_files = list(embase_dir.glob('*.csv'))
        return len(csv_files) > 0


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("\n=== Testing Metadata Collector ===")
    
    for study_id in ['Godos_2024', 'ai_2022', 'sleep_apnea']:
        print(f"\n--- {study_id} ---")
        study_dir = Path(f'studies/{study_id}')
        if study_dir.exists():
            collector = MetadataCollector(study_dir)
            metadata = collector.collect()
            print(f"  Domain: {metadata['domain']}")
            print(f"  Databases: {', '.join(metadata['databases'])}")
            print(f"  Queries: {metadata['num_queries']}")
            print(f"  Date range: {metadata['date_range']}")
            print(f"  Has Embase: {metadata['has_embase']}")
        else:
            print(f"  ✗ Directory not found")
