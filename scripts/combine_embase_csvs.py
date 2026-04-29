#!/usr/bin/env python3
"""
Combine multiple Embase CSV files into a single CSV file.
Handles both vertical format (field-value pairs) and standard CSV format.
"""

import csv
import argparse
from pathlib import Path
from typing import Dict, List, Set


def parse_vertical_format_csv(csv_path: str) -> List[Dict]:
    """
    Parse Embase CSV in vertical format (field_name, value per row).
    Detects record boundaries and returns list of records.
    """
    records = []
    current_record = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        for row in reader:
            if len(row) < 2:
                continue
            
            field_name = row[0].strip().upper()
            field_value = row[1].strip() if len(row) > 1 else ''
            
            # Start of new record when we see TITLE again (and we have a previous record)
            if field_name == 'TITLE' and current_record:
                records.append(current_record)
                current_record = {}
            
            # Store field in current record
            if field_value:
                current_record[field_name] = field_value
        
        # Don't forget the last record
        if current_record:
            records.append(current_record)
    
    return records


def deduplicate_records(records: List[Dict]) -> List[Dict]:
    """
    Remove duplicate records by checking PMID and DOI.
    Keeps first occurrence of each unique record.
    """
    seen = set()
    deduped = []
    
    for record in records:
        # Create a unique key from PMID or DOI (prioritize PMID)
        key = None
        if 'MEDLINE PMID' in record:
            key = ('pmid', record['MEDLINE PMID'])
        elif 'DOI' in record:
            key = ('doi', record['DOI'])
        elif 'TITLE' in record:
            key = ('title', record['TITLE'])
        
        if key and key not in seen:
            seen.add(key)
            deduped.append(record)
        elif not key:
            # If no identifiable key, include anyway
            deduped.append(record)
    
    return deduped


def combine_csv_files(input_files: List[str], output_file: str, deduplicate: bool = True):
    """
    Combine multiple Embase CSV files into one.
    
    Args:
        input_files: List of input CSV file paths
        output_file: Path to output combined CSV file
        deduplicate: Whether to remove duplicates (default True)
    """
    all_records = []
    
    # Parse all input files
    for input_file in input_files:
        print(f"Reading {input_file}...")
        records = parse_vertical_format_csv(input_file)
        all_records.extend(records)
        print(f"  Found {len(records)} records")
    
    print(f"\nTotal records before deduplication: {len(all_records)}")
    
    # Deduplicate if requested
    if deduplicate:
        all_records = deduplicate_records(all_records)
        print(f"Total records after deduplication: {len(all_records)}")
    
    # Write combined CSV
    if all_records:
        # Get all unique field names
        all_fields = set()
        for record in all_records:
            all_fields.update(record.keys())
        
        all_fields = sorted(list(all_fields))
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=all_fields)
            writer.writeheader()
            writer.writerows(all_records)
        
        print(f"\nCombined CSV saved to: {output_file}")
        print(f"Fields included: {', '.join(all_fields)}")
    else:
        print("No records found to write!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Combine multiple Embase CSV files into one'
    )
    parser.add_argument(
        'input_dir',
        help='Directory containing Embase CSV files to combine'
    )
    parser.add_argument(
        '--output',
        help='Output CSV file path (default: <input_dir>/combined_embase.csv)'
    )
    parser.add_argument(
        '--no-deduplicate',
        action='store_true',
        help='Do not remove duplicate records'
    )
    
    args = parser.parse_args()
    
    # Find all CSV files in input directory
    input_dir = Path(args.input_dir)
    csv_files = sorted(input_dir.glob('*.csv'))
    
    if not csv_files:
        print(f"No CSV files found in {input_dir}")
        exit(1)
    
    print(f"Found {len(csv_files)} CSV files:")
    for f in csv_files:
        print(f"  - {f.name}")
    
    # Determine output file
    output_file = args.output or str(input_dir / 'combined_embase.csv')
    
    # Combine files
    combine_csv_files(
        [str(f) for f in csv_files],
        output_file,
        deduplicate=not args.no_deduplicate
    )
