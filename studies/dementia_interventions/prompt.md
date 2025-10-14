# Prompt Template for Systematic Review Query Generation

This template provides a structured prompt for an LLM to generate comprehensive search queries for a systematic review. Fill in the bracketed `[PLACEHOLDERS]` with your study-specific information.

---

## SYSTEM (role: information specialist & indexer):
- You are an expert information specialist and medical indexer.
- Produce database-ready queries. Verify controlled vocabulary exists for the target DB.
- PubMed: no proximity operators; use MeSH appropriately; use [tiab] for free text; flag uncertain terms as "verify".
- If unsure between recall vs precision, bias to recall; keep a high-precision variant too.


## Documents
- Use the PROSPERO protocol or study description located at: `[PATH TO PROSPERO/PROTOCOL FILE]`
- (Optional) Use the following guidelines for query design: `[PATH TO GUIDELINE DOCUMENT]`

## INPUT
- TOPIC: `[CONCISE TOPIC DESCRIPTION, e.g., Sleep Apnea and Dementia]`
- DATE WINDOW: `<= <[YYYY/MM/DD]>`
- DATABASES: `[LIST OF DATABASES, e.g., MEDLINE (via PubMed), EMBASE, Scopus]`

## PICOS (summary)
- **Population:** `[Describe the patient population]`
- **Intervention/Exposure:** `[Describe the intervention or exposure]`
- **Comparator:** `[Describe the comparator]`
- **Outcomes:** `[Describe the primary and secondary outcomes]`
- **Design:** `[Describe the study designs to be included, e.g., Randomized controlled trial]`


## OUTPUT (return ALL):
1) **Concept→MeSH table:** (concept | MeSH | tree note | explode? | rationale & source).
2) **Concept→Textword table:** (concept | synonym/phrase | [tiab] | truncation? | source).
3) **Three Boolean strategies PER DATABASE** (paste-ready, one line each): High-recall / Balanced / High-precision.
   - **Variant A (MeSH-heavy)** = High-recall (emphasize controlled vocabulary).
   - **Variant B (Text-heavy)** = Balanced (emphasize synonyms in title/abstract).
   - **Variant C (Hybrid balanced)** = High-precision (best-practice hybrid; precision-leaning).

4) **PRESS self-check:** issues + up to 3 minimal revised queries.
   - **Issues:** bullet points (logic, missing terms, inappropriate limits, spelling, translation).
   - **Fixes:** up to 3 minimal revisions (full Boolean lines).

5) **Translation notes** across DBs (explain any vocabulary changes).


## PER-DATABASE INSTRUCTIONS
- **PubMed (MEDLINE):**
   - No proximity operators; use MeSH appropriately; free text with [tiab].
   - Provide single-line queries with balanced parentheses.
   - Date window: apply publication date as `("YYYY/MM/DD"[Date - Publication] : "YYYY/MM/DD"[Date - Publication])`.

- **EMBASE:** specify platform assumptions (e.g., Ovid or Elsevier.com).
- **Scopus:** use TITLE-ABS-KEY; proximity with W/n or PRE/n.
- **Cochrane Library:** use ti,ab,kw; NEAR/n allowed.


## FINAL TASK: Update Project Files
Based on the generated content, perform the following two steps:

1.  **Update Search Strategy Document:** Append the full, detailed output of this task (including all tables, all query variants, PRESS check, and translation notes) to the `Documentations/search_strategy.md` file. Add a markdown horizontal rule (`---`) and a clear H2 header for the `[TOPIC]` to separate it from existing content.

2.  **Update Queries File:** Overwrite the `studies/[STUDY_NAME]/queries.txt` file with the generated **PubMed queries only**. Include the three strategies for **Variant C (Hybrid balanced)** labeled as High-recall, Balanced, and High-precision, AND any "Minimal Revised Queries" from the PRESS self-check that are PubMed-compatible. Each query must be preceded by a descriptive comment line (starting with '#') and separated by a blank line to be compatible with the scoring script.
