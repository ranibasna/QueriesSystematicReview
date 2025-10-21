# Implemented Features

This section documents features and workflows that have been successfully implemented.

## 1. Automated Prompt Generation via Custom Command

**Motivation:** The manual creation of detailed prompt files for each systematic review study was time-consuming, repetitive, and prone to error. A standardized, automated workflow was needed to ensure consistency and improve efficiency.

**Logic:** This feature is implemented as a native Gemini CLI custom command named `/generate_prompt`. The command's logic is defined in `.gemini/commands/generate_prompt.toml`. When executed, it orchestrates a self-guided workflow for the agent.

**How to Use:** The command can be run directly from the Gemini CLI. For example:

```bash
/generate_prompt --command_name "run_sleep_apnea_final" --protocol_path "studies/sleep_apnea/prospero-sleep-apnea-dementia.md" --level "extended" --max_date "2021/03/01"
```

This creates a new command, `/run_sleep_apnea_final`, ready for immediate use.

### Under the Hood: The Generation Mechanism

The process is a sequence of steps that the agent follows based on the instructions in the `/generate_prompt` command definition:

1.  **User Invocation:** The process begins when the user executes the `/generate_prompt` command with its arguments (e.g., `--protocol_path`, `--level`).

2.  **Command Dispatch:** The Gemini CLI identifies `/generate_prompt` as a custom command and retrieves its definition from `.gemini/commands/generate_prompt.toml`.

3.  **Agent Instruction:** The `prompt` field from the `.toml` file is passed to the agent as its primary set of instructions. The user-provided arguments are interpolated into this master prompt as variables (e.g., `{protocol_path}`).

4.  **Agent Self-Orchestration:** The agent executes the instructions in the master prompt it just received. This involves the following tool-based workflow:
    *   **File Selection & Reading:** The agent uses conditional logic based on the `{level}` variable to determine which template file to use from the `prompts/` directory. It then calls the `read_file` tool to load the contents of both the chosen template and the user-specified protocol file.
    *   **Information Extraction:** Using its native LLM capabilities, the agent analyzes the text of the protocol file. It comprehends the document's structure to find and extract the relevant PICOS summary and the study's topic description.
    *   **Derivation and Population:** This is a series of string manipulation and replacement operations:
        *   The agent programmatically derives the `[STUDY_NAME]` by parsing the `{protocol_path}` string (it extracts the name of the parent directory).
        *   It then performs a series of search-and-replace actions on the template string, substituting all placeholders (e.g., `[STUDY_NAME]`, `[DATE_WINDOW_START]`, `[CONCISE TOPIC DESCRIPTION]`) with the corresponding variables and the text it extracted.
    *   **Final Assembly and File Write:** The agent constructs the complete content for the new `.toml` command file as a single string. It then calls the `write_file` tool, providing the full path (using the `{command_name}` for the filename) and the content to be written.

5.  **Confirmation:** After the `write_file` tool succeeds, the agent reports back to the user that the new command has been created.

---

# Future Development Tasks

This file outlines planned improvements and new features for the systematic review query generation workflow.

## 1. Enhance Prompt Template with Multi-Level Generation

**Status: COMPLETED.** This has been implemented via the `/generate_prompt` command and the creation of `basic`, `extended`, and `keywords` templates in the `prompts/` directory.

---

## 2. Automate and Improve Concept Extraction from Protocol

**Status: COMPLETED.**

**Objective:** Develop a more robust and automated method for extracting core concepts from a study protocol (e.g., a PROSPERO markdown file) and structuring them into a concept CSV file.

**Description:**
Currently, defining the concepts for the search (e.g., in `concept_terms_sleep_apnea.csv`) is a manual or semi-automated process. This task aims to create a more intelligent extraction workflow that directly uses the study protocol as the source of truth.

The improved process should:
1.  **Parse the Protocol:** Read a given protocol file (e.g., `studies/sleep_apnea/prospero-sleep-apnea-dementia.md`).
2.  **Identify Core Concepts:** Extract the main PICOS elements (Population, Intervention/Exposure, Outcomes).
3.  **Integrate Keywords:** Crucially, the process must also parse the **'Keywords'** section of the protocol. These keywords should be integrated into the concept groups. For example, if the main outcome is "Dementia", keywords like "Alzheimer disease" and "Lewy body disease" should be automatically grouped under the "Dementia" concept.
4.  **Generate Concept CSV:** The output should be a structured CSV file (e.g., `[study_name]_concepts.csv`) with columns like `concept`, `term`, `type` (e.g., 'synonym', 'acronym', 'MeSH', 'protocol_keyword'). This file can then be used as a definitive reference for the query generation script.

**Example Workflow:**
- **Input:** `prospero-sleep-apnea-dementia.md`
- **Action:** The script identifies "Sleep Apnea" (Population/Exposure) and "Dementia" (Outcome) as primary concepts. It then reads the keywords: "Alzheimer disease", "Lewy body disease", "Sleep apnea", etc.
- **Logic:** It maps "Alzheimer disease" and "Lewy body disease" as terms under the "Dementia" concept. It maps "Sleep apnea" under the "Sleep Apnea" concept.
- **Output:** A CSV file is generated containing these structured concept-term relationships.

**Acceptance Criteria:**
- A script or a well-defined LLM prompt is created that can take a protocol file path as input.
- The process correctly identifies and extracts PICOS elements and keywords.
- The output is a correctly formatted CSV file that logically groups keywords under the primary concepts.
- The process is demonstrably more accurate and less manual than the current approach.

---

## 3. Integrate a Second Database API (e.g., Scopus)

**Objective:** Extend the entire workflow to support a second major academic database beyond PubMed, enabling multi-database searching, scoring, and analysis.

**Description:**
The current tool is tightly coupled with the NCBI Entrez API for PubMed. This task involves abstracting the database-specific logic and adding support for a new database (e.g., Scopus via its API), which will impact the entire toolchain.

**Sub-Tasks & Design Questions:**

1.  **Core API Integration:**
    *   Develop a new API client module (e.g., `scopus_client.py`) to handle authentication, query execution, and response parsing for the new database.
    *   Abstract the existing Entrez logic into a `pubmed_client.py` to create a common interface for database clients (e.g., a `DatabaseClient` abstract base class).

2.  **Query Generation & Management:**
    *   Update the `FINAL TASK` in all prompt templates to instruct the LLM to save queries for each database.
    *   **Design Question:** How should we store queries for different databases? A single `queries.txt` with commented sections (`# --- PubMed Queries ---`, `# --- Scopus Queries ---`)? Or separate files (`queries_pubmed.txt`, `queries_scopus.txt`)?

3.  **Scoring and Selection (`llm_sr_select_and_score.py`):**
    *   Modify the `select`, `score`, and `finalize` commands to accept a `--database` argument (e.g., `pubmed`, `scopus`).
    *   Adapt the scoring heuristics. For example, replace the MeSH validation in the `select` command with an equivalent for the new database (e.g., Emtree for Embase) or a more generic quality check.
    *   Ensure the tool correctly handles different article identifiers (e.g., Scopus EID vs. PubMed PMID).

4.  **Handling Multi-Database Results (Brainstorming Required):**
    *   This is the most critical design decision.
    *   **Option A (Separate Silos):** Treat each database independently. The user would run `score --database pubmed` and `score --database scopus` separately. The results would be stored in separate directories. This is the simplest approach and a good first step.
    *   **Option B (Combined & De-duplicated):**
        *   Develop a de-duplication engine. This would involve fetching metadata for each article (Title, Authors, DOI, Year, Journal) and using a matching algorithm to identify duplicates across databases.
        *   The `score` command would then operate on a single, de-duplicated list of articles.
        *   **Implication:** This is a significant undertaking and would represent a major new capability for the tool.

5.  **Aggregation & Downstream Tools:**
    *   Update `scripts/aggregate_queries.py` and `scripts/compare_runs.py` to either handle the different database identifiers or work with a de-duplicated dataset, depending on the choice made in the previous step.

**Acceptance Criteria:**
- The user can successfully run a query search and scoring process against a new, non-PubMed database.
- A clear strategy for handling multi-database results is chosen and implemented.
- The prompt generation workflow is updated to save queries for the new database.
- Documentation (`README.md`) is updated to explain how to configure and use the new multi-database capabilities.

---

## 4. Integrate AI-powered Web Search for Supplemental Literature Discovery

**Objective:** Investigate using AI-powered web search tools (like Perplexity) to find literature beyond traditional database queries, such as through citation searching and discovery of grey literature.

**Description:**
This task involves exploring tools and workflows to supplement the core database searches. The user has suggested investigating "mcp" tools like "Preplexity mcp" (possibly Perplexity) for tasks such as:
-   **Backward Citation Searching:** Finding literature that is cited by a set of known relevant papers.
-   **Grey Literature:** Searching for conference proceedings, dissertations, and other non-peer-reviewed but potentially relevant sources.
-   **General Web Search:** Using the LLM's ability to search the internet to find related articles and concepts.

The investigation should result in a plan for how to integrate this into the existing workflow, considering aspects like reproducibility and the reliability of the sources.

**Acceptance Criteria:**
- A summary of available tools (including "Preplexity mcp") and their capabilities for systematic reviews.
- A proposed workflow for how to incorporate this type of search into the project.
- A discussion of the pros and cons, including potential for bias and challenges in documenting the search process.
