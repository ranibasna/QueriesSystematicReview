# Gold Standard Generation Report

**Study**: Riedy_2021
**Generated**: QueriesSystematicReview
**Confidence Threshold**: 0.79

## Summary Statistics

- **Total Included Studies**: 38
- **Accepted** (confidence ≥ 0.79): 38
- **Rejected** (confidence < 0.79): 0

## Coverage Metrics

| Metric | Count | Percentage |
|--------|-------|------------|
| With PMID | 25 | 65.8% |
| With DOI | 31 | 81.6% |
| With Both | 22 | 57.9% |
| With Neither | 4 | 10.5% |

## Confidence Distribution

- **Average**: 0.936
- **Range**: 0.807 - 1.000
- **Studies with confidence**: 34 / 38

## Lookup Sources

- **PubMed**: 22 (57.9%)
- **CrossRef**: 9 (23.7%)
- **Unknown**: 4 (10.5%)
- **EuropePMC**: 3 (7.9%)

## Warnings

⚠️  Low PMID coverage (65.8%)
   Expected: >70% for biomedical systematic reviews
   Suggestion: Check extraction and PubMed lookup logs
⚠️  4 studies have neither PMID nor DOI
   These studies cannot be matched in evaluation
   Suggestion: Manual review recommended

## Notes on Evaluation Score Interpretation

### Why recall numbers are lower than expected

The per-query recall numbers (e.g., Q1 best = 0.711 combined, 0.839 aggregated) reflect
**real retrieval performance**, but they are bounded by the following known issues in the
gold list. These are documented here, with resolution status.

#### Issue 1: Effective evaluation denominator is 31, not 38 [NOT FULLY ADDRESSED]

The scoring code computes `gold_unique_articles = max(n_PMIDs, n_DOIs) = max(25, 31) = 31`.
The recall denominator is therefore **31**, not the true total of 38 included studies.
This means **maximum achievable recall = 31/38 = 81.6%** even with perfect database retrieval.

The 7 excluded studies break down as:
- **4 with neither DOI nor PMID**: Borkowski 2001, Gragert 1990 (PhD thesis),
  Forquer 2007, Rocknathan 2017 (conference proceedings).
  These are truly unmatchable by identifier. Fuzzy title/author search would be needed.
  → *Accepted by user: fuzzy search may catch them at screening stage.*
- **3 with PMID-only (no DOI)**: Because `n_PMIDs (25) < n_DOIs (31)`, the formula
  `gold_articles_pmid_only = max(0, 25 - 31) = 0` treats all 25 PMIDs as subsumed
  within the 31 DOI articles. The 3 PMID-only articles therefore receive neither
  a denominator slot nor PMID-fallback matching.
  → *Not explicitly addressed; their contribution to recall is currently zero.*

#### Issue 2: Old literature — inconsistent DOI coverage [NOT ADDRESSED]

Many included studies date from the 1970s–1990s (e.g., Stanchina 2005, Forquer 2007,
Messingher 1981). Even when a DOI exists in the gold list, the corresponding database
records (Scopus, WoS, Embase) may not carry a matching DOI in their metadata, causing
missed matches that are not retrieval failures but metadata gaps.

#### Issue 3: Aggregation strategy is cross-database, not cross-query [INFORMATIONAL]

"Aggregation" combines results from multiple **databases** for a single query (PubMed +
Scopus + WoS + Embase → union/consensus). It does NOT combine results across queries.
This is why `precision_gated_union` for Q1 reaches recall 0.839 while the best individual
database (Embase) only reaches 0.632 — the two databases retrieve different gold subsets.

#### Summary

| Source of recall ceiling | Studies affected | Max loss | Status |
|--------------------------|------------------|----------|--------|
| No DOI, no PMID          | 4                | 4/38 = 10.5% | Accepted (fuzzy fallback) |
| PMID-only (invisible to scorer) | ~3        | 3/38 = 7.9%  | Not addressed |
| Old paper DOI gaps in databases | unknown    | variable     | Not addressed |
| **Hard ceiling (best case)** | **31/38** | **81.6% max recall** | — |
