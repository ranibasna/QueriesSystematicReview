# LLM-assisted Systematic Review: Selection & Scoring

This repo includes a single-file CLI: `llm_sr_select_and_score.py`.
It helps you evaluate PubMed queries, pick the best one (sealed), and optionally score against a gold set.

- select: evaluate candidate queries without gold; write a sealed JSON + CSV summary.
- finalize: compute recall/TP/NNR and similarity vs gold for a sealed run.
- score: benchmark queries vs a gold set directly.
- print-titles: fetch minimal metadata for PMIDs.

## Environment

Use the provided conda env.

```zsh
conda env create -f environment.yml
conda activate systematic_review_queries
# Update later if needed
conda env update -f environment.yml --prune
```

NCBI (required by Entrez):
- Set your email and optionally API key (can also be in .env/config):
```zsh
export NCBI_EMAIL="you@example.com"
# export NCBI_API_KEY="..."
```

## Inputs

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

# SCORE_MINDATE=2000/01/01
# SCORE_MAXDATE=2024/08/31
# SCORE_QUERIES_TXT=Queries/queries.txt
# SCORE_GOLD_CSV=gold_pmids.csv
# SCORE_OUTDIR=benchmark_outputs
```
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
```
Pass it with `--config sr_config.toml`.

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
## Automated Prompt Generation Workflow

This project includes a powerful workflow to automate the creation of runnable query generation commands, saving you from manually editing prompt files for each study. This is orchestrated by the `/generate_prompt` custom command.

**Note:** This is a new feature and is currently under testing.

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


## Q&A

✦ That's an excellent question, and it gets to the heart of the methodology behind the script. You are right that
  both commands deal with results, but their purpose and timing are fundamentally different.

  The core difference is the principle of blinding, which is crucial for a rigorous systematic review. You want to
  avoid bias by choosing your final search query before you know how well it performs against your gold-standard
  list.

  Here’s a breakdown of the roles:

  1. select: The Blind Prediction

   * Purpose: To predict which of your candidate queries is the most promising, using only objective, structural
     criteria. It works completely blind, without ever seeing your gold-standard answers.
   * Inputs:
       * Your list of candidate queries (Queries/queries.txt).
       * Your list of concepts (concept_terms.csv).
   * Output:
       * A sealed_...json file containing the single best query chosen by the heuristic score. Think of this as
         putting your chosen query into a sealed envelope. You have committed to it without knowing the outcome.

  2. finalize: The Reveal

   * Purpose: To validate the performance of the query that select chose. This is the step where you "unseal the
     envelope" and see how your blind prediction actually performed against the answers.
   * Inputs:
       * The sealed_...json file (the single query you committed to).
       * Your gold-standard list of articles.
   * Output:
       * A final_...json file. This is the same as the sealed file, but now with the performance metrics (Recall,
         Precision, etc.) added.

  ---

  Clarifying a Key Point

  You mentioned that finalize recorded the three results. This is a small mix-up in the workflow:

   * The command that evaluates all of your queries is the `score` command. The score command's output is the
     benchmark_outputs/details...json file, which shows the performance of every query in Queries/queries.txt.
   * The finalize command only ever looks at the one query that was saved in the sealed_...json file.

  Summary Table

  Here is a table to make the distinction clear:


  ┌───────┬──────────────────────────┬────────────┬─────────────────┬───────────────────────────────────┐
  │ Co... │ Purpose                  │ Key Input  │ Key Output      │ How Many Queries Processed?       │
  ├───────┼──────────────────────────┼────────────┼─────────────────┼───────────────────────────────────┤
  │ `s... │ Predict the best quer... │ `querie... │ sealed_...json  │ Processes all, but outputs one.   │
  │ `f... │ Validate the single c... │ `sealed... │ final_...json   │ Processes only the one from th... │
  │ score │ Benchmark all queries... │ `querie... │ `benchmark_o... │ Processes all queries from the... │
  └───────┴──────────────────────────┴────────────┴─────────────────┴───────────────────────────────────┘


  In short, the separation between select and finalize enforces a methodologically sound workflow: predict first, 
  then validate. This prevents you from simply running all the queries, seeing which one gets the best score, and
  choosing it after the fact.



  TP = 9: You retrieved all 9 gold (relevant) papers.

Retrieved = 91: Total unique papers your pipeline returned.

Gold = 9: Total relevant papers in your gold set.

Precision: 

P
=
T
P
Retrieved
=
9
91
≈
0.0989
P= 
Retrieved
TP
​
 = 
91
9
​
 ≈0.0989
About 9.9% of retrieved items are relevant (many false positives).

Recall: 

R
=
T
P
Gold
=
9
9
=
1.0
R= 
Gold
TP
​
 = 
9
9
​
 =1.0
You found every gold paper (perfect recall).

F1: 

F
1
=
2
P
R
P
+
R
=
2
×
0.0989
×
1
0.0989
+
1
≈
0.18
F1= 
P+R
2PR
​
 = 
0.0989+1
2×0.0989×1
​
 ≈0.18
Harmonic mean of precision and recall.

Jaccard: 

J
=
∣
A
∩
B
∣
∣
A
∪
B
∣
=
9
91
≈
0.0989
J= 
∣A∪B∣
∣A∩B∣
​
 = 
91
9
​
 ≈0.0989
With all gold inside retrieved, 
∣
A
∪
B
∣
=
∣
A
∣
=
91
∣A∪B∣=∣A∣=91, so Jaccard equals precision.

Overlap Coefficient: 

Overlap
=
∣
A
∩
B
∣
min
⁡
(
∣
A
∣
,
∣
B
∣
)
=
9
9
=
1.0
Overlap= 
min(∣A∣,∣B∣)
∣A∩B∣
​
 = 
9
9
​
 =1.0
Since 
B
⊆
A
B⊆A, overlap is perfect.

Practical takeaway: Recall is perfect, but precision is low (82 false positives). To improve precision, tighten queries or add filters/thresholds, while monitoring recall.

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

