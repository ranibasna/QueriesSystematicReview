# Gold Standard Generation Report

**Study**: Nexha_2024
**Generated**: QueriesSystematicReview
**Confidence Threshold**: 0.85
**Last Updated**: 2026-02-24

## Revision History

| Date | Change |
|------|--------|
| 2026-02-23 | Initial automated generation — 24 accepted, 1 rejected (Miura 2019, conf 0.807) |
| 2026-02-24 | Miura 2019 manually confirmed via DOI from paper reference list; added to gold standard as DOI-only entry (no PMID); gold standard expanded to 25 studies |

## Summary Statistics

- **Total Included Studies**: 25
- **Accepted** (confidence ≥ 0.85): 25
- **Rejected** (confidence < 0.85): 0
- **Manually confirmed (user-verified DOI)**: 1

## Coverage Metrics

| Metric | Count | Percentage |
|--------|-------|------------|
| With PMID | 24 | 96.0% |
| With DOI | 25 | 100.0% |
| With Both | 24 | 96.0% |
| DOI-only (no PMID) | 1 | 4.0% |
| With Neither | 0 | 0.0% |

## Confidence Distribution

- **Average**: 0.950 (automated studies)
- **Range**: 0.950 - 0.950 (automated studies)
- **Studies with automated confidence**: 24 / 25
- **Studies with user-confirmed confidence**: 1 / 25

## Lookup Sources

- **PubMed**: 23 (92.0%)
- **EuropePMC**: 1 (4.0%)
- **CrossRef + User Confirmed**: 1 (4.0%)

## Notes, Issues, and Challenges

### Automated Extraction Failure
The automated inclusion table extractor (`extract_included_studies.py`) could not parse the included studies table from the paper markdown. All 25 studies were extracted **manually** by reading Tables 1–2 and the full reference list in `paper_Nexha_2024.md`. This is a one-time cost with no impact on downstream quality, but means the extraction is not reproducible via script alone.

### Miura 2019 — DOI-Only Entry (Journal Not Indexed in PubMed)
- **Reference**: [51] Miura J, Honma R (2019). *Daytime sleepiness in relation to gender and premenstrual symptoms in a sample of Japanese college students.* Sleep and Biological Rhythms.
- **DOI**: `10.1007/s41105-019-00236-x`
- **PMID**: None — "Sleep and Biological Rhythms" (Springer) is **not indexed in PubMed or MEDLINE**
- **Initial status**: Rejected by automated pipeline (CrossRef confidence 0.807 < threshold 0.85)
- **Resolution (2026-02-24)**: DOI confirmed by user from paper reference list. Entry added manually to `gold_pmids_Nexha_2024_detailed.csv` as a DOI-only record. Confidence set to 1.0, method `user_confirmed`.
- **Impact on recall**: This study is **not retrieved by any of the four databases** (PubMed, Scopus, WOS, Embase) across all 6 queries. It represents an inherent ceiling miss — no query strategy can recover it from the searched databases.

### Impact on Recall Metrics
Because Miura 2019 is unrecoverable from all searched databases, its inclusion in the gold standard introduces a permanent 1-study ceiling penalty:
- **Maximum achievable recall** (any strategy, any query) = **24/25 = 96.0%**
- Q1 best achieved: 21/25 = 84.0% (vs 21/24 = 87.5% before correction)
- For fair benchmarking, consider reporting both the raw recall (denominator=25) and the ceiling-adjusted recall (denominator=24, excluding DOI-only non-indexed study).

## Previously Rejected Studies (Now Resolved)

| Ref | Authors | Year | Title (truncated) | DOI | PMID | Resolution |
|-----|---------|------|-------------------|-----|------|------------|
| [51] | Miura J, Honma R | 2019 | Daytime sleepiness in relation to gender and premenstrual symptoms... | 10.1007/s41105-019-00236-x | None | DOI confirmed by user 2026-02-24; added as DOI-only entry |
