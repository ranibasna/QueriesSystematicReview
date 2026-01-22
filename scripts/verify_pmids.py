#!/usr/bin/env python3
"""
Search and verify correct PMIDs for Ai 2022 gold standard.
"""

from Bio import Entrez
import os
import time

# Load env
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

Entrez.email = os.environ.get('NCBI_EMAIL', 'test@test.com')

# Search queries based on exact titles from the paper's Table 1 and references
SEARCHES = [
    # Ref 13: Amin 2004
    ('Amin_2004', 'Amin[1AU] AND "24-hour ambulatory blood pressure" AND children AND "sleep-disordered" AND 2004[PDAT]'),
    
    # Ref 28: Amin 2008 - Already verified: 18071053
    
    # Ref 29: Bixler 2008 - Already verified: 18838624
    
    # Ref 17: Chan 2020 - Thorax
    ('Chan_2020', 'Chan[1AU] AND "Childhood OSA" AND "blood pressure" AND adulthood AND Thorax[Journal]'),
    
    # Ref 30: Geng 2019 - Already verified: 32851326
    
    # Ref 18: Fernandez-Mendoza 2021 - Already verified: 34160576
    
    # Ref 31: Horne 2011 - Pediatrics
    ('Horne_2011', 'Horne[1AU] AND "Elevated blood pressure" AND sleep AND wake AND children AND 2011[PDAT]'),
    
    # Ref 32: Horne 2020 - Already verified: 31927221
    
    # Ref 33: Kaditis 2010 - Already verified: 20648668
    
    # Ref 34: Kang 2017 - J Pediatr
    ('Kang_2017', 'Kang[1AU] AND ambulatory blood pressure AND children AND obstructive sleep apnea AND 2017[PDAT]'),
    
    # Ref 12: Li 2008 - Sleep journal
    ('Li_2008', 'Li AM[AU] AND ambulatory blood pressure AND children AND obstructive AND 2008[PDAT]'),
    
    # Ref 35: McConnell 2009 - Already verified: 19286627
    
    # Ref 36: O'Driscoll 2009 - Already verified: 19848356
    
    # Ref 37: O'Driscoll 2011 - Already verified: 21521626
]

print("Searching for correct PMIDs...")
print("=" * 70)

for name, query in SEARCHES:
    print(f"\n{name}:")
    print(f"  Query: {query[:60]}...")
    
    try:
        handle = Entrez.esearch(db='pubmed', term=query, retmax=5)
        record = Entrez.read(handle)
        handle.close()
        
        ids = record.get('IdList', [])
        
        if ids:
            for pmid in ids[:2]:
                h = Entrez.efetch(db='pubmed', id=pmid, rettype='xml', retmode='xml')
                r = Entrez.read(h)
                h.close()
                
                if r.get('PubmedArticle'):
                    article = r['PubmedArticle'][0]['MedlineCitation']['Article']
                    title = article['ArticleTitle']
                    journal = article['Journal']['Title']
                    print(f"  PMID {pmid}: {title[:70]}...")
                    print(f"    Journal: {journal}")
        else:
            print("  NOT FOUND")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(0.5)
