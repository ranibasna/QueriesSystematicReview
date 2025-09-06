# Gemini Code Assistant Context

## Project Overview

This project provides a command-line tool (`llm_sr_select_and_score.py`) to assist with systematic reviews of academic literature, specifically focusing on PubMed. It helps researchers evaluate, select, and benchmark different search queries to find the most effective one for their needs.

The tool uses a heuristic-based approach to "select" the best query without a gold-standard set of articles, and it can also "score" queries against a gold standard to measure recall and precision.

The main technologies used are Python 3, with the following key libraries:
- **Biopython**: For interacting with the NCBI Entrez API to search PubMed.
- **pandas**: For data manipulation and analysis, especially for handling lists of articles and results.
- **tenacity**: For robustly handling API requests with retries.
- **argparse**: For creating the command-line interface.

## Building and Running

The project uses a Conda environment for managing dependencies.

**1. Environment Setup:**

To set up the environment, use the `environment.yml` file:

```bash
conda env create -f environment.yml
conda activate systematic_review_queries
```

**2. Running the Tool:**

The main script is `llm_sr_select_and_score.py`. It is a command-line tool with several subcommands.

**General Usage:**

```bash
python llm_sr_select_and_score.py [COMMAND] [OPTIONS]
```

**Key Commands:**

*   **`select`**: Evaluates candidate queries from a text file (`queries.txt`) and selects the best one based on heuristics.
    ```bash
    python llm_sr_select_and_score.py select --mindate 2015/01/01 --maxdate 2024/08/31 --concept-terms concept_terms.csv --queries-txt queries.txt --outdir sealed_outputs
    ```
*   **`score`**: Benchmarks a set of queries against a gold-standard list of PMIDs.
    ```bash
    python llm_sr_select_and_score.py score --mindate 2015/01/01 --maxdate 2024/08/31 --queries-txt queries.txt --gold-csv gold_pmids.csv --outdir benchmark_outputs
    ```
*   **`finalize`**: Takes a "sealed" query from the `select` command and evaluates it against a gold standard.
    ```bash
    python llm_sr_select_and_score.py finalize --sealed 'sealed_outputs/sealed_*.json' --gold-csv gold_pmids.csv
    ```

**Configuration:**

Configuration can be provided in three ways, in order of precedence:
1.  Command-line arguments
2.  Environment variables (can be stored in a `.env` file)
3.  A TOML or JSON configuration file (e.g., `sr_config.toml`)

## Development Conventions

*   **Code Style:** The code is written in a clear and modular style, with functions for specific tasks. It includes type hints and docstrings.
*   **Input Files:**
    *   `queries.txt`: A plain text file containing PubMed queries, separated by blank lines.
    *   `sr_config.toml`: A TOML file for configuring the tool's parameters.
    *   `concept_terms_*.csv`: CSV files that define key concepts and their corresponding search terms (using regular expressions).
*   **Output Files:** The tool generates several output files, typically in the `sealed_outputs`, `benchmark_outputs`, and `final_outputs` directories. These files are usually in JSON or CSV format.
*   **Testing:** While there are no dedicated test files in the repository, the `score` command can be used to benchmark the queries and validate the results.
