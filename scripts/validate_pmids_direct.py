#!/usr/bin/env python3
"""
PMID Validation via Direct PubMed Verification

This script validates PMIDs from multiple AI sources by:
1. Fetching each unique PMID from PubMed to get actual title/DOI
2. Comparing against the DOIs provided by each source
3. Determining which source is most accurate

Run with: conda run -n systematic_review_queries python scripts/validate_pmids_direct.py ai_2022
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from io import StringIO
from collections import defaultdict

from Bio import Entrez
import os

PROJECT_ROOT = Path(__file__).parent.parent

# Configure Entrez
Entrez.email = os.environ.get('NCBI_EMAIL', 'validation@example.com')
api_key = os.environ.get('NCBI_API_KEY')
if api_key:
    Entrez.api_key = api_key


def load_csv_flexible(filepath: Path) -> list[dict]:
    """Load CSV with flexible parsing, handles blank lines."""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    
    # Skip empty lines at start
    start_idx = next((i for i, line in enumerate(lines) if line.strip()), 0)
    content = ''.join(lines[start_idx:])
    
    studies = []
    reader = csv.DictReader(StringIO(content))
    
    for row in reader:
        study = {}
        
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
                doi = row[col].strip().lower()
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
        
        if study.get('pmid'):
            studies.append(study)
    
    return studies


def fetch_pmid_details(pmid: str) -> dict:
    """Fetch title, DOI, and author info for a PMID from PubMed."""
    try:
        handle = Entrez.efetch(db='pubmed', id=pmid, rettype='xml', retmode='xml')
        records = Entrez.read(handle)
        handle.close()
        
        if not records.get('PubmedArticle'):
            return {'valid': False, 'error': 'Not found'}
        
        article = records['PubmedArticle'][0]
        medline = article.get('MedlineCitation', {})
        article_data = medline.get('Article', {})
        
        # Get title
        title = str(article_data.get('ArticleTitle', ''))
        
        # Get DOI
        doi = ''
        for id_obj in article.get('PubmedData', {}).get('ArticleIdList', []):
            if id_obj.attributes.get('IdType') == 'doi':
                doi = str(id_obj).lower()
                break
        
        # Get first author
        authors = article_data.get('AuthorList', [])
        first_author = ''
        if authors:
            author = authors[0]
            first_author = author.get('LastName', '')
        
        # Get year
        pub_date = article_data.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
        year = pub_date.get('Year', '')
        
        return {
            'valid': True,
            'pmid': pmid,
            'title': title,
            'doi': doi,
            'first_author': first_author,
            'year': year
        }
        
    except Exception as e:
        return {'valid': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="Validate PMIDs by fetching from PubMed and comparing sources"
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
    print(f"🔬 Direct PMID Validation: {args.study_name}")
    print(f"{'='*70}")
    
    # Load all sources
    sources = {}
    for csv_file in source_dir.glob("*.csv"):
        filename = csv_file.name.lower()
        if 'gemini' in filename:
            name = 'gemini'
        elif 'final' in filename:
            name = 'sciespace'
        elif 'chatgpt' in filename:
            name = 'chatgpt'
        elif 'sciespace' in filename:
            name = 'sciespace'
        else:
            # Default fallback for unknown patterns
            name = csv_file.stem.split('_')[-1]
        
        print(f"\n📄 Loading: {csv_file.name} → {name}")
        studies = load_csv_flexible(csv_file)
        sources[name] = studies
        print(f"   Found {len(studies)} studies with PMIDs")
    
    # Collect all unique PMIDs
    all_pmids = {}  # pmid -> {source: doi_claimed}
    for source_name, studies in sources.items():
        for study in studies:
            pmid = study.get('pmid')
            doi = study.get('doi', '')
            if pmid:
                if pmid not in all_pmids:
                    all_pmids[pmid] = {'sources': {}, 'details': None}
                all_pmids[pmid]['sources'][source_name] = {
                    'doi_claimed': doi,
                    'title_claimed': study.get('title', ''),
                    'author_info': study.get('author_info', '')
                }
    
    print(f"\n🔍 Found {len(all_pmids)} unique PMIDs across all sources")
    print("-" * 70)
    
    # Fetch details for each PMID
    for i, (pmid, info) in enumerate(all_pmids.items(), 1):
        print(f"[{i}/{len(all_pmids)}] Validating PMID {pmid}...", end=" ")
        
        details = fetch_pmid_details(pmid)
        all_pmids[pmid]['details'] = details
        
        if details.get('valid'):
            print(f"✅ {details['first_author']} {details['year']}")
        else:
            print(f"❌ {details.get('error', 'Invalid')}")
        
        time.sleep(0.35)
    
    # Analyze: Check if DOIs match
    print(f"\n{'='*70}")
    print("📊 VALIDATION RESULTS")
    print(f"{'='*70}")
    
    source_stats = defaultdict(lambda: {'correct': 0, 'incorrect': 0, 'total': 0})
    discrepancies = []
    
    # Group PMIDs by DOI
    doi_to_pmid = {}  # doi -> actual pmid
    for pmid, info in all_pmids.items():
        if info['details'].get('valid'):
            doi = info['details'].get('doi', '')
            if doi:
                doi_to_pmid[doi] = pmid
    
    # Check each source's claims
    for source_name, studies in sources.items():
        print(f"\n📌 {source_name.upper()} Analysis:")
        print("-" * 40)
        
        for study in studies:
            pmid_claimed = study.get('pmid')
            doi_claimed = study.get('doi', '').lower()
            title_claimed = study.get('title', '')[:50]
            
            source_stats[source_name]['total'] += 1
            
            # Get actual details for claimed PMID
            actual = all_pmids.get(pmid_claimed, {}).get('details', {})
            actual_doi = actual.get('doi', '') if actual.get('valid') else ''
            actual_title = actual.get('title', '')[:50] if actual.get('valid') else ''
            
            # Check if DOIs match
            doi_match = doi_claimed and actual_doi and (doi_claimed == actual_doi)
            
            if doi_match:
                source_stats[source_name]['correct'] += 1
            else:
                source_stats[source_name]['incorrect'] += 1
                
                # Find the correct PMID for this DOI
                correct_pmid = doi_to_pmid.get(doi_claimed, None)
                
                discrepancies.append({
                    'source': source_name,
                    'doi_claimed': doi_claimed,
                    'pmid_claimed': pmid_claimed,
                    'pmid_actual_for_doi': correct_pmid,
                    'title_claimed': title_claimed,
                    'title_actual': actual_title
                })
                
                print(f"   ❌ DOI: {doi_claimed[:30]}...")
                print(f"      Claimed PMID: {pmid_claimed} → Actual DOI: {actual_doi}")
                if correct_pmid:
                    print(f"      Correct PMID for DOI: {correct_pmid}")
    
    # Summary statistics
    print(f"\n{'='*70}")
    print("📈 SOURCE ACCURACY SUMMARY")
    print(f"{'='*70}\n")
    
    for source_name in sorted(source_stats.keys()):
        stats = source_stats[source_name]
        total = stats['total']
        correct = stats['correct']
        pct = (correct / total * 100) if total > 0 else 0
        
        print(f"   {source_name.upper():12s}: {correct:2d}/{total:2d} correct ({pct:5.1f}%)")
    
    # Determine best source
    best_source = max(source_stats.items(), 
                      key=lambda x: x[1]['correct'] / max(x[1]['total'], 1))
    
    print(f"\n   🏆 Most accurate: {best_source[0].upper()}")
    
    # Generate consolidated gold PMID list
    # Strategy: Use PMIDs from the most accurate source, validated
    output_path = study_dir / (args.output or f"gold_pmids_{args.study_name}.csv")
    
    print(f"\n{'='*70}")
    print(f"📝 Generating Gold PMIDs from {best_source[0]}")
    print(f"{'='*70}")
    
    gold_pmids = []
    for study in sources[best_source[0]]:
        pmid = study.get('pmid')
        details = all_pmids.get(pmid, {}).get('details', {})
        if details.get('valid'):
            gold_pmids.append({
                'pmid': pmid,
                'doi': details.get('doi', ''),
                'title': details.get('title', ''),
                'first_author': details.get('first_author', ''),
                'year': details.get('year', '')
            })
            print(f"   ✅ {pmid}: {details.get('first_author', '?')} {details.get('year', '')}")
    
    # Write gold file (simple format for workflow)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['pmid'])
        for entry in gold_pmids:
            writer.writerow([entry['pmid']])
    
    print(f"\n   📄 Wrote {len(gold_pmids)} PMIDs to {output_path}")
    
    # Also write detailed version
    detailed_path = output_path.parent / f"gold_pmids_{args.study_name}_detailed.csv"
    with open(detailed_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['pmid', 'doi', 'first_author', 'year', 'title'])
        writer.writeheader()
        writer.writerows(gold_pmids)
    
    print(f"   📄 Wrote detailed version to {detailed_path}")
    
    # JSON report
    if args.json_report:
        report = {
            'study_name': args.study_name,
            'source_stats': dict(source_stats),
            'best_source': best_source[0],
            'all_pmids': {k: {'sources': v['sources'], 
                             'details': v['details']} 
                         for k, v in all_pmids.items()},
            'discrepancies': discrepancies,
            'gold_pmids': gold_pmids
        }
        report_path = study_dir / f"pmid_validation_report_{args.study_name}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"   📋 JSON report: {report_path}")
    
    print(f"\n{'='*70}")
    print("✅ Validation Complete!")
    print(f"{'='*70}\n")
    
    # Recommendations
    print("📋 RECOMMENDATIONS:")
    print("-" * 40)
    
    if source_stats[best_source[0]]['correct'] < source_stats[best_source[0]]['total']:
        print("⚠️  Not all PMIDs validated correctly!")
        print("   • Review the discrepancies above")
        print("   • Consider using DOI lookup for unmatched studies")
    
    if best_source[0] != 'gemini':
        print(f"\n💡 INSIGHT: ChatGPT/Sciespace appear more accurate than Gemini")
        print("   This suggests Gemini may be hallucinating PMIDs")
    else:
        print(f"\n💡 INSIGHT: Gemini was most accurate for this study")
    
    print("\n🔧 For future studies:")
    print("   1. Prefer sources that provide matching DOI + PMID pairs")
    print("   2. Always validate PMIDs via PubMed API before use")
    print("   3. Use DOI as ground truth when PMIDs disagree")


if __name__ == "__main__":
    main()
