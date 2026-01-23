#!/usr/bin/env python3
"""
Collect and standardize study results for cross-study validation.

This script collects data from multiple sources:
- aggregates_eval/*/sets_summary_*.csv (strategy performance)
- benchmark_outputs/*/summary_*.csv (query performance)  
- studies/*/gold_pmids_*.csv (gold standard)
- studies/*/ directory structure (metadata)

Usage:
    python scripts/collect_study_results.py --study Godos_2024
    python scripts/collect_study_results.py --all-studies
    python scripts/collect_study_results.py --study ai_2022 --output custom_path.json
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import jsonschema

# Import parsers from same package
from .parsers import (
    AggregatesCSVParser,
    BenchmarkCSVParser,
    GoldStandardExtractor,
    MetadataCollector,
    get_aggregates_csv,
    get_benchmark_csv,
    get_gold_standard_csv
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StudyDataCollector:
    """Main class for collecting and standardizing study data."""
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize collector.
        
        Args:
            base_dir: Base directory (defaults to current working directory)
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.schema_path = self.base_dir / 'cross_study_validation' / 'schemas' / 'study_result_schema.json'
        
        # Load JSON schema for validation
        if self.schema_path.exists():
            with open(self.schema_path, 'r') as f:
                self.schema = json.load(f)
        else:
            logger.warning(f"Schema file not found: {self.schema_path}")
            self.schema = None
    
    def collect_study(self, study_id: str) -> Optional[Dict]:
        """
        Collect all data for a single study.
        
        Args:
            study_id: Study identifier (e.g., 'Godos_2024')
        
        Returns:
            Dictionary conforming to study_result_schema, or None if collection fails
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Collecting data for: {study_id}")
        logger.info(f"{'='*60}")
        
        try:
            # 1. Get file paths
            agg_csv = get_aggregates_csv(study_id, self.base_dir)
            bench_csv = get_benchmark_csv(study_id, self.base_dir)
            gold_csv = get_gold_standard_csv(study_id, self.base_dir)
            study_dir = self.base_dir / 'studies' / study_id
            
            if not agg_csv:
                logger.error(f"  ✗ Aggregates CSV not found for {study_id}")
                return None
            if not gold_csv:
                logger.error(f"  ✗ Gold standard CSV not found for {study_id}")
                return None
            if not study_dir.exists():
                logger.error(f"  ✗ Study directory not found: {study_dir}")
                return None
            
            # 2. Parse aggregation strategies
            logger.info(f"\n  📊 Parsing aggregation strategies...")
            agg_parser = AggregatesCSVParser(agg_csv)
            strategies = agg_parser.parse()
            logger.info(f"  ✓ Found {len(strategies)} strategies")
            
            # 3. Parse query performance (optional)
            query_performance = None
            if bench_csv:
                logger.info(f"\n  🔍 Parsing query performance...")
                bench_parser = BenchmarkCSVParser(bench_csv)
                query_performance = bench_parser.parse()
                logger.info(f"  ✓ Found {len(query_performance)} queries")
            else:
                logger.warning(f"  ⚠ Benchmark CSV not found (optional)")
            
            # 4. Extract gold standard
            logger.info(f"\n  🏆 Extracting gold standard...")
            gold_extractor = GoldStandardExtractor(gold_csv)
            gold_standard = gold_extractor.extract()
            logger.info(f"  ✓ Found {gold_standard['count']} PMIDs")
            
            # 5. Collect metadata
            logger.info(f"\n  📋 Collecting metadata...")
            metadata_collector = MetadataCollector(study_dir)
            metadata = metadata_collector.collect()
            metadata['gold_size'] = gold_standard['count']
            
            # 6. Assemble result
            result = {
                'study_id': study_id,
                'schema_version': '1.0',
                'collection_timestamp': datetime.utcnow().isoformat() + 'Z',
                'metadata': metadata,
                'gold_standard': {
                    'pmids': gold_standard['pmids'],
                    'count': gold_standard['count']
                },
                'aggregation_strategies': strategies,
                'source_files': {
                    'aggregates_csv': str(agg_csv.relative_to(self.base_dir)),
                    'gold_standard_csv': str(gold_csv.relative_to(self.base_dir))
                }
            }
            
            # Add DOIs if available
            if gold_standard.get('dois'):
                result['gold_standard']['dois'] = gold_standard['dois']
            
            # Add query performance if available
            if query_performance:
                result['query_performance'] = query_performance
                result['source_files']['benchmark_csv'] = str(bench_csv.relative_to(self.base_dir))
            
            # 7. Validate against schema
            if self.schema:
                logger.info(f"\n  ✅ Validating against schema...")
                try:
                    jsonschema.validate(instance=result, schema=self.schema)
                    logger.info(f"  ✓ Validation passed")
                except jsonschema.ValidationError as e:
                    logger.error(f"  ✗ Validation failed: {e.message}")
                    logger.error(f"    Path: {' -> '.join(str(p) for p in e.path)}")
                    return None
            
            logger.info(f"\n{'='*60}")
            logger.info(f"✓ Successfully collected data for {study_id}")
            logger.info(f"{'='*60}\n")
            
            return result
            
        except Exception as e:
            logger.error(f"\n✗ Error collecting data for {study_id}: {e}")
            logger.exception(e)
            return None
    
    def collect_all_studies(self) -> Dict[str, Dict]:
        """
        Collect data for all studies found in aggregates_eval/.
        
        Returns:
            Dictionary mapping study_id -> study data
        """
        aggregates_dir = self.base_dir / 'aggregates_eval'
        if not aggregates_dir.exists():
            logger.error(f"Aggregates directory not found: {aggregates_dir}")
            return {}
        
        # Find all study directories
        study_dirs = [d for d in aggregates_dir.iterdir() if d.is_dir()]
        study_ids = [d.name for d in study_dirs]
        
        logger.info(f"Found {len(study_ids)} studies: {', '.join(study_ids)}")
        
        results = {}
        for study_id in study_ids:
            result = self.collect_study(study_id)
            if result:
                results[study_id] = result
        
        return results
    
    def save_study(self, study_data: Dict, output_path: Path):
        """
        Save study data to JSON file.
        
        Args:
            study_data: Study data dictionary
            output_path: Path to output JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(study_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Saved to: {output_path}")
    
    def save_all_studies(self, studies_data: Dict[str, Dict], output_dir: Path):
        """
        Save all studies data (individual files + combined file).
        
        Args:
            studies_data: Dictionary mapping study_id -> study data
            output_dir: Directory to save JSON files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save individual study files
        for study_id, data in studies_data.items():
            output_path = output_dir / f"{study_id}.json"
            self.save_study(data, output_path)
        
        # Save combined file
        combined_data = {
            'collection_timestamp': datetime.utcnow().isoformat() + 'Z',
            'num_studies': len(studies_data),
            'studies': studies_data
        }
        combined_path = output_dir / 'all_studies.json'
        with open(combined_path, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Saved combined file: {combined_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Collect and standardize study results for cross-study validation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect single study
  python scripts/collect_study_results.py --study Godos_2024
  
  # Collect all studies
  python scripts/collect_study_results.py --all-studies
  
  # Custom output path
  python scripts/collect_study_results.py --study ai_2022 --output my_data/ai_2022.json
  
  # Specify base directory
  python scripts/collect_study_results.py --all-studies --base-dir /path/to/project
        """
    )
    
    parser.add_argument(
        '--study',
        type=str,
        help='Study ID to collect (e.g., Godos_2024, ai_2022, sleep_apnea)'
    )
    parser.add_argument(
        '--all-studies',
        action='store_true',
        help='Collect all studies found in aggregates_eval/'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output JSON file path (default: cross_study_validation/data/<study_id>.json)'
    )
    parser.add_argument(
        '--base-dir',
        type=str,
        default='.',
        help='Base directory (default: current directory)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate arguments
    if not args.study and not args.all_studies:
        parser.error("Must specify either --study or --all-studies")
    
    if args.study and args.all_studies:
        parser.error("Cannot specify both --study and --all-studies")
    
    # Initialize collector
    base_dir = Path(args.base_dir).resolve()
    collector = StudyDataCollector(base_dir)
    
    # Collect data
    if args.study:
        # Single study
        study_data = collector.collect_study(args.study)
        if not study_data:
            logger.error("Failed to collect study data")
            return 1
        
        # Save
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = base_dir / 'cross_study_validation' / 'data' / f"{args.study}.json"
        
        collector.save_study(study_data, output_path)
        
    else:
        # All studies
        studies_data = collector.collect_all_studies()
        if not studies_data:
            logger.error("No studies collected")
            return 1
        
        logger.info(f"\n✓ Collected {len(studies_data)} studies successfully")
        
        # Save
        if args.output:
            output_dir = Path(args.output)
        else:
            output_dir = base_dir / 'cross_study_validation' / 'data'
        
        collector.save_all_studies(studies_data, output_dir)
    
    logger.info("\n✅ Collection complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
