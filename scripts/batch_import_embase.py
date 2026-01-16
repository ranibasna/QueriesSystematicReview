#!/usr/bin/env python3
"""
Batch import multiple Embase CSV exports for a study.

This script automates importing multiple Embase queries at once, matching the
structure of automated PubMed/Scopus/WOS queries.

Usage:
  python scripts/batch_import_embase.py \
    --study sleep_apnea \
    --csvs embase_query1.csv embase_query2.csv embase_query3.csv ... \
    --queries-file studies/sleep_apnea/embase_queries.txt

Or with a manifest file:
  python scripts/batch_import_embase.py \
    --study sleep_apnea \
    --manifest studies/sleep_apnea/embase_manifest.txt
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple
import subprocess


def read_queries_from_file(queries_file: Path) -> List[str]:
    """
    Read queries from a text file (same format as queries.txt).
    Blank lines separate queries, # lines are comments.
    Only lines starting with # Query are included (query descriptions).
    """
    with open(queries_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    queries = []
    current_query = []
    
    for line in content.splitlines():
        line_stripped = line.strip()
        
        # Skip empty lines and treat them as separators
        if not line_stripped:
            if current_query:
                queries.append('\n'.join(current_query))
                current_query = []
            continue
        
        # Only include query-specific comments (# Query X:), skip file header comments
        if line_stripped.startswith('#'):
            if line_stripped.startswith('# Query'):
                current_query.append(line_stripped)
            continue
        
        # This is the actual query line
        current_query.append(line_stripped)
    
    # Don't forget the last query
    if current_query:
        queries.append('\n'.join(current_query))
    
    return queries


def read_manifest(manifest_file: Path) -> List[Tuple[Path, str]]:
    """
    Read a manifest file with format:
    csv_file.csv|Query text here
    csv_file2.csv|Another query text
    """
    pairs = []
    with open(manifest_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '|' not in line:
                print(f"Warning: Line {line_num} missing '|' separator, skipping", file=sys.stderr)
                continue
            
            csv_path, query = line.split('|', 1)
            pairs.append((Path(csv_path.strip()), query.strip()))
    
    return pairs


def import_single_csv(csv_path: Path, output_path: Path, query: str) -> bool:
    """Import a single CSV using import_embase_manual.py"""
    cmd = [
        sys.executable,
        'scripts/import_embase_manual.py',
        '--input', str(csv_path),
        '--output', str(output_path),
        '--query', query
    ]
    
    print(f"\n{'='*60}")
    print(f"Importing: {csv_path.name}")
    print(f"Output:    {output_path.name}")
    print(f"Query:     {query[:80]}..." if len(query) > 80 else f"Query:     {query}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print(f"✅ Successfully imported {csv_path.name}")
        return True
    else:
        print(f"❌ Failed to import {csv_path.name}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Batch import multiple Embase CSV exports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--study', required=True,
                       help='Study name (e.g., sleep_apnea)')
    
    # Option 1: Separate CSV and queries files
    parser.add_argument('--csvs', nargs='+',
                       help='List of CSV files to import')
    parser.add_argument('--queries-file',
                       help='Text file with queries (same format as queries.txt)')
    
    # Option 2: Manifest file
    parser.add_argument('--manifest',
                       help='Manifest file with CSV|query pairs')
    
    args = parser.parse_args()
    
    study_dir = Path('studies') / args.study
    if not study_dir.exists():
        print(f"Error: Study directory not found: {study_dir}", file=sys.stderr)
        return 1
    
    # Determine CSV-query pairs
    pairs: List[Tuple[Path, str]] = []
    
    if args.manifest:
        # Read from manifest file
        pairs = read_manifest(Path(args.manifest))
    elif args.csvs and args.queries_file:
        # Match CSVs with queries from file
        csv_paths = [Path(csv) for csv in args.csvs]
        queries = read_queries_from_file(Path(args.queries_file))
        
        if len(csv_paths) != len(queries):
            print(f"⚠️  Warning: Number of CSVs ({len(csv_paths)}) doesn't match number of queries ({len(queries)})", 
                  file=sys.stderr)
            print(f"   This is normal if some queries returned zero results on Embase.", file=sys.stderr)
            
            if len(csv_paths) > len(queries):
                print(f"   Error: More CSVs than queries - please check your files.", file=sys.stderr)
                return 1
            else:
                # Fewer CSVs than queries - assume missing CSVs had zero results
                print(f"   Will import {len(csv_paths)} queries and skip {len(queries) - len(csv_paths)} query(ies) with no results.", file=sys.stderr)
                # Use only the first N queries to match the CSVs
                queries = queries[:len(csv_paths)]
        
        pairs = list(zip(csv_paths, queries))
    else:
        print("Error: Must provide either --manifest or both --csvs and --queries-file", file=sys.stderr)
        parser.print_help()
        return 1
    
    if not pairs:
        print("Error: No CSV-query pairs to process", file=sys.stderr)
        return 1
    
    print(f"\n📋 Batch Import Plan")
    print(f"Study: {args.study}")
    print(f"Total queries to import: {len(pairs)}")
    print(f"Output directory: {study_dir}/")
    
    # Import all CSVs
    success_count = 0
    failed = []
    
    for i, (csv_path, query) in enumerate(pairs, 1):
        if not csv_path.exists():
            print(f"\n❌ CSV file not found: {csv_path}", file=sys.stderr)
            failed.append(csv_path.name)
            continue
        
        # Generate output filename
        output_path = study_dir / f"embase_query{i}.json"
        
        if import_single_csv(csv_path, output_path, query):
            success_count += 1
        else:
            failed.append(csv_path.name)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Batch Import Summary")
    print(f"{'='*60}")
    print(f"✅ Successfully imported: {success_count}/{len(pairs)}")
    if failed:
        print(f"❌ Failed: {len(failed)}")
        for fname in failed:
            print(f"   - {fname}")
    
    print(f"\n📁 Output files:")
    for json_file in sorted(study_dir.glob('embase_query*.json')):
        print(f"   {json_file}")
    
    print(f"\n📋 Next steps:")
    print(f"   1. Verify imported files in studies/{args.study}/")
    print(f"   2. Run aggregation:")
    print(f"      python scripts/aggregate_queries.py \\")
    print(f"        --inputs benchmark_outputs/{args.study}/details_*.json \\")
    print(f"                 studies/{args.study}/embase_*.json \\")
    print(f"        --outdir aggregates/{args.study}")
    
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
