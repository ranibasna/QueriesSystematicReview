#!/usr/bin/env python3
"""Deep debug of set_metrics_multi_key function"""

import json
import csv

# Import the function
import sys
sys.path.insert(0, '.')
from llm_sr_select_and_score import set_metrics_multi_key, load_gold_multi_key

# Load gold standard
gold_pmids, gold_dois = load_gold_multi_key('studies/Li_2024/gold_pmids_Li_2024_detailed.csv')

print("=== GOLD STANDARD (from load_gold_multi_key) ===")
print(f"gold_pmids: {len(gold_pmids)} items")
print(f"gold_dois: {len(gold_dois)} items")
print(f"Sample gold PMID: {list(gold_pmids)[0] if gold_pmids else 'NONE'}")
print(f"Sample gold DOI: {list(gold_dois)[0] if gold_dois else 'NONE'}")

# Load Scopus data
with open('benchmark_outputs/Li_2024/details_20260203-213731.json', 'r') as f:
    details = json.load(f)

scopus_data = details[0]['provider_details']['scopus']
db_ids = set(scopus_data.get('retrieved_ids', []))
db_dois = set(scopus_data.get('retrieved_dois', []))

print("\n=== SCOPUS RETRIEVED DATA ===")
print(f"db_ids (Scopus IDs): {len(db_ids)} items")
print(f"db_dois: {len(db_dois)} items")
print(f"Sample db_id: {list(db_ids)[0] if db_ids else 'NONE'}")
print(f"Sample db_doi: {list(db_dois)[0] if db_dois else 'NONE'}")

# Call the function
print("\n=== CALLING set_metrics_multi_key ===")
metrics = set_metrics_multi_key(db_ids, db_dois, gold_pmids, gold_dois)

print("\n=== RESULTS ===")
print(f"TP: {metrics['TP']}")
print(f"Recall: {metrics['Recall']}")
print(f"Precision: {metrics['Precision']}")
print(f"matches_by_doi: {metrics['matches_by_doi']}")
print(f"matches_by_pmid_fallback: {metrics['matches_by_pmid_fallback']}")
print(f"Retrieved: {metrics['Retrieved']}")
print(f"Gold: {metrics['Gold']}")
