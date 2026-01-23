"""
Visualization generation for cross-study validation analysis.

Generates publication-quality figures including:
- Box plots for metric distributions
- Bar charts for strategy comparisons  
- Scatter plots for tradeoff analysis
- Heatmaps for domain-specific performance
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import logging

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np

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
