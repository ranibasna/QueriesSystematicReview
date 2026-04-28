"""
Visualization generation for cross-study validation analysis.

Generates publication-quality figures including:
- Box plots for metric distributions
- Bar charts for strategy comparisons  
- Scatter plots for tradeoff analysis
- Heatmaps for domain-specific performance
- Original-paper vs per-query retrieval comparisons
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import logging

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mtick
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D

# Configure matplotlib for publication-quality output
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9

logger = logging.getLogger(__name__)

# Color palette for strategies
STRATEGY_COLORS = {
    'precision_gated_union': '#2E86AB',
    'consensus_k2': '#A23B72',
    'consensus_k3': '#F18F01',
    'two_stage_screen': '#C73E1D',
    'time_stratified_hybrid': '#6A994E',
    'weighted_vote': '#BC4B51'
}

# Domain colors
DOMAIN_COLORS = {
    'nutrition': '#8B4513',
    'sleep medicine': '#4682B4',
    'artificial intelligence': '#9370DB'
}

# Original article counts reported in the published review papers.
PAPER_COUNTS = {
    'ai_2022': 4902,
    'Godos_2024': 2255,
    'lang_2024': 4582,
    'Lehner_2022': 2204,
    'Li_2024': 1179,
    'Medeiros_2023': 2724,
    'Nexha_2024': 575,
    'Riedy_2021': 564,
    'Cid-Verdejo_2024_Paper': 3233,
    'Cid_Verdejo_2024_Paper': 3233,
    'Varallo_2022': 6262,
}

QUERY_COLORS = ['#4E79A7', '#59A14F', '#F28E2B', '#E15759', '#76B7B2', '#B07AA1']


def format_count(value: Any) -> str:
    """Format article counts for report tables and annotations."""
    if value is None or pd.isna(value):
        return 'N/A'
    return f"{int(value):,}"


class VisualizationGenerator:
    """Generate publication-quality visualizations for cross-study analysis."""
    
    def __init__(self, data_file: Path, output_dir: Path):
        """
        Initialize visualization generator.
        
        Args:
            data_file: Path to all_studies.json
            output_dir: Directory to save figures
        """
        self.data_file = data_file
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_dir = data_file.parent.parent.parent
        
        # Load data
        with open(data_file, 'r') as f:
            data_json = json.load(f)
        
        # Handle both list format and dict format with 'studies' key
        if isinstance(data_json, dict) and 'studies' in data_json:
            self.data = list(data_json['studies'].values())
        elif isinstance(data_json, list):
            self.data = data_json
        else:
            raise ValueError(f"Unexpected data format in {data_file}")
        
        logger.info(f"Loaded {len(self.data)} studies for visualization")

    def _latest_query_summary_path(self, study_id: str, query_number: int) -> Path | None:
        """Return the newest summary_per_database CSV for a study/query pair."""
        query_dir = self.base_dir / 'benchmark_outputs' / study_id / f'query_{query_number:02d}'
        if not query_dir.exists():
            return None

        csv_files = list(query_dir.glob('summary_per_database_*.csv'))
        if not csv_files:
            return None

        return max(csv_files, key=lambda path: path.stat().st_mtime)

    def _load_query_combined_counts(self, study_id: str, expected_queries: int) -> List[float]:
        """Load per-query combined counts from the latest benchmark summary_per_database CSVs."""
        counts: List[float] = []

        for query_number in range(1, expected_queries + 1):
            summary_path = self._latest_query_summary_path(study_id, query_number)
            if summary_path is None:
                counts.append(np.nan)
                continue

            df = pd.read_csv(summary_path)
            combined_rows = df[df['database'].astype(str).str.upper() == 'COMBINED']
            if combined_rows.empty:
                logger.warning(
                    "No COMBINED row found in %s for %s Q%s",
                    summary_path.name,
                    study_id,
                    query_number,
                )
                counts.append(np.nan)
                continue

            counts.append(float(combined_rows.iloc[0]['results_count']))

        return counts

    @staticmethod
    def _format_study_label(study_id: str) -> str:
        """Format a study identifier for compact heatmap labels."""
        return study_id.replace('_Paper', '').replace('_', '\n')

    @staticmethod
    def _deduplicated_precision_percent(true_positives: Any, results_count: Any) -> float:
        """Return precision as a percentage using the deduplicated COMBINED result count."""
        if (
            true_positives is None or results_count is None or
            pd.isna(true_positives) or pd.isna(results_count) or
            float(results_count) <= 0
        ):
            return np.nan
        return float(true_positives) / float(results_count) * 100.0

    def _load_query_combined_row(self, study_id: str, query_number: int) -> Dict[str, float]:
        """Load the latest COMBINED row for a study/query pair from summary_per_database."""
        summary_path = self._latest_query_summary_path(study_id, query_number)
        if summary_path is None:
            return {}

        df = pd.read_csv(summary_path)
        combined_rows = df[df['database'].astype(str).str.upper() == 'COMBINED']
        if combined_rows.empty:
            logger.warning(
                "No COMBINED row found in %s for %s Q%s",
                summary_path.name,
                study_id,
                query_number,
            )
            return {}

        row = combined_rows.iloc[0]
        return {
            'results_count': float(row.get('results_count', np.nan)),
            'TP': float(row.get('TP', np.nan)),
            'recall': float(row.get('recall', np.nan)),
            'NNR_proxy': float(row.get('NNR_proxy', np.nan)),
        }

    def _resolve_query_combined_metrics(self, study: Dict[str, Any], query_number: int) -> Dict[str, float]:
        """Return deduplicated combined metrics for a single query with JSON fallback."""
        study_id = study['study_id']
        combined_row = self._load_query_combined_row(study_id, query_number)

        query_idx = query_number - 1
        query_perf = study.get('query_performance', [])
        fallback = query_perf[query_idx] if query_idx < len(query_perf) else {}

        results_count = combined_row.get('results_count', fallback.get('results_count', np.nan))
        true_positives = combined_row.get('TP', fallback.get('true_positives', np.nan))
        recall = combined_row.get('recall', fallback.get('recall', np.nan))
        recall_percent = float(recall) * 100.0 if pd.notna(recall) else np.nan

        return {
            'results_count': float(results_count) if pd.notna(results_count) else np.nan,
            'true_positives': float(true_positives) if pd.notna(true_positives) else np.nan,
            'recall_percent': recall_percent,
            'precision_percent': self._deduplicated_precision_percent(true_positives, results_count),
        }
    
    def generate_all(self) -> List[Path]:
        """
        Generate all visualizations.
        
        Returns:
            List of paths to generated figure files
        """
        figures = []
        
        logger.info("Generating box plots...")
        figures.extend(self.create_box_plots())
        
        logger.info("Generating bar charts...")
        figures.append(self.create_bar_chart())
        
        logger.info("Generating scatter plots...")
        figures.append(self.create_scatter_plot())
        
        logger.info("Generating heatmaps...")
        figures.append(self.create_heatmap())
        
        logger.info("Generating per-query recall charts...")
        figures.extend(self.create_per_query_recall_charts())

        logger.info("Generating per-query precision heatmap...")
        precision_heatmap = self.create_per_query_precision_heatmap()
        if precision_heatmap is not None:
            figures.append(precision_heatmap)

        logger.info("Generating retrieval comparison charts...")
        figures.extend(self.create_retrieval_comparison_charts())

        logger.info("Generating Q1-Q2 comparison heatmaps...")
        q1_q2_heatmap = self.create_q1_q2_recall_vs_retrieval_heatmaps()
        if q1_q2_heatmap is not None:
            figures.append(q1_q2_heatmap)
        
        logger.info(f"Generated {len(figures)} figures in {self.output_dir}")
        return figures
    
    def create_box_plots(self) -> List[Path]:
        """
        Create box plots showing distribution of recall, precision, and F1
        across studies for each strategy.
        
        Returns:
            List of paths to generated box plot files
        """
        metrics = ['recall', 'precision', 'f1']
        metric_labels = {
            'recall': 'Recall (%)',
            'precision': 'Precision (%)',
            'f1': 'F1 Score (%)'
        }
        
        figures = []
        
        for metric in metrics:
            # Prepare data for box plot
            data_for_plot = []
            
            for study in self.data:
                study_id = study['study_id']
                for strategy in study['aggregation_strategies']:
                    strategy_name = strategy['name']
                    value = strategy[metric] * 100  # Convert to percentage
                    
                    data_for_plot.append({
                        'Strategy': strategy_name,
                        'Value': value,
                        'Study': study_id
                    })
            
            df = pd.DataFrame(data_for_plot)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Get unique strategies and sort them
            strategies = sorted(df['Strategy'].unique())
            positions = range(len(strategies))
            
            # Create box plot with custom colors
            bp = ax.boxplot(
                [df[df['Strategy'] == s]['Value'].values for s in strategies],
                positions=positions,
                patch_artist=True,
                widths=0.6,
                showmeans=True,
                meanprops=dict(marker='D', markerfacecolor='red', markersize=6)
            )
            
            # Color boxes by strategy
            for patch, strategy in zip(bp['boxes'], strategies):
                color = STRATEGY_COLORS.get(strategy, '#999999')
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            # Overlay individual points
            for i, strategy in enumerate(strategies):
                strategy_data = df[df['Strategy'] == strategy]['Value'].values
                x = np.random.normal(i, 0.04, size=len(strategy_data))
                ax.scatter(x, strategy_data, alpha=0.6, s=50, 
                          color=STRATEGY_COLORS.get(strategy, '#999999'),
                          edgecolors='black', linewidths=0.5, zorder=3)
            
            # Formatting
            ax.set_xticks(positions)
            ax.set_xticklabels([s.replace('_', '\n') for s in strategies], rotation=0)
            ax.set_ylabel(metric_labels[metric], fontweight='bold')
            ax.set_title(f'{metric_labels[metric]} Distribution Across Studies', 
                        fontweight='bold', pad=20)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)
            
            # Add horizontal line at 100% for recall plots
            if metric == 'recall':
                ax.axhline(y=100, color='green', linestyle='--', 
                          alpha=0.5, linewidth=1.5, label='Perfect Recall')
                ax.legend(loc='upper right')
            
            plt.tight_layout()
            
            # Save figure
            output_file = self.output_dir / f'boxplot_{metric}.png'
            plt.savefig(output_file, bbox_inches='tight', dpi=300)
            plt.close()
            
            figures.append(output_file)
            logger.info(f"Created box plot: {output_file.name}")
        
        return figures
    
    def create_bar_chart(self) -> Path:
        """
        Create bar chart comparing mean performance across strategies
        with error bars showing standard deviation.
        
        Returns:
            Path to generated bar chart file
        """
        # Calculate mean and std for each strategy
        strategy_stats = {}
        
        for study in self.data:
            for strategy in study['aggregation_strategies']:
                name = strategy['name']
                if name not in strategy_stats:
                    strategy_stats[name] = {
                        'recall': [],
                        'precision': [],
                        'f1': []
                    }
                
                strategy_stats[name]['recall'].append(strategy['recall'] * 100)
                strategy_stats[name]['precision'].append(strategy['precision'] * 100)
                strategy_stats[name]['f1'].append(strategy['f1'] * 100)
        
        # Calculate means and stds
        strategies = sorted(strategy_stats.keys())
        
        recall_means = [np.mean(strategy_stats[s]['recall']) for s in strategies]
        recall_stds = [np.std(strategy_stats[s]['recall']) for s in strategies]
        
        precision_means = [np.mean(strategy_stats[s]['precision']) for s in strategies]
        precision_stds = [np.std(strategy_stats[s]['precision']) for s in strategies]
        
        f1_means = [np.mean(strategy_stats[s]['f1']) for s in strategies]
        f1_stds = [np.std(strategy_stats[s]['f1']) for s in strategies]
        
        # Create figure with subplots
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        
        x = np.arange(len(strategies))
        width = 0.6
        
        metrics_data = [
            ('Recall (%)', recall_means, recall_stds),
            ('Precision (%)', precision_means, precision_stds),
            ('F1 Score (%)', f1_means, f1_stds)
        ]
        
        for ax, (metric_label, means, stds) in zip(axes, metrics_data):
            colors = [STRATEGY_COLORS.get(s, '#999999') for s in strategies]
            
            bars = ax.bar(x, means, width, yerr=stds, 
                         capsize=5, color=colors, alpha=0.8,
                         edgecolor='black', linewidth=0.8,
                         error_kw={'linewidth': 1.5, 'ecolor': 'black'})
            
            # Add value labels on bars
            for bar, mean, std in zip(bars, means, stds):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + std + 1,
                       f'{mean:.1f}',
                       ha='center', va='bottom', fontsize=8, fontweight='bold')
            
            ax.set_xlabel('Strategy', fontweight='bold')
            ax.set_ylabel(metric_label, fontweight='bold')
            ax.set_title(f'Mean {metric_label} (±SD)', fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels([s.replace('_', '\n') for s in strategies], 
                              rotation=0, ha='center')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)
        
        plt.suptitle('Strategy Performance Comparison Across All Studies', 
                    fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        # Save figure
        output_file = self.output_dir / 'bar_chart_comparison.png'
        plt.savefig(output_file, bbox_inches='tight', dpi=300)
        plt.close()
        
        logger.info(f"Created bar chart: {output_file.name}")
        return output_file
    
    def create_scatter_plot(self) -> Path:
        """
        Create scatter plot showing precision vs recall tradeoffs
        for each strategy across all studies.
        
        Returns:
            Path to generated scatter plot file
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Collect data points
        for study in self.data:
            study_id = study['study_id']
            
            for strategy in study['aggregation_strategies']:
                name = strategy['name']
                recall = strategy['recall'] * 100
                precision = strategy['precision'] * 100
                
                color = STRATEGY_COLORS.get(name, '#999999')
                ax.scatter(recall, precision, s=150, alpha=0.7, 
                          color=color, edgecolors='black', linewidths=1,
                          label=name)
        
        # Remove duplicate labels
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), 
                 loc='best', framealpha=0.9, edgecolor='black')
        
        # Add diagonal line (Pareto frontier would be ideal)
        ax.plot([0, 100], [0, 100], 'k--', alpha=0.3, linewidth=1, 
               label='Equal Precision-Recall')
        
        # Formatting
        ax.set_xlabel('Recall (%)', fontweight='bold', fontsize=12)
        ax.set_ylabel('Precision (%)', fontweight='bold', fontsize=12)
        ax.set_title('Precision-Recall Tradeoff Across All Studies', 
                    fontweight='bold', fontsize=14, pad=20)
        ax.grid(alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Set reasonable axis limits
        ax.set_xlim(-5, 105)
        ax.set_ylim(-0.5, max([s['precision'] * 100 
                               for study in self.data 
                               for s in study['aggregation_strategies']]) + 1)
        
        plt.tight_layout()
        
        # Save figure
        output_file = self.output_dir / 'scatter_precision_recall.png'
        plt.savefig(output_file, bbox_inches='tight', dpi=300)
        plt.close()
        
        logger.info(f"Created scatter plot: {output_file.name}")
        return output_file
    
    def create_heatmap(self) -> Path:
        """
        Create heatmap showing strategy recall performance by study/domain.
        
        Returns:
            Path to generated heatmap file
        """
        # Prepare data for heatmap
        rows = []
        
        for study in self.data:
            study_id = study['study_id']
            domain = study['metadata']['domain']
            
            row = {'Study': f"{study_id}\n({domain})"}
            
            for strategy in study['aggregation_strategies']:
                row[strategy['name']] = strategy['recall'] * 100
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df = df.set_index('Study')
        
        # Sort columns by mean recall
        col_means = df.mean().sort_values(ascending=False)
        df = df[col_means.index]
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 6))
        
        sns.heatmap(df, annot=True, fmt='.1f', cmap='RdYlGn', 
                   cbar_kws={'label': 'Recall (%)'},
                   linewidths=0.5, linecolor='gray',
                   vmin=0, vmax=100, center=50,
                   ax=ax)
        
        ax.set_xlabel('Aggregation Strategy', fontweight='bold', fontsize=12)
        ax.set_ylabel('Study (Domain)', fontweight='bold', fontsize=12)
        ax.set_title('Strategy Recall Performance by Study', 
                    fontweight='bold', fontsize=14, pad=20)
        
        # Rotate x labels
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save figure
        output_file = self.output_dir / 'heatmap_recall_by_study.png'
        plt.savefig(output_file, bbox_inches='tight', dpi=300)
        plt.close()
        
        logger.info(f"Created heatmap: {output_file.name}")
        return output_file

    def create_per_query_recall_charts(self) -> List[Path]:
        """
        Create two per-query recall visualizations:
          1. Heatmap: studies × queries (Q1–Q6), cell = recall %
          2. Line chart: one line per study, x = query index, y = recall %

        Only studies that have query_performance data are included.

        Returns:
            List of paths to the two generated figures.
        """
        # Collect per-query data
        studies_with_queries = [
            s for s in self.data
            if s.get('query_performance') and len(s['query_performance']) > 0
        ]

        if not studies_with_queries:
            logger.warning("No query_performance data found; skipping per-query charts.")
            return []

        figures = []

        # --- 1. Heatmap: studies x queries ---
        heatmap_rows = []
        max_queries = max(len(s['query_performance']) for s in studies_with_queries)
        query_labels = [f"Q{i+1}" for i in range(max_queries)]

        for study in studies_with_queries:
            row = {'Study': study['study_id']}
            for i, qp in enumerate(study['query_performance']):
                row[f"Q{i+1}"] = round(qp['recall'] * 100, 1)
            heatmap_rows.append(row)

        df_heatmap = pd.DataFrame(heatmap_rows).set_index('Study')
        # Ensure all query columns exist (fill missing with NaN)
        for ql in query_labels:
            if ql not in df_heatmap.columns:
                df_heatmap[ql] = float('nan')
        df_heatmap = df_heatmap[query_labels]

        fig, ax = plt.subplots(figsize=(max(8, max_queries * 1.4), max(4, len(studies_with_queries) * 0.8)))
        sns.heatmap(
            df_heatmap,
            annot=True, fmt='.1f',
            cmap='RdYlGn',
            cbar_kws={'label': 'Recall (%)'},
            linewidths=0.5, linecolor='gray',
            vmin=0, vmax=100, center=50,
            ax=ax
        )
        ax.set_xlabel('Query', fontweight='bold', fontsize=12)
        ax.set_ylabel('Study', fontweight='bold', fontsize=12)
        ax.set_title('Per-Query Recall by Study (combined databases)',
                     fontweight='bold', fontsize=14, pad=15)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        plt.tight_layout()
        heatmap_file = self.output_dir / 'per_query_recall_heatmap.png'
        plt.savefig(heatmap_file, bbox_inches='tight', dpi=300)
        plt.close()
        figures.append(heatmap_file)
        logger.info(f"Created per-query recall heatmap: {heatmap_file.name}")

        # --- 2. Line chart: one line per study ---
        fig, ax = plt.subplots(figsize=(max(8, max_queries * 1.5), 5))

        # Build a colour cycle for studies
        cmap = plt.colormaps.get_cmap('tab10')
        study_colors = {
            s['study_id']: cmap(i % 10)
            for i, s in enumerate(studies_with_queries)
        }

        for study in studies_with_queries:
            sid = study['study_id']
            recalls = [qp['recall'] * 100 for qp in study['query_performance']]
            xs = list(range(1, len(recalls) + 1))
            ax.plot(xs, recalls, marker='o', linewidth=1.8, markersize=7,
                    label=sid, color=study_colors[sid])

        ax.set_xticks(list(range(1, max_queries + 1)))
        ax.set_xticklabels([f"Q{i}" for i in range(1, max_queries + 1)])
        ax.set_xlabel('Query', fontweight='bold', fontsize=12)
        ax.set_ylabel('Recall (%)', fontweight='bold', fontsize=12)
        ax.set_title('Per-Query Recall Across Studies (combined databases)',
                     fontweight='bold', fontsize=14, pad=15)
        ax.axhline(y=100, color='green', linestyle='--', alpha=0.5,
                   linewidth=1.2, label='Perfect Recall')
        ax.set_ylim(-5, 110)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        ax.legend(loc='lower right', framealpha=0.9, fontsize=8, ncol=2)
        plt.tight_layout()
        lines_file = self.output_dir / 'per_query_recall_lines.png'
        plt.savefig(lines_file, bbox_inches='tight', dpi=300)
        plt.close()
        figures.append(lines_file)
        logger.info(f"Created per-query recall line chart: {lines_file.name}")

        return figures

    def create_per_query_precision_heatmap(self) -> Path | None:
        """Create a study-by-query heatmap of deduplicated precision percentages."""
        studies_with_queries = [
            study for study in self.data
            if study.get('query_performance') and len(study['query_performance']) > 0
        ]

        if not studies_with_queries:
            logger.warning("No query_performance data found; skipping per-query precision heatmap.")
            return None

        max_queries = max(len(study['query_performance']) for study in studies_with_queries)
        query_labels = [f"Q{i+1}" for i in range(max_queries)]

        precision_rows = []
        for study in studies_with_queries:
            row = {'Study': study['study_id']}
            for query_number, label in enumerate(query_labels, start=1):
                metrics = self._resolve_query_combined_metrics(study, query_number)
                row[label] = metrics['precision_percent']
            precision_rows.append(row)

        df_precision = pd.DataFrame(precision_rows).set_index('Study')[query_labels]
        annot_precision = df_precision.apply(
            lambda column: column.map(
                lambda value: f"{value:.2f}" if pd.notna(value) else ''
            )
        )

        valid_precision = df_precision.to_numpy(dtype=float)
        valid_precision = valid_precision[np.isfinite(valid_precision)]
        precision_vmax = max(
            2.0,
            float(np.nanpercentile(valid_precision, 95)) if valid_precision.size else 2.0,
        )

        fig, ax = plt.subplots(
            figsize=(max(8, max_queries * 1.4), max(4, len(studies_with_queries) * 0.8))
        )
        sns.heatmap(
            df_precision,
            annot=annot_precision,
            fmt='',
            cmap='YlGnBu',
            cbar_kws={'label': 'Precision (%)'},
            linewidths=0.5,
            linecolor='gray',
            vmin=0,
            vmax=precision_vmax,
            ax=ax,
        )
        ax.set_xlabel('Query', fontweight='bold', fontsize=12)
        ax.set_ylabel('Study', fontweight='bold', fontsize=12)
        ax.set_title(
            'Per-Query Precision by Study\n(TP / deduplicated COMBINED results)',
            fontweight='bold',
            fontsize=14,
            pad=15,
        )
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        fig.text(
            0.5,
            -0.02,
            'Precision is derived as true positives divided by the deduplicated COMBINED results_count for each query.',
            ha='center',
            fontsize=9,
        )
        plt.tight_layout()

        output_file = self.output_dir / 'per_query_precision_heatmap.png'
        plt.savefig(output_file, bbox_inches='tight', dpi=300)
        plt.close()

        logger.info(f"Created per-query precision heatmap: {output_file.name}")
        return output_file

    def create_q1_q2_recall_vs_retrieval_heatmaps(self) -> Path | None:
        """Create the Q1/Q2 heatmap figure with recall, precision, and retrieval ratio panels."""
        query_labels = ['Q1', 'Q2']
        q1_q2_rows = []

        for study in self.data:
            study_id = study['study_id']
            q1_metrics = self._resolve_query_combined_metrics(study, 1)
            q2_metrics = self._resolve_query_combined_metrics(study, 2)
            metrics_by_query = {'Q1': q1_metrics, 'Q2': q2_metrics}

            if all(pd.isna(metrics['results_count']) and pd.isna(metrics['recall_percent']) for metrics in metrics_by_query.values()):
                continue

            study_label = self._format_study_label(study_id)
            paper_count = PAPER_COUNTS.get(study_id)

            recall_row = {'Study': study_label}
            precision_row = {'Study': study_label}
            ratio_row = {'Study': study_label}
            ratio_annotation_row = {'Study': study_label}

            for label in query_labels:
                metrics = metrics_by_query[label]
                retrieved_count = metrics['results_count']
                recall_row[label] = metrics['recall_percent']
                precision_row[label] = metrics['precision_percent']

                if paper_count and pd.notna(retrieved_count):
                    ratio_percent = retrieved_count / paper_count * 100.0
                else:
                    ratio_percent = np.nan

                ratio_row[label] = ratio_percent
                if pd.notna(retrieved_count) and pd.notna(ratio_percent):
                    ratio_annotation_row[label] = f"{format_count(retrieved_count)}\n({ratio_percent:.1f}%)"
                elif pd.notna(retrieved_count):
                    ratio_annotation_row[label] = f"{format_count(retrieved_count)}\n(N/A)"
                else:
                    ratio_annotation_row[label] = ''

            q1_q2_rows.append({
                'study_id': study_id,
                'recall_row': recall_row,
                'precision_row': precision_row,
                'ratio_row': ratio_row,
                'ratio_annotation_row': ratio_annotation_row,
            })

        if not q1_q2_rows:
            logger.warning('No Q1/Q2 data available; skipping Q1-Q2 heatmaps.')
            return None

        q1_q2_rows.sort(key=lambda item: item['study_id'].casefold())

        recall_rows = [item['recall_row'] for item in q1_q2_rows]
        precision_rows = [item['precision_row'] for item in q1_q2_rows]
        ratio_rows = [item['ratio_row'] for item in q1_q2_rows]
        ratio_annotations = [item['ratio_annotation_row'] for item in q1_q2_rows]

        df_recall = pd.DataFrame(recall_rows).set_index('Study')[query_labels]
        df_precision = pd.DataFrame(precision_rows).set_index('Study')[query_labels]
        df_ratio = pd.DataFrame(ratio_rows).set_index('Study')[query_labels]
        df_ratio_annot = pd.DataFrame(ratio_annotations).set_index('Study')[query_labels]

        df_recall_annot = df_recall.apply(
            lambda column: column.map(
                lambda value: f"{value:.1f}" if pd.notna(value) else ''
            )
        )
        df_precision_annot = df_precision.apply(
            lambda column: column.map(
                lambda value: f"{value:.2f}" if pd.notna(value) else ''
            )
        )

        valid_precision = df_precision.to_numpy(dtype=float)
        valid_precision = valid_precision[np.isfinite(valid_precision)]
        precision_vmax = max(
            2.0,
            float(np.nanpercentile(valid_precision, 95)) if valid_precision.size else 2.0,
        )

        valid_ratio = df_ratio.to_numpy(dtype=float)
        valid_ratio = valid_ratio[np.isfinite(valid_ratio)]
        ratio_vmax = max(
            100.0,
            float(np.nanmax(valid_ratio)) if valid_ratio.size else 100.0,
        )
        ratio_plot = df_ratio.fillna(-1.0)
        ratio_cmap = plt.cm.YlOrRd.copy()
        ratio_cmap.set_under('#D9D9D9')

        fig, axes = plt.subplots(
            1,
            3,
            figsize=(20, max(6.8, len(df_recall) * 0.9)),
            gridspec_kw={'width_ratios': [1, 1, 1.15]},
        )

        sns.heatmap(
            df_recall,
            annot=df_recall_annot,
            fmt='',
            cmap='RdYlGn',
            cbar_kws={'label': 'Recall (%)'},
            linewidths=0.5,
            linecolor='gray',
            vmin=0,
            vmax=100,
            center=50,
            ax=axes[0],
        )
        axes[0].set_title('Q1-Q2 Recall (%)', fontweight='bold', fontsize=13, pad=12)
        axes[0].set_xlabel('Query', fontweight='bold')
        axes[0].set_ylabel('Study', fontweight='bold')
        axes[0].set_xticklabels(query_labels, rotation=0)
        axes[0].set_yticklabels(df_recall.index.tolist(), rotation=0)

        sns.heatmap(
            df_precision,
            annot=df_precision_annot,
            fmt='',
            cmap='YlGnBu',
            cbar_kws={'label': 'Precision (%)'},
            linewidths=0.5,
            linecolor='gray',
            vmin=0,
            vmax=precision_vmax,
            ax=axes[1],
        )
        axes[1].set_title('Q1-Q2 Precision (%)', fontweight='bold', fontsize=13, pad=12)
        axes[1].set_xlabel('Query', fontweight='bold')
        axes[1].set_ylabel('')
        axes[1].set_xticklabels(query_labels, rotation=0)
        axes[1].set_yticklabels(df_precision.index.tolist(), rotation=0)

        sns.heatmap(
            ratio_plot,
            annot=df_ratio_annot,
            fmt='',
            cmap=ratio_cmap,
            linewidths=0.5,
            linecolor='gray',
            vmin=0,
            vmax=ratio_vmax,
            cbar_kws={'label': 'Query count / original paper count (%)'},
            ax=axes[2],
        )
        axes[2].set_title('Q1-Q2 Retrieval Ratio', fontweight='bold', fontsize=13, pad=12)
        axes[2].set_xlabel('Query', fontweight='bold')
        axes[2].set_ylabel('')
        axes[2].set_xticklabels(query_labels, rotation=0)
        axes[2].set_yticklabels(df_ratio.index.tolist(), rotation=0)

        fig.suptitle(
            'Q1-Q2 Recall, Precision, and Retrieval Comparison Across Studies',
            fontsize=18,
            fontweight='bold',
            y=1.02,
        )
        fig.text(
            0.5,
            -0.02,
            'Precision = TP / deduplicated COMBINED query results_count. Retrieval ratio = deduplicated query count / original paper count.',
            ha='center',
            fontsize=10,
        )
        plt.tight_layout()

        output_file = self.output_dir / 'q1_q2_recall_vs_retrieval_heatmaps.png'
        fig.savefig(output_file, bbox_inches='tight', dpi=300)
        plt.close(fig)

        logger.info(f"Created Q1-Q2 comparison heatmaps: {output_file.name}")
        return output_file

    def _build_retrieval_comparison_dataframe(self) -> pd.DataFrame:
        """Build per-study comparison data from benchmark COMBINED rows and paper counts."""
        rows = []
        max_queries = max(
            (len(study.get('query_performance', [])) for study in self.data),
            default=0,
        )
        query_labels = [f'Q{i+1}' for i in range(max_queries)]

        for study in sorted(self.data, key=lambda item: item['study_id']):
            study_id = study['study_id']
            query_counts = self._load_query_combined_counts(study_id, max_queries)

            row = {
                'study': study_id,
                'paper_original': PAPER_COUNTS.get(study_id),
            }

            for index, label in enumerate(query_labels):
                row[label] = query_counts[index] if index < len(query_counts) else np.nan

            rows.append(row)

        if not rows:
            return pd.DataFrame()

        return pd.DataFrame(rows).set_index('study')

    def _write_retrieval_comparison_report(self, df: pd.DataFrame, query_labels: List[str]):
        """Persist the comparison table used by the retrieval comparison figures."""
        reports_dir = self.output_dir.parent
        reports_dir.mkdir(parents=True, exist_ok=True)

        csv_path = reports_dir / 'retrieval_comparison.csv'
        df.to_csv(csv_path)
        logger.info(f"Saved retrieval comparison table: {csv_path.name}")

        md_lines = [
            '# Retrieval Comparison: Original Paper vs LLM Queries',
            '',
            '- `paper_original`: article count reported by the published review.',
            '- `Q1..Qn`: latest `summary_per_database_*.csv` `COMBINED` result count for that query.',
            '- Each `Q` value is deduplicated across databases within that query only.',
            '- The same latest `summary_per_database_*.csv` `COMBINED` values are used in the CSV and both retrieval comparison figures.',
            '- `results_count_raw` and individual database rows are intentionally not used for the `Q` columns here.',
            '',
            '| Study | Paper Original | ' + ' | '.join(query_labels) + ' |',
            '|-------|---------------:|' + '|'.join(['---:' for _ in query_labels]) + '|',
        ]

        for study_id, row in df.iterrows():
            values = [format_count(row['paper_original'])] + [format_count(row[label]) for label in query_labels]
            md_lines.append(f"| {study_id} | " + ' | '.join(values) + ' |')

        md_lines.extend([
            '',
            '> `Lehner_2022` uses the original paper retrieval count of 2,204.',
            '> `Varallo_2022` uses the post-dedup count reported in the paper because a pre-dedup total was not available.',
            '> These values are intended to match the `COMBINED` row in each per-query benchmark summary file.',
        ])

        md_path = reports_dir / 'retrieval_comparison.md'
        md_path.write_text('\n'.join(md_lines), encoding='utf-8')
        logger.info(f"Saved retrieval comparison summary: {md_path.name}")

    def _load_retrieval_comparison_csv(self) -> pd.DataFrame:
        """Load the persisted retrieval comparison table so figures use report values exactly."""
        csv_path = self.output_dir.parent / 'retrieval_comparison.csv'
        if not csv_path.exists():
            raise FileNotFoundError(f"Retrieval comparison CSV not found: {csv_path}")

        df = pd.read_csv(csv_path).set_index('study')
        for column in df.columns:
            df[column] = pd.to_numeric(df[column], errors='coerce')
        return df

    def _create_retrieval_ratio_matrix(self, df: pd.DataFrame, query_labels: List[str]) -> Path:
        """Create a study-by-query figure with raw counts and retrieval ratios from the CSV table."""
        counts_df = df[query_labels].apply(lambda column: pd.to_numeric(column, errors='coerce'))
        count_comparison_df = pd.concat(
            [df[['paper_original']].rename(columns={'paper_original': 'Paper'}), counts_df],
            axis=1,
        )
        ratio_df = counts_df.div(df['paper_original'], axis=0)
        ratio_percent_df = ratio_df * 100.0

        count_annotations = count_comparison_df.apply(lambda column: column.map(format_count))
        ratio_annotations = pd.DataFrame(index=df.index)
        for label in query_labels:
            ratio_annotations[label] = [
                f"{value:.2f}x" if pd.notna(value) else 'N/A'
                for value in ratio_df[label]
            ]

        positive_counts = count_comparison_df.to_numpy(dtype=float)
        positive_counts = positive_counts[np.isfinite(positive_counts) & (positive_counts > 0)]
        count_vmin = max(1.0, float(np.nanmin(positive_counts)) if positive_counts.size else 1.0)
        count_vmax = max(count_vmin, float(np.nanmax(positive_counts)) if positive_counts.size else count_vmin)
        ratio_vmax = max(
            100.0,
            float(np.nanmax(ratio_percent_df.to_numpy())) if not ratio_percent_df.empty else 100.0,
        )

        fig, axes = plt.subplots(
            1,
            2,
            figsize=(max(15, len(query_labels) * 4.2), max(6.8, len(df) * 0.78)),
            gridspec_kw={'width_ratios': [1, 1.12]},
        )

        study_labels = [study_id.replace('_Paper', '').replace('_', '\n') for study_id in df.index]

        sns.heatmap(
            count_comparison_df,
            annot=count_annotations,
            fmt='',
            cmap='Blues',
            norm=LogNorm(vmin=count_vmin, vmax=count_vmax),
            linewidths=0.5,
            linecolor='gray',
            cbar_kws={'label': 'Retrieved articles per query (log scale)'},
            ax=axes[0],
        )
        axes[0].set_title('Original Paper Count and Raw Query Counts', fontweight='bold', fontsize=13, pad=12)
        axes[0].set_xlabel('Count source', fontweight='bold')
        axes[0].set_ylabel('Study', fontweight='bold')
        axes[0].set_xticklabels(count_comparison_df.columns.tolist(), rotation=0)
        axes[0].set_yticklabels(study_labels, rotation=0)

        ratio_plot = ratio_percent_df.fillna(-1.0)
        ratio_cmap = plt.cm.YlOrRd.copy()
        ratio_cmap.set_under('#D9D9D9')

        sns.heatmap(
            ratio_plot,
            annot=ratio_annotations,
            fmt='',
            cmap=ratio_cmap,
            vmin=0,
            vmax=ratio_vmax,
            linewidths=0.5,
            linecolor='gray',
            cbar_kws={'label': 'Retrieval ratio = query count / original paper count (%)'},
            ax=axes[1],
        )
        axes[1].set_title('Retrieval Ratio by Study and Query', fontweight='bold', fontsize=13, pad=12)
        axes[1].set_xlabel('Query', fontweight='bold')
        axes[1].set_ylabel('')
        axes[1].set_xticklabels(query_labels, rotation=0)
        axes[1].set_yticklabels(study_labels, rotation=0)

        fig.suptitle(
            'Study-by-Query Retrieval Counts and Ratios\nRatios are computed from retrieval_comparison.csv as Q count / paper_original',
            fontsize=15,
            fontweight='bold',
            y=1.02,
        )
        fig.text(
            0.5,
            -0.02,
            'Gray ratio cells indicate studies without an original paper count, so the ratio is not defined.',
            ha='center',
            fontsize=10,
        )
        plt.tight_layout()

        ratio_matrix_path = self.output_dir / 'retrieval_comparison_ratio_matrix.png'
        fig.savefig(ratio_matrix_path, bbox_inches='tight', dpi=300)
        plt.close(fig)
        logger.info(f"Created retrieval ratio matrix: {ratio_matrix_path.name}")
        return ratio_matrix_path

    def create_retrieval_comparison_charts(self) -> List[Path]:
        """Create original-paper comparison figures using per-query COMBINED retrieval counts."""
        df = self._build_retrieval_comparison_dataframe()
        if df.empty:
            logger.warning('No study data available for retrieval comparison charts.')
            return []

        query_labels = [column for column in df.columns if column.startswith('Q')]
        self._write_retrieval_comparison_report(df, query_labels)
        df = self._load_retrieval_comparison_csv()

        figures = []
        studies = df.index.tolist()

        ratio_matrix_path = self._create_retrieval_ratio_matrix(df, query_labels)
        figures.append(ratio_matrix_path)

        ratio_df = pd.DataFrame(index=df.index)
        annot_df = pd.DataFrame(index=df.index)
        for label in query_labels:
            ratio_df[label] = np.where(
                pd.notna(df['paper_original']) & (df['paper_original'] > 0) & pd.notna(df[label]),
                (df[label] / df['paper_original']) * 100,
                np.nan,
            )
            annot_df[label] = [
                f"{format_count(df.loc[study_id, label])}\n({value:.1f}%)" if pd.notna(value) else 'N/A'
                for study_id, value in ratio_df[label].items()
            ]

        ratio_plot = ratio_df.fillna(-1.0)
        annot_plot = annot_df.copy()

        fig, ax = plt.subplots(
            figsize=(max(8, len(query_labels) * 1.8), max(5, len(ratio_plot) * 0.9)),
        )

        ratio_cmap = plt.cm.YlOrRd.copy()
        ratio_cmap.set_under('#D9D9D9')
        valid_ratio_values = ratio_df.to_numpy(dtype=float)
        valid_ratio_values = valid_ratio_values[np.isfinite(valid_ratio_values)]
        vmax = max(100.0, float(np.nanmax(valid_ratio_values)) if valid_ratio_values.size else 100.0)
        sns.heatmap(
            ratio_plot,
            annot=annot_plot,
            fmt='',
            cmap=ratio_cmap,
            linewidths=0.5,
            linecolor='gray',
            vmin=0,
            vmax=vmax,
            cbar_kws={'label': 'Query count / original paper count (%)'},
            ax=ax,
        )
        ax.set_xlabel('Query', fontweight='bold', fontsize=12)
        ax.set_ylabel('Study', fontweight='bold', fontsize=12)
        ax.set_title(
            'Per-Query Retrieval vs Original Paper Count\n(latest COMBINED row from summary_per_database)',
            fontweight='bold',
            fontsize=14,
            pad=15,
        )
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        ax.set_yticklabels([label.replace('_', '\n') for label in df.index], rotation=0)
        plt.tight_layout()

        heatmap_path = self.output_dir / 'retrieval_comparison_heatmap.png'
        fig.savefig(heatmap_path, bbox_inches='tight', dpi=300)
        plt.close(fig)
        figures.append(heatmap_path)
        logger.info(f"Created retrieval comparison heatmap: {heatmap_path.name}")

        # Faceted chart: per-query counts vs original paper count.
        # Use fewer columns and larger panels so every per-query value remains legible.
        ncols = min(2, max(1, len(studies)))
        nrows = int(np.ceil(len(studies) / ncols))
        fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 6.5, nrows * 5.4), sharey=False)
        axes = np.atleast_1d(axes).flatten()

        for index, study_id in enumerate(studies):
            ax = axes[index]
            query_values = [df.loc[study_id, label] if pd.notna(df.loc[study_id, label]) else 0 for label in query_labels]
            paper_value = df.loc[study_id, 'paper_original'] if pd.notna(df.loc[study_id, 'paper_original']) else None

            bar_colors = [QUERY_COLORS[i % len(QUERY_COLORS)] for i in range(len(query_labels))]
            bars = ax.bar(query_labels, query_values, color=bar_colors, alpha=0.9, edgecolor='white', width=0.65)

            if paper_value is not None:
                ax.axhline(paper_value, color='#1F3864', linewidth=2.0, linestyle='-')
            else:
                ax.text(
                    0.98,
                    0.95,
                    'Paper: N/A',
                    transform=ax.transAxes,
                    ha='right',
                    va='top',
                    fontsize=8.5,
                    color='#555555',
                    bbox={
                        'boxstyle': 'round,pad=0.18',
                        'facecolor': 'white',
                        'edgecolor': '#CCCCCC',
                        'alpha': 0.9,
                    },
                )

            ceiling = max(query_values + [paper_value or 0, 1])
            ax.set_ylim(0, ceiling * 1.24)

            label_offset = max(ceiling * 0.015, 18)
            for bar, label in zip(bars, [format_count(value) for value in query_values]):
                height = bar.get_height()
                if height <= 0:
                    continue
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + label_offset,
                    label,
                    ha='center',
                    va='bottom',
                    fontsize=9,
                    fontweight='semibold',
                    color='#222222',
                    clip_on=False,
                    bbox={
                        'boxstyle': 'round,pad=0.18',
                        'facecolor': 'white',
                        'edgecolor': 'none',
                        'alpha': 0.9,
                    },
                )

            ax.set_title(study_id.replace('_Paper', '').replace('_', '\n'), fontsize=10.5, fontweight='bold')
            ax.set_ylabel('Articles' if index % ncols == 0 else '', fontsize=8)
            ax.yaxis.set_major_formatter(
                mtick.FuncFormatter(lambda value, _: f"{int(value / 1000)}k" if value >= 1000 else f"{int(value)}")
            )
            ax.tick_params(axis='both', labelsize=9)
            ax.grid(axis='y', alpha=0.3, linestyle=':')
            ax.set_axisbelow(True)

        for index in range(len(studies), len(axes)):
            axes[index].set_visible(False)

        legend_handles = [
            mpatches.Patch(facecolor=QUERY_COLORS[i % len(QUERY_COLORS)], alpha=0.9, label=label)
            for i, label in enumerate(query_labels)
        ] + [
            Line2D([0], [0], color='#1F3864', linewidth=2.0, linestyle='-', label='Original paper count'),
        ]

        fig.legend(
            handles=legend_handles,
            loc='lower center',
            ncol=min(4, len(legend_handles)),
            fontsize=9,
            bbox_to_anchor=(0.5, -0.03),
            framealpha=0.9,
            title='Bars are latest COMBINED per-query counts; line is the original paper count',
            title_fontsize=9,
        )
        fig.suptitle(
            'Per-Query Retrieval vs Original Paper Count',
            fontsize=12,
            fontweight='bold',
            y=1.01,
        )
        plt.tight_layout(rect=[0, 0.05, 1, 1])

        query_path = self.output_dir / 'retrieval_comparison_queries.png'
        fig.savefig(query_path, bbox_inches='tight', dpi=300)
        plt.close(fig)
        figures.append(query_path)
        logger.info(f"Created per-query retrieval comparison chart: {query_path.name}")

        return figures


def generate_visualizations(
    base_dir: Path,
    data_file: Path = None,
    output_dir: Path = None
) -> List[Path]:
    """
    Generate all visualizations for cross-study analysis.
    
    Args:
        base_dir: Base directory of the project
        data_file: Path to all_studies.json (default: cross_study_validation/data/all_studies.json)
        output_dir: Output directory for figures (default: cross_study_validation/reports/figures)
    
    Returns:
        List of paths to generated figures
    """
    if data_file is None:
        data_file = base_dir / 'cross_study_validation' / 'data' / 'all_studies.json'
    
    if output_dir is None:
        output_dir = base_dir / 'cross_study_validation' / 'reports' / 'figures'
    
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_file}")
    
    generator = VisualizationGenerator(data_file, output_dir)
    return generator.generate_all()


if __name__ == '__main__':
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get base directory
    if len(sys.argv) > 1:
        base_dir = Path(sys.argv[1])
    else:
        base_dir = Path(__file__).parent.parent.parent
    
    # Generate visualizations
    try:
        figures = generate_visualizations(base_dir)
        print(f"\nSuccessfully generated {len(figures)} figures:")
        for fig in figures:
            print(f"  - {fig}")
    except Exception as e:
        print(f"Error generating visualizations: {e}")
        sys.exit(1)
