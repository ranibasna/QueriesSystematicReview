#!/usr/bin/env python3
"""
Analyze DOI/PMID extraction results to identify issues.
"""

import json
import sys
from pathlib import Path

def analyze_results(json_file: str):
    """Analyze extraction results and identify issues."""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print("🔍 ANALYSIS OF DOI/PMID EXTRACTION RESULTS")
    print("=" * 80)
    print(f"\nStudy: {data['study_name']}")
    print(f"Total studies: {data['total_included_studies']}")
    print()
    
    has_doi = []
    has_pmid = []
    has_both = []
    has_neither = []
    lookup_succeeded = []
    lookup_failed = []
    
    for study in data['included_studies']:
        ref_num = study['reference_number']
        author = f"{study['first_author']} ({study['year']})"
        doi = study.get('doi')
        pmid = study.get('pmid')
        lookup = study.get('pmid_lookup', {})
        
        # Categorize
        if doi and pmid:
            has_both.append((ref_num, author, doi, pmid))
        elif doi:
            has_doi.append((ref_num, author, doi))
        elif pmid:
            has_pmid.append((ref_num, author, pmid))
        else:
            has_neither.append((ref_num, author, study['title']))
        
        # Check lookup success
        if lookup:
            if lookup.get('confidence', 0) >= 0.80:
                lookup_succeeded.append((ref_num, author, lookup.get('confidence'), lookup.get('similarity')))
            else:
                lookup_failed.append((ref_num, author, lookup.get('confidence'), lookup.get('similarity')))
    
    # Print detailed breakdown
    print("\n📊 IDENTIFIER COVERAGE:")
    print(f"  ✅ Has BOTH DOI + PMID: {len(has_both)} ({len(has_both)/data['total_included_studies']*100:.1f}%)")
    print(f"  📗 Has DOI only: {len(has_doi)}")
    print(f"  📘 Has PMID only: {len(has_pmid)}")
    print(f"  ❌ Has NEITHER: {len(has_neither)} ({len(has_neither)/data['total_included_studies']*100:.1f}%)")
    
    print("\n🎯 LOOKUP PERFORMANCE:")
    print(f"  ✅ Lookup succeeded: {len(lookup_succeeded)} ({len(lookup_succeeded)/data['total_included_studies']*100:.1f}%)")
    print(f"  ❌ Lookup failed: {len(lookup_failed)} ({len(lookup_failed)/data['total_included_studies']*100:.1f}%)")
    
    # Show studies without identifiers
    if has_neither:
        print("\n⚠️  STUDIES WITHOUT IDENTIFIERS:")
        for ref_num, author, title in has_neither:
            print(f"  [{ref_num}] {author}")
            print(f"      Title: {title[:70]}...")
            print()
    
    # Show lookup failures
    if lookup_failed:
        print("\n❌ LOOKUP FAILURES:")
        for ref_num, author, conf, sim in lookup_failed:
            print(f"  [{ref_num}] {author}")
            print(f"      Confidence: {conf}, Similarity: {sim:.3f}")
            print()
    
    print("\n" + "=" * 80)
    print("\n💡 KEY ISSUES IDENTIFIED:")
    
    if len(has_neither) > 0:
        print(f"\n1. {len(has_neither)} studies have NO identifiers (DOI or PMID)")
        print("   → These were NOT found by PubMed lookup")
        print("   → Need to investigate why the lookup failed")
    
    if len(has_both) < data['total_included_studies']:
        missing = data['total_included_studies'] - len(has_both)
        print(f"\n2. {missing} studies don't have BOTH DOI and PMID")
        print("   → Current success rate: {:.1f}%".format(len(has_both)/data['total_included_studies']*100))
        print("   → Target should be >95%")
    
    print("\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_extraction_results.py <json_file>")
        sys.exit(1)
    
    analyze_results(sys.argv[1])
