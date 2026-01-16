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