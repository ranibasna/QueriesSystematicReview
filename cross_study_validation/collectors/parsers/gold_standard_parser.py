"""
Gold standard extractor for cross-study validation.

This module extracts and validates gold standard reference lists from CSV files.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


class GoldStandardExtractor:
    """Extract and validate gold standard reference lists."""
    
    # PMID validation: 8 digits typically
    PMID_PATTERN = re.compile(r'^\d{7,9}$')
    
    # DOI validation: Basic pattern
    DOI_PATTERN = re.compile(r'^10\.\d{4,}/[\S]+$')
    
    def __init__(self, csv_path: Path):
        """
        Initialize extractor with path to gold standard CSV.
        
        Args:
            csv_path: Path to gold_pmids_*.csv file
        """
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Gold standard CSV not found: {csv_path}")
    
    def extract(self) -> Dict:
        """
        Extract and validate gold standard PMIDs/DOIs.
        
        Returns:
            Dict with keys:
                - pmids: List[str] of validated PMIDs
                - dois: List[str] of DOIs (if available)
                - count: int number of references
                - invalid_pmids: List[str] of invalid entries (for logging)
        """
        df = pd.read_csv(self.csv_path)
        
        # Check for pmid column (case-insensitive)
        pmid_col = None
        for col in df.columns:
            if col.lower() == 'pmid':
                pmid_col = col
                break
        
        if pmid_col is None:
            raise ValueError(f"No 'pmid' column found in {self.csv_path}")
        
        # Extract PMIDs
        pmids_raw = df[pmid_col].dropna().astype(str).tolist()
        pmids_valid = []
        pmids_invalid = []
        
        for pmid in pmids_raw:
            pmid = pmid.strip()
            if self.PMID_PATTERN.match(pmid):
                pmids_valid.append(pmid)
            else:
                pmids_invalid.append(pmid)
                logger.warning(f"Invalid PMID format: {pmid}")
        
        # Check for DOI column (optional)
        doi_col = None
        for col in df.columns:
            if col.lower() == 'doi':
                doi_col = col
                break
        
        dois = []
        if doi_col:
            dois_raw = df[doi_col].dropna().astype(str).tolist()
            for doi in dois_raw:
                doi = doi.strip()
                if self.DOI_PATTERN.match(doi):
                    dois.append(doi)
        
        result = {
            'pmids': pmids_valid,
            'dois': dois if dois else None,
            'count': len(pmids_valid),
            'invalid_pmids': pmids_invalid if pmids_invalid else None
        }
        
        logger.info(f"Extracted {len(pmids_valid)} valid PMIDs from {self.csv_path.name}")
        if pmids_invalid:
            logger.warning(f"Found {len(pmids_invalid)} invalid PMIDs")
        if dois:
            logger.info(f"Found {len(dois)} DOIs")
        
        return result
    
    @staticmethod
    def validate_pmid(pmid: str) -> bool:
        """
        Validate PMID format.
        
        Args:
            pmid: PMID string to validate
        
        Returns:
            True if valid, False otherwise
        """
        return bool(GoldStandardExtractor.PMID_PATTERN.match(pmid.strip()))
    
    @staticmethod
    def validate_doi(doi: str) -> bool:
        """
        Validate DOI format.
        
        Args:
            doi: DOI string to validate
        
        Returns:
            True if valid, False otherwise
        """
        return bool(GoldStandardExtractor.DOI_PATTERN.match(doi.strip()))


def get_gold_standard_csv(study_id: str, base_dir: Path = None) -> Optional[Path]:
    """
    Find gold standard CSV for a study.
    
    Args:
        study_id: Study identifier (e.g., 'Godos_2024')
        base_dir: Base directory (defaults to current working directory)
    
    Returns:
        Path to CSV file, or None if not found
    """
    if base_dir is None:
        base_dir = Path.cwd()
    
    # Candidate study directories: exact name, then hyphen→underscore variant
    alt_id = study_id.replace('-', '_')
    candidate_dirs = [base_dir / 'studies' / study_id]
    if alt_id != study_id:
        candidate_dirs.append(base_dir / 'studies' / alt_id)

    # Try different naming conventions (using original study_id for filename)
    patterns = [
        f'gold_pmids_{study_id}.csv',
        f'gold_pmids_{study_id.lower()}.csv',
        f'gold_pmids_{alt_id}.csv',
        'gold_pmids.csv',
        f'Gold_list_{study_id}.csv'
    ]

    for study_dir in candidate_dirs:
        for pattern in patterns:
            csv_path = study_dir / pattern
            if csv_path.exists():
                logger.info(f"Found gold standard: {csv_path}")
                return csv_path

    # Also check in base directory for legacy files
    for pattern in patterns:
        csv_path = base_dir / pattern
        if csv_path.exists():
            logger.info(f"Found gold standard: {csv_path}")
            return csv_path

    logger.warning(f"No gold standard CSV found for {study_id}")
    return None


# Example usage and testing
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("\n=== Testing Gold Standard Extractor ===")
    
    # Test on actual studies
    for study_id in ['Godos_2024', 'ai_2022', 'sleep_apnea']:
        print(f"\n--- {study_id} ---")
        csv_path = get_gold_standard_csv(study_id)
        if csv_path:
            extractor = GoldStandardExtractor(csv_path)
            gold_standard = extractor.extract()
            print(f"  PMIDs: {gold_standard['count']}")
            print(f"  First 5 PMIDs: {gold_standard['pmids'][:5]}")
            if gold_standard['dois']:
                print(f"  DOIs: {len(gold_standard['dois'])}")
            if gold_standard['invalid_pmids']:
                print(f"  Invalid: {gold_standard['invalid_pmids']}")
        else:
            print(f"  ✗ Not found")
