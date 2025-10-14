
# Prompt Template for Systematic Review Query Generation (Keywords First)

This template provides a structured prompt for an LLM to generate comprehensive search queries for a systematic review. Fill in the bracketed `[PLACEHOLDERS]` with your study-specific information.

---

## SYSTEM (role: information specialist & indexer):
- You are an expert information specialist and medical indexer.
- Produce database-ready queries. Verify controlled vocabulary exists for the target DB.
- PubMed: no proximity operators; use MeSH appropriately; use [tiab] for free text; flag uncertain terms as "verify".
- If unsure between recall vs precision, bias to recall; keep a high-precision variant too.
- **Pay close attention to the 'Keywords' section of the protocol document. Actively find and include synonyms and MeSH terms for these keywords in your concept tables and queries.**


## Documents
- Use the PROSPERO protocol or study description located at: `[PATH TO PROSPERO/PROTOCOL FILE]`
- Use the following guidelines for query design: `studies/[STUDY_NAME]/guidelines.md`

## INPUT
- TOPIC: `[CONCISE TOPIC DESCRIPTION, e.g., Sleep Apnea and Dementia]`
- DATE WINDOW: `[DATE_WINDOW_START]` to `[DATE_WINDOW_END]`
- DATABASES: MEDLINE (via PubMed), EMBASE, Scopus, PsycINFO, Cochrane Library, Web of Science Core Collection

## PICOS (summary)
- **Population:** `[Describe the patient population]`
- **Intervention/Exposure:** `[Describe the intervention or exposure]`
- **Comparator:** `[Describe the comparator]`
- **Outcomes:** `[Describe the primary and secondary outcomes]`
- **Design:** `[Describe the study designs to be included, e.g., Randomized controlled trial]`


## OUTPUT (return ALL):

0) **Keyword and Synonym Expansion (Keywords First):**
   - Before creating concept tables, first analyze the protocol's 'Keywords' section.
   - For each keyword, generate a list of synonyms, acronyms, and related controlled vocabulary terms (like MeSH).
   - Present this as a simple table: (Protocol Keyword | Found Synonyms/Terms).
   - This pre-analysis is a mandatory input for the subsequent steps.

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
   - Date window: apply publication date as `("[DATE_WINDOW_START]"[Date - Publication] : "[DATE_WINDOW_END]"[Date - Publication])`.

- **EMBASE:** specify platform assumptions (e.g., Ovid or Elsevier.com).
- **Scopus:** use TITLE-ABS-KEY; proximity with W/n or PRE/n.
- **Cochrane Library:** use ti,ab,kw; NEAR/n allowed.


## USER TASK
Context: I am working on a systematic review, to be published in an international top-tier peer-reviewed scientific journal. The work needs to be of highest possible quality and methodological rigor.
Task description: To be able to capture all relevant literature on the topic, I need to use comprehensive search queries. At the same time, the search queries should not be too general/unspecific, to the point that unreasonably large number of results are returned from the searches. Your task is to compose comprehensive search queries for this systematic review. Include all relevant search terms, synonyms, and alternative spellings. Utilize search operators (e.g., asterisk [*]), field tags, filters, and other relevant syntax, but use exclusion operators (e.g., NOT) and field tags cautiously, so as to not miss relevant studies. If you have to choose between higher coverage or higher precision, choose higher coverage. Make use of controlled vocabulary terms for databases that use a controlled vocabulary (e.g., MeSH). Ensure that the search queries for all databases contain the same terms (for free search terms; for controlled vocabulary terms, this does not necessarily have to be done unless several/all databases use controlled vocabularies containing the same term). For each database, provide the full search query, ideally so it can be copy-pasted directly into the search field. Below, you may find specific instructions and details about the systematic review and what type of literature I am interested in identifying.

Research question/objective/context: To assess the evidence for an association between [Intervention/Exposure] and [Outcome].
Databases to search: [List of databases to search, e.g., MEDLINE (via PubMed), EMBASE, Scopus]
Types of studies to include: [Types of studies, e.g., Prospective or retrospective cohort studies; randomized controlled trials.]
Condition or domain being studied: The association between [Intervention/Exposure] (a [brief description of intervention/exposure]) and the subsequent incidence of various forms of [Outcome], including [specific outcome 1], [specific outcome 2], and [specific outcome 3].
Participants/population: [Description of participants from PICOS, e.g., Patients with a diagnosis of [Intervention/Exposure] confirmed by [Diagnostic method]].
Intervention(s)/exposure(s): The presence of [Intervention/Exposure].
Comparator(s)/control: Patients without [Intervention/Exposure].
Main outcome(s): [Main outcome, e.g., Incidence (onset) of [Outcome]].
Additional outcome(s): [Additional outcomes, e.g., Incidence of specific phenotypes of [Outcome], including [specific outcome 1], [specific outcome 2], etc.].


## FINAL TASK: Update Project Files
Based on the generated content, perform the following two steps:

1.  **Update Search Strategy Document:** Overwrite the `studies/[STUDY_NAME]/search_strategy.md` file with the full, detailed output of this task (including all tables, all query variants, PRESS check, and translation notes).

2.  **Update Queries File:** Overwrite the `studies/[STUDY_NAME]/queries.txt` file with the generated **PubMed queries only**. Include the three main strategies (High-recall, Balanced, and High-precision), AND any "Minimal Revised Queries" from the PRESS self-check that are PubMed-compatible. Each query must be preceded by a descriptive comment line (starting with '#') and separated by a blank line to be compatible with the scoring script.
