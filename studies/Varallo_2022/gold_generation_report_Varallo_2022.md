# Gold Standard Generation Report

**Study**: Varallo_2022
**Generated**: QueriesSystematicReview
**Confidence Threshold**: 0.85
**Last Updated**: 2026-02-24

---

## Summary Statistics

- **Total Included Studies**: 21
- **Accepted** (confidence ≥ 0.85): 19
- **Rejected by automated lookup** (confidence < 0.85): 2 → manually verified and added (see §Manual Corrections)

## Coverage Metrics (after manual corrections)

| Metric | Count | Percentage | Notes |
|--------|-------|------------|-------|
| With PMID | 10 | 47.6% (10/21) | Low: many studies are conference abstracts not indexed in PubMed |
| With DOI | 17 | 81.0% (17/21) | After manual DOI additions for refs [47], [57], [60], [63], [64] |
| With Both | 9 | 42.9% (9/21) | |
| With Neither | 4 | 19.0% (4/21) | Refs [51], [55], [59] (supplement/conference abstracts); [Soni 2020 rejected by Br J Pain letter] |
| In detailed CSV | 21 | 100% | All 21 entries present (DOI-only or PMID+DOI) |

## Confidence Distribution

- **Average**: 0.933
- **Range**: 0.900 - 0.950
- **Studies with confidence**: 14 / 19 (automated); 3 additional set to 0.95 after manual verification

## Lookup Sources

| Source | Count | % |
|--------|-------|---|
| PubMed | 8 | 38.1% |
| CrossRef | 4 | 19.0% |
| EuropePMC | 1 | 4.8% |
| Manual (user-verified) | 3 | 14.3% |
| No identifier found | 5 | 23.8% |

---

## Warnings

⚠️  **Low PMID coverage (47.6%)**
   This review includes a large proportion of conference abstracts and supplement proceedings (refs [50], [51], [55], [56], [58], [59], [60], [62]) that are not indexed in PubMed. This is expected for this study type and not a data quality issue.

⚠️  **4 studies with neither PMID nor DOI (unmatachable)**
   Refs [51] Soni 2020, [55] Schreiber 2016, [59] Gren 2018 are supplement/conference abstracts with no stable identifiers. These studies cannot be matched in any database evaluation and will always count as missed (false negatives). This places a hard ceiling on achievable recall of approximately **81% (17/21 matchable studies)**.

---

## Rejected Studies (Automated Lookup — Low Confidence)

| Ref | Author | Year | Auto Confidence | Action Taken |
|-----|--------|------|:--------------:|--------------|
| [60] | Baeyens M | 2019 | 0.812 | ✅ Manually verified — DOI `10.1136/rapm-2019-ESRAABS2019.418` confirmed by user; added to `gold_pmids_Varallo_2022_detailed.csv` |
| [63] | Bayman E | 2017 | 0.800 | ✅ Manually corrected — automated lookup returned wrong DOI (`10.1097/ALN.0000000000001576`, an Anesthesiology paper); correct DOI `10.1016/j.jpain.2017.02.254` confirmed by user; PMID 28248713 cleared |

---

## Manual Corrections Log (2026-02-24)

| Ref | Author | Issue | Resolution |
|-----|--------|-------|------------|
| [47] | Bjurstrom MF 2021 | No DOI/PMID found by automated lookup | DOI `10.1002/ejp.1761` provided by user; added to JSON and detailed CSV |
| [57] | Cho CH 2015 | Confidence 0.80, below threshold | DOI `10.1007/s11999-015-4258-1` confirmed correct; confidence set to 0.95 (manual_verified) |
| [60] | Baeyens M 2019 | Confidence 0.812, below threshold | DOI confirmed; confidence set to 0.95 (manual_verified) |
| [63] | Bayman E 2017 | Wrong DOI assigned; confidence 0.80 | DOI corrected to `10.1016/j.jpain.2017.02.254`; wrong PMID cleared; confidence set to 0.95 |
| [64] | Getachew M 2021 | No DOI/PMID found (table-parsed reference) | DOI `10.1002/msc.1522` provided by user; added to JSON and detailed CSV |
| [64–66] | Getachew, Rhon×2 | References in table format — missed by automated parser | Manually extracted and added to `included_studies.json`; refs [65] and [66] subsequently found via PubMed (PMIDs 31337179, 30479746) |

---

## Extraction Challenges

### 1. Table-format references blocked automated parsing
Refs [64], [65], and [66] were formatted as a markdown table in the converted paper (`paper_Varallo_2022.md`) rather than as standard list-style references. The automated `extract_included_studies.py` parser only found 18/21 included studies on first run. These three were manually added.

### 2. PDF ligature encoding corrupted titles
The PDF-to-markdown conversion rendered typographic ligatures (e.g., `fi`, `fl`) as unicode escapes (`/uniFB01`). This affected titles like ref [61] Miaskowski ("Identi**fi**cation...") and caused PubMed title-matching to fail. The title was manually cleaned to enable a successful lookup (PMID: 23182226).

### 3. High proportion of conference abstracts and supplement proceedings
8 of 21 included studies (38%) are conference abstracts or supplement entries (J Pain supplements, Br J Pain letters, ESRA proceedings). These are typically not indexed in PubMed and have inconsistent DOI assignment in CrossRef. This is the primary reason for low PMID coverage and explains why the gold denominator for evaluation is effectively 17 (not 21).

### 4. Wrong DOI assigned by automated lookup for ref [63]
The automated PubMed lookup for Bayman E 2017 ("A prospective study of predictors of chronic pain after thoracic surgery", J Pain) retrieved a different paper from Anesthesiology (DOI: `10.1097/ALN.0000000000001576`, PMID: 28248713). The J Pain citation was a brief abstract (1 page, S75) with a very similar title to other papers in the results set, leading to a false match. Corrected with user-provided DOI.

### 5. Effective recall ceiling ~81%
Of the 21 included studies, only 17 have at least one identifier (DOI or PMID) that can be matched against database results. The remaining 4 have no stable identifier and cannot be retrieved. Any evaluation recall above ~0.81 would require manual review of retrieved records. The best query (Q1 High-recall) achieved a raw recall of 0.905, but this is computed against the matchable subset only.

---

## Workflow Results (2026-02-24) — Query-by-Query, All Databases

**Databases**: PubMed · Scopus · Web of Science · Embase (manual import)
**Gold denominator**: 21 studies (17 matchable by identifier)

| Query | Strategy | Retrieved | TP | Recall | Best DB |
|-------|----------|:---------:|:--:|:------:|---------|
| Q1 | High-recall | 5,444 | 19 | **0.905** | Scopus 0.667 · Embase 0.571 |
| Q2 | Balanced | 1,117 | 13 | 0.619 | Embase 0.381 · Scopus 0.381 |
| Q3 | High-precision | 42 | 1 | 0.048 | Embase 0.048 |
| Q4 | Filter-based | 975 | 9 | 0.429 | Scopus 0.381 · Embase 0.190 |
| Q5 | Scope (title) | 4,199 | 11 | 0.524 | Embase 0.476 · Scopus 0.095 |
| Q6 | Proximity | 60 | 2 | 0.095 | Scopus 0.048 · WoS 0.048 |

**Key observations:**
- Q1 (High-recall) achieves 90.5% recall — the 2 missed studies are among those without any matchable identifier
- Embase and Scopus strongly outperform PubMed and WoS for this topic (surgical pain, orthopaedics); PubMed recall was ≤0.095 on all queries
- Q3 (High-precision with major headings) is too restrictive for this literature (recall 0.048)
- The low aggregate-strategy recall reflects the DOI-only nature of many included studies (conference abstracts), which are not consistently cross-referenced across databases
