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
import hashlib
import json
import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple
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


def create_placeholder_json(output_path: Path, query: str) -> None:
    """Create an embase_queryN.json with zero records for a skipped/excluded query.

    The JSON is keyed by the SHA-256 hash of the query text — identical to what
    import_embase_manual.py would produce — so that EmbaseLocalProvider can find
    the entry at runtime and return (set(), set(), 0) without a hash-miss warning.
    Keeping the placeholder means query numbering stays aligned with PubMed/Scopus/WoS.
    """
    query_hash = hashlib.sha256(query.encode()).hexdigest()
    payload = {
        query_hash: {
            "query": query,
            "provider": "embase_manual",
            "results_count": 0,
            "retrieved_dois": [],
            "retrieved_pmids": [],
            "pmids": [],
            "records": [],
            "source": "placeholder",
            "note": "Zero-record placeholder — query excluded intentionally (e.g. too many results).",
        }
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)


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
    parser.add_argument(
        '--placeholder-indices', nargs='+', type=int, metavar='N',
        help=(
            'Query indices (1-based) for which NO CSV is available. '
            'An empty placeholder JSON is written for each so that query numbering '
            'stays aligned with the other databases. '
            'The remaining CSVs are assigned to the other indices in order. '
            'Example: --placeholder-indices 1  (skip query 1, import CSVs for 2-6)'
        ),
    )

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
        placeholder_indices: Set[int] = set(args.placeholder_indices or [])

        if placeholder_indices:
            # Validate placeholder indices are within range
            for idx in sorted(placeholder_indices):
                if idx < 1 or idx > len(queries):
                    print(
                        f"❌ Error: --placeholder-indices {idx} is out of range "
                        f"(valid: 1–{len(queries)})",
                        file=sys.stderr,
                    )
                    return 1
            active_indices = [i for i in range(1, len(queries) + 1) if i not in placeholder_indices]
            if len(csv_paths) != len(active_indices):
                print(
                    f"❌ Error: {len(csv_paths)} CSV file(s) provided but "
                    f"{len(active_indices)} non-placeholder quer{'y' if len(active_indices)==1 else 'ies'} "
                    f"(total={len(queries)}, placeholders={sorted(placeholder_indices)}). "
                    "These numbers must match.",
                    file=sys.stderr,
                )
                return 1
            # pairs carries (csv_path_or_None, query_text, output_index)
            # We handle placeholders in the loop below; store as (Path|None, str, int)
            indexed_pairs: List[Tuple] = []
            csv_iter = iter(csv_paths)
            for idx in range(1, len(queries) + 1):
                q = queries[idx - 1]
                if idx in placeholder_indices:
                    indexed_pairs.append((None, q, idx))
                else:
                    indexed_pairs.append((next(csv_iter), q, idx))
        else:
            # Legacy: no placeholder indices — original behaviour with alignment check
            if len(csv_paths) != len(queries):
                print(
                    f"⚠️  Warning: Number of CSVs ({len(csv_paths)}) doesn't match "
                    f"number of queries ({len(queries)})",
                    file=sys.stderr,
                )
                print(
                    "   If a query returned no results on Embase, use "
                    "--placeholder-indices N to skip it while keeping numbering aligned.",
                    file=sys.stderr,
                )
                if len(csv_paths) > len(queries):
                    print("   Error: More CSVs than queries — please check your files.",
                          file=sys.stderr)
                    return 1
                else:
                    print(
                        f"   Matching first {len(csv_paths)} queries to CSVs. "
                        "Note: this may misalign query numbering — prefer --placeholder-indices.",
                        file=sys.stderr,
                    )
                    queries = queries[:len(csv_paths)]
            indexed_pairs = [(csv, q, i) for i, (csv, q) in enumerate(zip(csv_paths, queries), 1)]
    else:
        print("Error: Must provide either --manifest or both --csvs and --queries-file", file=sys.stderr)
        parser.print_help()
        return 1
    
    # At this point either 'pairs' (manifest path) or 'indexed_pairs' (csv+queries path) is set.
    # Normalise to indexed_pairs for the loop below.
    if args.manifest:
        if not pairs:
            print("Error: No CSV-query pairs to process", file=sys.stderr)
            return 1
        indexed_pairs = [(csv, q, i) for i, (csv, q) in enumerate(pairs, 1)]
    elif not indexed_pairs:  # type: ignore[possibly-undefined]
        print("Error: No CSV-query pairs to process", file=sys.stderr)
        return 1

    placeholder_count = sum(1 for (csv, _, _) in indexed_pairs if csv is None)
    real_count = len(indexed_pairs) - placeholder_count

    print(f"\n📋 Batch Import Plan")
    print(f"Study: {args.study}")
    print(f"Total queries: {len(indexed_pairs)} "
          f"({real_count} to import, {placeholder_count} placeholder{'s' if placeholder_count!=1 else ''})")
    print(f"Output directory: {study_dir}/")
    if placeholder_count:
        ph_indices = [idx for (csv, _, idx) in indexed_pairs if csv is None]
        print(f"Placeholder indices (zero-record JSON): {ph_indices}")

    # Import all CSVs
    success_count = 0
    failed = []

    for csv_path, query, output_index in indexed_pairs:
        output_path = study_dir / f"embase_query{output_index}.json"

        if csv_path is None:
            # Placeholder: write an empty JSON with the correct hash key
            create_placeholder_json(output_path, query)
            print(f"\n📄 Placeholder written for query {output_index}: {output_path.name}")
            success_count += 1
            continue

        if not csv_path.exists():
            print(f"\n❌ CSV file not found: {csv_path}", file=sys.stderr)
            failed.append(csv_path.name)
            continue

        if import_single_csv(csv_path, output_path, query):
            success_count += 1
        else:
            failed.append(csv_path.name)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Batch Import Summary")
    print(f"{'='*60}")
    print(f"✅ Succeeded: {success_count}/{len(indexed_pairs)} "
          f"({placeholder_count} placeholder{'s' if placeholder_count!=1 else ''} included)")
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
