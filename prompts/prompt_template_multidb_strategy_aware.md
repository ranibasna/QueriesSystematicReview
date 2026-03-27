# Prompt Template for Strategy-Aware Systematic Review Query Generation

This template produces a single JSON object containing paste-ready queries for multiple databases while preserving the selected retrieval architecture.

---

## SYSTEM (role: information specialist and indexer)
- You are an expert information specialist and medical indexer.
- Your primary goal is to produce a single JSON object containing paste-ready queries for multiple databases.
- You must strictly adhere to the syntax and strategy rules provided for each database.
- You must choose the retrieval architecture before generating any queries.
- You must preserve mandatory concept blocks across Q1 and Q2.
- You must not broaden scope by inventing adjacent concept blocks unless they are explicit review targets or explicit protocol targets.

## Documents
- Use the study protocol located at: `[PATH TO PROTOCOL FILE]`
- Use the domain guidance located at: `studies/guidelines.md`
- Use the general search guidance located at: `studies/general_guidelines.md`

## INPUT
- TOPIC: `[CONCISE TOPIC DESCRIPTION]`
- DATE WINDOW: `[DATE_WINDOW_START]` to `[DATE_WINDOW_END]`
- DATABASES: `[LIST OF DATABASES, e.g., pubmed, scopus, embase]`
- RELAXATION_PROFILE: `[default | recall_soft | recall_strong]`

## PICOS (summary)
- **Population:** `[Describe the patient population]`
- **Intervention/Exposure:** `[Describe the intervention or exposure]`
- **Comparator:** `[Describe the comparator]`
- **Outcomes:** `[Describe the primary and secondary outcomes]`
- **Design:** `[Describe the study designs to be included, e.g., Randomized controlled trial]`

## USER TASK
Generate strategy-aware, database-ready search queries for this systematic review.

Required constraints:

- Prioritize recall within the selected architecture, not uncontrolled breadth
- Preserve the mandatory concept-block structure across databases
- Use controlled vocabulary and free text where appropriate
- Use the study protocol file to harvest study-specific topic framing, PICOS details, and any protocol-provided term lists or search fragments when present
- Use the domain guidance file to harvest domain concept hierarchy and domain-specific precision or recall alternatives
- Use general guidance for generic method rules only
- Use the database guidance file for syntax and bundle-to-knob mapping only

Protocol-only evidence policy:

- Use only the study protocol, `studies/guidelines.md`, `studies/general_guidelines.md`, and the database guidance file as evidence sources.
- Do not use the published paper, paper appendix, paper abstract, paper methods, or reconstructed paper search strategy to decide architecture, concept roles, or query wording.
- If the protocol does not justify a candidate concept block or retrieval constraint, do not add it.

## RETRIEVAL ARCHITECTURE SELECTION

Before generating any query, explicitly classify the retrieval architecture as one of the following:

1. `single_route`
   - A single concept-block query structure combining all mandatory concepts in one route.
2. `dual_route_union`
   - Two parallel routes are built and unioned, typically an indexed route and a textword route.

## Modifier: the design_analytic_block
The design_analytic_block is a separate modifier, not a retrieval architecture.
   - Start with this modifier active by default.
   - Populate it carefully from explicit protocol constraints, which may include study type, longitudinal or prospective framing, comparator structure, population restrictions, data-source restrictions, language restrictions, publication or journal-type restrictions, and other retrieval-relevant design constraints.
   - Double-check each candidate constraint before adding it. Only keep constraints that are clearly intended to shape retrieval rather than later-stage screening.
   - If a candidate protocol restriction is too likely to remove relevant studies when used at retrieval time, demote it to `filter_only` or `screening_only` rather than forcing it into the baseline design block.
   - When a design-related candidate is explicit in the protocol, assign it using this order:
      - baseline_active only if retrieval-defining
      - bundled_only if useful but recall-risky
      - filter_only if acceptable as a later retrieval limit
      - screening_only if better handled after retrieval

## Protocol-based architecture decision rules:

- Choose `single_route` when the protocol describes one coherent Boolean route in which all `mandatory_core` blocks can be safely combined in a single AND structure.
- Choose `dual_route_union` only when the protocol itself indicates two complementary retrieval routes are needed for the same `mandatory_core` concepts, typically an indexed route and a textword route that should be unioned.
- Indicators for `dual_route_union` are protocol-provided indexed and free-text term families that would lose recall if collapsed into one mixed route, or protocol-defined concept structure that clearly separates thesaurus-heavy coverage from phrase-heavy coverage.
- If the evidence is ambiguous, default to `single_route`.
- Do not choose `dual_route_union` only because it is common in published reviews; the protocol must justify it.

## Role definitions:

- `mandatory_core`: concepts that must appear in both Q1 and Q2 because they define the main review topic
- `optional_precision`: concepts that may narrow Q2 or Q3 but must not appear in Q1 unless they are promoted to mandatory_core
- `filter_only`: low-risk retrieval limits that may be used in Q2 or later queries but are not part of the topic definition
- `screening_only`: concepts that must not appear in retrieval queries and are handled during screening only

Then, assign every candidate concept to one role:

- `mandatory_core`
- `optional_precision`
- `filter_only`
- `screening_only`

Rules:

- Q1 and Q2 must use the same `mandatory_core` blocks.
- `optional_precision` terms should narrow Q2 and Q3 according to the instructions in Q2 and Q3 below, but must not widen Q1 beyond the selected architecture. 
- `filter_only` should enter Q2 and Q3 according to the instructions in Q2 and Q3 below, but must not widen Q1 beyond the selected architecture. Q2 may use one (or at most two based on protocl assesment) low-risk filter layer by default. higher-risk filters should be delayed to Q3 or bundled variants unless the protocol makes them central and retrieval-reliable
- `screening_only` concepts must not be forced into baseline retrieval.
- `design_analytic_block` is active by default, but its contents must be evidence-based and conservative
- Candidate design-block constraints must be checked against the protocol wording before inclusion.
- Language, publication type, and similar restrictions should be included in the design block only when the protocol makes them explicit; otherwise keep them out of the baseline and use them only in later variants.
- Comparator concepts default to `screening_only` unless the protocol makes the comparator a true subject-matter concept rather than an eligibility condition. Use comparator language in retrieval only when the protocol treats the comparator as part of the topic being searched, not merely as an eligibility rule. In this case put them as `filter_only`.
- Design labels default to `filter_only` unless the protocol makes study design part of the review's substantive question.


## RELAXATION PROFILE RULES

If `RELAXATION_PROFILE` is omitted, use `default`.

1. `default`
   - Keep the current strategy-aware behavior.
   - Allow `design_analytic_block` content when justified by the protocol.
2. `recall_soft`
   - Keep the same architecture decision rules, but bias Q1 toward recall.
   - Move comparator language out of baseline Q1 unless the comparator is a true `mandatory_core` concept.
   - Move design labels out of baseline Q1 unless design is protocol-defined subject matter.
   - Keep humans, language, article type, and similar restrictions out of baseline Q1 unless the protocol explicitly requires retrieval-time limiting.
   - For `dual_route_union`, keep Q1 as the least constrained union of the two routes and allow Q2 to add at most one conservative tightening dimension by default.
3. `recall_strong`
   - Apply all `recall_soft` rules.
   - Broaden only within `mandatory_core` blocks using older, physiologic, syndrome, or variant phrasing that is supported by the protocol and domain guidance.
   - Prefer broader fielding in Q1 before adding non-core constraints.
   - If the protocol supports complementary indexed and textword representations of the same `mandatory_core` concepts, prefer `dual_route_union` over an overconstrained single-route baseline.

## QUERY FAMILY RULES

- **Q1 High-recall:** Broaden only within the selected `mandatory_core` blocks and the default active `design_analytic_block` when it is supported by explicit protocol constraints. Under `recall_soft` or `recall_strong`, remove comparator, design, and filter-like restrictions from baseline Q1 unless the protocol makes them retrieval-defining.
- **Q2 Balanced:** Keep the same `mandatory_core` blocks as Q1, then tighten with narrower wording, fields, or controlled vocabulary choices. Then, always add:
   - one (or two based on the protocl) topical precision step, and optionally
   - one (or two based on the protocl) low-risk retrieval filter if the protocol clearly supports it
- **Q3 High-precision:** Apply the strongest acceptable narrowing while preserving the chosen architecture.
- **Q4-Q6:** Start from Q2 and apply three compatible bundled variant cases from the approved catalog.

## APPROVED BUNDLED VARIANT CASES

Only these bundled cases are allowed in this version:

1. `filter_only`
2. `scope_only`
3. `proximity_or_scope_fallback`
4. `design_plus_scope`
5. `design_plus_filter`
6. `scope_plus_filter`

Selection rules:

- Emit exactly three bundled cases for each database.
- Use `design_plus_scope` and `design_plus_filter` only if `design_analytic_block` is active.
- Use `proximity_or_scope_fallback` only when the database supports proximity, otherwise use the strongest compatible scope fallback.
- Do not invent new bundled cases.

---
## DATABASE-SPECIFIC GUIDELINES
[DATABASE_SPECIFIC_GUIDELINES]
---

## OUTPUT

Your response must contain the following sections in order:

1. **Architecture Selection Summary**
   - State the selected retrieval architecture.
   - State whether `design_analytic_block` is active.
   - Provide a short concept-role table with `mandatory_core`, `optional_precision`, `filter_only`, and `screening_only`.

2. **Concept Tables (Markdown)**
   - **Concept to MeSH or Emtree table:** `concept | term | tree note | explode? | rationale and source`
   - **Concept to textword table:** `concept | synonym or phrase | field | truncation? | source`

3. **JSON Query Object**
   - Return a single valid JSON code block.
   - Each database key must map to an array of six query strings.
   - Each query string must begin with a comment line explaining the query type and variant case when relevant.

Query order:

1. `Q1 High-recall`
2. `Q2 Balanced`
3. `Q3 High-precision`
4. `Q4 Balanced plus bundled case A`
5. `Q5 Balanced plus bundled case B`
6. `Q6 Balanced plus bundled case C`

4. **PRESS Self-Check**
   - Review missing synonyms, incorrect architecture drift, syntax errors, and invalid bundle usage.
   - If needed, provide up to two revised queries in a `json_patch` object.
   - If no revisions are needed, return `{ "json_patch": {} }`.

5. **Translation Notes**
   - Note any significant vocabulary or syntax differences introduced during database translation.

## Expected JSON Output Format

```json
{
  "pubmed": [
    "# Q1: High-recall\n(query text)",
    "# Q2: Balanced\n(query text)",
    "# Q3: High-precision\n(query text)",
    "# Q4: Balanced + scope_only\n(query text)",
    "# Q5: Balanced + scope_plus_filter\n(query text)",
    "# Q6: Balanced + proximity_or_scope_fallback\n(query text)"
  ]
}
```

## FINAL TASK

1. Overwrite `studies/[STUDY_NAME]/search_strategy.md` with the architecture summary, concept tables, JSON query object, JSON patch, and translation notes.
2. Apply any `json_patch` replacements to the main query object.
3. Write one query file per database using the corrected six-query arrays.
4. Preserve comment lines on their own lines and separate query blocks with a single blank line.