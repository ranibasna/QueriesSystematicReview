#!/usr/bin/env python3
"""
Test why specific studies failed PubMed lookup.
"""

from Bio import Entrez
import time

Entrez.email = "test@example.com"

# The two studies that failed
failed_studies = [
    {
        "ref": 13,
        "author": "Amin RS",
        "year": 2004,
        "title": "Twenty-fourhour ambulatory blood pressure in children with sleep-disordered breathing",
        "journal": "Am J Respir Crit Care Med"
    },
    {
        "ref": 35,
        "author": "McConnell K",
        "year": 2009,
        "title": "Barore /uniFB02 ex gain in children with obstructive sleep apnea",
        "journal": "Am J Respir Crit Care Med"
    }
]

def test_search(title, author, year, ref_num):
    """Test different search strategies."""
    print(f"\n{'='*80}")
    print(f"Testing [{ref_num}] {author} ({year})")
    print(f"Title: {title}")
    print(f"{'='*80}")
    
    # Strategy 1: Exact title
    print("\n1️⃣  Strategy 1: Exact title + author + year")
    query = f'{title}[Title] AND {author}[Author] AND {year}[PDAT]'
    print(f"   Query: {query}")
    try:
        handle = Entrez.esearch(db='pubmed', term=query, retmax=5)
        result = Entrez.read(handle)
        pmids = result['IdList']
        print(f"   ✓ Found {len(pmids)} results: {pmids}")
        if pmids:
            return pmids[0]
        time.sleep(0.4)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Strategy 2: First 50 chars of title
    print("\n2️⃣  Strategy 2: Partial title (first 50 chars)")
    title_partial = title[:50] if len(title) > 50 else title
    query = f'{title_partial}[Title] AND {author}[Author] AND {year}[PDAT]'
    print(f"   Query: {query}")
    try:
        handle = Entrez.esearch(db='pubmed', term=query, retmax=5)
        result = Entrez.read(handle)
        pmids = result['IdList']
        print(f"   ✓ Found {len(pmids)} results: {pmids}")
        if pmids:
            return pmids[0]
        time.sleep(0.4)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Strategy 3: Just author + year
    print("\n3️⃣  Strategy 3: Broad search (author + year only)")
    query = f'{author}[Author] AND {year}[PDAT]'
    print(f"   Query: {query}")
    try:
        handle = Entrez.esearch(db='pubmed', term=query, retmax=20)
        result = Entrez.read(handle)
        pmids = result['IdList']
        print(f"   ✓ Found {len(pmids)} results: {pmids[:5]}")
        time.sleep(0.4)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Strategy 4: Try cleaning the title
    print("\n4️⃣  Strategy 4: Clean title (remove special chars)")
    # Remove special unicode characters
    import re
    title_clean = re.sub(r'[^\w\s\-:]', ' ', title)
    title_clean = ' '.join(title_clean.split())  # normalize whitespace
    query = f'{title_clean}[Title] AND {author}[Author] AND {year}[PDAT]'
    print(f"   Cleaned title: {title_clean}")
    print(f"   Query: {query}")
    try:
        handle = Entrez.esearch(db='pubmed', term=query, retmax=5)
        result = Entrez.read(handle)
        pmids = result['IdList']
        print(f"   ✓ Found {len(pmids)} results: {pmids}")
        if pmids:
            return pmids[0]
        time.sleep(0.4)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Strategy 5: Try first few words only
    print("\n5️⃣  Strategy 5: First 5 words of title")
    words = title.split()[:5]
    title_short = ' '.join(words)
    query = f'{title_short}[Title] AND {author}[Author] AND {year}[PDAT]'
    print(f"   Short title: {title_short}")
    print(f"   Query: {query}")
    try:
        handle = Entrez.esearch(db='pubmed', term=query, retmax=5)
        result = Entrez.read(handle)
        pmids = result['IdList']
        print(f"   ✓ Found {len(pmids)} results: {pmids}")
        if pmids:
            return pmids[0]
        time.sleep(0.4)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    return None

# Test each failed study
print("\n" + "🔍 TESTING FAILED STUDIES" + "\n")

for study in failed_studies:
    pmid = test_search(
        study['title'],
        study['author'],
        study['year'],
        study['ref']
    )
    
    if pmid:
        print(f"\n✅ SUCCESS! Found PMID: {pmid}")
        # Fetch details
        handle = Entrez.efetch(db='pubmed', id=pmid, rettype='medline', retmode='text')
        print("\nPubMed Record:")
        print(handle.read()[:500])
    else:
        print(f"\n❌ FAILED to find PMID for this study")
    
    print("\n" + "="*80 + "\n")
    time.sleep(1)
