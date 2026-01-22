#!/usr/bin/env python3
"""
DOI-Based PMID Validation Script

This script validates PMIDs from multiple sources by using DOIs as ground truth.
DOIs are unique identifiers that can reliably resolve to the correct PMID.

Key Features:
- Uses DOIs to verify correct PMIDs via CrossRef/PubMed API
- Identifies which AI source (ChatGPT, Gemini, Sciespace) is more accurate
- Generates a validated gold standard file

Usage:
    python scripts/validate_pmids_by_doi.py ai_2022
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Optional
from io import StringIO

# Try to import optional dependencies
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from Bio import Entrez
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False

PROJECT_ROOT = Path(__file__).parent.parent


def load_csv_with_empty_lines(filepath: Path) -> list[dict]:
    """Load CSV, handling blank lines at start."""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    
    # Skip empty lines
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip():
            start_idx = i
            break
    
    content = ''.join(lines[start_idx:])
    studies = []
    
    reader = csv.DictReader(StringIO(content))
    for row in reader:
        study = {}
        
        # Get all relevant fields
        for col in ['Title', 'title']:
            if col in row and row[col]:
                study['title'] = row[col].strip()
                break
        
        for col in ['PMID', 'pmid']:
            if col in row and row[col]:
                pmid = ''.join(c for c in row[col] if c.isdigit())
                if pmid:
                    study['pmid'] = pmid
                break
        
        for col in ['DOI', 'doi']:
            if col in row and row[col]:
                doi = row[col].strip()
                # Normalize DOI (remove https://doi.org/ prefix if present)
                if doi.startswith('https://doi.org/'):
                    doi = doi[16:]
                elif doi.startswith('http://doi.org/'):
                    doi = doi[15:]
                study['doi'] = doi
                break
        
        for col in ['First Author Year', 'First Author (Date)', 'Authors']:
            if col in row and row[col]:
                study['author_info'] = row[col].strip()
                break
        
        if study.get('doi') or study.get('pmid'):
            studies.append(study)
    
    return studies


def pmid_from_doi_pubmed(doi: str, email: str = None) -> Optional[str]:
    """Look up PMID from DOI using PubMed Entrez API."""
    if not BIOPYTHON_AVAILABLE:
        return None
    
    import os
    Entrez.email = email or os.environ.get('NCBI_EMAIL', 'validate@example.com')
    api_key = os.environ.get('NCBI_API_KEY')
    if api_key:
        Entrez.api_key = api_key
    
    try:
        # Search by DOI
        handle = Entrez.esearch(db='pubmed', term=f'{doi}[DOI]')
        record = Entrez.read(handle)
        handle.close()
        
        id_list = record.get('IdList', [])
        if id_list:
            return id_list[0]
        
        return None
        
    except Exception as e:
        print(f"   ⚠️ Entrez error for {doi}: {e}")
        return None


def validate_pmids_by_doi(sources: dict[str, list[dict]]) -> list[dict]:
    """
    Validate PMIDs across sources using DOIs as ground truth.
    
    Returns list of validated study records with:
    - doi: the DOI
    - correct_pmid: PMID looked up from DOI
    - source_pmids: PMIDs from each source
    - accuracy: which sources got it right
    """
    # First, collect all unique DOIs
    doi_studies = {}
    
    for source_name, studies in sources.items():
        for study in studies:
            doi = study.get('doi', '').lower()
            if not doi:
                continue
            
            if doi not in doi_studies:
                doi_studies[doi] = {
                    'doi': study.get('doi'),  # Original case
                    'title': study.get('title', ''),
                    'author_info': study.get('author_info', ''),
                    'source_pmids': {},
                    'correct_pmid': None
                }
            
            doi_studies[doi]['source_pmids'][source_name] = study.get('pmid', '')
    
    print(f"\n🔍 Found {len(doi_studies)} unique DOIs across all sources")
    print("-" * 60)
    
    # Look up correct PMID for each DOI
    validated = []
    for i, (doi, record) in enumerate(doi_studies.items(), 1):
        print(f"[{i}/{len(doi_studies)}] Looking up DOI: {record['doi'][:40]}...", end=" ")
        
        pmid = pmid_from_doi_pubmed(record['doi'])
        if pmid:
            record['correct_pmid'] = pmid
            print(f"✅ PMID: {pmid}")
        else:
            print("❌ Not found")
        
        # Determine accuracy
        record['accuracy'] = {}
        for source, source_pmid in record['source_pmids'].items():
            if record['correct_pmid']:
                record['accuracy'][source] = source_pmid == record['correct_pmid']
            else:
                record['accuracy'][source] = None
        
        validated.append(record)
        time.sleep(0.35)  # Rate limiting
    
    return validated


def analyze_source_accuracy(validated: list[dict]) -> dict:
    """Analyze accuracy of each source."""
    accuracy = {}
    
    for record in validated:
        if record['correct_pmid'] is None:
            continue
        
        for source, is_correct in record['accuracy'].items():
            if source not in accuracy:
                accuracy[source] = {'correct': 0, 'incorrect': 0, 'missing': 0}
            
            source_pmid = record['source_pmids'].get(source, '')
            if not source_pmid:
                accuracy[source]['missing'] += 1
            elif is_correct:
                accuracy[source]['correct'] += 1
            else:
                accuracy[source]['incorrect'] += 1
    
    # Calculate percentages
    for source, counts in accuracy.items():
        total = counts['correct'] + counts['incorrect']
        if total > 0:
            counts['accuracy_pct'] = counts['correct'] / total * 100
        else:
            counts['accuracy_pct'] = 0.0
    
    return accuracy


def generate_validated_gold_file(
    validated: list[dict],
    output_path: Path,
    preferred_source: str = None
) -> int:
    """Generate gold PMID file using validated PMIDs."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    pmids = set()
    
    for record in validated:
        # Prefer the DOI-validated PMID
        if record['correct_pmid']:
            pmids.add(record['correct_pmid'])
        elif preferred_source and record['source_pmids'].get(preferred_source):
            pmids.add(record['source_pmids'][preferred_source])
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['pmid'])
        for pmid in sorted(pmids, key=int):
            writer.writerow([pmid])
    
    return len(pmids)


def main():
    parser = argparse.ArgumentParser(
        description="Validate PMIDs using DOI lookup as ground truth"
    )
    
    parser.add_argument("study_name", help="Name of the study")
    parser.add_argument("--source-dir", default="pmids_multiple_sources")
    parser.add_argument("--output", default=None)
    parser.add_argument("--json-report", action="store_true")
    
    args = parser.parse_args()
    
    study_dir = PROJECT_ROOT / "studies" / args.study_name
    source_dir = study_dir / args.source_dir
    
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print(f"🔬 DOI-Based PMID Validation: {args.study_name}")
    print(f"{'='*70}")
    
    # Load all sources
    sources = {}
    for csv_file in source_dir.glob("*.csv"):
        filename = csv_file.name.lower()
        if 'gemini' in filename:
            name = 'gemini'
        elif 'final' in filename:
            name = 'chatgpt'
        else:
            name = 'sciespace'
        
        print(f"\n📄 Loading: {csv_file.name} → {name}")
        studies = load_csv_with_empty_lines(csv_file)
        sources[name] = studies
        print(f"   Found {len(studies)} studies with DOI/PMID")
    
    # Validate by DOI
    validated = validate_pmids_by_doi(sources)
    
    # Analyze accuracy
    accuracy = analyze_source_accuracy(validated)
    
    print(f"\n{'='*70}")
    print("📊 SOURCE ACCURACY ANALYSIS")
    print(f"{'='*70}")
    
    for source, counts in sorted(accuracy.items(), key=lambda x: -x[1]['accuracy_pct']):
        print(f"\n   📌 {source.upper()}:")
        print(f"      ✅ Correct: {counts['correct']}")
        print(f"      ❌ Incorrect: {counts['incorrect']}")
        print(f"      ⚪ Missing: {counts['missing']}")
        print(f"      📈 Accuracy: {counts['accuracy_pct']:.1f}%")
    
    # Show discrepancies
    print(f"\n{'='*70}")
    print("⚠️  PMID DISCREPANCIES")
    print(f"{'='*70}")
    
    discrepancy_count = 0
    for record in validated:
        if not record['correct_pmid']:
            continue
        
        incorrect_sources = [s for s, is_correct in record['accuracy'].items() 
                           if is_correct == False]
        if incorrect_sources:
            discrepancy_count += 1
            print(f"\n   📖 DOI: {record['doi']}")
            print(f"      ✅ Correct PMID: {record['correct_pmid']}")
            for source in incorrect_sources:
                wrong_pmid = record['source_pmids'].get(source, 'N/A')
                print(f"      ❌ {source}: {wrong_pmid}")
    
    if discrepancy_count == 0:
        print("\n   🎉 No discrepancies found! All sources agree.")
    
    # Generate output
    output_path = study_dir / (args.output or f"gold_pmids_{args.study_name}.csv")
    
    # Use the most accurate source as fallback
    best_source = max(accuracy.items(), key=lambda x: x[1]['accuracy_pct'])[0] if accuracy else None
    
    print(f"\n📝 Generating validated Gold PMIDs: {output_path}")
    count = generate_validated_gold_file(validated, output_path, best_source)
    print(f"   ✅ Wrote {count} validated PMIDs")
    
    # JSON report
    if args.json_report:
        report_path = study_dir / f"pmid_doi_validation_{args.study_name}.json"
        report = {
            'study_name': args.study_name,
            'source_accuracy': accuracy,
            'validated_records': validated,
            'total_pmids': count
        }
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"📋 JSON report saved: {report_path}")
    
    print(f"\n{'='*70}")
    print("✅ DOI-Based Validation Complete!")
    print(f"{'='*70}\n")
    
    # Recommendations
    if accuracy:
        best = max(accuracy.items(), key=lambda x: x[1]['accuracy_pct'])
        worst = min(accuracy.items(), key=lambda x: x[1]['accuracy_pct'])
        
        print("📋 RECOMMENDATIONS:")
        print(f"   • Best performing source: {best[0]} ({best[1]['accuracy_pct']:.1f}% accuracy)")
        print(f"   • Lowest performing source: {worst[0]} ({worst[1]['accuracy_pct']:.1f}% accuracy)")
        if best[1]['accuracy_pct'] < 100:
            print("   • Consider using DOI-validated PMIDs as the gold standard")
            print("   • AI agents may hallucinate PMIDs - always verify via DOI lookup")


if __name__ == "__main__":
    main()
