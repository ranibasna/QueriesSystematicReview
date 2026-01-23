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
│  └── /run_<study>_multidb_extended                          │
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
│  ├── benchmark_outputs/      (Query performance)           │
│  ├── aggregates/             (Combined strategies)         │
│  └── aggregates_eval/        (Strategy performance)        │
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
└── pmids_multiple_sources/          # Empty folder (you'll populate before workflow)
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
├── gold_pmids_godos_2024.csv        # ← Created in STEP 5
├── embase_manual_queries/           # ← Populated in STEP 4
│   ├── embase_query1.csv
│   ├── embase_query2.csv
│   ├── embase_query3.csv
│   ├── embase_query4.csv
│   ├── embase_query5.csv
│   └── embase_query6.csv
├── benchmark_outputs/               # ← Generated in STEP 6
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
Create an executable LLM command that will generate database-specific search queries from your PROSPERO protocol.

## Requirements
- ✅ Markdown files from STEP 1 completed
- ✅ LLM tool installed (Gemini CLI, Claude Desktop, etc.)

## Command

```bash
/generate_multidb_prompt \
  --command_name run_godos_2024_multidb_extended \
  --protocol_path studies/Godos_2024/prospero_godos_2024.md \
  --databases pubmed,scopus,wos,embase \
  --level extended \
  --min_date "1990/01/01" \
  --max_date "2023/12/31"
```

## Parameter Explanations

| Parameter | Description | Your Value | Notes |
|-----------|-------------|------------|-------|
| `--command_name` | Name for the LLM command you're creating | `run_godos_2024_multidb_extended` | Becomes `/<command_name>` |
| `--protocol_path` | Path to PROSPERO markdown from STEP 1 | `studies/Godos_2024/prospero_godos_2024.md` | Use PROSPERO, not Paper |
| `--databases` | Which databases to generate queries for | `pubmed,scopus,wos,embase` | **No spaces!** |
| `--level` | Query complexity (basic/extended/keywords/exhaustive) | `extended` | **Recommended**: 6 queries/DB |
| `--min_date` | Start of literature search date range | `1990/01/01` | YYYY/MM/DD format |
| `--max_date` | End of literature search date range | `2023/12/31` | Match your review |

**Level Options:**

| Level | Queries/DB | Description | Recommended For |
|-------|------------|-------------|-----------------|
| `basic` | 3 | High-recall, Balanced, High-precision | Quick tests |
| `extended` | 6 | Basic 3 + 3 micro-variants (Filter/Scope/Proximity) | **Most studies ← Use this** |
| `keywords` | 4 | Keyword-focused variations | Explicit keyword lists in protocol |
| `exhaustive` | 9 | All variants + exploration queries | Comprehensive reviews |

## What This Does

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Read Template Files                                 │
├─────────────────────────────────────────────────────────────┤
│ ✓ prompts/prompt_template_multidb.md                       │
│ ✓ prompts/database_guidelines.md                           │
│ ✓ studies/Godos_2024/prospero_godos_2024.md               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Extract Protocol Information                        │
├─────────────────────────────────────────────────────────────┤
│ From PROSPERO markdown, extract:                            │
│ • Research question / topic                                 │
│ • Population (P in PICOS)                                   │
│ • Intervention/Exposure (I)                                 │
│ • Comparator (C)                                            │
│ • Outcomes (O)                                              │
│ • Study designs (S)                                         │
│ • Keywords                                                  │
│ • Date range                                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Extract Database Guidelines                         │
├─────────────────────────────────────────────────────────────┤
│ For each database (pubmed, scopus, wos, embase):           │
│ • Syntax rules ([MeSH], TITLE-ABS-KEY, etc.)              │
│ • Precision_Knobs (filters, scope, proximity)              │
│ • Boolean operators (AND, OR, NOT)                         │
│ • Field tags ([tiab], [majr], etc.)                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Build Complete Prompt                               │
├─────────────────────────────────────────────────────────────┤
│ • Insert protocol info into template placeholders          │
│ • Insert database guidelines for selected DBs               │
│ • Insert level-specific instructions (extended = 6 queries)│
│ • Add date range constraints                                │
│ • Add output format specifications                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Write Executable Command File                       │
├─────────────────────────────────────────────────────────────┤
│ Save to: .gemini/commands/run_godos_2024_multidb_extended.toml │
│                                                              │
│ File contains:                                              │
│ • description = "Runs query generation for Godos_2024..."  │
│ • prompt = '''[FULL POPULATED PROMPT]'''                   │
│                                                              │
│ Ready to invoke via: /run_godos_2024_multidb_extended      │
└─────────────────────────────────────────────────────────────┘
```

## Expected Output

```
═══════════════════════════════════════════════════════════════
  🔧 LLM Command Generation
═══════════════════════════════════════════════════════════════

Reading template files...
  ✓ prompts/prompt_template_multidb.md
  ✓ prompts/database_guidelines.md

Reading protocol...
  ✓ studies/Godos_2024/prospero_godos_2024.md

Extracting protocol information...
  ✓ Topic: "Mediterranean Diet and Cardiovascular Health"
  ✓ Population: Adults aged 18+
  ✓ Intervention: Mediterranean diet adherence
  ✓ Outcomes: CVD incidence, mortality
  ✓ Designs: Cohort studies, RCTs

Extracting database guidelines...
  ✓ PubMed syntax & Precision_Knobs
  ✓ Scopus syntax & Precision_Knobs
  ✓ Web of Science syntax & Precision_Knobs
  ✓ Embase syntax & Precision_Knobs

Building prompt with level: extended (6 queries per database)...
  ✓ Injected PICOS framework
  ✓ Injected database-specific guidelines
  ✓ Injected extended-level instructions
  ✓ Added date range: 1990/01/01 to 2023/12/31

Writing command file...
  ✓ Saved to: .gemini/commands/run_godos_2024_multidb_extended.toml

✅ Command generation complete!

═══════════════════════════════════════════════════════════════

The new command is ready to execute:

  /run_godos_2024_multidb_extended

This command will generate:
  • 6 queries for PubMed
  • 6 queries for Scopus
  • 6 queries for Web of Science
  • 6 queries for Embase
  ────────────────────────
  Total: 24 queries

Next step: Run the command to execute the LLM prompt!
```

## Verify Output

```bash
# Check command file was created
ls -lh .gemini/commands/run_godos_2024_multidb_extended.toml

# Preview the file (first 100 lines)
head -100 .gemini/commands/run_godos_2024_multidb_extended.toml
```

## Troubleshooting

**Problem: "Protocol file not found"**
```bash
# Check STEP 1 completed successfully
ls studies/Godos_2024/prospero_*.md

# If missing, re-run STEP 1
```

**Problem: "Template files not found"**
```bash
# Check you're in project root
pwd  # Should end with QueriesSystematicReview

# Check template files exist
ls prompts/prompt_template_multidb.md
ls prompts/database_guidelines.md
```

**Problem: "Invalid database name"**
```bash
# Valid options: pubmed, scopus, wos, embase
# NO SPACES! ❌ "pubmed, scopus" ✅ "pubmed,scopus"

# Correct usage:
/generate_multidb_prompt \
  --databases pubmed,scopus,wos,embase \
  ...
```

---

# STEP 3: Run LLM Command to Generate Queries

## Purpose
Execute the LLM command from STEP 2 to automatically generate 24 database-specific search queries (6 for each of PubMed, Scopus, WOS, Embase).

## Requirements
- ✅ Command file from STEP 2 completed
- ✅ LLM access (Gemini CLI / Claude Desktop / GPT-4)

## Command

```bash
/run_godos_2024_multidb_extended
```

## What This Does

The LLM will:

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Analyze PROSPERO Protocol                          │
├─────────────────────────────────────────────────────────────┤
│ • Read research question                                    │
│ • Extract PICOS framework elements                          │
│ • Identify key concepts (e.g., "Mediterranean diet", "CVD")│
│ • Note study design requirements                            │
│ • Note date range constraints                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Create Concept-to-Term Mapping Tables              │
├─────────────────────────────────────────────────────────────┤
│ Concept→MeSH/Emtree Mapping:                               │
│ ┌──────────────┬─────────────────┬─────────┬─────────┐    │
│ │ Concept      │ MeSH Term       │ Tree    │ Explode │    │
│ ├──────────────┼─────────────────┼─────────┼─────────┤    │
│ │ Med. Diet    │ Diet, Mediter.  │ E02.642 │ Yes     │    │
│ │ CVD          │ Card. Diseases  │ C14     │ Yes     │    │
│ └──────────────┴─────────────────┴─────────┴─────────┘    │
│                                                              │
│ Concept→Textword Mapping:                                  │
│ ┌──────────────┬──────────────────┬───────┬──────────┐    │
│ │ Concept      │ Synonym/Phrase   │ Field │ Truncat? │    │
│ ├──────────────┼──────────────────┼───────┼──────────┤    │
│ │ Med. Diet    │ mediterranean*   │ tiab  │ Yes      │    │
│ │ Med. Diet    │ med diet         │ tiab  │ No       │    │
│ │ CVD          │ cardiovascular*  │ tiab  │ Yes      │    │
│ │ CVD          │ heart disease*   │ tiab  │ Yes      │    │
│ └──────────────┴──────────────────┴───────┴──────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Generate 6 Queries for Each Database               │
├─────────────────────────────────────────────────────────────┤
│ FOR EACH DATABASE (PubMed, Scopus, WOS, Embase):           │
│                                                              │
│ Query 1 - High-recall:                                      │
│ • Use exploded MeSH/Emtree terms                           │
│ • Include all text synonyms with OR                         │
│ • Broad Boolean logic (maximize sensitivity)                │
│                                                              │
│ Query 2 - Balanced:                                         │
│ • Mix of controlled vocab + free text                       │
│ • Add study design filters                                  │
│ • Moderate precision                                        │
│                                                              │
│ Query 3 - High-precision:                                   │
│ • Major focus terms only ([majr], */de)                    │
│ • Title-only searches                                       │
│ • Strict filters                                            │
│                                                              │
│ Query 4 - Micro-variant (Filter-based):                    │
│ • Start with Balanced query                                 │
│ • Add: humans[Filter] (PubMed)                             │
│ • Add: DOCTYPE(ar OR re) (Scopus)                          │
│ • Add: article or review (Embase)                          │
│                                                              │
│ Query 5 - Micro-variant (Scope-based):                     │
│ • Start with Balanced query                                 │
│ • Restrict key concepts to title: [ti]                     │
│ • Or use major headings: [majr]                            │
│                                                              │
│ Query 6 - Micro-variant (Proximity-based):                 │
│ • Start with Balanced query                                 │
│ • Add: W/5 for Scopus (within 5 words)                    │
│ • Add: ADJ5 for Embase                                     │
│ • For PubMed: use [majr] (no proximity operator)          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Apply Database-Specific Syntax                     │
├─────────────────────────────────────────────────────────────┤
│ PubMed Example:                                             │
│ ("Diet, Mediterranean"[MeSH] OR mediterranean diet[tiab])   │
│ AND ("Cardiovascular Diseases"[MeSH] OR cardiovascular[tiab│
│ AND ("1990/01/01"[Date - Publication] : "2023/12/31"[Date])│
│                                                              │
│ Scopus Example:                                             │
│ TITLE-ABS-KEY("mediterranean diet" OR "med diet") AND      │
│ TITLE-ABS-KEY(cardiovascular OR "heart disease") AND       │
│ PUBYEAR > 1989 AND PUBYEAR < 2024                          │
│                                                              │
│ [Similar for WOS and Embase]                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Self-Check with PRESS Criteria                     │
├─────────────────────────────────────────────────────────────┤
│ LLM reviews its own work:                                   │
│ • Are MeSH terms correct and appropriately exploded?        │
│ • Are synonyms comprehensive?                               │
│ • Is Boolean logic correct?                                 │
│ • Are date filters applied correctly?                       │
│ • Are queries syntactically valid?                          │
│                                                              │
│ If issues found: Apply corrections via json_patch           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 6: Output JSON with All Queries                       │
├─────────────────────────────────────────────────────────────┤
│ Returns:                                                    │
│ {                                                            │
│   "pubmed": ["query1", "query2", ..., "query6"],          │
│   "scopus": ["query1", "query2", ..., "query6"],          │
│   "wos": ["query1", "query2", ..., "query6"],             │
│   "embase": ["query1", "query2", ..., "query6"]           │
│ }                                                            │
└─────────────────────────────────────────────────────────────┘
```

## Expected Output

The LLM will return a JSON object with all queries. You'll see:

```json
{
  "pubmed": [
    "(\"Diet, Mediterranean\"[MeSH] OR \"mediterranean diet\"[tiab] OR \"med diet\"[tiab]) AND (\"Cardiovascular Diseases\"[MeSH] OR cardiovascular[tiab] OR \"heart disease\"[tiab]) AND (\"Cohort Studies\"[MeSH] OR cohort[tiab]) AND (\"1990/01/01\"[Date - Publication] : \"2023/12/31\"[Date - Publication])",
    
    "(\"Diet, Mediterranean\"[MeSH] OR mediterranean[tiab]) AND (\"Cardiovascular Diseases\"[MeSH] OR cvd[tiab]) AND (\"1990/01/01\"[Date - Publication] : \"2023/12/31\"[Date - Publication])",
    
    "\"Diet, Mediterranean\"[Majr] AND \"Cardiovascular Diseases\"[Majr] AND (\"1990/01/01\"[Date - Publication] : \"2023/12/31\"[Date - Publication])",
    
    "(\"Diet, Mediterranean\"[MeSH] OR mediterranean[tiab]) AND (\"Cardiovascular Diseases\"[MeSH] OR cvd[tiab]) AND humans[Filter] AND (\"1990/01/01\"[Date - Publication] : \"2023/12/31\"[Date - Publication])",
    
    "\"Diet, Mediterranean\"[Majr] AND cardiovascular[ti] AND (\"1990/01/01\"[Date - Publication] : \"2023/12/31\"[Date - Publication])",
    
    "\"Diet, Mediterranean\"[Majr] AND \"Cardiovascular Diseases\"[Majr] AND english[Language] AND (\"1990/01/01\"[Date - Publication] : \"2023/12/31\"[Date - Publication])"
  ],
  
  "scopus": [
    "TITLE-ABS-KEY((\"mediterranean diet\" OR \"med diet\" OR mediterranean)) AND TITLE-ABS-KEY((cardiovascular OR \"heart disease\" OR cvd)) AND TITLE-ABS-KEY(cohort) AND PUBYEAR > 1989 AND PUBYEAR < 2024",
    
    "TITLE-ABS-KEY(mediterranean AND diet) AND TITLE-ABS-KEY(cardiovascular) AND PUBYEAR > 1989 AND PUBYEAR < 2024",
    
    "TITLE(mediterranean AND diet) AND TITLE(cardiovascular) AND PUBYEAR > 1989 AND PUBYEAR < 2024",
    
    "TITLE-ABS-KEY(mediterranean AND diet) AND TITLE-ABS-KEY(cardiovascular) AND DOCTYPE(ar OR re) AND PUBYEAR > 1989 AND PUBYEAR < 2024",
    
    "TITLE(mediterranean AND diet) AND TITLE-ABS-KEY(cardiovascular) AND PUBYEAR > 1989 AND PUBYEAR < 2024",
    
    "TITLE-ABS-KEY(mediterranean W/5 diet) AND TITLE-ABS-KEY(cardiovascular) AND PUBYEAR > 1989 AND PUBYEAR < 2024"
  ],
  
  "wos": [
    "...",  
  ],
  
  "embase": [
    "..."
  ]
}
```

## Save Queries to Files

**IMPORTANT**: You must manually copy each array of queries to the corresponding file:

```bash
# 1. Copy pubmed queries to studies/Godos_2024/queries.txt
#    One query per line (6 lines total)

# 2. Copy scopus queries to studies/Godos_2024/queries_scopus.txt
#    One query per line (6 lines total)

# 3. Copy wos queries to studies/Godos_2024/queries_wos.txt
#    One query per line (6 lines total)

# 4. Copy embase queries to studies/Godos_2024/queries_embase.txt
#    One query per line (6 lines total)
```

**Format Example** (`queries.txt`):
```
("Diet, Mediterranean"[MeSH] OR "mediterranean diet"[tiab]) AND ("Cardiovascular Diseases"[MeSH] OR cardiovascular[tiab]) AND ("1990/01/01"[Date - Publication] : "2023/12/31"[Date - Publication])
("Diet, Mediterranean"[MeSH] OR mediterranean[tiab]) AND (cvd[tiab]) AND ("1990/01/01"[Date - Publication] : "2023/12/31"[Date - Publication])
"Diet, Mediterranean"[Majr] AND "Cardiovascular Diseases"[Majr] AND ("1990/01/01"[Date - Publication] : "2023/12/31"[Date - Publication])
...
```

## Verify Output

```bash
# Check all query files were created
ls studies/Godos_2024/queries*.txt

# Count lines (should be 6 for each)
wc -l studies/Godos_2024/queries*.txt

# Expected output:
#   6 studies/Godos_2024/queries.txt
#   6 studies/Godos_2024/queries_scopus.txt
#   6 studies/Godos_2024/queries_wos.txt
#   6 studies/Godos_2024/queries_embase.txt
```

## Troubleshooting

**Problem: "LLM returned incomplete JSON"**
```bash
# Re-run the command
/run_godos_2024_multidb_extended

# Or try with a different level
/generate_multidb_prompt \
  --level basic \  # Start with simpler (3 queries per DB)
  ...
```

**Problem: "Queries don't match my protocol"**
```bash
# Review your PROSPERO markdown
cat studies/Godos_2024/prospero_godos_2024.md

# If PICOS unclear, manually edit the markdown to add clarity
# Then re-run STEP 2 and STEP 3
```

**Problem: "How do I review queries before saving?"**
```markdown
**Best Practice**: Manually review all queries for:
1. Correct MeSH/Emtree terms (check against PubMed MeSH browser)
2. Complete synonym lists (add missing variants)
3. Correct Boolean logic (AND/OR precedence)
4. Date range accuracy
5. Syntax validity (test one query manually on each database)

Make edits directly in the .txt files before proceeding to STEP 4.
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

# STEP 5: Create Gold Standard PMID List Using LLM-Based Extraction and Validation

## Purpose
Create a validated CSV file containing the PMIDs (PubMed IDs) of all studies that were included in the final systematic review. This uses **LLM agents to extract PMIDs** from your paper, followed by **automated validation** against PubMed to ensure accuracy.

## Requirements
- ✅ Published paper markdown from STEP 1 (`paper_<study>.md`)
- ✅ Access to multiple LLM agents (ChatGPT, Claude, Gemini, or Sciespace)
- ✅ Python environment with Biopython (`systematic_review_queries`)

## ⚠️ Important: Working Directory
**All commands in STEP 5 must be run from the project root directory:**
```bash
# Navigate to project root (if not already there)
cd to QueriesSystematicReview

# Verify you're in the right place
pwd
# Should output: .../QueriesSystematicReview
```

**Do NOT run from:**
- ❌ `studies/Godos_2024/` (study folder)
- ❌ `studies/Godos_2024/pmids_multiple_sources/` (sources folder)

The validation scripts automatically find CSV files in `studies/<study_name>/pmids_multiple_sources/` when you provide the study name as an argument.

## What is a Gold Standard?

Your gold standard is the list of **studies that were actually included** in your systematic review after full-text screening. These are typically found in:
- Table 1 (Study characteristics)
- Supplementary materials (Included studies list)
- References section (only the included studies, not all references)

**Example**: If your review included 47 studies after screening 2,356 articles, your gold standard will have 47 PMIDs.

## The Complete Workflow: LLM Extraction + Automated Validation

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

---

## Step 5.1: Prepare Study Folder

```bash
# Create folder for multiple LLM sources
mkdir -p studies/Godos_2024/pmids_multiple_sources
```

---

## Step 5.2: Extract PMIDs Using Multiple LLM Agents

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

## Step 5.3: Validate PMIDs Across Sources

Now use the automated validation script to cross-check the LLM outputs against PubMed:

```bash
# IMPORTANT: Run from project root directory
cd to QueriesSystematicReview

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

## Step 5.4: Review and Verify Output

### Check the Generated Gold File

```bash
# From project root:
cd to QueriesSystematicReview

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
cd to QueriesSystematicReview

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
cd to QueriesSystematicReview

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
cd to QueriesSystematicReview
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

## The Universal Command

```bash
bash scripts/run_complete_workflow.sh Godos_2024 --databases pubmed,scopus,wos
```

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
# Run with default databases (PubMed only)
bash scripts/run_complete_workflow.sh Godos_2024

# Specify multiple databases
bash scripts/run_complete_workflow.sh Godos_2024 --databases pubmed,scopus,wos

# Include Embase (auto-detects CSV files)
bash scripts/run_complete_workflow.sh Godos_2024 --databases pubmed,scopus,wos,embase
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
| `--databases` | Select which databases to query | Customizing database selection |
| `--skip-embase` | Ignore Embase CSV files | Testing without Embase |
| `--embase-only` | Only import Embase, skip APIs | Already ran API queries |
| `--skip-aggregation` | Skip aggregation phase | Only want individual query performance |
| `--help` | Show usage information | Learning command options |

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
- [ ] Ran: `/generate_multidb_prompt` with correct parameters
- [ ] Command file created in `.gemini/commands/`
- [ ] Verified command name is correct

### STEP 3: Query Generation
- [ ] Ran: `/<command_name>` (LLM command from STEP 2)
- [ ] Received JSON output with queries for all databases
- [ ] Copied PubMed queries to `queries.txt` (one per line)
- [ ] Copied Scopus queries to `queries_scopus.txt` (one per line)
- [ ] Copied WOS queries to `queries_wos.txt` (one per line)
- [ ] Copied Embase queries to `queries_embase.txt` (one per line)
- [ ] Verified: Each file has 6 lines (for extended level)
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
/generate_multidb_prompt --command_name run_godos_2024_multidb_extended ...

# 3. Run LLM
/run_godos_2024_multidb_extended
# → Copy output to queries*.txt files

# 4. Export Embase (manual, but streamlined)
# Save CSVs to embase_manual_queries/

# 5. Create gold standard
# Create gold_pmids_godos_2024.csv

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
1. Choose query complexity level (basic/extended/keywords/exhaustive)
2. Set date range for literature search
3. Select which databases to target
4. Run command generation tool

**Future**: Could create interactive wizard, but parameter selection will always need human decision

---

# Advanced Tips & Best Practices

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
- Level: Extended (6 queries per database)
- Date: 2026-01-21
- Command: /run_godos_2024_multidb_extended_v2

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

**A**: Change the `--level` parameter in STEP 2:

```bash
# 3 queries per database (faster, less comprehensive)
/generate_multidb_prompt --level basic ...

# 6 queries per database (recommended balance)
/generate_multidb_prompt --level extended ...

# 9 queries per database (most comprehensive)
/generate_multidb_prompt --level exhaustive ...
```

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
