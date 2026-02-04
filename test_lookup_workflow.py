#!/usr/bin/env python3
"""
Standalone test script for the multi-tier lookup system.
Tests PubMed → Europe PMC → CrossRef workflow with validation.
"""

import sys
import json
sys.path.insert(0, '/Users/ra1077ba/Documents/DataScience/GU/Daniil/LLM/QueriesSystematicReview')

from scripts.lookup_pmid import PubMedLookup
from scripts.lookup_europepmc import EuropePMCLookup
from scripts.lookup_crossref import CrossRefLookup

def test_lookup_workflow(email="test@example.com", min_confidence=0.80, max_year_diff=1):
    """Test the complete lookup workflow."""
    
    # Load test data
    with open('test_lookup_input.json', 'r') as f:
        data = json.load(f)
    
    studies = data['included_studies']
    
    # Initialize clients
    pubmed_client = PubMedLookup(email=email)
    europepmc_client = EuropePMCLookup(email=email)
    crossref_client = CrossRefLookup(email=email)
    
    print(f"🔍 Testing Multi-Tier Lookup Workflow")
    print(f"   Strategy: PubMed → Europe PMC → CrossRef")
    print(f"   Min confidence: {min_confidence}")
    print(f"   Year tolerance: ±{max_year_diff}")
    print()
    
    pubmed_success = 0
    europepmc_success = 0
    crossref_success = 0
    failures = 0
    
    for i, study in enumerate(studies, 1):
        title = study['title'][:60]
        print(f"[{i}/{len(studies)}] {title}...")
        
        # Try PubMed
        match = pubmed_client.find_best_match(
            study,
            min_confidence=min_confidence,
            max_year_diff=max_year_diff
        )
        
        if match:
            study['pmid'] = match.pmid
            study['doi'] = match.doi
            study['lookup_source'] = 'PubMed'
            study['confidence'] = match.confidence
            pubmed_success += 1
            print(f"   ✅ [PubMed] PMID: {match.pmid}, DOI: {match.doi or 'N/A'}, Conf: {match.confidence:.2f}")
        else:
            # Try Europe PMC
            print(f"   → PubMed failed, trying Europe PMC...")
            
            epmc_match = europepmc_client.find_best_match(
                study,
                min_confidence=min_confidence,
                max_year_diff=max_year_diff
            )
            
            if epmc_match:
                study['pmid'] = epmc_match.pmid
                study['doi'] = epmc_match.doi
                study['lookup_source'] = 'EuropePMC'
                study['confidence'] = epmc_match.confidence
                europepmc_success += 1
                print(f"   ✅ [Europe PMC] PMID: {epmc_match.pmid or 'N/A'}, DOI: {epmc_match.doi or 'N/A'}, Conf: {epmc_match.confidence:.2f}")
            else:
                # Try CrossRef
                print(f"   → Europe PMC failed, trying CrossRef...")
                
                cr_match = crossref_client.find_best_match(
                    study,
                    min_confidence=min_confidence,
                    max_year_diff=max_year_diff
                )
                
                if cr_match:
                    study['doi'] = cr_match.doi
                    study['lookup_source'] = 'CrossRef'
                    study['confidence'] = cr_match.confidence
                    crossref_success += 1
                    print(f"   ✅ [CrossRef] DOI: {cr_match.doi}, Conf: {cr_match.confidence:.2f}")
                else:
                    failures += 1
                    print(f"   ❌ All lookup methods failed")
        
        print()
    
    # Summary
    print("=" * 70)
    print(f"SUMMARY:")
    print(f"  PubMed matches:      {pubmed_success}")
    print(f"  Europe PMC matches:  {europepmc_success}")
    print(f"  CrossRef matches:    {crossref_success}")
    print(f"  Failures:            {failures}")
    print(f"  Total resolved:      {pubmed_success + europepmc_success + crossref_success}/{len(studies)}")
    
    # Calculate coverage
    with_doi = sum(1 for s in studies if s.get('doi'))
    with_pmid = sum(1 for s in studies if s.get('pmid'))
    
    print(f"\nCOVERAGE:")
    print(f"  DOI coverage:  {with_doi}/{len(studies)} ({with_doi/len(studies)*100:.1f}%)")
    print(f"  PMID coverage: {with_pmid}/{len(studies)} ({with_pmid/len(studies)*100:.1f}%)")
    
    # Save results
    with open('test_lookup_output.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Results saved to test_lookup_output.json")
    
    return data

if __name__ == '__main__':
    test_lookup_workflow()
