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

        # Check if it's vertical format (no header row, field names in first column).
        # Use csv.reader to parse the first line so quoted commas in the title value
        # don't cause false negatives (the raw comma count check was unreliable).
        # Guard: vertical rows have ≤3 CSV fields (field_name + value + optional extra);
        # wide horizontal header rows (many columns) are excluded by len(_first_row) <= 3.
        _first_row = next(csv.reader([first_line]))
        _is_vertical = (
            len(_first_row) >= 1
            and _first_row[0].strip().strip('"').upper() == 'TITLE'
            and len(_first_row) <= 3
        )
        if _is_vertical:
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

                # W4.1: Extract first author from AUTHOR NAMES field.
                # The vertical-format row is: ["AUTHOR NAMES", "LastName I.", ...]
                # row[1] is the first author entry in the CSV column sequence.
                elif field_name == 'AUTHOR NAMES':
                    # row[1] is already consumed into field_value by the reader;
                    # take the first space-delimited token as the last name.
                    first_entry = field_value  # e.g. "Smith J." or "van den Berg A."
                    if first_entry:
                        # For "LastName Initials." format → split on space, take all
                        # except trailing initials (last dot-terminated token).
                        # Simplest robust approach: everything up to the last space
                        # chunk that contains a dot is considered a suffix/initial,
                        # so we take the first token which is always the last name.
                        last_name = first_entry.split()[0].rstrip('.') if first_entry.split() else first_entry
                        if last_name:
                            current_record['first_author'] = last_name

                # W4.1: Extract publication year (vertical format: YEAR field).
                elif field_name in ('YEAR', 'PUBLICATION YEAR', 'PY'):
                    if field_value and field_value.strip().isdigit():
                        current_record['year'] = int(field_value.strip())

                # W4.1: Extract journal/source title (vertical format).
                elif field_name in ('SOURCE', 'JOURNAL', 'JOURNAL TITLE', 'PUBLICATION TITLE', 'SOURCE TITLE'):
                    if field_value and field_value.strip():
                        current_record['journal'] = field_value.strip()
            
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

                # W4.1: Extract first author from author columns.
                # Embase horizontal exports typically put all authors in one cell,
                # separated by semicolons or commas.  Take the first entry and
                # extract the last name (everything before the first comma or the
                # first space-delimited token that is not an initial).
                for col in ['Author Names', 'AUTHOR NAMES', 'Authors', 'Author(s)', 'First Author']:
                    if col in row and row[col]:
                        authors_str = row[col].strip()
                        # First author: first semicolon-delimited segment
                        first_entry = authors_str.split(';')[0].strip()
                        if first_entry:
                            # Remove trailing period and take last-name token
                            last_name = first_entry.split()[0].rstrip('.') if first_entry.split() else first_entry
                            if last_name:
                                record['first_author'] = last_name
                        break

                # W4.1: Extract publication year (horizontal format).
                for col in ['Year', 'Publication Year', 'PY', 'YEAR', 'year']:
                    if col in row and row[col]:
                        yr = str(row[col]).strip()
                        if yr.isdigit():
                            record['year'] = int(yr)
                        break

                # W4.1: Extract journal/source title (horizontal format).
                for col in ['Source title', 'Source Title', 'Journal', 'JOURNAL',
                            'Publication Title', 'Journal Title', 'Source']:
                    if col in row and row[col]:
                        jn = row[col].strip()
                        if jn:
                            record['journal'] = jn
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
