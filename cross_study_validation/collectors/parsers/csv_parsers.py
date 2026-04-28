"""
CSV parsing utilities for cross-study validation framework.

This module provides parsers to extract data from:
- aggregates_eval/*/sets_summary_*.csv (aggregation strategy performance)
- benchmark_outputs/*/summary_*.csv (individual query performance)
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def find_latest_matching_csv(study_dir: Path, predicate) -> Optional[Path]:
    """Return the most recent CSV in a directory that satisfies a filename predicate."""
    study_dir = Path(study_dir)
    if not study_dir.exists():
        logger.warning(f"Study directory not found: {study_dir}")
        return None

    csv_files = [path for path in study_dir.glob('*.csv') if predicate(path.name)]
    if not csv_files:
        logger.warning(f"No matching CSV files found in {study_dir}")
        return None

    latest = max(csv_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Found latest CSV: {latest.name} (modified: {datetime.fromtimestamp(latest.stat().st_mtime)})")
    return latest


class AggregatesCSVParser:
    """Parser for aggregates_eval CSV files."""
    
    def __init__(self, csv_path: Path):
        """
        Initialize parser with path to aggregates CSV.
        
        Args:
            csv_path: Path to sets_summary_*.csv file
        """
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    def parse(self) -> List[Dict]:
        """
        Parse aggregates CSV and return list of strategy performance dicts.
        
        Returns:
            List of dicts with keys: name, recall, precision, f1, jaccard,
            overlap_coeff, retrieved_count, true_positives, false_negatives
        """
        df = pd.read_csv(self.csv_path)
        
        # Expected columns: name, path, TP, Retrieved, Gold, Precision, Recall, F1, Jaccard, OverlapCoeff
        required_cols = ['name', 'TP', 'Retrieved', 'Gold', 'Precision', 'Recall', 'F1']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        strategies = []
        for _, row in df.iterrows():
            strategy = {
                'name': row['name'],
                'recall': float(row['Recall']),
                'precision': float(row['Precision']),
                'f1': float(row['F1']),
                'jaccard': float(row.get('Jaccard', 0.0)),
                'overlap_coeff': float(row.get('OverlapCoeff', 0.0)),
                'retrieved_count': int(row['Retrieved']),
                'true_positives': int(row['TP']),
                'false_negatives': int(row['Gold']) - int(row['TP'])
            }
            strategies.append(strategy)
        
        logger.info(f"Parsed {len(strategies)} strategies from {self.csv_path.name}")
        return strategies


class BenchmarkCSVParser:
    """Parser for benchmark_outputs CSV files."""
    
    def __init__(self, csv_path: Path):
        """
        Initialize parser with path to benchmark CSV.
        
        Args:
            csv_path: Path to summary_*.csv file
        """
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

    @staticmethod
    def _query_sort_key(path: Path):
        """Sort query directories numerically when names follow query_01, query_02, ..."""
        suffix = path.name.split('_')[-1]
        return int(suffix) if suffix.isdigit() else suffix

    @staticmethod
    def _row_to_query(row) -> Dict:
        """Convert a benchmark summary row into standardized query metrics."""
        return {
            'query_text': str(row['query']),
            'results_count': int(row['results_count']),
            'true_positives': int(row['TP']),
            'recall': float(row['recall']),
            'nnr_proxy': float(row.get('NNR_proxy', 0.0))
        }

    def _parse_query_directories(self, study_dir: Path) -> List[Dict]:
        """Parse one latest combined summary per query from query_XX subdirectories."""
        query_dirs = sorted(
            [path for path in study_dir.glob('query_*') if path.is_dir()],
            key=self._query_sort_key,
        )
        if not query_dirs:
            return []

        queries = []
        for query_dir in query_dirs:
            summary_csv = find_latest_matching_csv(
                query_dir,
                lambda name: name.startswith('summary_') and not name.startswith('summary_per_database_'),
            )
            if not summary_csv:
                logger.warning(f"No summary CSV found in {query_dir}")
                continue

            df = pd.read_csv(summary_csv)
            if df.empty:
                logger.warning(f"Summary CSV is empty: {summary_csv}")
                continue

            queries.append(self._row_to_query(df.iloc[0]))

        if queries:
            logger.info(
                f"Parsed {len(queries)} queries from per-query benchmark summaries in {study_dir.name}"
            )
        return queries
    
    def parse(self) -> List[Dict]:
        """
        Parse benchmark CSV and return list of query performance dicts.
        
        Returns:
            List of dicts with keys: query_text, results_count, true_positives,
            recall, nnr_proxy
        """
        study_dir = self.csv_path if self.csv_path.is_dir() else self.csv_path.parent
        query_dir_results = self._parse_query_directories(study_dir)
        if query_dir_results:
            return query_dir_results

        df = pd.read_csv(self.csv_path)
        
        # Expected columns: query, results_count, TP, gold_size, recall, NNR_proxy
        required_cols = ['query', 'results_count', 'TP', 'recall']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        if 'database' in df.columns:
            df = df[df['database'].astype(str).str.upper() == 'COMBINED'].copy()
            if 'query_num' in df.columns:
                df = df.sort_values('query_num')
        
        queries = []
        for _, row in df.iterrows():
            queries.append(self._row_to_query(row))
        
        logger.info(f"Parsed {len(queries)} queries from {self.csv_path.name}")
        return queries


def find_latest_csv(study_dir: Path, csv_pattern: str) -> Optional[Path]:
    """
    Find the most recent CSV file matching pattern in study directory.
    
    Args:
        study_dir: Directory to search (e.g., aggregates_eval/Godos_2024/)
        csv_pattern: Glob pattern (e.g., 'sets_summary_*.csv')
    
    Returns:
        Path to most recent CSV file, or None if no matches
    """
    study_dir = Path(study_dir)
    if not study_dir.exists():
        logger.warning(f"Study directory not found: {study_dir}")
        return None
    
    csv_files = list(study_dir.glob(csv_pattern))
    if not csv_files:
        logger.warning(f"No CSV files matching '{csv_pattern}' in {study_dir}")
        return None
    
    # Sort by modification time, return most recent
    latest = max(csv_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Found latest CSV: {latest.name} (modified: {datetime.fromtimestamp(latest.stat().st_mtime)})")
    return latest


def get_aggregates_csv(study_id: str, base_dir: Path = None) -> Optional[Path]:
    """
    Get the latest aggregates_eval CSV for a study.
    
    Args:
        study_id: Study identifier (e.g., 'Godos_2024')
        base_dir: Base directory (defaults to current working directory)
    
    Returns:
        Path to CSV file, or None if not found
    """
    if base_dir is None:
        base_dir = Path.cwd()
    
    study_dir = base_dir / 'aggregates_eval' / study_id
    return find_latest_csv(study_dir, 'sets_summary_*.csv')


def get_benchmark_csv(study_id: str, base_dir: Path = None) -> Optional[Path]:
    """
    Get the latest benchmark_outputs CSV for a study.
    
    Args:
        study_id: Study identifier (e.g., 'Godos_2024')
        base_dir: Base directory (defaults to current working directory)
    
    Returns:
        Path to CSV file, or None if not found
    """
    if base_dir is None:
        base_dir = Path.cwd()
    
    study_dir = base_dir / 'benchmark_outputs' / study_id
    return find_latest_matching_csv(
        study_dir,
        lambda name: name.startswith('summary_') and not name.startswith('summary_per_database_'),
    )


# Example usage and testing
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Test aggregates parser
    print("\n=== Testing Aggregates Parser ===")
    agg_csv = get_aggregates_csv('Godos_2024')
    if agg_csv:
        parser = AggregatesCSVParser(agg_csv)
        strategies = parser.parse()
        print(f"\nFound {len(strategies)} strategies:")
        for s in strategies:
            print(f"  {s['name']}: Recall={s['recall']:.2%}, Precision={s['precision']:.4f}, Retrieved={s['retrieved_count']}")
    
    # Test benchmark parser
    print("\n=== Testing Benchmark Parser ===")
    bench_csv = get_benchmark_csv('Godos_2024')
    if bench_csv:
        parser = BenchmarkCSVParser(bench_csv)
        queries = parser.parse()
        print(f"\nFound {len(queries)} queries:")
        for i, q in enumerate(queries[:3], 1):  # Show first 3
            print(f"  Query {i}: Retrieved={q['results_count']}, TP={q['true_positives']}, Recall={q['recall']:.2%}")
