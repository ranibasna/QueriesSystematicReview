# Gold Standard Generation Report

**Study**: Medeiros_2023
**Generated**: 2026-02-23
**Last Updated**: 2026-02-24
**Confidence Threshold**: 0.85

## Summary Statistics

- **Total Included Studies**: 6
- **Accepted** (confidence ≥ 0.85): 6
- **Rejected** (confidence < 0.85): 0

## Coverage Metrics

| Metric | Count | Percentage |
|--------|-------|------------|
| With PMID | 6 | 100.0% |
| With DOI | 6 | 100.0% |
| With Both | 6 | 100.0% |
| With Neither | 0 | 0.0% |

## Confidence Distribution

- **Average**: 0.950
- **Range**: 0.950 - 0.950
- **Studies with confidence**: 6 / 6

## Lookup Sources

- **PubMed**: 6 (100.0%)

---

## Gold Standard Studies

| # | First Author | Year | Journal | PMID | DOI |
|---|-------------|------|---------|------|-----|
| 1 | El-Sheikh | 2007 | Journal of Sleep Research | 17542949 | 10.1111/j.1365-2869.2007.00593.x |
| 2 | Hall | 2015 | Sleep Medicine | 25468623 | 10.1016/j.sleep.2014.10.005 |
| 3 | Park | 2016 | Psychosomatic Medicine | 27136501 | 10.1097/PSY.0000000000000340 |
| 4 | Chiang | 2019 | Psychoneuroendocrinology | 30690224 | 10.1016/j.psyneuen.2018.11.026 |
| 5 | LaVoy | 2020 | International Journal of Psychophysiology | 33130179 | 10.1016/j.ijpsycho.2020.10.010 |
| 6 | Park | 2020 | Journal of Adolescent Health | 32586679 | 10.1016/j.jadohealth.2020.04.015 |

---

## Extraction Notes and Challenges

### Extraction Method: Manual LLM-Assisted (Stage 1 automated extraction failed)

**Date**: 2026-02-23

Automated extraction (`extract_included_studies.py`) failed with:
> `❌ Error: Could not find included studies table`

The included studies were extracted manually from the paper's Table 1 ("Description of studies included"), which is a non-standard table structure split across children and adolescent sub-headers — not recognized by the automated parser. The 6 studies were identified from the text and references section of `paper_Medeiros_2023.md`.

Stage 2 (PubMed API lookup) completed successfully with 100% PMID and DOI coverage (confidence 0.95 for all 6 studies).

---

## Query Execution Results (2026-02-24)

Workflow run: `bash scripts/run_complete_workflow.sh Medeiros_2023 --databases pubmed,scopus,wos --multi-key --query-by-query`
Databases: PubMed, Scopus, Web of Science, Embase (manual export)
Gold size: 6

### Per-Query, Per-Database Performance

| Query | Description | Database | Results | TP | Recall |
|-------|-------------|----------|---------|----|--------|
| Q1 | High-recall | **COMBINED** | **3,879** | **6** | **1.000** |
| Q1 | High-recall | PubMed | 913 | 5 | 0.833 |
| Q1 | High-recall | Scopus | 3,501 | 6 | 1.000 |
| Q1 | High-recall | WoS | 1,273 | 5 | 0.833 |
| Q1 | High-recall | Embase | 0 | 0 | 0.000 ⚠️ |
| Q2 | Balanced | **COMBINED** | **3,666** | **3** | **0.500** |
| Q2 | Balanced | PubMed | 73 | 2 | 0.333 |
| Q2 | Balanced | Scopus | 64 | 1 | 0.167 |
| Q2 | Balanced | WoS | 48 | 0 | 0.000 |
| Q2 | Balanced | Embase | 3,535 | 2 | 0.333 |
| Q3 | High-precision | **COMBINED** | **9** | **1** | **0.167** |
| Q3 | High-precision | PubMed | 0 | 0 | 0.000 |
| Q3 | High-precision | Scopus | 8 | 1 | 0.167 |
| Q3 | High-precision | WoS | 5 | 1 | 0.167 |
| Q3 | High-precision | Embase | 1 | 0 | 0.000 |
| Q4 | Filter variant | **COMBINED** | **2,615** | **3** | **0.500** |
| Q4 | Filter variant | PubMed | 72 | 2 | 0.333 |
| Q4 | Filter variant | Scopus | 50 | 1 | 0.167 |
| Q4 | Filter variant | WoS | 10 | 0 | 0.000 |
| Q4 | Filter variant | Embase | 2,510 | 2 | 0.333 |
| Q5 | Scope variant | **COMBINED** | **6** | **1** | **0.167** |
| Q5 | Scope variant | PubMed | 3 | 1 | 0.167 |
| Q5 | Scope variant | Scopus | 2 | 0 | 0.000 |
| Q5 | Scope variant | WoS | 2 | 0 | 0.000 |
| Q5 | Scope variant | Embase | 4 | 0 | 0.000 |
| Q6 | Proximity/Major | **COMBINED** | **40** | **1** | **0.167** |
| Q6 | Proximity/Major | PubMed | 34 | 1 | 0.167 |
| Q6 | Proximity/Major | Scopus | 11 | 1 | 0.167 |
| Q6 | Proximity/Major | WoS | 8 | 0 | 0.000 |
| Q6 | Proximity/Major | Embase | 0 | 0 | 0.000 ⚠️ |

### Best Strategy per Query

| Query | Best Strategy | Retrieved | TP | Recall |
|-------|--------------|-----------|-----|--------|
| **Q1** | precision_gated_union | **3,853** | **6** | **1.000** ✅ |
| Q2 | consensus_k2 | 40 | 1 | 0.167 |
| Q3 | consensus_k2 | 5 | 1 | 0.167 |
| Q4 | consensus_k2 | 20 | 1 | 0.167 |
| Q5 | precision_gated_union | 4 | 1 | 0.167 |
| Q6 | consensus_k2 | 9 | 1 | 0.167 |

**Recommended strategy**: Query 1 → `precision_gated_union` (Recall = 1.000, 3,853 articles to screen)

---

## Issues and Challenges

### ⚠️ Embase Query 1 — Not Exported (too many results)

**File**: `studies/Medeiros_2023/embase_manual_queries/embase_query1.csv` — **0 bytes (empty)**

The high-recall Embase query (Q1) returned an extremely large number of articles in the Embase interface, making bulk export infeasible. The export was intentionally omitted. As a result, Embase contributes **0 results** for Q1 despite the query being valid.

**Impact**: The 100% recall achieved by Q1 is driven entirely by **Scopus** (3,501 results, 6/6 gold studies). PubMed and WoS each find 5/6 gold studies independently. Embase's absence from Q1 does not reduce the combined recall since Scopus already captures the full gold set.

### ⚠️ Embase Query 6 — Not Exported (empty)

**File**: `studies/Medeiros_2023/embase_manual_queries/embase_query6.csv` — **0 bytes (empty)**

The proximity-based Embase query (Q6) was also not exported (likely returned too many or no filtered results). This has minimal impact as Q6 is a precision-focused micro-variant query.

### ⚠️ Embase Q2 and Q4 High Retrieval Without Date Filtering

Embase queries Q2 (3,535 results) and Q4 (2,510 results) return very high result counts. Per Embase database guidelines, **date filters must be applied via the platform interface after execution** — they are not included inline in the exported queries. As a result, these Embase exports likely contain articles from the full date range (no 1990–2021 restriction applied), inflating retrieval counts and reducing precision significantly. Despite the large retrieval, only 2/6 gold studies are found in each (recall = 0.333).

### ℹ️ Small Gold Standard (n=6)

The review included only 6 studies, which leads to high variability in recall metrics — a single missed study changes recall by 16.7 percentage points. This makes precision-focused queries appear to perform poorly even when logically sound. The maximum achievable recall is limited by how many gold studies are indexed by each database.
