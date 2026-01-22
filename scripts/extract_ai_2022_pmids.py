#!/usr/bin/env python3
"""
Extract Gold Standard PMIDs for ai_2022 Study

This script extracts PMIDs for the 14 studies included in the 
Ai 2022 systematic review on blood pressure and childhood OSA.

The studies are references [12, 13, 17, 18, 28-37] from the paper.
"""

import os
import sys
import csv
import time

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except ImportError:
    pass

from Bio import Entrez

# Configure Entrez
Entrez.email = os.environ.get("NCBI_EMAIL", "example@example.com")
api_key = os.environ.get("NCBI_API_KEY")
if api_key:
    Entrez.api_key = api_key

# 14 studies from Table 1: References [12, 13, 17, 18, 28-37]
# Using exact PMIDs when known, or very specific title searches
STUDIES = [
    # Ref 13: Amin RS et al. 2004 - "24-hour ambulatory blood pressure in children with SDB"
    # PMID: 15257594 (from looking up the DOI/reference)
    {"pmid": "15257594", "first_author": "Amin", "year": "2004"},
    
    # Ref 28: Amin R et al. 2008 - "Activity-adjusted 24-hour ambulatory BP"
    {"pmid": "18071053", "first_author": "Amin", "year": "2008"},
    
    # Ref 29: Bixler EO et al. 2008 - "Blood pressure associated with SDB in population sample"
    {"pmid": "18838624", "first_author": "Bixler", "year": "2008"},
    
    # Ref 17: Chan KC et al. 2020 - "Childhood OSA is an independent determinant"
    # Published in Thorax 2020;75:422-31
    {"pmid": "32094252", "first_author": "Chan", "year": "2020"},
    
    # Ref 30: Geng X et al. 2019 - "Ambulatory BP monitoring in children with OSA"
    {"pmid": "32851326", "first_author": "Geng", "year": "2019"},
    
    # Ref 18: Fernandez-Mendoza J et al. 2021 - "Association of Pediatric OSA with BP"
    {"pmid": "34160576", "first_author": "Fernandez-Mendoza", "year": "2021"},
    
    # Ref 31: Horne RS et al. 2011 - "Elevated blood pressure during sleep and wake"
    # Published in Pediatrics 2011;128:e85-92
    {"pmid": "21708806", "first_author": "Horne", "year": "2011"},
    
    # Ref 32: Horne RSC et al. 2020 - "Are there gender differences in severity"
    {"pmid": "31927221", "first_author": "Horne", "year": "2020"},
    
    # Ref 33: Kaditis AG et al. 2010 - "Correlation of urinary excretion of sodium"
    {"pmid": "20648668", "first_author": "Kaditis", "year": "2010"},
    
    # Ref 34: Kang KT et al. 2017 - "Comparisons of office and 24-hour ambulatory"
    {"pmid": "28159417", "first_author": "Kang", "year": "2017"},
    
    # Ref 12: Li AM et al. 2008 - "Ambulatory blood pressure in children with OSA"
    # Published in Sleep 2008;31:1071-8
    {"pmid": "18714778", "first_author": "Li", "year": "2008"},
    
    # Ref 35: McConnell K et al. 2009 - "Baroreflex gain in children with OSA"
    {"pmid": "19286627", "first_author": "McConnell", "year": "2009"},
    
    # Ref 36: O'Driscoll DM et al. 2009 - "Acute cardiovascular changes"
    {"pmid": "19848356", "first_author": "O'Driscoll", "year": "2009"},
    
    # Ref 37: O'Driscoll DM et al. 2011 - "Increased sympathetic activity"
    {"pmid": "21521626", "first_author": "O'Driscoll", "year": "2011"},
]


def fetch_pmid_details(pmid, author, year):
    """Fetch details for a known PMID."""
    try:
        handle = Entrez.efetch(
            db="pubmed", 
            id=pmid, 
            rettype="xml", 
            retmode="xml"
        )
        records = Entrez.read(handle)
        handle.close()
        
        if records.get("PubmedArticle"):
            article = records["PubmedArticle"][0]
            medline = article.get("MedlineCitation", {})
            article_data = medline.get("Article", {})
            
            title = str(article_data.get("ArticleTitle", ""))
            journal = article_data.get("Journal", {}).get("Title", "")
            
            # Extract DOI
            doi = ""
            pub_data = article.get("PubmedData", {})
            for id_obj in pub_data.get("ArticleIdList", []):
                if id_obj.attributes.get("IdType") == "doi":
                    doi = str(id_obj)
                    break
            
            return {
                "pmid": pmid,
                "first_author": author,
                "year": year,
                "title": title,
                "journal": journal,
                "doi": doi
            }
        
    except Exception as e:
        print(f"   Warning: Failed to fetch PMID {pmid} - {e}")
    
    return None


def main():
    print("=" * 70)
    print("Extracting Gold Standard PMIDs for ai_2022 Study")
    print("=" * 70)
    print()
    
    results = []
    
    for i, study in enumerate(STUDIES, 1):
        pmid = study["pmid"]
        author = study["first_author"]
        year = study["year"]
        
        print(f"[{i}/{len(STUDIES)}] Fetching PMID {pmid} ({author} {year})...", end=" ", flush=True)
        
        result = fetch_pmid_details(pmid, author, year)
        
        if result:
            results.append(result)
            print(f"✅")
        else:
            # Still include the PMID even if we couldn't fetch details
            results.append({
                "pmid": pmid,
                "first_author": author,
                "year": year,
                "title": "",
                "journal": "",
                "doi": ""
            })
            print("⚠️ (added without details)")
        
        time.sleep(0.3)
    
    # Save results
    output_path = os.path.join(PROJECT_ROOT, "studies", "ai_2022", "gold_pmids_ai_2022.csv")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f, 
            fieldnames=['pmid', 'first_author', 'year', 'title', 'journal', 'doi']
        )
        writer.writeheader()
        writer.writerows(results)
    
    # Summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"✅ Processed: {len(results)} studies")
    print(f"📝 Output: {output_path}")
    print()
    
    # Also print just PMIDs for easy copy
    print("PMIDs (for quick reference):")
    for r in results:
        print(f"  {r['pmid']}")


if __name__ == "__main__":
    main()
