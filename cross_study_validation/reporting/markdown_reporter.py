"""
Markdown report generator for cross-study validation results.

This module generates comprehensive markdown reports summarizing cross-study
analysis findings.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging
import sys

# Add analysis directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'analysis'))
from descriptive_stats import DescriptiveStats, load_studies_data

logger = logging.getLogger(__name__)


class MarkdownReporter:
    """Generate markdown reports for cross-study validation."""
    
    def __init__(self, studies_data: Dict[str, Dict]):
        """
        Initialize reporter with studies data.
        
        Args:
            studies_data: Dictionary mapping study_id -> study data
        """
        self.studies_data = studies_data
        self.stats_calc = DescriptiveStats(studies_data)
    
    def generate_full_report(self) -> str:
        """
        Generate comprehensive markdown report.
        
        Returns:
            Markdown formatted string
        """
        lines = []
        
        # Header
        lines.extend(self._generate_header())
        lines.append("")
        
        # Executive Summary
        lines.extend(self._generate_executive_summary())
        lines.append("")
        
        # Study Characteristics
        lines.extend(self._generate_study_characteristics())
        lines.append("")
        
        # Strategy Performance Summary
        lines.extend(self._generate_strategy_performance())
        lines.append("")
        
        # Best Strategy Recommendation
        lines.extend(self._generate_recommendation())
        lines.append("")
        
        # Detailed Strategy Analysis
        lines.extend(self._generate_detailed_analysis())
        lines.append("")
        
        # Per-Study Breakdown
        lines.extend(self._generate_per_study_breakdown())
        lines.append("")
        
        # Conclusions
        lines.extend(self._generate_conclusions())
        
        return "\n".join(lines)
    
    def _generate_header(self) -> List[str]:
        """Generate report header."""
        return [
            "# Cross-Study Validation Report",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Number of Studies**: {len(self.studies_data)}  ",
            f"**Analysis Type**: Aggregation Strategy Performance Evaluation",
            "",
            "---"
        ]
    
    def _generate_executive_summary(self) -> List[str]:
        """Generate executive summary section."""
        lines = ["## Executive Summary", ""]
        
        # Calculate key findings
        strategy_stats = self.stats_calc.calculate_strategy_stats()
        best = self.stats_calc.get_best_strategy(strategy_stats, require_perfect_recall=False)
        characteristics = self.stats_calc.compare_study_characteristics()
        
        lines.append(f"This report analyzes the performance of **{len(strategy_stats)} aggregation strategies** "
                    f"across **{len(self.studies_data)} systematic review studies** covering "
                    f"**{characteristics['gold_sizes']['total']} total gold standard articles**.")
        lines.append("")
        
        # Count perfect recall strategies
        perfect_recall_strategies = [name for name, stats in strategy_stats.items() 
                                     if stats['num_perfect_recall'] == stats['num_studies']]
        
        if perfect_recall_strategies:
            lines.append(f"**Key Finding**: {len(perfect_recall_strategies)} strateg{'y' if len(perfect_recall_strategies)==1 else 'ies'} "
                        f"achieved 100% recall across all studies: `{'`, `'.join(perfect_recall_strategies)}`")
        else:
            lines.append(f"**Key Finding**: No single strategy achieved 100% recall across all {len(self.studies_data)} studies.")
        lines.append("")
        
        lines.append(f"**Recommended Strategy**: `{best['name']}`  ")
        lines.append(f"*{best['justification']}*")
        
        return lines
    
    def _generate_study_characteristics(self) -> List[str]:
        """Generate study characteristics section."""
        lines = ["## Study Characteristics", ""]
        
        characteristics = self.stats_calc.compare_study_characteristics()
        
        # Table of studies
        lines.append("| Study ID | Domain | Databases | Gold Standard Size | Queries |")
        lines.append("|----------|--------|-----------|-------------------|---------|")
        
        for study_id, study in sorted(self.studies_data.items()):
            metadata = study['metadata']
            databases = ", ".join(metadata['databases'])
            lines.append(f"| `{study_id}` | {metadata['domain']} | {databases} | "
                        f"{metadata['gold_size']} | {metadata.get('num_queries', 'N/A')} |")
        
        lines.append("")
        lines.append(f"**Total Gold Standard Articles**: {characteristics['gold_sizes']['total']}  ")
        lines.append(f"**Average Gold Standard Size**: {characteristics['gold_sizes']['mean']:.1f}  ")
        lines.append(f"**Unique Domains**: {', '.join(characteristics['unique_domains'])}")
        
        return lines
    
    def _generate_strategy_performance(self) -> List[str]:
        """Generate strategy performance summary table."""
        lines = ["## Strategy Performance Summary", ""]
        
        strategy_stats = self.stats_calc.calculate_strategy_stats()
        
        lines.append("### Performance Metrics Across All Studies")
        lines.append("")
        lines.append("| Strategy | Mean Recall | Mean Precision | Mean Retrieved | Perfect Recall |")
        lines.append("|----------|-------------|----------------|----------------|----------------|")
        
        # Sort by recall descending
        sorted_strategies = sorted(strategy_stats.items(), 
                                  key=lambda x: x[1]['mean_recall'], 
                                  reverse=True)
        
        for name, stats in sorted_strategies:
            lines.append(f"| `{name}` | "
                        f"{stats['mean_recall']:.1%} ± {stats['std_recall']:.1%} | "
                        f"{stats['mean_precision']:.4f} ± {stats['std_precision']:.4f} | "
                        f"{stats['mean_retrieved']:.0f} ± {stats['std_retrieved']:.0f} | "
                        f"{stats['num_perfect_recall']}/{stats['num_studies']} |")
        
        lines.append("")
        lines.append("*Perfect Recall: Number of studies where strategy achieved 100% recall*")
        
        return lines
    
    def _generate_recommendation(self) -> List[str]:
        """Generate best strategy recommendation."""
        lines = ["## Recommended Strategy", ""]
        
        strategy_stats = self.stats_calc.calculate_strategy_stats()
        best = self.stats_calc.get_best_strategy(strategy_stats, require_perfect_recall=False)
        
        lines.append(f"### `{best['name']}`")
        lines.append("")
        lines.append(f"**Justification**: {best['justification']}")
        lines.append("")
        
        # Detailed stats
        stats = best['stats']
        lines.append("**Performance Details**:")
        lines.append(f"- **Recall**: {stats['mean_recall']:.2%} (range: {stats['min_recall']:.2%} - {stats['max_recall']:.2%})")
        lines.append(f"- **Precision**: {stats['mean_precision']:.4f} (range: {stats['min_precision']:.4f} - {stats['max_precision']:.4f})")
        lines.append(f"- **F1 Score**: {stats['mean_f1']:.4f}")
        lines.append(f"- **Retrieved Articles**: {stats['mean_retrieved']:.0f} on average (range: {stats['min_retrieved']:.0f} - {stats['max_retrieved']:.0f})")
        lines.append(f"- **Perfect Recall**: {stats['num_perfect_recall']}/{stats['num_studies']} studies")
        
        return lines
    
    def _generate_detailed_analysis(self) -> List[str]:
        """Generate detailed per-strategy analysis."""
        lines = ["## Detailed Strategy Analysis", ""]
        
        strategy_stats = self.stats_calc.calculate_strategy_stats()
        
        for name in sorted(strategy_stats.keys()):
            stats = strategy_stats[name]
            lines.append(f"### `{name}`")
            lines.append("")
            
            # Summary stats
            lines.append("| Metric | Mean | Std Dev | Min | Max |")
            lines.append("|--------|------|---------|-----|-----|")
            lines.append(f"| Recall | {stats['mean_recall']:.2%} | {stats['std_recall']:.2%} | "
                        f"{stats['min_recall']:.2%} | {stats['max_recall']:.2%} |")
            lines.append(f"| Precision | {stats['mean_precision']:.4f} | {stats['std_precision']:.4f} | "
                        f"{stats['min_precision']:.4f} | {stats['max_precision']:.4f} |")
            lines.append(f"| F1 Score | {stats['mean_f1']:.4f} | {stats['std_f1']:.4f} | "
                        f"{stats['min_f1']:.4f} | {stats['max_f1']:.4f} |")
            lines.append(f"| Retrieved | {stats['mean_retrieved']:.0f} | {stats['std_retrieved']:.0f} | "
                        f"{stats['min_retrieved']:.0f} | {stats['max_retrieved']:.0f} |")
            
            lines.append("")
            
            # Per-study performance
            lines.append("**Performance by Study**:")
            lines.append("")
            for study_data in stats['studies']:
                recall_icon = "✅" if study_data['recall'] >= 0.999 else "⚠️"
                lines.append(f"- {recall_icon} **{study_data['study_id']}**: "
                            f"Recall={study_data['recall']:.1%}, "
                            f"Retrieved={study_data['retrieved_count']}/{study_data['gold_size']} gold")
            
            lines.append("")
        
        return lines
    
    def _generate_per_study_breakdown(self) -> List[str]:
        """Generate per-study performance breakdown."""
        lines = ["## Per-Study Performance Breakdown", ""]
        
        strategy_stats = self.stats_calc.calculate_strategy_stats()
        
        for study_id in sorted(self.studies_data.keys()):
            study = self.studies_data[study_id]
            metadata = study['metadata']
            
            lines.append(f"### {study_id}")
            lines.append("")
            lines.append(f"**Domain**: {metadata['domain']}  ")
            lines.append(f"**Gold Standard Size**: {metadata['gold_size']}  ")
            lines.append(f"**Databases**: {', '.join(metadata['databases'])}")
            lines.append("")
            
            # Strategy comparison table
            lines.append("| Strategy | Recall | Precision | F1 | Retrieved |")
            lines.append("|----------|--------|-----------|----|-----------| ")
            
            # Collect this study's data from strategy_stats
            for name in sorted(strategy_stats.keys()):
                study_data = [s for s in strategy_stats[name]['studies'] if s['study_id'] == study_id][0]
                lines.append(f"| `{name}` | {study_data['recall']:.1%} | "
                            f"{study_data['precision']:.4f} | {study_data['f1']:.4f} | "
                            f"{study_data['retrieved_count']} |")
            
            lines.append("")
        
        return lines
    
    def _generate_conclusions(self) -> List[str]:
        """Generate conclusions section."""
        lines = ["## Conclusions", ""]
        
        strategy_stats = self.stats_calc.calculate_strategy_stats()
        characteristics = self.stats_calc.compare_study_characteristics()
        
        # Key insights
        lines.append("### Key Insights")
        lines.append("")
        
        # 1. Recall consistency
        perfect_recall_strategies = {name: stats for name, stats in strategy_stats.items() 
                                     if stats['num_perfect_recall'] == stats['num_studies']}
        
        if perfect_recall_strategies:
            best_perfect = min(perfect_recall_strategies.items(), 
                             key=lambda x: x[1]['mean_retrieved'])
            lines.append(f"1. **Perfect Recall**: `{best_perfect[0]}` achieves 100% recall in all studies "
                        f"with the lowest retrieval burden ({best_perfect[1]['mean_retrieved']:.0f} articles on average)")
        else:
            lines.append(f"1. **Recall Variability**: No strategy achieves 100% recall across all {len(self.studies_data)} studies, "
                        "suggesting domain-specific tuning may be needed")
        
        # 2. Precision-recall tradeoff
        lines.append(f"2. **Precision-Recall Tradeoff**: Strategies vary widely in retrieved article counts "
                    f"(range: {min(s['mean_retrieved'] for s in strategy_stats.values()):.0f} - "
                    f"{max(s['mean_retrieved'] for s in strategy_stats.values()):.0f})")
        
        # 3. Domain diversity
        lines.append(f"3. **Domain Diversity**: Analysis covers {len(characteristics['unique_domains'])} domains, "
                    "providing evidence for generalizability of findings")
        
        return lines
    
    def save_report(self, output_path: Path):
        """
        Generate and save report to file.
        
        Args:
            output_path: Path to save markdown file
        """
        report = self.generate_full_report()
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Report saved to: {output_path}")


# CLI interface
if __name__ == '__main__':
    import argparse
    
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(description='Generate cross-study validation markdown report')
    parser.add_argument('--data-dir', type=str, default='cross_study_validation/data',
                       help='Directory containing study JSON files')
    parser.add_argument('--output', type=str, default=None,
                       help='Output markdown file path')
    
    args = parser.parse_args()
    
    # Load data
    data_dir = Path(args.data_dir)
    studies = load_studies_data(data_dir)
    
    if not studies:
        print(f"No studies found in {data_dir}")
        exit(1)
    
    # Generate report
    reporter = MarkdownReporter(studies)
    
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        output_path = Path(f'cross_study_validation/reports/report_{timestamp}.md')
    
    reporter.save_report(output_path)
    
    print(f"\n✅ Report generated: {output_path}")
    print(f"📊 Analyzed {len(studies)} studies")
