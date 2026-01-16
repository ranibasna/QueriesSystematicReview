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
Generate comprehensive, database-ready search queries for this systematic review.
- Prioritize recall over precision (when in doubt, choose broader queries)
- Use controlled vocabulary (MeSH, Emtree) where available
- Include synonyms, alternative spellings, and truncation
- Apply exclusion operators (NOT) cautiously to avoid missing studies
- Ensure free-text terms are consistent across databases

---
## DATABASE-SPECIFIC GUIDELINES
[DATABASE_SPECIFIC_GUIDELINES]
---

## Precision_Knobs Framework

The DATABASE-SPECIFIC GUIDELINES section above contains categorized Precision_Knobs for each database. These knobs are organized into functional categories:

- **Filter Knobs:** Species, language, document type, subject area restrictions
- **Scope Knobs:** Field restrictions (title, abstract), major/focus headings
- **Vocabulary Knobs:** Explosion control, term specificity
- **Design Knobs:** Study methodology requirements
- **Exclusion Knobs:** Publication type filters
- **Proximity Knobs:** Term co-occurrence requirements

When generating micro-variants in extended/exhaustive levels:
- **Filter-based variant:** Uses knobs from the "Filter Knobs" category
- **Field/Scope-based variant:** Uses knobs from the "Scope Knobs" category
- **Proximity-based variant:** Uses knobs from the "Proximity Knobs" category (or falls back to "Scope Knobs" for databases without proximity operators like PubMed)

Note: Placeholders like `[CONCEPT]`, `[TERM]`, `[MESH_TERM]` should be replaced with actual study-specific concepts from your PICOS framework.

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
4.  **Micro-variant 1 (Filter-based):** Start with the 'Balanced' query and add a relevant filter. Look under "Filter Knobs" in the Precision_Knobs section for the current database (e.g., `humans[Filter]` for PubMed, `DOCTYPE(ar OR re)` for Scopus).
5.  **Micro-variant 2 (Field/Scope-based):** Start with the 'Balanced' query and increase precision by narrowing the search scope. Look under "Scope Knobs" in the Precision_Knobs section (e.g., `[ti]` for PubMed, `TITLE(...)` for Scopus).
6.  **Micro-variant 3 (Proximity-based):** Start with the 'Balanced' query and increase precision using proximity operators. Look under "Proximity Knobs" in the Precision_Knobs section (e.g., `W/5` for Scopus, `ADJ5` for Embase). 
   
   **For databases without proximity operators (e.g., PubMed):** Fall back to the "Scope Knobs" category and prefer major heading/focus mechanisms (e.g., `[majr]` for PubMed, `*term` for Embase). If no major heading mechanism exists, use title restriction from Scope Knobs.

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
4.  **Micro-variant 1 (Filter):** Start with 'Balanced' and add a filter knob. Look under "Filter Knobs" in the Precision_Knobs section for the current database.
5.  **Micro-variant 2 (Scope):** Start with 'Balanced' and add a scope-narrowing knob. Look under "Scope Knobs" in the Precision_Knobs section.
6.  **Micro-variant 3 (Proximity):** Start with 'Balanced' and add a proximity knob. Look under "Proximity Knobs" in the Precision_Knobs section. For databases without proximity operators (e.g., PubMed), fall back to "Scope Knobs" and prefer major heading mechanisms.
7.  **Micro-variant 4 (Combo: Scope + Filter):** Start with 'Balanced' and combine one Scope Knob and one Filter Knob.
8.  **Micro-variant 5 (Combo: Scope + Proximity):** Start with 'Balanced' and combine one Scope Knob and one Proximity Knob (or two Scope Knobs if no proximity available).
9.  **Micro-variant 6 (Exclusion):** Start with 'High-precision' and add an exclusion knob. Look under "Exclusion Knobs" in the Precision_Knobs section for publication type filters.

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

## Expected JSON Output Format

Your JSON Query Object should follow this structure, with database names as keys and arrays of query strings as values. Each query string must include a leading comment line (starting with '#') explaining the strategy:

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

Note: The number of queries per database depends on the level (basic: 3, extended: 6, keywords: 4, exhaustive: 9).



---

## FINAL TASK: Update Project Files
Based on the generated content, perform the following steps:

1.  **Update Search Strategy Document:** Overwrite the `studies/[STUDY_NAME]/search_strategy.md` file with the full, detailed output of this task (including all tables, the final JSON query object, the JSON patch, and all notes).

2.  **Generate a Query File for Each Database:**
    - First, apply any revisions from the `json_patch` object to the main 
     `JSON Query Object` (replace queries at specified indices).
    - For each database key in the now-corrected query object:
      - Determine the correct filename:
        - If the key is `pubmed`, the filename is `studies/[STUDY_NAME]/queries.txt`.
        - For all other keys, the filename is `studies/[STUDY_NAME]/queries_{database_name}.txt` (e.g., `queries_scopus.txt`).
      - Write the list of corrected queries from the JSON object into that file. Each query must be separated by a blank line.
