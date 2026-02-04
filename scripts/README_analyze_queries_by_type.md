# Query Type Analysis Script

## Overview

The `analyze_queries_by_type.py` script aggregates query performance metrics by query semantic type (High-recall, Balanced, High-precision, etc.) across all databases (PubMed, Scopus, Web of Science, Embase).

This provides insights into how different query strategies perform when combining results from multiple databases, answering questions like:
- Does the High-recall query maintain its advantage across all databases?
- Which query type provides the best multi-database coverage?
- How does average recall compare between query strategies?

## Prerequisites

- Workflow must be complete (query execution and evaluation done)
- Per-database summary file must exist: `benchmark_outputs/<STUDY_NAME>/summary_per_database_*.csv`
- Query files should have descriptive comments like:
  ```
  # Query 1: High-recall - Broad MeSH terms...
  # Query 2: Balanced - Mix of approaches...
  # Query 3: High-precision - Focused terms...
  ```

## Usage

### Basic Usage (All Query Types)

```bash
python scripts/analyze_queries_by_type.py <STUDY_NAME>
```

Example:
```bash
python scripts/analyze_queries_by_type.py Medeiros_2023
```

Output:
```
====================================================================================================
Query Performance Aggregated by Type Across All Databases
====================================================================================================

Query 1: High-recall
--------------------------------------------------------------------------------
  Databases: embase+pubmed+scopus (3 total)
  Total Results (before dedup): 22,746
  Best Recall Achieved: 100.0% (6/6 gold studies)
  Average Recall: 94.4%

Query 2: Balanced
--------------------------------------------------------------------------------
  Databases: embase+pubmed+scopus (3 total)
  Total Results (before dedup): 1,998
  Best Recall Achieved: 16.7% (1/6 gold studies)
  Average Recall: 11.1%
```

### Detailed Breakdown (Per-Database Stats)

```bash
python scripts/analyze_queries_by_type.py <STUDY_NAME> --detailed
```

Output includes per-database metrics:
```
Query 1: High-recall
--------------------------------------------------------------------------------
  Databases: embase+pubmed+scopus (3 total)
  Total Results (before dedup): 22,746
  Best Recall Achieved: 100.0% (6/6 gold studies)
  Average Recall: 94.4%

  Per-Database Breakdown:
    • EMBASE: 17,990 results, 6 TP, 100.0% recall
    • PUBMED: 1,188 results, 5 TP, 83.3% recall
    • SCOPUS: 3,568 results, 6 TP, 100.0% recall
```

### Filter Specific Query Types

```bash
python scripts/analyze_queries_by_type.py <STUDY_NAME> --query-types "High-recall,Balanced"
```

Shows only the specified query types.

### Export to CSV

```bash
python scripts/analyze_queries_by_type.py <STUDY_NAME> --output results.csv
```

Saves detailed results to CSV file while also printing summary to console.

## Command-Line Options

| Option | Description |
|--------|-------------|
| `study_name` | (Required) Study name (e.g., Medeiros_2023) |
| `--query-types TYPES` | Comma-separated list of query types to analyze (default: all) |
| `--detailed` | Show detailed per-database breakdown |
| `--output FILE` or `-o FILE` | Export results to CSV file |
| `--benchmark-dir DIR` | Benchmark outputs directory (default: benchmark_outputs) |

## Interpreting Results

### Key Metrics

- **Databases**: Which databases contributed to this query type (e.g., `embase+pubmed+scopus`)
- **Total Results (before dedup)**: Sum of results across all databases (before deduplication)
- **Best Recall Achieved**: Highest recall observed in any single database
- **Average Recall**: Mean recall across all databases
- **Gold Size**: Total number of studies in gold standard

### What to Look For

1. **High-recall queries should show:**
   - Best Recall close to 100%
   - Consistently high Average Recall (>90%)
   - Large Total Results count

2. **Balanced queries should show:**
   - Moderate Best Recall (60-95%)
   - Smaller Total Results than High-recall
   - Good coverage across databases

3. **High-precision queries should show:**
   - Variable Best Recall (depends on strategy)
   - Lowest Total Results
   - May have lower recall but very focused results

### Cross-Database Insights

The per-database breakdown reveals:
- **Database-specific strengths**: Some databases may excel for certain topics
- **Coverage gaps**: Queries that work well in one database but not others
- **Complementary value**: Whether combining databases truly improves coverage

## Examples

### Compare High-Recall vs Balanced Strategies

```bash
python scripts/analyze_queries_by_type.py Medeiros_2023 \
  --query-types "High-recall,Balanced" \
  --detailed
```

### Export Full Analysis for All Query Types

```bash
python scripts/analyze_queries_by_type.py Godos_2024 \
  --output query_analysis_godos_2024.csv \
  --detailed
```

### Quick Check: Which Query Type Has Best Multi-DB Coverage?

```bash
python scripts/analyze_queries_by_type.py Li_2024 | grep "Best Recall"
```

## Integration with Workflow

This script is automatically suggested after running the complete workflow:

```bash
bash scripts/run_complete_workflow.sh <STUDY_NAME> --multi-key

# At the end, you'll see:
# 4. (Optional) Analyze query performance by type across databases:
#    python scripts/analyze_queries_by_type.py <STUDY_NAME> --detailed
```

## Troubleshooting

### Error: "Study directory not found"

Ensure the study exists:
```bash
ls studies/<STUDY_NAME>/
```

### Error: "No per-database summary found"

Run the workflow first:
```bash
bash scripts/run_complete_workflow.sh <STUDY_NAME>
```

### Warning: "Could not extract query types"

Query files need descriptive comments:
```
# Query 1: High-recall - description here
```

Not just:
```
# Query 1
```

### "Unknown" Query Types Appearing

Some databases may have different or missing query type comments. Check:
```bash
grep "^#" studies/<STUDY_NAME>/queries*.txt
```

Ensure all query files have consistent type annotations.

## CSV Output Format

The exported CSV includes these columns:
- `query_num`: Query number (1-6)
- `query_type`: Semantic type (High-recall, Balanced, etc.)
- `databases`: Databases included (e.g., "embase+pubmed+scopus")
- `num_databases`: Count of databases
- `total_results`: Sum of results before deduplication
- `max_TP`: Maximum true positives across databases
- `max_recall`: Best recall achieved
- `avg_recall`: Average recall across databases
- `gold_size`: Gold standard size
- Per-database columns: `<db>_results`, `<db>_TP`, `<db>_recall` for each database

## Related Documentation

- Main workflow: `scripts/run_complete_workflow.sh`
- Skill documentation: `.github/skills/systematic-review-queries-to-results/SKILL.md`
- Query generation: `.github/skills/systematic-review-pdf-to-queries/SKILL.md`
