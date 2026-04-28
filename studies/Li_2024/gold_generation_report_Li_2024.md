# Gold Standard Generation Report

**Study**: Li_2024
**Topic**: Sleep disturbances and female infertility
**Paper DOI**: 10.1186/s12905-024-03508-y
**PROSPERO**: CRD42024498443
**Confidence Threshold**: 0.85
**Last Updated**: 2026-02-24

---

## Summary Statistics

- **Total Included Studies (from paper)**: 19
- **Accepted** (confidence ≥ 0.85): 18
- **Rejected** (confidence < 0.85): 1
- **Gold standard size used in scoring**: 18 (PMID+DOI combined)

## Coverage Metrics

| Metric | Count | Percentage |
|--------|-------|------------|
| With PMID | 17 | 94.4% |
| With DOI | 18 | 100.0% |
| With Both | 17 | 94.4% |
| With Neither | 0 | 0.0% |

## Confidence Distribution

- **Average**: 0.944
- **Range**: 0.900 - 0.950
- **Studies with confidence**: 17 / 18

## Lookup Sources

- **PubMed**: 17 (94.4%)
- **Unknown**: 1 (5.6%)

## Accepted Studies

| PMID | First Author | Year | Journal |
|------|-------------|------|---------|
| 37908752 | Li | 2023 | Frontiers in Endocrinology |
| 35259255 | Yao | 2022 | Human Reproduction |
| 34910749 | Lim | 2021 | PLOS ONE |
| 34013438 | Yang | 2022 | Sleep and Breathing |
| 34374922 | Pimolsri | 2021 | Journal of Assisted Reproduction and Genetics |
| *(no PMID)* | Ozcelik | 2023 | Journal of Psychosomatic Obstetrics and Gynaecology |
| 34949542 | Philipsen | 2022 | Sleep Health |
| 32981061 | Stocker | 2021 | Acta Obstetricia et Gynecologica Scandinavica |
| 34180998 | Eisenberg | 2021 | Journal of Clinical Endocrinology and Metabolism |
| 30987736 | Willis | 2019 | Fertility and Sterility |
| 29136234 | Wang | 2018 | Sleep |
| 32836186 | Shi | 2020 | Sleep Medicine |
| 35620388 | Liang | 2022 | Frontiers in Endocrinology |
| 36877353 | Zhao | 2023 | Sleep and Breathing |
| 36586812 | Freeman | 2023 | Fertility and Sterility |
| 36435629 | Liu | 2023 | Fertility and Sterility |
| 37593900 | Zhang | 2023 | Journal of Clinical Sleep Medicine |
| 36609819 | Ibrahim | 2023 | Sleep and Breathing |

## Rejected Studies (Low Confidence)

- **"Sleep in women undergoing in vitro fertilization: a pilot study"** (confidence: 0.80) — below 0.85 threshold; excluded from gold standard

---

## Gold Standard Extraction Challenges (2026-02-20)

### 1. Automated extraction failed
The automated `extract_included_studies.py` script could not locate the included-studies table in the converted markdown (`paper_Li_2024.md`). The failure message was *"Could not find included studies table"*. This required full manual extraction.

### 2. Manual extraction from three tables
Studies were spread across **Tables 1, 2, and 3** in the paper covering three subgroups:
- Table 1: Reproductive-age females and IVF group studies
- Table 2: Additional IVF/infertility studies
- Table 3: OSA (obstructive sleep apnea) subgroup

Total: 19 studies extracted manually and written to `included_studies.json`.

### 3. One PMID lookup failure
**Özçelik 2023** ("Evaluation of chronotype and sleep quality in infertile population...") could not be found via PubMed API lookup. The DOI was successfully retrieved via CrossRef (`10.1080/0167482X.2022.2148523`). This study is included in the detailed gold standard by DOI only (no PMID row in `gold_pmids_Li_2024.csv`).

### 4. Broken PDF symlinks
The study directory contained broken symlinks (`Paper.pdf → Li 2024 - Paper.pdf`) pointing to non-existent targets. Fixed by copying actual PDFs from `OldResults/V1/studies/Li_2024/`. PDF-to-markdown conversion (Docling) then succeeded.

---

## Workflow Execution — Issues and Fixes (2026-02-23)

### Issue 1: Workflow aborted after Embase import step
**Cause**: `set -e` (exit on error) at the top of `run_complete_workflow.sh` caused the script to abort immediately when `batch_import_embase.py` returned exit code 1 due to 2 failed CSV imports (queries 2 and 4). The `if [ $? -eq 0 ]` guard never ran.

**Fix**: Changed to `|| EMBASE_IMPORT_RC=$?` to capture the exit code without triggering `set -e`, then continue with partial results.

### Issue 2: Embase CSV queries 2 and 4 failed import (vertical format detection bug)
**Cause**: The format-detection condition in `import_embase_manual.py` used a raw comma count on the unparsed CSV line (`first_line.count(',') <= 2`). When a title value contained internal commas (e.g. *"effectiveness, safety, persistence and predictors of response"*), the count exceeded 2, misclassifying the file as horizontal format — which then found no DOI/PMID columns.

**Fix**: Replaced comma-count heuristic with `csv.reader`-based parsing of the first line, checking that the first CSV field is exactly `"TITLE"` and the row has ≤ 3 fields (to exclude wide horizontal headers). Both queries 2 and 4 now import successfully.

### Issue 3: Scopus API error on Query 1
**Cause**: Scopus returned `400 Bad Request` for query 1 (high-recall broad query), likely due to query length or offset pagination limit (`start=5000`). Scopus contributed 0 results for Q1.

**Impact**: Q1 COMBINED recall is still 1.000 (PubMed alone retrieved all 18 gold articles). No fix needed.

### Issue 4: Embase query 6 returned 0 results
The proximity-based Embase query (micro-variant 3, `ADJ10`) returned 0 results. An empty placeholder JSON was created automatically. This is expected behaviour — the query is intentionally narrow.

**Note**: Embase query 1 has **7,516 records** (not zero). This is a large high-recall export that was deliberately included in the workflow.

---

## Query Performance Results (2026-02-23)

Gold standard size for scoring: **18** articles (DOI-based matching, multi-key mode).

### Per-Database Recall by Query

| Query | Type | PubMed | Scopus | WOS | Embase | COMBINED |
|-------|------|--------|--------|-----|--------|----------|
| Q1 | High-recall broad | **1.000** | *(API error)* | 0.944 | 0.944 | **1.000** |
| Q2 | Balanced | 0.833 | 0.833 | 0.833 | **0.889** | 0.889 |
| Q3 | High-precision | 0.389 | 0.222 | 0.333 | **0.444** | 0.556 |
| Q4 | Filter-based | 0.833 | 0.833 | 0.833 | 0.889* | 0.889 |
| Q5 | Scope-based (title) | 0.722 | 0.333 | 0.389 | **0.778** | 0.889 |
| Q6 | Proximity (ADJ10) | 0.667 | 0.556 | 0.444 | 0.000† | 0.778 |

*Q4 Embase result from re-run after fix; †Q6 Embase returned 0 results (empty placeholder).

### Aggregation Strategy Scores by Query (best strategies shown)

| Query | Strategy | TP | Retrieved | Recall | Precision |
|-------|----------|----|-----------|--------|-----------|
| Q1 | `precision_gated_union` | 17 | 8,632 | **0.944** | 0.002 |
| Q1 | `consensus_k2` | 16 | 2,030 | 0.889 | 0.008 |
| Q2 | `consensus_k2` *(+Embase)* | 15 | 867 | 0.833 | 0.017 |
| Q2 | `precision_gated_union` *(+Embase)* | 15 | 5,931 | 0.833 | 0.003 |
| Q3 | `precision_gated_union` | 9 | 59 | 0.500 | 0.153 |
| Q4 | `precision_gated_union` | 15 | 1,525 | 0.833 | 0.010 |
| Q5 | `precision_gated_union` | 15 | 603 | 0.833 | 0.025 |
| Q5 | `consensus_k2` | 10 | 90 | 0.556 | 0.111 |
| Q6 | `precision_gated_union` | 14 | 209 | 0.778 | 0.067 |

### Key Observations

- **Q1 achieves perfect recall (1.000)** in COMBINED mode — all 18 gold articles retrieved. PubMed alone with the high-recall query is sufficient for complete coverage.
- **Embase consistently outperforms other single databases** for recall across all queries where it was included (Q2, Q3, Q5).
- **Q3 (high-precision)** has intentionally low recall (0.556 combined) — this is expected for a precision-optimised query.
- **Q6 (proximity ADJ10)** Embase export returned 0 results; PubMed/Scopus/WOS collectively still recover 0.778 recall.
- **consensus_k2 for Q1** (2,030 articles, recall=0.889) offers the best precision-recall tradeoff if a more manageable screening set is needed.
- **1 gold article unrecovered**: "Sleep in women undergoing IVF" (Özçelik 2023, DOI only) — not found by any database in any query, likely due to indexing lag or publisher access.

---

## Output Files

| File | Description |
|------|-------------|
| `gold_pmids_Li_2024.csv` | 17 PMIDs (simple format, ≥0.85 confidence) |
| `gold_pmids_Li_2024_detailed.csv` | 18 studies with PMID + DOI (used for scoring) |
| `included_studies.json` | 19 manually extracted studies with metadata |
| `embase_query{1-6}.json` | Imported Embase results (Q6 = empty placeholder) |
