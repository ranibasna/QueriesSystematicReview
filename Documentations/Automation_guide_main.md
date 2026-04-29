---
title: "Complete Systematic Review Automation Guide"
subtitle: "The Definitive End-to-End Guide: From Raw PDFs to Final Results"
author: "Systematic Review Queries Project"
date: "January 21, 2026"
format:
  html:
    toc: true
    toc-location: left
    toc-depth: 3
    toc-title: "Contents"
    number-sections: true
    theme: cosmo
    code-copy: true
    code-overflow: wrap
---

## 🎯 Purpose of This Guide

This guide walks you through the **complete automated systematic review workflow** - from raw PDF files (PROSPERO protocol + published paper) to final aggregated results with performance metrics.

**What you'll learn:**
- How to convert PDFs to markdown automatically
- How to generate database-specific queries using LLM
- How to create gold standard PMID lists
- How to run the complete multi-database workflow in ONE command
- How to interpret and use the results

**Time investment:**
- **One-time setup**: 15 minutes (install dependencies, configure APIs)
- **Per study**: 45-90 minutes total
  - Automated steps: 30-40 minutes
  - Manual steps: 15-50 minutes (mostly Embase export)
- **Cross-study validation** (optional): 2-5 minutes after completing ≥2 studies

---

## 📊 The Complete Workflow at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│  START: Raw Study Files                                     │
│  ├── Paper.pdf                 (Published systematic review)│
│  └── PROSPERO.pdf              (Protocol document)          │
└─────────────────────────────────────────────────────────────┘
           ↓ STEP 1: Convert PDFs (5 min, automated)
┌─────────────────────────────────────────────────────────────┐
│  Markdown Files Created                                     │
│  ├── paper_<study>.md                                       │
│  └── prospero_<study>.md                                    │
└─────────────────────────────────────────────────────────────┘
           ↓ STEP 2: Generate LLM Command (2 min, automated)
┌─────────────────────────────────────────────────────────────┐
│  LLM Command Ready                                          │
│  └── /run_<study>_multidb_strategy                          │
└─────────────────────────────────────────────────────────────┘
           ↓ STEP 3: Run LLM Command (5 min, automated)
┌─────────────────────────────────────────────────────────────┐
│  Query Files Created                                        │
│  ├── queries.txt           (6 PubMed queries)              │
│  ├── queries_scopus.txt    (6 Scopus queries)              │
│  ├── queries_wos.txt       (6 WOS queries)                 │
│  └── queries_embase.txt    (6 Embase queries)              │
└─────────────────────────────────────────────────────────────┘
           ↓ STEP 4: Manual Embase Export (10-30 min, manual)
┌─────────────────────────────────────────────────────────────┐
│  Embase CSVs Exported                                       │
│  └── embase_manual_queries/                                 │
│      ├── embase_query1.csv                                  │
│      ├── embase_query2.csv                                  │
│      └── ... (6 files total)                                │
└─────────────────────────────────────────────────────────────┘
           ↓ STEP 5: Create Gold Standard (5-30 min, automated)
┌─────────────────────────────────────────────────────────────┐
│  Gold Standard Created                                      │
│  └── gold_pmids_<study>.csv  (15-50 PMIDs)                 │
└─────────────────────────────────────────────────────────────┘
           ↓ STEP 6: Run Complete Workflow (15-30 min, automated)
┌─────────────────────────────────────────────────────────────┐
│  Final Results                                              │
│  ├── benchmark_outputs/                                     │
│  │   ├── details_*.json           (Query results)          │
│  │   ├── summary_*.csv            (Combined metrics)       │
│  │   └── summary_per_database_*.csv (Per-DB metrics)       │
│  ├── aggregates/             (Combined strategies)         │
│  └── aggregates_eval/        (Strategy performance)        │
│                                                              │
│  📊 Per-Database Performance:                               │
│     • PubMed:  94.4% recall                                 │
│     • Scopus:  100% recall (DOI matching)                  │
│     • WOS:     88.9% recall (DOI matching)                 │
│     • Embase:  94.4% recall (DOI matching)                 │
│     • COMBINED: 100% recall                                 │
│                                                              │
│  🏆 Best Strategy: precision_gated_union                    │
│     → 1,704 PMIDs, 100% Recall                             │
└─────────────────────────────────────────────────────────────┘
           ↓ STEP 7: Cross-Study Validation (2-5 min, after ≥2 studies)
┌─────────────────────────────────────────────────────────────┐
│  Meta-Analysis Across Studies                               │
│  ├── cross_study_validation/                                │
│  │   ├── reports/           (Analysis & visualizations)     │
│  │   └── data/              (Standardized JSON)             │
│                                                              │
│  📊 Cross-Study Insights: Which strategy works best        │
│     across different medical domains?                       │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Prerequisites (One-Time Setup)

### 1. Install Required Software

```bash
# Install Miniconda (if not already installed)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh

# Clone repository
cd ~/Documents/DataScience
git clone https://github.com/ranibasna/QueriesSystematicReview.git
cd QueriesSystematicReview
```

### 2. Create Conda Environments

**Main environment (for systematic review workflow):**
```bash
conda env create -f environment.yml
conda activate systematic_review_queries
```

**Docling environment (for PDF conversion):**
```bash
conda create -n docling python=3.11
conda activate docling
pip install docling
conda deactivate
```

### 3. Configure API Keys

Create `.env` file in project root:

```bash
# .env file
# PubMed (free, but API key recommended)
NCBI_EMAIL=your.email@institution.edu
NCBI_API_KEY=your_ncbi_api_key_optional

# Scopus (requires institutional subscription)
SCOPUS_API_KEY=your_scopus_api_key
SCOPUS_INSTTOKEN=your_institution_token_optional
SCOPUS_SKIP_DATE_FILTER=true

# Web of Science (requires institutional subscription)
WOS_API_KEY=your_wos_api_key
```

**Where to get API keys:**
- **PubMed**: https://www.ncbi.nlm.nih.gov/account/settings/ (free)
- **Scopus**: Contact your institution's library
- **WOS**: Contact your institution's library

---

## 📋 Complete End-to-End Workflow: 6 Steps from Raw PDFs

This section shows you how to go from **raw PDF files** to **final results** with detailed step-by-step instructions.

**Example Study Structure (Starting Point):**
```
studies/Godos_2024/
├── Paper.pdf                        # Published systematic review (raw)
├── PROSPERO.pdf                     # PROSPERO protocol (raw)
├── embase_manual_queries/           # Empty folder (you'll populate during workflow)
└── pmids_multiple_sources/          # Optional; only needed for the manual LLM fallback in STEP 5
```

**After completing all steps:**
```
studies/Godos_2024/
├── Paper.pdf
├── PROSPERO.pdf
├── paper_godos_2024.md              # ← Generated in STEP 1
├── prospero_godos_2024.md           # ← Generated in STEP 1
├── queries.txt                      # ← Generated in STEP 3 (6 PubMed queries)
├── queries_scopus.txt               # ← Generated in STEP 3 (6 Scopus queries)
├── queries_wos.txt                  # ← Generated in STEP 3 (6 WOS queries)
├── queries_embase.txt               # ← Generated in STEP 3 (6 Embase queries)
├── gold_pmids_godos_2024.csv        # ← Created in STEP 5 (Simple: PMID-only)
├── gold_pmids_godos_2024_detailed.csv # ← Created in STEP 5 (Detailed: PMID + DOI)
├── embase_manual_queries/           # ← Populated in STEP 4
│   ├── embase_query1.csv
│   ├── embase_query2.csv
│   ├── embase_query3.csv
│   ├── embase_query4.csv
│   ├── embase_query5.csv
│   └── embase_query6.csv
├── benchmark_outputs/               # ← Generated in STEP 6
│   ├── details_*.json               # Query results with DOIs
│   ├── summary_*.csv                # Combined metrics
│   └── summary_per_database_*.csv   # Per-database metrics (NEW!)
├── aggregates/                      # ← Generated in STEP 6
└── aggregates_eval/                 # ← Generated in STEP 6
```

---

# STEP 1: Convert PDFs to Markdown

## Purpose
Convert your raw PDF files (Paper.pdf and PROSPERO.pdf) to markdown format so they can be processed by the LLM in subsequent steps.

## Requirements
- ✅ Conda environment `docling` installed (see Prerequisites section)
- ✅ PDF files in your study directory

## Command

```bash
# Activate main environment first
conda activate systematic_review_queries

# Run PDF conversion script
python scripts/prepare_study.py Godos_2024 --docling-env docling
```

## What This Does

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Activate Docling Environment                       │
├─────────────────────────────────────────────────────────────┤
│ • Switches to: conda activate docling                       │
│ • Loads PDF processing libraries                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Scan Study Directory                               │
├─────────────────────────────────────────────────────────────┤
│ • Finds: studies/Godos_2024/Paper.pdf                      │
│ • Finds: studies/Godos_2024/PROSPERO.pdf                   │
│ • Detects file types and sizes                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Convert Each PDF                                   │
├─────────────────────────────────────────────────────────────┤
│ Processing Paper.pdf...                                     │
│ • Extract text, tables, figures                             │
│ • Preserve formatting (headings, lists, references)         │
│ • Convert to markdown syntax                                │
│ • Save as: paper_godos_2024.md                             │
│                                                              │
│ Processing PROSPERO.pdf...                                  │
│ • Extract protocol sections (PICOS, dates, keywords)        │
│ • Convert to markdown                                       │
│ • Save as: prospero_godos_2024.md                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Return to Main Environment                         │
├─────────────────────────────────────────────────────────────┤
│ • Switches back to: systematic_review_queries               │
│ • Ready for next step                                       │
└─────────────────────────────────────────────────────────────┘
```

## Expected Output

```
═══════════════════════════════════════════════════════════════
  📄 PDF to Markdown Conversion: Godos_2024
═══════════════════════════════════════════════════════════════

Activating docling environment...
✓ Environment activated

Scanning study directory...
Found PDFs:
  • Paper.pdf (3.2 MB)
  • PROSPERO.pdf (0.8 MB)

Converting Paper.pdf...
  ✓ Extracted 24 pages
  ✓ Found 3 tables
  ✓ Found 156 references
  ✓ Saved to: studies/Godos_2024/paper_godos_2024.md

Converting PROSPERO.pdf...
  ✓ Extracted 6 pages
  ✓ Found PICOS framework
  ✓ Saved to: studies/Godos_2024/prospero_godos_2024.md

✅ Conversion complete!

Generated files:
  • studies/Godos_2024/paper_godos_2024.md
  • studies/Godos_2024/prospero_godos_2024.md

Next step: Generate LLM command for query generation
```

## Verify Output

```bash
# Check files were created
ls -lh studies/Godos_2024/*.md

# Preview PROSPERO markdown
head -50 studies/Godos_2024/prospero_godos_2024.md

# Preview Paper markdown
head -50 studies/Godos_2024/paper_godos_2024.md
```

---

# STEP 6.5: Analyze Query Performance by Type (Optional)

## Purpose
After running the complete workflow, analyze how different query strategies (High-recall, Balanced, High-precision) perform when aggregated across all databases.

## Requirements
- ✅ STEP 6 completed (workflow ran successfully)
- ✅ Per-database summary file exists: `benchmark_outputs/<STUDY_NAME>/summary_per_database_*.csv`

## Command

```bash
# Basic analysis (all query types)
python scripts/analyze_queries_by_type.py <STUDY_NAME>

# Detailed per-database breakdown
python scripts/analyze_queries_by_type.py <STUDY_NAME> --detailed

# Filter specific query types
python scripts/analyze_queries_by_type.py <STUDY_NAME> --query-types "High-recall,Balanced"

# Export to CSV
python scripts/analyze_queries_by_type.py <STUDY_NAME> --output query_analysis.csv
```

## Example Output

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
```

## Use Cases

1. **Compare Strategies**: See if high-recall queries maintain advantage across all databases
2. **Database Selection**: Identify which databases provide best coverage for your topic
3. **Coverage Analysis**: Find queries that work well in some databases but not others
4. **Multi-Database Value**: Quantify whether combining databases improves overall coverage

## When to Use This

- ✅ After completing multi-database workflow
- ✅ When you want to understand cross-database query performance
- ✅ For systematic review methodology reporting
- ✅ To make informed decisions about query/database selection

**For complete documentation**: See `scripts/README_analyze_queries_by_type.md`

## Troubleshooting

**Problem: "docling environment not found"**
```bash
# Create the docling environment
conda create -n docling python=3.11
conda activate docling
pip install docling
conda deactivate
```

**Problem: "PDF file not found"**
```bash
# Check file names (case-sensitive!)
ls studies/Godos_2024/*.pdf

# If named differently, rename:
mv studies/Godos_2024/paper.pdf studies/Godos_2024/Paper.pdf
mv studies/Godos_2024/prospero.pdf studies/Godos_2024/PROSPERO.pdf
```

**Problem: "Conversion failed - corrupted PDF"**
```bash
# Try opening PDF manually to verify it's valid
# If corrupted, re-download from source
```

---

# STEP 2: Generate LLM Query Generation Command

## Purpose
Create a runnable strategy-aware command or prompt that reads your protocol and writes aligned database-specific query files for the study.

## Requirements
- ✅ Markdown files from STEP 1 completed
- ✅ Access to either Gemini CLI or GitHub Copilot Chat in VS Code

## Current Source of Truth

The latest generation workflow uses:

- `prompts/prompt_template_multidb_strategy_aware.md`
- `prompts/database_guidelines_strategy_aware.md`
- `studies/guidelines.md`
- `studies/general_guidelines.md`
- `studies/<study>/prospero_<study>.md`

This workflow is fixed to the current six-query family (`Q1` through `Q6`). The older level-based modes are not the current strategy-aware path.

## Two Supported Generation Approaches

### Option A: Gemini CLI

```bash
/generate_multidb_prompt \
  --command_name run_godos_2024_multidb_strategy \
  --protocol_path studies/Godos_2024/prospero_godos_2024.md \
  --databases pubmed,scopus,wos,embase \
  --relaxation_profile default \
  --min_date "1990/01/01" \
  --max_date "2023/12/31"
```

### Option B: VS Code Copilot Chat

```text
/generate-multidb-prompt run_godos_2024_multidb_strategy studies/Godos_2024/prospero_godos_2024.md pubmed,scopus,wos,embase default 1990/01/01 2023/12/31
```

Both approaches now point at the same strategy-aware template stack.

## Parameter Explanations

| Parameter | Description | Example | Notes |
|-----------|-------------|---------|-------|
| `command_name` | Name of the runnable command to create | `run_godos_2024_multidb_strategy` | Becomes `/<command_name>` |
| `protocol_path` | Path to PROSPERO markdown from STEP 1 | `studies/Godos_2024/prospero_godos_2024.md` | Use protocol markdown, not the paper |
| `databases` | Databases to generate queries for | `pubmed,scopus,wos,embase` | Include `embase` here if you want `queries_embase.txt` |
| `relaxation_profile` | Strategy-aware recall/precision bias | `default` | One of `default`, `recall_soft`, `recall_strong` |
| `min_date` | Start of literature search date range | `1990/01/01` | YYYY/MM/DD format |
| `max_date` | End of literature search date range | `2023/12/31` | Match your review |

## What the Generator Does

1. Reads the strategy-aware template and database-guidance files.
2. Reads shared study guidance plus your study protocol markdown.
3. Extracts topic framing and PICOS information from the protocol.
4. Injects selected database guidance, date window, and relaxation profile into the populated prompt.
5. Preserves the runtime exchange format used by the strategy-aware workflow: one JSON query object keyed by database plus an optional `json_patch` correction block.
6. Writes a reusable command file to either `.gemini/commands/` or `.github/prompts/`.

## Verify Output

```bash
# Gemini path
ls -lh .gemini/commands/run_godos_2024_multidb_strategy.toml

# Copilot prompt path
ls -lh .github/prompts/run_godos_2024_multidb_strategy.prompt.md
```

## Troubleshooting

**Problem: "Protocol file not found"**
```bash
ls studies/Godos_2024/prospero_*.md
```

**Problem: "Template files not found"**
```bash
pwd
ls prompts/prompt_template_multidb_strategy_aware.md
ls prompts/database_guidelines_strategy_aware.md
```

**Problem: "I restored Gemini files but they still use the old prompt stack"**
```text
Regenerate the study-specific command after updating the generator.
Older run_*_multidb*.toml and .prompt.md files do not automatically migrate.
```

---

# STEP 3: Run the Generated LLM Command

## Purpose
Execute the generated command so the system writes the strategy summary and aligned query files automatically.

## Command

```bash
/run_godos_2024_multidb_strategy
```

## What This Does

The generated command now:

1. Executes the populated strategy-aware instructions for this study and the requested databases.
2. Selects the retrieval architecture (`single_route` or `dual_route_union`) and determines whether the `design_analytic_block` stays active.
3. Builds the concept tables that map protocol concepts to controlled vocabulary and textword terms for each database.
4. Generates a single JSON query object keyed by database, where each database contains six comment-prefixed query strings (`Q1` through `Q6`).
5. Runs the PRESS self-check and records any needed `json_patch` corrections.
6. Writes `search_strategy.md` with the architecture summary, concept tables, JSON query object, `json_patch`, and translation notes.
7. Applies any corrections and writes the final database-specific `queries*.txt` files into `studies/Godos_2024/`.

## Files Written Automatically

- `studies/Godos_2024/search_strategy.md` (architecture summary, concept tables, JSON query object, `json_patch`, translation notes)
- `studies/Godos_2024/queries.txt`
- `studies/Godos_2024/queries_scopus.txt`
- `studies/Godos_2024/queries_wos.txt`
- `studies/Godos_2024/queries_embase.txt`

The JSON query object is the intermediate communication format used during generation. In the current workflow it is stored inside `search_strategy.md` rather than as a separate standalone query JSON file.

Manual copying of JSON arrays into query files is no longer part of the current workflow.

## Verify Output

```bash
ls studies/Godos_2024/search_strategy.md
ls studies/Godos_2024/queries*.txt
grep -n "json_patch" studies/Godos_2024/search_strategy.md

# Optional quick check that comment-prefixed query blocks were written
grep -c "^# Q" studies/Godos_2024/queries.txt
```

## Review Before Proceeding

- Confirm the query files exist for each requested database.
- Confirm the six query blocks stay aligned across database files.
- Review `search_strategy.md` for the selected architecture, concept-role assignments, and translation notes.
- Make any manual refinements directly in the generated `queries*.txt` files before moving to STEP 4.

## Troubleshooting

**Problem: "Queries don't match my protocol"**
```bash
cat studies/Godos_2024/prospero_godos_2024.md
```

Clarify the protocol markdown if needed, then regenerate the command and rerun it.

**Problem: "Generated command did not write query files"**
```text
This usually means you are still running an older generated command file.
Regenerate it using the current strategy-aware generator, then rerun the new command.
```

---

# STEP 4: Manual Embase Export

## Purpose
Export search results from Embase.com for each of your 6 Embase queries, since Embase has no API access.

## Requirements
- ✅ Embase queries from STEP 3 (`queries_embase.txt`)
- ✅ Institutional subscription to Embase.com
- ✅ Folder created: `studies/Godos_2024/embase_manual_queries/`

## Why Manual?

**Embase does not provide API access.** You must:
1. Log in to Embase.com
2. Copy each query from `queries_embase.txt`
3. Run the query on the website
4. Export results as CSV
5. Save each CSV as `embase_query1.csv`, `embase_query2.csv`, etc.

## Step-by-Step Instructions

### Step 4.1: Create Export Folder

```bash
mkdir -p studies/Godos_2024/embase_manual_queries
```

### Step 4.2: Read Your Queries

```bash
# Display all Embase queries
cat -n studies/Godos_2024/queries_embase.txt
```

You'll see something like:
```
1  ('mediterranean diet'/exp OR 'mediterranean diet':ab,ti) AND ('cardiovascular disease'/exp OR cardiovascular:ab,ti) AND ([article]/lim OR [review]/lim) AND [1990-2023]/py
2  'mediterranean diet'/de AND cardiovascular:ab,ti AND [1990-2023]/py
3  'mediterranean diet':ti AND 'cardiovascular disease':ti AND [1990-2023]/py
4  ('mediterranean diet'/exp OR mediterranean:ab,ti) AND (cvd:ab,ti OR 'heart disease':ab,ti) AND [article]/lim AND [1990-2023]/py
5  'mediterranean diet'/de AND cardiovascular:ti AND [1990-2023]/py
6  'mediterranean diet' NEAR/5 diet AND cardiovascular:ab,ti AND [1990-2023]/py
```

### Step 4.3: Export from Embase.com (Repeat for Each Query)

**For Query 1:**

1. **Log in** to Embase.com (https://www.embase.com)

2. **Copy Query 1** from `queries_embase.txt`:
   ```
   ('mediterranean diet'/exp OR 'mediterranean diet':ab,ti) AND ('cardiovascular disease'/exp OR cardiovascular:ab,ti) AND ([article]/lim OR [review]/lim) AND [1990-2023]/py
   ```

3. **Paste into Embase search box** and click "Search"

4. **Wait for results** (may take 30-60 seconds for large result sets)

5. **Export results**:
   - Click "Export" button (top-right of results)
   - Select "All fields" or "Citation and abstract"
   - Select format: **CSV** (or Excel, then save as CSV)
   - Click "Export"

6. **Save file** as `embase_query1.csv` in:
   ```
   studies/Godos_2024/embase_manual_queries/embase_query1.csv
   ```

7. **Repeat for queries 2-6**, saving as:
   - `embase_query2.csv`
   - `embase_query3.csv`
   - `embase_query4.csv`
   - `embase_query5.csv`
   - `embase_query6.csv`

### Step 4.4: Verify Exports

```bash
# Check all 6 CSV files exist
ls -lh studies/Godos_2024/embase_manual_queries/

# Expected output:
# embase_query1.csv
# embase_query2.csv
# embase_query3.csv
# embase_query4.csv
# embase_query5.csv
# embase_query6.csv

# Check file sizes (should be > 0 bytes)
du -h studies/Godos_2024/embase_manual_queries/*.csv

# Count records in each file (optional)
wc -l studies/Godos_2024/embase_manual_queries/*.csv
```

## Important CSV Format Notes

**Required CSV Format:**
- Must have header row
- Must include DOI column (for deduplication)
- Recommended columns: Title, Authors, Year, DOI, PMID (if available)

**Typical Embase CSV structure:**
```csv
Title,Authors,Year,DOI,PMID,Abstract,Source
"Mediterranean diet and cardiovascular...",Smith J; Brown A,2021,10.1234/example,12345678,"Abstract text...","Journal of..."
...
```

**If CSV has issues**, the import script (`batch_import_embase.py` in STEP 6) will report them and you can fix them before proceeding.

## Time Estimate

- **Per query**: 2-5 minutes (search + export + save)
- **Total for 6 queries**: 10-30 minutes

## Troubleshooting

**Problem: "Embase query syntax error"**
```markdown
Common issues:
1. Missing quotes around phrases: ❌ mediterranean diet ✅ 'mediterranean diet'
2. Wrong operators: ❌ AND/OR ✅ AND, OR (with commas in some contexts)
3. Field tags: Use :ab,ti for abstract/title, /exp for explosion, /de for exact

**Solution**: Test query in Embase search box, refine syntax, update queries_embase.txt
```

**Problem: "No DOI column in exported CSV"**
```markdown
**Issue**: Embase export settings didn't include DOI field

**Solution**:
1. Re-export with "All fields" selected
2. Or manually add DOI column by matching PMIDs (if available)
3. DOI is critical for cross-database deduplication
```

**Problem: "Export button greyed out / not working"**
```markdown
**Common causes**:
1. Too many results (>10,000) - add more filters to narrow
2. Session timeout - re-login and try again
3. Browser issues - try different browser (Chrome recommended)

**Solution**: If >10,000 results, split by date ranges:
- Run query with: AND [1990-2000]/py
- Run query with: AND [2001-2010]/py
- Run query with: AND [2011-2023]/py
- Merge CSVs manually before saving as embase_query1.csv
```

**Problem: "Don't have Embase subscription"**
```markdown
**Options**:
1. Contact your institution's library for access
2. Skip Embase: Use --skip-embase flag in STEP 6
3. Use PubMed/Scopus/WOS only (still effective for most reviews)

**Note**: Embase covers more European/pharmaceutical literature, but PubMed 
often suffices for clinical systematic reviews.
```

---

# STEP 5: Create Gold Standard PMID/DOI List

## Purpose
Create a validated CSV file containing the PMIDs and DOIs of all studies that were included in the final systematic review. Two methods are available: automated extraction (recommended) or manual LLM-based extraction.

## What is a Gold Standard?

Your gold standard is the list of **studies that were actually included** in your systematic review after full-text screening. These are typically found in:
- Table 1 (Study characteristics)
- Supplementary materials (Included studies list)
- References section (only the included studies, not all references)

**Example**: If your review included 47 studies after screening 2,356 articles, your gold standard will have 47 PMIDs/DOIs.

---

## Choose Your Method

```
┌────────────────────────────────────────────────────────────────┐
│ ⭐ Method A: Automated Extraction (RECOMMENDED)               │
│    • Time: 5-10 minutes (fully automated)                      │
│    • Accuracy: 85-95% with confidence scoring                  │
│    • Output: Both PMID and DOI automatically                   │
│    • Reproducible: Deterministic parsing + API lookup          │
│    • Best for: Standard paper format with "Included Studies"   │
│      table                                                      │
└────────────────────────────────────────────────────────────────┘
          ↓ Try this first
┌────────────────────────────────────────────────────────────────┐
│ 🔄 Method B: Manual LLM Extraction (Fallback)                 │
│    • Time: 20-40 minutes (manual + validation)                 │
│    • Accuracy: Variable (depends on LLM, needs validation)     │
│    • Output: Requires manual CSV creation                      │
│    • Use when: Method A fails, non-standard paper format       │
└────────────────────────────────────────────────────────────────┘
```

---

## Method A: Automated Extraction ⭐ **RECOMMENDED**

### Overview

This method automatically extracts included studies from your markdown paper using:
1. **Deterministic parsing**: Finds "Table 1: Included Studies" and extracts reference numbers
2. **Reference matching**: Maps reference numbers to full citations in References section
3. **Optional: Sampling-based extraction** (NEW): Runs extraction multiple times with majority voting for enhanced robustness  
3. **Multi-tier identifier lookup**: PubMed API (PMID+DOI) → CrossRef API (DOI) fallback
4. **Confidence scoring**: Validates matches using title similarity (>0.85 threshold)
5. **Gold standard generation**: Creates both simple and detailed CSV formats

### Requirements
- ✅ Published paper markdown from STEP 1 (`paper_<study>.md`)
- ✅ Paper has identifiable "Included Studies" table
- ✅ Python environment with Biopython (`systematic_review_queries`)
- ✅ PubMed API access (free, email required)

### The ONE COMMAND Workflow

### The ONE COMMAND Workflow

**Standard Extraction**:
```bash
python scripts/extract_included_studies.py <study_name> \
  --lookup-pmid \
  --pubmed-email your.email@institution.edu \
  --generate-gold-csv
```

**Sampling-Based Extraction** (for problematic PDFs or high-stakes reviews):
```bash
python scripts/extract_included_studies.py <study_name> \
  --sampling-runs 5 \
  --voting-threshold 0.60 \
  --lookup-pmid \
  --pubmed-email your.email@institution.edu \
  --generate-gold-csv
```

**Example**:
```bash
# Standard (try this first)
python scripts/extract_included_studies.py Godos_2024 \
  --lookup-pmid \
  --pubmed-email john.doe@university.edu \
  --generate-gold-csv

# Sampling-based (if PDF has issues)
python scripts/extract_included_studies.py Godos_2024 \
  --sampling-runs 5 --voting-threshold 0.60 \
  --lookup-pmid \
  --pubmed-email john.doe@university.edu \
  --generate-gold-csv
```

### What Happens Automatically

```
Step 1: Parse Markdown (Deterministic Parsing - No LLM)
═══════════════════════════════════════════════════════════════
├─ Finds "Table 1: Included Studies" or similar headings
├─ Extracts reference numbers from table rows: [12], [35], [48]
├─ Matches reference numbers to References section
└─ Parses citations: Author, Year, Title, Journal, DOI*, PMID*
   (* if present in citation text)

Time: 10-30 seconds
Success Rate: 85-90% (depends on paper formatting)

Step 2: Multi-Tier Identifier Lookup (Enhanced 2026)
═══════════════════════════════════════════════════════════════
Strategy: PubMed → Europe PMC → CrossRef (three-tier fallback)

For each extracted study:
  Tier 1 - PubMed E-utilities (Primary):
    1. Try 5 query strategies (exact → relaxed → broad)
    2. Validate: Year tolerance (±1), author match, metadata
    3. If match: Get both DOI and PMID from PubMed
    4. Confidence: Similarity + validation checks
    
  Tier 2 - Europe PMC (Fallback if Tier 1 fails):
    1. Structured queries (TITLE/FIRST_AUTHOR/PUB_YEAR)
    2. Same validation as Tier 1
    3. If match: Get PMID + DOI (both when available)
    
  Tier 3 - CrossRef (Final fallback):
    1. Title-based DOI lookup via CrossRef API
    2. Work type filtering (excludes preprints by default)
    3. If match: Get DOI only (CrossRef doesn't provide PMID)
    
  Quality control:
    • Default threshold: 0.80 (raised from 0.70)
    • Attach metadata: confidence, source (PubMed/EuropePMC/CrossRef)

Time: 3-8 minutes (depends on number of studies)
Success Rate: 95-98% DOI coverage, 90-95% PMID coverage

Step 3: Generate Gold Standard CSV Files
═══════════════════════════════════════════════════════════════
├─ Filter studies by confidence threshold (default: 0.85)
├─ Deduplicate PMIDs (if multiple references cite same article)
├─ Generate TWO formats:
│   • gold_pmids_<study>.csv         (PMID-only, backward compatible)
│   • gold_pmids_<study>_detailed.csv (PMID+DOI+metadata)
├─ Create quality report: gold_generation_report_<study>.md
└─ Statistics: DOI coverage, PMID coverage, confidence distribution

Time: 5-10 seconds
Output: Ready-to-use CSV files + detailed report
```

### Expected Output

```
═══════════════════════════════════════════════════════════════
  📄 Automated Gold Standard Extraction: Godos_2024
═══════════════════════════════════════════════════════════════

Step 1: Parsing markdown file...
✓ Found table: Table 1. Characteristics of included studies
✓ Extracted 47 reference numbers from table

Step 2: Matching references...
✓ Parsed 47 references from References section
✓ Matched 47 citations

📊 Initial Extraction Statistics:
   Total included studies: 47
   With DOI (from citation): 12 (25.5%)
   With PMID (from citation): 8 (17.0%)

Step 3: Looking up DOIs and PMIDs...
   Email: john.doe@university.edu
  Min confidence: 0.80
  Strategy: PubMed → Europe PMC → CrossRef

  [1/47] Mediterranean diet and cardiovascular disease risk...
      → [PubMed] DOI: 10.1016/j.nutr.2021.111234, PMID: 33445678,
        Confidence: 0.95 ✓
  
  [2/47] Effects of olive oil consumption on metabolic syndrome...
      → [PubMed] DOI: 10.1017/S0007114520001234, PMID: 32567890,
        Confidence: 0.92 ✓
  
  [3/47] 睡眠呼吸暂停综合征的研究...
    → PubMed: No match, trying Europe PMC...
    → Europe PMC: No match, trying CrossRef...
      → [CrossRef] DOI: 10.12345/cjrm.2020.03.001, Confidence: 0.88 ✓

[... 44 more studies ...]

✅ Updated 45 studies
   PubMed: 42 studies (DOI + PMID)
     Europe PMC: 0 studies (DOI + PMID when available)
     CrossRef: 3 studies (DOI only)

📊 Final Statistics:
   With DOI: 45 (95.7%)
   With PMID: 42 (89.4%)

📝 Generating gold standard CSV files...
   Confidence threshold: 0.85

✓ Accepted: 45 studies (confidence ≥ 0.85)
✗ Rejected: 2 studies (confidence < 0.85)

📁 Generated Files:
   ✓ studies/Godos_2024/included_studies.json
   ✓ studies/Godos_2024/gold_pmids_godos_2024.csv (45 PMIDs)
   ✓ studies/Godos_2024/gold_pmids_godos_2024_detailed.csv (45 rows)
   ✓ studies/Godos_2024/gold_generation_report_godos_2024.md

✅ Gold standard extraction complete!

═══════════════════════════════════════════════════════════════
```

### Verify Output Files

```bash
# Check generated files
ls -lh studies/Godos_2024/gold_pmids_*.csv

# Preview simple format (PMID-only)
head -5 studies/Godos_2024/gold_pmids_godos_2024.csv
# Output:
# 33445678
# 32567890
# 31789012
# 30123456

# Preview detailed format (PMID+DOI+metadata)
head -3 studies/Godos_2024/gold_pmids_godos_2024_detailed.csv
# Output:
# pmid,first_author,year,title,journal,doi
# 33445678,Garcia-Lopez M,2021,Mediterranean diet and cardiovascular...,Nutrients,10.1016/j.nutr.2021.111234
# 32567890,Fernandez A,2020,Effects of olive oil consumption...,Br J Nutr,10.1017/S0007114520001234

# Read quality report
cat studies/Godos_2024/gold_generation_report_godos_2024.md
```

### Advanced Options

```bash
# Custom confidence threshold (default: 0.80, raised from 0.70 in 2026)
python scripts/extract_included_studies.py Godos_2024 \
  --lookup-pmid \
  --pubmed-email your@email.edu \
  --min-confidence 0.80 \
  --generate-gold-csv

# Stricter matching (high-stakes validations)
python scripts/extract_included_studies.py Godos_2024 \
  --lookup-pmid \
  --pubmed-email your@email.edu \
  --min-confidence 0.90 \
  --gold-confidence 0.95 \
  --generate-gold-csv

# Year tolerance control (new 2026) - default ±1 year
python scripts/extract_included_studies.py Godos_2024 \
  --lookup-pmid \
  --pubmed-email your@email.edu \
  --max-year-diff 1 \
  --generate-gold-csv

# Exact year matching only
python scripts/extract_included_studies.py Godos_2024 \
  --lookup-pmid \
  --pubmed-email your@email.edu \
  --max-year-diff 0 \
  --generate-gold-csv

# With PubMed API key (increases rate limit 3x → 10x)
python scripts/extract_included_studies.py Godos_2024 \
  --lookup-pmid \
  --pubmed-email your@email.edu \
  --pubmed-api-key YOUR_NCBI_API_KEY \
  --generate-gold-csv

# Debug mode (show detailed parsing info)
python scripts/extract_included_studies.py Godos_2024 \
  --lookup-pmid \
  --pubmed-email your@email.edu \
  --generate-gold-csv \
  --debug
```

### Troubleshooting Method A

#### Issue: "Could not find included studies table"

**Cause**: Parser looks for specific table headings like "Table 1", "Included Studies", "Characteristics of included studies"

**Debug**:
```bash
# Check what table headings exist in your markdown
grep -i "table" studies/Godos_2024/paper_godos_2024.md | head -10

# Check if "included" appears in headings
grep -i "included" studies/Godos_2024/paper_godos_2024.md | head -10
```

**Solutions**:
1. **Manually edit markdown**: Rename table heading to include "included studies"
2. **Use --markdown-file with pre-processed version**
3. **Fall back to Method B** (manual LLM extraction)

#### Issue: "Low DOI/PMID coverage (<50%)"

**Cause**: 
- References missing DOIs/PMIDs in original citation
- PubMed API couldn't find matches (non-indexed journals, pre-2000 articles)
- CrossRef fallback also failed

**Debug**:
```bash
# Check confidence scores in included_studies.json
python -c "
import json
with open('studies/Godos_2024/included_studies.json') as f:
    data = json.load(f)
    for s in data['included_studies']:
        conf = s.get('lookup_metadata', {}).get('confidence', 'N/A')
        print(f'{s[\"first_author\"]} ({s[\"year\"]}): confidence={conf}, doi={s.get(\"doi\", \"None\")}')
"
```

**Solutions**:
1. **Lower confidence threshold**: `--min-confidence 0.60` (trade precision for coverage)
2. **Manual lookup**: For rejected studies, manually search PubMed/CrossRef and add to CSV
3. **Accept lower coverage**: If >70% have DOI, multi-key evaluation still beneficial

#### Issue: "Extracted wrong studies (included excluded studies)"

**Cause**: Parser found wrong table or misinterpreted table structure

**Debug**:
```bash
# Check which reference numbers were extracted
python -c "
import json
with open('studies/Godos_2024/included_studies.json') as f:
    data = json.load(f)
    ref_nums = [s['reference_number'] for s in data['included_studies']]
    print(f'Extracted references: {sorted(ref_nums)}')
"
```

**Solutions**:
1. **Manual verification**: Compare extracted list with paper's PRISMA diagram (final n=)
2. **Edit JSON**: Remove incorrect studies from `included_studies.json`
3. **Re-generate CSVs**: Run `generate_gold_standard.py` manually

#### Issue: "Parsing found 0 studies"

**Cause**: Paper format doesn't match expected structure

**Solution**: Use Method B (manual LLM extraction) instead

### When Method A Works Best

✅ **Ideal scenarios**:
- Paper has clear "Table 1: Characteristics of included studies"
- References section is numbered and matches table citations
- Modern articles (post-2000) with DOIs
- English-language references

⚠️ **May struggle with**:
- Unnumbered references (Author-Year style)
- Multiple tables with similar names
- Heavily formatted tables (merged cells, complex layout)
- Non-standard paper structure

---

## Method B: Manual LLM Extraction (Fallback)

### Overview

This method uses multiple LLM agents (ChatGPT, Claude, Gemini) to extract included studies, followed by cross-validation to detect hallucinations. While more time-consuming than Method A, it works with any paper format.

### When to Use Method B

Use manual LLM extraction when:
- ❌ Method A failed to find included studies table
- ❌ Paper has non-standard structure (no clear table)
- ✅ You want to verify Method A results (cross-check)
- ✅ Testing different LLM capabilities

### Requirements
- ✅ Published paper markdown from STEP 1 (`paper_<study>.md`)
- ✅ Access to multiple LLM agents (ChatGPT, Claude, Gemini, or Sciespace)
- ✅ Python environment with Biopython (`systematic_review_queries`)

### The Complete Workflow: LLM Extraction + Automated Validation

This process uses **multiple LLM agents** to extract PMIDs and **cross-validates** them to catch hallucinations:

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: LLM-Based PMID Extraction (Manual, 10-20 min)     │
├─────────────────────────────────────────────────────────────┤
│ • Ask 2-3 LLMs to extract included studies from paper      │
│ • Get PMIDs + DOIs + titles for each study                 │
│ • Save each LLM's output as separate CSV                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Automated Validation (Automated, 5-10 min)        │
├─────────────────────────────────────────────────────────────┤
│ • Script fetches actual metadata from PubMed for each PMID │
│ • Compares DOIs to detect hallucinations                    │
│ • Identifies which LLM source is most accurate              │
│ • Generates validated gold standard CSV                     │
└─────────────────────────────────────────────────────────────┘
```

### ⚠️ Important: Working Directory

**All validation commands must be run from the project root directory:**
```bash
# Navigate to project root (if not already there)
cd ~/Documents/DataScience/GU/Daniil/LLM/QueriesSystematicReview

# Verify you're in the right place
pwd
# Should output: .../QueriesSystematicReview
```

**Do NOT run from:**
- ❌ `studies/Godos_2024/` (study folder)
- ❌ `studies/Godos_2024/pmids_multiple_sources/` (sources folder)

---

### Step B.1: Prepare Study Folder

```bash
# Create folder for multiple LLM sources
mkdir -p studies/Godos_2024/pmids_multiple_sources
```

---

### Step B.2: Extract PMIDs Using Multiple LLM Agents

**Why multiple sources?** LLMs can hallucinate PMIDs. Using 2-3 sources and cross-validating catches errors.

### Recommended LLM Agents

Based on validation testing (see [ai_2022 case study](../studies/ai_2022/PMID_VALIDATION_REPORT.md)):
- ✅ **ChatGPT**: 100% accuracy (highly recommended)
- ✅ **Claude**: Expected high accuracy
- ✅ **Sciespace**: 100% accuracy (if available)
- ⚠️ **Gemini**: 0% accuracy in testing (use with caution, always validate)

### The Extraction Prompt

Use this prompt template with each LLM agent:

```markdown
I need you to extract the list of included studies from my systematic review paper.

For each included study in the final analysis (NOT excluded studies), provide:
1. Title (exact as published)
2. First author name and year (e.g., "Smith 2020")
3. DOI (Digital Object Identifier - very important!)
4. PMID (PubMed ID)

Please format your response as a CSV table with these exact columns:
Title,Authors,DOI,PMID

Look for the included studies in:
- Table 1 (Study Characteristics)
- Supplementary materials
- The list of studies included in meta-analysis
- References section (but only those that were included in the review)

Here is my paper:

[Paste your paper_<study>.md content here]

Important:
- Only include studies that were IN the final analysis
- Do NOT include excluded studies
- Verify PMID and DOI match each other
- If you can't find PMID/DOI, leave blank but include the title
```

### Execute with Each LLM

**LLM 1: ChatGPT**
1. Go to https://chat.openai.com
2. Paste the prompt with your paper content
3. Save response as CSV:
   ```bash
   # Save to: studies/Godos_2024/pmids_multiple_sources/godos_2024_chatgpt.csv
   ```

**LLM 2: Claude**
1. Go to https://claude.ai
2. Paste the prompt with your paper content
3. Save response as CSV:
   ```bash
   # Save to: studies/Godos_2024/pmids_multiple_sources/godos_2024_claude.csv
   ```

**LLM 3: Sciespace (optional)**
1. Go to https://typeset.io
2. Upload your paper PDF
3. Ask: "List all included studies with their PMIDs and DOIs"
4. Save response as CSV:
   ```bash
   # Save to: studies/Godos_2024/pmids_multiple_sources/godos_2024_sciespace.csv
   ```

### CSV Format Requirements

Each CSV file must have these columns (exact names not critical, script auto-detects):

```csv
Title,Authors,DOI,PMID
"Twenty-four-hour ambulatory blood pressure in children...",Amin 2004,10.1164/rccm.200309-1305OC,14764433
"Activity-adjusted 24-hour ambulatory blood pressure...",Amin 2008,10.1161/HYPERTENSIONAHA.107.099762,18071053
...
```

**Critical fields:**
- **Title**: Full study title
- **Authors**: First author and year (for reference)
- **DOI**: Digital Object Identifier (MOST IMPORTANT for validation)
- **PMID**: PubMed ID

**Example**: Studies from ai_2022:
```csv
Title,Authors,DOI,PMID
Twenty-four-hour ambulatory blood pressure in children with sleep-disordered breathing,Amin 2004,10.1164/rccm.200309-1305OC,14764433
Blood pressure associated with sleep-disordered breathing in a population sample of children,Bixler 2008,10.1161/HYPERTENSIONAHA.108.116756,18838624
```

---

### Step B.3: Validate PMIDs Across Sources

Now use the automated validation script to cross-check the LLM outputs against PubMed:

```bash
# IMPORTANT: Run from project root directory
cd /path/to/QueriesSystematicReview

# Activate environment
conda activate systematic_review_queries

# Run validation script (study name as argument)
python scripts/validate_pmids_direct.py Godos_2024 --json-report
```

**Working Directory**: You must run this from the **project root** (`QueriesSystematicReview/`), NOT from inside `studies/Godos_2024/` or `pmids_multiple_sources/`. The script automatically looks for CSV files in `studies/<study_name>/pmids_multiple_sources/`.

### What This Script Does

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Load All Source CSVs                                │
├─────────────────────────────────────────────────────────────┤
│ Auto-detects source from filename:                          │
│ • Contains "chatgpt" → ChatGPT                             │
│ • Contains "claude" → Claude                               │
│ • Contains "gemini" → Gemini                               │
│ • Contains "sciespace" → Sciespace                         │
│                                                              │
│ Loaded: 3 sources with 47 PMIDs each                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Extract Unique PMIDs                                │
├─────────────────────────────────────────────────────────────┤
│ Total unique PMIDs across all sources: 52                   │
│ (Some overlap, some unique to each source)                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Fetch Ground Truth from PubMed                      │
├─────────────────────────────────────────────────────────────┤
│ For EACH unique PMID:                                       │
│   • Query PubMed API: Entrez.efetch(pmid)                  │
│   • Get actual title, DOI, author, year                     │
│   • This is ground truth (PubMed is authoritative)          │
│                                                              │
│ Example:                                                    │
│   PMID 14764433 → Actual DOI: 10.1164/rccm.200309-1305oc  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Compare Claimed vs Actual DOIs                      │
├─────────────────────────────────────────────────────────────┤
│ For each source's claimed PMID:                             │
│   • Compare: DOI_claimed == DOI_actual (case-insensitive)  │
│   • If match → ✅ Correct PMID                             │
│   • If mismatch → ❌ Hallucinated PMID                     │
│                                                              │
│ Example (ChatGPT):                                          │
│   Claimed: PMID 14764433, DOI 10.1164/rccm.200309-1305OC  │
│   Actual:  PMID 14764433, DOI 10.1164/rccm.200309-1305oc  │
│   Result: ✅ MATCH (case-insensitive)                      │
│                                                              │
│ Example (Gemini):                                           │
│   Claimed: PMID 15306535, DOI 10.1254/ajrccm.170.10.1130  │
│   Actual:  PMID 15306535, DOI 10.1164/rccm.200407-885oc   │
│   Result: ❌ MISMATCH (Gemini hallucinated - different paper!)│
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Calculate Accuracy & Select Best Source             │
├─────────────────────────────────────────────────────────────┤
│ ChatGPT:   47/47 correct (100.0% accuracy) ✅              │
│ Claude:    46/47 correct (97.9% accuracy)  ✅              │
│ Gemini:    0/47 correct  (0.0% accuracy)   ❌              │
│                                                              │
│ Best source: ChatGPT                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 6: Generate Validated Gold Standard                    │
├─────────────────────────────────────────────────────────────┤
│ Output files:                                               │
│ • gold_pmids_godos_2024.csv (simple format for workflow)   │
│ • gold_pmids_godos_2024_detailed.csv (with metadata)       │
│ • pmid_validation_report_godos_2024.json (full analysis)   │
└─────────────────────────────────────────────────────────────┘
```

### Expected Output

```
═══════════════════════════════════════════════════════════════
  🔬 Direct PMID Validation: Godos_2024
═══════════════════════════════════════════════════════════════

📄 Loading: godos_2024_chatgpt.csv → chatgpt
   Found 47 studies with PMIDs

📄 Loading: godos_2024_claude.csv → claude
   Found 47 studies with PMIDs

📄 Loading: godos_2024_gemini.csv → gemini
   Found 47 studies with PMIDs

🔍 Found 52 unique PMIDs across all sources
────────────────────────────────────────────────────────────────
[1/52] Validating PMID 12345678... ✅ Smith 2020
[2/52] Validating PMID 23456789... ✅ Jones 2019
[3/52] Validating PMID 34567890... ❌ Mismatch detected
...

═══════════════════════════════════════════════════════════════
📈 SOURCE ACCURACY SUMMARY
═══════════════════════════════════════════════════════════════

   CHATGPT     : 47/47 correct (100.0%)  ← Best!
   CLAUDE      : 46/47 correct ( 97.9%)
   GEMINI      :  0/47 correct (  0.0%)  ← Hallucinated!

   🏆 Most accurate: CHATGPT

═══════════════════════════════════════════════════════════════
📝 Generating Gold PMIDs from chatgpt
═══════════════════════════════════════════════════════════════

   📄 Wrote 47 PMIDs to studies/Godos_2024/gold_pmids_godos_2024.csv
   📄 Wrote detailed version to gold_pmids_godos_2024_detailed.csv
   📋 JSON report: pmid_validation_report_godos_2024.json

✅ Validation Complete!
```

---

### Step B.4: Review and Verify Output

### Check the Generated Gold File

```bash
# From project root:
cd /path/to/QueriesSystematicReview

# Simple format (for workflow integration)
head studies/Godos_2024/gold_pmids_godos_2024.csv
```

Expected format:
```csv
pmid
12345678
23456789
34567890
...
```

### Check the Detailed File

```bash
# Detailed format (with metadata for reference)
head studies/Godos_2024/gold_pmids_godos_2024_detailed.csv
```

Expected format:
```csv
pmid,doi,first_author,year,title
12345678,10.1234/example,Smith,2020,Mediterranean diet and cardiovascular...
23456789,10.5678/example,Jones,2019,Sleep apnea and hypertension...
...
```

### Verify PMID Count

```bash
# Count PMIDs (subtract 1 for header)
wc -l studies/Godos_2024/gold_pmids_godos_2024.csv

# Should match number of included studies in your paper
# Example: 47 studies → 48 lines (47 PMIDs + 1 header)
```

---

## Alternative Validation Scripts

If you encounter issues or want different validation approaches:

### Method A: Multi-Source Cross-Validation (Title Matching)

Uses title similarity matching instead of DOI:

```bash
# From project root:
cd /path/to/QueriesSystematicReview

python scripts/validate_pmids_multi_source.py Godos_2024 --validate-pubmed
```

**When to use:**
- Some studies missing DOIs
- Want consensus-based validation
- Need title fuzzy matching

### Method B: DOI-Based Validation (Reverse Lookup)

Looks up PMIDs from DOIs instead of validating PMIDs:

```bash
# From project root:
cd /path/to/QueriesSystematicReview

python scripts/validate_pmids_by_doi.py Godos_2024 --json-report
```

**When to use:**
- Your paper lists DOIs but not PMIDs
- DOIs are more reliable in your source
- Want to verify PMID→DOI mapping

---

## Understanding Validation Results

### What Gets Validated

The script compares **DOIs** as the ground truth because:
1. DOIs are permanent, unique identifiers (one DOI = one paper, forever)
2. PMIDs can occasionally change or be incorrect
3. Title matching is fuzzy and unreliable for similar papers

### Example: Catching Hallucinations

**Real case from ai_2022 study:**

```
Gemini claimed for "Amin 2004" study:
  PMID: 15306535
  DOI:  10.1254/ajrccm.170.10.1130

PubMed actual record for PMID 15306535:
  Title: "Transmission of Mycobacterium tuberculosis..."
  Author: Nuermberger (not Amin!)
  Year: 2004
  DOI: 10.1164/rccm.200407-885oc

❌ MISMATCH! Gemini gave a valid PMID but for the WRONG paper!
→ This is a hallucination: plausible-looking but incorrect
```

### Why This Matters

Without validation, using hallucinated PMIDs would cause:
- ❌ Gold standard contains wrong studies
- ❌ Query performance metrics are meaningless
- ❌ Systematic review workflow produces garbage results

With validation:
- ✅ Catch hallucinations before they corrupt your gold standard
- ✅ Identify which LLM source is most reliable
- ✅ Generate verified gold PMIDs with confidence

---

## Troubleshooting

### Problem: "No CSV files found in pmids_multiple_sources"

```bash
# From project root, check folder exists and has files
cd /path/to/QueriesSystematicReview
ls -la studies/Godos_2024/pmids_multiple_sources/

# Make sure you saved LLM outputs as CSV files in this folder
# Example expected output:
#   godos_2024_chatgpt.csv
#   godos_2024_claude.csv
#   godos_2024_sciespace.csv
```

### Problem: "All sources show 0% accuracy"

**Possible causes:**
1. CSV columns misnamed (must have 'PMID', 'DOI', 'Title')
2. PMIDs are not valid PubMed IDs
3. DOIs are incomplete or malformed

**Solution:**
```bash
# Check CSV format
head -5 studies/Godos_2024/pmids_multiple_sources/*.csv

# Verify columns: Title, Authors, DOI, PMID (case-insensitive)
# Verify PMIDs are 8-digit numbers
# Verify DOIs start with "10."
```

### Problem: "LLM extracted excluded studies too"

**Solution**: Review the LLM's output and manually remove excluded studies before saving CSV:
1. Cross-check against paper's "Excluded Studies" table
2. Verify against PRISMA flow diagram (final n= count)
3. Only keep studies actually used in the analysis

### Problem: "Can't find PMID for a study"

Some included studies may not have PMIDs (e.g., grey literature).

**Options:**
1. **Omit them** (gold standard only covers PubMed-indexed studies)
2. **Add DOI-only** entries and use `validate_pmids_by_doi.py` to look up PMIDs
3. **Mark as non-PMID** and exclude from validation

### Problem: "Different LLMs give different PMID counts"

This is normal! Cross-validation will identify discrepancies.

**Investigation steps:**
```bash
# Compare which studies each LLM found
python scripts/validate_pmids_multi_source.py Godos_2024

# Review the discrepancies section in output
# Manually verify disputed studies in your paper
```

---

## Best Practices

### 1. Always Use Multiple LLM Sources

| Approach | Reliability | Time | Recommended? |
|----------|-------------|------|--------------|
| Single LLM (no validation) | Low | 10 min | ❌ Never |
| Single LLM + validation | Medium | 15 min | ⚠️ Acceptable |
| 2-3 LLMs + validation | High | 20 min | ✅ Best practice |

### 2. Prefer ChatGPT or Claude

Based on validation testing:
- ✅ **ChatGPT**: 100% accuracy (ai_2022 study)
- ✅ **Claude**: Expected high accuracy
- ✅ **Sciespace**: 100% accuracy when available
- ❌ **Gemini**: 0% accuracy (ai_2022 study) - DO NOT use without validation

### 3. Require DOI + PMID Pairs

When prompting LLMs:
```markdown
IMPORTANT: For each study, provide BOTH the DOI and PMID.
The DOI is critical for validation - do not skip it.
```

### 4. Validate Before Using in Workflow

```bash
# ALWAYS run validation before STEP 6
python scripts/validate_pmids_direct.py <study_name> --json-report

# Only proceed if accuracy ≥ 95% for at least one source
```

---

## Output Files

After validation, you'll have:

| File | Purpose |
|------|---------|
| `gold_pmids_<study>.csv` | **Use this in STEP 6** - Simple format (pmid column only) |
| `gold_pmids_<study>_detailed.csv` | Reference with metadata (pmid, doi, author, year, title) |
| `pmid_validation_report_<study>.json` | Full validation details for documentation |

---

## Time Estimate

| Task | Time | Type |
|------|------|------|
| Extract PMIDs from 2-3 LLMs | 10-20 min | Manual |
| Run validation script | 5-10 min | Automated |
| Review discrepancies | 5-10 min | Manual |
| **Total** | **20-40 min** | **Mostly automated** |

---

## Example: Complete Workflow for ai_2022 Study

See the full case study with real results:
- [studies/ai_2022/PMID_VALIDATION_REPORT.md](../studies/ai_2022/PMID_VALIDATION_REPORT.md)

**Summary:**
- 14 included studies
- 3 LLM sources (ChatGPT, Gemini, Sciespace)
- Validation found Gemini hallucinated all 14 PMIDs
- ChatGPT and Sciespace both 100% accurate
- Generated validated gold standard in 15 minutes

---

# STEP 6: Run Complete Automated Workflow

## Purpose
Execute the complete multi-database systematic review workflow in ONE command: query execution → deduplication → scoring → aggregation → evaluation.

## Requirements
- ✅ Query files from STEP 3 (`queries.txt`, `queries_scopus.txt`, etc.)
- ✅ Gold standard from STEP 5 (`gold_pmids_godos_2024.csv`)
- ✅ Embase CSVs from STEP 4 (optional but recommended)
- ✅ API keys configured (PubMed, Scopus, WOS)

## 🆕 NEW FEATURE: DOI-Aware Multi-Key Evaluation

### What Is Multi-Key Evaluation?

**The Problem with PMID-Only Matching:**
- Scopus and Web of Science primarily use DOI, not always PMID
- When retrieved articles have DOI but gold has PMID (or vice versa), PMID-only matching misses them
- This creates **5-15% false negative rate** on multi-database queries
- Underestimates recall for Scopus/WoS queries

**The Solution: DOI-Primary Matching**
- Uses DOI as primary identifier (universal across all databases)
- Falls back to PMID only for articles without DOI
- More accurate evaluation of multi-database search strategies

### When to Use Multi-Key Evaluation?

✅ **Use multi-key evaluation when:**
- Running queries on Scopus or Web of Science
- Your gold standard includes DOI information
- You want accurate recall measurement across databases
- Evaluating multi-database search strategies

❌ **PMID-only is fine when:**
- Running PubMed-only queries
- Your gold standard only has PMIDs (no DOI)
- Quick testing or prototyping

---

## The Universal Command

### Standard Workflow (PMID-Only)

```bash
bash scripts/run_complete_workflow.sh Godos_2024 --databases pubmed,scopus,wos
```

### Enhanced Workflow (DOI-Aware Multi-Key)

```bash
bash scripts/run_complete_workflow.sh Godos_2024 \
  --databases pubmed,scopus,wos \
  --multi-key
```

If `gold_pmids_<study>_detailed.csv` already exists, the wrapper also enables multi-key matching automatically even when `--multi-key` is omitted. Passing the flag explicitly is still useful when you want to make that behavior obvious in the command line.

**That's it!** This single command runs the entire workflow automatically.

## What This Command Does

```
═══════════════════════════════════════════════════════════════
  🚀 Complete Systematic Review Workflow: Godos_2024
═══════════════════════════════════════════════════════════════

Phase 1: Validation
───────────────────────────────────────────────────────────────
Checking study directory...
  ✓ studies/Godos_2024/ exists

Checking required files...
  ✓ queries.txt found (6 queries)
  ✓ queries_scopus.txt found (6 queries)
  ✓ queries_wos.txt found (6 queries)
  ✓ gold_pmids_godos_2024.csv found (47 PMIDs)

Checking optional Embase files...
  ✓ queries_embase.txt found (6 queries)
  ✓ embase_manual_queries/ found (6 CSV files)

═══════════════════════════════════════════════════════════════

Phase 2: Embase Import (if CSV files found)
───────────────────────────────────────────────────────────────
Importing Embase query results from CSV files...

Processing embase_query1.csv...
  • Found 1,245 records
  • Extracted 987 DOIs
  • Saved to: studies/Godos_2024/embase_query1.json

Processing embase_query2.csv...
  • Found 856 records
  • Extracted 723 DOIs
  • Saved to: studies/Godos_2024/embase_query2.json

[... queries 3-6 ...]

✅ Embase import complete!
   Total: 6 JSON files created
   Total records: 5,432
   Total unique DOIs: 4,187

═══════════════════════════════════════════════════════════════

Phase 3: API Query Execution
───────────────────────────────────────────────────────────────
Running queries on selected databases: pubmed, scopus, wos

Database: PubMed (6 queries)
──────────────────────────────────────────────────
Query 1/6: Running...
  ✓ Found 2,341 results
  ✓ Saved to: benchmark_outputs/Godos_2024/details_*.json

Query 2/6: Running...
  ✓ Found 1,523 results

[... queries 3-6 ...]

Database: Scopus (6 queries)
──────────────────────────────────────────────────
[Similar output for Scopus...]

Database: Web of Science (6 queries)
──────────────────────────────────────────────────
[Similar output for WOS...]

✅ API queries complete!
   PubMed: 6 queries, 8,432 total results
   Scopus: 6 queries, 6,234 total results
   WOS: 6 queries, 5,123 total results

═══════════════════════════════════════════════════════════════

Phase 4: Deduplication & Scoring
───────────────────────────────────────────────────────────────
Deduplicating results across databases (DOI-based)...
  ✓ Found 15,234 total records
  ✓ Identified 9,876 unique DOIs
  ✓ Removed 5,358 duplicates (35.2%)

Scoring queries against gold standard...
  ✓ Gold standard: 47 PMIDs
  
Individual Query Performance:
┌────────┬───────┬──────────┬──────────┬───────────┬───────┐
│ DB     │ Query │ Retrieved│ TP (Gold)│ Recall    │ Prec. │
├────────┼───────┼──────────┼──────────┼───────────┼───────┤
│ PubMed │ 1     │ 2341     │ 45       │ 0.957     │ 0.019 │
│ PubMed │ 2     │ 1523     │ 43       │ 0.915     │ 0.028 │
│ PubMed │ 3     │ 456      │ 38       │ 0.809     │ 0.083 │
│ PubMed │ 4     │ 1834     │ 44       │ 0.936     │ 0.024 │
│ PubMed │ 5     │ 892      │ 41       │ 0.872     │ 0.046 │
│ PubMed │ 6     │ 1987     │ 45       │ 0.957     │ 0.023 │
├────────┼───────┼──────────┼──────────┼───────────┼───────┤
│ Scopus │ 1     │ 1834     │ 42       │ 0.894     │ 0.023 │
[... more rows ...]
└────────┴───────┴──────────┴──────────┴───────────┴───────┘

Best single query: PubMed Query 1 (Recall: 95.7%, 2341 to screen)

═══════════════════════════════════════════════════════════════

Phase 5: Aggregation Strategies
───────────────────────────────────────────────────────────────
Aggregating queries using 5 different strategies...

Strategy 1: consensus_k2 (require ≥2 queries to agree)
  ✓ Created aggregate with 1,234 unique PMIDs
  ✓ Saved to: aggregates/Godos_2024/consensus_k2.txt

Strategy 2: two_stage_screen (high-precision first, high-recall second)
  ✓ Created aggregate with 1,456 unique PMIDs

Strategy 3: precision_gated_union (include high-precision + balanced)
  ✓ Created aggregate with 2,789 unique PMIDs

Strategy 4: time_stratified_hybrid (different strategies by publication year)
  ✓ Created aggregate with 2,801 unique PMIDs

Strategy 5: weighted_vote (queries weighted by individual performance)
  ✓ Created aggregate with 2,795 unique PMIDs

✅ Aggregation complete!
   5 strategies created in: aggregates/Godos_2024/

═══════════════════════════════════════════════════════════════

Phase 6: Evaluate Aggregation Strategies
───────────────────────────────────────────────────────────────
Scoring each aggregation strategy against gold standard...

🏆 FINAL RESULTS: Aggregation Strategy Performance
═══════════════════════════════════════════════════════════════
Strategy Name             Retrieved  TP   Recall   Precision  F1
─────────────────────────────────────────────────────────────
precision_gated_union     2789       47   1.000    0.017     0.033
time_stratified_hybrid    2801       47   1.000    0.017     0.033
weighted_vote             2795       47   1.000    0.017     0.033
two_stage_screen          1456       46   0.979    0.032     0.061
consensus_k2              1234       44   0.936    0.036     0.069
═══════════════════════════════════════════════════════════════

✅ WORKFLOW COMPLETE!

📊 Summary:
   • 3 strategies found 100% of gold studies (Recall = 1.000)
   • Best strategy: precision_gated_union (2789 articles, all 47 found)
   • Time saved: ~85% vs manual screening of all 15,234 results

📁 Results saved to:
   • aggregates/Godos_2024/           (PMID lists for each strategy)
   • aggregates_eval/Godos_2024/      (Performance metrics CSV)
   • benchmark_outputs/Godos_2024/    (Individual query results)

🎯 Recommendation:
   Use precision_gated_union strategy for screening
   → Screen 2,789 articles instead of 15,234 (81.7% reduction)
   → Guaranteed to find all 47 gold studies

═══════════════════════════════════════════════════════════════
```

## Command Options

### Basic Usage

```bash
# Run with the wrapper defaults: pubmed,scopus,wos
bash scripts/run_complete_workflow.sh Godos_2024

# Specify the provider set explicitly
bash scripts/run_complete_workflow.sh Godos_2024 --databases pubmed,scopus,wos

# Embase CSV imports are still auto-detected; including embase here is optional shorthand
bash scripts/run_complete_workflow.sh Godos_2024 --databases pubmed,scopus,wos,embase
```

### Mode Selection

```bash
# Run the full score-and-aggregate flow once per aligned query block
bash scripts/run_complete_workflow.sh Godos_2024 --query-by-query

# Run that same flow for a single query index only
bash scripts/run_complete_workflow.sh Godos_2024 --query-index 3
```

### Advanced Options

```bash
# Skip Embase even if CSV files exist
bash scripts/run_complete_workflow.sh Godos_2024 --databases pubmed,scopus --skip-embase

# Import Embase only (don't re-run API queries)
bash scripts/run_complete_workflow.sh Godos_2024 --embase-only

# Skip aggregation (only run queries and scoring)
bash scripts/run_complete_workflow.sh Godos_2024 --databases pubmed --skip-aggregation

# Show help
bash scripts/run_complete_workflow.sh --help
```

### Flags Explained

| Flag | Purpose | Use When |
|------|---------|----------|
| `--databases` | Select which API-backed providers to query | Customizing provider selection; default is `pubmed,scopus,wos` |
| `--skip-embase` | Ignore Embase CSV files | Testing without Embase |
| `--embase-only` | Only import Embase, skip APIs | Already ran API queries |
| `--skip-aggregation` | Skip aggregation phase | Only want individual query performance |
| `--query-by-query` | Run score + aggregation once per query block | Comparing query families one at a time |
| `--query-index N` | Run score + aggregation for one query block | Debugging or targeted experiments |
| `--multi-key` | Use DOI-first matching with PMID fallback | Preferred when detailed gold CSV exists; auto-enabled when the detailed gold CSV is detected |
| `--help` | Show usage information | Learning command options |

**Important Embase note:** Embase is still integrated via manual CSV export and JSON import, not as a live API-backed provider. `scripts/run_complete_workflow.sh` accepts `,embase` for convenience, but strips it before forwarding provider names to the Python CLI.

## Understanding the Output Files

### Standard Output (PMID-Only Matching)

After the script completes, you'll see:

```
🏆 Aggregation Strategy Performance:
════════════════════════════════════════════════════════════
name                       Retrieved  TP   Recall   Precision  F1
precision_gated_union      1704       14   1.000    0.008      0.016
time_stratified_hybrid     1704       14   1.000    0.008      0.016
weighted_vote              1704       14   1.000    0.008      0.016
consensus_k2               488        5    0.357    0.010      0.020
two_stage_screen           556        5    0.357    0.009      0.018
```

**What this means:**
- ✅ Three strategies achieved 100% recall (found all 14 gold studies)
- ✅ `precision_gated_union` is recommended (balance of recall/precision)
- ✅ Results saved to `aggregates/ai_2022/precision_gated_union.txt`

### Multi-Key Enhanced Output (DOI-Aware)

With `--multi-key` flag enabled:

```
🏆 Aggregation Strategy Performance (Multi-Key DOI-Primary):
════════════════════════════════════════════════════════════════════════════════
[INFO] Multi-key mode: Gold standard has 12 PMIDs and 12 DOIs
[INFO] Retrieved results contain 487 unique articles (by DOI)

name                       Retrieved  TP   DOI   PMID-fb  Recall   Precision  F1
precision_gated_union      552        4    4     0        0.333    0.007      0.014
time_stratified_hybrid     535        4    4     0        0.333    0.007      0.015
weighted_vote              533        4    4     0        0.333    0.008      0.015
consensus_k2               487        4    4     0        0.333    0.008      0.016
two_stage_screen           468        4    4     0        0.333    0.009      0.017
```

**Key differences from PMID-only:**

| Metric | Description | Example |
|--------|-------------|---------|
| **DOI** | Articles matched by DOI (primary identifier) | `4` |
| **PMID-fb** | Articles matched by PMID fallback (only for gold without DOI) | `0` |
| **TP** | Total true positives (`DOI + PMID-fb`) | `4` |
| **Gold** | Unique articles in gold standard | `12` (not 24!) |

**Interpretation:**
- All 4 matches found via DOI (universal identifier)
- 0 matches required PMID fallback (all gold articles have DOI)
- This confirms DOI-based deduplication is working correctly
- For Scopus-heavy queries, DOI matches prevent false negatives

---

## 📊 Complete Workflow Examples

### Example 1: New Study with Automated Gold Standard

```bash
# ============================================================================
# Complete workflow with automated gold standard extraction
# ============================================================================

# Step 1: Create study directory
mkdir -p studies/microbiome_2024

# Step 2: Place raw files
cp ~/Downloads/paper_microbiome_2024.pdf studies/microbiome_2024/

# Step 3: Extract included studies with DOI/PMID lookup
python scripts/extract_included_studies.py microbiome_2024 \
  --lookup-pmid \
  --pubmed-email your.email@institution.edu \
  --generate-gold-csv

# Output:
#   ✓ studies/microbiome_2024/included_studies.json (with DOI+PMID)
#   ✓ studies/microbiome_2024/gold_pmids_microbiome_2024_detailed.csv

# Step 4: Generate strategy-aware queries
/generate_multidb_prompt --command_name run_microbiome_2024_multidb_strategy ...
/run_microbiome_2024_multidb_strategy
# Writes search_strategy.md and queries*.txt automatically

# Step 5: Run complete workflow with multi-key evaluation
bash scripts/run_complete_workflow.sh microbiome_2024 \
  --databases pubmed,scopus,wos \
  --multi-key

# Done! Results in aggregates_eval/microbiome_2024/
```

**Time**: ~45 minutes (mostly automated)

### Example 2: Existing Study - Compare PMID-Only vs Multi-Key

```bash
# ============================================================================
# Compare evaluation methods on same data
# ============================================================================

# Step 1: Run PMID-only baseline (for comparison)
bash scripts/run_complete_workflow.sh ai_2022 \
  --databases pubmed,scopus,wos

# Results saved to: aggregates_eval/ai_2022/ (PMID-only)

# Step 2: Create gold standard with DOI (if not exists)
python scripts/extract_included_studies.py ai_2022 \
  --lookup-pmid \
  --pubmed-email your.email@institution.edu \
  --generate-gold-csv

# Step 3: Run multi-key evaluation
bash scripts/run_complete_workflow.sh ai_2022 \
  --databases pubmed,scopus,wos \
  --multi-key

# Results saved to: aggregates_eval/ai_2022/ (with multi-key metrics)

# Step 4: Compare results
echo "=== PMID-Only Baseline ==="
grep "consensus_k2" aggregates_eval/ai_2022/sets_summary_*.csv | head -1

echo "=== Multi-Key DOI-Aware ==="
grep "consensus_k2" aggregates_eval/ai_2022/sets_summary_*.csv | tail -1
```

**Expected improvement**: 5-15% recall increase for Scopus-heavy queries

### Example 3: Quick Testing with PubMed Only

```bash
# ============================================================================
# Fast testing workflow (PubMed only, no multi-key needed)
# ============================================================================

# PubMed-only queries don't benefit from multi-key (all have PMID)
bash scripts/run_complete_workflow.sh ai_2022 --databases pubmed

# This is faster and PMID-only matching is sufficient
```

**Time**: ~5 minutes (no Scopus/WoS API calls)

---

## Understanding the Output Files

### Folder Structure After Completion

```
studies/Godos_2024/
├── benchmark_outputs/
│   └── Godos_2024/
│       ├── details_20260121-143022.json  (Individual query results)
│       └── summary_20260121-143022.csv   (Query performance table)
│
├── aggregates/
│   └── Godos_2024/
│       ├── consensus_k2.txt              (Strategy 1 PMIDs)
│       ├── two_stage_screen.txt          (Strategy 2 PMIDs)
│       ├── precision_gated_union.txt     (Strategy 3 PMIDs)
│       ├── time_stratified_hybrid.txt    (Strategy 4 PMIDs)
│       └── weighted_vote.txt             (Strategy 5 PMIDs)
│
└── aggregates_eval/
    └── Godos_2024/
        ├── sets_summary_20260121-143045.csv   (Strategy performance)
        └── sets_details_20260121-143045.json  (Detailed metrics)
```

### Key Files to Review

**1. `aggregates_eval/.../sets_summary_*.csv`** (MOST IMPORTANT)
```csv
name,retrieved,tp,recall,precision,f1
precision_gated_union,2789,47,1.000,0.017,0.033
time_stratified_hybrid,2801,47,1.000,0.017,0.033
weighted_vote,2795,47,1.000,0.017,0.033
```
- **recall = 1.000** means strategy found ALL gold studies ✅
- **retrieved** shows how many articles you'll need to screen
- **Choose the strategy with Recall=1.0 AND lowest retrieved count**

**2. `aggregates/.../precision_gated_union.txt`** (Use for screening)
```
12345678
23456789
34567890
...
```
- List of PMIDs to screen (one per line)
- Import this into your screening tool (Covidence, Rayyan, etc.)

**3. `benchmark_outputs/.../summary_*.csv`** (Individual query analysis)
```csv
database,query_num,retrieved,tp,recall,precision
pubmed,1,2341,45,0.957,0.019
pubmed,2,1523,43,0.915,0.028
```
- Shows performance of each query individually
- Useful for understanding which precision level works best

## What to Do Next (After Workflow Completes)

### 1. Choose Best Strategy

Look at `aggregates_eval/.../sets_summary_*.csv`:

```bash
# View strategy performance
cat aggregates_eval/Godos_2024/sets_summary_*.csv
```

**Decision criteria:**
- ✅ **Recall = 1.000** (found all gold studies)
- ✅ **Lowest "retrieved" count** (fewer articles to screen)

**Example**: All 3 strategies have Recall=1.0, so choose `precision_gated_union` (2789 articles) over `time_stratified_hybrid` (2801 articles).

### 2. Export PMIDs for Screening

```bash
# Copy chosen strategy PMIDs
cp aggregates/Godos_2024/precision_gated_union.txt \
   ~/Desktop/godos_2024_screening_list.txt

# Or convert to CSV for import into screening tools
# (Add header row for Covidence/Rayyan)
echo "pmid" > screening_import.csv
cat aggregates/Godos_2024/precision_gated_union.txt >> screening_import.csv
```

### 3. Import to Screening Tool

**Covidence:**
1. Create new review
2. Import → Upload file
3. Select `screening_import.csv`

**Rayyan:**
1. Create new review
2. Import → PubMed IDs
3. Paste contents of `precision_gated_union.txt`

**Manual Screening:**
1. Use PubMed batch lookup: https://www.ncbi.nlm.nih.gov/sites/batchentrez
2. Paste PMIDs, select "PubMed", click "Retrieve"
3. Export as CSV or XML

## Time Breakdown

| Phase | Time | Automated? |
|-------|------|------------|
| Validation | 10 seconds | ✅ Yes |
| Embase import | 1-2 minutes | ✅ Yes |
| API queries (PubMed+Scopus+WOS) | 10-15 minutes | ✅ Yes |
| Deduplication | 30 seconds | ✅ Yes |
| Scoring | 1 minute | ✅ Yes |
| Aggregation | 2 minutes | ✅ Yes |
| Evaluation | 1 minute | ✅ Yes |
| **Total** | **15-25 minutes** | **100% automated** |

---

## Time Breakdown

| Phase | Time | Automated? |
|-------|------|------------|
| Validation | 10 seconds | ✅ Yes |
| Embase import | 1-2 minutes | ✅ Yes |
| API queries (PubMed+Scopus+WOS) | 10-15 minutes | ✅ Yes |
| Deduplication | 30 seconds | ✅ Yes |
| Scoring | 1 minute | ✅ Yes |
| Aggregation | 2 minutes | ✅ Yes |
| Evaluation | 1 minute | ✅ Yes |
| **Total** | **15-25 minutes** | **100% automated** |

## Troubleshooting STEP 6

### Multi-Key Specific Issues

#### Issue: "Gold standard missing DOI column"

**Cause**: Your gold CSV was created before DOI support

**Solution**:
```bash
# Regenerate gold standard with DOI
python scripts/extract_included_studies.py <study> \
  --lookup-pmid \
  --pubmed-email your.email@institution.edu \
  --generate-gold-csv

# Or manually add DOI column to existing CSV
```

#### Issue: "Multi-key shows 0 DOI matches but PMID-only works"

**Cause**: Retrieved results don't have DOI, or DOI format mismatch

**Debug**:
```bash
# Check DOI coverage in retrieved results
python -c "
import json
with open('benchmark_outputs/<study>/details_*.json') as f:
    data = json.load(f)
    for qname, qdata in data.items():
        dois = [d for d in qdata.get('retrieved_dois', []) if d]
        print(f'{qname}: {len(dois)} articles with DOI')
"
```

**Solution**: If DOI coverage is low (<50%), PMID-only matching may be more appropriate

#### Issue: "Gold count doubled (24 instead of 12)"

**Cause**: Bug in older version (now fixed)

**Solution**: Update to latest version - gold count now correctly uses `max(pmids, dois)` not `sum`

#### Issue: "Multi-key aggregate CSV files not found"

**Cause**: `--multi-key` flag not passed to aggregation step

**Solution**:
```bash
# Ensure flag is present in workflow script
bash scripts/run_complete_workflow.sh <study> \
  --databases pubmed,scopus,wos \
  --multi-key  # ← Must be here
```

---

### General Issues

### Error: "Queries file not found"

```bash
# Check file exists
ls studies/Godos_2024/queries.txt

# If missing, complete STEP 3 first
```

### Error: "Gold standard not found"

```bash
# Check file name matches pattern: gold_pmids_<STUDY_NAME>.csv
ls studies/Godos_2024/gold_pmids_*.csv

# Correct naming:
# ✅ gold_pmids_godos_2024.csv
# ❌ gold_list.csv
# ❌ gold_pmids.csv
```

### Error: "API authentication failed"

```bash
# Check .env file has correct keys
cat .env | grep API_KEY

# Re-export environment variables
export $(cat .env | xargs)

# Test PubMed connection
python -c "from Bio import Entrez; Entrez.email='test@test.com'; print('OK')"
```

### Warning: "Embase CSV files not found"

```markdown
This is not an error - the workflow will continue without Embase.

If you want to include Embase:
1. Complete STEP 4 (manual Embase export)
2. Re-run the workflow
```

### Error: "Query execution failed"

```markdown
**Common causes:**
1. API rate limit exceeded → Wait 5 minutes, try again
2. Invalid query syntax → Test query manually on database website
3. Network timeout → Check internet connection

**Solutions:**
- For PubMed: Add/update NCBI_API_KEY in .env (increases rate limit)
- For Scopus/WOS: Verify institutional access is active
- For syntax errors: Review and fix queries in queries*.txt files
```

---

# Complete Workflow Checklist

Use this checklist to ensure you've completed all steps correctly:

## Prerequisites (One-Time Setup)
- [ ] Conda installed (Miniconda or Anaconda)
- [ ] Repository cloned to local machine
- [ ] Conda environment `systematic_review_queries` created
- [ ] Conda environment `docling` created  
- [ ] `.env` file created with API keys
- [ ] API keys tested (PubMed, Scopus, WOS)

## Study-Specific Workflow

### STEP 1: PDF Conversion
- [ ] Study folder created: `studies/<YOUR_STUDY>/`
- [ ] `Paper.pdf` file present in study folder
- [ ] `PROSPERO.pdf` file present in study folder
- [ ] Ran: `python scripts/prepare_study.py <YOUR_STUDY> --docling-env docling`
- [ ] Verified: `paper_<study>.md` created
- [ ] Verified: `prospero_<study>.md` created

### STEP 2: LLM Command Generation
- [ ] Ran either `/generate_multidb_prompt ... --relaxation_profile ...` or `/generate-multidb-prompt ...`
- [ ] Command or prompt file created in `.gemini/commands/` or `.github/prompts/`
- [ ] Verified command name is correct

### STEP 3: Query Generation
- [ ] Ran: `/<command_name>` (LLM command from STEP 2)
- [ ] Verified: `search_strategy.md` was written automatically
- [ ] Verified: `queries.txt`, `queries_scopus.txt`, `queries_wos.txt`, and `queries_embase.txt` were written automatically as needed
- [ ] Verified: Each database file contains 6 aligned query blocks
- [ ] Manually reviewed queries for accuracy

### STEP 4: Embase Export (Optional but Recommended)
- [ ] Created folder: `studies/<YOUR_STUDY>/embase_manual_queries/`
- [ ] Logged into Embase.com
- [ ] Exported Query 1 → saved as `embase_query1.csv`
- [ ] Exported Query 2 → saved as `embase_query2.csv`
- [ ] Exported Query 3 → saved as `embase_query3.csv`
- [ ] Exported Query 4 → saved as `embase_query4.csv`
- [ ] Exported Query 5 → saved as `embase_query5.csv`
- [ ] Exported Query 6 → saved as `embase_query6.csv`
- [ ] Verified: All CSV files have DOI column

### STEP 5: Gold Standard Creation
- [ ] **Option A: Automated Extraction (Recommended)**
  - [ ] Ran: `python scripts/extract_included_studies.py <YOUR_STUDY> --lookup-pmid --pubmed-email your@email.edu`
  - [ ] OR: Ran with sampling for robustness: `python scripts/extract_included_studies.py <YOUR_STUDY> --sampling-runs 5 --voting-threshold 0.60 --lookup-pmid --pubmed-email your@email.edu`
  - [ ] Verified: `included_studies.json` or `included_studies_sampling.json` created
  - [ ] Verified: DOI/PMID coverage >85%
  - [ ] If using sampling: Reviewed voting statistics
- [ ] **Option B: Manual Extraction (Fallback)**
  - [ ] Identified all included studies from published paper
  - [ ] Converted study citations to PMIDs (via PubMed)
- [ ] Created file: `gold_pmids_<YOUR_STUDY>.csv`
- [ ] Format: One PMID per line, no header, no quotes
- [ ] Verified: Line count matches number of included studies
- [ ] Checked for duplicate PMIDs (removed if found)

### STEP 6: Run Workflow
- [ ] Activated conda environment: `conda activate systematic_review_queries`
- [ ] Ran: `bash scripts/run_complete_workflow.sh <YOUR_STUDY> --databases pubmed,scopus,wos`
- [ ] Workflow completed without errors
- [ ] Results folder created: `aggregates_eval/<YOUR_STUDY>/`
- [ ] Reviewed: `sets_summary_*.csv` file
- [ ] Identified strategy with Recall=1.0 and lowest retrieved count
- [ ] Exported PMIDs from chosen strategy for screening

## Post-Workflow
- [ ] Copied PMID list to screening tool (Covidence/Rayyan)
- [ ] Documented which aggregation strategy was used
- [ ] Saved workflow outputs for reproducibility
- [ ] (Optional) Committed study files to git repository

---

# Comparing Workflows: Before vs After

## Before (Old Manual Workflow)

```bash
# Step 1: Edit study-specific script
vim run_workflow_sleep_apnea.sh
# Manually change: STUDY_NAME="sleep_apnea"

# Step 2: Run queries
bash run_workflow_sleep_apnea.sh

# Step 3: Manually import Embase (separate script, different folder)
# Copy CSVs to different location
# Edit another script
bash scripts/complete_embase_workflow.sh

# Step 4: Manually re-aggregate (different script, manual paths)
python aggregate_queries.py --inputs ...long paths... --outdir ...

# Step 5: Manually score (different script)
python llm_sr_select_and_score.py ...

# Total: 5+ commands, 2+ scripts to edit, 30-40 minutes
```

**Pain points:**
- ❌ Had to edit scripts for each study (hardcoded study names)
- ❌ Separate Embase workflow (different folder structure)
- ❌ Manual path construction for aggregation
- ❌ Easy to forget steps or run in wrong order
- ❌ Not portable (paths hardcoded)

## After (New Automated Workflow)

```bash
# All 6 steps from raw PDFs:

# 1. Convert PDFs
python scripts/prepare_study.py Godos_2024 --docling-env docling

# 2. Generate LLM command
/generate_multidb_prompt --command_name run_godos_2024_multidb_strategy --relaxation_profile default ...

# 3. Run LLM
/run_godos_2024_multidb_strategy
# → Writes search_strategy.md and queries*.txt automatically

# 4. Export Embase (manual, but streamlined)
# Save CSVs to embase_manual_queries/

# 5. Create gold standard
# Option A: Automated (recommended)
python scripts/extract_included_studies.py Godos_2024 --lookup-pmid --pubmed-email your@email.edu

# OR: With sampling for enhanced robustness
python scripts/extract_included_studies.py Godos_2024 --sampling-runs 5 --voting-threshold 0.60 --lookup-pmid --pubmed-email your@email.edu

# Option B: Manual (fallback)
# Create gold_pmids_godos_2024.csv manually

# 6. Run complete workflow (ONE COMMAND)
bash scripts/run_complete_workflow.sh Godos_2024 --databases pubmed,scopus,wos

# Total: 6 commands, 0 scripts to edit, 45-90 minutes end-to-end
```

**Improvements:**
- ✅ No script editing (study name as parameter)
- ✅ Unified Embase workflow (auto-detects CSVs)
- ✅ Automatic path construction
- ✅ All steps in logical order
- ✅ Fully portable (works for ANY study)
- ✅ Complete end-to-end from PDFs to results

## Time Savings

| Task | Before | After | Savings |
|------|--------|-------|---------|
| Script editing | 5-10 min | 0 min | 100% |
| Embase integration | 15-20 min | 2 min | 85% |
| Aggregation setup | 10 min | 0 min | 100% |
| Manual path construction | 5 min | 0 min | 100% |
| Total manual work per study | 35-45 min | 2 min | **95%** |

---

# What Cannot Be Automated

These steps still require human involvement:

## 1. Embase Export (10-30 minutes)
**Why**: No API available for Embase database

**Manual steps**:
1. Log into Embase.com
2. Copy query from `queries_embase.txt`
3. Paste into search box
4. Click "Export" → Save as CSV
5. Repeat for each query (typically 6 queries)

**Future**: If Embase releases an API, this can be automated

## 2. LLM Query Review (10-20 minutes)
**Why**: Requires domain expertise to validate query accuracy

**Manual steps**:
1. Review LLM-generated queries for correctness
2. Check MeSH terms match concepts
3. Verify Boolean logic
4. Test one query per database manually
5. Edit queries if needed before saving

**Future**: Could add automated syntax validation, but semantic review will always need humans

## 3. Gold Standard Creation (15-30 minutes)
**Why**: Requires understanding of which studies were included in final analysis

**Manual steps**:
1. Read published paper
2. Identify included studies
3. Extract PMIDs from each study citation
4. Compile into CSV file

**Future**: If papers include structured supplementary files with PMIDs, this could be partially automated

## 4. Query Generation Command Setup (2-5 minutes)
**Why**: Requires specifying study-specific parameters

**Manual steps**:
1. Choose the strategy-aware relaxation profile (`default`, `recall_soft`, or `recall_strong`)
2. Set date range for literature search
3. Select which databases to target
4. Run command generation tool

**Future**: Could create interactive wizard, but parameter selection will always need human decision

---

# Advanced Tips & Best Practices

## Multi-Key Evaluation Best Practices

### When to Use Multi-Key vs PMID-Only

**Decision Matrix:**

| Scenario | Recommended Method | Reason |
|----------|-------------------|--------|
| PubMed-only queries | PMID-only | All PubMed articles have PMID |
| Multi-database (PubMed + Scopus/WoS) | Multi-key | DOI coverage critical |
| Gold standard has DOI | Multi-key | Accurate cross-database matching |
| Gold standard PMID-only | PMID-only | DOI not available |
| Prototype/testing | PMID-only | Faster, simpler |
| Production evaluation | Multi-key | More accurate recall |

**Check your gold standard DOI coverage:**
```bash
python -c "
import pandas as pd
df = pd.read_csv('studies/<study>/gold_pmids_<study>_detailed.csv')
dois = df['doi'].notna().sum()
total = len(df)
print(f'DOI coverage: {dois}/{total} ({dois/total*100:.1f}%)')
if dois/total > 0.7:
    print('→ Recommend: --multi-key')
else:
    print('→ Recommend: PMID-only')
"
```

### Gold Standard Quality

**Ensure high-quality gold standard:**
```bash
# Automated extraction (recommended)
python scripts/extract_included_studies.py <study> \
  --lookup-pmid \
  --pubmed-email your.email@institution.edu \
  --generate-gold-csv

# This automatically:
# ✓ Extracts PMIDs from full-text references
# ✓ Looks up DOIs from PubMed
# ✓ Validates all identifiers
# ✓ Creates detailed CSV with metadata
```

### Testing Strategy

**Progressive testing approach:**

```bash
# Step 1: Quick PubMed-only test (5 min)
bash scripts/run_complete_workflow.sh <study> --databases pubmed

# Step 2: Add Scopus, use PMID-only baseline (15 min)
bash scripts/run_complete_workflow.sh <study> --databases pubmed,scopus

# Step 3: Enable multi-key for accurate evaluation (20 min)
bash scripts/run_complete_workflow.sh <study> \
  --databases pubmed,scopus,wos \
  --multi-key

# Step 4: Compare results
grep consensus_k2 aggregates_eval/<study>/sets_summary_*.csv
```

---

## Tip 1: Test with PubMed First

```bash
# Before running full workflow, test with PubMed only (fast & free)
bash scripts/run_complete_workflow.sh Godos_2024 --databases pubmed

# If successful, add other databases
bash scripts/run_complete_workflow.sh Godos_2024 --databases pubmed,scopus,wos
```

**Why**: PubMed queries execute faster (free API, no rate limits with API key). Catch file/configuration issues early.

## Tip 2: Version Control Your Study Files

```bash
# Initialize git in study folder
cd studies/Godos_2024
git init
git add queries*.txt gold_pmids*.csv
git commit -m "Initial query setup"

# Track changes to queries
git diff queries.txt  # See what changed

# Restore previous version if needed
git checkout HEAD~1 queries.txt
```

**Why**: Easy to track query iterations, revert mistakes, document changes for reproducibility.

## Tip 3: Validate Queries Manually Before Running

```bash
# Test one PubMed query manually
# 1. Go to: https://pubmed.ncbi.nlm.nih.gov
# 2. Copy first line from queries.txt
# 3. Paste and run search
# 4. Verify results look relevant
# 5. Check result count is reasonable (not 0, not >100,000)
```

**Why**: Catch syntax errors or overly broad/narrow queries before wasting time on full workflow.

## Tip 4: Document Your Decisions

Create a `README.md` in your study folder:

```markdown
# Godos 2024 Study

## Overview
- Topic: Mediterranean diet and cardiovascular health
- Date range: 1990-2023
- Databases: PubMed, Scopus, Web of Science, Embase
- Gold standard: 47 PMIDs from published systematic review

## Query Generation
- LLM: Gemini 1.5 Pro
- Generation mode: Strategy-aware six-query family (`Q1`-`Q6`)
- Date: 2026-01-21
- Command: /run_godos_2024_multidb_strategy

## Workflow Execution
- Date: 2026-01-21
- Command: bash scripts/run_complete_workflow.sh Godos_2024 --databases pubmed,scopus,wos
- Results: precision_gated_union found 100% recall (2789 articles)

## Notes
- Embase export completed on 2026-01-20
- Queries manually reviewed and approved
- No modifications needed to LLM-generated queries
```

**Why**: Future you (or collaborators) will thank you for clear documentation.

## Tip 5: Iterative Query Refinement

If first workflow run has poor recall:

```bash
# 1. Analyze which gold studies were missed
python scripts/analyze_missed_studies.py \
  --gold studies/Godos_2024/gold_pmids_godos_2024.csv \
  --results aggregates/Godos_2024/precision_gated_union.txt

# 2. Review those studies manually to identify missing terms
# 3. Add missing synonyms to queries
# 4. Re-run workflow
bash scripts/run_complete_workflow.sh Godos_2024 --databases pubmed,scopus,wos

# 5. Compare new vs old recall
```

**Why**: Systematic approach to improving query sensitivity.

---

# Frequently Asked Questions

## Q1: How long does the complete workflow take?

**A**: Depends on number of queries and databases:
- **PubMed only**: 5-10 minutes
- **PubMed + Scopus**: 10-15 minutes
- **PubMed + Scopus + WOS**: 15-25 minutes
- **All databases + Embase**: 20-30 minutes

Plus manual time for STEPS 1-5: 45-90 minutes total end-to-end.

## Q2: Can I run the workflow on multiple studies in parallel?

**A**: Yes, but be careful with API rate limits:

```bash
# Terminal 1
bash scripts/run_complete_workflow.sh Study_A --databases pubmed &

# Terminal 2 (wait 2-3 minutes before starting)
bash scripts/run_complete_workflow.sh Study_B --databases pubmed &
```

**Caution**: PubMed allows 10 requests/second with API key. Running too many studies simultaneously may hit rate limits.

## Q3: What if my review doesn't have a PROSPERO protocol?

**A**: Create a markdown file manually with PICOS framework:

```markdown
# Study Protocol: Your Study Name

## Research Question
[Your research question here]

## PICOS Framework

### Population
[Describe target population]

### Intervention/Exposure
[Describe intervention]

### Comparator
[Describe comparator, if applicable]

### Outcomes
[List outcomes of interest]

### Study Design
[List acceptable study designs]

## Keywords
[List key terms and synonyms]

## Date Range
From [start date] to [end date]
```

Save as `studies/YourStudy/prospero_yourstudy.md` and use in STEP 2.

## Q4: Can I use this workflow without institutional database subscriptions?

**A**: Yes! PubMed is free and often sufficient:

```bash
# Run PubMed-only workflow
bash scripts/run_complete_workflow.sh YourStudy --databases pubmed
```

**Note**: You'll miss some articles only indexed in Scopus/WOS/Embase, but for clinical reviews PubMed has good coverage (~80-90%).

## Q5: How do I share my workflow results with collaborators?

**A**: Package the study folder:

```bash
# Create archive
tar -czf Godos_2024_results.tar.gz studies/Godos_2024/ aggregates/Godos_2024/ aggregates_eval/Godos_2024/

# Share via email/cloud storage
# Collaborators can extract and review:
tar -xzf Godos_2024_results.tar.gz
```

Or use git:

```bash
# Push to GitHub repository
cd studies/Godos_2024
git add .
git commit -m "Complete workflow results"
git push origin main
```

## Q6: What if I want more/fewer queries per database?

**A**: The current strategy-aware workflow is fixed to six aligned queries per database (`Q1` to `Q6`). The main knob is now `relaxation_profile`, not query count.

```bash
# Default behavior
/generate_multidb_prompt --relaxation_profile default ...

# Slightly more recall-friendly baseline
/generate_multidb_prompt --relaxation_profile recall_soft ...

# Strongest recall bias within the same six-query family
/generate_multidb_prompt --relaxation_profile recall_strong ...
```

If you truly need a different number of queries, that requires a different template workflow rather than a flag change in the current strategy-aware generator.

## Q7: Can I customize the aggregation strategies?

**A**: Yes! Edit `scripts/aggregate_queries.py` or run custom aggregation:

```bash
# Use only specific queries (e.g., PubMed queries 1,2,4)
python scripts/custom_aggregate.py \
  --queries "pubmed_1,pubmed_2,pubmed_4" \
  --output aggregates/Godos_2024/custom_strategy.txt
```

See [complete_pipeline_guide.md](complete_pipeline_guide.md) Step 7 for details.

---

# STEP 7: Cross-Study Validation (Meta-Analysis)

## Purpose

After completing **multiple systematic reviews** (Steps 1-6 for each), you can perform **cross-study validation** to:
- Compare aggregation strategy performance across different medical domains
- Identify which strategies work universally vs. domain-specific cases
- Generate evidence-based recommendations backed by data from multiple studies
- Create publication-quality visualizations of performance patterns

**When to run this**: After you've completed ≥2 individual systematic reviews in different domains.

**Time investment**: 2-5 minutes total (fully automated).

## Requirements

- ✅ Completed Steps 1-6 for at least 2 different studies
- ✅ Studies have different topics/domains (e.g., nutrition, sleep medicine, AI)
- ✅ Conda environment: `systematic_review_queries`
- ✅ Packages: matplotlib, seaborn (install once: `pip install matplotlib seaborn`)

## Command

```bash
# Activate environment
conda activate systematic_review_queries

# Run complete cross-study analysis
python -m cross_study_validation run
```

## What This Does

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Data Collection from All Studies                   │
├─────────────────────────────────────────────────────────────┤
│ • Scans aggregates_eval/ for all completed studies         │
│ • Extracts strategy performance (recall, precision, F1)     │
│ • Scans benchmark_outputs/ for query performance           │
│ • Extracts gold standard PMIDs from studies/                │
│ • Infers study domain (nutrition, sleep medicine, AI, etc.)│
│ • Validates data against JSON schema                        │
│ • Creates standardized JSON files:                          │
│   - cross_study_validation/data/Godos_2024.json           │
│   - cross_study_validation/data/sleep_apnea.json          │
│   - cross_study_validation/data/ai_2022.json              │
│   - cross_study_validation/data/all_studies.json          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Statistical Analysis                               │
├─────────────────────────────────────────────────────────────┤
│ • Calculates mean ± std for each strategy across studies   │
│ • Identifies strategies with perfect recall (100%)          │
│ • Ranks strategies by recall, precision, F1                 │
│ • Compares retrieval burden (number of articles to screen)  │
│ • Generates evidence-based recommendations                   │
│ • Creates markdown report:                                   │
│   - cross_study_validation/reports/report_<timestamp>.md   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Visualization Generation (6 figures)               │
├─────────────────────────────────────────────────────────────┤
│ 1. Box plots (3 files):                                     │
│    • boxplot_recall.png - Recall distribution by strategy   │
│    • boxplot_precision.png - Precision distribution         │
│    • boxplot_f1.png - F1 score distribution                │
│                                                              │
│ 2. Bar chart (1 file):                                      │
│    • bar_chart_comparison.png - Mean performance with       │
│      error bars (±SD) for all strategies                    │
│                                                              │
│ 3. Scatter plot (1 file):                                   │
│    • scatter_precision_recall.png - Precision vs recall     │
│      tradeoffs for each strategy across all studies         │
│                                                              │
│ 4. Heatmap (1 file):                                        │
│    • heatmap_recall_by_study.png - Performance matrix       │
│      showing recall % by study and strategy                 │
│                                                              │
│ All figures: 300 DPI, publication-ready PNG format          │
│ Saved to: cross_study_validation/reports/figures/           │
└─────────────────────────────────────────────────────────────┘
```

## Expected Output

```
═══════════════════════════════════════════════════════════════
Running complete cross-study validation workflow
═══════════════════════════════════════════════════════════════

Step 1: Collecting study data...
Found 3 studies: Godos_2024, sleep_apnea, ai_2022

════════════════════════════════════════════════════════════
Collecting data for: Godos_2024
════════════════════════════════════════════════════════════
  📊 Parsing aggregation strategies...
  ✓ Parsed 5 strategies from sets_summary_20260122-091122.csv
  
  🔍 Parsing query performance...
  ✓ Parsed 6 queries from summary_20260122-091116.csv
  
  🏆 Extracting gold standard...
  ✓ Extracted 23 valid PMIDs from gold_pmids_Godos_2024.csv
  
  📋 Collecting metadata...
  ✓ Inferred domain 'nutrition' with confidence score 59
    Domain: nutrition
    Databases: ['pubmed', 'scopus', 'wos', 'embase']
    Queries: 12
  
  ✅ Validating against schema...
  ✓ Validation passed
════════════════════════════════════════════════════════════
✓ Successfully collected data for Godos_2024
════════════════════════════════════════════════════════════

[... repeats for sleep_apnea and ai_2022 ...]

✓ Collected 3 studies successfully

✓ Saved to: cross_study_validation/data/Godos_2024.json
✓ Saved to: cross_study_validation/data/sleep_apnea.json
✓ Saved to: cross_study_validation/data/ai_2022.json
✓ Saved combined file: cross_study_validation/data/all_studies.json

✅ Collection complete!

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

✅ Generated 6 visualizations:
   📊 boxplot_recall.png
   📊 boxplot_precision.png
   📊 boxplot_f1.png
   📊 bar_chart_comparison.png
   📊 scatter_precision_recall.png
   📊 heatmap_recall_by_study.png

═══════════════════════════════════════════════════════════════
✅ Complete workflow finished successfully!
═══════════════════════════════════════════════════════════════
```

## Verify Output

```bash
# Check report was created
ls -lh cross_study_validation/reports/report_*.md

# Preview report
head -100 cross_study_validation/reports/report_*.md

# Check visualizations
ls -lh cross_study_validation/reports/figures/

# View visualizations
open cross_study_validation/reports/figures/
```

## Understanding the Report

**Report file**: `cross_study_validation/reports/report_<timestamp>.md`

**Example sections**:

### Executive Summary
```markdown
This report analyzes the performance of **5 aggregation strategies** 
across **3 systematic review studies** covering **48 total gold 
standard articles**.

**Key Finding**: precision_gated_union achieved 100% recall in 2/3 
studies, making it the most reliable strategy across diverse domains.
```

### Study Characteristics
```markdown
| Study ID | Domain | Databases | Gold Size | Queries |
|----------|--------|-----------|-----------|---------|
| Godos_2024 | nutrition | pubmed,scopus,wos,embase | 23 | 12 |
| ai_2022 | AI | pubmed,scopus,wos,embase | 14 | 12 |
| sleep_apnea | sleep med | pubmed,scopus,wos,embase | 11 | 12 |

**Total Gold Standard Articles**: 48
```

### Strategy Performance Summary
```markdown
| Strategy | Mean Recall | Mean Precision | Mean Retrieved | Perfect Recall |
|----------|-------------|----------------|----------------|----------------|
| precision_gated_union | 78.6% ± 37.1% | 0.0052 ± 0.0041 | 9283 ± 13916 | 2/3 |
| weighted_vote | 78.6% ± 37.1% | 0.0052 ± 0.0041 | 9283 ± 13916 | 2/3 |
| consensus_k2 | 50.0% ± 32.3% | 0.0186 ± 0.0203 | 1966 ± 2928 | 0/3 |
```

**What this tells you**:
- `precision_gated_union` achieved 100% recall in 2 out of 3 studies
- Mean recall of 78.6% across all studies
- High standard deviation (±37.1%) indicates domain variability
- `consensus_k2` has lower recall but much smaller screening burden

### Recommended Strategy
```markdown
### precision_gated_union

**Justification**: 
- Achieved 100% recall in 2 out of 3 studies
- Highest mean recall (78.6%) across all domains
- Consistent performance in nutrition and AI domains
- Manageable screening burden (~9,283 articles)

**Performance by Study**:
- Godos_2024 (nutrition): 100% recall, 23/23 articles found
- ai_2022 (AI): 100% recall, 14/14 articles found
- sleep_apnea (sleep med): 36.4% recall, 4/11 articles found
```

## Understanding the Visualizations

### Box Plots (3 files)

**Files**: `boxplot_recall.png`, `boxplot_precision.png`, `boxplot_f1.png`

**Shows**: Distribution of performance metrics across studies for each strategy

**How to interpret**:
- **Box height**: Interquartile range (50% of data)
- **Line in box**: Median value
- **Whiskers**: Min and max values
- **Individual dots**: Actual study datapoints
- **Wide boxes**: High variability across studies (domain-dependent)
- **Narrow boxes**: Consistent performance (universal strategy)

**Example insights**:
- If `precision_gated_union` box is high with narrow spread → reliable across domains
- If `consensus_k2` box has large whiskers → performance varies by domain

### Bar Chart (1 file)

**File**: `bar_chart_comparison.png`

**Shows**: Mean performance ± standard deviation for all strategies across 3 panels (Recall, Precision, F1)

**How to interpret**:
- **Bar height**: Mean performance across all studies
- **Error bars**: ±1 standard deviation
- **Long error bars**: Inconsistent performance across studies
- **Short error bars**: Reliable, consistent strategy

**Example insights**:
- Tallest bar in Recall panel = best strategy for comprehensive reviews
- Smallest error bars = most reliable strategy

### Scatter Plot (1 file)

**File**: `scatter_precision_recall.png`

**Shows**: Precision vs. recall tradeoffs for each strategy across all studies

**How to interpret**:
- **Top-right corner**: Ideal (high precision + high recall)
- **Top-left**: High recall, low precision (comprehensive but many irrelevant)
- **Bottom-right**: High precision, low recall (few but highly relevant)
- **Color**: Different strategies

**Example insights**:
- Cluster of points in top-left → all strategies prioritize recall over precision
- Scattered points → different strategies make different tradeoffs

### Heatmap (1 file)

**File**: `heatmap_recall_by_study.png`

**Shows**: Performance matrix with studies as rows, strategies as columns, recall as color

**How to interpret**:
- **Green cells**: High recall (80-100%)
- **Yellow cells**: Moderate recall (40-80%)
- **Red cells**: Low recall (<40%)
- **Green columns**: Strategies that work well across all studies
- **Mixed columns**: Domain-specific strategies

**Example insights**:
- Full green column for `precision_gated_union` → works in all domains
- Red cell in sleep_apnea row → strategy failed in that domain

## Advanced Usage

### Collect data only (no analysis)
```bash
python -m cross_study_validation collect --all
```

### Generate report only (after data collection)
```bash
python -m cross_study_validation analyze
```

### Generate visualizations only
```bash
python -m cross_study_validation visualize
```

### Collect single study
```bash
python -m cross_study_validation collect --study Godos_2024
```

### Custom output location
```bash
python -m cross_study_validation analyze --output my_report.md
python -m cross_study_validation visualize --output ./my_figures/
```

### Verbose logging
```bash
python -m cross_study_validation run --verbose
```

## Adding New Studies

When you complete a new systematic review:

**Step 1**: Complete Steps 1-6 for the new study
```bash
bash scripts/run_complete_workflow.sh new_study --databases pubmed,scopus,wos
```

**Step 2**: Re-run cross-study validation (automatically includes new study)
```bash
python -m cross_study_validation run
```

**Step 3**: Compare with previous reports
```bash
# The new report includes all studies (old + new)
cat cross_study_validation/reports/report_*.md | head -100
```

## Troubleshooting

### Problem: "No studies found"
```bash
# Check that you have completed studies
ls aggregates_eval/*/sets_summary_*.csv
ls benchmark_outputs/*/summary_*.csv
ls studies/*/gold_pmids_*.csv

# Solution: Complete Steps 1-6 for at least 2 studies first
```

### Problem: "Validation failed"
```bash
# Check data format
cat cross_study_validation/schemas/study_result_schema.json

# Common issues:
# - Missing CSV columns
# - Invalid PMID format
# - Empty CSV files

# Solution: Re-run the study workflow
bash scripts/run_complete_workflow.sh STUDY --databases pubmed,scopus,wos
```

### Problem: "Visualization generation failed"
```bash
# Install required packages
pip install matplotlib seaborn

# Re-run visualization step
python -m cross_study_validation visualize
```

### Problem: "ModuleNotFoundError: No module named 'jsonschema'"
```bash
# Install jsonschema
pip install jsonschema

# Re-run
python -m cross_study_validation run
```

## Use Cases for Your Paper

**Methods Section**:
```
We selected the precision_gated_union aggregation strategy based on 
cross-study validation showing 100% recall in 2 out of 3 diverse 
systematic reviews (nutrition: 23/23, AI: 14/14, sleep medicine: 4/11).
```

**Results Section**:
```
Our selected strategy retrieved 1,704 articles with 100% recall 
(23/23 gold standard articles found), consistent with its mean 
performance across studies (78.6% ± 37.1%).
```

**Figures**:
- Include `heatmap_recall_by_study.png` as supplementary material
- Include `bar_chart_comparison.png` to justify strategy selection

---

# Summary: Your Complete Workflow

## You've Learned How To:

✅ **STEP 1**: Convert raw PDF files to markdown for LLM processing  
✅ **STEP 2**: Generate executable LLM commands for multi-database query creation  
✅ **STEP 3**: Run LLM to automatically generate 24 database-specific queries  
✅ **STEP 4**: Export Embase results manually (the only unavoidable manual step)  
✅ **STEP 5**: Create gold standard PMID list from published review  
✅ **STEP 6**: Execute complete workflow in ONE command: query → deduplicate → score → aggregate → evaluate  
✅ **STEP 7** (Optional): Perform cross-study meta-analysis to compare strategy performance across domains  

## The Key Innovation

**Before**: Study-specific scripts requiring manual editing for each new systematic review

**Now**: Universal workflow accepting study name as parameter, working for ANY study automatically

```bash
# Works for ANY study, no editing needed:
bash scripts/run_complete_workflow.sh sleep_apnea --databases pubmed,scopus,wos
bash scripts/run_complete_workflow.sh ai_2022 --databases pubmed,scopus,wos
bash scripts/run_complete_workflow.sh Godos_2024 --databases pubmed,scopus,wos
bash scripts/run_complete_workflow.sh YOUR_STUDY --databases pubmed,scopus,wos
```

## Time Investment Summary

| Phase | Time | Type |
|-------|------|------|
| **One-time setup** | 15 minutes | Once ever |
| **Per study preparation** | 45-90 minutes | Per study |
| **Automated execution** | 15-25 minutes | Per study |
| **Total per study** | 60-115 minutes | 80% automated |

## Final Result

You now have:
- ✅ Complete query performance metrics for each database
- ✅ Deduplicated result sets across all databases  
- ✅ 5 aggregation strategies tested and scored
- ✅ Recommendation for which strategy found 100% of gold studies
- ✅ PMID list ready for import into screening tools
- ✅ Reproducible workflow for future systematic reviews
- ✅ (Optional) Cross-study validation reports and visualizations

## Next Steps

1. **Import PMIDs** from chosen aggregation strategy into Covidence/Rayyan
2. **Begin title/abstract screening** (knowing you have 100% recall)
3. **Document your workflow** in your systematic review protocol
4. **Complete more studies** and run STEP 7 for cross-study insights
5. **Share this guide** with collaborators for their systematic reviews

---

# Need More Help?

## Additional Resources

- **Technical Reference**: [complete_pipeline_guide.md](complete_pipeline_guide.md) - Comprehensive 1000+ line technical guide with every detail
- **Multi-Database Deduplication**: [multi_database_deduplication_complete.md](multi_database_deduplication_complete.md)
- **Precision Knobs**: [precision_knobs_critical_analysis.md](precision_knobs_critical_analysis.md)
- **API Configuration**: [api_configuration_and_embase_import.md](api_configuration_and_embase_import.md)

## Common Issues & Solutions

Most issues are covered in troubleshooting sections within each STEP above. If stuck:

1. Check error message carefully
2. Review troubleshooting section for that STEP
3. Verify file names match required patterns (case-sensitive!)
4. Ensure conda environment is activated
5. Check API keys in `.env` file

## Support

For bugs or feature requests:
- Open an issue on GitHub: [github.com/ranibasna/QueriesSystematicReview](https://github.com/ranibasna/QueriesSystematicReview)

---

**Congratulations!** You now have a complete, automated, end-to-end systematic review workflow from raw PDFs to final screening lists. 🎉

```bash
# Show full help and options
bash scripts/run_complete_workflow.sh --help

# Test with PubMed only (fast)
bash scripts/run_complete_workflow.sh ai_2022 --databases pubmed

# Check study structure
tree studies/ai_2022/
```
