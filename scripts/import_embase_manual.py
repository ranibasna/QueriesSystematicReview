#!/usr/bin/env python3
"""
Import manually exported Embase results into the workflow.

When you don't have Embase API access but can run queries manually on the Embase website,
this script converts Embase CSV exports to the format expected by the workflow.

Usage:
  1. Run your query on Embase website
  2. Export results as CSV (include: Title, Authors, DOI, PubMed ID if available)
  3. Run this script:
     python scripts/import_embase_manual.py \
       --input embase_export.csv \
       --output studies/sleep_apnea/embase_results.json \
       --query "your query text here"

The output JSON can then be used with aggregate_queries.py or score-sets command.
"""

import argparse
import csv
import json
import hashlib
from pathlib import Path
from typing import Set, List, Dict


def parse_embase_csv(csv_path: str) -> tuple[Set[str], Set[str], List[Dict], int]:
    """
    Parse Embase CSV export and extract DOIs and PMIDs.
    Supports two formats:
    1. Standard CSV with headers (columns: DOI, PMID, Title, etc.)
    2. Vertical format with field-value pairs (field_name, value per row)

    Returns:
        (dois, pmids, records, raw_row_count)
        raw_row_count: number of data rows seen before DOI/PMID filtering.
        A count of 0 means the query genuinely returned no results (empty export).
        A count > 0 with empty dois/pmids means the export is missing the expected columns.
    """
    dois: Set[str] = set()
    pmids: Set[str] = set()
    records: List[Dict] = []
    raw_row_count: int = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        # Read first line to detect format
        first_line = f.readline()
        f.seek(0)

        # Check if it's vertical format (no header row, field names in first column)
        if 'TITLE' in first_line.upper() and first_line.count(',') <= 2:
            # Vertical format: field_name, value
            reader = csv.reader(f)
            current_record = {}

            for row in reader:
                if len(row) < 2:
                    continue
                raw_row_count += 1
                    
                field_name = row[0].strip().upper()
                field_value = row[1].strip() if len(row) > 1 else ''
                
                # Start of new record when we see TITLE again
                if field_name == 'TITLE' and current_record:
                    # Save previous record
                    if 'doi' in current_record or 'pmid' in current_record:
                        records.append(current_record)
                    current_record = {}
                
                # Extract DOI
                if field_name == 'DOI' and field_value and field_value.lower() != 'n/a':
                    current_record['doi'] = field_value
                    dois.add(field_value)
                
                # Extract PMID
                elif 'MEDLINE PMID' in field_name or field_name == 'PMID':
                    if field_value and field_value.isdigit():
                        current_record['pmid'] = field_value
                        pmids.add(field_value)
                
                # Extract title
                elif field_name == 'TITLE':
                    current_record['title'] = field_value
            
            # Don't forget the last record
            if current_record and ('doi' in current_record or 'pmid' in current_record):
                records.append(current_record)
        
        else:
            # Standard horizontal format with DictReader
            reader = csv.DictReader(f)

            for row in reader:
                raw_row_count += 1
                record = {}
                
                # Extract DOI (various possible column names)
                doi = None
                for col in ['DOI', 'doi', 'Digital Object Identifier']:
                    if col in row and row[col]:
                        doi = row[col].strip()
                        if doi and doi.lower() != 'n/a':
                            dois.add(doi)
                            record['doi'] = doi
                            break
                
                # Extract PMID if available
                pmid = None
                for col in ['PubMed ID', 'PMID', 'pmid', 'Medline PMID']:
                    if col in row and row[col]:
                        pmid = str(row[col]).strip()
                        if pmid and pmid.isdigit():
                            pmids.add(pmid)
                            record['pmid'] = pmid
                            break
                
                # Extract title for reference
                for col in ['Title', 'title', 'Article Title', 'TITLE']:
                    if col in row and row[col]:
                        record['title'] = row[col].strip()
                        break
                
                # Only add records that have at least a DOI or PMID
                if doi or pmid:
                    records.append(record)
    
    return dois, pmids, records, raw_row_count


def create_workflow_json(query: str, dois: Set[str], pmids: Set[str], 
                         records: List[Dict], output_path: str):
    """
    Create a JSON file compatible with the workflow's details_*.json format.
    """
    query_hash = hashlib.sha256(query.encode()).hexdigest()
    
    output = {
        query_hash: {
            'query': query,
            'provider': 'embase_manual',
            'results_count': len(dois),
            'retrieved_dois': sorted(dois),
            'retrieved_pmids': sorted(pmids),
            'pmids': sorted(pmids),  # Legacy compatibility
            'records': records,
            'source': 'manual_export',
            'note': 'Manually exported from Embase website and imported via import_embase_manual.py'
        }
    }
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    return query_hash


def main():
    parser = argparse.ArgumentParser(
        description='Import manually exported Embase CSV into workflow format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--input', '-i', required=True,
                       help='Path to Embase CSV export file')
    parser.add_argument('--output', '-o', required=True,
                       help='Path for output JSON file (e.g., studies/*/embase_results.json)')
    parser.add_argument('--query', '-q', required=True,
                       help='The Embase query text you ran (for documentation)')
    
    args = parser.parse_args()
    
    print(f"Reading Embase export from: {args.input}")
    dois, pmids, records, raw_row_count = parse_embase_csv(args.input)

    print(f"\nExtracted:")
    print(f"  - {len(dois)} unique DOIs")
    print(f"  - {len(pmids)} PMIDs (cross-referenced articles)")
    print(f"  - {len(records)} total records")

    if len(dois) == 0 and len(pmids) == 0:
        if raw_row_count == 0:
            # Genuinely empty CSV — the query returned no results on Embase.
            # Create an empty-but-valid JSON placeholder so positional ordering
            # is preserved across all 6 query slots and return success.
            print("\nℹ️  Query returned 0 results on Embase — creating empty JSON placeholder.")
            print("   This query will score Recall=0 / Precision=0 but will not block the workflow.")
            query_hash = create_workflow_json(args.query, set(), set(), [], args.output)
            print(f"\n✅ Created empty JSON placeholder:")
            print(f"   {args.output}")
            print(f"   Query hash: {query_hash[:8]}")
            return 0
        else:
            # CSV has data rows but DOI/PMID columns could not be found — bad export format.
            print(f"\n⚠️  WARNING: No DOIs or PMIDs found!")
            print(f"   CSV has {raw_row_count} data rows but no DOI or PubMed ID column could be extracted.")
            print("   Make sure your CSV export includes DOI and/or PubMed ID columns.")
            return 1
    
    query_hash = create_workflow_json(args.query, dois, pmids, records, args.output)
    
    print(f"\n✅ Created workflow-compatible JSON:")
    print(f"   {args.output}")
    print(f"   Query hash: {query_hash[:8]}")
    
    print(f"\n📋 Next steps:")
    print(f"   1. Use with aggregate_queries.py:")
    print(f"      python scripts/aggregate_queries.py \\")
    print(f"        --inputs benchmark_outputs/study/details_*.json {args.output} \\")
    print(f"        --outdir aggregates/study")
    print(f"\n   2. Or score directly:")
    print(f"      python llm_sr_select_and_score.py \\")
    print(f"        --study-name <study> \\")
    print(f"        score-sets \\")
    print(f"        --sets {args.output} \\")
    print(f"        --gold-csv studies/<study>/gold_pmids.csv \\")
    print(f"        --outdir aggregates_eval")
    
    return 0


if __name__ == '__main__':
    exit(main())
