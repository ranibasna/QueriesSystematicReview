# Complete Workflow Guide: lang_2024 Study

**Study:** lang_2024  
**Date Started:** 23 January 2026  
**Status:** Ready to begin

---

## 📋 Pre-Flight Checklist

- [x] PDFs in place:
  - `Lange 2024 - Paper.pdf`
  - `Lange 2024 - PROSPERO.pdf`
- [ ] Conda environments ready
- [ ] API keys configured in `.env`
- [ ] Main environment activated

---

## 🚀 STEP 1: Convert PDFs to Markdown

**Purpose:** Convert raw PDF files to markdown format for LLM processing.

**Prerequisites:**
- ✅ PDFs exist in `studies/lang_2024/`
- ✅ Docling conda environment installed

### Commands

```bash
# 1. Activate main environment
conda activate systematic_review_queries

# 2. Navigate to project root (if not already there)
cd /Users/ra1077ba/Documents/DataScience/GU/Daniil/LLM/QueriesSystematicReview

# 3. Run PDF conversion script
python scripts/prepare_study.py lang_2024 --docling-env docling
```

### Expected Output Files

After completion, you should have:
```
studies/lang_2024/
├── Lange 2024 - Paper.pdf
├── Lange 2024 - PROSPERO.pdf
├── paper_lang_2024.md          ← NEW
└── prospero_lang_2024.md       ← NEW
```

### Verification

```bash
# Check files were created
ls -lh studies/lang_2024/*.md

# Preview PROSPERO markdown (first 50 lines)
head -50 studies/lang_2024/prospero_lang_2024.md

# Preview Paper markdown (first 50 lines)
head -50 studies/lang_2024/paper_lang_2024.md
```

### What This Does

1. **Activates docling environment** (specialized for PDF processing)
2. **Scans study directory** for PDF files
3. **Converts each PDF:**
   - Extracts text, tables, figures
   - Preserves formatting (headings, lists, references)
   - Converts to markdown syntax
4. **Returns to main environment**

### Troubleshooting

**If conversion fails:**
```bash
# Check if docling environment exists
conda env list | grep docling

# If missing, create it:
conda create -n docling python=3.11
conda activate docling
pip install docling
conda deactivate
```

---

## 🔍 STEP 2: Generate LLM Query Generation Command

**Purpose:** Create an executable LLM command that will generate database-specific search queries.

**Prerequisites:**
- ✅ Markdown files from STEP 1 completed
- ✅ You've reviewed the PROSPERO protocol to understand:
  - Research question
  - Date range of literature search
  - Study design

### Key Decisions to Make

Before running this command, you need to decide:

1. **Databases to include:** 
   - Recommended: `pubmed,scopus,wos,embase`
   - Minimum: `pubmed`

2. **Query complexity level:**
   - `basic` = 3 queries/database
   - `extended` = 6 queries/database ← **RECOMMENDED**
   - `keywords` = 4 queries/database
   - `exhaustive` = 9 queries/database

3. **Date range:**
   - Check PROSPERO protocol for search dates
   - Format: YYYY/MM/DD

### Command Template

```bash
/generate_multidb_prompt \
  --command_name run_lang_2024_multidb_extended \
  --protocol_path studies/lang_2024/prospero_lang_2024.md \
  --databases pubmed,scopus,wos,embase \
  --level extended \
  --min_date "1990/01/01" \
  --max_date "2024/12/31"
```

### Parameter Explanations

| Parameter | Value | Reasoning |
|-----------|-------|-----------|
| `--command_name` | `run_lang_2024_multidb_extended` | Name becomes `/run_lang_2024_multidb_extended` |
| `--protocol_path` | `studies/lang_2024/prospero_lang_2024.md` | Path to PROSPERO markdown from STEP 1 |
| `--databases` | `pubmed,scopus,wos,embase` | All 4 databases (NO SPACES!) |
| `--level` | `extended` | 6 queries per database (recommended) |
| `--min_date` | `"1990/01/01"` | **ADJUST BASED ON PROSPERO** |
| `--max_date` | `"2024/12/31"` | **ADJUST BASED ON PROSPERO** |

### Action Required: Review PROSPERO for Dates

```bash
# Open PROSPERO markdown and find the date range
grep -i "date" studies/lang_2024/prospero_lang_2024.md | head -20

# Look for phrases like:
# - "from inception to..."
# - "January 2020 to December 2023"
# - "up to March 2024"
```

**Adjust `--min_date` and `--max_date` accordingly!**

### What This Does

1. **Reads template files:**
   - `prompts/prompt_template_multidb.md`
   - `prompts/database_guidelines.md`
   - `studies/lang_2024/prospero_lang_2024.md`

2. **Extracts protocol information:**
   - Research question
   - PICOS elements (Population, Intervention, Comparator, Outcomes, Study design)
   - Keywords

3. **Builds complete prompt:**
   - Inserts protocol info
   - Inserts database-specific syntax rules
   - Inserts level-specific instructions (extended = 6 queries)

4. **Creates command file:**
   - Saves to: `run_lang_2024_multidb_extended.toml`
   - Ready to execute via: `/run_lang_2024_multidb_extended`

### Expected Output

```
✅ Command created successfully!

Generated file:
  • run_lang_2024_multidb_extended.toml

To generate queries, run:
  /run_lang_2024_multidb_extended

This will create:
  • studies/lang_2024/queries.txt (6 PubMed queries)
  • studies/lang_2024/queries_scopus.txt (6 Scopus queries)
  • studies/lang_2024/queries_wos.txt (6 WOS queries)
  • studies/lang_2024/queries_embase.txt (6 Embase queries)
```

---

## 🤖 STEP 3: Run LLM Command to Generate Queries

**Purpose:** Use LLM to automatically generate optimized database-specific queries.

**Prerequisites:**
- ✅ Command file from STEP 2 exists
- ✅ LLM tool available (Claude Desktop, Gemini CLI, etc.)

### Command

```bash
/run_lang_2024_multidb_extended
```

### What Happens

1. **LLM receives the complete prompt** (from STEP 2) containing:
   - Your PROSPERO protocol
   - Database-specific syntax rules
   - Instructions to generate 6 queries per database

2. **LLM generates queries** for each database:
   - Query 1: High-recall (broad, maximize sensitivity)
   - Query 2: Balanced (mix of controlled vocab + free text)
   - Query 3: High-precision (focused, maximize specificity)
   - Query 4: Filter variant (adds filters to Query 2)
   - Query 5: Scope variant (adjusts field scope)
   - Query 6: Proximity variant (adds proximity operators)

3. **System saves query files:**
   - `studies/lang_2024/queries.txt` (PubMed)
   - `studies/lang_2024/queries_scopus.txt` (Scopus)
   - `studies/lang_2024/queries_wos.txt` (Web of Science)
   - `studies/lang_2024/queries_embase.txt` (Embase)

### Expected Output Structure

Each query file should look like this:

```
studies/lang_2024/queries.txt:
-----------------------------------------
Query 1: High-recall
("sleep apnea"[MeSH Terms] OR "sleep apnea"[tiab] OR OSA[tiab]) AND (dementia[MeSH Terms] OR dementia[tiab])

Query 2: Balanced
("Sleep Apnea, Obstructive"[Mesh] OR "sleep apnea"[tiab]) AND ("Dementia"[Mesh] OR dementia[tiab] OR "cognitive decline"[tiab]) AND (cohort[tiab] OR "prospective"[tiab])

Query 3: High-precision
"Sleep Apnea Syndromes"[Mesh:NoExp] AND "Dementia"[Mesh:NoExp] AND (cohort[tiab] OR prospective[tiab])

Query 4: Filter variant (Query 2 + filters)
[Similar to Query 2 but with additional study design filters]

Query 5: Scope variant
[Similar to Query 2 but with adjusted field tags]

Query 6: Proximity variant
[Similar to Query 2 but with proximity operators like NEAR/5]
```

### Verification

```bash
# Check all query files were created
ls -lh studies/lang_2024/queries*.txt

# Count queries in each file (should be 6)
grep -c "^Query [0-9]:" studies/lang_2024/queries.txt
grep -c "^Query [0-9]:" studies/lang_2024/queries_scopus.txt
grep -c "^Query [0-9]:" studies/lang_2024/queries_wos.txt
grep -c "^Query [0-9]:" studies/lang_2024/queries_embase.txt

# Preview PubMed queries
cat studies/lang_2024/queries.txt
```

---

## 📤 STEP 4: Manual Embase Export (Manual Process)

**Purpose:** Export Embase results manually since Embase doesn't provide API access.

**Time Required:** 10-30 minutes (depends on Embase interface speed)

### Prerequisites

- ✅ Embase queries generated in STEP 3
- ✅ Institutional access to Embase database
- ✅ Directory created: `studies/lang_2024/embase_manual_queries/`

### Create Directory

```bash
# Create directory for Embase exports
mkdir -p studies/lang_2024/embase_manual_queries
```

### Process

1. **Open Embase query file:**
   ```bash
   cat studies/lang_2024/queries_embase.txt
   ```

2. **For each query (1-6):**
   
   **a) Log into Embase** via your institution
   
   **b) Copy query text** (excluding "Query N:" label)
   
   **c) Paste into Embase search box** and execute
   
   **d) Export results as CSV:**
   - Select: "Title", "Authors", "Publication Year", "DOI", "PubMed ID"
   - Format: CSV
   - Save as: `embase_query1.csv`, `embase_query2.csv`, etc.
   
   **e) Move CSV to study directory:**
   ```bash
   mv ~/Downloads/embase_query1.csv studies/lang_2024/embase_manual_queries/
   ```

3. **Repeat for all 6 queries**

### Expected Directory Structure After Completion

```
studies/lang_2024/embase_manual_queries/
├── embase_query1.csv
├── embase_query2.csv
├── embase_query3.csv
├── embase_query4.csv
├── embase_query5.csv
└── embase_query6.csv
```

### Verification

```bash
# Check all 6 CSV files exist
ls -lh studies/lang_2024/embase_manual_queries/

# Count total records across all files (excluding headers)
wc -l studies/lang_2024/embase_manual_queries/*.csv

# Preview first file
head -5 studies/lang_2024/embase_manual_queries/embase_query1.csv
```

### Important Notes

- **File naming is critical:** Must be exactly `embase_query1.csv` through `embase_query6.csv`
- **Column names must include:** At minimum "Title" and either "DOI" or "PubMed ID"
- **Encoding:** UTF-8 (default for most modern CSV exports)

---

## 🏆 STEP 5: Create Gold Standard PMID List

**Purpose:** Create a list of PMIDs for articles that were included in the final systematic review (the "gold standard" for evaluation).

**Time Required:** 5-30 minutes (depends on availability of supplementary data)

### Method 1: Extract from Supplementary Materials (Preferred)

Many systematic reviews publish their included studies as supplementary files.

```bash
# If you have a supplementary CSV/Excel file with included studies
# Look for columns like: PMID, PubMed ID, DOI, Title

# Example: If you have included_studies.csv
# Extract PMIDs and save to gold standard file
```

**Manual extraction if needed:**

1. **Open the paper markdown:**
   ```bash
   cat studies/lang_2024/paper_lang_2024.md | less
   ```

2. **Look for:**
   - Supplementary materials section
   - References section
   - Results section with study counts

3. **Create gold PMID list:**
   ```bash
   # Create file with header
   echo "pmid" > studies/lang_2024/gold_pmids_lang_2024.csv
   
   # Add PMIDs (one per line)
   echo "12345678" >> studies/lang_2024/gold_pmids_lang_2024.csv
   echo "23456789" >> studies/lang_2024/gold_pmids_lang_2024.csv
   # ... continue for all included studies
   ```

### Method 2: Use Automated Extraction Script

If the paper has DOIs or titles of included studies:

```bash
# Run extraction script (if available)
python scripts/extract_gold_pmids.py \
  --paper studies/lang_2024/paper_lang_2024.md \
  --output studies/lang_2024/gold_pmids_lang_2024.csv
```

### Expected File Format

```csv
pmid
12345678
23456789
34567890
45678901
```

**Format Requirements:**
- CSV file with header row: `pmid`
- One PMID per line
- No quotes, no extra columns
- File name: `gold_pmids_lang_2024.csv`

### Verification

```bash
# Check file exists and has correct format
cat studies/lang_2024/gold_pmids_lang_2024.csv

# Count PMIDs (excluding header)
tail -n +2 studies/lang_2024/gold_pmids_lang_2024.csv | wc -l

# Validate PMIDs are numeric
tail -n +2 studies/lang_2024/gold_pmids_lang_2024.csv | grep -v "^[0-9]*$" || echo "All PMIDs valid"
```

### Typical PMID Counts

- Small focused reviews: 15-30 PMIDs
- Medium reviews: 30-80 PMIDs
- Large comprehensive reviews: 80-200 PMIDs

---

## 🎯 STEP 6: Run Complete Multi-Database Workflow

**Purpose:** Execute all queries across all databases, deduplicate results, evaluate performance, and generate aggregation strategies.

**Time Required:** 15-30 minutes (automated, depends on API rate limits)

**Prerequisites:**
- ✅ Query files exist (STEP 3)
- ✅ Embase CSVs exported (STEP 4)
- ✅ Gold standard created (STEP 5)
- ✅ API keys configured in `.env`

### Pre-Flight Check

```bash
# 1. Verify all required files exist
ls -lh studies/lang_2024/queries*.txt
ls -lh studies/lang_2024/embase_manual_queries/*.csv
ls -lh studies/lang_2024/gold_pmids_lang_2024.csv

# 2. Activate environment
conda activate systematic_review_queries

# 3. Navigate to project root
cd /Users/ra1077ba/Documents/DataScience/GU/Daniil/LLM/QueriesSystematicReview
```

### The Main Command

```bash
./run_workflow.sh lang_2024
```

### What This Does: Complete Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Query Execution (5-10 min)                         │
├─────────────────────────────────────────────────────────────┤
│ For each database (PubMed, Scopus, WOS):                   │
│   For each query (1-6):                                     │
│     • Execute query via API                                 │
│     • Fetch article metadata (title, DOI, PMID, year)      │
│     • Save raw results                                      │
│                                                              │
│ For Embase:                                                 │
│   • Import pre-exported CSVs                                │
│   • Parse and standardize format                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Deduplication (1-2 min)                           │
├─────────────────────────────────────────────────────────────┤
│ • Normalize DOIs (remove URLs, lowercase)                  │
│ • Merge duplicate articles across databases using DOI      │
│ • Track source databases for each unique article           │
│ • Preserve all metadata                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Query Evaluation (1-2 min)                        │
├─────────────────────────────────────────────────────────────┤
│ For each query:                                             │
│   • Calculate Precision: (true_positives / total_results)  │
│   • Calculate Recall: (true_positives / gold_standard)     │
│   • Calculate F1-score: harmonic mean of P & R             │
│   • Generate confusion matrix                              │
│   • Rank queries by performance                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Strategy Aggregation (2-5 min)                    │
├─────────────────────────────────────────────────────────────┤
│ Generate 5 aggregation strategies:                         │
│                                                              │
│ 1. consensus_k2: Articles in ≥2 queries                   │
│ 2. precision_gated_union: Union of high-precision queries  │
│ 3. time_stratified_hybrid: Recent + historical balance     │
│ 4. two_stage_screen: High-recall → precision filter       │
│ 5. weighted_vote: Confidence scoring system                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Strategy Evaluation (1-2 min)                     │
├─────────────────────────────────────────────────────────────┤
│ For each strategy:                                          │
│   • Calculate final Precision, Recall, F1                  │
│   • Count total unique PMIDs                               │
│   • Rank strategies                                         │
│   • Generate comparison report                              │
└─────────────────────────────────────────────────────────────┘
```

### Expected Console Output

```
═══════════════════════════════════════════════════════════════
  Multi-Database Systematic Review Workflow: lang_2024
═══════════════════════════════════════════════════════════════

[Phase 1/5] Query Execution
────────────────────────────────────────────────────────────────
Executing PubMed queries...
  ✓ Query 1: 2,847 results
  ✓ Query 2: 1,523 results
  ✓ Query 3: 892 results
  ✓ Query 4: 1,205 results
  ✓ Query 5: 1,398 results
  ✓ Query 6: 1,156 results

Executing Scopus queries...
  ✓ Query 1: 3,124 results
  ✓ Query 2: 1,687 results
  ✓ Query 3: 945 results
  ✓ Query 4: 1,334 results
  ✓ Query 5: 1,512 results
  ✓ Query 6: 1,267 results

Executing WOS queries...
  ✓ Query 1: 2,956 results
  ✓ Query 2: 1,601 results
  ✓ Query 3: 901 results
  ✓ Query 4: 1,278 results
  ✓ Query 5: 1,445 results
  ✓ Query 6: 1,189 results

Importing Embase results...
  ✓ Query 1: 3,201 results (embase_query1.csv)
  ✓ Query 2: 1,734 results (embase_query2.csv)
  ✓ Query 3: 978 results (embase_query3.csv)
  ✓ Query 4: 1,389 results (embase_query4.csv)
  ✓ Query 5: 1,567 results (embase_query5.csv)
  ✓ Query 6: 1,298 results (embase_query6.csv)

[Phase 2/5] Deduplication
────────────────────────────────────────────────────────────────
Processing 28,456 total article records...
  • Found 18,234 unique DOIs
  • Merged 10,222 duplicates
  • Final unique articles: 18,234

[Phase 3/5] Query Evaluation
────────────────────────────────────────────────────────────────
Loading gold standard: 42 PMIDs
Evaluating 24 queries (4 databases × 6 queries)...

Top performing queries:
  1. pubmed_query2 (Balanced): P=0.042, R=0.952, F1=0.080
  2. scopus_query4 (Filter): P=0.039, R=0.929, F1=0.075
  3. wos_query2 (Balanced): P=0.041, R=0.905, F1=0.078

[Phase 4/5] Strategy Aggregation
────────────────────────────────────────────────────────────────
Generating 5 aggregation strategies...
  ✓ consensus_k2: 3,456 PMIDs
  ✓ precision_gated_union: 1,704 PMIDs
  ✓ time_stratified_hybrid: 2,890 PMIDs
  ✓ two_stage_screen: 2,123 PMIDs
  ✓ weighted_vote: 2,567 PMIDs

[Phase 5/5] Strategy Evaluation
────────────────────────────────────────────────────────────────
Evaluating strategies against gold standard...

╔════════════════════════════════════════════════════════════╗
║                FINAL STRATEGY RANKINGS                      ║
╠════════════════════════════════════════════════════════════╣
║ Rank │ Strategy              │ PMIDs │ Recall │ Precision ║
╠══════╪═══════════════════════╪═══════╪════════╪═══════════╣
║  1   │ precision_gated_union │ 1,704 │ 100.0% │   2.47%  ║
║  2   │ weighted_vote         │ 2,567 │ 100.0% │   1.64%  ║
║  3   │ two_stage_screen      │ 2,123 │  97.6% │   1.93%  ║
║  4   │ time_stratified       │ 2,890 │  97.6% │   1.42%  ║
║  5   │ consensus_k2          │ 3,456 │  95.2% │   1.16%  ║
╚══════╧═══════════════════════╧═══════╧════════╧═══════════╝

🏆 BEST STRATEGY: precision_gated_union
   → Achieves 100% recall with 1,704 PMIDs to screen

✅ Workflow complete!

Output directories:
  • benchmark_outputs/lang_2024/    (Query performance metrics)
  • aggregates/lang_2024/           (Strategy PMID lists)
  • aggregates_eval/lang_2024/      (Strategy performance metrics)
```

### Output Directory Structure

```
studies/lang_2024/
├── benchmark_outputs/
│   └── lang_2024/
│       ├── summary_TIMESTAMP.csv          # Query performance summary
│       └── details_TIMESTAMP.json         # Detailed query results
├── aggregates/
│   └── lang_2024/
│       ├── consensus_k2.txt               # Strategy 1 PMIDs
│       ├── precision_gated_union.txt      # Strategy 2 PMIDs
│       ├── time_stratified_hybrid.txt     # Strategy 3 PMIDs
│       ├── two_stage_screen.txt           # Strategy 4 PMIDs
│       └── weighted_vote.txt              # Strategy 5 PMIDs
└── aggregates_eval/
    └── lang_2024/
        ├── strategy_performance.csv       # Strategy comparison
        └── strategy_details.json          # Detailed metrics
```

### Interpreting Results

**Key Metrics:**
- **Recall:** % of gold standard PMIDs found (want 95-100%)
- **Precision:** % of results that are relevant (higher = less screening)
- **F1-score:** Harmonic mean of precision and recall
- **PMIDs:** Total articles to screen (lower = less work)

**Best Strategy Selection:**
- If recall ≥ 95%: Choose strategy with highest precision (fewest PMIDs)
- If all strategies have 100% recall: Choose smallest PMID count
- `precision_gated_union` typically wins: high recall, moderate precision

---

## 📊 STEP 7: Cross-Study Validation (Optional, After ≥2 Studies)

**Purpose:** Meta-analyze performance across multiple studies to identify which aggregation strategies work best across different medical domains.

**When to Run:** After completing ≥2 studies (e.g., lang_2024 + Godos_2024)

**Time Required:** 2-5 minutes

### Prerequisites

- ✅ Completed STEP 6 for ≥2 studies
- ✅ Each study has:
  - `benchmark_outputs/<study>/`
  - `aggregates_eval/<study>/`

### Command

```bash
# Navigate to cross-study validation module
cd cross_study_validation

# Run meta-analysis
python -m cross_study_validation

# Or run specific analysis
python -m cross_study_validation.analysis.meta_analysis
```

### What This Does

1. **Collects data from all studies:**
   - Query performance metrics
   - Strategy performance metrics
   - Gold standard statistics

2. **Standardizes formats:**
   - Normalizes column names
   - Converts to unified schema
   - Validates data integrity

3. **Performs meta-analysis:**
   - Average recall/precision across studies
   - Strategy consistency analysis
   - Domain-specific performance patterns

4. **Generates reports:**
   - HTML visualizations
   - CSV summary tables
   - Strategy recommendations

### Expected Output

```
cross_study_validation/
├── data/                              # Standardized JSON data
│   ├── lang_2024.json
│   ├── Godos_2024.json
│   └── ...
└── reports/                           # Analysis reports
    ├── meta_analysis.html             # Interactive dashboard
    ├── strategy_rankings.csv          # Cross-study rankings
    └── domain_insights.html           # Domain-specific patterns
```

### Sample Insights

**Example meta_analysis.html content:**

```
Cross-Study Strategy Performance (n=3 studies)

Average Recall:
  1. precision_gated_union:  98.7% (±1.2%)
  2. weighted_vote:          97.9% (±2.1%)
  3. two_stage_screen:       96.4% (±3.4%)

Average PMIDs to Screen:
  1. precision_gated_union:  1,850 (±450)
  2. two_stage_screen:       2,200 (±520)
  3. weighted_vote:          2,650 (±680)

Recommendation:
  precision_gated_union is the most consistent strategy
  across multiple medical domains, achieving high recall
  (>95%) while minimizing screening burden.
```

---

## ✅ Workflow Completion Checklist

### Files Created

- [ ] `studies/lang_2024/paper_lang_2024.md`
- [ ] `studies/lang_2024/prospero_lang_2024.md`
- [ ] `studies/lang_2024/queries.txt`
- [ ] `studies/lang_2024/queries_scopus.txt`
- [ ] `studies/lang_2024/queries_wos.txt`
- [ ] `studies/lang_2024/queries_embase.txt`
- [ ] `studies/lang_2024/embase_manual_queries/` (6 CSV files)
- [ ] `studies/lang_2024/gold_pmids_lang_2024.csv`
- [ ] `studies/lang_2024/benchmark_outputs/`
- [ ] `studies/lang_2024/aggregates/`
- [ ] `studies/lang_2024/aggregates_eval/`

### Key Results

- [ ] All 6 queries executed per database
- [ ] Deduplication completed successfully
- [ ] Gold standard validation performed
- [ ] Strategy performance evaluated
- [ ] Best strategy identified

### Next Steps

1. **Review best strategy PMIDs:**
   ```bash
   cat studies/lang_2024/aggregates/lang_2024/precision_gated_union.txt
   ```

2. **Export for screening:**
   ```bash
   # Copy PMIDs to screening tool (Covidence, Rayyan, etc.)
   cat studies/lang_2024/aggregates/lang_2024/precision_gated_union.txt | pbcopy
   ```

3. **Run cross-study validation:**
   ```bash
   cd cross_study_validation
   python -m cross_study_validation
   ```

---

## 🛠️ Troubleshooting Quick Reference

### Issue: PDF Conversion Fails

```bash
# Check docling environment
conda activate docling
python -c "import docling; print('OK')"
conda deactivate

# Re-install if needed
conda create -n docling python=3.11 -y
conda activate docling
pip install docling
```

### Issue: API Rate Limits

```bash
# Add delays in .env
echo "PUBMED_REQUEST_DELAY=0.5" >> .env
echo "SCOPUS_REQUEST_DELAY=1.0" >> .env
```

### Issue: Missing Gold Standard PMIDs

```bash
# Manually create file
echo "pmid" > studies/lang_2024/gold_pmids_lang_2024.csv
# Add PMIDs from paper's supplementary materials
```

### Issue: Embase Import Fails

```bash
# Check file names (must be exact!)
ls studies/lang_2024/embase_manual_queries/

# Correct naming:
# embase_query1.csv, embase_query2.csv, ..., embase_query6.csv

# Check CSV format (must have header row)
head -1 studies/lang_2024/embase_manual_queries/embase_query1.csv
```

### Issue: Deduplication Errors

```bash
# Check DOI format in results
# DOIs should be normalized (lowercase, no URL prefix)

# Run manual validation
python scripts/validate_dois.py studies/lang_2024/
```

---

## 📝 Notes and Observations

### Space for Your Notes

```
Study characteristics:
  • Research domain: [e.g., cardiology, neurology]
  • Number of included studies in SR: 
  • Date range: 
  • Databases searched in original: 

Performance observations:
  • Best performing query: 
  • Best aggregation strategy: 
  • Total unique PMIDs: 
  • Gold standard recall achieved: 

Challenges encountered:
  • 
  • 

Time spent:
  • STEP 1 (PDF conversion): 
  • STEP 2-3 (Query generation): 
  • STEP 4 (Embase export): 
  • STEP 5 (Gold standard): 
  • STEP 6 (Full workflow): 
  • TOTAL: 
```

---

## 🎓 Summary

This workflow automates ~85% of the systematic review search process:

**Automated:**
- ✅ PDF → Markdown conversion
- ✅ LLM-powered query generation (4 databases × 6 queries = 24 queries)
- ✅ API-based search execution (PubMed, Scopus, WOS)
- ✅ DOI-based deduplication
- ✅ Performance evaluation
- ✅ Strategy aggregation
- ✅ Cross-study meta-analysis

**Manual (but guided):**
- 📝 Embase export (10-30 min)
- 📝 Gold standard creation (5-30 min)
- 📝 Reviewing PROSPERO for date ranges (2-5 min)

**Total time investment:** 45-90 minutes per study

**Expected result:** Best aggregation strategy achieving 95-100% recall with optimized screening workload.

---

**Ready to begin? Start with STEP 1!**
