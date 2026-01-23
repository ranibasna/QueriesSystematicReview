"""
Data collectors for cross-study validation.
"""

from .collect_study_results import StudyDataCollector
from .parsers import (
    AggregatesCSVParser,
    BenchmarkCSVParser,
    GoldStandardExtractor,
    MetadataCollector,
    get_aggregates_csv,
    get_benchmark_csv,
    get_gold_standard_csv,
    find_latest_csv
)

def collect_study_results(study_id: str = None, all_studies: bool = False, base_dir=None):
    """
    Convenience function to collect study results.
    
    Args:
        study_id: Study identifier (e.g., 'Godos_2024')
        all_studies: Collect all studies
        base_dir: Base directory (defaults to cwd)
    
    Returns:
        Dictionary of study data
    """
    from pathlib import Path
    
    base_dir = Path(base_dir) if base_dir else Path.cwd()
    collector = StudyDataCollector(base_dir)
    
    if all_studies:
        return collector.collect_all_studies()
    elif study_id:
        return collector.collect_study(study_id)
    else:
        raise ValueError("Must specify either study_id or all_studies=True")

def load_studies_data(data_dir=None):
    """
    Load all study JSON files from data directory.
    
    Args:
        data_dir: Path to data directory (defaults to cross_study_validation/data/)
    
    Returns:
        Dictionary mapping study_id -> study data
    """
    import json
    from pathlib import Path
    
    if data_dir is None:
        data_dir = Path.cwd() / 'cross_study_validation' / 'data'
    else:
        data_dir = Path(data_dir)
    
    # Try loading combined file first
    combined_file = data_dir / 'all_studies.json'
    if combined_file.exists():
        with open(combined_file, 'r') as f:
            data = json.load(f)
        return data.get('studies', {})
    
    # Otherwise load individual files
    studies = {}
    for json_file in data_dir.glob('*.json'):
        if json_file.name == 'all_studies.json':
            continue
        with open(json_file, 'r') as f:
            study_data = json.load(f)
            study_id = study_data['study_id']
            studies[study_id] = study_data
    
    return studies

__all__ = [
    'StudyDataCollector',
    'AggregatesCSVParser',
    'BenchmarkCSVParser',
    'GoldStandardExtractor',
    'MetadataCollector',
    'get_aggregates_csv',
    'get_benchmark_csv',
    'get_gold_standard_csv',
    'find_latest_csv',
    'collect_study_results',
    'load_studies_data',
]
