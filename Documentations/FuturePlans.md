# Strategic Plan: Dynamic Multi-Database Query Generation

This document outlines the strategic plan to enhance the query generation workflow to support multiple databases in a unified, "run-once" process.

The goal is to create a system that can generate tailored, balanced sets of search queries for multiple databases (e.g., PubMed, Scopus, Embase) from a single command.

## Core Components of the New Workflow

1.  **Centralized Database Guidelines:**
    *   A new file, `prompts/database_guidelines.md`, will be created to act as a single source of truth for all database-specific rules.
    *   For each database, this file will define syntax, controlled vocabulary usage, and a list of "Precision Knobs" for generating precision-lean query variants.

2.  **Generic and Powerful Prompt Template:**
    *   A new prompt template, `prompts/prompt_template_multidb.md`, will be developed.
    *   This template will be generic and will feature placeholders for dynamically injected database guidelines.
    *   It will instruct the LLM to produce a balanced number of queries (including micro-variants) for all target databases.
    *   Crucially, it will mandate that the LLM's final output is a single, structured JSON object containing all generated queries.

3.  **Dynamic Prompt Generation Command:**
    *   A new Gemini command, `/generate_multidb_prompt`, will be created. This command will be the user's primary interface for setting up a new multi-database query generation task.
    *   It will accept a list of target databases (e.g., `--databases "pubmed,scopus"`).
    *   It will read `database_guidelines.md`, select the relevant sections, and inject them into the `prompt_template_multidb.md` to create a final, fully-formed prompt.
    *   The output of this command is another, runnable Gemini command (e.g., `/run_my_study_all_db`).

4.  **Unified "Run-Once" Execution:**
    *   The user will execute the newly generated command (e.g., `/run_my_study_all_db`) just once.
    *   The agent will execute the complex prompt, receive the single JSON output from the LLM, parse it, and automatically write the queries to their respective files (`queries.txt`, `queries_scopus.txt`, etc.) in a single, atomic operation.

## Benefits of this Approach

*   **Scalability & Maintainability:** Database-specific rules are decoupled from the prompt logic, making it easy to add new databases or update rules.
*   **Consistency:** The system guarantees that the same number of queries are generated for each database, ensuring the downstream pipeline functions correctly.
*   **Powerful Automation:** The entire process, from a study protocol to a complete set of multi-database query files, is automated through a simple two-stage command workflow.

# New January 2026 Future Plans

## 1 Add the DOI checking and Evaluate Aggregation Strategies to DOI 
Currently, we use PubMed IDs (PMIDs) to validate and aggregate study records across multiple sources. However, this approach has limitations, especially when dealing with studies not indexed in PubMed. So as a future plan, we will transition to using Digital Object Identifiers (DOIs) as the primary identifier for study validation and aggregation.


## 2 DOI and pmid extraction automation

The idea is in the first step we have converted the systematic review paper to markdwon format using the conda environment doclingo. From here we can 
1. extract the list of the studies included in the systematic review. This can be supported by give a solid list of instructions to the LLM to extract the studies in a structured format. We can extract the Title, Authors, Journal, Year, DOI (if it exists), and PMID (if it exists).
2. In the mose cases, the DOI and PMID will not be available in the systematic review paper. So we can 
 - use the searh tools like #web to search and extract the DOI or PMID (this can be done based on the flag that ask the LLM to choose DOI or PMID). 
 - Other options is to use the set of API keys already available in the project to search for the DOI and PMID based on the Title, Authors, Journal, and Year information.
 - Or add a new CrossRef API key to search for the DOI based on the Title, Authors, Journal, and Year information.

3. once we have the DOI and PMID extracted, we can use the existing scripts to validate the studies based on the DOI and PMID. We can also use the DOI to aggregate the studies across multiple sources.

4. One extra gained functionality here, and that should be taken into consideration, is that we can use the DOI extraction at any place/point of the workflow/project to utilise the DOI extraction.
    - For example, this can be in the aggregation to get the DOI. 


## 3 Validation of the results across multiple sources for the recall and precision evaluation
The idea is that after testing the workflwow over multiple systematic reviews, we need to evaluate the recall and precision of the generated queries based on the aggregated results across multiple sources.

More specifically, We need to build an evaluation framework that can compare the evaluated results of the aggregation for all the systematic reviews and give a comprehensive report on the recall and precision over the aggregation availbe methods of the generated queries approach.  

The validation need to ba able to take into considearation any number of final aggregated results from multiple systemic reviews and give a comprehensive report on the recall and precision over the aggregation available methods of the generated queries approach.

It also has to be independent of the previous steps and take as input only the final aggregated results from multiple systemic reviews and the gold standard studies included in the systematic review. Maybe use jason files to store the aggregated results from multiple systemic reviews and the gold standard studies included in the systematic review.

## 4 Create a new prompt files as vs code compatible
Currently we have the commands in. a gemini format. However, to expand the usability of the prompt files, we can create a new set of prompt files that are compatible with VS Code. This will allow users to easily edit and manage the prompt files using a popular code editor.

This has to keep the commands generation and workflow steps excately the same it is right now in the gemini. So better to copy the text and then only adjust the yaml headers to be compatible with VS Code.
