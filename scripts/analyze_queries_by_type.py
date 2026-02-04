#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze Query Performance by Type Across Databases

This script aggregates query performance metrics by query type (e.g., High-recall,
Balanced, High-precision) across all databases (PubMed, Scopus, WOS, Embase).

Usage:
    python scripts/analyze_queries_by_type.py <STUDY_NAME> [--query-types TYPE1,TYPE2,...]
    
Examples:
    # Show all query types
    python scripts/analyze_queries_by_type.py Medeiros_2023
    
    # Show specific query types only
    python scripts/analyze_queries_by_type.py Medeiros_2023 --query-types "High-recall,Balanced"
    
    # Export to CSV
    python scripts/analyze_queries_by_type.py Medeiros_2023 --output results.csv
"""

import argparse
import pandas as pd
import sys
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple

def extract_query_type_from_comment(comment: str) -> Optional[str]:
    """
    Extract query type from comment line.
    
    Examples:
        "# Query 1: High-recall - Broad MeSH terms..." -> "High-recall"
        "# High-recall: Broad search..." -> "High-recall"
        "# Balanced - Mix of MeSH..." -> "Balanced"
        "# Micro-variant 1 (Filter-based)" -> "Micro-variant 1"
    """
    if not comment or not isinstance(comment, str):
        return None
    
    # Remove leading # and whitespace
    comment = comment.lstrip('#').strip()
    
    # Pattern 1: "Query N: TYPE - description"
    # Match everything after "Query N:" until we hit " - " or end of string
    match = re.match(r'Query\s+\d+\s*:\s*(.+?)(?:\s+-\s+|\s*$)', comment, re.IGNORECASE)
    if match:
        query_type = match.group(1).strip()
        return query_type
    
    # Pattern 2: "TYPE - description" or "TYPE: description" (no "Query N:")
    # Match everything before " - " or ": "
    match = re.match(r'^(.+?)(?:\s+[-:]\s+|\s*$)', comment)
    if match:
        query_type = match.group(1).strip()
        # Exclude common non-type words
        if query_type.lower() not in ['note', 'notes', 'important', 'warning', 'example', 'examples']:
            return query_type
    
    return None

def parse_query_files_for_types(study_dir: Path) -> Dict[int, Dict[str, str]]:
    """
    Parse all query files to extract query types for each database.
    
    Returns:
        Dict mapping query_num -> {database: query_type}
    """
    query_types = {}
    
    query_files = {
        'pubmed': study_dir / 'queries.txt',
        'scopus': study_dir / 'queries_scopus.txt',
        'wos': study_dir / 'queries_wos.txt',
        'embase': study_dir / 'queries_embase.txt',
    }
    
    for db_name, query_file in query_files.items():
        if not query_file.exists():
            continue
        
        with open(query_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        query_num = 0
        current_comment = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#'):
                current_comment = line
                continue
            
            # Non-empty, non-comment line = actual query
            if line and not line.startswith('#'):
                query_num += 1
                
                if current_comment:
                    query_type = extract_query_type_from_comment(current_comment)
                    if query_type:
                        if query_num not in query_types:
                            query_types[query_num] = {}
                        query_types[query_num][db_name] = query_type
                
                current_comment = None
    
    return query_types

def aggregate_by_query_type(
    per_db_csv: Path,
    query_types: Dict[int, Dict[str, str]],
    filter_types: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Aggregate per-database metrics by query type.
    
    Args:
        per_db_csv: Path to summary_per_database_*.csv
        query_types: Query type mapping from parse_query_files_for_types()
        filter_types: Only include these query types (None = all)
    
    Returns:
        DataFrame with aggregated metrics by query type
    """
    df = pd.read_csv(per_db_csv)
    
    # Filter out COMBINED rows (we'll compute our own)
    df = df[df['database'] != 'COMBINED'].copy()
    
    # Add query type column
    df['query_type'] = df.apply(
        lambda row: query_types.get(row['query_num'], {}).get(row['database'], 'Unknown'),
        axis=1
    )
    
    # Filter by requested types
    if filter_types:
        df = df[df['query_type'].isin(filter_types)]
    
    if df.empty:
        print(f"⚠️  No data found for query types: {filter_types}", file=sys.stderr)
        return pd.DataFrame()
    
    # Group by query_num and query_type, aggregate across databases
    aggregated = []
    
    for (query_num, query_type), group in df.groupby(['query_num', 'query_type']):
        databases = sorted(group['database'].unique())
        
        # Collect all PMIDs across databases (deduped)
        # Note: This is approximate since we don't have actual PMID lists here
        # We use the COMBINED row if available, otherwise sum results_count
        
        combined_row = {
            'query_num': query_num,
            'query_type': query_type,
            'databases': '+'.join(databases),
            'num_databases': len(databases),
            'total_results': int(group['results_count'].sum()),  # Total before dedup
            'max_TP': int(group['TP'].max()),  # Best case across databases
            'max_recall': float(group['recall'].max()),  # Best recall achieved
            'avg_recall': float(group['recall'].mean()),  # Average recall
            'gold_size': int(group['gold_size'].iloc[0]),  # Should be same for all
        }
        
        # Add per-database breakdown
        for _, row in group.iterrows():
            db = row['database']
            combined_row[f'{db}_results'] = int(row['results_count'])
            combined_row[f'{db}_TP'] = int(row['TP'])
            combined_row[f'{db}_recall'] = float(row['recall'])
        
        aggregated.append(combined_row)
    
    result_df = pd.DataFrame(aggregated)
    
    # Sort by query_num
    result_df = result_df.sort_values('query_num')
    
    return result_df

def format_output(df: pd.DataFrame, detailed: bool = False) -> str:
    """
    Format DataFrame for console output.
    """
    if df.empty:
        return "No results to display."
    
    output = []
    output.append("=" * 100)
    output.append("Query Performance Aggregated by Type Across All Databases")
    output.append("=" * 100)
    output.append("")
    
    for _, row in df.iterrows():
        query_type = row['query_type']
        query_num = int(row['query_num'])
        databases = row['databases']
        num_dbs = int(row['num_databases'])
        
        output.append(f"Query {query_num}: {query_type}")
        output.append("-" * 80)
        output.append(f"  Databases: {databases} ({num_dbs} total)")
        output.append(f"  Total Results (before dedup): {int(row['total_results']):,}")
        output.append(f"  Best Recall Achieved: {row['max_recall']:.1%} ({int(row['max_TP'])}/{int(row['gold_size'])} gold studies)")
        output.append(f"  Average Recall: {row['avg_recall']:.1%}")
        
        if detailed:
            output.append("")
            output.append("  Per-Database Breakdown:")
            
            # Extract database-specific columns
            for col in df.columns:
                if col.endswith('_recall'):
                    db_name = col.replace('_recall', '')
                    if f'{db_name}_results' in row and pd.notna(row[f'{db_name}_results']):
                        results = int(row[f'{db_name}_results'])
                        tp = int(row[f'{db_name}_TP'])
                        recall = float(row[f'{db_name}_recall'])
                        output.append(f"    • {db_name.upper()}: {results:,} results, {tp} TP, {recall:.1%} recall")
        
        output.append("")
    
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(
        description='Analyze query performance by type across databases',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show all query types with summary
  python scripts/analyze_queries_by_type.py Medeiros_2023
  
  # Show detailed breakdown for specific types
  python scripts/analyze_queries_by_type.py Medeiros_2023 --query-types "High-recall,Balanced" --detailed
  
  # Export to CSV
  python scripts/analyze_queries_by_type.py Medeiros_2023 --output query_type_analysis.csv
        """
    )
    
    parser.add_argument(
        'study_name',
        help='Study name (e.g., Medeiros_2023)'
    )
    
    parser.add_argument(
        '--query-types',
        help='Comma-separated list of query types to analyze (e.g., "High-recall,Balanced"). Default: all types'
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed per-database breakdown'
    )
    
    parser.add_argument(
        '--output',
        '-o',
        help='Output CSV file path (optional). If not specified, prints to console'
    )
    
    parser.add_argument(
        '--benchmark-dir',
        default='benchmark_outputs',
        help='Benchmark outputs directory (default: benchmark_outputs)'
    )
    
    args = parser.parse_args()
    
    # Validate paths
    study_dir = Path('studies') / args.study_name
    if not study_dir.exists():
        print(f"❌ Error: Study directory not found: {study_dir}", file=sys.stderr)
        sys.exit(1)
    
    benchmark_dir = Path(args.benchmark_dir) / args.study_name
    if not benchmark_dir.exists():
        print(f"❌ Error: Benchmark directory not found: {benchmark_dir}", file=sys.stderr)
        print(f"   Run the workflow first: bash scripts/run_complete_workflow.sh {args.study_name}", file=sys.stderr)
        sys.exit(1)
    
    # Find latest per-database summary
    per_db_files = sorted(benchmark_dir.glob('summary_per_database_*.csv'))
    if not per_db_files:
        print(f"❌ Error: No per-database summary found in {benchmark_dir}", file=sys.stderr)
        print(f"   Expected: summary_per_database_*.csv", file=sys.stderr)
        sys.exit(1)
    
    latest_per_db = per_db_files[-1]
    print(f"📊 Analyzing: {latest_per_db.name}", file=sys.stderr)
    print("", file=sys.stderr)
    
    # Parse query types from query files
    print("📋 Extracting query types from query files...", file=sys.stderr)
    query_types = parse_query_files_for_types(study_dir)
    
    if not query_types:
        print("⚠️  Warning: Could not extract query types from query files", file=sys.stderr)
        print("   Query files should have comments like: # Query 1: High-recall - description", file=sys.stderr)
    else:
        print(f"   Found query types for {len(query_types)} queries", file=sys.stderr)
    
    print("", file=sys.stderr)
    
    # Parse filter types
    filter_types = None
    if args.query_types:
        filter_types = [t.strip() for t in args.query_types.split(',')]
        print(f"🔍 Filtering for query types: {', '.join(filter_types)}", file=sys.stderr)
        print("", file=sys.stderr)
    
    # Aggregate data
    result_df = aggregate_by_query_type(latest_per_db, query_types, filter_types)
    
    if result_df.empty:
        sys.exit(1)
    
    # Output
    if args.output:
        result_df.to_csv(args.output, index=False)
        print(f"✅ Saved to: {args.output}", file=sys.stderr)
        print("", file=sys.stderr)
        
        # Also print summary to console
        summary = format_output(result_df, detailed=False)
        print(summary)
    else:
        # Print to console
        output = format_output(result_df, detailed=args.detailed)
        print(output)

if __name__ == '__main__':
    main()
