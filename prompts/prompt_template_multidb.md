# Prompt Template for Systematic Review Query Generation (Multi-Database)

This template provides a structured prompt for an LLM to generate comprehensive, balanced, and tailored search queries for multiple databases simultaneously.

---

## SYSTEM (role: information specialist & indexer):
- You are an expert information specialist and medical indexer.
- Your primary goal is to produce a single JSON object containing paste-ready queries for multiple databases.
- You must strictly adhere to the syntax and strategy rules provided for each database.
- If unsure between recall vs precision, bias towards recall, but generate high-precision variants as requested.
- **Pay close attention to the 'Keywords' section of the protocol document. Actively find and include synonyms and controlled vocabulary for these keywords in your concept tables and queries.**

## Documents
- Use the PROSPERO protocol or study description located at: `[PATH TO PROSPERO/PROTOCOL FILE]`
- Use the following guidelines for query design: `studies/[STUDY_NAME]/guidelines.md`
- Use the general guidelines for query design: `studies/[STUDY_NAME]/general_guidelines.md`

## INPUT
- TOPIC: `[CONCISE TOPIC DESCRIPTION, e.g., Sleep Apnea and Dementia]`
- DATE WINDOW: `[DATE_WINDOW_START]` to `[DATE_WINDOW_END]`
- DATABASES: `[LIST OF DATABASES, e.g., pubmed, scopus, embase]`

## PICOS (summary)
- **Population:** `[Describe the patient population]`
- **Intervention/Exposure:** `[Describe the intervention or exposure]`
- **Comparator:** `[Describe the comparator]`
- **Outcomes:** `[Describe the primary and secondary outcomes]`
- **Design:** `[Describe the study designs to be included, e.g., Randomized controlled trial]`

## USER TASK
Context: I am working on a systematic review, to be published in an international top-tier peer-reviewed scientific journal. The work needs to be of highest possible quality and methodological rigor.
Task description: To be able to capture all relevant literature on the topic, I need to use comprehensive search queries. At the same time, the search queries should not be too general/unspecific, to the point that unreasonably large number of results are returned from the searches. Your task is to compose comprehensive search queries for this systematic review. Include all relevant search terms, synonyms, and alternative spellings. Utilize search operators (e.g., asterisk [*]), field tags, filters, and other relevant syntax, but use exclusion operators (e.g., NOT) and field tags cautiously, so as to not miss relevant studies. If you have to choose between higher coverage or higher precision, choose higher coverage. Make use of controlled vocabulary terms for databases that use a controlled vocabulary (e.g., MeSH). Ensure that the search queries for all databases contain the same terms (for free search terms; for controlled vocabulary terms, this does not necessarily have to be done unless several/all databases use controlled vocabularies containing the same term). For each database, provide the full search query, ideally so it can be copy-pasted directly into the search field.

---
## DATABASE-SPECIFIC GUIDELINES
[DATABASE_SPECIFIC_GUIDELINES]
---

## OUTPUT (Your entire response should be a single block of text containing the following sections)

--- START LEVEL-SPECIFIC INSTRUCTIONS ---

--- LEVEL: basic ---
### 1. Concept Tables (Markdown)
- **Concept→MeSH/Emtree table:** (concept | term | tree note | explode? | rationale & source).
- **Concept→Textword table:** (concept | synonym/phrase | field | truncation? | source).

### 2. JSON Query Object (MUST be a single valid JSON code block)
Generate **3 queries** for each database:
1.  **High-recall:** (Emphasize controlled vocabulary, broad terms).
2.  **Balanced:** (A hybrid of controlled vocabulary and free-text synonyms).
3.  **High-precision:** (Emphasize major focus terms, title searches, and specific synonyms).

Return a single, valid JSON code block containing all the queries. The keys must be the database names from the `INPUT` section. The value for each key must be an array of strings, with each string being a complete, paste-ready query. For each query, include a leading comment line explaining the strategy.

### 3. PRESS Self-Check (JSON Patch)
- After generating the main JSON Query Object, critically review your own work.
- If you identify any significant issues (e.g., a missing synonym, a logical error), provide up to **2 revised queries** in a `json_patch` object.
- The `json_patch` object must use keys corresponding to the database and the 0-based index of the query to be replaced.
- **Example `json_patch`:**
  ```json
  {
    "json_patch": {
      "pubmed": {
        "0": "# High-recall (revised): (the new, corrected query...)"
      }
    }
  }
  ```
- If no revisions are needed, you must return an empty `json_patch` object: `{ "json_patch": {} }`.
- **Translation Notes:** Also include any notes on significant vocabulary or syntax changes made between databases.
--- END LEVEL: basic ---

--- LEVEL: extended ---
### 1. Concept Tables (Markdown)
- **Concept→MeSH/Emtree table:** (concept | term | tree note | explode? | rationale & source).
- **Concept→Textword table:** (concept | synonym/phrase | field | truncation? | source).

### 2. JSON Query Object (MUST be a single valid JSON code block)
Generate **6 queries** for each database by following this specific recipe:
1.  **High-recall:** (Emphasize controlled vocabulary, broad terms).
2.  **Balanced:** (A hybrid of controlled vocabulary and free-text synonyms).
3.  **High-precision:** (Emphasize major focus terms and specific synonyms).
4.  **Micro-variant 1 (Filter-based):** Start with the 'Balanced' query and add a relevant filter. Look in the `Precision_Knobs` list for the current database for knobs related to filters (e.g., `humans[Filter]`, `DOCTYPE(ar OR re)`).
5.  **Micro-variant 2 (Field/Scope-based):** Start with the 'Balanced' query and increase precision by narrowing the search scope. Look in the `Precision_Knobs` list for knobs related to field codes (e.g., `dementia[ti]`, `TITLE(...)`).
6.  **Micro-variant 3 (Proximity-based):** Start with the 'Balanced' query and increase precision using proximity operators. Look in the `Precision_Knobs` list for knobs related to proximity (e.g., `W/5`, `ADJ5`). If no proximity operators are available for a database (like PubMed), use a different knob, such as a major focus heading (`[majr]`).

To generate these queries, you must use the `Precision_Knobs` list found in the `DATABASE-SPECIFIC GUIDELINES` section, which is visible to you in this prompt. Return a single, valid JSON code block containing all the queries. The keys must be the database names from the `INPUT` section. The value for each key must be an array of strings, with each string being a complete, paste-ready query. For each query, include a leading comment line explaining the strategy.

### 3. PRESS Self-Check (JSON Patch)
- After generating the main JSON Query Object, critically review your own work.
- If you identify any significant issues (e.g., a missing synonym, a logical error), provide up to **2 revised queries** in a `json_patch` object.
- The `json_patch` object must use keys corresponding to the database and the 0-based index of the query to be replaced.
- **Example `json_patch`:**
  ```json
  {
    "json_patch": {
      "pubmed": {
        "0": "# High-recall (revised): (the new, corrected query...)"
      }
    }
  }
  ```
- If no revisions are needed, you must return an empty `json_patch` object: `{ "json_patch": {} }`.
- **Translation Notes:** Also include any notes on significant vocabulary or syntax changes made between databases.
--- END LEVEL: extended ---

--- LEVEL: keywords ---
### 0. Keyword and Synonym Expansion (Keywords First)
- Before creating concept tables, first analyze the protocol's 'Keywords' section.
- For each keyword, generate a list of synonyms, acronyms, and related controlled vocabulary terms (like MeSH).
- Present this as a simple markdown table: (Protocol Keyword | Found Synonyms/Terms).
- This pre-analysis is a mandatory input for the subsequent steps.

### 1. Concept Tables (Markdown)
- **Concept→MeSH/Emtree table:** (concept | term | tree note | explode? | rationale & source).
- **Concept→Textword table:** (concept | synonym/phrase | field | truncation? | source).

### 2. JSON Query Object (MUST be a single valid JSON code block)
Generate **4 queries** for each database:
1.  **Keyword-focused:** A broad query that prioritizes the terms found in the "Keyword and Synonym Expansion" step.
2.  **High-recall:** (Emphasize controlled vocabulary, broad terms).
3.  **Balanced:** (A hybrid of controlled vocabulary and free-text synonyms).
4.  **High-precision:** (Emphasize major focus terms, title searches, and specific synonyms).

Return a single, valid JSON code block containing all the queries. The keys must be the database names from the `INPUT` section. The value for each key must be an array of strings, with each string being a complete, paste-ready query. For each query, include a leading comment line explaining the strategy.

### 3. PRESS Self-Check (JSON Patch)
- After generating the main JSON Query Object, critically review your own work.
- If you identify any significant issues (e.g., a missing synonym, a logical error), provide up to **2 revised queries** in a `json_patch` object.
- The `json_patch` object must use keys corresponding to the database and the 0-based index of the query to be replaced.
- **Example `json_patch`:**
  ```json
  {
    "json_patch": {
      "pubmed": {
        "0": "# High-recall (revised): (the new, corrected query...)"
      }
    }
  }
  ```
- If no revisions are needed, you must return an empty `json_patch` object: `{ "json_patch": {} }`.
- **Translation Notes:** Also include any notes on significant vocabulary or syntax changes made between databases.
--- END LEVEL: keywords ---

--- LEVEL: exhaustive ---
### 1. Concept Tables (Markdown)
- **Concept→MeSH/Emtree table:** (concept | term | tree note | explode? | rationale & source).
- **Concept→Textword table:** (concept | synonym/phrase | field | truncation? | source).

### 2. JSON Query Object (MUST be a single valid JSON code block)
Generate **9 queries** for each database by following this specific recipe:
1.  **High-recall:** (Emphasize controlled vocabulary, broad terms).
2.  **Balanced:** (A hybrid of controlled vocabulary and free-text synonyms).
3.  **High-precision:** (Emphasize major focus terms and specific synonyms).
4.  **Micro-variant 1 (Filter):** Start with 'Balanced' and add a filter knob (e.g., `humans[Filter]`, `DOCTYPE(ar OR re)`).
5.  **Micro-variant 2 (Scope):** Start with 'Balanced' and add a scope-narrowing knob (e.g., `[ti]`, `TITLE(...)`).
6.  **Micro-variant 3 (Proximity):** Start with 'Balanced' and add a proximity knob (e.g., `W/5`, `ADJ5`). If none, use another specific knob like `[majr]`.
7.  **Micro-variant 4 (Combo: Scope + Filter):** Start with 'Balanced' and combine a scope-narrowing knob and a filter knob.
8.  **Micro-variant 5 (Combo: Scope + Proximity):** Start with 'Balanced' and combine a scope-narrowing knob and a proximity knob.
9.  **Micro-variant 6 (Exclusion):** Start with 'High-precision' and add a knob that excludes certain publication types (e.g., `NOT (case reports[pt] OR letter[pt])`).

To generate these queries, you must use the `Precision_Knobs` list found in the `DATABASE-SPECIFIC GUIDELINES` section, which is visible to you in this prompt. Return a single, valid JSON code block containing all the queries. The keys must be the database names from the `INPUT` section. The value for each key must be an array of strings, with each string being a complete, paste-ready query. For each query, include a leading comment line explaining the strategy.

### 3. PRESS Self-Check (JSON Patch)
- After generating the main JSON Query Object, critically review your own work.
- If you identify any significant issues (e.g., a missing synonym, a logical error), provide up to **2 revised queries** in a `json_patch` object.
- The `json_patch` object must use keys corresponding to the database and the 0-based index of the query to be replaced.
- **Example `json_patch`:**
  ```json
  {
    "json_patch": {
      "pubmed": {
        "0": "# High-recall (revised): (the new, corrected query...)"
      }
    }
  }
  ```
- If no revisions are needed, you must return an empty `json_patch` object: `{ "json_patch": {} }`.
- **Translation Notes:** Also include any notes on significant vocabulary or syntax changes made between databases.
--- END LEVEL: exhaustive ---

--- END LEVEL-SPECIFIC INSTRUCTIONS ---

**Example JSON Structure (for 'extended' level):**
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
    "# Balanced: ...",
    "# High-precision: ...",
    "# Micro-variant 1: ...",
    "# Micro-variant 2: ...",
    "# Micro-variant 3: ..."
  ]
}
```

### 3. PRESS Self-Check & Translation Notes (Markdown)
- **Issues:** Note any potential issues (logic, missing terms, translation challenges).
- **Translation Notes:** Explain any significant vocabulary or syntax changes made between databases.

---

## FINAL TASK: Update Project Files
Based on the generated content, perform the following steps:

1.  **Update Search Strategy Document:** Overwrite the `studies/[STUDY_NAME]/search_strategy.md` file with the full, detailed output of this task (including all tables, the final JSON query object, the JSON patch, and all notes).

2.  **Generate a Query File for Each Database:**
    - Parse the main `JSON Query Object` and the `json_patch` object you created.
    - **Apply the patch:** Before writing the files, update the main query list in your memory with any revisions from the `json_patch` object.
    - For each database key in the now-corrected query object:
      - Determine the correct filename:
        - If the key is `pubmed`, the filename is `studies/[STUDY_NAME]/queries.txt`.
        - For all other keys, the filename is `studies/[STUDY_NAME]/queries_{database_name}.txt` (e.g., `queries_scopus.txt`).
      - Write the list of corrected queries from the JSON object into that file. Each query must be separated by a blank line.
