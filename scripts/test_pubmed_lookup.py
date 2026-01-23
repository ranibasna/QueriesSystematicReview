#!/usr/bin/env python3
"""
Test script for PubMed lookup functionality.
"""

import json
from pathlib import Path
from lookup_pmid import PubMedLookup

# Load a real study from ai_2022
studies_file = Path(__file__).parent.parent / "studies" / "ai_2022" / "included_studies.json"

with open(studies_file) as f:
    data = json.load(f)

# Get first few studies
test_studies = data['included_studies'][:3]

print("🔍 Testing PubMed Lookup on Real Studies")
print(f"   Email: test@example.com (replace with real email)")
print(f"   Testing {len(test_studies)} studies from ai_2022\n")

# Initialize client
client = PubMedLookup(email="test@example.com")

for i, study in enumerate(test_studies, 1):
    print(f"Study {i}: {study['title'][:60]}...")
    print(f"  Author: {study['first_author']}, Year: {study['year']}")
    
    match = client.find_best_match(study, min_confidence=0.70)
    
    if match:
        print(f"  ✅ PMID: {match.pmid}")
        print(f"     DOI: {match.doi or 'N/A'}")
        print(f"     Confidence: {match.confidence:.3f}")
        print(f"     Similarity: {match.similarity_score:.3f}")
    else:
        print(f"  ❌ No match found")
    
    print()
