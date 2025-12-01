# Database Querying Guidelines

This file provides database-specific syntax and strategy rules for the LLM to use when generating search queries.

## PubMed
- **Syntax**: Use `[tiab]` for title/abstract searches. Use `[mh]` for MeSH terms, `[majr]` for major MeSH terms, and `[tw]` for all text words. Do not use proximity operators. Parentheses must be balanced.
- **Controlled Vocabulary**: Use MeSH (Medical Subject Headings). Validate that terms exist. Use `:NoExp` suffix to prevent automatic explosion of a broad MeSH term.
- **Date Syntax**: Use the format `("YYYY/MM/DD"[Date - Publication] : "YYYY/MM/DD"[Date - Publication])`.
- **Precision_Knobs**:
  - "Use `[Mesh:NoExp]` on broad MeSH headings to increase precision."
  - "Add filters such as `humans[Filter]` and `english[Filter]`."
  - "Require study design terms in title/abstract (e.g., `(cohort[tiab] OR rct[tiab])`)."
  - "Emphasize key concepts by searching in title only (e.g., `dementia[ti]`)."
  - "Exclude publication types like case reports or editorials: `NOT (case reports[pt] OR letter[pt])`."

## Scopus
- **Syntax**: Use `TITLE-ABS-KEY(...)` for general topic searches. Field codes like `TITLE(...)` and `ABS(...)` are also available.
- **Controlled Vocabulary**: Primarily uses Emtree, but its coverage can be inconsistent. A combination of Emtree terms and free-text words is recommended.
- **Proximity Operators**: Use `W/n` (words appear within `n` words of each other, in any order) or `PRE/n` (words appear within `n` words, in the specified order).
- **Date Syntax**: Use `PUBYEAR > YYYY` and `PUBYEAR < YYYY`. For example: `(PUBYEAR > 2019 AND PUBYEAR < 2023)`.
- **Precision_Knobs**:
  - "Emphasize key concepts in the title only using `TITLE(...)`."
  - "Use a tight proximity operator for core concepts (e.g., `(sleep apnea W/5 dementia)`)."
  - "Limit document type to article and review: `DOCTYPE(ar OR re)`."
  - "Limit results to a specific subject area, e.g., `SUBJAREA(MEDI)` for medicine."
  - "Use more specific Emtree terms instead of broad ones."

## Embase
- **Syntax**: On platforms like Ovid, use `.ti,ab.` for title/abstract. Use field codes like `.ti.` or `.ab.`.
- **Controlled Vocabulary**: Emtree is the primary thesaurus. Use the format `'term'/exp` to search for a term and explode it. Use `'term'/de` for the term without explosion.
- **Proximity Operators**: Use `ADJn` where `n` is the number of words apart.
- **Date Syntax**: `<YYYYMMDD>.dt.`
- **Precision_Knobs**:
  - "Use single-word or more specific Emtree terms (e.g., `'dementia'/de` instead of `'dementia'/exp`)."
  - "Use the `.ti.` field code to search for concepts in the title only."
  - "Combine key concepts with a tight proximity operator (e.g., `'sleep apnea':ti,ab ADJ5 'dementia':ti,ab`)."
  - "Limit by publication type: `limit to article or review`."
  - "Use major focus (`*term`) to find articles where the term is a primary subject."

## Web of Science
- **Syntax**: Use field tags like `TS=` (Topic), `TI=` (Title), `AB=` (Abstract).
- **Controlled Vocabulary**: Limited native thesaurus. Relies heavily on author keywords and `KeyWords Plus`.
- **Proximity Operators**: `NEAR/n` or `SAME` (same sentence).
- **Date Syntax**: Use the format `PY=(YYYY-YYYY)`.
- **Precision_Knobs**:
  - "Search for key concepts in the title only: `TI=(dementia)`."
  - "Use a tight proximity operator: `(sleep apnea NEAR/5 dementia)`."
  - "Refine by Web of Science Categories (e.g., `WC=(NEUROSCIENCES)`)."
  - "Limit document types: `DT=(Article OR Review)`."
