"""
Descriptive statistics analysis for cross-study validation.

This module calculates summary statistics across multiple studies to evaluate
aggregation strategy performance.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import statistics
import logging

logger = logging.getLogger(__name__)


class DescriptiveStats:
    """Calculate descriptive statistics across studies."""
    
    def __init__(self, studies_data: Dict[str, Dict]):
        """
        Initialize with studies data.
        
        Args:
            studies_data: Dictionary mapping study_id -> study data
        """
        self.studies_data = studies_data
        self.num_studies = len(studies_data)
    
    def calculate_strategy_stats(self) -> Dict[str, Dict]:
        """
        Calculate statistics for each aggregation strategy across all studies.
        
        Returns:
            Dict mapping strategy_name -> statistics dict with:
                - mean_recall, std_recall, min_recall, max_recall
                - mean_precision, std_precision, min_precision, max_precision
                - mean_f1, std_f1, min_f1, max_f1
                - mean_retrieved, std_retrieved, min_retrieved, max_retrieved
                - studies_with_perfect_recall: List[study_id]
                - studies: List of individual study performances
        """
        # Collect data by strategy
        strategy_data = {}
        
        for study_id, study in self.studies_data.items():
            for strat in study['aggregation_strategies']:
                name = strat['name']
                if name not in strategy_data:
                    strategy_data[name] = {
                        'recall': [],
                        'precision': [],
                        'f1': [],
                        'retrieved': [],
                        'studies': []
                    }
                
                strategy_data[name]['recall'].append(strat['recall'])
                strategy_data[name]['precision'].append(strat['precision'])
                strategy_data[name]['f1'].append(strat['f1'])
                strategy_data[name]['retrieved'].append(strat['retrieved_count'])
                strategy_data[name]['studies'].append({
                    'study_id': study_id,
                    'recall': strat['recall'],
                    'precision': strat['precision'],
                    'f1': strat['f1'],
                    'retrieved_count': strat['retrieved_count'],
                    'gold_size': study['metadata']['gold_size']
                })
        
        # Calculate statistics
        stats = {}
        for name, data in strategy_data.items():
            # Find studies with perfect recall
            perfect_recall = [s['study_id'] for s in data['studies'] if s['recall'] >= 0.999]
            
            stats[name] = {
                # Recall
                'mean_recall': statistics.mean(data['recall']),
                'std_recall': statistics.stdev(data['recall']) if len(data['recall']) > 1 else 0.0,
                'min_recall': min(data['recall']),
                'max_recall': max(data['recall']),
                
                # Precision
                'mean_precision': statistics.mean(data['precision']),
                'std_precision': statistics.stdev(data['precision']) if len(data['precision']) > 1 else 0.0,
                'min_precision': min(data['precision']),
                'max_precision': max(data['precision']),
                
                # F1
                'mean_f1': statistics.mean(data['f1']),
                'std_f1': statistics.stdev(data['f1']) if len(data['f1']) > 1 else 0.0,
                'min_f1': min(data['f1']),
                'max_f1': max(data['f1']),
                
                # Retrieved count
                'mean_retrieved': statistics.mean(data['retrieved']),
                'std_retrieved': statistics.stdev(data['retrieved']) if len(data['retrieved']) > 1 else 0.0,
                'min_retrieved': min(data['retrieved']),
                'max_retrieved': max(data['retrieved']),
                
                # Meta info
                'num_studies': len(data['studies']),
                'studies_with_perfect_recall': perfect_recall,
                'num_perfect_recall': len(perfect_recall),
                
                # Individual study data for drill-down
                'studies': data['studies']
            }
        
        logger.info(f"Calculated stats for {len(stats)} strategies across {self.num_studies} studies")
        return stats
    
    def rank_strategies(self, stats: Dict[str, Dict], 
                       criterion: str = 'recall', 
                       minimize_retrieved: bool = True) -> List[Dict]:
        """
        Rank strategies by a performance criterion.
        
        Args:
            stats: Statistics dict from calculate_strategy_stats()
            criterion: 'recall', 'precision', 'f1', or 'retrieved'
            minimize_retrieved: If True, prefer strategies with fewer retrieved articles
        
        Returns:
            List of dicts with keys: rank, name, mean_<criterion>, std_<criterion>
        """
        if criterion not in ['recall', 'precision', 'f1', 'retrieved']:
            raise ValueError(f"Invalid criterion: {criterion}")
        
        # Sort strategies
        sorted_strategies = []
        for name, data in stats.items():
            mean_key = f'mean_{criterion}'
            std_key = f'std_{criterion}'
            
            sorted_strategies.append({
                'name': name,
                'mean': data[mean_key],
                'std': data[std_key],
                'min': data[f'min_{criterion}'],
                'max': data[f'max_{criterion}'],
                'mean_retrieved': data['mean_retrieved'],
                'num_perfect_recall': data['num_perfect_recall']
            })
        
        # Sort descending for recall/precision/f1, ascending for retrieved
        reverse = (criterion != 'retrieved')
        sorted_strategies.sort(key=lambda x: x['mean'], reverse=reverse)
        
        # Add ranks
        for i, strat in enumerate(sorted_strategies, 1):
            strat['rank'] = i
        
        return sorted_strategies
    
    def get_best_strategy(self, stats: Dict[str, Dict],
                         require_perfect_recall: bool = True,
                         minimize_retrieved: bool = True) -> Dict:
        """
        Determine the best overall strategy using multi-criteria evaluation.
        
        Args:
            stats: Statistics dict from calculate_strategy_stats()
            require_perfect_recall: If True, only consider strategies with 100% recall in all studies
            minimize_retrieved: Prefer strategies with fewer retrieved articles
        
        Returns:
            Dict with keys: name, justification, stats
        """
        candidates = {}
        
        for name, data in stats.items():
            # Filter by perfect recall if required
            if require_perfect_recall and data['num_perfect_recall'] < data['num_studies']:
                continue
            
            candidates[name] = data
        
        if not candidates:
            logger.warning("No strategies have perfect recall in all studies, relaxing constraint")
            # Fall back to strategies with highest mean recall
            candidates = stats
        
        # Among candidates, select the one with minimum retrieved articles
        if minimize_retrieved:
            best_name = min(candidates.keys(), key=lambda name: candidates[name]['mean_retrieved'])
        else:
            # Select by highest F1 score
            best_name = max(candidates.keys(), key=lambda name: candidates[name]['mean_f1'])
        
        best_stats = candidates[best_name]
        
        # Build justification
        if best_stats['num_perfect_recall'] == best_stats['num_studies']:
            justification = (
                f"{best_name} achieves 100% recall in all {self.num_studies} studies "
                f"while retrieving an average of {best_stats['mean_retrieved']:.0f} articles "
                f"(min: {best_stats['min_retrieved']}, max: {best_stats['max_retrieved']})"
            )
        else:
            justification = (
                f"{best_name} has the best performance with mean recall {best_stats['mean_recall']:.2%} "
                f"and mean F1 {best_stats['mean_f1']:.4f}"
            )
        
        return {
            'name': best_name,
            'justification': justification,
            'stats': best_stats
        }
    
    def compare_study_characteristics(self) -> Dict:
        """
        Compare study characteristics across all studies.
        
        Returns:
            Dict with summary of study characteristics:
                - domains: List of domains
                - databases: Set of all databases used
                - gold_sizes: List of gold standard sizes
                - date_ranges: List of date ranges
        """
        domains = []
        all_databases = set()
        gold_sizes = []
        date_ranges = []
        
        for study_id, study in self.studies_data.items():
            metadata = study['metadata']
            domains.append(metadata['domain'])
            all_databases.update(metadata['databases'])
            gold_sizes.append(metadata['gold_size'])
            if metadata.get('date_range'):
                date_ranges.append(metadata['date_range'])
        
        return {
            'num_studies': self.num_studies,
            'domains': domains,
            'unique_domains': list(set(domains)),
            'databases_used': sorted(all_databases),
            'gold_sizes': {
                'values': gold_sizes,
                'mean': statistics.mean(gold_sizes),
                'min': min(gold_sizes),
                'max': max(gold_sizes),
                'total': sum(gold_sizes)
            },
            'date_ranges': date_ranges
        }


def load_studies_data(data_dir: Path) -> Dict[str, Dict]:
    """
    Load all study JSON files from data directory.
    
    Args:
        data_dir: Path to cross_study_validation/data/
    
    Returns:
        Dictionary mapping study_id -> study data
    """
    data_dir = Path(data_dir)
    
    # Try loading combined file first
    combined_file = data_dir / 'all_studies.json'
    if combined_file.exists():
        logger.info(f"Loading combined studies file: {combined_file}")
        with open(combined_file, 'r') as f:
            data = json.load(f)
        return data.get('studies', {})
    
    # Otherwise load individual files
    logger.info(f"Loading individual study files from {data_dir}")
    studies = {}
    for json_file in data_dir.glob('*.json'):
        if json_file.name == 'all_studies.json':
            continue
        
        with open(json_file, 'r') as f:
            study_data = json.load(f)
            study_id = study_data['study_id']
            studies[study_id] = study_data
    
    logger.info(f"Loaded {len(studies)} studies")
    return studies


# Example usage and testing
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("\n=== Cross-Study Descriptive Statistics ===\n")
    
    # Load data
    data_dir = Path('cross_study_validation/data')
    studies = load_studies_data(data_dir)
    
    if not studies:
        print("No studies found. Run collect_study_results.py first.")
        exit(1)
    
    # Initialize stats calculator
    stats_calc = DescriptiveStats(studies)
    
    # 1. Study characteristics
    print("--- Study Characteristics ---")
    characteristics = stats_calc.compare_study_characteristics()
    print(f"Number of studies: {characteristics['num_studies']}")
    print(f"Domains: {', '.join(characteristics['unique_domains'])}")
    print(f"Databases: {', '.join(characteristics['databases_used'])}")
    print(f"Gold standard sizes: {characteristics['gold_sizes']['min']}-{characteristics['gold_sizes']['max']} "
          f"(mean: {characteristics['gold_sizes']['mean']:.1f}, total: {characteristics['gold_sizes']['total']})")
    
    # 2. Strategy statistics
    print("\n--- Strategy Performance Statistics ---")
    strategy_stats = stats_calc.calculate_strategy_stats()
    
    for name, stats in sorted(strategy_stats.items()):
        print(f"\n{name}:")
        print(f"  Recall: {stats['mean_recall']:.2%} ± {stats['std_recall']:.2%} "
              f"(range: {stats['min_recall']:.2%} - {stats['max_recall']:.2%})")
        print(f"  Precision: {stats['mean_precision']:.4f} ± {stats['std_precision']:.4f}")
        print(f"  Retrieved: {stats['mean_retrieved']:.0f} ± {stats['std_retrieved']:.0f} "
              f"(range: {stats['min_retrieved']:.0f} - {stats['max_retrieved']:.0f})")
        print(f"  Perfect recall: {stats['num_perfect_recall']}/{stats['num_studies']} studies")
    
    # 3. Best strategy
    print("\n--- Best Strategy Recommendation ---")
    best = stats_calc.get_best_strategy(strategy_stats)
    print(f"Recommended: {best['name']}")
    print(f"Justification: {best['justification']}")
    
    # 4. Rankings
    print("\n--- Strategy Rankings by Recall ---")
    rankings = stats_calc.rank_strategies(strategy_stats, criterion='recall')
    for rank_info in rankings:
        print(f"  {rank_info['rank']}. {rank_info['name']}: {rank_info['mean']:.2%} "
              f"(retrieved: {rank_info['mean_retrieved']:.0f})")
