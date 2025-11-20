#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhance Gold Standard with DOIs

This script fetches DOIs from PubMed for a list of PMIDs in a gold standard CSV file
and creates an enhanced version with both PMIDs and DOIs.

Usage:
    python enhance_gold_standard.py input.csv output.csv [--email your@email.com]

Input CSV format:
    pmid
    32045010
    31464350
    ...

Output CSV format:
    pmid,doi
    32045010,10.1002/lary.28558
    31464350,10.1002/ana.25564
    ...

Requirements:
    - biopython (pip install biopython)
    - NCBI Entrez API access (free, no key required but email recommended)
"""

import csv
import sys
import time
import argparse
from typing import Dict, List, Optional
from pathlib import Path

try:
    from Bio import Entrez
except ImportError:
    print("ERROR: Biopython is required. Install with: pip install biopython", file=sys.stderr)
    sys.exit(1)

RATE_LIMIT_SECONDS = 0.34  # NCBI rate limit without API key


def fetch_doi_for_pmid(pmid: str, verbose: bool = True) -> Optional[str]:
    """
    Fetch DOI from PubMed for a given PMID.
    
    Args:
        pmid: PubMed ID
        verbose: Print progress messages
    
    Returns:
        DOI string if found, None otherwise
    """
    try:
        handle = Entrez.efetch(db='pubmed', id=pmid, rettype='medline', retmode='xml')
        records = Entrez.read(handle)
        handle.close()
        time.sleep(RATE_LIMIT_SECONDS)
        
        for article in records.get('PubmedArticle', []):
            # Method 1: Check ArticleIdList for DOI
            article_ids = article.get('PubmedData', {}).get('ArticleIdList', [])
            for article_id in article_ids:
                attrs = getattr(article_id, 'attributes', {})
                if attrs.get('IdType') == 'doi':
                    doi = str(article_id).strip()
                    if verbose:
                        print(f"  ✓ PMID {pmid} → DOI: {doi}")
                    return doi
            
            # Method 2: Check ELocationID for DOI
            e_locations = article.get('MedlineCitation', {}).get('Article', {}).get('ELocationID', [])
            for eloc in e_locations:
                attrs = getattr(eloc, 'attributes', {})
                if attrs.get('EIdType') == 'doi':
                    doi = str(eloc).strip()
                    if verbose:
                        print(f"  ✓ PMID {pmid} → DOI: {doi}")
                    return doi
        
        if verbose:
            print(f"  ✗ PMID {pmid} → DOI: NOT FOUND", file=sys.stderr)
        return None
        
    except Exception as e:
        print(f"  ✗ PMID {pmid} → ERROR: {e}", file=sys.stderr)
        return None


def load_gold_pmids(input_path: Path) -> List[str]:
    """
    Load PMIDs from input CSV file.
    
    Args:
        input_path: Path to input CSV file
    
    Returns:
        List of PMIDs
    """
    pmids = []
    
    with open(input_path, 'r') as infile:
        reader = csv.DictReader(infile)
        
        # Detect PMID column name (case-insensitive)
        pmid_column = None
        for field in reader.fieldnames:
            if field.lower() in ('pmid', 'pubmed_id', 'pubmedid'):
                pmid_column = field
                break
        
        if not pmid_column:
            raise ValueError(f"No PMID column found in {input_path}. Expected column name: 'pmid', 'PMID', or 'pubmed_id'")
        
        for row in reader:
            pmid = row[pmid_column].strip()
            if pmid:
                pmids.append(pmid)
    
    return pmids


def enhance_gold_standard(input_path: Path, output_path: Path, email: str, verbose: bool = True):
    """
    Read gold PMIDs and write enhanced version with DOIs.
    
    Args:
        input_path: Input CSV file with PMIDs
        output_path: Output CSV file with PMIDs and DOIs
        email: Email for Entrez API
        verbose: Print progress messages
    """
    # Set Entrez email
    Entrez.email = email
    
    # Load PMIDs
    if verbose:
        print(f"Loading PMIDs from: {input_path}")
    
    pmids = load_gold_pmids(input_path)
    
    if verbose:
        print(f"Found {len(pmids)} PMIDs")
        print(f"\nFetching DOIs from PubMed...")
        print("-" * 70)
    
    # Fetch DOIs
    results = []
    for i, pmid in enumerate(pmids, 1):
        if verbose:
            print(f"[{i}/{len(pmids)}] ", end='')
        
        doi = fetch_doi_for_pmid(pmid, verbose=verbose)
        results.append({
            'pmid': pmid,
            'doi': doi if doi else ''
        })
    
    # Write output
    with open(output_path, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=['pmid', 'doi'])
        writer.writeheader()
        writer.writerows(results)
    
    # Summary
    with_doi = sum(1 for row in results if row['doi'])
    without_doi = len(results) - with_doi
    
    if verbose:
        print("-" * 70)
        print(f"\n✓ Enhanced gold standard written to: {output_path}")
        print(f"\nSummary:")
        print(f"  Total PMIDs: {len(results)}")
        print(f"  PMIDs with DOI: {with_doi} ({with_doi/len(results)*100:.1f}%)")
        print(f"  PMIDs without DOI: {without_doi} ({without_doi/len(results)*100:.1f}%)")
        
        if without_doi > 0:
            print(f"\n⚠ PMIDs without DOI:")
            for row in results:
                if not row['doi']:
                    print(f"    - {row['pmid']}")


def main():
    parser = argparse.ArgumentParser(
        description='Enhance gold standard CSV with DOIs fetched from PubMed',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python enhance_gold_standard.py input.csv output.csv
  
  # With email for NCBI
  python enhance_gold_standard.py input.csv output.csv --email your@email.com
  
  # Quiet mode
  python enhance_gold_standard.py input.csv output.csv --quiet

Input CSV format:
  pmid
  32045010
  31464350
  ...

Output CSV format:
  pmid,doi
  32045010,10.1002/lary.28558
  31464350,10.1002/ana.25564
  ...
        """
    )
    
    parser.add_argument('input', type=Path, help='Input CSV file with PMIDs')
    parser.add_argument('output', type=Path, help='Output CSV file for PMIDs and DOIs')
    parser.add_argument('--email', default='user@example.com', help='Email for NCBI Entrez API (recommended)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress progress messages')
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not args.input.exists():
        print(f"ERROR: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Warn if output exists
    if args.output.exists():
        response = input(f"WARNING: Output file exists: {args.output}\nOverwrite? [y/N] ")
        if response.lower() not in ('y', 'yes'):
            print("Aborted.")
            sys.exit(0)
    
    # Run enhancement
    try:
        enhance_gold_standard(
            args.input, 
            args.output, 
            args.email, 
            verbose=not args.quiet
        )
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
