#!/usr/bin/env python3
"""Debug script to check why Scopus recall is 0%"""

import json
import csv

# Load details file
with open('benchmark_outputs/Li_2024/details_20260203-213731.json', 'r') as f:
    details = json.load(f)

# Get Scopus data from first query
scopus_data = details[0]['provider_details']['scopus']
scopus_dois = set(d.lower() for d in scopus_data['retrieved_dois'])
scopus_ids = set(scopus_data['retrieved_ids'])

print("=== SCOPUS DATA ===")
print(f"Scopus DOIs: {len(scopus_dois)}")
print(f"Scopus IDs: {len(scopus_ids)}")
print(f"First 3 DOIs: {list(scopus_dois)[:3]}")

# Load gold standard
with open('studies/Li_2024/gold_pmids_Li_2024_detailed.csv', 'r') as f:
    reader = csv.DictReader(f)
    gold_rows = list(reader)

gold_pmids = set(row['pmid'] for row in gold_rows if row['pmid'])
gold_dois = set(row['doi'].lower() for row in gold_rows if row['doi'])

print("\n=== GOLD STANDARD ===")
print(f"Gold PMIDs: {len(gold_pmids)}")
print(f"Gold DOIs: {len(gold_dois)}")
print(f"First 3 DOIs: {list(gold_dois)[:3]}")

# Check matching
doi_matches = scopus_dois & gold_dois
pmid_matches = scopus_ids & gold_pmids

print("\n=== MATCHING ===")
print(f"DOI matches: {len(doi_matches)}")
print(f"PMID matches: {len(pmid_matches)}")

if doi_matches:
    print(f"\nMatched DOIs ({len(doi_matches)}):")
    for doi in sorted(doi_matches):
        # Find the corresponding article
        for row in gold_rows:
            if row['doi'].lower() == doi:
                print(f"  - {row['first_author']} {row['year']}: {doi}")
                break

# Now test the actual function
print("\n=== TESTING set_metrics_multi_key ===")

# Simulate what the code does
db_ids = set(scopus_data.get('retrieved_ids', []))
db_dois = set(scopus_data.get('retrieved_dois', []))

print(f"db_ids type: {type(db_ids)}, length: {len(db_ids)}")
print(f"db_dois type: {type(db_dois)}, length: {len(db_dois)}")
print(f"First db_doi: {list(db_dois)[0] if db_dois else 'NONE'}")

# Now manually run set_metrics_multi_key logic
retrieved_dois_norm = {doi.lower() for doi in db_dois if doi}
gold_dois_norm = {doi.lower() for doi in gold_dois if doi}

matches_by_doi = retrieved_dois_norm & gold_dois_norm

print(f"\nNormalized DOI matches: {len(matches_by_doi)}")
print(f"Expected TP: {len(matches_by_doi)}")
print(f"Expected Recall: {len(matches_by_doi) / len(gold_dois)}")
