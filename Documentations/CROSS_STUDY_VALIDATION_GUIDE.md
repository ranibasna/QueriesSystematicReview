# Cross-Study Validation Framework: Architecture & User Guide

**Version**: 1.0  
**Date**: January 23, 2026  
**Status**: Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Directory Structure & Data Flow](#directory-structure--data-flow)
4. [How Everything Connects](#how-everything-connects)
5. [Quick Start](#quick-start)
6. [Detailed Workflows](#detailed-workflows)
7. [Understanding the Output](#understanding-the-output)

---

## Overview

The **Cross-Study Validation Framework** is a meta-analysis system that evaluates aggregation strategy performance across multiple systematic review studies. It answers the critical question: **"Which aggregation strategy works best across different medical domains?"**

### What Problem Does It Solve?

Before this framework:
- Each study was evaluated in isolation
- No way to compare strategy performance across studies
- Strategy selection based on intuition or single-study results
- Unknown whether good performance generalizes to other domains

After this framework:
- Evidence-based strategy recommendations backed by cross-study data
- Statistical analysis of strategy consistency
- Identification of domain-specific vs. universal best practices
- Confidence in methodology choices for new studies

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXISTING WORKFLOW                             │
│                                                                  │
│  studies/                     Individual study files             │
│  ├── Godos_2024/                                                │
│  │   ├── queries.txt          ← Query definitions               │
│  │   ├── gold_pmids_*.csv     ← Gold standard PMIDs            │
│  │   └── ...                                                     │
│  ├── ai_2022/                                                   │
│  └── sleep_apnea/                                               │
│                                                                  │
│                          ↓ [Run Workflow]                       │
│                                                                  │
│  aggregates_eval/             Strategy performance results      │
│  ├── Godos_2024/                                                │
│  │   └── sets_summary_*.csv   ← Recall, precision, F1          │
│  ├── ai_2022/                                                   │
│  └── sleep_apnea/                                               │
│                                                                  │
│  benchmark_outputs/           Individual query performance      │
│  ├── Godos_2024/                                                │
│  │   └── summary_*.csv        ← Per-query metrics              │
│  └── ...                                                         │
└─────────────────────────────────────────────────────────────────┘

                          ↓ [NEW: Data Collection]

┌─────────────────────────────────────────────────────────────────┐
│              CROSS-STUDY VALIDATION FRAMEWORK                    │
│                                                                  │
│  cross_study_validation/                                        │
│  │                                                               │
│  ├── data/                    ← Standardized study data (JSON)  │
│  │   ├── Godos_2024.json      ← All data for one study         │
│  │   ├── ai_2022.json                                           │
│  │   ├── sleep_apnea.json                                       │
│  │   └── all_studies.json     ← Combined dataset               │
│  │                                                               │
│  ├── schemas/                 ← Data validation                 │
│  │   └── study_result_schema.json                              │
│  │                                                               │
│  ├── analysis/                ← Statistical analysis            │
│  │   └── descriptive_stats.py                                  │
│  │                                                               │
├── reporting/               ← Report & visualization generation│
│   ├── markdown_reporter.py                                  │
│   └── visualizations.py    ← Publication-quality figures   │
│                                                               │
├── reports/                 ← Generated reports               │
│   ├── report_*.md          ← Cross-study findings            │
│   └── figures/             ← Visualizations (PNG, 300 DPI)   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure & Data Flow

### 1. `studies/` - Individual Study Input

**Purpose**: Contains raw study materials and configuration for each systematic review.

**Key Files**:
- `queries.txt` - PubMed queries (6 variations: high-recall, balanced, high-precision)
- `queries_scopus.txt`, `queries_wos.txt`, `queries_embase.txt` - Database-specific queries
- `gold_pmids_<study>.csv` - Gold standard reference list (PMIDs of included studies)
- `prospero_<study>.md`, `paper_<study>.md` - Study documentation

**Example**:
```
studies/Godos_2024/
├── queries.txt                    # 6 PubMed queries
├── queries_scopus.txt             # 6 Scopus queries
├── queries_wos.txt                # 6 WOS queries
├── queries_embase.txt             # 6 Embase queries
├── gold_pmids_Godos_2024.csv      # 23 gold standard PMIDs
├── prospero_Godos_2024.md         # PROSPERO protocol
└── paper_Godos_2024.md            # Published paper
```

### 2. `aggregates_eval/` - Strategy Performance Results

**Purpose**: Output from running the workflow - contains performance metrics for each aggregation strategy.

**Generated By**: Running `run_workflow.sh` or `llm_sr_select_and_score.py`

**Key Files**:
- `sets_summary_<timestamp>.csv` - Performance of each aggregation strategy
  - Columns: name, TP, Retrieved, Gold, Precision, Recall, F1, Jaccard, OverlapCoeff

**Example**:
```
aggregates_eval/Godos_2024/sets_summary_20260122-091122.csv

name,TP,Retrieved,Gold,Precision,Recall,F1
consensus_k2,20,5339,23,0.0037,0.8696,0.0075
precision_gated_union,23,25331,23,0.0009,1.0,0.0018
...
```

**Aggregation Strategies**:
1. `consensus_k2` - Articles found by ≥2 queries
2. `consensus_k3` - Articles found by ≥3 queries
3. `two_stage_screen` - Two-phase screening approach
4. `precision_gated_union` - Union of high-precision queries
5. `time_stratified_hybrid` - Temporal-based hybrid
6. `weighted_vote` - Weighted voting mechanism

### 3. `benchmark_outputs/` - Individual Query Performance

**Purpose**: Performance metrics for each individual query (not aggregated).

**Generated By**: Same workflow as `aggregates_eval/`

**Key Files**:
- `summary_<timestamp>.csv` - Per-query performance
  - Columns: query, results_count, TP, gold_size, recall, NNR_proxy

**Example**:
```
benchmark_outputs/Godos_2024/summary_20260122-091116.csv

query,results_count,TP,gold_size,recall,NNR_proxy
"((Diet, Mediterranean[Mesh] OR ...",22184,21,23,0.9130,1056.38
...
```

### 4. `cross_study_validation/` - Meta-Analysis Framework (NEW)

**Purpose**: Standardizes data from multiple studies and performs cross-study analysis.

#### 4a. `cross_study_validation/data/` - Standardized Study Data

**Generated By**: Running `scripts/collect_study_results.py`

**Format**: JSON files conforming to `schemas/study_result_schema.json`

**Contents**:
```json
{
  "study_id": "Godos_2024",
  "metadata": {
    "domain": "nutrition",
    "databases": ["pubmed", "scopus", "wos", "embase"],
    "gold_size": 23,
    "date_range": {"start": "1990-01-01", "end": "2023-12-31"}
  },
  "gold_standard": {
    "pmids": ["20808113", "28364422", ...],
    "count": 23
  },
  "aggregation_strategies": [
    {
      "name": "precision_gated_union",
      "recall": 1.0,
      "precision": 0.0009,
      "f1": 0.0018,
      "retrieved_count": 25331,
      "true_positives": 23
    },
    ...
  ],
  "query_performance": [...],
  "source_files": {
    "aggregates_csv": "aggregates_eval/Godos_2024/sets_summary_20260122-091122.csv",
    "benchmark_csv": "benchmark_outputs/Godos_2024/summary_20260122-091116.csv",
    "gold_standard_csv": "studies/Godos_2024/gold_pmids_Godos_2024.csv"
  }
}
```

#### 4b. `cross_study_validation/reports/` - Generated Reports & Visualizations

**Generated By**: Running `python -m cross_study_validation run` or individual commands

**Contents**: 

**Markdown Reports** (`report_*.md`):
- Executive summary
- Study characteristics comparison
- Strategy performance tables (mean, std, min, max)
- Best strategy recommendations
- Per-study breakdowns
- Evidence-based conclusions

**Visualizations** (`figures/` directory):
- Box plots showing recall/precision/F1 distributions
- Bar charts with error bars for strategy comparison
- Scatter plots for precision-recall tradeoffs
- Heatmaps for strategy performance by study/domain
- Publication-quality PNG files (300 DPI)

---

## How Everything Connects

### Data Flow Diagram

```
Step 1: Individual Study Workflow
═══════════════════════════════════════════════════════════════

studies/Godos_2024/
  ├── queries.txt                [INPUT: Query definitions]
  └── gold_pmids_*.csv           [INPUT: Gold standard]

         ↓ [Run: run_workflow.sh]

aggregates_eval/Godos_2024/
  └── sets_summary_*.csv         [OUTPUT: Strategy results]

benchmark_outputs/Godos_2024/
  └── summary_*.csv              [OUTPUT: Query results]


Step 2: Cross-Study Collection (Repeat for each study)
═══════════════════════════════════════════════════════════════

[Run: scripts/collect_study_results.py --all-studies]

         ↓ [Reads from 3 sources:]

  studies/          aggregates_eval/     benchmark_outputs/
  └── */gold_*.csv  └── */sets_*.csv    └── */summary_*.csv

         ↓ [Standardizes & validates]

cross_study_validation/data/
  ├── Godos_2024.json          [Standardized study data]
  ├── ai_2022.json
  ├── sleep_apnea.json
  └── all_studies.json         [Combined dataset]


Step 3: Cross-Study Analysis
═══════════════════════════════════════════════════════════════

cross_study_validation/data/all_studies.json

         ↓ [Run: reporting/markdown_reporter.py]

cross_study_validation/analysis/
  └── descriptive_stats.py     [Calculate statistics]

         ↓

cross_study_validation/reports/
  └── report_*.md              [Comprehensive report]
```

### Connection Summary

| Folder | Role | Input | Output |
|--------|------|-------|--------|
| `studies/` | Individual study configuration | User-created queries & gold standards | Feeds into workflow |
| `aggregates_eval/` | Strategy performance results | Generated by workflow | Read by collection script |
| `benchmark_outputs/` | Query performance results | Generated by workflow | Read by collection script |
| `cross_study_validation/data/` | Standardized study data | Collected from above 3 sources | Feeds into analysis |
| `cross_study_validation/reports/` | Cross-study findings | Generated from standardized data | Final output |

---

## Quick Start

### Prerequisites

Ensure you have:
1. Completed workflows for at least 2 studies (so `aggregates_eval/` and `studies/` are populated)
2. Activated conda environment: `conda activate systematic_review_queries`
3. Installed jsonschema: `pip install jsonschema` (already done)

### Workflow

**Complete Workflow (Recommended)**
```bash
cd /path/to/QueriesSystematicReview

# Run everything: collect + analyze + visualize
python -m cross_study_validation run
```

**Output**: 
- Creates `cross_study_validation/data/<study>.json` files
- Creates `cross_study_validation/reports/report_<timestamp>.md`
- Creates `cross_study_validation/reports/figures/*.png` (6 visualizations)

---

**Step-by-Step Workflow**

**Step 1: Collect Data from All Studies**
```bash
# Collect all available studies
python -m cross_study_validation collect --all

# Or collect single study
python -m cross_study_validation collect --study Godos_2024
```

**Output**: Creates `cross_study_validation/data/<study>.json` files

**Step 2: Generate Analysis Report**
```bash
# Generate cross-study analysis report
python -m cross_study_validation analyze
```

**Output**: Creates `cross_study_validation/reports/report_<timestamp>.md`

**Step 3: Generate Visualizations**
```bash
# Generate publication-quality figures
python -m cross_study_validation visualize
```

**Output**: Creates 6 PNG files in `cross_study_validation/reports/figures/`:
- `boxplot_recall.png` - Recall distribution by strategy
- `boxplot_precision.png` - Precision distribution by strategy  
- `boxplot_f1.png` - F1 score distribution by strategy
- `bar_chart_comparison.png` - Strategy comparison with error bars
- `scatter_precision_recall.png` - Precision vs recall tradeoffs
- `heatmap_recall_by_study.png` - Performance matrix by study

**Step 4: Review Results**
```bash
# View the report
cat cross_study_validation/reports/report_*.md

# Or open in markdown viewer
open cross_study_validation/reports/report_*.md

# View visualizations
open cross_study_validation/reports/figures/
```

---

## Detailed Workflows

### Adding a New Study to the Analysis

When you complete a new systematic review study:

1. **Run the standard workflow** for the new study
   ```bash
   ./run_workflow.sh <new_study_name>
   ```
   
   This populates:
   - `aggregates_eval/<new_study>/`
   - `benchmark_outputs/<new_study>/`

2. **Collect the new study's data**
   ```bash
   python -m cross_study_validation collect --study <new_study_name>
   ```
   
   This creates:
   - `cross_study_validation/data/<new_study>.json`

3. **Re-run the cross-study analysis** (now includes new study)
   ```bash
   python -m cross_study_validation run
   ```
   
   This updates:
   - All JSON data files
   - Analysis report with new study included
   - All visualizations with updated data

### Understanding Multiple Runs

If you've run the workflow multiple times for a study, you'll see multiple CSV files with timestamps:
```
aggregates_eval/Godos_2024/
├── sets_summary_20260115-143544.csv
├── sets_summary_20260120-153106.csv
└── sets_summary_20260122-091122.csv  ← Most recent
```

**The collection script automatically selects the most recent file** based on modification timestamp.

---

## Understanding the Output

### Example Report Structure

```markdown
# Cross-Study Validation Report

## Executive Summary
- Analyzes 5 strategies across 3 studies
- Total 48 gold standard articles
- Key finding: precision_gated_union achieves 100% recall in 2/3 studies

## Study Characteristics
| Study | Domain | Gold Size |
|-------|--------|-----------|
| Godos_2024 | nutrition | 23 |
| ai_2022 | artificial intelligence | 14 |
| sleep_apnea | sleep medicine | 11 |

## Strategy Performance Summary
| Strategy | Mean Recall | Mean Retrieved | Perfect Recall |
|----------|-------------|----------------|----------------|
| precision_gated_union | 78.6% ± 37.1% | 9283 ± 13916 | 2/3 |
| consensus_k2 | 50.0% ± 32.3% | 1966 ± 2928 | 0/3 |

## Recommended Strategy
**precision_gated_union** - Achieves highest mean recall while balancing 
retrieval burden across diverse domains.
```

### Key Metrics Explained

- **Recall**: % of gold standard articles found (sensitivity)
- **Precision**: % of retrieved articles that are relevant
- **F1**: Harmonic mean of precision and recall
- **Retrieved**: Total number of articles to screen
- **Perfect Recall**: Studies where recall = 100%

---

## Troubleshooting

### "No studies found"
**Cause**: `aggregates_eval/` directory is empty  
**Solution**: Run individual study workflows first

### "CSV file not found"
**Cause**: Study workflow incomplete  
**Solution**: Ensure both `aggregates_eval/` and `benchmark_outputs/` have files

### "Validation failed"
**Cause**: Data doesn't match schema  
**Solution**: Check `cross_study_validation/schemas/study_result_schema.json`

---

## Technical Details

### JSON Schema
All collected data validates against `cross_study_validation/schemas/study_result_schema.json`:
- Ensures data consistency
- Validates PMID formats
- Required fields enforcement
- Type checking

### Modules

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `cross_study_validation/collectors/parsers/csv_parsers.py` | Parse CSV files | `AggregatesCSVParser`, `BenchmarkCSVParser` |
| `cross_study_validation/collectors/parsers/gold_standard_parser.py` | Extract PMIDs | `GoldStandardExtractor` |
| `cross_study_validation/collectors/parsers/metadata_collector.py` | Infer study metadata | `MetadataCollector` |
| `cross_study_validation/collectors/collect_study_results.py` | Orchestrate collection | CLI entry point |
| `cross_study_validation/analysis/descriptive_stats.py` | Calculate statistics | `DescriptiveStats` |
| `cross_study_validation/reporting/markdown_reporter.py` | Generate reports | `MarkdownReporter` |
| `cross_study_validation/reporting/visualizations.py` | Generate visualizations | `VisualizationGenerator` |
| `cross_study_validation/__main__.py` | Unified CLI | Command dispatcher |

---

## Implementation Status

Completed phases:
- ✅ Phase 1: Data collection & standardization (Complete)
- ✅ Phase 2: Descriptive statistics & reporting (Complete)
- ✅ Phase 3: Visualizations (Complete - box plots, bar charts, scatter plots, heatmaps)

Planned phases:
- ⏳ Phase 4: Statistical inference (t-tests, confidence intervals, effect sizes)
- ⏳ Phase 5: Correlation analysis (domain effects, database effects, study characteristics)

### Phase 3 Features

The visualization module generates 6 publication-quality figures:

1. **Box Plots** (3 files): Show distribution of recall, precision, and F1 across studies for each strategy
2. **Bar Chart**: Compare mean performance with error bars (±SD) across all strategies
3. **Scatter Plot**: Visualize precision-recall tradeoffs for each strategy
4. **Heatmap**: Display strategy performance by study/domain with color-coded recall values

All figures are:
- 300 DPI resolution (publication-ready)
- Customizable color palettes
- Professional styling with labels, grids, and legends
- Generated in <3 seconds

---

## Questions?

See also:
- [Documentations/plans/cross_study_validation_framework_plan.md](../Documentations/plans/cross_study_validation_framework_plan.md) - Original design plan
- [Documentations/tasks/cross_study_validation_tasks.md](../Documentations/tasks/cross_study_validation_tasks.md) - Implementation tasks
- [cross_study_validation/README.md](README.md) - Quick reference

**Generated**: January 23, 2026
