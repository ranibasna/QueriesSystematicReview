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
│  • Precision, Recall, F1-score                              │
│  • Set-level performance metrics                             │
│  • Gold standard validation                                  │
└─────────────────────────────────────────────────────────────┘
```

### Key Concepts

**DOI-Based Deduplication**: ~96% of modern articles have DOIs. The system uses DOIs as the primary key for identifying duplicate articles across databases.

**Query Precision Levels**:
- **High-recall**: Broad terms, maximizes sensitivity (finds all relevant articles + many irrelevant)
- **Balanced**: Mix of controlled vocabulary and free text with filters
- **High-precision**: Focused terms, maximizes specificity (finds fewer but more relevant articles)

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
git clone https://github.com/yourusername/QueriesSystematicReview.git
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

# Multi-database configuration (no spaces after commas!)
SR_DATABASES=pubmed,scopus

# Skip date filters for Scopus (recommended due to API limitations)
SCOPUS_SKIP_DATE_FILTER=true
```

**Important**: No spaces around commas in `SR_DATABASES`! Incorrect: `pubmed, scopus` ❌ Correct: `pubmed,scopus` ✅

**Flag Explanations**:
- `NCBI_EMAIL`: Required by NCBI to contact you if there are issues
- `NCBI_API_KEY`: Optional, increases rate limit from 3 to 10 requests/second
- `SCOPUS_INSTTOKEN`: Optional, institution-specific token for enhanced access
- `SCOPUS_SKIP_DATE_FILTER`: Recommended `true` - Scopus API date filtering has known issues
- `SR_DATABASES`: Default databases to use (can be overridden via command line)

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
    ├── queries_wos.txt                   # Web of Science queries (5-6 queries)
    ├── queries_embase.txt                # Embase queries (5-6 queries)
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

This step uses a Large Language Model (LLM) to automatically generate database-specific search queries from a PROSPERO protocol or study description. Instead of manually writing queries for each database, the LLM acts as an expert information specialist, translating your research question into optimized queries for PubMed, Scopus, Web of Science, and Embase.

**What You'll Learn:**
- How the command generation system works
- Creating executable prompts from templates
- Running LLM-powered query generation
- Understanding the integration between templates, guidelines, and protocols

### Architecture: Command Generation System

```
┌───────────────────────────────────────────────────────────────┐
│                    INPUT LAYER                                 │
│  ┌──────────────────┐  ┌──────────────────┐                  │
│  │ PROSPERO Protocol│  │ Study Guidelines │                  │
│  │ (study-specific) │  │ (study-specific) │                  │
│  └──────────────────┘  └──────────────────┘                  │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│                  TEMPLATE LAYER                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  prompt_template_multidb.md                            │  │
│  │  • Contains 4 levels: basic, extended, keywords,       │  │
│  │    exhaustive                                           │  │
│  │  • Has [PLACEHOLDERS] for injection                    │  │
│  │  • Includes Precision_Knobs Framework                  │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│                  GUIDELINES LAYER                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  database_guidelines.md                                │  │
│  │  • PubMed syntax & Precision_Knobs                     │  │
│  │  • Scopus syntax & Precision_Knobs                     │  │
│  │  • Embase syntax & Precision_Knobs                     │  │
│  │  • Web of Science syntax & Precision_Knobs             │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│               ORCHESTRATION LAYER                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  generate_multidb_prompt.toml                          │  │
│  │  • Reads template + guidelines + protocol             │  │
│  │  • Extracts level-specific instructions               │  │
│  │  • Injects database guidelines for selected DBs       │  │
│  │  • Populates all placeholders                          │  │
│  │  • Writes executable command file                      │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│                  OUTPUT LAYER                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  run_<study>_multidb_<level>.toml                      │  │
│  │  • Complete, ready-to-execute command                  │  │
│  │  • Contains full populated prompt                      │  │
│  │  • Invoked via: /run_<study>_multidb_<level>          │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│                  EXECUTION LAYER                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  LLM (Claude, GPT, Gemini)                             │  │
│  │  • Reads prompt with protocol + guidelines             │  │
│  │  • Generates queries for each database                 │  │
│  │  • Returns JSON with paste-ready queries               │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

---

### Step 2.1: Prepare Study Materials

Before generating queries, you need:

1. **PROSPERO protocol** (or study description)
2. **Study-specific guidelines** (optional but recommended)
3. **General systematic review guidelines** (optional)

#### Example: Sleep Apnea Study Structure

```
studies/sleep_apnea/
├── prospero-sleep-apnea-dementia.md     # PROSPERO protocol
├── guidelines.md                         # Study-specific query guidelines
└── general_guidelines.md                 # General SR best practices
```

#### PROSPERO Protocol File

**File: `studies/sleep_apnea/prospero-sleep-apnea-dementia.md`**

```markdown
# PROSPERO Protocol: Sleep Apnea and Dementia

## Research Question
Does sleep apnea increase the risk of dementia?

## PICOS Framework

### Population
Patients with sleep apnea diagnosed by:
- Polysomnography (PSG) study
- Overnight oximetry study
- Apnea-Hypopnea Index (AHI) or Oxygen Desaturation Index (ODI) clearly specified
- No age limit

### Intervention/Exposure
Presence of sleep apnea

### Comparator
Patients without sleep apnea

### Outcomes
Primary: Onset of dementia (all-cause)

Secondary:
- Alzheimer's disease
- Parkinson's disease dementia
- Lewy body dementia
- Frontotemporal dementia
- Vascular dementia
- Mixed dementia

### Study Design
- Prospective cohort studies
- Retrospective cohort studies
- Randomized controlled trials

## Keywords
Sleep apnea, obstructive sleep apnea, OSA, sleep-disordered breathing, 
dementia, cognitive decline, Alzheimer's, cognitive impairment

## Date Range
From inception to March 1, 2021
```

#### Study Guidelines File

**File: `studies/sleep_apnea/guidelines.md`**

```markdown
# Sleep Apnea Study - Query Generation Guidelines

## Key Concepts to Emphasize

### Exposure Concept (Sleep Apnea)
- Use both MeSH/Emtree: "Sleep Apnea Syndromes"
- Include variants: sleep apnea, sleep apnoea, OSA, OSAS
- Include: sleep-disordered breathing, sleep breathing disorders

### Outcome Concept (Dementia)
- Use broad MeSH/Emtree: "Dementia"
- Include specific types: Alzheimer's, vascular dementia, Lewy body
- Include: cognitive decline, cognitive impairment

### Study Design Filters
- Cohort studies (prospective/retrospective)
- RCTs
- Exclude: case reports, case series, reviews

## Precision Strategy
- High-recall: Maximize MeSH explosion, broad text words
- Balanced: Combine MeSH with filtered free text
- High-precision: Major focus headings, title searches
```

---

### Step 2.2: Generate the Command File

Now you'll use the command generator to create an executable LLM prompt.

#### Command Structure

```bash
/generate_multidb_prompt \
  --command_name <name_for_new_command> \
  --protocol_path <path_to_protocol_file> \
  --databases <comma_separated_db_list> \
  --level <basic|extended|keywords|exhaustive> \
  --min_date <YYYY/MM/DD> \
  --max_date <YYYY/MM/DD>
```

#### Parameter Explanations

| Parameter | Description | Example | Default |
|-----------|-------------|---------|---------|
| `--command_name` | Name for the generated command (becomes `/<command_name>`) | `run_sleep_apnea_multidb_extended_v2` | *Required* |
| `--protocol_path` | Absolute path to PROSPERO/protocol file | `studies/sleep_apnea/prospero-sleep-apnea-dementia.md` | *Required* |
| `--databases` | Comma-separated database list (no spaces!) | `pubmed,scopus,embase` | `pubmed` |
| `--level` | Query complexity level (see below) | `extended` | `extended` |
| `--min_date` | Start of date range for literature search | `1990/01/01` | `1980/01/01` |
| `--max_date` | End of date range for literature search | `2021/03/01` | `2025/12/31` |

**Level Options:**

| Level | Queries per DB | Description | Use When |
|-------|----------------|-------------|----------|
| **basic** | 3 | High-recall, Balanced, High-precision | Quick testing, simple reviews |
| **extended** | 6 | Basic 3 + 3 micro-variants (Filter, Scope, Proximity) | **Recommended** for most studies |
| **keywords** | 4 | Keyword-focused + Basic 3 | Protocol has explicit keyword list |
| **exhaustive** | 9 | All variants + extra exploration | Comprehensive systematic reviews |

**Important Database Notes:**
- `pubmed`: Always free, no API key needed (but recommended for rate limits)
- `scopus`: Requires institutional subscription + API key
- `embase`: No API access - requires manual export (see Step 4)
- `wos`: Requires institutional subscription + API key

#### Example: Sleep Apnea Command Generation

```bash
/generate_multidb_prompt \
  --command_name run_sleep_apnea_multidb_extended_v2 \
  --protocol_path studies/sleep_apnea/prospero-sleep-apnea-dementia.md \
  --databases pubmed,scopus,embase \
  --level extended \
  --min_date "" \
  --max_date "2021/03/01"
```

**What This Does:**

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Read Input Files                                    │
├─────────────────────────────────────────────────────────────┤
│ ✓ Read prompts/prompt_template_multidb.md                  │
│ ✓ Read prompts/database_guidelines.md                      │
│ ✓ Read studies/sleep_apnea/prospero-sleep-apnea-dementia.md│
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Extract Level-Specific Instructions                 │
├─────────────────────────────────────────────────────────────┤
│ • Find text between:                                        │
│   --- START LEVEL-SPECIFIC INSTRUCTIONS ---                │
│   and                                                        │
│   --- END LEVEL-SPECIFIC INSTRUCTIONS ---                  │
│                                                              │
│ • Within that block, extract:                               │
│   --- LEVEL: extended ---                                   │
│   [content here]                                            │
│   --- END LEVEL: extended ---                               │
│                                                              │
│ • Remove the LEVEL markers, keep only content               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Extract Database Guidelines                         │
├─────────────────────────────────────────────────────────────┤
│ Databases: pubmed, scopus, embase                           │
│                                                              │
│ From database_guidelines.md, extract:                       │
│ ✓ ## PubMed section (all content)                          │
│ ✓ ## Scopus section (all content)                          │
│ ✓ ## Embase section (all content)                          │
│                                                              │
│ Concatenate into single string                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Extract Protocol Information                        │
├─────────────────────────────────────────────────────────────┤
│ From prospero-sleep-apnea-dementia.md:                      │
│ • Topic: "The Association Between Sleep Apnea and Dementia"│
│ • Population: "Patients with sleep apnea diagnosed..."     │
│ • Intervention: "Presence of sleep apnea"                  │
│ • Comparator: "Patients without sleep apnea"               │
│ • Outcomes: "Onset of dementia (all-cause)..."             │
│ • Design: "Prospective or retrospective cohort studies..." │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Populate Template                                   │
├─────────────────────────────────────────────────────────────┤
│ Replace placeholders:                                        │
│ [PATH TO PROSPERO/PROTOCOL FILE] →                         │
│   studies/sleep_apnea/prospero-sleep-apnea-dementia.md    │
│                                                              │
│ [STUDY_NAME] → sleep_apnea                                 │
│                                                              │
│ [DATE_WINDOW_START] → "" (from inception)                  │
│ [DATE_WINDOW_END] → "2021/03/01"                           │
│                                                              │
│ [LIST OF DATABASES] → pubmed,scopus,embase                 │
│                                                              │
│ [CONCISE TOPIC DESCRIPTION] →                               │
│   "The Association Between Sleep Apnea and Dementia"       │
│                                                              │
│ [DATABASE_SPECIFIC_GUIDELINES] →                            │
│   [Full concatenated guidelines for PubMed+Scopus+Embase]  │
│                                                              │
│ [Describe the patient population] →                         │
│   "Patients with sleep apnea diagnosed..."                 │
│ [... and all other PICOS placeholders ...]                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 6: Write Output File                                   │
├─────────────────────────────────────────────────────────────┤
│ File: .gemini/commands/run_sleep_apnea_multidb_extended_v2.toml │
│                                                              │
│ Content: TOML file with populated prompt in '''...'''      │
└─────────────────────────────────────────────────────────────┘
```

#### Expected Output

```
✅ Command Generation Complete!

Generated file:
  .gemini/commands/run_sleep_apnea_multidb_extended_v2.toml

The new command is ready to execute:
  /run_sleep_apnea_multidb_extended_v2

This command will:
  • Generate 6 queries for PubMed (high-recall, balanced, high-precision, 
    filter-variant, scope-variant, proximity-variant)
  • Generate 6 queries for Scopus (same structure)
  • Generate 6 queries for Embase (same structure)
  • Total: 18 queries across 3 databases

Next step: Run the command to execute the LLM prompt!
```

---

### Step 2.3: Understand the Generated Command File

Let's examine what was created in `.gemini/commands/run_sleep_apnea_multidb_extended_v2.toml`.

#### File Structure

```toml
# In: ~/.gemini/commands/run_sleep_apnea_multidb_extended_v2.toml
# This command will be invoked via: /run_sleep_apnea_multidb_extended_v2

description = "Runs the multi-database query generation prompt for the study based on studies/sleep_apnea/prospero-sleep-apnea-dementia.md."

prompt = '''
[FULL POPULATED PROMPT HERE - 200+ lines]
'''
```

#### Key Sections in the Populated Prompt

**1. System Instructions**
```markdown
## SYSTEM (role: information specialist & indexer):
- You are an expert information specialist and medical indexer.
- Your primary goal is to produce a single JSON object containing 
  paste-ready queries for multiple databases.
- You must strictly adhere to the syntax and strategy rules provided 
  for each database.
```

**2. Input Specification**
```markdown
## INPUT
- TOPIC: `The Association Between Sleep Apnea and Dementia`
- DATE WINDOW: `` to `2021/03/01`
- DATABASES: `pubmed,scopus,embase`
```

**3. PICOS Summary** (extracted from protocol)
```markdown
## PICOS (summary)
- **Population:** `Patients with sleep apnea diagnosed by polysomnography...`
- **Intervention/Exposure:** `Presence of sleep apnea`
- **Comparator:** `Patients without sleep apnea`
- **Outcomes:** `Onset of dementia (all-cause)...`
- **Design:** `Prospective or retrospective cohort studies...`
```

**4. Database-Specific Guidelines** (injected from database_guidelines.md)
```markdown
## DATABASE-SPECIFIC GUIDELINES

## PubMed
- **Syntax**: Use `[tiab]` for title/abstract searches...
- **Precision_Knobs**:
  **Filter Knobs:**
  - Species filter: `humans[Filter]`
  - Language filter: `english[Filter]`
  
  **Scope Knobs:**
  - Title only: `[ti]`
  - Major headings: `[majr]`
  ...

## Scopus
- **Syntax**: Use `TITLE-ABS-KEY(...)` for general topic searches...
- **Precision_Knobs**:
  **Filter Knobs:**
  - Document type: `DOCTYPE(ar OR re)`
  ...

## Embase
[Similar structure]
```

**5. Output Instructions** (level-specific, cleaned of markers)
```markdown
## OUTPUT

### 1. Concept Tables (Markdown)
- **Concept→MeSH/Emtree table:** ...
- **Concept→Textword table:** ...

### 2. JSON Query Object
Generate **6 queries** for each database by following this recipe:
1. **High-recall:** ...
2. **Balanced:** ...
3. **High-precision:** ...
4. **Micro-variant 1 (Filter-based):** Start with 'Balanced' and add 
   a filter from "Filter Knobs"
5. **Micro-variant 2 (Field/Scope-based):** Start with 'Balanced' and 
   add a scope restriction from "Scope Knobs"
6. **Micro-variant 3 (Proximity-based):** Start with 'Balanced' and 
   add proximity operators from "Proximity Knobs"

### 3. PRESS Self-Check (JSON Patch)
- Critically review your work
- Provide up to 2 revisions in json_patch object
```

**6. Expected Output Format**
```markdown
## Expected JSON Output Format

Your JSON Query Object should follow this structure:

```json
{
  "pubmed": [
    "# High-recall: ...",
    "# Balanced: ...",
    "# High-precision: ...",
    "# Micro-variant 1: ...",
    "# Micro-variant 2: ...",
    "# Micro-variant 3: ..."
  ],
  "scopus": [
    "# High-recall: ...",
    ...
  ],
  "embase": [
    "# High-recall: ...",
    ...
  ]
}
```

Note: The number of queries per database depends on the level 
(basic: 3, extended: 6, keywords: 4, exhaustive: 9).
```

---

### Step 2.4: Execute the LLM Prompt

Now run the generated command to execute the prompt with an LLM.

#### Basic Execution

```bash
/run_sleep_apnea_multidb_extended_v2
```

This invokes the LLM (Claude, GPT, Gemini, etc.) with the complete prompt.

#### What Happens During Execution

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: LLM Analyzes Protocol                              │
├─────────────────────────────────────────────────────────────┤
│ • Reads PICOS framework                                     │
│ • Identifies key concepts: sleep apnea, dementia           │
│ • Notes study design requirements: cohort, RCT             │
│ • Notes date range: inception to 2021/03/01                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: LLM Creates Concept Tables                         │
├─────────────────────────────────────────────────────────────┤
│ Concept→MeSH Table:                                         │
│ ┌─────────────┬──────────────────┬─────────┬──────────┐   │
│ │ Concept     │ MeSH Term        │ Tree    │ Explode? │   │
│ ├─────────────┼──────────────────┼─────────┼──────────┤   │
│ │ Sleep Apnea │ Sleep Apnea Syn. │ C08.618 │ Yes      │   │
│ │ Dementia    │ Dementia         │ F03.615 │ Yes      │   │
│ └─────────────┴──────────────────┴─────────┴──────────┘   │
│                                                              │
│ Concept→Textword Table:                                     │
│ ┌─────────────┬──────────────────┬───────┬────────────┐   │
│ │ Concept     │ Synonym/Phrase   │ Field │ Truncation │   │
│ ├─────────────┼──────────────────┼───────┼────────────┤   │
│ │ Sleep Apnea │ sleep apnea      │ tiab  │ No         │   │
│ │ Sleep Apnea │ sleep apnoea     │ tiab  │ No         │   │
│ │ Sleep Apnea │ OSA              │ tiab  │ No         │   │
│ │ Dementia    │ cognitive decline│ tiab  │ No         │   │
│ └─────────────┴──────────────────┴───────┴────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: LLM Generates Queries (Database by Database)       │
├─────────────────────────────────────────────────────────────┤
│ FOR EACH DATABASE (pubmed, scopus, embase):                │
│                                                              │
│ 1. High-recall query:                                       │
│    • Use exploded MeSH/Emtree terms                        │
│    • Include all synonyms with OR                           │
│    • Broad Boolean logic                                    │
│                                                              │
│ 2. Balanced query:                                          │
│    • Mix of MeSH + free text                               │
│    • Add study design filters                               │
│    • Moderate precision                                     │
│                                                              │
│ 3. High-precision query:                                    │
│    • Major focus terms only ([majr], *term)                │
│    • Title searches                                         │
│    • Strict filters                                         │
│                                                              │
│ 4. Micro-variant 1 (Filter):                               │
│    • Start with Balanced                                    │
│    • Add: humans[Filter] (PubMed)                          │
│    • Add: DOCTYPE(ar OR re) (Scopus)                       │
│    • Add: limit to article (Embase)                        │
│                                                              │
│ 5. Micro-variant 2 (Scope):                                │
│    • Start with Balanced                                    │
│    • Restrict key concepts to title: [ti]                  │
│    • Or use major headings: [majr]                         │
│                                                              │
│ 6. Micro-variant 3 (Proximity):                            │
│    • Start with Balanced                                    │
│    • Add: W/5 for Scopus (within 5 words)                 │
│    • Add: ADJ5 for Embase                                  │
│    • For PubMed (no proximity): use [majr] fallback       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: LLM Applies Database-Specific Syntax               │
├─────────────────────────────────────────────────────────────┤
│ PubMed:                                                     │
│ ("Sleep Apnea Syndromes"[MeSH] OR "sleep apnea"[tiab] OR   │
│  "sleep apnoea"[tiab]) AND ("Dementia"[MeSH] OR            │
│  dementia[tiab]) AND ("1990/01/01"[Date - Publication] :   │
│  "2021/03/01"[Date - Publication])                         │
│                                                              │
│ Scopus:                                                     │
│ TITLE-ABS-KEY("sleep apnea" OR "sleep apnoea" OR           │
│ "obstructive sleep apnea") AND TITLE-ABS-KEY(dementia OR   │
│ "cognitive decline") AND PUBYEAR > 1989 AND PUBYEAR < 2022 │
│                                                              │
│ Embase:                                                     │
│ ('sleep apnea syndrome'/exp OR 'sleep apnea':ti,ab) AND    │
│ ('dementia'/exp OR dementia:ti,ab) AND [1990-2021]/py      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: LLM Performs PRESS Self-Check                      │
├─────────────────────────────────────────────────────────────┤
│ • Reviews generated queries for:                            │
│   - Missing synonyms                                        │
│   - Syntax errors                                           │
│   - Logical inconsistencies                                 │
│                                                              │
│ • If issues found, creates JSON patch:                      │
│   {                                                          │
│     "json_patch": {                                         │
│       "pubmed.0": "# Revised query...",                    │
│       "scopus.2": "# Revised query..."                     │
│     }                                                        │
│   }                                                          │
│                                                              │
│ • Includes translation notes documenting syntax differences │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 6: LLM Returns JSON Output                            │
├─────────────────────────────────────────────────────────────┤
│ {                                                            │
│   "pubmed": [                                               │
│     "# High-recall: Broad MeSH...",                        │
│     "(\"Sleep Apnea Syndromes\"[MeSH] OR...)",             │
│     "# Balanced: Mix of MeSH...",                          │
│     "(\"Sleep Apnea Syndromes\"[MeSH] OR...)",             │
│     ...                                                     │
│   ],                                                         │
│   "scopus": [...],                                          │
│   "embase": [...]                                           │
│ }                                                            │
└─────────────────────────────────────────────────────────────┘
```

#### Expected LLM Response Format

The LLM will return a structured response with three main sections:

**1. Concept Tables (Markdown)**
```markdown
### 1. Concept Tables

#### Concept→MeSH/Emtree Table

| Concept | Term | Tree Note | Explode? | Rationale & Source |
|---------|------|-----------|----------|-------------------|
| Sleep Apnea | Sleep Apnea Syndromes | C08.618.085 | Yes | Captures all SA types; from PROSPERO keywords |
| Dementia | Dementia | F03.615.400 | Yes | Broad outcome capture; PICOS primary outcome |
| Study Design | Cohort Studies | E05.318.372 | Yes | PICOS specifies cohort + RCT designs |

#### Concept→Textword Table

| Concept | Synonym/Phrase | Field | Truncation? | Source |
|---------|----------------|-------|-------------|--------|
| Sleep Apnea | sleep apnea | tiab | No | PROSPERO keywords |
| Sleep Apnea | sleep apnoea | tiab | No | UK spelling variant |
| Sleep Apnea | OSA | tiab | No | Common abbreviation |
| Sleep Apnea | obstructive sleep apnea | tiab | No | Most common type |
| Dementia | dementia | tiab | No | PROSPERO keywords |
| Dementia | cognitive decline | tiab | No | Related outcome term |
```

**2. JSON Query Object**
````json
{
  "pubmed": [
    "# High-recall: Broad MeSH terms with explosion, all text word synonyms",
    "(\"Sleep Apnea Syndromes\"[MeSH] OR \"sleep apnea\"[tiab] OR \"sleep apnoea\"[tiab] OR \"obstructive sleep apnea\"[tiab] OR \"OSA\"[tiab] OR \"OSAS\"[tiab]) AND (\"Dementia\"[MeSH] OR dementia[tiab] OR \"cognitive decline\"[tiab] OR \"cognitive impairment\"[tiab] OR alzheimer*[tiab]) AND (\"1990/01/01\"[Date - Publication] : \"2021/03/01\"[Date - Publication])",
    
    "# Balanced: Mix of MeSH and free text with study design filter",
    "(\"Sleep Apnea Syndromes\"[MeSH] OR \"sleep apnea\"[tiab]) AND (\"Dementia\"[MeSH] OR dementia[tiab]) AND (\"Cohort Studies\"[MeSH] OR cohort[tiab] OR prospective[tiab] OR \"Randomized Controlled Trial\"[pt]) AND (\"1990/01/01\"[Date - Publication] : \"2021/03/01\"[Date - Publication])",
    
    "# High-precision: Major MeSH headings and title searches",
    "(\"Sleep Apnea Syndromes\"[majr]) AND (\"Dementia\"[majr]) AND (cohort[ti] OR trial[ti]) AND (\"1990/01/01\"[Date - Publication] : \"2021/03/01\"[Date - Publication])",
    
    "# Micro-variant 1 (Filter): Balanced + humans filter",
    "(\"Sleep Apnea Syndromes\"[MeSH] OR \"sleep apnea\"[tiab]) AND (\"Dementia\"[MeSH] OR dementia[tiab]) AND (\"Cohort Studies\"[MeSH] OR cohort[tiab]) AND humans[Filter] AND (\"1990/01/01\"[Date - Publication] : \"2021/03/01\"[Date - Publication])",
    
    "# Micro-variant 2 (Scope): Balanced + title restriction on key concepts",
    "(\"Sleep Apnea Syndromes\"[MeSH] OR \"sleep apnea\"[ti]) AND (\"Dementia\"[MeSH] OR dementia[ti]) AND (cohort[tiab] OR prospective[tiab]) AND (\"1990/01/01\"[Date - Publication] : \"2021/03/01\"[Date - Publication])",
    
    "# Micro-variant 3 (Proximity fallback): Balanced + major headings (PubMed has no proximity)",
    "(\"Sleep Apnea Syndromes\"[majr] OR \"sleep apnea\"[tiab]) AND (\"Dementia\"[majr] OR dementia[tiab]) AND (cohort[tiab] OR trial[tiab]) AND (\"1990/01/01\"[Date - Publication] : \"2021/03/01\"[Date - Publication])"
  ],
  
  "scopus": [
    "# High-recall: Broad keyword search across all fields",
    "TITLE-ABS-KEY(\"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR OSA OR OSAS OR \"sleep disordered breathing\") AND TITLE-ABS-KEY(dementia OR \"cognitive decline\" OR \"cognitive impairment\" OR alzheimer*) AND PUBYEAR > 1989 AND PUBYEAR < 2022",
    
    "# Balanced: Mixed fields with document type filter",
    "TITLE-ABS-KEY(\"sleep apnea\" OR \"obstructive sleep apnea\") AND TITLE-ABS-KEY(dementia OR \"cognitive decline\") AND TITLE-ABS-KEY(cohort OR prospective OR trial) AND DOCTYPE(ar OR re) AND PUBYEAR > 1989 AND PUBYEAR < 2022",
    
    "# High-precision: Title-only search for key concepts",
    "TITLE(\"sleep apnea\" OR \"obstructive sleep apnea\") AND TITLE(dementia) AND TITLE-ABS-KEY(cohort OR trial) AND DOCTYPE(ar) AND PUBYEAR > 1989 AND PUBYEAR < 2022",
    
    "# Micro-variant 1 (Filter): Balanced + article/review document type",
    "TITLE-ABS-KEY(\"sleep apnea\" OR \"obstructive sleep apnea\") AND TITLE-ABS-KEY(dementia OR \"cognitive decline\") AND TITLE-ABS-KEY(cohort OR prospective) AND DOCTYPE(ar OR re) AND PUBYEAR > 1989 AND PUBYEAR < 2022",
    
    "# Micro-variant 2 (Scope): Balanced + title restriction",
    "TITLE(\"sleep apnea\") AND TITLE(dementia) AND TITLE-ABS-KEY(cohort OR prospective OR trial) AND PUBYEAR > 1989 AND PUBYEAR < 2022",
    
    "# Micro-variant 3 (Proximity): Balanced + W/5 proximity operator",
    "TITLE-ABS-KEY(\"sleep apnea\" W/5 dementia) AND TITLE-ABS-KEY(cohort OR prospective OR trial) AND DOCTYPE(ar OR re) AND PUBYEAR > 1989 AND PUBYEAR < 2022"
  ],
  
  "embase": [
    "# High-recall: Exploded Emtree terms with broad free text",
    "('sleep apnea syndrome'/exp OR 'sleep apnea':ti,ab OR 'sleep apnoea':ti,ab OR 'obstructive sleep apnea':ti,ab OR OSA:ti,ab) AND ('dementia'/exp OR dementia:ti,ab OR 'cognitive decline':ti,ab OR 'cognitive impairment':ti,ab) AND [1990-2021]/py",
    
    "# Balanced: Mixed Emtree and free text with study design",
    "('sleep apnea syndrome'/exp OR 'sleep apnea':ti,ab) AND ('dementia'/exp OR dementia:ti,ab) AND ('cohort analysis'/exp OR cohort:ti,ab OR prospective:ti,ab OR 'randomized controlled trial'/exp) AND [1990-2021]/py",
    
    "# High-precision: Major focus terms and title searches",
    "*'sleep apnea syndrome' AND *'dementia' AND (cohort:ti OR trial:ti) AND [1990-2021]/py AND [article]/lim",
    
    "# Micro-variant 1 (Filter): Balanced + article limit",
    "('sleep apnea syndrome'/exp OR 'sleep apnea':ti,ab) AND ('dementia'/exp OR dementia:ti,ab) AND (cohort:ti,ab OR prospective:ti,ab) AND [1990-2021]/py AND [article]/lim",
    
    "# Micro-variant 2 (Scope): Balanced + title restriction",
    "('sleep apnea syndrome'/exp OR 'sleep apnea':ti) AND ('dementia'/exp OR dementia:ti) AND (cohort:ti,ab OR prospective:ti,ab) AND [1990-2021]/py",
    
    "# Micro-variant 3 (Proximity): Balanced + ADJ5 adjacency operator",
    "('sleep apnea':ti,ab ADJ5 dementia:ti,ab) AND (cohort:ti,ab OR prospective:ti,ab OR trial:ti,ab) AND [1990-2021]/py"
  ]
}
````

**3. PRESS Self-Check & JSON Patch**
```json
{
  "json_patch": {
    "pubmed.1": "# Balanced: Mix of MeSH and free text with study design filter (REVISED: added RCT publication type)\n(\"Sleep Apnea Syndromes\"[MeSH] OR \"sleep apnea\"[tiab]) AND (\"Dementia\"[MeSH] OR dementia[tiab]) AND (\"Cohort Studies\"[MeSH] OR cohort[tiab] OR prospective[tiab] OR \"Randomized Controlled Trial\"[pt] OR \"controlled clinical trial\"[pt]) AND (\"1990/01/01\"[Date - Publication] : \"2021/03/01\"[Date - Publication])"
  }
}
```

**Translation Notes:**
```markdown
## Translation Notes

### Database Syntax Differences
- **Date filters**: PubMed uses [Date - Publication] range, Scopus uses PUBYEAR comparisons, Embase uses /py suffix
- **Field codes**: PubMed [tiab], Scopus TITLE-ABS-KEY(), Embase :ti,ab
- **Controlled vocab**: PubMed uses MeSH with [MeSH], Embase uses Emtree with /exp or /de
- **Major focus**: PubMed [majr], Embase *'term' prefix, Scopus has no direct equivalent (use TITLE)
- **Proximity**: Scopus W/n, Embase ADJn, PubMed has none (fallback to [majr])

### Significant Changes Between Databases
- Scopus queries use PUBYEAR > 1989 instead of >= 1990 to ensure 1990 is included
- PubMed includes RCT publication type [pt] for design filter
- Embase uses [article]/lim instead of DOCTYPE for precision variants
```

---

### Step 2.5: Save and Organize Query Outputs

After receiving the LLM response, you need to extract and save the queries.

#### Manual Extraction Process

**Step 1: Copy JSON Queries**

From the LLM response, copy the JSON object (between the ` ```json ` markers).

**Step 2: Create Database-Specific Query Files**

For each database, create a text file with queries:

**File: `studies/sleep_apnea/queries.txt` (PubMed)**
```
# High-recall: Broad MeSH terms with explosion, all text word synonyms
("Sleep Apnea Syndromes"[MeSH] OR "sleep apnea"[tiab] OR "sleep apnoea"[tiab] OR "obstructive sleep apnea"[tiab] OR "OSA"[tiab] OR "OSAS"[tiab]) AND ("Dementia"[MeSH] OR dementia[tiab] OR "cognitive decline"[tiab] OR "cognitive impairment"[tiab] OR alzheimer*[tiab]) AND ("1990/01/01"[Date - Publication] : "2021/03/01"[Date - Publication])

# Balanced: Mix of MeSH and free text with study design filter
("Sleep Apnea Syndromes"[MeSH] OR "sleep apnea"[tiab]) AND ("Dementia"[MeSH] OR dementia[tiab]) AND ("Cohort Studies"[MeSH] OR cohort[tiab] OR prospective[tiab] OR "Randomized Controlled Trial"[pt]) AND ("1990/01/01"[Date - Publication] : "2021/03/01"[Date - Publication])

# High-precision: Major MeSH headings and title searches
("Sleep Apnea Syndromes"[majr]) AND ("Dementia"[majr]) AND (cohort[ti] OR trial[ti]) AND ("1990/01/01"[Date - Publication] : "2021/03/01"[Date - Publication])

# Micro-variant 1 (Filter): Balanced + humans filter
("Sleep Apnea Syndromes"[MeSH] OR "sleep apnea"[tiab]) AND ("Dementia"[MeSH] OR dementia[tiab]) AND ("Cohort Studies"[MeSH] OR cohort[tiab]) AND humans[Filter] AND ("1990/01/01"[Date - Publication] : "2021/03/01"[Date - Publication])

# Micro-variant 2 (Scope): Balanced + title restriction on key concepts
("Sleep Apnea Syndromes"[MeSH] OR "sleep apnea"[ti]) AND ("Dementia"[MeSH] OR dementia[ti]) AND (cohort[tiab] OR prospective[tiab]) AND ("1990/01/01"[Date - Publication] : "2021/03/01"[Date - Publication])

# Micro-variant 3 (Proximity fallback): Balanced + major headings
("Sleep Apnea Syndromes"[majr] OR "sleep apnea"[tiab]) AND ("Dementia"[majr] OR dementia[tiab]) AND (cohort[tiab] OR trial[tiab]) AND ("1990/01/01"[Date - Publication] : "2021/03/01"[Date - Publication])
```

**File: `studies/sleep_apnea/queries_scopus.txt` (Scopus)**
```
# High-recall: Broad keyword search across all fields
TITLE-ABS-KEY("sleep apnea" OR "sleep apnoea" OR "obstructive sleep apnea" OR OSA OR OSAS OR "sleep disordered breathing") AND TITLE-ABS-KEY(dementia OR "cognitive decline" OR "cognitive impairment" OR alzheimer*) AND PUBYEAR > 1989 AND PUBYEAR < 2022

# Balanced: Mixed fields with document type filter
TITLE-ABS-KEY("sleep apnea" OR "obstructive sleep apnea") AND TITLE-ABS-KEY(dementia OR "cognitive decline") AND TITLE-ABS-KEY(cohort OR prospective OR trial) AND DOCTYPE(ar OR re) AND PUBYEAR > 1989 AND PUBYEAR < 2022

[... continue with remaining 4 queries ...]
```

**File: `studies/sleep_apnea/queries_embase.txt` (Embase)**
```
# High-recall: Exploded Emtree terms with broad free text
('sleep apnea syndrome'/exp OR 'sleep apnea':ti,ab OR 'sleep apnoea':ti,ab OR 'obstructive sleep apnea':ti,ab OR OSA:ti,ab) AND ('dementia'/exp OR dementia:ti,ab OR 'cognitive decline':ti,ab OR 'cognitive impairment':ti,ab) AND [1990-2021]/py

[... continue with remaining 5 queries ...]
```

#### Automated Extraction (Optional)

You can create a script to parse the JSON and generate query files automatically:

```python
# scripts/extract_queries_from_json.py
import json
import sys
from pathlib import Path

def extract_queries(json_file, output_dir):
    """Extract queries from LLM JSON output to database-specific files."""
    
    with open(json_file) as f:
        data = json.load(f)
    
    # Database → filename mapping
    file_map = {
        'pubmed': 'queries.txt',
        'scopus': 'queries_scopus.txt',
        'embase': 'queries_embase.txt',
        'wos': 'queries_wos.txt'
    }
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for db, queries in data.items():
        if db == 'json_patch':
            continue  # Skip patch object
        
        output_file = output_dir / file_map.get(db, f'queries_{db}.txt')
        
        with open(output_file, 'w') as f:
            for query in queries:
                f.write(query + '\n\n')
        
        print(f"✅ Created {output_file} ({len(queries)} queries)")

if __name__ == '__main__':
    extract_queries(sys.argv[1], sys.argv[2])
```

**Usage:**
```bash
python scripts/extract_queries_from_json.py \
  llm_output.json \
  studies/sleep_apnea/
```

---

### Step 2.6: Integration with Workflow

The generated queries are now ready to use with the main workflow.

#### Verification Checklist

Before proceeding to query execution, verify:

- [ ] **Query files exist** for all databases:
  ```bash
  ls studies/sleep_apnea/queries*.txt
  # Should show: queries.txt, queries_scopus.txt, queries_embase.txt
  ```

- [ ] **Query count matches level**:
  ```bash
  # For extended level: 6 queries per database
  grep -c "^# " studies/sleep_apnea/queries.txt
  # Should output: 6
  ```

- [ ] **Database syntax is correct**:
  - PubMed: Check for `[MeSH]`, `[tiab]`, `[Date - Publication]`
  - Scopus: Check for `TITLE-ABS-KEY()`, `PUBYEAR`, `DOCTYPE()`
  - Embase: Check for `/exp`, `:ti,ab`, `/py`

- [ ] **Queries are paste-ready** (no markdown formatting, code blocks, or extra whitespace)

- [ ] **Date ranges match protocol** (inception to 2021/03/01 for sleep apnea example)

#### Query Quality Assessment

Review the generated queries for:

1. **Concept Coverage**
   - ✅ All PICOS concepts included (sleep apnea, dementia, study design)
   - ✅ Synonyms and variants present
   - ✅ Controlled vocabulary used (MeSH, Emtree)

2. **Syntax Correctness**
   - ✅ Parentheses balanced
   - ✅ Boolean operators correct (AND, OR, NOT)
   - ✅ Field codes valid for database

3. **Precision Gradient**
   - ✅ High-recall query is broadest (most OR clauses)
   - ✅ High-precision query is narrowest (major headings, title searches)
   - ✅ Micro-variants apply appropriate Precision_Knobs

4. **Cross-Database Consistency**
   - ✅ Query 1 in all files = same strategy (high-recall)
   - ✅ Query 2 in all files = same strategy (balanced)
   - ✅ Concept coverage equivalent across databases

#### Next Steps

```
┌────────────────────────────────────────────────────────────┐
│ ✅ LLM Query Generation Complete                           │
│                                                             │
│ You now have:                                               │
│ • studies/sleep_apnea/queries.txt (6 PubMed queries)      │
│ • studies/sleep_apnea/queries_scopus.txt (6 Scopus)       │
│ • studies/sleep_apnea/queries_embase.txt (6 Embase)       │
│                                                             │
│ Next: Execute queries across all databases                 │
│       → See Step 5: Multi-Database Query Execution         │
└────────────────────────────────────────────────────────────┘
```

---

### Step 2.7: Comparison with Manual Query Design

You now have two options for query creation:

| Aspect | **LLM-Powered (Step 2)** | **Manual Design (Step 3)** |
|--------|-------------------------|---------------------------|
| **Time required** | ~5-10 minutes (generation + review) | ~2-4 hours (per database) |
| **Expertise needed** | Protocol writing | Database syntax + SR methods |
| **Consistency** | High (automated translation) | Variable (manual translation) |
| **Customization** | Template-based levels | Fully customizable |
| **Quality control** | PRESS self-check included | Manual peer review |
| **Best for** | Multiple databases, rapid prototyping | Single database, expert-level queries |

**Recommendation**: 
- Use **LLM-powered** for initial query generation and multi-database consistency
- Use **manual refinement** (Step 3) to optimize queries based on preliminary results
- Combine both: Generate with LLM, refine manually, regenerate if needed

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
bash scripts/complete_embase_workflow.sh
```

**What it does**:
1. Validates CSV files exist
2. Batch imports all Embase queries
3. Aggregates with existing PubMed/Scopus/WOS results
4. Scores combined sets against gold standard

**When to use**: After running the main workflow, when adding Embase results.

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
6. ✅ Falls back to CrossRef API for non-PubMed articles
7. ✅ Generates `gold_pmids_ai_2022.csv` (simple format)
8. ✅ Generates `gold_pmids_ai_2022_detailed.csv` (multi-key format)
9. ✅ Creates quality report: `gold_generation_report_ai_2022.md`

**Expected runtime**: 5-10 minutes for 40-50 included studies

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
   Output: studies/ai_2022/included_studies_ai_2022.json

Summary:
  - Total included studies: 14
  - With DOI (from paper): 8
  - With PMID (from paper): 6
  - With neither: 0
```

**Output format** (`included_studies_ai_2022.json`):
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
  --input studies/ai_2022/included_studies_ai_2022.json \
  --output studies/ai_2022/included_studies_ai_2022_with_pmids.json \
  --email your.email@institution.edu
```

**What happens**:
```
🔍 Looking up PMIDs for 14 studies...

Study 1/14: Li AM (2008)
  Query: "Ambulatory blood pressure in children with obstructive sleep apnoea"[Title] AND Li AM[Author] AND 2008[Date]
  ✅ Found PMID: 18388205 (confidence: 0.95)
  ✅ Found DOI: 10.1136/thx.2007.091132

Study 2/14: Amin RS (2004)
  PMID already present: 14764433
  🔍 Looking up DOI...
  ✅ Found DOI: 10.1164/rccm.200309-1305OC

Study 3/14: Chan KC (2020)
  ✅ Found PMID: 32209641 (confidence: 0.92)
  ✅ Found DOI: 10.1136/thoraxjnl-2019-213692

...

📊 Lookup Complete!
   With PMID: 14/14 (100%)
   With DOI: 14/14 (100%)
   Average confidence: 0.93
```

**API Strategy**:
1. **PubMed E-utilities** (primary):
   - Queries by title + author + year
   - Returns PMID + DOI (both from PubMed record)
   - Confidence scoring: Title similarity using Levenshtein distance

2. **CrossRef API** (fallback):
   - Used when PubMed returns no match
   - Returns DOI only (CrossRef doesn't have PMID)
   - Useful for non-indexed journals, preprints

**Confidence Thresholds**:
- **Accept**: confidence ≥ 0.85 (high similarity)
- **Review**: confidence 0.70-0.85 (moderate similarity)
- **Reject**: confidence < 0.70 (poor match)

#### Step 4.5.3: Generate Gold Standard CSV Files

**Command**:
```bash
python scripts/generate_gold_standard.py \
  --input studies/ai_2022/included_studies_ai_2022_with_pmids.json \
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

Lower threshold for more inclusive gold standard:
```bash
python scripts/extract_included_studies.py ai_2022 \
  --lookup-pmid \
  --generate-gold-csv \
  --confidence 0.75
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
| `included_studies_<study>.json` | JSON | Intermediate: Extracted studies (no API lookups) |
| `included_studies_<study>_with_pmids.json` | JSON | Intermediate: After API lookups (with confidence) |
| `gold_pmids_<study>.csv` | CSV (1 column) | Simple: PMID-only, backward compatible |
| `gold_pmids_<study>_detailed.csv` | CSV (6 columns) | **Main output**: PMID+DOI, multi-key ready |
| `gold_generation_report_<study>.md` | Markdown | Quality report: Coverage, confidence, rejected studies |

---

## Step 5: Multi-Database Query Execution

### Understanding the Main Workflow Script

The main workflow script (`run_workflow_sleep_apnea.sh`) orchestrates everything:

**What it does**:
1. Loads environment variables (`.env`)
2. Activates conda environment
3. Queries all enabled databases (PubMed, Scopus, WOS)
4. Auto-detects Embase imports
5. Deduplicates results by DOI
6. Evaluates query performance
7. Aggregates queries
8. Scores aggregated sets

### Running the Full Workflow

**Basic command**:
```bash
# Run with default databases (from .env file)
./run_workflow_sleep_apnea.sh
```

**Override databases via environment variable**:
```bash
# Run specific databases (overrides .env)
DATABASES="pubmed,scopus,wos" ./run_workflow_sleep_apnea.sh
```

**Available database names**:
- `pubmed` - PubMed (NCBI Entrez)
- `scopus` - Scopus (Elsevier)
- `wos` or `web_of_science` - Web of Science (Clarivate)

**Database Flags Explained**:

```bash
# The script automatically forwards these from .env to the Python script:
--databases pubmed,scopus,wos          # Which databases to query
--scopus-api-key YOUR_KEY              # Scopus API key
--scopus-insttoken YOUR_TOKEN          # Optional institution token
--scopus-skip-date-filter              # Skip date filtering (recommended)
--wos-api-key YOUR_KEY                 # Web of Science API key
```

### What Happens During Execution

**Phase 1: Query Evaluation and Selection**

The script runs three commands sequentially:

**Command 1: Select** (Heuristic-based selection)
```bash
python llm_sr_select_and_score.py \
    --study-name sleep_apnea \
    --databases pubmed,scopus,wos \
    select \
    --concept-terms concept_terms_sleep_apnea.csv \
    --queries-txt queries.txt \
    --outdir sealed_outputs
```

**What it does**:
- Uses heuristics to choose the "best" query WITHOUT gold standard
- Analyzes query characteristics (term counts, specificity, etc.)
- Creates a "sealed" recommendation
- Output: `sealed_outputs/sleep_apnea/sealed_TIMESTAMP.json`

**When to use**: When you don't have a gold standard yet, or for blind validation.

---

**Command 2: Score** (Benchmark all queries)
```bash
python llm_sr_select_and_score.py \
    --study-name sleep_apnea \
    --databases pubmed,scopus,wos \
    score \
    --queries-txt queries.txt \
    --gold-csv gold_pmids_sleep_apnea.csv \
    --outdir benchmark_outputs
```

**What it does**:
- Executes all queries across all databases
- Deduplicates by DOI for each query
- Calculates precision, recall, F1 against gold standard
- Creates detailed and summary reports

**Outputs**:
- `benchmark_outputs/sleep_apnea/details_TIMESTAMP.json` - Full results with DOIs/PMIDs
- `benchmark_outputs/sleep_apnea/summary_TIMESTAMP.csv` - Performance metrics

**Example output**:
```
Query 1 (High-recall):
  Retrieved: 1850 articles
  True Positives: 11/11 (100% recall)
  Precision: 0.59%
  F1-score: 0.012

Query 3 (High-precision):
  Retrieved: 237 articles
  True Positives: 5/11 (45% recall)
  Precision: 2.1%
  F1-score: 0.040
```

---

**Command 3: Finalize** (Validate sealed selection)
```bash
python llm_sr_select_and_score.py \
    --study-name sleep_apnea \
    --databases pubmed,scopus,wos \
    finalize \
    --sealed sealed_outputs/sleep_apnea/sealed_TIMESTAMP.json \
    --gold-csv gold_pmids_sleep_apnea.csv
```

**What it does**:
- Takes the heuristically-selected "best" query
- Scores it against gold standard
- Validates whether heuristics matched actual performance

**Output**: `final_outputs/sleep_apnea/final_TIMESTAMP.json`

---

**Phase 2: Query Aggregation**

The script automatically detects Embase files:

```bash
# Check for manually imported Embase results
EMBASE_FILES=()

# Check for single Embase result file
if [ -f "studies/$STUDY_NAME/embase_results.json" ]; then
    EMBASE_FILES+=("studies/$STUDY_NAME/embase_results.json")
fi

# Check for batch-imported Embase queries
for file in studies/$STUDY_NAME/embase_query*.json; do
    if [ -f "$file" ]; then
        EMBASE_FILES+=("$file")
    fi
done
```

Then runs aggregation:

```bash
python scripts/aggregate_queries.py \
    --inputs benchmark_outputs/sleep_apnea/details_*.json \
             studies/sleep_apnea/embase_query*.json \
    --outdir aggregates/sleep_apnea
```

**What it does**:
- Takes all query results (PubMed, Scopus, WOS, Embase)
- Creates multiple aggregation strategies:
  - **consensus_k2.txt**: Articles found by ≥2 queries
  - **consensus_k3.txt**: Articles found by ≥3 queries
  - **precision_gated_union.txt**: Union with precision threshold
  - **weighted_vote.txt**: Weighted by query performance
  - **two_stage_screen.txt**: High-precision first, then high-recall
  - **time_stratified_hybrid.txt**: Newer articles from precision, older from recall

**Output**: Text files with PMIDs, one per line

---

**Phase 3: Score Aggregated Sets**

```bash
python llm_sr_select_and_score.py \
    --study-name sleep_apnea \
    --databases pubmed,scopus,wos \
    score-sets \
    --sets aggregates/sleep_apnea/*.txt \
    --gold-csv gold_pmids_sleep_apnea.csv \
    --outdir aggregates_eval
```

**What it does**:
- Evaluates each aggregation strategy
- Calculates precision, recall, F1 for each set
- Creates summary CSV and detailed JSON

**Outputs**:
- `aggregates_eval/sleep_apnea/sets_summary_TIMESTAMP.csv`
- `aggregates_eval/sleep_apnea/sets_details_TIMESTAMP.json`

**Example output**:
```
Set[consensus_k2]: n=72 TP=3 Precision=0.042 Recall=0.273 F1=0.072
Set[precision_gated_union]: n=1961 TP=11 Precision=0.006 Recall=1.000 F1=0.011
Set[weighted_vote]: n=1961 TP=11 Precision=0.006 Recall=1.000 F1=0.011
```

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

## Step 9: Understanding the Outputs

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

# 6. Run full workflow (includes Embase automatically)
DATABASES="pubmed,scopus,wos" ./run_workflow_sleep_apnea.sh

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

# 2. Run complete Embase workflow (import + re-aggregate + re-score)
bash scripts/complete_embase_workflow.sh

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
DATABASES="pubmed" ./run_workflow_sleep_apnea.sh
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

**Cause**: Space after comma in `.env` file:
```bash
# WRONG
SR_DATABASES=pubmed, scopus

# Bash tries to execute " scopus" as a command
```

**Solution**: Remove spaces:
```bash
# CORRECT
SR_DATABASES=pubmed,scopus
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
│  │        2. Import Embase (batch_import_embase.py)
│  │        3. Run full workflow (run_workflow_sleep_apnea.sh)
│  │
│  └─ No → Use Method 2
│           1. Run full workflow first
│           2. Export Embase later
│           3. Run complete_embase_workflow.sh
│
└─ No
   │
   Which databases do you have access to?
   │
   ├─ PubMed only (free)
   │  → DATABASES="pubmed" ./run_workflow_sleep_apnea.sh
   │
   ├─ PubMed + Scopus
   │  → DATABASES="pubmed,scopus" ./run_workflow_sleep_apnea.sh
   │
   └─ PubMed + Scopus + WOS
      → DATABASES="pubmed,scopus,wos" ./run_workflow_sleep_apnea.sh
```

---

### Quick Reference Commands

```bash
# Complete workflow (automated databases + auto-detect Embase)
DATABASES="pubmed,scopus,wos" ./run_workflow_sleep_apnea.sh

# Import single Embase query
python scripts/import_embase_manual.py -i query.csv -o query.json -q "query text"

# Batch import Embase queries
python scripts/batch_import_embase.py --study STUDY --csvs *.csv --queries-file queries_embase.txt

# Complete Embase workflow (import + aggregate + score)
bash scripts/complete_embase_workflow.sh

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
