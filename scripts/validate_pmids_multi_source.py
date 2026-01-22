#!/usr/bin/env python3
"""
Multi-Source PMID Validation Script

This script cross-validates PMIDs collected from multiple AI agents
(ChatGPT, Gemini, Sciespace) and generates a consensus gold standard file.

Key Features:
- Matches studies across sources by title/author similarity
- Identifies PMID agreements and discrepancies
- Optionally validates PMIDs via PubMed API
- Generates the final gold_pmids CSV for workflow integration

Usage:
    python scripts/validate_pmids_multi_source.py <study_name> [options]
    
Examples:
    # Basic cross-validation
    python scripts/validate_pmids_multi_source.py ai_2022
    
    # With PubMed validation
    python scripts/validate_pmids_multi_source.py ai_2022 --validate-pubmed
    
    # Custom output path
    python scripts/validate_pmids_multi_source.py ai_2022 --output custom_gold.csv
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Optional
from difflib import SequenceMatcher

# Try to import optional dependencies
try:
    from Bio import Entrez
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent


def normalize_text(text: str) -> str:
    """Normalize text for comparison (lowercase, strip punctuation)."""
    if not text:
        return ""
    # Remove common variations and normalize
    text = text.lower().strip()
    text = text.replace("et al.", "").replace("et al", "")
    text = text.replace(",", "").replace(".", "").replace(";", "")
    return " ".join(text.split())


def similarity_score(text1: str, text2: str) -> float:
    """Calculate similarity between two text strings."""
    t1 = normalize_text(text1)
    t2 = normalize_text(text2)
    return SequenceMatcher(None, t1, t2).ratio()


def extract_first_author_year(author_year_str: str) -> tuple[str, str]:
    """
    Extract first author and year from strings like 'Amin 2004' or 'Amin (2004)'.
    
    Returns:
        Tuple of (author, year)
    """
    import re
    
    text = author_year_str.strip()
    
    # Pattern: Author (Year) or Author Year
    match = re.search(r'([A-Za-z\-]+)\s*[\(\[]?(\d{4})[\)\]]?', text)
    if match:
        return match.group(1), match.group(2)
    
    return text, ""


def load_csv_flexible(filepath: Path) -> list[dict]:
    """
    Load CSV with flexible column detection.
    
    Handles various column naming conventions from different sources.
    """
    studies = []
    
    # Read file content and skip empty lines at start
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    
    # Skip empty lines at the beginning
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip():
            start_idx = i
            break
    
    # Use StringIO to create a file-like object for csv.DictReader
    from io import StringIO
    content = ''.join(lines[start_idx:])
    
    reader = csv.DictReader(StringIO(content))
    
    for row in reader:
        study = {}
        
        # Title (various column names)
        for col in ['Title', 'title', 'TITLE', 'Study Title']:
            if col in row and row[col]:
                study['title'] = row[col].strip()
                break
        
        # PMID
        for col in ['PMID', 'pmid', 'PubMed ID', 'pubmed_id']:
            if col in row and row[col]:
                pmid = row[col].strip()
                # Clean up PMID (remove non-numeric characters)
                pmid = ''.join(c for c in pmid if c.isdigit())
                study['pmid'] = pmid
                break
        
        # DOI
        for col in ['DOI', 'doi']:
            if col in row and row[col]:
                study['doi'] = row[col].strip()
                break
        
        # Authors
        for col in ['Authors', 'authors', 'Author', 'author']:
            if col in row and row[col]:
                study['authors'] = row[col].strip()
                break
        
        # First Author Year (various formats)
        for col in ['First Author Year', 'First Author (Date)', 'first_author_year']:
            if col in row and row[col]:
                author, year = extract_first_author_year(row[col])
                study['first_author'] = author
                study['year'] = year
                break
        
        # If no explicit first author field, try to extract from authors
        if 'first_author' not in study and 'authors' in study:
            # Take first word of authors string
            first_word = study['authors'].split()[0] if study['authors'] else ""
            study['first_author'] = first_word.rstrip(',;')
        
        if study.get('pmid') and study.get('title'):
            studies.append(study)
    
    return studies


def match_studies_across_sources(
    sources: dict[str, list[dict]],
    threshold: float = 0.7
) -> list[dict]:
    """
    Match studies across multiple sources using title similarity.
    
    Args:
        sources: Dict mapping source name to list of studies
        threshold: Minimum similarity score for matching (0-1)
        
    Returns:
        List of matched study groups with PMIDs from each source
    """
    source_names = list(sources.keys())
    primary_source = source_names[0]
    
    matched_groups = []
    
    for primary_study in sources[primary_source]:
        group = {
            'title': primary_study.get('title', 'Unknown'),
            'first_author': primary_study.get('first_author', ''),
            'year': primary_study.get('year', ''),
            'doi': primary_study.get('doi', ''),
            'pmids': {primary_source: primary_study.get('pmid', '')},
            'match_scores': {}
        }
        
        # Find matches in other sources
        for other_source in source_names[1:]:
            best_match = None
            best_score = 0
            
            for other_study in sources[other_source]:
                score = similarity_score(
                    primary_study.get('title', ''),
                    other_study.get('title', '')
                )
                
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = other_study
            
            if best_match:
                group['pmids'][other_source] = best_match.get('pmid', '')
                group['match_scores'][other_source] = best_score
            else:
                group['pmids'][other_source] = ''
                group['match_scores'][other_source] = 0.0
        
        matched_groups.append(group)
    
    return matched_groups


def analyze_pmid_consensus(matched_groups: list[dict]) -> dict:
    """
    Analyze PMID agreement across sources.
    
    Returns:
        Analysis results with statistics and discrepancies
    """
    results = {
        'total_studies': len(matched_groups),
        'full_agreement': [],      # All sources agree
        'partial_agreement': [],    # Some sources agree
        'all_different': [],        # No agreement
        'missing_pmids': [],        # Some sources missing
        'statistics': {}
    }
    
    for group in matched_groups:
        pmids = group['pmids']
        valid_pmids = {k: v for k, v in pmids.items() if v}
        unique_pmids = set(valid_pmids.values())
        
        group_info = {
            'title': group['title'][:60] + '...' if len(group['title']) > 60 else group['title'],
            'first_author': group['first_author'],
            'year': group['year'],
            'pmids': pmids,
            'unique_pmids': list(unique_pmids)
        }
        
        if len(valid_pmids) < len(pmids):
            results['missing_pmids'].append(group_info)
        
        if len(unique_pmids) == 1 and len(valid_pmids) == len(pmids):
            results['full_agreement'].append(group_info)
        elif len(unique_pmids) == 1:
            results['partial_agreement'].append(group_info)
        elif len(unique_pmids) > 1:
            # Check if any subset agrees
            pmid_counts = {}
            for pmid in valid_pmids.values():
                pmid_counts[pmid] = pmid_counts.get(pmid, 0) + 1
            
            max_count = max(pmid_counts.values()) if pmid_counts else 0
            if max_count >= 2:
                results['partial_agreement'].append(group_info)
            else:
                results['all_different'].append(group_info)
    
    # Calculate statistics
    results['statistics'] = {
        'full_agreement_count': len(results['full_agreement']),
        'partial_agreement_count': len(results['partial_agreement']),
        'all_different_count': len(results['all_different']),
        'missing_count': len(results['missing_pmids']),
        'agreement_rate': len(results['full_agreement']) / len(matched_groups) * 100 if matched_groups else 0
    }
    
    return results


def select_consensus_pmid(group: dict, priority_order: list[str] = None) -> tuple[str, str]:
    """
    Select the consensus PMID for a study group.
    
    Strategy:
    1. If all sources agree → use that PMID
    2. If majority agrees → use majority PMID
    3. If tie → use priority order (default: ChatGPT > Sciespace > Gemini)
    
    Returns:
        Tuple of (selected_pmid, selection_reason)
    """
    if priority_order is None:
        priority_order = ['chatgpt', 'sciespace', 'gemini']
    
    pmids = group['pmids']
    valid_pmids = {k: v for k, v in pmids.items() if v}
    
    if not valid_pmids:
        return '', 'no_pmids_available'
    
    # Count occurrences
    pmid_votes = {}
    for source, pmid in valid_pmids.items():
        if pmid:
            if pmid not in pmid_votes:
                pmid_votes[pmid] = []
            pmid_votes[pmid].append(source)
    
    if len(pmid_votes) == 1:
        pmid = list(pmid_votes.keys())[0]
        return pmid, f'unanimous ({len(pmid_votes[pmid])} sources)'
    
    # Find majority
    max_votes = max(len(v) for v in pmid_votes.values())
    majority_pmids = [p for p, sources in pmid_votes.items() if len(sources) == max_votes]
    
    if len(majority_pmids) == 1:
        pmid = majority_pmids[0]
        sources = pmid_votes[pmid]
        return pmid, f'majority ({len(sources)}/{len(valid_pmids)}: {", ".join(sources)})'
    
    # Tie-breaker: use priority order
    for source in priority_order:
        if source in valid_pmids:
            pmid = valid_pmids[source]
            return pmid, f'priority_selection ({source})'
    
    # Fallback: first available
    first_pmid = list(valid_pmids.values())[0]
    return first_pmid, 'fallback'


def validate_pmid_pubmed(pmid: str, expected_title: str = None, email: str = None) -> dict:
    """
    Validate a PMID by fetching its record from PubMed.
    
    Returns:
        Dict with validation result, actual title, and match status
    """
    if not BIOPYTHON_AVAILABLE:
        return {'valid': None, 'error': 'Biopython not available'}
    
    import os
    
    Entrez.email = email or os.environ.get('NCBI_EMAIL', 'validation@example.com')
    api_key = os.environ.get('NCBI_API_KEY')
    if api_key:
        Entrez.api_key = api_key
    
    try:
        handle = Entrez.efetch(db='pubmed', id=pmid, rettype='xml', retmode='xml')
        records = Entrez.read(handle)
        handle.close()
        
        if records.get('PubmedArticle'):
            article = records['PubmedArticle'][0]
            medline = article.get('MedlineCitation', {})
            article_data = medline.get('Article', {})
            
            actual_title = str(article_data.get('ArticleTitle', ''))
            
            result = {
                'valid': True,
                'actual_title': actual_title,
                'pmid': pmid
            }
            
            if expected_title:
                result['title_match_score'] = similarity_score(expected_title, actual_title)
                result['title_matches'] = result['title_match_score'] > 0.8
            
            return result
        
        return {'valid': False, 'error': 'PMID not found'}
        
    except Exception as e:
        return {'valid': None, 'error': str(e)}


def generate_gold_pmids_csv(
    matched_groups: list[dict],
    output_path: Path,
    include_metadata: bool = False
) -> int:
    """
    Generate the final gold PMIDs CSV file for workflow integration.
    
    Args:
        matched_groups: List of matched study groups
        output_path: Path to output CSV
        include_metadata: If True, include additional columns
        
    Returns:
        Number of PMIDs written
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if include_metadata:
        fieldnames = ['pmid', 'first_author', 'year', 'title', 'selection_reason']
    else:
        fieldnames = ['pmid']
    
    written = 0
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for group in matched_groups:
            pmid, reason = select_consensus_pmid(group)
            
            if pmid:
                if include_metadata:
                    writer.writerow({
                        'pmid': pmid,
                        'first_author': group.get('first_author', ''),
                        'year': group.get('year', ''),
                        'title': group.get('title', ''),
                        'selection_reason': reason
                    })
                else:
                    writer.writerow({'pmid': pmid})
                written += 1
    
    return written


def print_analysis_report(
    analysis: dict,
    sources: dict[str, list[dict]],
    matched_groups: list[dict]
):
    """Print a formatted analysis report."""
    
    print("\n" + "=" * 70)
    print("📊 PMID CROSS-VALIDATION REPORT")
    print("=" * 70)
    
    # Source summary
    print("\n📁 Sources Loaded:")
    for name, studies in sources.items():
        print(f"   • {name}: {len(studies)} studies")
    
    # Statistics
    stats = analysis['statistics']
    print(f"\n📈 Agreement Statistics:")
    print(f"   • Total studies matched: {analysis['total_studies']}")
    print(f"   • Full agreement (all sources): {stats['full_agreement_count']} ({stats['agreement_rate']:.1f}%)")
    print(f"   • Partial agreement (majority): {stats['partial_agreement_count']}")
    print(f"   • Complete disagreement: {stats['all_different_count']}")
    print(f"   • Missing from some sources: {stats['missing_count']}")
    
    # Discrepancies
    if analysis['all_different']:
        print(f"\n⚠️  Studies with Complete Disagreement ({len(analysis['all_different'])}):")
        print("-" * 70)
        for item in analysis['all_different']:
            print(f"   📖 {item['first_author']} {item['year']}: {item['title']}")
            for source, pmid in item['pmids'].items():
                print(f"      {source}: {pmid or 'N/A'}")
            print()
    
    if analysis['partial_agreement']:
        print(f"\n🔶 Studies with Partial Agreement ({len(analysis['partial_agreement'])}):")
        print("-" * 70)
        for item in analysis['partial_agreement'][:5]:  # Show first 5
            print(f"   📖 {item['first_author']} {item['year']}")
            for source, pmid in item['pmids'].items():
                status = "✓" if pmid == item['unique_pmids'][0] else "✗"
                print(f"      {status} {source}: {pmid or 'N/A'}")
        if len(analysis['partial_agreement']) > 5:
            print(f"   ... and {len(analysis['partial_agreement']) - 5} more")
    
    # Full agreements (just summary)
    if analysis['full_agreement']:
        print(f"\n✅ Studies with Full Agreement ({len(analysis['full_agreement'])}):")
        for item in analysis['full_agreement'][:3]:
            print(f"   • {item['first_author']} {item['year']} → PMID: {item['unique_pmids'][0]}")
        if len(analysis['full_agreement']) > 3:
            print(f"   ... and {len(analysis['full_agreement']) - 3} more")


def main():
    parser = argparse.ArgumentParser(
        description="Cross-validate PMIDs from multiple AI sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate_pmids_multi_source.py ai_2022
  python scripts/validate_pmids_multi_source.py ai_2022 --validate-pubmed
  python scripts/validate_pmids_multi_source.py ai_2022 --output gold_final.csv
        """
    )
    
    parser.add_argument(
        "study_name",
        help="Name of the study (directory under studies/)"
    )
    
    parser.add_argument(
        "--output",
        default=None,
        help="Output filename for gold PMIDs (default: gold_pmids_<study>.csv)"
    )
    
    parser.add_argument(
        "--validate-pubmed",
        action="store_true",
        help="Validate selected PMIDs against PubMed"
    )
    
    parser.add_argument(
        "--include-metadata",
        action="store_true",
        help="Include metadata columns in output (author, year, title)"
    )
    
    parser.add_argument(
        "--json-report",
        action="store_true",
        help="Save detailed JSON report"
    )
    
    parser.add_argument(
        "--source-dir",
        default="pmids_multiple_sources",
        help="Subdirectory containing source CSV files (default: pmids_multiple_sources)"
    )
    
    args = parser.parse_args()
    
    # Find study directory
    study_dir = PROJECT_ROOT / "studies" / args.study_name
    source_dir = study_dir / args.source_dir
    
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print(f"🔍 Multi-Source PMID Validation: {args.study_name}")
    print(f"📂 Source Directory: {source_dir}")
    print(f"{'='*70}")
    
    # Load all CSV files from source directory
    sources = {}
    source_mapping = {
        'final': 'chatgpt',      # Ai_2022_Included_Studies_Final.csv
        'gemini': 'gemini',
        'pmids': 'sciespace'     # Default/other source
    }
    
    for csv_file in source_dir.glob("*.csv"):
        # Determine source name from filename
        filename_lower = csv_file.name.lower()
        
        if 'gemini' in filename_lower:
            source_name = 'gemini'
        elif 'final' in filename_lower:
            source_name = 'chatgpt'
        else:
            source_name = 'sciespace'
        
        print(f"\n📄 Loading: {csv_file.name} → {source_name}")
        studies = load_csv_flexible(csv_file)
        sources[source_name] = studies
        print(f"   Found {len(studies)} studies")
    
    if len(sources) < 2:
        print(f"⚠️  Warning: Only {len(sources)} source(s) found. Cross-validation requires 2+.")
    
    # Match studies across sources
    print("\n🔗 Matching studies across sources...")
    matched_groups = match_studies_across_sources(sources)
    print(f"   Matched {len(matched_groups)} study groups")
    
    # Analyze consensus
    analysis = analyze_pmid_consensus(matched_groups)
    
    # Print report
    print_analysis_report(analysis, sources, matched_groups)
    
    # Generate output
    if args.output:
        output_path = study_dir / args.output
    else:
        output_path = study_dir / f"gold_pmids_{args.study_name}.csv"
    
    print(f"\n📝 Generating Gold PMIDs: {output_path}")
    count = generate_gold_pmids_csv(matched_groups, output_path, args.include_metadata)
    print(f"   ✅ Wrote {count} PMIDs")
    
    # PubMed validation
    if args.validate_pubmed:
        print("\n🔬 Validating PMIDs via PubMed API...")
        import os
        email = os.environ.get('NCBI_EMAIL')
        
        valid_count = 0
        invalid_count = 0
        
        for group in matched_groups[:5]:  # Validate first 5 as sample
            pmid, _ = select_consensus_pmid(group)
            if pmid:
                result = validate_pmid_pubmed(pmid, group.get('title'), email)
                if result.get('valid'):
                    valid_count += 1
                    print(f"   ✅ {pmid}: Valid")
                    if result.get('title_match_score'):
                        print(f"      Title match: {result['title_match_score']:.2%}")
                else:
                    invalid_count += 1
                    print(f"   ❌ {pmid}: {result.get('error', 'Invalid')}")
        
        print(f"\n   Sample validation: {valid_count}/{valid_count + invalid_count} valid")
    
    # JSON report
    if args.json_report:
        report_path = study_dir / f"pmid_validation_report_{args.study_name}.json"
        report = {
            'study_name': args.study_name,
            'sources': {name: len(studies) for name, studies in sources.items()},
            'analysis': analysis,
            'matched_groups': matched_groups
        }
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"\n📋 JSON report saved: {report_path}")
    
    print(f"\n{'='*70}")
    print("✅ Validation Complete!")
    print(f"{'='*70}\n")
    
    # Recommendations
    if analysis['all_different']:
        print("⚠️  RECOMMENDATIONS:")
        print("   1. Manually verify PMIDs for studies with complete disagreement")
        print("   2. Consider using DOIs to look up correct PMIDs")
        print("   3. Cross-check against original systematic review paper")


if __name__ == "__main__":
    main()
