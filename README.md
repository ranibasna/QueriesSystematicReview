# LLM-Assisted Multi-Database Systematic Review Automation

**An end-to-end automated workflow for systematic literature reviews across PubMed, Scopus, Web of Science, and Embase.**

This repository provides tools to:
- 🤖 **Generate database-specific queries** using LLM from PROSPERO protocols
- 🔍 **Execute searches** across 4+ major databases with automatic API integration
- 🔄 **Deduplicate results** using DOI-based matching (~96% coverage)
- 📊 **Benchmark performance** against gold standard PMID lists
- 🎯 **Aggregate strategies** to optimize precision and recall
- ⚡ **Complete automation** from raw PDFs to final results in ~45-90 minutes

## 📚 Documentation

- **[Complete Pipeline Guide](Documentations/complete_pipeline_guide.md)** - Comprehensive technical walkthrough of all steps
- **[Automation Guide](Documentations/AUTOMATION_GUIDE.md)** - End-to-end workflow from raw PDFs to results
- **[Multi-Database Deduplication](Documentations/multi_database_deduplication_complete.md)** - DOI-based deduplication design

## 🚀 Quick Start

### One-Command Workflow
```bash
# Run complete workflow for a study
bash scripts/run_complete_workflow.sh Godos_2024 --databases pubmed,scopus,wos
```

### Core Commands
- **select**: Evaluate candidate queries without gold standard
- **score**: Benchmark queries against gold standard PMID list
- **finalize**: Add gold standard metrics to sealed results
- **score-sets**: Evaluate aggregation strategies
- **print-titles**: Fetch metadata for PMIDs

## 🛠️ Environment Setup

### 1. Install Conda and Clone Repository

```zsh
# Install Miniconda (if not already installed)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh

# Clone repository
git clone https://github.com/ranibasna/QueriesSystematicReview.git
cd QueriesSystematicReview
```

### 2. Create Conda Environments

**Main environment** (for systematic review workflow):
```zsh
conda env create -f environment.yml
conda activate systematic_review_queries
# Update later if needed
conda env update -f environment.yml --prune
```

**Docling environment** (for PDF conversion):
```zsh
conda create -n docling python=3.11
conda activate docling
pip install docling
conda deactivate
```

### 3. Configure API Keys

⚠️ **SECURITY IMPORTANT**: Never commit API keys to version control!

Create a `.env` file in the project root (this file is git-ignored):

```bash
# .env file
# PubMed (free, but API key increases rate limit)
NCBI_EMAIL=your.email@institution.edu
NCBI_API_KEY=your_ncbi_api_key_optional

# Scopus (requires institutional subscription)
SCOPUS_API_KEY=your_scopus_api_key
SCOPUS_INSTTOKEN=your_institution_token_optional
SCOPUS_SKIP_DATE_FILTER=true

# Web of Science (requires institutional subscription)
WOS_API_KEY=your_wos_api_key

# Multi-database configuration (no spaces after commas!)
SR_DATABASES=pubmed,scopus,wos
```

**Where to get API keys:**
- **PubMed**: https://www.ncbi.nlm.nih.gov/account/settings/ (free)
- **Scopus**: Contact your institution's library
- **WOS**: Contact your institution's library

**Important Notes:**
- ✅ `.env` is in `.gitignore` and will NOT be committed
- ✅ `sr_config.toml` is in `.gitignore` and will NOT be committed
- ❌ Never hardcode API keys in Python files
- ✅ Use environment variables or config files only
- 📋 See [SECURITY_AUDIT.md](SECURITY_AUDIT.md) for security review

## 📋 Complete Workflow: From PDFs to Results

This workflow takes ~45-90 minutes per study (30-40 min automated, 15-50 min manual Embase).

### STEP 1: Convert PDFs to Markdown (5 min, automated)
```bash
python scripts/prepare_study.py Godos_2024 --docling-env docling
```

### STEP 2: Generate LLM Command (2 min, automated)
```bash
/generate_multidb_prompt \
  --command_name run_godos_2024_multidb_extended \
  --protocol_path studies/Godos_2024/prospero_godos_2024.md \
  --databases pubmed,scopus,wos,embase \
  --level extended \
  --min_date "1990/01/01" \
  --max_date "2023/12/31"
```

### STEP 3: Run LLM Command to Generate Queries (5 min, automated)
```bash
/run_godos_2024_multidb_extended
```
This creates:
- `queries.txt` (6 PubMed queries)
- `queries_scopus.txt` (6 Scopus queries)
- `queries_wos.txt` (6 WOS queries)
- `queries_embase.txt` (6 Embase queries)

### STEP 4: Export Embase Results (10-30 min, manual)
1. Go to Embase.com
2. Run each query from `queries_embase.txt`
3. Export results as CSV
4. Place in `studies/Godos_2024/embase_manual_queries/`

### STEP 5: Create Gold Standard (5-30 min, semi-automated)
```bash
python scripts/validate_pmids_multi_source.py \
  --study-name Godos_2024 \
  --paper studies/Godos_2024/paper_godos_2024.md
```

### STEP 6: Run Complete Workflow (15-30 min, automated)
```bash
bash scripts/run_complete_workflow.sh Godos_2024 --databases pubmed,scopus,wos
```

Results will be in:
- `benchmark_outputs/Godos_2024/` - Individual query performance
- `aggregates/Godos_2024/` - Combined query strategies
- `aggregates_eval/Godos_2024/` - Strategy performance metrics

See [Automation Guide](Documentations/AUTOMATION_GUIDE.md) for detailed instructions.

## 📊 Supported Databases

| Database | Status | API Required | Notes |
|----------|--------|--------------|-------|
| **PubMed** | ✅ Full support | Optional (increases rate limit) | Free via NCBI Entrez |
| **Scopus** | ✅ Full support | Yes | Institutional subscription required |
| **Web of Science** | ✅ Full support | Yes | Institutional subscription required |
| **Embase** | ⚠️ Manual export | No API | Export CSV from Embase.com manually |

## 🔄 Multi-Database Deduplication

**Automatic DOI-based deduplication** (Option A implemented):
- ~96% of modern articles have DOIs
- Eliminates duplicates across databases perfectly
- Logs deduplication statistics (e.g., "3,771 raw → 3,502 unique, 269 duplicates removed")
- See [deduplication documentation](Documentations/multi_database_deduplication_complete.md)

- Queries/queries.txt (UTF-8): one or more PubMed Boolean queries.
  - Separate queries with a blank line.
  - Lines inside a query block are concatenated with spaces.
  - Lines starting with `#` are comments and ignored.
  - Keep parentheses/quotes balanced; avoid proximity operators (NEAR/ADJ) for PubMed.
  - Do not hard-code date limits here; pass them via CLI/env/config instead.

Example (3 PubMed strategies, no date filters):
```
# High-recall
(("Sleep Apnea, Obstructive"[Mesh]) OR ("Obstructive Sleep Apnea"[tiab] OR "OSA"[tiab] OR "OSAHS"[tiab] OR "Sleep-Disordered Breathing"[tiab] OR "Sleep Apnea Hypopnea Syndrome"[tiab] OR "Upper Airway Resistance Syndrome"[tiab] OR "UARS"[tiab]))
AND
(("Microbiota"[Mesh]) OR (microbiome*[tiab] OR microbiota*[tiab] OR "gut flora"[tiab] OR "intestinal flora"[tiab] OR "oral flora"[tiab] OR "nasal flora"[tiab] OR dysbiosis[tiab] OR "alpha diversity"[tiab] OR "beta diversity"[tiab] OR "Shannon index"[tiab] OR "Simpson index"[tiab] OR "Chao1"[tiab]))
AND
(("Case-Control Studies"[Mesh]) OR ("case control*"[tiab] OR "case comparison*"[tiab] OR "case referent*"[tiab] OR retrospective*[tiab]))

# Balanced
(("Sleep Apnea, Obstructive"[Mesh:NoExp]) OR ("Obstructive Sleep Apnea"[tiab] OR "OSAHS"[tiab]))
AND
(("Microbiota"[Mesh]) OR (microbiome*[tiab] OR microbiota*[tiab] OR "gut flora"[tiab] OR "intestinal flora"[tiab]))
AND
(("Case-Control Studies"[Mesh]) OR ("case control"[tiab]))

# High-precision
("Sleep Apnea, Obstructive"[Mesh:NoExp] AND ("Gastrointestinal Microbiome"[Mesh] OR "gut microbiome"[tiab] OR "intestinal microbiome"[tiab]) AND "Case-Control Studies"[Mesh])
```

- concept_terms CSV: CSV with headers `concept,term_regex`; used to compute query concept coverage (regex applied to the raw Boolean text). Example file is provided and adapted for OSA + microbiome case–control.

### Provider-specific query files (beta)

Task 1 (structured LLM output) is still underway, so database-specific files are authored manually for now.

**Step-by-step**

1. Keep the canonical PubMed queries in `studies/<study>/queries.txt` (current behavior).
2. For every additional provider:
   - Copy `queries.txt` into the same folder and rename it using one of these patterns:
     - `queries_scopus.txt`
     - `queries.scopus.txt`
     - `queries-scopus.txt`
     - (future options: `queries_wos.txt`, `queries_embase.txt`, …)
   - Edit the new file so each query uses that provider’s syntax (`TITLE-ABS-KEY`, field tags, proximity operators, etc.).
3. Repeat until you have one aligned file per provider.

**Requirements**

- Every provider file **must contain the same number of queries, in the same order**, as the base file so bundle #1/#2/#3 line up across providers.
- Queries remain separated by blank lines; inline comments starting with `#` are still ignored.
- If a provider-specific file is missing, the workflow reuses `queries.txt` for that provider and emits a warning so you know you are running untailored syntax.

**Example**

```
studies/sleep_apnea/
  queries.txt             # PubMed strategies
  queries_scopus.txt      # Scopus strategies (see repo for full file)
```

Snippet from `queries_scopus.txt` (Variant A):

```
(TITLE-ABS-KEY("sleep apnea syndrome" OR "sleep apnea, obstructive" OR "sleep apnea, central" OR "obstructive sleep apnea")
 AND TITLE-ABS-KEY("dementia" OR "alzheimer disease" OR "vascular dementia" OR "frontotemporal dementia"))
```

With this layout you can iterate on Scopus queries immediately while the PubMed-only workflow keeps running unchanged.

## Configuration modes (precedence: CLI > ENV > CONFIG)

You can provide inputs by:
1) CLI flags
2) Environment variables (optionally in a `.env` file)
3) Config file via `--config` (TOML or JSON)

### Environment variables (.env)
Create `.env` (exact name). Example:
```
NCBI_EMAIL=you@example.com
# NCBI_API_KEY=your_api_key_here

SELECT_MINDATE=2015/01/01
SELECT_MAXDATE=2024/08/31
SELECT_CONCEPT_TERMS=concept_terms_OSA_microbiome_case_control.csv
SELECT_QUERIES_TXT=Queries/queries.txt
SELECT_OUTDIR=sealed_outputs
# SELECT_TARGET_RESULTS=5000
# SELECT_MIN_RESULTS=50

# FINALIZE_SEALED_GLOB=sealed_outputs/sealed_*.json
# FINALIZE_GOLD_CSV=gold_pmids.csv

SCORE_MINDATE=2000/01/01
SCORE_MAXDATE=2024/08/31
SCORE_QUERIES_TXT=Queries/queries.txt
SCORE_GOLD_CSV=gold_pmids.csv
SCORE_OUTDIR=benchmark_outputs

# Multi-database controls
SR_DATABASES=pubmed,scopus            # Comma-separated list of providers to run
SCOPUS_API_KEY=your_scopus_api_key    # Required when Scopus is enabled
# SCOPUS_INSTTOKEN=optional_insttoken  # Only needed for institutions requiring it
# SCOPUS_SKIP_DATE_FILTER=true         # Set to true to temporarily drop PUBYEAR filters
```
> Tip: provide secrets without surrounding quotes. If you have `SCOPUS_API_KEY="abc123"`, remove the quotes so the value is `SCOPUS_API_KEY=abc123`.
Note: the loader reads `.env`, not `.env.yaml`.

### Config file (TOML/JSON)
Copy and edit:
```zsh
cp sr_config.example.toml sr_config.toml
```
Then fill values, e.g.:
```toml
mindate = "2015/01/01"
maxdate = "2024/08/31"
concept_terms = "concept_terms_OSA_microbiome_case_control.csv"
queries_txt = "Queries/queries.txt"
outdir = "sealed_outputs"
# target_results = 5000
# min_results = 50

[databases]
default = ["pubmed"]

[databases.scopus]
enabled = true
api_key = "${SCOPUS_API_KEY}"
insttoken = "${SCOPUS_INSTTOKEN}"
view = "STANDARD"
# skip_date_filter = true
```
Pass it with `--config sr_config.toml`.

### Selecting databases (beta)

- Use `--databases pubmed,scopus` (or set `SR_DATABASES=pubmed,scopus`) to query multiple providers in one run.
- Provider credentials can come from CLI flags (`--scopus-api-key`, `--scopus-insttoken`), environment variables (`SCOPUS_API_KEY`, `SCOPUS_INSTTOKEN`), or the `[databases.<name>]` section in `sr_config.toml`.
- If you need to run without date limits (e.g., waiting on an Insttoken), add `--scopus-skip-date-filter` or set `SCOPUS_SKIP_DATE_FILTER=true`. This flag removes the automatic `PUBYEAR` clause so Scopus behaves like your standalone test script. If Scopus still rejects the call, the workflow logs the error but continues with the remaining providers.
- **Deduplication**: DOI-based deduplication (Option A) is now implemented and automatic. Articles are deduplicated by DOI, handling 96% of articles perfectly. The workflow logs deduplication statistics showing raw results → unique articles. See `Documentations/multi_database_deduplication_complete.md` for details.

## Multi-Database Workflow (beta)

You can now run the workflow across PubMed and Scopus simultaneously. This is an interim experience while we finish Task 1 (structured query prompts) and future DOI/PubMed normalization work.

### 1. Prepare queries

1. Keep your canonical PubMed queries in `studies/<name>/queries.txt`.
2. Create a Scopus-specific file with the exact same number of queries in the same order, using any of these names placed next to the original file:
   - `queries_scopus.txt`
   - `queries.scopus.txt`
   - `queries-scopus.txt`
3. Each provider file can tailor syntax (e.g., set `TITLE-ABS-KEY`, `PUBYEAR`, proximity operators) to that database’s rules. Missing provider files fall back to `queries.txt` and emit a warning so you know uniform queries are being used.

### 2. Configure credentials

Add the Scopus credentials to `.env` (or export them in your shell):

```
SCOPUS_API_KEY=your_elsevier_key_here
# SCOPUS_INSTTOKEN=optional_institution_token_if_required
SR_DATABASES=pubmed,scopus
```

- `SCOPUS_API_KEY` is picked up automatically. The CLI also exposes `--scopus-api-key` if you prefer to pass it explicitly.
- `SCOPUS_INSTTOKEN` is optional and only needed for institutions that require an Insttoken. Use the `--scopus-insttoken` flag to override per run.
- If you temporarily disable the date filter, remember to re-enable it (remove `SCOPUS_SKIP_DATE_FILTER` or the CLI flag) once you obtain an Insttoken so Scopus respects `mindate`/`maxdate`.
- Internally the CLI calls `_instantiate_providers(...)`, which looks for `SCOPUS_API_KEY` / `SCOPUS_INSTTOKEN` / `SCOPUS_SKIP_DATE_FILTER` in this priority order: CLI flag → environment variable (`.env`) → `[databases.scopus]` section in `sr_config.toml`.
- `SR_DATABASES=pubmed,scopus` enables both providers globally. You can override it on demand with `--databases`.

### 3. Run the workflow

From the repo root:

```zsh
conda activate systematic_review_queries
DATABASES="pubmed,scopus" ./run_workflow_sleep_apnea.sh
```

Or call the CLI directly:

```zsh
python llm_sr_select_and_score.py \
  --study-name sleep_apnea \
  --databases pubmed,scopus \
  select \
  --concept-terms concept_terms_sleep_apnea.csv \
  --queries-txt queries.txt \
  --outdir sealed_outputs
```

The same `--databases` flag works for `score`, `finalize`, and `score-sets`. Every bundled query run prints per-provider diagnostics, and the resulting `details_*.json` / `sealed_*.json` files now include a `provider_details` section with the specific query used, result count, and raw IDs returned for each database.

### 4. Inspecting results

- `sealed_outputs/<study>/sealed_*.json` now include `retrieved_dois`, `retrieved_pmids` (PubMed only), and a `provider_details` map. This lets you inspect which provider contributed which identifiers.
- `benchmark_outputs/<study>/details_*.json` mirror the same structure for the scoring phase.
- **Deduplication**: Results are automatically deduplicated by DOI. Check the console logs for deduplication statistics (e.g., "3,771 raw results → 3,502 unique articles (269 duplicates removed, 7.1%)").

### 5. Gold Standard Enhancement (Optional)

For robust matching with Scopus-only articles, you can enhance your gold standard PMID list with DOIs:

```bash
python scripts/enhance_gold_standard.py \
  studies/<study>/gold_pmids.csv \
  studies/<study>/gold_pmids_with_doi.csv
```

This script fetches DOIs from PubMed for each PMID and creates an enhanced CSV with both identifiers. The workflow automatically supports both formats (simple PMID-only and enhanced PMID+DOI).

## Commands

Global option:
- `--config PATH`  Use TOML/JSON config (overridden by CLI; env sits between).

Subcommands:

1) select — evaluate candidates and write sealed output
```zsh
# CLI-only
python llm_sr_select_and_score.py select \
  --mindate 2015/01/01 --maxdate 2024/08/31 \
  --concept-terms concept_terms_OSA_microbiome_case_control.csv \
  --queries-txt Queries/queries.txt \
  --outdir sealed_outputs

# Using .env (no flags)
python llm_sr_select_and_score.py select

# Using config
python llm_sr_select_and_score.py --config sr_config.toml select
```
Outputs:
- sealed_outputs/sealed_YYYYMMDD-HHMMSS.json
- sealed_outputs/selection_summary_YYYYMMDD-HHMMSS.csv

2) finalize — add metrics vs gold to sealed output
```zsh
python llm_sr_select_and_score.py finalize \
  --sealed 'sealed_outputs/sealed_*.json' \
  --gold-csv gold_pmids.csv

# or rely on .env/config
python llm_sr_select_and_score.py finalize
python llm_sr_select_and_score.py --config sr_config.toml finalize
```
Output:
- sealed_outputs/final_YYYYMMDD-HHMMSS.json

3) score — benchmark queries vs gold
```zsh
python llm_sr_select_and_score.py score \
  --mindate 2015/01/01 --maxdate 2024/08/31 \
  --queries-txt Queries/queries.txt \
  --gold-csv gold_pmids.csv \
  --outdir benchmark_outputs
```
Outputs:
- benchmark_outputs/summary_YYYYMMDD-HHMMSS.csv
- benchmark_outputs/details_YYYYMMDD-HHMMSS.json

Example:
```zsh
python llm_sr_select_and_score.py score --mindate 2015/01/01 --maxdate 2024/08/31 --queries-txt Queries/queries.txt --gold-csv Gold_list__all_included_studies_.csv --outdir benchmark_outputs
```

4) print-titles — fetch minimal metadata for PMIDs
```zsh
# From a sealed file
python llm_sr_select_and_score.py print-titles --sealed sealed_outputs/sealed_*.json

# Or explicit list
python llm_sr_select_and_score.py print-titles --pmids 12345,67890
```


Evaluates multiple sets of PMIDs (e.g. from `aggregates/*.txt`):
```zsh
python llm_sr_select_and_score.py score-sets \
  --sets aggregates/*.txt \
  --gold-csv gold_pmids.csv \
  --outdir aggregates_eval

Example:
python llm_sr_select_and_score.py score-sets --sets aggregates/*.txt --gold-csv Gold_list__all_included_studies_.csv --outdir aggregates_eval  
```
## 🎓 Project Structure

```
QueriesSystematicReview/
├── llm_sr_select_and_score.py    # Main CLI tool
├── search_providers.py            # Database API integrations
├── scripts/                       # Utility scripts
│   ├── run_complete_workflow.sh   # Complete workflow automation
│   ├── prepare_study.py           # PDF to markdown conversion
│   ├── validate_pmids_multi_source.py  # Gold standard creation
│   └── enhance_gold_standard.py   # Add DOIs to gold PMIDs
├── studies/                       # Study-specific data
│   ├── Godos_2024/
│   ├── ai_2022/
│   └── sleep_apnea/
├── prompts/                       # LLM prompt templates
│   ├── prompt_template_multidb.md
│   └── database_guidelines.md
├── Documentations/                # Comprehensive guides
└── .env                          # API keys (git-ignored)

### The `/generate_prompt` Command

This command reads a study protocol file, extracts key information, and injects it into a template to create a new, permanent, and runnable command for query generation.

**Arguments:**

*   `--command_name` (Required): The name for the new command you are creating (e.g., `run_my_study`).
*   `--protocol_path` (Required): The absolute path to the study's protocol file (e.g., `studies/my_study/protocol.md`).
*   `--level` (Optional): The template to use. Can be `basic`, `extended`, or `keywords`. Defaults to `basic`.
*   `--min_date` (Optional): The start date for the search (YYYY/MM/DD). Defaults to `1980/01/01`.
*   `--max_date` (Optional): The end date for the search (YYYY/MM/DD). Defaults to `2025/12/31`.

### Usage Examples

Here are three examples demonstrating how to use the command for different levels of prompt complexity.

**1. Basic Level**

This generates a command using the standard template, focusing on the core query strategies.

```bash
/generate_prompt --command_name "run_basic_study" --protocol_path "studies/sleep_apnea/prospero-sleep-apnea-dementia.md" --level "basic" --max_date "2021/03/01"
```

This will create a new command `/run_basic_study` in your Gemini command list.

**2. Extended Level**

This uses the extended template, which includes the detailed `USER TASK` section and instructions for generating precision-lean micro-variants.

```bash
/generate_prompt --command_name "run_extended_study" --protocol_path "studies/sleep_apnea/prospero-sleep-apnea-dementia.md" --level "extended" --max_date "2021/03/01"
```

This will create a new command `/run_extended_study`.

**3. Keywords Level**

This uses the keywords-first template, which adds a preliminary step for the LLM to expand on the protocol's keywords before building the main query concepts.

```bash
/generate_prompt --command_name "run_keywords_study" --protocol_path "studies/sleep_apnea/prospero-sleep-apnea-dementia.md" --level "keywords" --max_date "2021/03/01"
```

This will create a new command `/run_keywords_study`.


## Heuristics & checks (what affects the score)
- PubMed esearch uses XML mode.
- Lint: unbalanced parentheses/quotes, empty groups, duplicated operators, proximity ops.
- Coverage: fraction of concepts matched (via regexes from concept_terms CSV).
- Burden: prefers result counts close to target; penalizes too few results.
- Vocabulary penalty: invalid MeSH or headings introduced after `maxdate` year.
- Simplicity: penalizes very long/deeply nested queries.

## Troubleshooting
- "Missing required values": provide via CLI, `.env`, or `sr_config.toml`.
- "NCBI email": set `NCBI_EMAIL` (CLI/env/config).
- NotXMLError: ensure you’re using this script version (XML mode is set).
- No env: confirm `conda activate systematic_review_queries` and VS Code interpreter/kernel.
- .env not loaded: file must be named `.env` and `python-dotenv` must be installed (it is in `environment.yml`).

## Precision-lean variants framework (new)

This repo now includes an abstract "Recall Lock + Precision Knobs" framework to help generate precision-lean PubMed variants without sacrificing recall.

- Reusable include: `.github/prompts/includes/precision_knobs.md` (concepts, knobs, and diversity guidance).
- Integrated in MS prompt: `.github/prompts/run_sleep_ms.prompt.md` now asks the LLM to output:
  - Recall_Lock (invariant MS + sleep + RCT core for PubMed)
  - Precision_Knobs list (humans/lang; title emphasis; Mesh:NoExp; exclude case reports; narrower sleep; RCT tiab signal)
  - 6 PubMed micro-variants (V1–V6), each toggling ≤2 knobs, with rationale + expected_recall_delta
  - PRESS picks top-3 precision variants to append to `Queries/queries.txt`

Workflow impact:
- After you run the prompt-driven generator and overwrite `Queries/queries.txt`, you'll have the usual strategies plus a few precision-lean variants. Use `score` to benchmark them against your gold list and compare precision/recall/NNR.


## Automated Multi-Database Prompt Generation

This project features an advanced, two-stage workflow for automatically generating runnable commands that produce complex, multi-database search queries. This system is designed to be robust, maintainable, and highly specific to your study's needs.

### Stage 1: Create a Study-Specific Command

The first step is to use the `/generate_multidb_prompt` command to create a new, permanent, and runnable command tailored to your specific study protocol.

**Command:**
`/generate_multidb_prompt`

**Arguments:**

*   `--command_name` (Required): The name for the new command you want to create (e.g., `run_my_study_multidb`).
*   `--protocol_path` (Required): The path to the study's protocol file (e.g., `studies/my_study/protocol.md`).
*   `--databases` (Required): A comma-separated list of databases (e.g., `pubmed,scopus,embase`).
*   `--level` (Optional): Specifies the complexity and detail of the queries to be generated. Defaults to `extended`. The available levels are:
    *   `basic`: Generates the 3 core strategies (High-recall, Balanced, High-precision).
    *   `extended`: Generates the 3 core strategies plus 3 prescriptive micro-variants based on the database-specific `Precision_Knobs`.
    *   `keywords`: Adds a preliminary keyword-expansion step and generates 4 keyword-focused queries.
    *   `exhaustive`: Generates the 3 core strategies plus 6 micro-variants, creating a highly comprehensive set of queries.
*   `--min_date` / `--max_date` (Optional): The date window for the search (YYYY/MM/DD).

**Example Usage:**

```bash
/generate_multidb_prompt --command_name "run_sleep_apnea_multidb_extended" --protocol_path "studies/sleep_apnea/prospero-sleep-apnea-dementia.md" --databases "pubmed,scopus,embase" --level "extended" --max_date "2021/03/01"
```

This command will read the protocol, select the correct instructions from the master template for the `extended` level, and create a new, permanent Gemini command named `/run_sleep_apnea_multidb_extended`.

### Stage 2: Execute the New Command to Generate Queries

Once Stage 1 is complete, you can run the command you just created to perform the actual query generation.

**Example Usage:**

```bash
/run_sleep_apnea_multidb_extended
```

Running this command will instruct the LLM to execute the complex, level-specific prompt. The output is a single JSON object containing all queries, which is then automatically parsed to create separate files for each database in your study's folder (e.g., `studies/sleep_apnea/`):

*   `queries.txt` (for PubMed)
*   `queries_scopus.txt`
*   `queries_embase.txt`

### Advanced Architectural Features

The multi-database generation workflow includes several advanced features to ensure high-quality and robust output:

*   **Master Template Architecture:** All prompt logic is consolidated into a single master template (`prompts/prompt_template_multidb.md`). The generator intelligently processes this file to select the correct instructions based on the chosen `--level`, making the system highly maintainable.
*   **Prescriptive Micro-variants:** The `extended` and `exhaustive` levels use a detailed recipe to create micro-variants, telling the LLM what *type* of `Precision_Knob` to use (e.g., Filter-based, Scope-based) for each variant, ensuring consistent and high-quality output.
*   **"JSON Patch" Self-Correction:** The prompt includes a structured self-correction step. The LLM reviews its own generated queries and produces a machine-readable `json_patch` object for any necessary fixes. This patch is then automatically applied before the final files are written, creating a reliable self-healing mechanism.
*   **High-Level Context (`USER TASK`):** The prompt includes a dedicated section to provide the LLM with the high-level goals and context of a rigorous systematic review, which helps steer the model towards producing better results.



### Example results explanation of the select Command

  How the select Command Works

  The llm_sr_select_and_score.py script uses a heuristic scoring system
   to choose the best query without looking at the gold-standard
  answers. It acts like an information specialist who is trying to
  predict which query is the most promising.

  The script calculates a score for each query based on five main
  factors:

   1. Concept Coverage (Weight: 2.0): This is the most important
      factor. It checks if the query text contains terms for all the
      key concepts you define in a concept_terms.csv file. A query
      that covers more concepts gets a much higher score.
   2. Screening Burden: This score rewards queries that return a
      "reasonable" number of results. By default, it aims for a target
      of 5000 results and penalizes queries that return too many (high
      burden) or too few (risk of missing studies). There is a hard
      penalty if the query returns fewer than a minimum threshold
      (default: 50 results).
   3. Query Quality (Linting): It checks for simple errors like
      unbalanced parentheses or accidental duplicates (AND AND) and
      applies a small penalty for each issue found.
   4. Vocabulary Check: It validates the MeSH terms in the query to
      ensure they are real and were available within your project's
      date window, applying a penalty for invalid terms.
   5. Simplicity: It penalizes queries that are excessively long or
      complex, as they can be hard to read and maintain.

  The final score is calculated roughly as:
  Score = (2 * Concept Coverage) + Screening Burden - Penalties

  Why the High-Recall Query Was Chosen in Your Run

  In your specific case, the Screening Burden was the deciding factor.

   1. The Balanced query returned 10 results.
   2. The High-Precision query returned 5 results.
   3. The High-Recall query returned 91 results.

  The script has a min_results setting which defaults to 50. Both the
  Balanced and High-Precision queries fell below this threshold, which
  gives them a large penalty. The High-Recall query, with 91 results,
  was the only one to clear this minimum bar.

  Therefore, even though its result count was far from the ideal target
   of 5000, it was selected as the most viable candidate because the
  others were considered too narrow.

### The score Command: The Benchmark

  The score command is your primary tool for benchmarking. Its purpose is to
  directly measure how well your queries perform against a known list of correct
  answers (the "gold standard").

  Logic:
   1. It takes all the queries from Queries/queries.txt.
   2. For each query, it runs the search on PubMed to get a list of results.
   3. It compares those results to your Gold_list__all_included_studies_.csv.
   4. It calculates metrics that tell you how effective each query was.

  The Math & Meaning (from `benchmark_outputs/details_20250904-130104.json`)

  Let's look at your High-Recall query's results:

   1 "results_count": 91,
   2 "TP": 9,
   3 "gold_size": 9,
   4 "recall": 1.0,
   5 "NNR_proxy": 10.11

   * `results_count`: 91
       * Meaning: This query found 91 articles on PubMed. This is your total
         screening burden.

   * `gold_size`: 9
       * Meaning: You have 9 articles in your gold-standard list that you consider
         essential to find.

   * `TP` (True Positives): 9
       * Meaning: These are the "hits." Of the 91 articles found, 9 of them were
         also in your gold-standard list.
       * Math: count(articles in results AND in gold list)

   * `recall`: 1.0
       * Meaning: This is the most critical metric for a systematic review. It
         means your query found 100% of the articles in your gold list. You didn't
         miss anything.
       * Math: TP / gold_size  (9 / 9 = 1.0)

   * `NNR_proxy` (Number Needed to Read): 10.11
       * Meaning: This estimates your workload. On average, you will need to screen
         about 10 articles to find one relevant paper. A lower NNR is better, but
         the top priority is high recall.
       * Math: results_count / TP (91 / 9 = 10.11)

  ---

### The finalize Command: Unsealing the Winner

  The finalize command takes the single "best" query chosen by the select command
  (which was selected without seeing the gold list) and runs the same
  gold-standard evaluation on it. It's the final step that reveals how well the
  automated selection process worked.

  Logic:
   1. It finds the sealed_...json file that was created by the select command.
   2. It takes the query and its list of results from that file.
   3. It compares those results to your gold-standard list.
   4. It calculates a more detailed set of metrics and saves them to a final_...json
      file.

  The Math & Meaning (from `final_outputs/final_20250904-124919.json`)

  This file contains the same metrics as above, plus a few more for deeper analysis:


   1 "Precision": 0.0989,
   2 "Recall": 1.0,
   3 "F1": 0.1799,
   4 "Jaccard": 0.0989,
   5 "OverlapCoeff": 1.0

   * `Precision`: 0.0989
       * Meaning: Of all the articles the query found, only about 9.9% were
         relevant (i.e., in your gold list). This is the inverse of NNR and shows
         the trade-off you made for getting perfect recall.
       * Math: TP / results_count (9 / 91 = 0.0989)

   * `F1-Score`: 0.1799
       * Meaning: This is a combined score that tries to balance precision and
         recall into a single number. It's useful for comparing different queries,
         but for systematic reviews, recall is far more important.
       * Math: 2 * (Precision * Recall) / (Precision + Recall)

   * `Jaccard` & `OverlapCoeff`: These are other statistical measures of how well
     the two sets (results vs. gold list) overlap. An OverlapCoeff of 1.0 is
     another way of saying that 100% of the items in your gold list were found
     within the search results.

  In summary:
   * `score` is for benchmarking all your candidate queries.
   * `finalize` is for formally evaluating the single query that the select command
     chose based on its heuristics.


## Workflow

This section outlines the typical workflow for using the tools in this repository to generate, evaluate, and refine PubMed queries for a systematic review.

### 1. Query Generation

The first step is to generate a set of candidate queries using the Gemini CLI. This is done by executing a predefined command that contains a prompt for the Large Language Model (LLM).

-   **Process:** Run a command such as `/run_sleep` or `/run_sleep_ms`. These commands are defined in TOML files located in the `.gemini/commands/` directory (e.g., `run_sleep.toml`). The `prompt` within the TOML file instructs the LLM to generate a series of PubMed queries based on a specific research question and PICOS criteria.
-   **Input:** A prompt defined in a `.toml` file (e.g., `.gemini/commands/run_sleep.toml`).
-   **Output:** The LLM-generated queries are automatically saved to the `Queries/Queries/queries.txt` file.

### 2. Query Evaluation and Selection

Once the candidate queries are generated, the `llm_sr_select_and_score.py` script is used to evaluate and select the best-performing queries.

-   **Process:** This script offers several subcommands:
    -   `select`: Evaluates queries based on heuristics (e.g., concept coverage, screening burden) without using a gold-standard list. It "seals" the best query for later evaluation.
    -   `score`: Benchmarks all queries against a gold-standard list of PMIDs (e.g., `Gold_list__all_included_studies_.csv`) to calculate metrics like recall, precision, and Number Needed to Read (NNR).
    -   `finalize`: Takes a "sealed" query from the `select` step and runs a full evaluation against the gold-standard list.
-   **Inputs:**
    -   `Queries/Queries/queries.txt`: The file containing the candidate queries.
    -   A gold-standard list of PMIDs in a CSV file (e.g., `Gold_list__all_included_studies_.csv`) for the `score` and `finalize` commands.
    -   Configuration parameters, which can be provided via the command line, a `.env` file, or `sr_config.toml`.
-   **Outputs:**
    -   `select`: A `sealed_*.json` file and a `selection_summary_*.csv` file in the `sealed_outputs/` directory.
    -   `score`: A `summary_*.csv` file and a `details_*.json` file in the `benchmark_outputs/` directory.
    -   `finalize`: A `final_*.json` file in the `sealed_outputs/` directory.

### 3. Query Aggregation and Comparison

After evaluating the queries, you can use additional scripts to aggregate results or compare different runs.

-   **Process:**
    -   `scripts/aggregate_queries.py`: This script combines PMIDs from multiple queries using various strategies (e.g., consensus, weighted voting) to create aggregated sets of results. This can help in finding a balance between recall and precision.
    -   `scripts/compare_runs.py`: This script compares the outputs of two different query generation runs (e.g., from different prompts or models), providing statistics on the overlap and differences in the retrieved PMIDs.
-   **Inputs:**
    -   `aggregate_queries.py`: JSON files from the `benchmark_outputs/` or `sealed_outputs/` directories.
    -   `compare_runs.py`: The output directories of two different runs (e.g., `benchmark_A/` and `benchmark_B/`).
-   **Outputs:**
    -   `aggregate_queries.py`: A set of `.txt` files in the `aggregates/` directory, each containing a list of aggregated PMIDs.
    -   `compare_runs.py`: A `report.json` file in a new directory named after the two compared runs (e.g., `benchmark_A_vs_benchmark_B/`).

### Workflow Diagram

The following diagram illustrates the overall workflow:

```mermaid
graph TD
    subgraph "Step 1: Query Generation"
        A[Start] --> B{Run Gemini Command<br>(e.g., /run_sleep)};
        B -- LLM Generates Queries --> C[Save to<br>Queries/Queries/queries.txt];
    end

    subgraph "Step 2: Evaluation & Selection"
        C --> D{llm_sr_select_and_score.py};
        D -- select --> E[Sealed Query<br>(sealed_outputs/*.json)];
        D -- score --> F[Benchmark Results<br>(benchmark_outputs/*.json)];
        D -- finalize --> G[Final Results<br>(sealed_outputs/final_*.json)];
    end

    subgraph "Step 3: Aggregation & Comparison"
        F --> H{aggregate_queries.py};
        H --> I[Aggregated PMIDs<br>(aggregates/*.txt)];
        F --> J{compare_runs.py};
J[Comparison Report<br>(runA_vs_runB/report.json)];
    end

### Example Workflow Execution

The `run_workflow_sleep_apnea.sh` script provides an automated way to execute the entire workflow, from query evaluation to aggregation and comparison.

-   **Process:** This script runs the `select`, `finalize`, `score`, `aggregate`, and `evaluate aggregates` steps in sequence. It is a convenient way to perform a full analysis of your queries with a single command.
-   **Inputs:** The script accepts various command-line options to customize the workflow, such as changing the date range, input files, or output directories.
-   **Output:** The script will create the output files from each step in the respective directories (`sealed_outputs/`, `final_outputs/`, `benchmark_outputs/`, `aggregates/`, and `aggregates_eval/`).

**Usage:**

```bash
./run_workflow_sleep_apnea.sh [OPTIONS]
```

**Options:**

| Option                      | Description                                                  | Default                                     |
| --------------------------- | ------------------------------------------------------------ | ------------------------------------------- |
| `-m`, `--mindate`           | Minimum date for the search (YYYY/MM/DD).                    | `2015/01/01`                                |
| `-x`, `--maxdate`           | Maximum date for the search (YYYY/MM/DD).                    | `2024/08/31`                                |
| `-q`, `--queries-txt`       | Path to the queries text file.                               | `Queries/queries.txt`                       |
| `-g`, `--gold-csv`          | Path to the gold-standard CSV file.                          | `Gold_list__all_included_studies_.csv`      |
| `-c`, `--concept-terms`     | Path to the concept terms CSV file.                          | `concept_terms_OSA_microbiome_case_control.csv` |
| `-os`, `--outdir-select`    | Output directory for the `select` command.                   | `sealed_outputs`                            |
| `-ob`, `--outdir-score`     | Output directory for the `score` command.                    | `benchmark_outputs`                         |
| `-oa`, `--outdir-aggregates`| Output directory for the aggregation script.                 | `aggregates`                                |
| `-oe`, `--outdir-aggregates-eval`| Output directory for the aggregates evaluation.         | `aggregates_eval`                           |
| `-of`, `--outdir-final`     | Output directory for the `finalize` command.                 | `final_outputs`                             |
| `-h`, `--help`              | Display the help message.                                    |                                             |

**Example:**

To run the workflow with a different date range and a specific queries file, you can use the following command:

```bash
./run_workflow_sleep_apnea.sh --mindate 2010/01/01 --maxdate 2023/12/31 --queries-txt My_Queries/new_queries.txt
```
```
