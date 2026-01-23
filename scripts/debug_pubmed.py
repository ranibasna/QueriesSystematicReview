#!/usr/bin/env python3
"""
Debug script for PubMed lookup functionality.
"""

import json
from pathlib import Path
from lookup_pmid import PubMedLookup

# Load a study
studies_file = Path(__file__).parent.parent / "studies" / "ai_2022" / "included_studies.json"

with open(studies_file) as f:
    data = json.load(f)

# Test with first study
study = data['included_studies'][2]  # Chan KC 2020 study

print("🔍 Debug PubMed Lookup")
print(f"\n📄 Study Details:")
print(f"   Title: {study['title']}")
print(f"   Author: {study['first_author']}")
print(f"   Year: {study['year']}")
print()

# Initialize client with debug
client = PubMedLookup(email="test@example.com")

# Test search
print("🔍 Step 1: PubMed Search")
pmids = client.search_pubmed(
    title=study['title'],
    first_author=study['first_author'],
    year=study['year'],
    max_results=10
)
print(f"   Found {len(pmids)} PMIDs: {pmids}")
print()

# If we have PMIDs, fetch metadata
if pmids:
    print("📥 Step 2: Fetch Metadata for First PMID")
    metadata = client.fetch_pubmed_metadata(pmids[0])
    
    if metadata:
        print(f"   PMID: {metadata['pmid']}")
        print(f"   DOI: {metadata.get('doi', 'N/A')}")
        print(f"   Title: {metadata['title'][:80]}...")
        print(f"   Authors: {', '.join(metadata.get('authors', [])[:3])}")
        print(f"   Journal: {metadata.get('journal', 'N/A')}")
        print(f"   Year: {metadata.get('year', 'N/A')}")
        print()
        
        # Test similarity
        print("🔍 Step 3: Calculate Similarity")
        similarity = client.calculate_similarity(study['title'], metadata['title'])
        print(f"   Similarity: {similarity:.3f}")
        print()
        
        # Test confidence
        print("🎯 Step 4: Calculate Confidence")
        last_name = client._extract_last_name(study['first_author']).lower()
        author_match = any(last_name in author.lower() for author in metadata.get('authors', [])[:3])
        confidence = client.calculate_confidence(similarity, len(pmids), author_match)
        print(f"   Author match: {author_match}")
        print(f"   Confidence: {confidence:.3f}")
else:
    print("❌ No PMIDs found. Trying broader search...")
    
    # Try without full title
    print("\n🔍 Alternative Search: Using only key terms")
    title_keywords = " ".join(study['title'].split()[:5])  # First 5 words
    print(f"   Keywords: {title_keywords}")
    
    pmids = client.search_pubmed(
        title=title_keywords,
        first_author=study['first_author'],
        year=study['year'],
        max_results=10
    )
    print(f"   Found {len(pmids)} PMIDs: {pmids}")
