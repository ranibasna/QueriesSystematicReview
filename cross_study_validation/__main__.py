#!/usr/bin/env python3
"""
Cross-Study Validation Framework - Main CLI

Unified command-line interface for cross-study validation analysis.

Usage:
    # Collect data from all studies
    python -m cross_study_validation collect --all
    
    # Collect data from specific study
    python -m cross_study_validation collect --study Godos_2024
    
    # Generate analysis report
    python -m cross_study_validation analyze
    
    # Generate report (alias for analyze)
    python -m cross_study_validation report
    
    # Complete workflow: collect + analyze
    python -m cross_study_validation run
"""

import sys
import argparse
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_collect(args):
    """Collect study results."""
    from .collectors import StudyDataCollector
    
    base_dir = Path(args.base_dir).resolve()
    collector = StudyDataCollector(base_dir)
    
    if args.all:
        logger.info("Collecting all studies...")
        studies_data = collector.collect_all_studies()
        if not studies_data:
            logger.error("No studies collected")
            return 1
        
        logger.info(f"\n✓ Collected {len(studies_data)} studies successfully")
        
        # Save
        output_dir = base_dir / 'cross_study_validation' / 'data'
        collector.save_all_studies(studies_data, output_dir)
        
    elif args.study:
        logger.info(f"Collecting study: {args.study}")
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
        logger.error("Must specify either --all or --study")
        return 1
    
    logger.info("\n✅ Collection complete!")
    return 0


def cmd_analyze(args):
    """Generate analysis report."""
    from .reporting import MarkdownReporter
    from .collectors import load_studies_data
    from datetime import datetime
    
    base_dir = Path(args.base_dir).resolve()
    data_dir = base_dir / 'cross_study_validation' / 'data'
    
    # Load data
    logger.info(f"Loading studies from {data_dir}")
    studies = load_studies_data(data_dir)
    
    if not studies:
        logger.error(f"No studies found in {data_dir}")
        logger.error("Run 'collect' command first")
        return 1
    
    logger.info(f"Loaded {len(studies)} studies")
    
    # Generate report
    reporter = MarkdownReporter(studies)
    
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        output_path = base_dir / 'cross_study_validation' / 'reports' / f'report_{timestamp}.md'
    
    reporter.save_report(output_path)
    
    logger.info(f"\n✅ Report generated: {output_path}")
    logger.info(f"📊 Analyzed {len(studies)} studies")
    return 0


def cmd_run(args):
    """Run complete workflow: collect + analyze."""
    logger.info("="*60)
    logger.info("Running complete cross-study validation workflow")
    logger.info("="*60)
    
    # Step 1: Collect
    logger.info("\nStep 1: Collecting study data...")
    args.all = True
    result = cmd_collect(args)
    if result != 0:
        return result
    
    # Step 2: Analyze
    logger.info("\nStep 2: Generating analysis report...")
    result = cmd_analyze(args)
    if result != 0:
        return result
    
    logger.info("\n" + "="*60)
    logger.info("✅ Complete workflow finished successfully!")
    logger.info("="*60)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Cross-Study Validation Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Complete workflow
  python -m cross_study_validation run
  
  # Collect all studies
  python -m cross_study_validation collect --all
  
  # Collect specific study
  python -m cross_study_validation collect --study Godos_2024
  
  # Generate report
  python -m cross_study_validation analyze
  
  # Custom output location
  python -m cross_study_validation analyze --output my_report.md
        """
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
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Collect command
    collect_parser = subparsers.add_parser('collect', help='Collect study results')
    collect_parser.add_argument('--study', type=str, help='Study ID to collect')
    collect_parser.add_argument('--all', action='store_true', help='Collect all studies')
    collect_parser.add_argument('--output', type=str, help='Output JSON file path')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Generate analysis report')
    analyze_parser.add_argument('--output', type=str, help='Output markdown file path')
    
    # Report command (alias for analyze)
    report_parser = subparsers.add_parser('report', help='Generate analysis report (alias for analyze)')
    report_parser.add_argument('--output', type=str, help='Output markdown file path')
    
    # Run command (collect + analyze)
    run_parser = subparsers.add_parser('run', help='Run complete workflow (collect + analyze)')
    run_parser.add_argument('--output', type=str, help='Output markdown file path')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == 'collect':
        return cmd_collect(args)
    elif args.command in ['analyze', 'report']:
        return cmd_analyze(args)
    elif args.command == 'run':
        return cmd_run(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
