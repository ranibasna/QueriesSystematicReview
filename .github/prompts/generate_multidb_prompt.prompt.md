---
description: "Generates a runnable VS Code prompt for strategy-aware multi-database search queries"
name: generate-multidb-prompt
argument-hint: "run_study_name studies/path/to/protocol.md pubmed,scopus,wos,embase default min_date max_date"
agent: agent
tools: [filesystem]
vars:
    command_name:
        description: "Name of the command/prompt to create"
        default: "run_new_study_multidb"
    protocol_path:
        description: "Path to the protocol/prospero markdown file"
        default: "studies/study_name/prospero_study_name.md"
    databases:
        description: "Comma-separated list of target databases"
        default: "pubmed,scopus,wos,embase"
    relaxation_profile:
        description: "Strategy-aware relaxation profile"
        default: "default"
    min_date:
        description: "Earliest publication date (YYYY/MM/DD)"
        default: "1980/01/01"
    max_date:
        description: "Latest publication date (YYYY/MM/DD)"
        default: "2025/12/31"
---

You are an expert assistant for systematic reviews. Your task is to **generate and save a new VS Code prompt file** for strategy-aware multi-database query generation by following these steps:

## Input Parameters

You can provide parameters in two ways:

**Option 1: Inline arguments (recommended)**
```
gh copilot prompt --prompt-file .github/prompts/generate_multidb_prompt.prompt.md \
    --var command_name=run_study_name \
    --var protocol_path=studies/path/protocol.md \
    --var databases=pubmed,scopus,wos,embase \
    --var relaxation_profile=default \
    --var min_date=1990/01/01 \
    --var max_date=2023/12/31
```

**Option 2: Interactive prompts**
If arguments are not provided, Copilot will prompt for:
- **Command name:** ${command_name}
- **Protocol path:** ${protocol_path}
- **Databases:** ${databases}
- **Relaxation profile:** ${relaxation_profile}
- **Min date:** ${min_date}
- **Max date:** ${max_date}

## Generation Instructions

1.  **Acknowledge Inputs:** You have been given a new command name (`${command_name}`), a protocol path (`${protocol_path}`), a list of target databases (`${databases}`), a relaxation profile (`${relaxation_profile}`), a min date (`${min_date}`), and a max date (`${max_date}`).

2.  **Read Required Files:**
    *   Read the master multi-database template file: `prompts/prompt_template_multidb_strategy_aware.md`.
    *   Read the database guidelines file: `prompts/database_guidelines_strategy_aware.md`.
    *   Read the shared study guidance file: `studies/guidelines.md`.
    *   Read the shared general guidance file: `studies/general_guidelines.md`.
    *   Read the protocol file located at `${protocol_path}`.

3.  **Prepare Database-Specific Guidelines:**
    *   Parse the content of `prompts/database_guidelines_strategy_aware.md`. It contains markdown sections starting with `## {database_name}`.
    *   Create a string variable that will hold the concatenated guidelines.
    *   For each database name in the `${databases}` list (e.g., "pubmed", "scopus"):
        *   Find the corresponding markdown section in the guidelines file.
        *   Append the full text of that section to your string variable.
    *   The resulting string is your collection of database-specific guidelines.

4.  **Extract Information from Protocol:**
    *   Analyze the content of the protocol file you read.
    *   Extract the following key pieces of information:
        *   A concise topic description.
        *   The full PICOS summary (Population, Intervention/Exposure, Comparator, Outcomes, Design).

5.  **Process and Populate the Template:**
    *   Take the content of the master template file you read (`prompts/prompt_template_multidb_strategy_aware.md`).
    *   This template is the current strategy-aware six-query workflow. Do not try to recover or recreate the retired level-based instruction system.
    *   Systematically replace the following placeholders:
        *   Replace `[PATH TO PROSPERO/PROTOCOL FILE]` with the value of `${protocol_path}`.
        *   Replace `[STUDY_NAME]` with the derived study name (the folder from the protocol path).
        *   Replace `[DATE_WINDOW_START]` with `${min_date}`.
        *   Replace `[DATE_WINDOW_END]` with `${max_date}`.
        *   Replace `[LIST OF DATABASES, e.g., pubmed, scopus, embase]` with `${databases}`.
        *   Replace `[default | recall_soft | recall_strong]` with `${relaxation_profile}`.
        *   Replace `[CONCISE TOPIC DESCRIPTION]` with the topic you extracted.
        *   Replace the PICOS placeholders (`[Describe the patient population]`, etc.) with the corresponding PICOS summary you extracted.
        *   Replace `[DATABASE_SPECIFIC_GUIDELINES]` with the concatenated guidelines string you prepared in Step 3.
    *   Preserve the template's final task, which writes `studies/[STUDY_NAME]/search_strategy.md` and the per-database query files automatically when the generated prompt is executed.

6.  **Generate the New Prompt File:**
    *   You will now create a new VS Code prompt file.
    *   The name of the new file will be `.github/prompts/${command_name}.prompt.md`.
    *   Construct the content for this new file as follows:

        ```markdown
        ---
        description: "Runs the multi-database query generation prompt for the study based on ${protocol_path}"
        name: ${command_name}
        agent: agent
        tools: [filesystem]
        ---

        [INSERT THE FULLY POPULATED PROMPT TEXT FROM STEP 5 HERE]
        ```
    *   Use the filesystem tool to create this new file with the specified content.
    *   After writing the file, report that the new command `/${command_name}` has been created successfully and is ready to be executed in VS Code Copilot Chat.
    *   Explicitly mention that executing the generated command will overwrite or create `search_strategy.md` and the database-specific `queries*.txt` files automatically.

## Important Notes

- The generated prompt file must use VS Code prompt file syntax (`.prompt.md` extension with YAML frontmatter)
- All placeholders in the template must be replaced with actual values from the protocol
- The output file should be immediately executable via `/${command_name}` in VS Code Copilot Chat
- Ensure the file is written to `.github/prompts/` directory in the workspace root
- The strategy-aware flow is fixed to the current six-query family. Older level-based prompt files should be regenerated rather than copied forward.
