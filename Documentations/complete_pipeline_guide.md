---
title: "Complete Systematic Review Pipeline Guide"
subtitle: "A comprehensive, step-by-step technical walkthrough of the multi-database systematic review workflow"
author: "Systematic Review Queries Project"
date: "January 15, 2026"
format:
  html:
    toc: true
    toc-depth: 4
    toc-location: left
    toc-title: "Pipeline Steps"
    number-sections: true
    number-depth: 3
    code-fold: false
    code-tools: true
    code-block-bg: true
    code-block-border-left: "#31BAE9"
    theme: cosmo
    smooth-scroll: true
    link-external-newwindow: true
---

# Complete Systematic Review Pipeline Guide

## Table of Contents

1. [Overview & Architecture](#overview--architecture)
2. [Prerequisites & Setup](#prerequisites--setup)
3. [Step 1: Study Initialization](#step-1-study-initialization)
4. [Step 2: LLM-Powered Multi-Database Query Generation](#step-2-llm-powered-multi-database-query-generation)
5. [Step 3: Manual Query Design & Generation](#step-3-manual-query-design--generation)
6. [Step 4: Embase Manual Export & Import](#step-4-embase-manual-export--import)
7. [Step 4.5: Automated Gold Standard Generation](#step-45-automated-gold-standard-generation-optional)
8. [Step 5: Multi-Database Query Execution](#step-5-multi-database-query-execution)
9. [Step 6: Query Evaluation & Selection](#step-6-query-evaluation--selection)
10. [Step 7: Results Aggregation](#step-7-results-aggregation)
11. [Step 8: Performance Scoring](#step-8-performance-scoring)
12. [Understanding the Outputs](#understanding-the-outputs)
13. [Complete Workflow Examples](#complete-workflow-examples)
14. [Troubleshooting & Best Practices](#troubleshooting--best-practices)

---

## Overview & Architecture

### Pipeline Goals

This systematic review pipeline automates:
1. **Multi-database literature search** across PubMed, Scopus, Web of Science, and Embase
2. **Query optimization** at multiple precision levels (high-recall, balanced, high-precision)
3. **Automatic deduplication** using DOI-based matching
4. **Performance evaluation** against gold standard datasets
5. **Aggregation strategies** to combine multiple queries effectively
6. **Cross-study meta-analysis** to evaluate strategy performance across multiple reviews

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Input Layer                               │
│  • Study-specific queries (queries.txt, queries_scopus.txt) │
│  • Gold standard PMIDs (gold_pmids_<study>.csv)             │
│  • Concept terms (concept_terms_<study>.csv)                │
│  • Embase manual exports (embase_query*.csv)                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                 Query Execution Layer                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │ PubMed  │  │ Scopus  │  │   WOS   │  │ Embase  │       │
│  │  (API)  │  │  (API)  │  │  (API)  │  │(Manual) │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Deduplication Layer (DOI-based)                 │
│  • Merge duplicate articles across databases                │
│  • Cross-reference PMIDs                                     │
│  • Preserve source metadata                                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                 Aggregation Layer                            │
│  • Consensus strategies (k=2, k=3)                          │
│  • Union strategies (precision-gated)                        │
│  • Hybrid strategies (time-stratified)                       │
│  • Voting mechanisms (weighted)                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  Evaluation Layer                            │
│  • Per-database metrics (PubMed, Scopus, WOS, Embase)      │
│  • Multi-key matching (DOI-primary with PMID fallback)     │
│  • Precision, Recall, F1-score per query and database      │
│  • Set-level performance metrics                             │
│  • Gold standard validation (auto-detects detailed format)  │
│  • Auto-enables DOI matching when detailed gold std found   │
└─────────────────────────────────────────────────────────────┘
```

### Key Concepts

**DOI-Based Deduplication**: ~96% of modern articles have DOIs. The system uses DOIs as the primary key for identifying duplicate articles across databases.

**Query Precision Levels**:
- **High-recall**: Broad terms, maximizes sensitivity (finds all relevant articles + many irrelevant)
- **Balanced**: Mix of controlled vocabulary and free text with filters
- **High-precision**: Focused terms, maximizes specificity (finds fewer but more relevant articles)

**Multi-Key Matching Strategy**:
- **Auto-detection**: Workflow automatically detects if `gold_pmids_<study>_detailed.csv` exists (with DOI column)
- **DOI-primary matching**: When detailed gold standard found, uses DOI as primary key, PMID as fallback
- **Why important**: Scopus/WOS return DOIs (not PMIDs), so DOI matching is essential for accurate recall
- **Performance impact**: Without DOI matching, Scopus/WOS show 0% recall; with DOI matching, 90-100% recall
- **Automatic activation**: The main wrapper enables multi-key matching automatically when a detailed gold standard is detected

**Study-Specific Structure**: All files organized under `studies/<study_name>/` for portability and clarity.

---

## Prerequisites & Setup

### System Requirements

```bash
# Required software
- Python 3.11+
- Conda/Miniconda
- Git (for version control)

# API Access (optional but recommended)
- PubMed: Free (NCBI Entrez)
- Scopus: Requires institutional subscription
- Web of Science: Requires institutional subscription
- Embase: Manual export (no API in this workflow)
```

### Environment Setup

**Step 1: Clone Repository**
```bash
git clone https://github.com/ranibasna/QueriesSystematicReview.git
cd QueriesSystematicReview
```

**Step 2: Create Conda Environment**
```bash
# Create environment from environment.yml
conda env create -f environment.yml

# Activate environment
conda activate systematic_review_queries

# Verify installation
python -c "import Bio; print('Biopython installed')"
```

**Step 3: Configure API Keys**

Create a `.env` file in the project root:

```bash
# .env file
# PubMed (free, but API key increases rate limit)
NCBI_EMAIL=your.email@institution.edu
NCBI_API_KEY=your_ncbi_api_key_optional

# Scopus (requires subscription)
SCOPUS_API_KEY=your_scopus_api_key
SCOPUS_INSTTOKEN=your_institution_token_optional

# Web of Science (requires subscription)
WOS_API_KEY=your_wos_api_key

# Skip date filters for Scopus (recommended due to API limitations)
SCOPUS_SKIP_DATE_FILTER=true
```

The main wrapper uses `pubmed,scopus,wos` by default. Override that provider set with `--databases` when you run `bash scripts/run_complete_workflow.sh <study>`.

**Flag Explanations**:
- `NCBI_EMAIL`: Required by NCBI to contact you if there are issues
- `NCBI_API_KEY`: Optional, increases rate limit from 3 to 10 requests/second
- `SCOPUS_INSTTOKEN`: Optional, institution-specific token for enhanced access
- `SCOPUS_SKIP_DATE_FILTER`: Recommended `true` - Scopus API date filtering has known issues

---

## Step 1: Study Initialization

### Creating a New Study

Every systematic review is a "study" with its own directory structure.

**Directory Structure**:
```
studies/
└── sleep_apnea/                          # Your study name
    ├── queries.txt                       # PubMed queries (6 queries)
    ├── queries_scopus.txt                # Scopus queries (6 queries)
  ├── queries_wos.txt                   # Web of Science queries (6 queries)
  ├── queries_embase.txt                # Embase queries (6 queries)
    ├── concept_terms_sleep_apnea.csv     # Concepts for query generation
    ├── gold_pmids_sleep_apnea.csv        # Gold standard PMIDs
    ├── embase_query1.csv                 # Embase manual exports (optional)
    ├── embase_query2.csv
    └── ...
```

**Create Study Directory**:
```bash
# Create directory structure
mkdir -p studies/sleep_apnea

# Navigate to study directory
cd studies/sleep_apnea
```

---

## Step 2: LLM-Powered Multi-Database Query Generation

### Overview

The current query-generation system is strategy-aware. It reads the study protocol plus shared guidance, selects a retrieval architecture, and writes aligned six-query families for each requested database.

### Architecture: Current Strategy-Aware Stack

```
┌───────────────────────────────────────────────────────────────┐
│                    INPUT LAYER                                │
│  • studies/<study>/prospero_<study>.md                       │
│  • studies/guidelines.md                                     │
│  • studies/general_guidelines.md                             │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│                  TEMPLATE LAYER                               │
│  • prompts/prompt_template_multidb_strategy_aware.md         │
│  • prompts/database_guidelines_strategy_aware.md             │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│                GENERATOR LAYER                                │
│  • /generate_multidb_prompt                                  │
│  • /generate-multidb-prompt                                  │
│  • parameterized by relaxation_profile                       │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│                 EXECUTION LAYER                               │
│  • /run_<study>_multidb_strategy                             │
│  • selects architecture, builds Q1-Q6, applies json_patch    │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│                   OUTPUT LAYER                                │
│  • studies/<study>/search_strategy.md                        │
│  • studies/<study>/queries.txt                               │
│  • studies/<study>/queries_scopus.txt                        │
│  • studies/<study>/queries_wos.txt                           │
│  • studies/<study>/queries_embase.txt                        │
└───────────────────────────────────────────────────────────────┘
```

### Step 2.1: Prepare Study Inputs

Before generating queries, make sure you have:

1. The study protocol markdown from Step 1.
2. The shared study guidance file `studies/guidelines.md`.
3. The shared general guidance file `studies/general_guidelines.md`.

### Step 2.2: Generate a Runnable Command

You can generate the study-specific runnable command through either supported path.

**Gemini CLI**

```bash
/generate_multidb_prompt \
  --command_name run_sleep_apnea_multidb_strategy \
  --protocol_path studies/sleep_apnea/prospero-sleep-apnea-dementia.md \
  --databases pubmed,scopus,wos,embase \
  --relaxation_profile default \
  --min_date "" \
  --max_date "2021/03/01"
```

**VS Code Copilot Chat**

```text
/generate-multidb-prompt run_sleep_apnea_multidb_strategy studies/sleep_apnea/prospero-sleep-apnea-dementia.md pubmed,scopus,wos,embase default "" 2021/03/01
```

#### Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `command_name` | Name for the generated runnable command | `run_sleep_apnea_multidb_strategy` |
| `protocol_path` | Path to the protocol markdown | `studies/sleep_apnea/prospero-sleep-apnea-dementia.md` |
| `databases` | Comma-separated database list | `pubmed,scopus,wos,embase` |
| `relaxation_profile` | Strategy-aware recall/precision bias | `default` |
| `min_date` | Start of search window | `1990/01/01` or empty for inception |
| `max_date` | End of search window | `2021/03/01` |

`relaxation_profile` replaces the retired level-based generation model. The current strategy-aware path is fixed to the latest six-query family and does not use `basic`, `extended`, `keywords`, or `exhaustive` as the main workflow contract.

### Step 2.3: Execute the Generated Command

```bash
/run_sleep_apnea_multidb_strategy
```

When executed, the generated command:

1. Classifies the retrieval architecture.
2. Builds the concept tables and aligned `Q1` to `Q6` query families for each requested database.
3. Produces a single JSON query object keyed by database, then applies any `json_patch` corrections.
4. Writes `search_strategy.md` with the architecture summary, concept tables, JSON query object, `json_patch`, and translation notes.
5. Writes the final query files directly to the study folder.

### Step 2.4: Verify Generated Outputs

```bash
ls studies/sleep_apnea/search_strategy.md
ls studies/sleep_apnea/queries*.txt
```

Things to verify:

- The command wrote `search_strategy.md` automatically, including the JSON query object and any `json_patch` block.
- The command wrote aligned `queries*.txt` files automatically.
- The query families remain aligned across databases.
- Manual JSON copying is not required in the current workflow.

If an older generated `run_*_multidb*.toml` or `.prompt.md` file still references `prompt_template_multidb.md`, `database_guidelines.md`, or `--level`, regenerate it before continuing.

### Step 2.5: Compare With Manual Query Design

| Aspect | Current Strategy-Aware Generation | Manual Design (Step 3) |
|--------|-----------------------------------|------------------------|
| Time required | ~5-10 minutes plus review | ~2-4 hours per database |
| Source of truth | Protocol + shared guidance + strategy-aware template | Human-authored logic |
| Output shape | Fixed aligned Q1-Q6 family | Fully custom |
| Best use | Fast, consistent cross-database starting point | Expert refinement and edge cases |

Recommendation: use Step 2 to generate the baseline query family, then refine manually in Step 3 if the study needs tighter control.

---

## Step 3: Manual Query Design & Generation

### Understanding Query Files

Each database requires database-specific syntax:

| Database | Query File | Syntax Features |
|----------|-----------|-----------------|
| **PubMed** | `queries.txt` | MeSH terms, `[MeSH]`, `[tiab]`, Boolean operators |
| **Scopus** | `queries_scopus.txt` | `TITLE-ABS-KEY()`, `DOCTYPE()`, parentheses grouping |
| **Web of Science** | `queries_wos.txt` | `TS=()`, `TI=()`, Boolean AND/OR/NOT |
| **Embase** | `queries_embase.txt` | Emtree terms, `/exp`, `:ti,ab`, `[article]/lim` |

### Query File Format

**All query files follow the same format**:

```
# Comment line describing query 1
(query text here with database-specific syntax)

# Comment line describing query 2  
(another query with database-specific syntax)

# Comment line describing query 3
(third query)
```

**Rules**:
- Blank lines separate queries
- `#` lines are comments (descriptive only)
- Each query can span multiple lines
- Queries must match across files (query 1 in all files = same precision level)

### Example: PubMed Queries (queries.txt)

```
# High-recall: Broad MeSH terms and text words to maximize sensitivity
("Sleep Apnea Syndromes"[MeSH] OR "sleep apnea"[tiab] OR "sleep apnoea"[tiab] OR "sleep disordered breathing"[tiab] OR "obstructive sleep apnea"[tiab]) AND ("Dementia"[MeSH] OR dementia[tiab] OR "cognitive decline"[tiab] OR "cognitive impairment"[tiab] OR alzheimer*[tiab]) AND (1990:2021[dp])

# Balanced: Mix of MeSH and text words with study design filter
("Sleep Apnea Syndromes"[MeSH] OR "sleep apnea"[tiab] OR "obstructive sleep apnea"[tiab]) AND ("Dementia"[MeSH] OR "Alzheimer Disease"[MeSH] OR dementia[tiab] OR "cognitive impairment"[tiab] OR alzheimer*[tiab]) AND (cohort[tiab] OR prospective[tiab] OR retrospective[tiab] OR randomized[tiab] OR trial[tiab]) AND (1990:2021[dp])

# High-precision: Focused on major MeSH terms with title search
("Sleep Apnea Syndromes"[MeSH:noexp] OR "sleep apnea"[ti]) AND ("Dementia"[MeSH:noexp] OR "Alzheimer Disease"[MeSH:noexp] OR dementia[ti] OR alzheimer*[ti]) AND (cohort[tiab] OR prospective[tiab] OR trial[tiab]) AND (1990:2021[dp])

# Micro-variant 1: Balanced + human subjects filter
("Sleep Apnea Syndromes"[MeSH] OR "sleep apnea"[tiab] OR "obstructive sleep apnea"[tiab]) AND ("Dementia"[MeSH] OR "Alzheimer Disease"[MeSH] OR dementia[tiab] OR "cognitive impairment"[tiab] OR alzheimer*[tiab]) AND (cohort[tiab] OR prospective[tiab] OR randomized[tiab] OR trial[tiab]) AND "humans"[MeSH] AND (1990:2021[dp])

# Micro-variant 2: Balanced with title restriction on dementia
("Sleep Apnea Syndromes"[MeSH] OR "sleep apnea"[tiab] OR "obstructive sleep apnea"[tiab]) AND ("Dementia"[MeSH] OR "Alzheimer Disease"[MeSH] OR dementia[ti] OR "cognitive impairment"[ti] OR alzheimer*[ti]) AND (cohort[tiab] OR prospective[tiab] OR randomized[tiab] OR trial[tiab]) AND (1990:2021[dp])

# Micro-variant 3: Use of proximity operator for tight association
("sleep apnea"[tiab] OR "obstructive sleep apnea"[tiab]) AND (dementia[tiab] OR "cognitive impairment"[tiab] OR alzheimer*[tiab]) AND (cohort[tiab] OR prospective[tiab] OR randomized[tiab] OR trial[tiab]) AND (1990:2021[dp])
```

**Query Design Philosophy**:
1. **Query 1-3**: Main precision levels (high-recall → balanced → high-precision)
2. **Query 4-6**: Micro-variants testing specific filters or restrictions
3. **Alignment**: Query N in PubMed should match precision level of Query N in Scopus/WOS/Embase

### Example: Embase Queries (queries_embase.txt)

```
# High-recall: Broad Emtree terms and textwords
('sleep apnea syndrome'/exp OR 'sleep apnea':ti,ab OR 'sleep apnoea':ti,ab OR 'sleep disordered breathing':ti,ab) AND ('dementia'/exp OR dementia:ti,ab OR 'cognitive decline':ti,ab OR 'cognitive impairment':ti,ab OR 'alzheimer*':ti,ab OR 'lewy body':ti,ab) AND [1990-2021]/py

# Balanced: Emtree + textwords + study design filter
('sleep apnea syndrome'/exp OR 'sleep apnea':ti,ab OR 'sleep apnoea':ti,ab OR 'apnea-hypopnea index':ti,ab) AND ('dementia'/exp OR 'alzheimer disease'/exp OR dementia:ti,ab OR 'cognitive impairment':ti,ab OR 'alzheimer*':ti,ab) AND ('cohort analysis'/exp OR cohort:ti,ab OR prospective:ti,ab OR retrospective:ti,ab OR 'randomized controlled trial'/exp OR randomi*:ti,ab OR trial:ti,ab) AND [1990-2021]/py

# High-precision: Major focus Emtree terms
('sleep apnea syndrome'/exp OR 'sleep apnea':ti) AND ('dementia'/exp OR dementia:ti OR 'alzheimer*':ti) AND ('cohort analysis'/exp OR cohort:ti,ab OR prospective:ti,ab OR 'randomized controlled trial'/exp OR randomi*:ti,ab OR trial:ti,ab) AND [1990-2021]/py

# Micro-variant 1: Balanced + article/review filter
('sleep apnea syndrome'/exp OR 'sleep apnea':ti,ab OR 'apnea-hypopnea index':ti,ab) AND ('dementia'/exp OR 'alzheimer disease'/exp OR dementia:ti,ab OR 'cognitive impairment':ti,ab OR 'alzheimer*':ti,ab) AND ('cohort analysis'/exp OR cohort:ti,ab OR prospective:ti,ab OR 'randomized controlled trial'/exp OR randomi*:ti,ab OR trial:ti,ab) AND ([article]/lim OR [review]/lim) AND [1990-2021]/py

# Micro-variant 2: Balanced with title restriction
('sleep apnea syndrome'/exp OR 'sleep apnea':ti,ab OR 'apnea-hypopnea index':ti,ab) AND ('dementia'/exp OR 'alzheimer disease'/exp OR dementia:ti OR 'cognitive impairment':ti OR 'alzheimer*':ti) AND ('cohort analysis'/exp OR cohort:ti,ab OR prospective:ti,ab OR 'randomized controlled trial'/exp OR randomi*:ti,ab OR trial:ti,ab) AND [1990-2021]/py

# Micro-variant 3: Proximity operator (may return 0 results)
('sleep apnea syndrome'/exp OR 'sleep apnea':ti,ab) ADJ10 ('dementia'/exp OR dementia:ti,ab OR 'cognitive impairment':ti,ab OR 'alzheimer*':ti,ab) AND ('cohort analysis'/exp OR cohort:ti,ab OR prospective:ti,ab OR 'randomized controlled trial'/exp OR randomi*:ti,ab OR trial:ti,ab) AND [1990-2021]/py
```

**Embase Syntax Notes**:
- `/exp`: Explode term (include all narrower terms)
- `:ti,ab`: Search in title and abstract
- `:ti`: Search in title only
- `/py`: Publication year filter
- `[article]/lim`: Limit to article publication type
- `ADJ10`: Terms within 10 words of each other

### Creating the Gold Standard

The gold standard is a CSV file with PMIDs of known relevant articles.

**File**: `studies/sleep_apnea/gold_pmids_sleep_apnea.csv`

```csv
pmid
12345678
23456789
34567890
45678901
```

**How to create**:
1. Identify relevant articles from prior systematic reviews
2. Extract PMIDs from PubMed
3. Save as CSV with header `pmid`

**Why it's important**: The gold standard is used to calculate precision, recall, and F1-scores for query validation.

### Creating Concept Terms (Optional)

For LLM-assisted query generation:

**File**: `studies/sleep_apnea/concept_terms_sleep_apnea.csv`

```csv
concept,terms
sleep_apnea,"sleep apnea, sleep apnoea, obstructive sleep apnea, OSA, sleep disordered breathing"
dementia,"dementia, Alzheimer, cognitive decline, cognitive impairment, Alzheimer's disease"
study_design,"cohort, prospective, retrospective, randomized, trial, RCT"
```

---

## Step 4: Embase Manual Export & Import

### Why Embase is Special

Embase doesn't provide free API access. You must:
1. Log into Embase.com with institutional credentials
2. Run queries manually
3. Export results as CSV
4. Import CSVs into the workflow

### Exporting from Embase

**Step-by-step process**:

1. **Log into Embase.com**
   ```
   https://www.embase.com
   ```

2. **Run Query**
   - Paste query from `queries_embase.txt` (e.g., query 1)
   - Click "Search"
   - Review results

3. **Export Results**
   - Select all results (or click "Select all")
   - Click **"Export"** button
   - Choose format: **CSV**
   - **CRITICAL FIELDS** (check these boxes):
     - ✅ Title
     - ✅ Author Names
     - ✅ **Digital Object Identifier (DOI)** ← Required
     - ✅ **Medline PMID** ← Required for PubMed cross-reference
   - Click "Export"

4. **Save File**
   - Save as: `studies/sleep_apnea/embase_query1.csv`
   - Repeat for all queries (query2.csv, query3.csv, etc.)

**Important**: If a query returns **zero results**, skip it. The import script handles missing queries automatically.

### Import Single Embase Query

**Command**:
```bash
python scripts/import_embase_manual.py \
  --input studies/sleep_apnea/embase_query1.csv \
  --output studies/sleep_apnea/embase_query1.json \
  --query "('sleep apnea syndrome'/exp OR 'sleep apnea':ti,ab ...) AND [1990-2021]/py"
```

**Parameters**:
- `--input` / `-i`: Path to Embase CSV export
- `--output` / `-o`: Path for output JSON file
- `--query` / `-q`: The exact query you ran (for documentation)

**What it does**:
1. Reads CSV in Embase's "vertical" format (field-value pairs per row)
2. Extracts DOIs and PMIDs from each article
3. Creates JSON in same format as automated database queries
4. Enables deduplication with other databases

**Output**:
```
Reading Embase export from: studies/sleep_apnea/embase_query1.csv

Extracted:
  - 2113 unique DOIs
  - 1412 PMIDs (cross-referenced articles)
  - 2330 total records

✅ Created workflow-compatible JSON:
   studies/sleep_apnea/embase_query1.json
   Query hash: 487a3588
```

### Batch Import Multiple Embase Queries

**Command**:
```bash
python scripts/batch_import_embase.py \
  --study sleep_apnea \
  --csvs studies/sleep_apnea/embase_query1.csv \
         studies/sleep_apnea/embase_query2.csv \
         studies/sleep_apnea/embase_query3.csv \
         studies/sleep_apnea/embase_query4.csv \
         studies/sleep_apnea/embase_query5.csv \
  --queries-file studies/sleep_apnea/queries_embase.txt
```

**Or use wildcard**:
```bash
python scripts/batch_import_embase.py \
  --study sleep_apnea \
  --csvs studies/sleep_apnea/embase_query*.csv \
  --queries-file studies/sleep_apnea/queries_embase.txt
```

**Parameters**:
- `--study`: Study name (creates output in `studies/<study>/`)
- `--csvs`: List of CSV files (space-separated) or wildcard pattern
- `--queries-file`: Path to queries file (matches CSVs with queries)

**What it does**:
1. Counts CSV files and queries
2. If counts don't match (e.g., query 6 had zero results), automatically adjusts
3. Imports each CSV with corresponding query text
4. Creates numbered JSON files: `embase_query1.json`, `embase_query2.json`, etc.

**Output**:
```
⚠️  Warning: Number of CSVs (5) doesn't match number of queries (6)
   This is normal if some queries returned zero results on Embase.
   Will import 5 queries and skip 1 query(ies) with no results.

📋 Batch Import Plan
Study: sleep_apnea
Total queries to import: 5
Output directory: studies/sleep_apnea/

============================================================
Importing: embase_query1.csv
Output:    embase_query1.json
============================================================
Extracted:
  - 2113 unique DOIs
  - 1412 PMIDs
✅ Successfully imported embase_query1.csv

[... repeats for all 5 queries ...]

📊 Batch Import Summary
============================================================
✅ Successfully imported: 5/5

📁 Output files:
   studies/sleep_apnea/embase_query1.json
   studies/sleep_apnea/embase_query2.json
   studies/sleep_apnea/embase_query3.json
   studies/sleep_apnea/embase_query4.json
   studies/sleep_apnea/embase_query5.json
```

### Complete Embase Workflow (All-in-One)

**Command**:
```bash
bash scripts/run_complete_workflow.sh sleep_apnea --databases pubmed,scopus,wos,embase
```

**What it does**:
1. Validates study files and provider query alignment
2. Batch imports all Embase CSV exports it finds
3. Scores queries, aggregates results, and scores combined sets
4. Reuses the main workflow wrapper instead of a separate Embase-only helper

**When to use**: Whenever you want the main wrapper to include imported Embase results.

---

## Step 4.5: Automated Gold Standard Generation (Optional)

### Enhancement: Sampling-Based Extraction

**New Feature**: As of January 24, 2026, the extraction system supports **sampling-based extraction with majority voting** for improved robustness.

#### What is Sampling-Based Extraction?

Instead of running extraction once, the system can:
1. **Run extraction multiple times** (default: 5 runs) with different parameters
2. **Cluster similar studies** across runs using fuzzy matching
3. **Apply majority voting** to accept only studies found in ≥60% of runs
4. **Quantify consistency** with detailed voting statistics

#### When to Use It

✅ **Use sampling when**:
- PDF extraction is unreliable (complex tables, garbled text)
- High-stakes systematic reviews (clinical, safety-critical)
- Known problematic PDFs with intermittent parsing errors
- Budget allows 5x LLM costs (can be parallelized in future)

❌ **Skip sampling when**:
- Standard extraction already works well (e.g., 100% on ai_2022)
- Time/cost constraints
- Simple, well-formatted PDFs

#### Usage

```bash
# Standard extraction (recommended to try first)
python scripts/extract_included_studies.py ai_2022

# Sampling-based extraction (for problematic cases)
python scripts/extract_included_studies.py ai_2022 \
  --sampling-runs 5 \
  --voting-threshold 0.60

# With PMID/DOI lookup
python scripts/extract_included_studies.py ai_2022 \
  --sampling-runs 5 \
  --voting-threshold 0.60 \
  --lookup-pmid \
  --pubmed-email your@email.com

# Full pipeline with sampling
python scripts/extract_included_studies.py ai_2022 \
  --sampling-runs 5 \
  --voting-threshold 0.60 \
  --lookup-pmid \
  --pubmed-email your@email.com \
  --generate-gold-csv
```

#### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--sampling-runs` | None | Number of extraction runs (e.g., 5). Enables sampling mode |
| `--voting-threshold` | 0.60 | Minimum fraction of runs required (0.60 = 3/5 runs) |

#### Output

**File**: `studies/<study>/included_studies_sampling.json`

```json
{
  "study_name": "ai_2022",
  "extraction_method": "sampling_based_with_voting",
  "sampling_parameters": {
    "runs": 5,
    "voting_threshold": 0.60,
    "temperature_schedule": [0.3, 0.5, 0.7, 0.3, 0.5]
  },
  "total_included_studies": 14,
  "voting_statistics": {
    "accepted_count": 14,
    "rejected_count": 0,
    "consistency_rate": 1.0
  }
}
```

#### Performance Example (ai_2022)

```
🎲 Sampling-Based Extraction: ai_2022
   Runs: 5
   Voting threshold: 60% (3/5 required)

🔄 Run 1/5 (temp=0.3, seed=42)...
   → Extracted 14 studies ✓
🔄 Run 2/5 (temp=0.5, seed=142)...
   → Extracted 14 studies ✓
...

✅ Voting complete!
   Accepted: 14 studies (≥3 votes)
   Rejected: 0 studies (<3 votes)
   Consistency rate: 100.0%
```

---

### Standard Automated Gold Standard Generation

### Overview

Before running queries (Step 5), you may need to generate the gold standard CSV files. The automated gold standard extraction system parses your systematic review paper (in markdown format) and automatically looks up DOIs and PMIDs for all included studies.

**When to use this step**:
- You have a published systematic review paper (converted to `.md`)
- You need to create `gold_pmids_<study>.csv` and `gold_pmids_<study>_detailed.csv`
- You want automated extraction instead of manual LLM-based methods

**When to skip this step**:
- You already have `gold_pmids_<study>.csv` and `gold_pmids_<study>_detailed.csv`
- You prefer manual extraction using LLMs (see Automation_guide_main.md STEP 5, Method B)

### Prerequisites

**Required files**:
1. `studies/<study>/paper_<study>.md` - Your systematic review paper in markdown
2. The paper must have:
   - "Table 1: Included Studies" or similar heading
   - References section with numbered citations

**Example structure** (`studies/ai_2022/paper_ai_2022.md`):
```markdown
## Results

### Characteristics of Included Studies

Table 1 summarizes the 14 included studies...

| Study | Population | Intervention | Outcome |
|-------|------------|--------------|---------|
| Li et al., 2008 [12] | Children | OSA treatment | Blood pressure |
| Amin et al., 2004 [14] | Pediatric | CPAP therapy | Cardiovascular |
...

## References

12. Li AM, Au CT, Sung RYT, et al. Ambulatory blood pressure in children 
    with obstructive sleep apnoea: a community based study. Thorax. 
    2008;63(9):803-809. DOI: 10.1136/thx.2007.091132

14. Amin RS, Carroll JL, Jeffries JL, et al. Twenty-four-hour ambulatory 
    blood pressure in children with sleep-disordered breathing. Am J Respir 
    Crit Care Med. 2004;169(8):950-956. PMID: 14764433
...
```

### ONE COMMAND Workflow

**Command**:
```bash
python scripts/extract_included_studies.py ai_2022 \
  --lookup-pmid \
  --generate-gold-csv
```

**This single command does everything**:
1. ✅ Finds "Included Studies" table in `paper_ai_2022.md`
2. ✅ Extracts reference numbers: [12], [14], [35], etc.
3. ✅ Matches to References section
4. ✅ Parses citations → extracts title, author, year, journal
5. ✅ Looks up DOI + PMID via PubMed E-utilities API
6. ✅ Falls back to Europe PMC and CrossRef when PubMed does not resolve an article
7. ✅ Generates `gold_pmids_ai_2022.csv` (simple format)
8. ✅ Generates `gold_pmids_ai_2022_detailed.csv` (multi-key format)
9. ✅ Creates quality report: `gold_generation_report_ai_2022.md`

**Expected runtime**: 5-10 minutes for 40-50 included studies

For most users, the one-command workflow above is the current path. The sub-steps below expose the same phases for technical inspection or debugging.

### Step-by-Step Breakdown

#### Step 4.5.1: Extract Included Studies from Paper

**Command** (extraction only, no API lookups):
```bash
python scripts/extract_included_studies.py ai_2022
```

**What happens**:
```
📄 Reading paper: studies/ai_2022/paper_ai_2022.md

🔍 Finding included studies table...
   ✅ Found table with 14 reference numbers

📚 Parsing References section...
   ✅ Matched 14/14 citations

✅ Extraction complete!
  Output: studies/ai_2022/included_studies.json

Summary:
  - Total included studies: 14
  - With DOI (from paper): 8
  - With PMID (from paper): 6
  - With neither: 0
```

**Output format** (`included_studies.json`):
```json
{
  "study_name": "ai_2022",
  "paper_path": "studies/ai_2022/paper_ai_2022.md",
  "extraction_date": "2026-01-24T10:30:00",
  "total_included_studies": 14,
  "included_studies": [
    {
      "reference_number": 12,
      "first_author": "Li AM",
      "year": 2008,
      "title": "Ambulatory blood pressure in children with obstructive sleep apnoea",
      "journal": "Thorax",
      "doi": null,
      "pmid": null
    },
    {
      "reference_number": 14,
      "first_author": "Amin RS",
      "year": 2004,
      "title": "Twenty-four-hour ambulatory blood pressure in children",
      "journal": "Am J Respir Crit Care Med",
      "doi": null,
      "pmid": "14764433"
    }
  ]
}
```

#### Step 4.5.2: Look Up DOIs and PMIDs

**Command**:
```bash
python scripts/lookup_pmid.py \
  --input studies/ai_2022/included_studies.json \
  --output studies/ai_2022/included_studies_with_identifiers.json \
  --email your.email@institution.edu
```

**What happens**:
```
🔍 Looking up identifiers for 14 studies (multi-tier strategy)...
   Strategy: PubMed → Europe PMC → CrossRef
   Min confidence: 0.80
   Year tolerance: ±1 years

Study 1/14: Li AM (2008)
  Tier 1 [PubMed]: Trying 5 query strategies...
    Strategy 2: Found 1 result
  ✅ [PubMed] PMID: 18388205, DOI: 10.1136/thx.2007.091132
     Confidence: 0.95 ✓

Study 2/14: Amin RS (2004)
  Tier 1 [PubMed]: Trying 5 query strategies...
    Strategy 2: Found 1 result
  ✅ [PubMed] PMID: 14764433, DOI: 10.1164/rccm.200309-1305OC
     Confidence: 0.95 ✓

Study 3/14: Obscure Study (2015)
  Tier 1 [PubMed]: No match (all strategies failed)
  → Trying Europe PMC...
  ✅ [Europe PMC] PMID: 26123456, DOI: 10.1234/example
     Confidence: 0.82 ✓

Study 4/14: Non-Indexed Article (2020)
  Tier 1 [PubMed]: No match
  Tier 2 [Europe PMC]: No match
  → Trying CrossRef...
  ✅ [CrossRef] DOI: 10.9999/obscure-journal
     Confidence: 0.81 ✓

...

📊 Lookup Complete!
   PubMed (Tier 1): 12 studies (85.7%)
   Europe PMC (Tier 2): 1 study (7.1%)
   CrossRef (Tier 3): 1 study (7.1%)
   
   With PMID: 13/14 (92.9%)
   With DOI: 14/14 (100.0%)
   Average confidence: 0.89
```

**API Strategy** (Enhanced 2026):
1. **PubMed E-utilities** (Tier 1 - Primary):
   - Multiple query strategies (exact → relaxed → broad)
   - Returns PMID + DOI (both from PubMed record)
   - Validation: Year tolerance (±1), author match, metadata checks
   - Confidence scoring: Title similarity + validation checks

2. **Europe PMC** (Tier 2 - Fallback):
   - Structured queries (TITLE/FIRST_AUTHOR/PUB_YEAR)
   - Returns PMID + DOI (both when available)
   - Validation: Same strict criteria as Tier 1
   - Useful for European journals, early online publications

3. **CrossRef API** (Tier 3 - Final Fallback):
   - Used when Tier 1-2 return no match
   - Returns DOI only (CrossRef doesn't have PMID)
   - Work type filtering (excludes preprints/proceedings by default)
   - Useful for non-indexed journals, book chapters

**Confidence Thresholds** (raised in 2026):
- **Accept**: confidence ≥ 0.80 (high similarity + validation pass)
- **Review**: confidence 0.70-0.80 (moderate similarity)
- **Reject**: confidence < 0.70 (poor match)

#### Step 4.5.3: Generate Gold Standard CSV Files

**Command**:
```bash
python scripts/generate_gold_standard.py \
  --input studies/ai_2022/included_studies_with_identifiers.json \
  --study ai_2022 \
  --confidence 0.85
```

**What happens**:
```
📊 Filtering studies by confidence threshold (0.85)...
   Accepted: 12/14 (85.7%)
   Rejected: 2/14 (14.3%)

📄 Generating gold_pmids_ai_2022.csv (simple format)...
   ✅ Created with 12 PMIDs

📄 Generating gold_pmids_ai_2022_detailed.csv (multi-key format)...
   ✅ Created with 12 rows (PMID + DOI + metadata)

📊 Creating quality report...
   ✅ gold_generation_report_ai_2022.md
```

**Output 1: Simple format** (`gold_pmids_ai_2022.csv`):
```
18388205
14764433
32209641
29056283
31217195
18621673
...
```
**Purpose**: Backward compatible, used for basic PMID-only evaluation

**Output 2: Detailed format** (`gold_pmids_ai_2022_detailed.csv`):
```csv
pmid,first_author,year,title,journal,doi
18388205,Li AM,2008,Ambulatory blood pressure in children with obstructive sleep apnoea: a community based study,Thorax,10.1136/thx.2007.091132
14764433,Amin RS,2004,Twenty-four-hour ambulatory blood pressure in children with sleep-disordered breathing,Am J Respir Crit Care Med,10.1164/rccm.200309-1305OC
32209641,Chan KC,2020,Childhood OSA is an independent determinant of blood pressure in adulthood: longitudinal follow-up study,Thorax,10.1136/thoraxjnl-2019-213692
```
**Purpose**: Multi-key evaluation (DOI + PMID matching)

**Output 3: Quality Report** (`gold_generation_report_ai_2022.md`):
```markdown
# Gold Standard Generation Report

**Study**: ai_2022
**Generated**: 2026-01-24
**Confidence Threshold**: 0.85

## Summary Statistics

- **Total Included Studies**: 14
- **Accepted** (confidence ≥ 0.85): 12
- **Rejected** (confidence < 0.85): 2

## Coverage Metrics

| Metric | Count | Percentage |
|--------|-------|------------|
| With PMID | 12 | 100.0% |
| With DOI | 12 | 100.0% |
| With Both | 12 | 100.0% |

## Rejected Studies (Low Confidence)

- [32] Are there gender differences in the severity... (confidence: 0.80)
- [35] Baroreflex gain in children with obstructive... (confidence: 0.78)

**Recommendation**: Manually review rejected studies and add to CSV if appropriate.
```

### Advanced Options

#### Custom Confidence Threshold

Default threshold raised to 0.80 (from 0.70) with enhanced validation:
```bash
python scripts/extract_included_studies.py ai_2022 \
  --lookup-pmid \
  --generate-gold-csv \
  --min-confidence 0.80
```

For stricter matching (high-stakes validations):
```bash
python scripts/extract_included_studies.py ai_2022 \
  --lookup-pmid \
  --generate-gold-csv \
  --min-confidence 0.90
```

#### Year Tolerance Control (New)

Control allowed publication year difference (±1 year default):
```bash
python scripts/extract_included_studies.py ai_2022 \
  --lookup-pmid \
  --generate-gold-csv \
  --max-year-diff 1
```

For exact year matching only:
```bash
python scripts/extract_included_studies.py ai_2022 \
  --lookup-pmid \
  --generate-gold-csv \
  --max-year-diff 0
```

#### Email Configuration (for PubMed API)

PubMed requires email for E-utilities:
```bash
export PUBMED_EMAIL="your.email@institution.edu"
python scripts/extract_included_studies.py ai_2022 --lookup-pmid
```

Or use `.env` file:
```bash
# .env
PUBMED_EMAIL=your.email@institution.edu
PUBMED_API_KEY=your_api_key_here  # Optional, increases rate limit
```

#### API Key (optional, 3x faster)

Get API key from: https://www.ncbi.nlm.nih.gov/account/settings/
```bash
export PUBMED_API_KEY="your_api_key_here"
```
**Effect**: Rate limit increases from 3 req/sec → 10 req/sec (3x faster)

### Integration with Evaluation Pipeline

After generating gold standard files, they're automatically used by the evaluation system:

```python
# In llm_sr_select_and_score.py
gold_pmids, gold_dois = load_gold_multi_key("studies/ai_2022/gold_pmids_ai_2022_detailed.csv")

# Multi-key matching
matches_by_doi = retrieved_dois & gold_dois      # Primary strategy
matches_by_pmid = retrieved_pmids & gold_pmids   # Fallback for DOI-less articles
```

**See**: [DOI_PMID_MULTI_KEY_EVALUATION_GUIDE.md Section 9](DOI_PMID_MULTI_KEY_EVALUATION_GUIDE.md#9-gold-standard-extraction-technical-architecture) for technical implementation details.

### Troubleshooting

#### Issue 1: "No included studies table found"

**Cause**: Parser can't locate the table

**Solutions**:
1. Check markdown file has section heading:
   - "Table 1: Included Studies"
   - "Characteristics of Included Studies"
   - "## Included Studies"

2. Verify table is properly formatted (markdown table syntax)

3. **Fallback**: Use manual LLM extraction (Automation_guide_main.md STEP 5, Method B)

#### Issue 2: Low confidence matches

**Example output**:
```
⚠️  Warning: 5 studies below confidence threshold (0.85)
   Review: gold_generation_report_ai_2022.md
```

**Solutions**:
1. **Lower threshold**: Use `--confidence 0.75` if matches look correct
2. **Manual review**: Check quality report, manually add correct PMIDs to CSV
3. **Title mismatch**: Paper title differs from PubMed title (abbreviations, punctuation)

#### Issue 3: PubMed rate limiting

**Symptoms**:
```
⚠️  Rate limit exceeded: Waiting 10 seconds...
⚠️  Rate limit exceeded: Waiting 10 seconds...
```

**Solutions**:
1. **Get API key**: Free from NCBI, increases limit 3x
2. **Be patient**: Script automatically retries with exponential backoff
3. **Smaller batches**: Process fewer studies at a time

#### Issue 4: Some studies missing DOI/PMID

**Example report**:
```
Coverage Metrics:
  With PMID: 45/47 (95.7%)
  With DOI: 42/47 (89.4%)
  With Neither: 2/47 (4.3%)
```

**Solutions**:
1. **Acceptable**: 90%+ coverage is normal (some old articles lack DOIs)
2. **Manual lookup**: Search PubMed manually for missing 2 studies
3. **Add to CSV**: Manually append PMIDs to `gold_pmids_<study>_detailed.csv`

### Output Files Summary

| File | Format | Purpose |
|------|--------|---------|
| `included_studies.json` | JSON | Intermediate: Extracted study list; the current default extractor output |
| `included_studies_sampling.json` | JSON | Intermediate: Sampling-mode study list when `--sampling-runs` is used |
| `gold_pmids_<study>.csv` | CSV (1 column) | Simple: PMID-only, backward compatible |
| `gold_pmids_<study>_detailed.csv` | CSV (6 columns) | **Main output**: PMID+DOI, multi-key ready |
| `gold_generation_report_<study>.md` | Markdown | Quality report: Coverage, confidence, rejected studies |

---

## Step 5: Multi-Database Query Execution

### Understanding the Main Workflow Wrapper

The main orchestrator is now `scripts/run_complete_workflow.sh`.

**What it does**:
1. Validates the study folder and aligned query files.
2. Auto-detects a detailed DOI-aware gold standard and enables multi-key mode when available.
3. Imports Embase CSV exports when present.
4. Runs query scoring across the selected API-backed providers.
5. Aggregates query results.
6. Scores the aggregate result sets.

### Running the Wrapper

**Default full-set mode**
```bash
bash scripts/run_complete_workflow.sh sleep_apnea
```

This uses the current wrapper defaults: `pubmed,scopus,wos`.

**Explicit provider selection**
```bash
bash scripts/run_complete_workflow.sh sleep_apnea --databases pubmed,scopus,wos
```

**Query-level modes**
```bash
# Run the full score-and-aggregate flow once per aligned query block
bash scripts/run_complete_workflow.sh sleep_apnea --query-by-query

# Run only query 3 through the same flow
bash scripts/run_complete_workflow.sh sleep_apnea --query-index 3
```

### Embase Handling

- Embase remains a manual-export path, not a live API-backed provider.
- Export the six Embase CSVs from Embase.com into `studies/<study>/embase_manual_queries/`.
- Re-run the wrapper and it will convert those CSVs into `embase_query*.json`, then include them in scoring and aggregation automatically.
- The wrapper accepts `--databases ... ,embase` as a convenience token, but strips `embase` before forwarding provider names to the Python CLI.

### Outputs

The wrapper produces the main study outputs in:

- `benchmark_outputs/<study>/`
- `aggregates/<study>/`
- `aggregates_eval/<study>/`

### Relationship to the Low-Level Commands

The wrapper is now the documented primary entry point. Internally it delegates to `llm_sr_select_and_score.py` and `scripts/aggregate_queries.py`.

- Step 6 describes the lower-level query-scoring commands.
- Step 7 describes the aggregation layer.

Use those lower-level commands when you need debugging, custom experiments, or manual decomposition of the workflow.

---

## Step 6: Query Evaluation & Selection

### Understanding Query Performance Metrics

**Precision**: Of all articles retrieved, what % are relevant?
```
Precision = True Positives / (True Positives + False Positives)
```

**Recall**: Of all relevant articles, what % were retrieved?
```
Recall = True Positives / (True Positives + False Negatives)
```

**F1-Score**: Harmonic mean of precision and recall
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

**Trade-offs**:
- **High-recall queries**: Find all relevant articles but retrieve many irrelevant (low precision, high recall)
- **High-precision queries**: Find mostly relevant articles but miss some (high precision, low recall)
- **Balanced queries**: Compromise between the two

### Interpreting Results

**Example from sleep_apnea study**:

```csv
query,precision,recall,f1,retrieved,tp,gold_total
high_recall,0.0059,1.0000,0.0118,1850,11,11
balanced,0.0089,0.7272,0.0176,900,8,11
high_precision,0.0211,0.4545,0.0403,237,5,11
```

**Interpretation**:
- **High-recall**: Found all 11 relevant articles (100% recall) but retrieved 1850 total (0.59% precision)
- **High-precision**: Found only 5 relevant articles (45% recall) but retrieved 237 total (2.1% precision)
- **Balanced**: Found 8 relevant articles (72% recall) with 900 total (0.89% precision)

**Which is best?** Depends on your goals:
- Systematic review: Use high-recall (can't afford to miss articles)
- Quick screening: Use high-precision (manually review fewer articles)
- Exploratory: Use balanced

---

## Step 7: Results Aggregation

### Aggregation Strategies Explained

**1. Consensus (k=2, k=3)**

Logic: Article must be found by ≥k queries

```python
# Pseudocode
consensus_k2 = set()
for article in all_articles:
    query_count = number_of_queries_that_found(article)
    if query_count >= 2:
        consensus_k2.add(article)
```

**Advantages**:
- Reduces false positives (article validated by multiple queries)
- Higher precision than single queries

**Disadvantages**:
- May miss articles found by only one query
- Lower recall

---

**2. Precision-Gated Union**

Logic: Union of all queries, but remove articles from low-performing queries

```python
# Pseudocode
final_set = set()
for query in queries:
    if query.precision >= threshold:
        final_set.update(query.articles)
```

**Advantages**:
- Maintains high recall from union
- Filters out low-quality results

**Disadvantages**:
- Requires tuning precision threshold

---

**3. Weighted Vote**

Logic: Weight each query by its F1-score, select articles with high cumulative weight

```python
# Pseudocode
article_scores = {}
for query in queries:
    weight = query.f1_score
    for article in query.articles:
        article_scores[article] += weight

final_set = {article for article, score in article_scores.items() if score >= threshold}
```

**Advantages**:
- Incorporates query quality
- Balances precision and recall

**Disadvantages**:
- More complex
- Requires gold standard for weights

---

**4. Two-Stage Screen**

Logic: First screen with high-precision, then expand with high-recall

```python
# Pseudocode
stage1 = high_precision_query.articles  # Quick manual review
stage2 = high_recall_query.articles      # Comprehensive coverage

# Reviewers screen stage1 first, then stage2
final_set = stage1.union(stage2)
```

**Advantages**:
- Practical for manual review workflow
- Prioritizes high-quality results

**Disadvantages**:
- Doesn't reduce total screening burden

---

**5. Time-Stratified Hybrid**

Logic: Use precision queries for recent articles, recall queries for older articles

```python
# Pseudocode
recent_threshold = "2015-01-01"

recent = high_precision_query.articles.filter(date >= recent_threshold)
older = high_recall_query.articles.filter(date < recent_threshold)

final_set = recent.union(older)
```

**Advantages**:
- Recent articles have better metadata → precision works well
- Older articles may have incomplete indexing → need recall

**Disadvantages**:
- Requires date metadata
- Arbitrary threshold selection

---

## Step 8: Performance Scoring

### Scoring Individual Queries

**Run scoring manually**:
```bash
python llm_sr_select_and_score.py \
    --study-name sleep_apnea \
    --databases pubmed,scopus,wos \
    score \
    --queries-txt studies/sleep_apnea/queries.txt \
    --gold-csv studies/sleep_apnea/gold_pmids_sleep_apnea.csv \
    --outdir benchmark_outputs
```

**Output files**:
- `benchmark_outputs/sleep_apnea/summary_TIMESTAMP.csv` - Metrics table
- `benchmark_outputs/sleep_apnea/summary_per_database_TIMESTAMP.csv` - Per-database metrics
- `benchmark_outputs/sleep_apnea/details_TIMESTAMP.json` - Full results

**Summary CSV format**:
```csv
query,precision,recall,f1,jaccard,overlap,retrieved,tp,gold_total,provider
high_recall,0.0059,1.0000,0.0118,0.0059,1.0000,1850,11,11,multi
balanced,0.0089,0.7272,0.0176,0.0088,0.7272,900,8,11,multi
high_precision,0.0211,0.4545,0.0403,0.0206,0.4545,237,5,11,multi
```

### Scoring Aggregated Sets

**Run scoring manually**:
```bash
python llm_sr_select_and_score.py \
    --study-name sleep_apnea \
    score-sets \
    --sets aggregates/sleep_apnea/*.txt \
    --gold-csv studies/sleep_apnea/gold_pmids_sleep_apnea.csv \
    --outdir aggregates_eval
```

**Output format**:
```
Set[consensus_k2]: n=72 TP=3 Precision=0.042 Recall=0.273 F1=0.072
Set[precision_gated_union]: n=1961 TP=11 Precision=0.006 Recall=1.000 F1=0.011
```

**Interpretation**:
- `n`: Total articles in set
- `TP`: True positives (articles in gold standard found)
- `Precision`, `Recall`, `F1`: Standard metrics

---

## Step 8.5: Query Type Analysis Across Databases (Optional)

### Overview

After running the complete workflow, you can analyze query performance by semantic type (High-recall, Balanced, High-precision, etc.) aggregated across all databases. This provides insights into:
- How different query strategies perform when combining results from multiple databases
- Which databases contribute most to each query type's coverage
- Whether high-recall queries maintain their advantage across all databases

**When to use**: After completing Step 6 (Complete Workflow) with multi-database queries.

**Time investment**: 1-2 minutes for analysis.

### Running Query Type Analysis

**Basic analysis (all query types)**:
```bash
python scripts/analyze_queries_by_type.py sleep_apnea
```

**Detailed per-database breakdown**:
```bash
python scripts/analyze_queries_by_type.py sleep_apnea --detailed
```

**Filter specific query types**:
```bash
python scripts/analyze_queries_by_type.py sleep_apnea --query-types "High-recall,Balanced"
```

**Export to CSV for further analysis**:
```bash
python scripts/analyze_queries_by_type.py sleep_apnea --output query_analysis.csv
```

### Understanding the Output

**Example output**:
```
====================================================================================================
Query Performance Aggregated by Type Across All Databases
====================================================================================================

Query 1: High-recall
--------------------------------------------------------------------------------
  Databases: embase+pubmed+scopus+wos (4 total)
  Total Results (before dedup): 22,746
  Best Recall Achieved: 100.0% (47/47 gold studies)
  Average Recall: 94.4%

  Per-Database Breakdown:
    • EMBASE: 17,990 results, 46 TP, 97.9% recall
    • PUBMED: 1,188 results, 45 TP, 95.7% recall
    • SCOPUS: 3,568 results, 44 TP, 93.6% recall
    • WOS: 2,037 results, 42 TP, 89.4% recall

Query 2: Balanced
--------------------------------------------------------------------------------
  Databases: embase+pubmed+scopus+wos (4 total)
  Total Results (before dedup): 5,234
  Best Recall Achieved: 95.7% (45/47 gold studies)
  Average Recall: 91.5%
```

### Key Metrics Explained

| Metric | Description | What to Look For |
|--------|-------------|------------------|
| **Databases** | Which databases contributed to this query type | More databases = better coverage |
| **Total Results** | Sum across all databases (before dedup) | High-recall should have most |
| **Best Recall** | Highest recall achieved in any single database | Should be close to 100% for high-recall |
| **Average Recall** | Mean recall across all databases | Consistency indicator |
| **Per-Database Breakdown** | Individual database performance | Identifies database-specific strengths |

### Use Cases

1. **Compare Strategy Effectiveness**: See if high-recall queries truly outperform balanced/precision queries across databases
2. **Database Selection**: Identify which databases are most valuable for your topic
3. **Coverage Gaps**: Find queries that work well in one database but not others
4. **Multi-Database Value**: Quantify whether combining databases improves coverage

### CSV Output Format

When using `--output`, the CSV includes:
- `query_num`: Query number (1-6)
- `query_type`: Semantic type (High-recall, Balanced, etc.)
- `databases`: Databases included (e.g., "embase+pubmed+scopus")
- `num_databases`: Count of databases
- `total_results`: Sum before deduplication
- `max_TP`, `max_recall`, `avg_recall`: Aggregate metrics
- `<db>_results`, `<db>_TP`, `<db>_recall`: Per-database columns

**For complete documentation**: See `scripts/README_analyze_queries_by_type.md`

---

## Step 9: Cross-Study Validation & Meta-Analysis

### Overview

After completing multiple systematic review studies (Steps 1-8), you can perform **cross-study validation** to:
- Compare aggregation strategy performance across different medical domains
- Identify universally effective vs. domain-specific strategies
- Generate evidence-based recommendations for future studies
- Visualize performance patterns across studies

**When to use this**: After completing ≥2 individual studies with different topics/domains.

**Time investment**: 2-5 minutes for complete analysis + visualization generation.

### Architecture: Cross-Study Validation Framework

```
┌───────────────────────────────────────────────────────────────┐
│              INDIVIDUAL STUDIES (Steps 1-8)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Godos_2024  │  │  sleep_apnea │  │   ai_2022    │       │
│  │  (nutrition) │  │  (sleep med) │  │     (AI)     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                                │
│  Each produces:                                                │
│  • aggregates_eval/<study>/sets_summary_*.csv                 │
│  • benchmark_outputs/<study>/summary_*.csv                    │
│  • studies/<study>/gold_pmids_<study>.csv                    │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│           STEP 9: CROSS-STUDY VALIDATION                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  python -m cross_study_validation run                  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Phase 1: Data Collection                                      │
│  • Extract strategy performance from all studies               │
│  • Standardize data format (JSON)                              │
│  • Validate against schema                                     │
│                                                                │
│  Phase 2: Statistical Analysis                                 │
│  • Calculate mean/std/min/max for each strategy               │
│  • Rank strategies by recall, precision, F1                    │
│  • Identify strategies with perfect recall                     │
│                                                                │
│  Phase 3: Visualization Generation                             │
│  • Box plots (recall/precision/F1 distributions)              │
│  • Bar charts (strategy comparison with error bars)           │
│  • Scatter plots (precision-recall tradeoffs)                  │
│  • Heatmaps (performance by study/domain)                      │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│                      OUTPUTS                                   │
│  • cross_study_validation/reports/report_*.md                  │
│  • cross_study_validation/reports/figures/*.png                │
│  • cross_study_validation/data/all_studies.json               │
└───────────────────────────────────────────────────────────────┘
```

### Directory Structure

**Before running Step 9** (after completing multiple studies):
```
studies/
├── Godos_2024/
│   └── gold_pmids_Godos_2024.csv
├── sleep_apnea/
│   └── gold_pmids_sleep_apnea.csv
└── ai_2022/
    └── gold_pmids_ai_2022.csv

aggregates_eval/
├── Godos_2024/
│   └── sets_summary_20260122-091122.csv     # Strategy performance
├── sleep_apnea/
│   └── sets_summary_20260115-143544.csv
└── ai_2022/
    └── sets_summary_20260121-093646.csv

benchmark_outputs/
├── Godos_2024/
│   └── summary_20260122-091116.csv           # Query performance
├── sleep_apnea/
│   └── summary_20260115-142946.csv
└── ai_2022/
    └── summary_20260121-093645.csv
```

**After running Step 9**:
```
cross_study_validation/
├── __init__.py
├── __main__.py                               # Unified CLI entry point
├── collectors/
│   ├── collect_study_results.py              # Data collection orchestrator
│   └── parsers/
│       ├── csv_parsers.py                    # Parse aggregates_eval CSVs
│       ├── gold_standard_parser.py           # Extract PMIDs
│       └── metadata_collector.py             # Infer study domain
├── analysis/
│   └── descriptive_stats.py                  # Calculate statistics
├── reporting/
│   ├── markdown_reporter.py                  # Generate reports
│   └── visualizations.py                     # Generate figures
├── data/                                      # Standardized study data (gitignored)
│   ├── Godos_2024.json
│   ├── sleep_apnea.json
│   ├── ai_2022.json
│   └── all_studies.json                      # Combined dataset
├── reports/                                   # Generated reports (gitignored)
│   ├── report_20260123-111053.md
│   └── figures/
│       ├── boxplot_recall.png                # 300 DPI, publication-ready
│       ├── boxplot_precision.png
│       ├── boxplot_f1.png
│       ├── bar_chart_comparison.png
│       ├── scatter_precision_recall.png
│       └── heatmap_recall_by_study.png
└── schemas/
    └── study_result_schema.json              # Data validation rules
```

### Step 9.1: Complete Workflow (Recommended)

**Run everything in one command**:

```bash
# Activate environment
conda activate systematic_review_queries

# Run complete cross-study workflow
python -m cross_study_validation run
```

**What this does**:
1. **Collects data** from all completed studies in `aggregates_eval/`, `benchmark_outputs/`, and `studies/`
2. **Generates analysis report** with strategy performance comparison
3. **Creates 6 visualizations** showing performance patterns

**Expected output**:
```
═══════════════════════════════════════════════════════════════
Running complete cross-study validation workflow
═══════════════════════════════════════════════════════════════

Step 1: Collecting study data...
Found 3 studies: Godos_2024, sleep_apnea, ai_2022

Collecting data for: Godos_2024
  ✓ Parsed 5 strategies from sets_summary_20260122-091122.csv
  ✓ Parsed 6 queries from summary_20260122-091116.csv
  ✓ Extracted 23 valid PMIDs from gold_pmids_Godos_2024.csv
  ✓ Inferred domain 'nutrition' with confidence score 59
  ✓ Validation passed

Collecting data for: sleep_apnea
  ✓ Parsed 5 strategies
  ✓ Parsed 5 queries
  ✓ Extracted 11 valid PMIDs
  ✓ Domain: sleep medicine
  ✓ Validation passed

Collecting data for: ai_2022
  ✓ Parsed 5 strategies
  ✓ Parsed 6 queries
  ✓ Extracted 14 valid PMIDs
  ✓ Domain: artificial intelligence
  ✓ Validation passed

✅ Collection complete!
✓ Saved combined file: cross_study_validation/data/all_studies.json

Step 2: Generating analysis report...
✓ Loaded 3 studies
✓ Calculated stats for 5 strategies across 3 studies
✅ Report generated: cross_study_validation/reports/report_20260123-111053.md
📊 Analyzed 3 studies

Step 3: Generating visualizations...
  ✓ Created box plot: boxplot_recall.png
  ✓ Created box plot: boxplot_precision.png
  ✓ Created box plot: boxplot_f1.png
  ✓ Created bar chart: bar_chart_comparison.png
  ✓ Created scatter plot: scatter_precision_recall.png
  ✓ Created heatmap: heatmap_recall_by_study.png
✅ Generated 6 visualizations

═══════════════════════════════════════════════════════════════
✅ Complete workflow finished successfully!
═══════════════════════════════════════════════════════════════
```

### Step 9.2: Step-by-Step Workflow (Optional)

For more control, run each phase separately:

**Phase 1: Collect data from all studies**
```bash
python -m cross_study_validation collect --all
```

**Phase 2: Generate analysis report**
```bash
python -m cross_study_validation analyze
```

**Phase 3: Generate visualizations**
```bash
python -m cross_study_validation visualize
```

### Step 9.3: Understanding the Report

**Report file**: `cross_study_validation/reports/report_TIMESTAMP.md`

**Example report sections**:

```markdown
# Cross-Study Validation Report

## Executive Summary

This report analyzes the performance of **5 aggregation strategies** 
across **3 systematic review studies** covering **48 total gold 
standard articles**.

**Key Finding**: precision_gated_union achieved 100% recall in 2/3 
studies, making it the most reliable strategy across diverse domains.

## Study Characteristics

| Study ID | Domain | Databases | Gold Standard Size | Queries |
|----------|--------|-----------|-------------------|---------|
| Godos_2024 | nutrition | pubmed, scopus, wos, embase | 23 | 12 |
| ai_2022 | artificial intelligence | pubmed, scopus, wos, embase | 14 | 12 |
| sleep_apnea | sleep medicine | pubmed, scopus, wos, embase | 11 | 12 |

**Total Gold Standard Articles**: 48  
**Average Gold Standard Size**: 16.0  
**Unique Domains**: nutrition, artificial intelligence, sleep medicine

## Strategy Performance Summary

| Strategy | Mean Recall | Mean Precision | Mean Retrieved | Perfect Recall |
|----------|-------------|----------------|----------------|----------------|
| precision_gated_union | 78.6% ± 37.1% | 0.0052 ± 0.0041 | 9283 ± 13916 | 2/3 |
| time_stratified_hybrid | 78.6% ± 37.1% | 0.0052 ± 0.0041 | 9283 ± 13916 | 2/3 |
| weighted_vote | 78.6% ± 37.1% | 0.0052 ± 0.0041 | 9283 ± 13916 | 2/3 |
| two_stage_screen | 54.5% ± 31.9% | 0.0134 ± 0.0133 | 2696 ± 4071 | 0/3 |
| consensus_k2 | 50.0% ± 32.3% | 0.0186 ± 0.0203 | 1966 ± 2928 | 0/3 |

*Perfect Recall: Number of studies where strategy achieved 100% recall*

## Recommended Strategy

### precision_gated_union

**Justification**: 
- Achieved 100% recall in 2 out of 3 studies
- Highest mean recall (78.6%) across all domains
- Consistent performance across nutrition, sleep medicine, and AI domains
- Manageable screening burden (~9,283 articles on average)

**Performance by Study**:
- Godos_2024 (nutrition): 100% recall, 23/23 articles found
- ai_2022 (AI): 100% recall, 14/14 articles found
- sleep_apnea (sleep medicine): 36.4% recall, 4/11 articles found

## Strategy-Specific Analysis

### consensus_k2 (Articles found by ≥2 queries)
- Mean Recall: 50.0% ± 32.3%
- Mean Retrieved: 1,966 ± 2,928
- Best for: Reducing screening burden when perfect recall isn't required

### two_stage_screen (Two-phase screening)
- Mean Recall: 54.5% ± 31.9%
- Mean Retrieved: 2,696 ± 4,071
- Best for: Balanced approach with moderate screening burden

[... continues with detailed breakdowns per study ...]
```

### Step 9.4: Understanding the Visualizations

**All figures saved to**: `cross_study_validation/reports/figures/`

**1. Box Plots** (`boxplot_recall.png`, `boxplot_precision.png`, `boxplot_f1.png`)
- Show distribution of metrics across studies for each strategy
- Individual study points overlaid on boxes
- Helps identify strategy consistency

**Example interpretation**:
- Wide boxes = high variability across studies (domain-specific)
- Narrow boxes = consistent performance (universally reliable)
- Outliers = unusual performance in specific domains

**2. Bar Chart** (`bar_chart_comparison.png`)
- Compares mean performance across all strategies
- Error bars show ±1 standard deviation
- Three panels: Recall, Precision, F1

**Example interpretation**:
- Tallest bar in Recall panel = highest mean recall
- Large error bars = inconsistent performance across studies
- Small error bars = reliable strategy

**3. Scatter Plot** (`scatter_precision_recall.png`)
- Shows precision-recall tradeoffs
- Each point = one strategy in one study
- Color-coded by strategy

**Example interpretation**:
- Top-right corner = ideal (high precision + high recall)
- Top-left = high recall, low precision (comprehensive but many irrelevant)
- Bottom-right = high precision, low recall (few but relevant)

**4. Heatmap** (`heatmap_recall_by_study.png`)
- Rows = studies (with domain labels)
- Columns = strategies (sorted by mean recall)
- Cell color = recall percentage (green = high, red = low)

**Example interpretation**:
- Green columns = strategies that work well across all studies
- Red cells = strategy failure in specific domain
- Patterns reveal domain-specific vs. universal strategies

### Step 9.5: Adding New Studies to the Analysis

When you complete a new systematic review:

**Step 1**: Complete the individual study workflow (Steps 1-8)
```bash
# Example: New study called "diabetes_2025"
DATABASES="pubmed,scopus,wos" ./run_workflow_diabetes_2025.sh
```

**Step 2**: Re-run cross-study validation (automatically includes new study)
```bash
python -m cross_study_validation run
```

**Step 3**: Compare new report with previous reports
```bash
# View latest report
cat cross_study_validation/reports/report_*.md | tail -n 1

# Compare visualizations
open cross_study_validation/reports/figures/
```

### Advanced Usage

**Collect single study only**:
```bash
python -m cross_study_validation collect --study Godos_2024
```

**Custom output location**:
```bash
python -m cross_study_validation analyze --output my_custom_report.md
python -m cross_study_validation visualize --output ./my_figures/
```

**Verbose logging**:
```bash
python -m cross_study_validation run --verbose
```

### Troubleshooting

**Problem: "No studies found"**
```bash
# Check that you have completed studies with required files
ls aggregates_eval/*/sets_summary_*.csv
ls benchmark_outputs/*/summary_*.csv
ls studies/*/gold_pmids_*.csv

# If missing, complete Steps 1-8 for at least 2 studies first
```

**Problem: "Data validation failed"**
```bash
# Check schema requirements
cat cross_study_validation/schemas/study_result_schema.json

# Common issues:
# - Missing required CSV columns
# - Invalid PMID format
# - Corrupted CSV files

# Solution: Re-run the individual study workflow
```

**Problem: "Visualization generation failed"**
```bash
# Ensure matplotlib and seaborn are installed
conda activate systematic_review_queries
pip install matplotlib seaborn

# Re-run visualization step
python -m cross_study_validation visualize
```

**Problem: "Different number of strategies across studies"**
```bash
# This is expected if you ran studies at different times
# The system will compare only strategies present in all studies
# Check report for "Strategies analyzed: consensus_k2, precision_gated_union, ..."
```

### Best Practices

**✅ Do**:
- Run cross-study validation after completing ≥2 studies
- Compare studies from different medical domains for robust insights
- Use visualizations to communicate findings to stakeholders
- Re-run analysis when adding new studies
- Keep study names descriptive (e.g., "diabetes_2025" not "study1")

**❌ Don't**:
- Run cross-study validation with only 1 study (no comparison possible)
- Manually edit generated JSON files (they'll be overwritten)
- Delete intermediate files (they're gitignored anyway)
- Compare studies with vastly different gold standard sizes (<10 vs >100)

### Integration with Paper Writing

**Use cases for cross-study validation**:

1. **Methods section**: Justify aggregation strategy choice
   - "We used precision_gated_union based on cross-study validation 
     showing 100% recall in 2/3 diverse systematic reviews."

2. **Results section**: Report performance metrics
   - "Our selected strategy retrieved 1,704 articles with 100% recall 
     (23/23 gold standard articles found)."

3. **Discussion section**: Compare with other domains
   - "The high recall observed in our nutrition study (100%) aligns with
     previous findings in AI and sleep medicine domains (mean 78.6%)."

4. **Figures**: Publication-ready visualizations
   - Include `heatmap_recall_by_study.png` to show strategy comparison
   - Include `bar_chart_comparison.png` to justify strategy selection

---

## Step 10: Understanding the Outputs

### Directory Structure After Workflow

```
studies/sleep_apnea/
├── queries.txt                       # Input: PubMed queries
├── queries_scopus.txt                # Input: Scopus queries
├── queries_wos.txt                   # Input: WOS queries
├── queries_embase.txt                # Input: Embase queries
├── gold_pmids_sleep_apnea.csv        # Input: Gold standard
├── embase_query1.json                # Generated: Embase imports
├── embase_query2.json
└── ...

benchmark_outputs/sleep_apnea/
├── details_20260115-142946.json      # Full query results (DOIs, PMIDs, metadata)
└── summary_20260115-142946.csv       # Performance metrics per query

sealed_outputs/sleep_apnea/
└── sealed_20260115-140530.json       # Heuristic-selected best query

final_outputs/sleep_apnea/
└── final_20260115-144436.json        # Sealed query validation

aggregates/sleep_apnea/
├── consensus_k2.txt                  # Aggregation strategy outputs (PMIDs)
├── precision_gated_union.txt
├── weighted_vote.txt
└── ...

aggregates_eval/sleep_apnea/
├── sets_summary_20260115-142946.csv  # Aggregation performance
└── sets_details_20260115-142946.json # Detailed aggregation results
```

### Details JSON Structure

**File**: `benchmark_outputs/sleep_apnea/details_20260115-142946.json`

```json
{
  "abc123hash...": {
    "query": "('Sleep Apnea Syndromes'[MeSH] OR ...) AND (1990:2021[dp])",
    "provider": "multi",
    "results_count": 1850,
    "retrieved_dois": [
      "10.1016/j.sleep.2020.01.001",
      "10.1002/alz.12345",
      ...
    ],
    "retrieved_pmids": [
      "32451234",
      "33567890",
      ...
    ],
    "records": [
      {
        "doi": "10.1016/j.sleep.2020.01.001",
        "pmid": "32451234",
        "title": "Sleep apnea and dementia: A systematic review",
        "sources": ["pubmed", "scopus"]
      }
    ],
    "deduplication_summary": {
      "total_raw_results": 1987,
      "unique_articles": 1850,
      "duplicates_removed": 137,
      "deduplication_rate": 0.069
    }
  }
}
```

**Key fields**:
- `query`: Full query text
- `provider`: Database(s) queried (`multi` = multiple databases)
- `retrieved_dois`, `retrieved_pmids`: Identifiers for retrieved articles
- `records`: Full article metadata
- `sources`: Which databases found each article (for provenance tracking)
- `deduplication_summary`: How many duplicates were removed

### Summary CSV Structure

**File**: `benchmark_outputs/sleep_apnea/summary_20260115-142946.csv`

```csv
query,precision,recall,f1,jaccard,overlap,retrieved,tp,fp,fn,gold_total,provider,query_hash
high_recall,0.0059,1.0000,0.0118,0.0059,1.0000,1850,11,1839,0,11,multi,abc123...
balanced,0.0089,0.7272,0.0176,0.0088,0.7272,900,8,892,3,11,multi,def456...
high_precision,0.0211,0.4545,0.0403,0.0206,0.4545,237,5,232,6,11,multi,ghi789...
```

**Column definitions**:
- `query`: Query description
- `precision`, `recall`, `f1`: Standard metrics
- `jaccard`: Jaccard similarity coefficient
- `overlap`: Overlap coefficient
- `retrieved`: Total articles retrieved
- `tp`: True positives (found and in gold standard)
- `fp`: False positives (found but not in gold standard)
- `fn`: False negatives (in gold standard but not found)
- `gold_total`: Total articles in gold standard
- `provider`: Database(s) used
- `query_hash`: Unique identifier for this query

---

## Step 10: Complete Workflow Examples

### Example 1: New Study from Scratch (Method 1 - Recommended)

**Scenario**: You're starting a new systematic review on sleep apnea and dementia. You have Embase access.

**Steps**:

```bash
# 1. Create study directory
mkdir -p studies/sleep_apnea

# 2. Create query files (manually or via LLM)
# - studies/sleep_apnea/queries.txt
# - studies/sleep_apnea/queries_scopus.txt
# - studies/sleep_apnea/queries_wos.txt
# - studies/sleep_apnea/queries_embase.txt

# 3. Create gold standard
# - studies/sleep_apnea/gold_pmids_sleep_apnea.csv

# 4. Export Embase queries from Embase.com
# Save as: embase_query1.csv, embase_query2.csv, ...

# 5. Import Embase results FIRST
python scripts/batch_import_embase.py \
  --study sleep_apnea \
  --csvs studies/sleep_apnea/embase_query*.csv \
  --queries-file studies/sleep_apnea/queries_embase.txt

# 6. Run full workflow (the wrapper will import Embase CSVs automatically)
bash scripts/run_complete_workflow.sh sleep_apnea --databases pubmed,scopus,wos,embase

# Done! All databases queried, deduplicated, aggregated, and scored in ONE run.
```

**Time**: ~10-20 minutes depending on query complexity and article counts

**Outputs**: All benchmark, aggregation, and evaluation files created

---

### Example 2: Add Embase to Existing Results (Method 2)

**Scenario**: You already ran the workflow with PubMed/Scopus/WOS. Now you discovered you have Embase access.

**Steps**:

```bash
# 1. Export Embase queries from Embase.com
# Save as: studies/sleep_apnea/embase_query*.csv

# 2. Re-run the main workflow wrapper
bash scripts/run_complete_workflow.sh sleep_apnea --databases pubmed,scopus,wos,embase

# Done! Embase integrated with existing results.
```

**What happens**:
1. Imports all Embase CSVs
2. Finds existing PubMed/Scopus/WOS results in `benchmark_outputs/`
3. Re-aggregates everything together
4. Re-scores aggregated sets

**Time**: ~5-10 minutes

---

### Example 3: Single Database Only (PubMed)

**Scenario**: You only have PubMed access (free), want to test queries quickly.

**Steps**:

```bash
# Run with PubMed only
bash scripts/run_complete_workflow.sh sleep_apnea --databases pubmed
```

**Outputs**: Same structure, but only PubMed results

---

### Example 4: Manual Query Execution (Advanced)

**Scenario**: You want to run individual steps manually for debugging or customization.

```bash
# 1. Query PubMed only, save results
python llm_sr_select_and_score.py \
    --study-name sleep_apnea \
    --databases pubmed \
    score \
    --queries-txt studies/sleep_apnea/queries.txt \
    --gold-csv studies/sleep_apnea/gold_pmids_sleep_apnea.csv \
    --outdir benchmark_outputs

# 2. Query Scopus only, save results
python llm_sr_select_and_score.py \
    --study-name sleep_apnea \
    --databases scopus \
    --scopus-api-key YOUR_KEY \
    --scopus-skip-date-filter \
    score \
    --queries-txt studies/sleep_apnea/queries_scopus.txt \
    --gold-csv studies/sleep_apnea/gold_pmids_sleep_apnea.csv \
    --outdir benchmark_outputs

# 3. Aggregate manually
python scripts/aggregate_queries.py \
    --inputs benchmark_outputs/sleep_apnea/details_*.json \
    --outdir aggregates/sleep_apnea

# 4. Score aggregated sets
python llm_sr_select_and_score.py \
    --study-name sleep_apnea \
    score-sets \
    --sets aggregates/sleep_apnea/*.txt \
    --gold-csv studies/sleep_apnea/gold_pmids_sleep_apnea.csv \
    --outdir aggregates_eval
```

---

## Step 10: Troubleshooting & Best Practices

### Common Errors and Solutions

#### Error: "Provider query counts differ"

**Message**:
```
Provider query counts differ: {'pubmed': 6, 'scopus': 6, 'web_of_science': 5}
```

**Cause**: Different databases have different numbers of queries in their query files.

**Why it matters**: Query N across all databases should represent the same precision level (e.g., all query 1 = high-recall).

**Solution**: Ensure all query files have the same number of queries. If a query doesn't work for a specific database, include a placeholder or comment it as "Not applicable".

---

#### Error: ".env: line 30: scopus: command not found"

**Cause**: Space after comma in an optional comma-separated `.env` variable such as `SR_DATABASES`:
```bash
# WRONG
SR_DATABASES=pubmed, scopus,wos

# Bash tries to execute " scopus" as a command
```

**Solution**: Remove spaces:
```bash
# CORRECT
SR_DATABASES=pubmed,scopus,wos
```

---

#### Warning: "⚠️  WARNING: No DOIs or PMIDs found!"

**Cause**: Embase CSV export doesn't include required fields.

**Solution**: Re-export from Embase with:
- ✅ Digital Object Identifier (DOI)
- ✅ Medline PMID

---

#### Low Precision Results

**Example**:
```
Set[precision_gated_union]: n=1961 TP=11 Precision=0.006 Recall=1.000
```

**Is this bad?** No! This is expected for high-recall systematic reviews.

**Interpretation**:
- Found ALL 11 relevant articles (100% recall) ✅
- But retrieved 1961 total (0.6% precision) ⚠️
- This is acceptable - you'll manually screen the 1961 articles
- Alternative: Use high-precision query (fewer articles but may miss some relevant ones)

---

### Best Practices

#### 1. Query Design

✅ **Do**:
- Test queries on each database manually first
- Start with 3 precision levels (high-recall, balanced, high-precision)
- Add 2-3 micro-variants to test specific filters
- Keep queries aligned across databases (query 1 = high-recall on all platforms)

❌ **Don't**:
- Mix precision levels randomly
- Create too many queries (6 is a good number)
- Use database-specific syntax in wrong database files

---

#### 2. Gold Standard Creation

✅ **Do**:
- Use articles from prior systematic reviews as gold standard
- Include 10-20 articles minimum
- Verify PMIDs are correct (check PubMed)
- Update gold standard as you discover new relevant articles

❌ **Don't**:
- Use articles without PMIDs (can't validate)
- Include articles outside your date range
- Use articles from different topics

---

#### 3. Embase Integration

✅ **Do**:
- Export with DOI + Medline PMID fields
- Keep all query texts in `queries_embase.txt` (even if some return 0 results)
- Use Method 1 (import Embase first) for new projects

❌ **Don't**:
- Manually remove queries from `queries_embase.txt` (script handles it)
- Export without DOI field (can't deduplicate)
- Mix up query order between files

---

#### 4. Deduplication

✅ **Do**:
- Trust the DOI-based deduplication
- Expect ~10-15% deduplication rate across databases
- Check `deduplication_summary` in details JSON

❌ **Don't**:
- Manually deduplicate (the system handles it)
- Worry about articles without DOIs (older articles may not have them)

---

#### 5. Performance Interpretation

✅ **Do**:
- Use high-recall queries for comprehensive systematic reviews
- Use balanced queries for exploratory searches
- Compare F1-scores across queries
- Consider both precision and recall, not just F1

❌ **Don't**:
- Expect high precision with high recall (it's a trade-off)
- Dismiss low-precision queries (they may have perfect recall)
- Focus only on precision (recall is equally important)

---

### Workflow Decision Tree

```
Do you have Embase access?
│
├─ Yes
│  │
│  Do you want maximum efficiency?
│  │
│  ├─ Yes → Use Method 1
│  │        1. Export Embase queries
│  │        2. Save CSVs under studies/<study>/embase_manual_queries/
│  │        3. Run full workflow (scripts/run_complete_workflow.sh)
│  │
│  └─ No → Use Method 2
│           1. Run full workflow first
│           2. Export Embase later
│           3. Re-run scripts/run_complete_workflow.sh
│
└─ No
   │
   Which databases do you have access to?
   │
  ├─ PubMed only (free)
  │  → bash scripts/run_complete_workflow.sh sleep_apnea --databases pubmed
   │
  ├─ PubMed + Scopus
  │  → bash scripts/run_complete_workflow.sh sleep_apnea --databases pubmed,scopus
   │
  └─ PubMed + Scopus + WOS
    → bash scripts/run_complete_workflow.sh sleep_apnea --databases pubmed,scopus,wos
```

---

### Quick Reference Commands

```bash
# Complete workflow (automated databases + auto-detect Embase)
bash scripts/run_complete_workflow.sh sleep_apnea --databases pubmed,scopus,wos

# Import single Embase query
python scripts/import_embase_manual.py -i query.csv -o query.json -q "query text"

# Batch import Embase queries
python scripts/batch_import_embase.py --study STUDY --csvs *.csv --queries-file queries_embase.txt

# Re-run the main wrapper to include imported Embase results
bash scripts/run_complete_workflow.sh sleep_apnea --databases pubmed,scopus,wos,embase

# Manual aggregation
python scripts/aggregate_queries.py --inputs benchmark_outputs/STUDY/details_*.json --outdir aggregates/STUDY

# Manual scoring
python llm_sr_select_and_score.py --study-name STUDY score-sets --sets aggregates/STUDY/*.txt --gold-csv gold.csv --outdir aggregates_eval
```

---

## Conclusion

This pipeline automates systematic literature review across multiple databases with:
- ✅ Automated querying (PubMed, Scopus, WOS)
- ✅ Manual integration (Embase)
- ✅ DOI-based deduplication
- ✅ Multiple aggregation strategies
- ✅ Performance validation against gold standards

**Next Steps**:
1. Create your study directory structure
2. Design queries for your research question
3. Follow Method 1 or Method 2 based on your needs
4. Analyze results and select best query/aggregation strategy

**For more information**:
- [Embase Integration Guide](embase_integration_guide.md) - Detailed Embase workflow
- [Multi-Database Deduplication](multi_database_deduplication_complete.md) - How deduplication works
- [README.md](../README.md) - Project overview

---

**Document Version**: 1.0  
**Last Updated**: January 15, 2026  
**Study Example**: sleep_apnea
