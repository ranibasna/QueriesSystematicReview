# Database Querying Guidelines

This file provides database-specific syntax and strategy rules for the LLM to use when generating search queries.

## PubMed
- **Syntax**: Use `[tiab]` for title/abstract searches. Use `[mh]` for MeSH terms, `[majr]` for major MeSH terms, and `[tw]` for all text words. Do not use proximity operators. Parentheses must be balanced.
- **Controlled Vocabulary**: Use MeSH (Medical Subject Headings). Validate that terms exist. Use `:NoExp` suffix to prevent automatic explosion of a broad MeSH term.
- **Date Syntax**: Use the format `("YYYY/MM/DD"[Date - Publication] : "YYYY/MM/DD"[Date - Publication])`.
- **Precision_Knobs**:
  
  **Filter Knobs (apply only when appropriate for review scope):**
  - Species filter: `humans[Filter]` - Add to restrict to human subjects only (omit for animal or mixed-species reviews)
  - Language filter: `english[Filter]` - Add to restrict to English-language publications (omit for multilingual reviews)
  
  **Scope Knobs:**
  - Title only: `[ti]` - Restrict key concepts to title field (e.g., `[CONCEPT][ti]`)
  - Major headings: `[majr]` - Use only major MeSH focus headings (e.g., `[CONCEPT][majr]`)
  
  **Vocabulary Knobs:**
  - No explosion: `[Mesh:NoExp]` - Prevent automatic MeSH tree expansion (e.g., `[MESH_TERM][Mesh:NoExp]`)
  
  **Design Knobs:**
  - Study methodology: Require study design terms in title/abstract: `(cohort[tiab] OR follow-up[tiab] OR prospective[tiab] OR retrospective[tiab] OR randomized[tiab] OR randomised[tiab] OR trial[tiab] OR rct[tiab])`
  
  **Exclusion Knobs:**
  - Publication types: `NOT (case reports[pt] OR letter[pt] OR editorial[pt] OR comment[pt])` - Exclude low-quality publication types
  
  **Proximity Knobs:**
  - Not available for PubMed (no proximity operators supported)"

## Scopus
- **Syntax**: Use `TITLE-ABS-KEY(...)` for general topic searches. Field codes like `TITLE(...)` and `ABS(...)` are also available.
- **Controlled Vocabulary**: Primarily uses Emtree, but its coverage can be inconsistent. A combination of Emtree terms and free-text words is recommended.
- **Proximity Operators**: Use `W/n` (words appear within `n` words of each other, in any order) or `PRE/n` (words appear within `n` words, in the specified order).
- **Date Syntax**: Use `PUBYEAR > YYYY` and `PUBYEAR < YYYY`. For example: `(PUBYEAR > 2019 AND PUBYEAR < 2023)`.
- **Precision_Knobs**:
  
  **Filter Knobs:**
  - Document type: `DOCTYPE(ar OR re)` - Limit to articles and reviews
  - Subject area: `SUBJAREA(MEDI)` - Limit to specific subject area (e.g., MEDI for medicine)
  
  **Scope Knobs:**
  - Title only: `TITLE([CONCEPT])` - Restrict key concepts to title field
  
  **Vocabulary Knobs:**
  - Specific terms: Use more specific Emtree terms instead of broad ones
  
  **Proximity Knobs:**
  - Tight proximity: `W/5` or `PRE/5` - Require concepts within 5 words (e.g., `[CONCEPT1] W/5 [CONCEPT2]`)

## Embase

- **Date Syntax**: Date filtering varies by platform. For inline queries, OMIT date filters entirely and apply them through the platform's interface after execution. DO NOT use `limit to yr=` syntax in inline queries.

- **Syntax**: On platforms like Ovid, use `.ti,ab.` for title/abstract. Use field codes like `.ti.` or `.ab.`.
- **Controlled Vocabulary**: Emtree is the primary thesaurus. Use the format `'term'/exp` to search for a term and explode it. Use `'term'/de` for the term without explosion.
- **Proximity Operators**: Use `ADJn` where `n` is the number of words apart.
- **Date Syntax**: `<YYYYMMDD>.dt.`
- **Precision_Knobs**:
  
  **Filter Knobs:**
  - Publication type: `limit to article or review` - Limit to articles and reviews
  
  **Scope Knobs:**
  - Title only: `.ti.` - Search for concepts in title field only (e.g., `[CONCEPT].ti.`)
  - Major focus: `*[TERM]` - Find articles where the term is a primary subject (e.g., `*'dementia'`)
  
  **Vocabulary Knobs:**
  - No explosion: `'[TERM]'/de` - Use Emtree term without explosion (e.g., `'dementia'/de` instead of `'dementia'/exp`)
  
  **Proximity Knobs:**
  - Adjacent terms: `ADJ5` - Require concepts within 5 words (e.g., `'[CONCEPT1]':ti,ab ADJ5 '[CONCEPT2]':ti,ab`)

## Web of Science
- **Syntax**: Use field tags like `TS=` (Topic), `TI=` (Title), `AB=` (Abstract).
- **Controlled Vocabulary**: Limited native thesaurus. Relies heavily on author keywords and `KeyWords Plus`.
- **Proximity Operators**: `NEAR/n` or `SAME` (same sentence).
- **Date Syntax**: Use the format `PY=(YYYY-YYYY)`.
- **Precision_Knobs**:
  
  **Filter Knobs:**
  - Document type: `DT=(Article OR Review)` - Limit to articles and reviews
  - Subject category: `WC=([CATEGORY])` - Refine by Web of Science Categories (e.g., `WC=(NEUROSCIENCES)`)
  
  **Scope Knobs:**
  - Title only: `TI=([CONCEPT])` - Search for key concepts in title field only
  
  **Proximity Knobs:**
  - Tight proximity: `NEAR/5` - Require concepts within 5 words (e.g., `[CONCEPT1] NEAR/5 [CONCEPT2]`)
  - Same sentence: `SAME` - Require concepts in same sentence
