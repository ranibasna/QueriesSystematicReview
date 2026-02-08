#!/usr/bin/env python3
import pandas as pd
import re

def extract_query_type_from_comment(comment: str):
    if not comment or not isinstance(comment, str):
        return None
    comment = comment.lstrip('#').strip()
    match = re.match(r'Query\s+\d+\s*-\s*(.+?)(?:\s*:\s+|\s*$)', comment, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

# Parse query types
query_types = {}
with open('studies/Li_2024/queries.txt', 'r') as f:
    lines = f.readlines()

query_num = 0
current_comment = None
for line in lines:
    line = line.strip()
    if line.startswith('#'):
        current_comment = line
        continue
    if line and not line.startswith('#'):
        query_num += 1
        if current_comment:
            query_type = extract_query_type_from_comment(current_comment)
            if query_type:
                if query_num not in query_types:
                    query_types[query_num] = {}
                query_types[query_num]['pubmed'] = query_type
        current_comment = None

print("Query types extracted:", query_types)
print()

# Load data
df = pd.read_csv('benchmark_outputs/Li_2024/summary_per_database_20260204-080252.csv')
combined_df = df[df['database'] == 'COMBINED'].copy()

# Add query type to combined
combined_df['query_type'] = combined_df['query_num'].apply(
    lambda qnum: next(
        (qt for qt in query_types.get(qnum, {}).values()),
        'Unknown'
    )
)

print("Combined df with query types:")
print(combined_df[['query_num', 'query_type', 'results_count', 'TP', 'recall']])
print()

# Filter for High-recall
high_recall = combined_df[combined_df['query_type'] == 'High-recall']
print("High-recall rows in combined_df:")
print(high_recall[['query_num', 'query_type', 'results_count', 'TP', 'recall']])
print()
print("Is empty?", high_recall.empty)
