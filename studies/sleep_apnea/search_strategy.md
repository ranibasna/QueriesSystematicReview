### 1. Concept Tables (Markdown)

**Concept→MeSH/Emtree table:**

| concept | term | tree note | explode? | rationale & source |
| :--- | :--- | :--- | :--- | :--- |
| Sleep Apnea | Sleep Apnea Syndromes | C23.888.592.612.850 | Yes | MeSH heading covering all types of sleep apnea. |
| Sleep Apnea | 'sleep apnea syndrome' | | Yes | Emtree heading, exploded to include central, obstructive, etc. |
| Dementia | Dementia | C10.228.140.380, F03 | Yes | Broad MeSH heading for dementia and related cognitive disorders. |
| Dementia | 'dementia' | | Yes | Broad Emtree heading for dementia. |
| Dementia | Alzheimer Disease | C10.228.140.380.100, F03.050.126.300 | Yes | MeSH heading. |
| Dementia | 'alzheimer disease' | | Yes | Emtree heading. |
| Dementia | Lewy Body Disease | C10.228.140.545 | Yes | MeSH heading. |
| Dementia | 'lewy body dementia' | | Yes | Emtree heading. |
| Dementia | Frontotemporal Dementia | C10.228.140.380.420 | Yes | MeSH heading. |
| Dementia | 'frontotemporal dementia' | | Yes | Emtree heading. |
| Dementia | Dementia, Vascular | C10.228.140.380.850 | Yes | MeSH heading. |
| Dementia | 'vascular dementia' | | Yes | Emtree heading. |
| Study Design | Cohort Studies | E05.318.308.940.350 | Yes | MeSH heading for cohort studies. |
| Study Design | 'cohort analysis' | | Yes | Emtree heading. |
| Study Design | Randomized Controlled Trial | E05.318.308.940.770 | Yes | MeSH heading for RCTs. |
| Study Design | 'randomized controlled trial' | | Yes | Emtree heading. |

**Concept→Textword table:**

| concept | synonym/phrase | field | truncation? | source |
| :--- | :--- | :--- | :--- | :--- |
| Sleep Apnea | sleep apnea | tiab | Yes | PICOS/Keywords |
| Sleep Apnea | sleep apnoea | tiab | Yes | Spelling variant |
| Sleep Apnea | sleep disordered breathing | tiab | No | PICOS/Keywords |
| Sleep Apnea | SDB | tiab | No | Acronym |
| Sleep Apnea | obstructive sleep apnea | tiab | Yes | PICOS/Keywords |
| Sleep Apnea | OSA | tiab | No | Acronym |
| Sleep Apnea | apnea-hypopnea index | tiab | No | PICOS |
| Sleep Apnea | AHI | tiab | No | Acronym |
| Sleep Apnea | oxygen desaturation index | tiab | No | PICOS |
| Sleep Apnea | ODI | tiab | No | Acronym |
| Dementia | dementia | tiab | Yes | PICOS/Keywords |
| Dementia | cognitive decline | tiab | No | Synonym |
| Dementia | cognitive impairment | tiab | No | Synonym |
| Dementia | Alzheimer* | tiab | Yes | PICOS/Keywords |
| Dementia | Lewy body | tiab | No | PICOS/Keywords |
| Dementia | frontotemporal dementia | tiab | No | PICOS/Keywords |
| Dementia | FTD | tiab | No | Acronym |
| Dementia | vascular dementia | tiab | No | PICOS/Keywords |
| Study Design | cohort | tiab | No | Study Design |
| Study Design | prospective | tiab | No | Study Design |
| Study Design | retrospective | tiab | No | Study Design |
| Study Design | follow-up | tiab | No | Study Design |
| Study Design | randomized | tiab | No | Study Design |
| Study Design | randomised | tiab | No | Spelling variant |
| Study Design | trial | tiab | No | Study Design |
| Study Design | rct | tiab | No | Acronym |

### 2. JSON Query Object (MUST be a single valid JSON code block)
```json
{
  "pubmed": [
    "# High-recall: Uses broad MeSH terms and textwords to maximize sensitivity.",
    "(((\"Sleep Apnea Syndromes\"[Mesh]) OR (\"sleep apnea\"[tiab] OR \"sleep apnoea\"[tiab] OR \"sleep disordered breathing\"[tiab]))) AND (((\"Dementia\"[Mesh]) OR (\"dementia\"[tiab] OR \"cognitive decline\"[tiab] OR \"cognitive impairment\"[tiab] OR \"Alzheimer s\"[tiab] OR \"Lewy body\"[tiab]))) AND (\"1900/01/01\"[Date - Publication] : \"2021/03/01\"[Date - Publication])",
    "# Balanced: Combines MeSH and textwords with a study design filter for relevance.",
    "(((\"Sleep Apnea Syndromes\"[Mesh]) OR (\"sleep apnea\"[tiab] OR \"sleep apnoea\"[tiab] OR \"sleep disordered breathing\"[tiab] OR \"apnea-hypopnea index\"[tiab] OR \"oxygen desaturation index\"[tiab]))) AND (((\"Alzheimer Disease\"[Mesh] OR \"Lewy Body Disease\"[Mesh] OR \"Frontotemporal Dementia\"[Mesh] OR \"Dementia, Vascular\"[Mesh])) OR (\"dementia\"[tiab] OR \"cognitive impairment\"[tiab] OR \"Alzheimer*\"[tiab])) AND ((cohort[tiab] OR follow-up[tiab] OR prospective[tiab] OR retrospective[tiab] OR randomized[tiab] OR randomised[tiab] OR trial[tiab])) AND (\"1900/01/01\"[Date - Publication] : \"2021/03/01\"[Date - Publication])",
    "# High-precision: Focuses on major MeSH terms and title searches for core concepts.",
    "(((\"Sleep Apnea Syndromes\"[majr])) OR (\"sleep apnea\"[ti])) AND (((\"Dementia\"[majr])) OR (\"dementia\"[ti] OR \"Alzheimer*\"[ti])) AND ((cohort[tiab] OR prospective[tiab] OR retrospective[tiab] OR randomized[tiab] OR trial[tiab])) AND (\"1900/01/01\"[Date - Publication] : \"2021/03/01\"[Date - Publication])",
    "# Micro-variant 1 (Filter-based): Starts with Balanced and adds human and English language filters.",
    "(((\"Sleep Apnea Syndromes\"[Mesh]) OR (\"sleep apnea\"[tiab] OR \"sleep apnoea\"[tiab] OR \"sleep disordered breathing\"[tiab] OR \"apnea-hypopnea index\"[tiab] OR \"oxygen desaturation index\"[tiab]))) AND (((\"Alzheimer Disease\"[Mesh] OR \"Lewy Body Disease\"[Mesh] OR \"Frontotemporal Dementia\"[Mesh] OR \"Dementia, Vascular\"[Mesh])) OR (\"dementia\"[tiab] OR \"cognitive impairment\"[tiab] OR \"Alzheimer*\"[tiab])) AND ((cohort[tiab] OR follow-up[tiab] OR prospective[tiab] OR retrospective[tiab] OR randomized[tiab] OR randomised[tiab] OR trial[tiab])) AND (humans[Filter] AND english[Filter]) AND (\"1900/01/01\"[Date - Publication] : \"2021/03/01\"[Date - Publication])",
    "# Micro-variant 2 (Field/Scope-based): Starts with Balanced and restricts dementia terms to the title for higher specificity.",
    "(((\"Sleep Apnea Syndromes\"[Mesh]) OR (\"sleep apnea\"[tiab] OR \"sleep apnoea\"[tiab] OR \"sleep disordered breathing\"[tiab] OR \"apnea-hypopnea index\"[tiab] OR \"oxygen desaturation index\"[tiab]))) AND (((\"Alzheimer Disease\"[Mesh] OR \"Lewy Body Disease\"[Mesh] OR \"Frontotemporal Dementia\"[Mesh] OR \"Dementia, Vascular\"[Mesh])) OR (\"dementia\"[ti] OR \"cognitive impairment\"[ti] OR \"Alzheimer*\"[ti])) AND ((cohort[tiab] OR follow-up[tiab] OR prospective[tiab] OR retrospective[tiab] OR randomized[tiab] OR randomised[tiab] OR trial[tiab])) AND (\"1900/01/01\"[Date - Publication] : \"2021/03/01\"[Date - Publication])",
    "# Micro-variant 3 (Proximity-based Fallback): Starts with Balanced and uses major MeSH headings for core concepts to increase relevance.",
    "(((\"Sleep Apnea Syndromes\"[majr]) OR (\"sleep apnea\"[tiab] OR \"sleep apnoea\"[tiab] OR \"sleep disordered breathing\"[tiab]))) AND (((\"Dementia\"[majr] OR \"Alzheimer Disease\"[majr])) OR (\"dementia\"[tiab] OR \"cognitive impairment\"[tiab] OR \"Alzheimer*\"[tiab])) AND ((cohort[tiab] OR follow-up[tiab] OR prospective[tiab] OR retrospective[tiab] OR randomized[tiab] OR randomised[tiab] OR trial[tiab])) AND (\"1900/01/01\"[Date - Publication] : \"2021/03/01\"[Date - Publication])"
  ],
  "scopus": [
    "# High-recall: Uses broad TITLE-ABS-KEY searches to maximize sensitivity.",
    "(TITLE-ABS-KEY(\"sleep apnea\" OR \"sleep apnoea\" OR \"sleep disordered breathing\")) AND (TITLE-ABS-KEY(dementia OR \"cognitive decline\" OR \"cognitive impairment\" OR Alzheimer* OR \"Lewy body\")) AND (PUBYEAR > 1989 AND PUBYEAR < 2022)",
    "# Balanced: Combines textwords with a study design filter for relevance.",
    "(TITLE-ABS-KEY(\"sleep apnea\" OR \"sleep apnoea\" OR \"sleep disordered breathing\" OR \"apnea-hypopnea index\" OR \"oxygen desaturation index\")) AND (TITLE-ABS-KEY(dementia OR \"cognitive impairment\" OR Alzheimer*)) AND (TITLE-ABS-KEY(cohort OR prospective OR retrospective OR \"follow up\" OR randomi* OR trial)) AND (PUBYEAR > 1989 AND PUBYEAR < 2022)",
    "# High-precision: Focuses on title searches and proximity for core concepts.",
    "(TITLE(\"sleep apnea\" OR \"sleep apnoea\")) AND (TITLE(dementia OR Alzheimer*)) AND (TITLE-ABS-KEY(cohort OR prospective OR retrospective OR randomi* OR trial)) AND (PUBYEAR > 1989 AND PUBYEAR < 2022)",
    "# Micro-variant 1 (Filter-based): Starts with Balanced and limits document type to articles and reviews.",
    "(TITLE-ABS-KEY(\"sleep apnea\" OR \"sleep apnoea\" OR \"sleep disordered breathing\" OR \"apnea-hypopnea index\" OR \"oxygen desaturation index\")) AND (TITLE-ABS-KEY(dementia OR \"cognitive impairment\" OR Alzheimer*)) AND (TITLE-ABS-KEY(cohort OR prospective OR retrospective OR \"follow up\" OR randomi* OR trial)) AND (DOCTYPE(ar OR re)) AND (PUBYEAR > 1989 AND PUBYEAR < 2022)",
    "# Micro-variant 2 (Field/Scope-based): Starts with Balanced and restricts dementia terms to the title.",
    "(TITLE-ABS-KEY(\"sleep apnea\" OR \"sleep apnoea\" OR \"sleep disordered breathing\" OR \"apnea-hypopnea index\" OR \"oxygen desaturation index\")) AND (TITLE(dementia OR \"cognitive impairment\" OR Alzheimer*)) AND (TITLE-ABS-KEY(cohort OR prospective OR retrospective OR \"follow up\" OR randomi* OR trial)) AND (PUBYEAR > 1989 AND PUBYEAR < 2022)",
    "# Micro-variant 3 (Proximity-based): Starts with Balanced and requires sleep apnea and dementia concepts to be within 10 words of each other.",
    "((TITLE-ABS-KEY(\"sleep apnea\" OR \"sleep apnoea\" OR \"sleep disordered breathing\")) W/10 (TITLE-ABS-KEY(dementia OR \"cognitive impairment\" OR Alzheimer*))) AND (TITLE-ABS-KEY(cohort OR prospective OR retrospective OR \"follow up\" OR randomi* OR trial)) AND (PUBYEAR > 1989 AND PUBYEAR < 2022)"
  ],
  "embase": [
    "# High-recall: Uses broad Emtree terms and textwords to maximize sensitivity.",
    "('sleep apnea syndrome'/exp OR 'sleep apnea':ti,ab OR 'sleep apnoea':ti,ab OR 'sleep disordered breathing':ti,ab) AND ('dementia'/exp OR dementia:ti,ab OR 'cognitive decline':ti,ab OR 'cognitive impairment':ti,ab OR 'alzheimer*':ti,ab OR 'lewy body':ti,ab) AND [1990-2021]/py",
    "# Balanced: Combines Emtree and textwords with a study design filter for relevance.",
    "('sleep apnea syndrome'/exp OR 'sleep apnea':ti,ab OR 'sleep apnoea':ti,ab OR 'apnea-hypopnea index':ti,ab OR 'oxygen desaturation index':ti,ab) AND ('dementia'/exp OR 'alzheimer disease'/exp OR 'lewy body dementia'/exp OR 'frontotemporal dementia'/exp OR 'vascular dementia'/exp OR dementia:ti,ab OR 'cognitive impairment':ti,ab OR 'alzheimer*':ti,ab) AND ('cohort analysis'/exp OR cohort:ti,ab OR prospective:ti,ab OR retrospective:ti,ab OR 'follow up':ti,ab OR 'randomized controlled trial'/exp OR randomi*:ti,ab OR trial:ti,ab) AND [1990-2021]/py",
    "# High-precision: Focuses on major focus Emtree terms and title searches.",
    "(*'sleep apnea syndrome'/exp OR 'sleep apnea':ti) AND (*'dementia'/exp OR dementia:ti OR 'alzheimer*':ti) AND ('cohort analysis'/exp OR cohort:ti,ab OR prospective:ti,ab OR retrospective:ti,ab OR 'randomized controlled trial'/exp OR randomi*:ti,ab OR trial:ti,ab) AND [1990-2021]/py",
    "# Micro-variant 1 (Filter-based): Starts with Balanced and limits to article or review publication types.",
    "('sleep apnea syndrome'/exp OR 'sleep apnea':ti,ab OR 'sleep apnoea':ti,ab OR 'apnea-hypopnea index':ti,ab OR 'oxygen desaturation index':ti,ab) AND ('dementia'/exp OR 'alzheimer disease'/exp OR 'lewy body dementia'/exp OR 'frontotemporal dementia'/exp OR 'vascular dementia'/exp OR dementia:ti,ab OR 'cognitive impairment':ti,ab OR 'alzheimer*':ti,ab) AND ('cohort analysis'/exp OR cohort:ti,ab OR prospective:ti,ab OR retrospective:ti,ab OR 'follow up':ti,ab OR 'randomized controlled trial'/exp OR randomi*:ti,ab OR trial:ti,ab) AND ([article]/lim OR [review]/lim) AND [1990-2021]/py",
    "# Micro-variant 2 (Field/Scope-based): Starts with Balanced and restricts dementia terms to the title.",
    "('sleep apnea syndrome'/exp OR 'sleep apnea':ti,ab OR 'sleep apnoea':ti,ab OR 'apnea-hypopnea index':ti,ab OR 'oxygen desaturation index':ti,ab) AND ('dementia'/exp OR 'alzheimer disease'/exp OR 'lewy body dementia'/exp OR 'frontotemporal dementia'/exp OR 'vascular dementia'/exp OR dementia:ti OR 'cognitive impairment':ti OR 'alzheimer*':ti) AND ('cohort analysis'/exp OR cohort:ti,ab OR prospective:ti,ab OR retrospective:ti,ab OR 'follow up':ti,ab OR 'randomized controlled trial'/exp OR randomi*:ti,ab OR trial:ti,ab) AND [1990-2021]/py",
    "# Micro-variant 3 (Proximity-based): Starts with Balanced and requires sleep apnea and dementia concepts to be adjacent within 10 words.",
    "('sleep apnea syndrome'/exp OR 'sleep apnea':ti,ab OR 'sleep apnoea':ti,ab) ADJ10 ('dementia'/exp OR dementia:ti,ab OR 'cognitive impairment':ti,ab OR 'alzheimer*':ti,ab) AND ('cohort analysis'/exp OR cohort:ti,ab OR prospective:ti,ab OR retrospective:ti,ab OR 'follow up':ti,ab OR 'randomized controlled trial'/exp OR randomi*:ti,ab OR trial:ti,ab) AND [1990-2021]/py"
  ]
}
```
### 3. PRESS Self-Check (JSON Patch)
```json
{
  "json_patch": {
    "pubmed": {
      "1": "# Balanced (revised): Added broad 'Dementia' MeSH term to concept group to improve recall.",
      "(((\"Sleep Apnea Syndromes\"[Mesh]) OR (\"sleep apnea\"[tiab] OR \"sleep apnoea\"[tiab] OR \"sleep disordered breathing\"[tiab] OR \"apnea-hypopnea index\"[tiab] OR \"oxygen desaturation index\"[tiab]))) AND (((\"Dementia\"[Mesh] OR \"Alzheimer Disease\"[Mesh] OR \"Lewy Body Disease\"[Mesh] OR \"Frontotemporal Dementia\"[Mesh] OR \"Dementia, Vascular\"[Mesh])) OR (\"dementia\"[tiab] OR \"cognitive impairment\"[tiab] OR \"Alzheimer*\"[tiab])) AND ((cohort[tiab] OR follow-up[tiab] OR prospective[tiab] OR retrospective[tiab] OR randomized[tiab] OR randomised[tiab] OR trial[tiab])) AND (\"1900/01/01\"[Date - Publication] : \"2021/03/01\"[Date - Publication])"
    }
  }
}
```

### 3. PRESS Self-Check & Translation Notes (Markdown)
- **Issues:** The initial 'Balanced' PubMed query accidentally omitted the broad "Dementia"[Mesh] term, including only specific dementia types. This has been corrected in the patch to ensure studies on all-cause dementia are captured.
- **Translation Notes:**
  - **Controlled Vocabulary:** PubMed uses MeSH (`"Term"[Mesh]`), while Embase uses Emtree (`'term'/exp`). Scopus has less reliable controlled vocabulary, so queries rely more heavily on textwords in `TITLE-ABS-KEY`.
  - **Syntax:**
    - Field codes differ: `[tiab]` (PubMed), `TITLE-ABS-KEY()` (Scopus), `.ti,ab.` (Embase).
    - Proximity operators are `W/n` in Scopus and `ADJn` in Embase. PubMed has no proximity operator, so a fallback to major headings (`[majr]`) was used for the proximity-based variant.
    - Truncation is `*` in PubMed and Scopus, and often handled automatically or with `*` in Embase depending on the platform.
  - **Date:** Date syntax is distinct for each: `"YYYY/MM/DD"[Date - Publication]` for PubMed, `PUBYEAR > YYYY` for Scopus, and `YYYY-YYYY/py` for Embase. The date range was broadened to be more inclusive.
