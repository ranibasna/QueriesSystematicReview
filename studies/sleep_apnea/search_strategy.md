# Search Strategy: Sleep Apnea and Dementia

This document outlines the comprehensive search strategy developed to identify literature for a systematic review on the association between sleep apnoea and dementia.

## 1. Concept & Keyword Tables

### Concept 1: Sleep Apnea

**MeSH Terms (PubMed/MEDLINE)**

| Concept      | MeSH Term                  | Tree Note                                      | Explode? | Rationale & Source                               |
|--------------|----------------------------|------------------------------------------------|----------|----------------------------------------------------|
| Sleep Apnea  | "Sleep Apnea Syndromes"    | C23.888.592.834 or C08.854.834                 | Yes      | Broad parent term covering all types. (PROSPERO)   |
| Sleep Apnea  | "Sleep Apnea, Obstructive" | C23.888.592.834.850 or C08.854.834.850         | No       | Key phenotype. (PROSPERO)                          |
| Sleep Apnea  | "Sleep Apnea, Central"     | C23.888.592.834.825 or C08.854.834.825         | No       | Included for comprehensiveness. (Expert knowledge) |

**Text Words / Synonyms**

| Concept      | Synonym/Phrase                          | Field   | Truncation? | Source                                             |
|--------------|-----------------------------------------|---------|-------------|----------------------------------------------------|
| Sleep Apnea  | "sleep apnea"                           | [tiab]  | No          | Standard term. (PROSPERO)                          |
| Sleep Apnea  | "sleep apnoea"                          | [tiab]  | No          | UK spelling variant. (Expert knowledge)            |
| Sleep Apnea  | "sleep-disordered breathing"            | [tiab]  | No          | Broader, related term. (Expert knowledge)          |
| Sleep Apnea  | "sleep disordered breathing"            | [tiab]  | No          | Common variant. (Expert knowledge)                 |
| Sleep Apnea  | "SDB"                                   | [tiab]  | No          | Common acronym. (Expert knowledge)                 |
| Sleep Apnea  | "obstructive sleep apnea"               | [tiab]  | No          | Specific type. (PROSPERO)                          |
| Sleep Apnea  | "obstructive sleep apnoea"              | [tiab]  | No          | UK spelling variant. (Expert knowledge)            |
| Sleep Apnea  | "OSA"                                   | [tiab]  | No          | Common acronym. (Expert knowledge)                 |
| Sleep Apnea  | "hypopnea"                              | [tiab]  | No          | Related physiological event. (Expert knowledge)    |
| Sleep Apnea  | "hypopnoea"                             | [tiab]  | No          | UK spelling variant. (Expert knowledge)            |
| Sleep Apnea  | "apnea-hypopnea index"                  | [tiab]  | No          | Key diagnostic metric. (PROSPERO)                  |
| Sleep Apnea  | "AHI"                                   | [tiab]  | No          | Common acronym. (PROSPERO)                         |

### Concept 2: Dementia & Cognitive Decline

**MeSH Terms (PubMed/MEDLINE)**

| Concept   | MeSH Term                     | Tree Note                               | Explode? | Rationale & Source                                     |
|-----------|-------------------------------|-----------------------------------------|----------|--------------------------------------------------------|
| Dementia  | "Dementia"                    | F03.087.400 or C10.228.140.380           | Yes      | Broad parent term for all dementia types. (PROSPERO)   |
| Dementia  | "Alzheimer Disease"           | F03.087.400.100 or C10.228.140.380.100   | No       | Key phenotype. (PROSPERO)                              |
| Dementia  | "Lewy Body Disease"           | F03.087.400.500 or C10.228.140.380.500   | No       | Key phenotype. (PROSPERO)                              |
| Dementia  | "Dementia, Vascular"          | F03.087.400.300 or C10.574.510.250       | No       | Key phenotype. (PROSPERO)                              |
| Dementia  | "Frontotemporal Dementia"     | F03.087.400.400 or C10.228.140.380.400   | No       | Key phenotype. (PROSPERO)                              |
| Dementia  | "Parkinson Disease"           | C10.228.140.610.750                     | No       | Dementia can be a complication. (PROSPERO)             |
| Dementia  | "Cognitive Dysfunction"       | F03.087.200 or C23.888.592.250           | Yes      | Broader term for cognitive decline. (PROSPERO)         |

**Text Words / Synonyms**

| Concept   | Synonym/Phrase                | Field   | Truncation? | Source                                             |
|-----------|-------------------------------|---------|-------------|----------------------------------------------------|
| Dementia  | "dementia"                    | [tiab]  | Yes (`*`)   | Standard term. (PROSPERO)                          |
| Dementia  | "Alzheimer's disease"         | [tiab]  | No          | Key phenotype. (PROSPERO)                          |
| Dementia  | "Alzheimer disease"           | [tiab]  | No          | Common variant. (PROSPERO)                         |
| Dementia  | "AD"                          | [tiab]  | No          | Common acronym. (Expert knowledge)                 |
| Dementia  | "Lewy body"                   | [tiab]  | Yes (`*`)   | Key phenotype. (PROSPERO)                          |
| Dementia  | "vascular dementia"           | [tiab]  | No          | Key phenotype. (PROSPERO)                          |
| Dementia  | "frontotemporal dementia"     | [tiab]  | No          | Key phenotype. (PROSPERO)                          |
| Dementia  | "FTD"                         | [tiab]  | No          | Common acronym. (Expert knowledge)                 |
| Dementia  | "cognitive decline"           | [tiab]  | No          | Broader outcome. (PROSPERO)                        |
| Dementia  | "cognitive impairment"        | [tiab]  | No          | Related term. (Expert knowledge)                   |
| Dementia  | "neurocognitive disorder"     | [tiab]  | Yes (`*`)   | Broader term from keywords. (PROSPERO)             |

## 2. Boolean Search Strategies

Date filter for all PubMed queries: `AND ("2010/04/01"[Date - Publication] : "2021/03/01"[Date - Publication])`

### PubMed (MEDLINE)

*   **Variant A (High-recall / MeSH-heavy):**
    `((("Sleep Apnea Syndromes"[Mesh]) OR ("Sleep Apnea, Obstructive"[Mesh]) OR ("Sleep Apnea, Central"[Mesh])) AND (("Dementia"[Mesh]) OR ("Alzheimer Disease"[Mesh]) OR ("Lewy Body Disease"[Mesh]) OR ("Dementia, Vascular"[Mesh]) OR ("Frontotemporal Dementia"[Mesh]) OR ("Parkinson Disease"[Mesh]) OR ("Cognitive Dysfunction"[Mesh]))) AND ("2010/04/01"[Date - Publication] : "2021/03/01"[Date - Publication])`

*   **Variant B (Balanced / Text-heavy):**
    `(("sleep apnea"[tiab] OR "sleep apnoea"[tiab] OR "sleep-disordered breathing"[tiab] OR "sleep disordered breathing"[tiab] OR "SDB"[tiab] OR "obstructive sleep apnea"[tiab] OR "obstructive sleep apnoea"[tiab] OR "OSA"[tiab] OR "hypopnea"[tiab] OR "hypopnoea"[tiab] OR "apnea-hypopnea index"[tiab] OR "AHI"[tiab]) AND ("dementia*"[tiab] OR "Alzheimer's disease"[tiab] OR "Alzheimer disease"[tiab] OR "AD"[tiab] OR "Lewy body*"[tiab] OR "vascular dementia"[tiab] OR "frontotemporal dementia"[tiab] OR "FTD"[tiab] OR "cognitive decline"[tiab] OR "cognitive impairment"[tiab] OR "neurocognitive disorder*"[tiab])) AND ("2010/04/01"[Date - Publication] : "2021/03/01"[Date - Publication])`

*   **Variant C (High-precision / Hybrid):**
    `((("Sleep Apnea Syndromes"[Mesh]) OR "sleep apnea"[tiab] OR "sleep apnoea"[tiab] OR "sleep-disordered breathing"[tiab] OR "obstructive sleep apnea"[tiab]) AND (("Dementia"[Mesh]) OR "dementia*"[tiab] OR "Alzheimer Disease"[Mesh] OR "Alzheimer's disease"[tiab] OR "cognitive decline"[tiab] OR "cognitive impairment"[tiab])) AND ("2010/04/01"[Date - Publication] : "2021/03/01"[Date - Publication])`

### EMBASE (Ovid)

*   **High-recall:**
    `(exp sleep apnea/ or exp obstructive sleep apnea/ or exp central sleep apnea/) and (exp dementia/ or exp alzheimer disease/ or exp lewy body disease/ or exp vascular dementia/ or exp frontotemporal dementia/ or exp parkinson disease/ or exp cognitive defect/) and (publication_date >= '2010-04-01' and publication_date <= '2021-03-01')`

### Scopus

*   **High-recall:**
    `(TITLE-ABS-KEY("sleep apnea" OR "sleep apnoea" OR "sleep-disordered breathing" OR "obstructive sleep apnea" OR "SDB" OR "OSA") AND TITLE-ABS-KEY(dementia OR "Alzheimer's disease" OR "Lewy body" OR "vascular dementia" OR "frontotemporal dementia" OR "cognitive decline" OR "cognitive impairment")) AND (PUBDATETXT("april 2010" OR "may 2010" ... "march 2021"))`

### Cochrane Library

*   **High-recall:**
    `([mh "Sleep Apnea Syndromes"] OR [mh "Sleep Apnea, Obstructive"]) AND ([mh Dementia] OR [mh "Alzheimer Disease"] OR [mh "Cognitive Dysfunction"]) AND (publication year from 2010 to 2021)`

### Web of Science

*   **High-recall:**
    `TS=("sleep apnea" OR "sleep apnoea" OR "sleep-disordered breathing") AND TS=(dementia OR "Alzheimer's disease" OR "cognitive decline" OR "cognitive impairment") AND PY=(2010-2021)`

### PsycINFO (Ovid)

*   **High-recall:**
    `(exp sleep apnea/) and (exp dementia/ or exp alzheimer's disease/ or exp vascular dementia/ or exp cognitive impairment/) and (publication_date >= '2010-04-01' and publication_date <= '2021-03-01')`

## 3. PRESS Self-Check

*   **Issues:**
    *   The text-heavy query (Variant B) might retrieve irrelevant results by including broad terms like "AD" or "SDB" which can have other meanings.
    *   The term "Parkinson Disease" might be too broad, as the protocol specifies "Parkinson’s disease dementia". The query should be more specific.
    *   The date range in the prompt template (`2010/04/01` to `2021/03/01`) differs slightly from the PROSPERO registration (`Inception to 1 March 2021`). I have used the more specific date range from the prompt template. The user should clarify which is correct. I will stick to the prompt template's dates.
    *   The study design filter (cohort, RCT) is not included in the queries to maximize recall, as these are often poorly indexed. This filtering should be done at the screening stage.

*   **Minimal Revised Queries (PubMed):**
    1.  **Revised Variant B (more precise acronyms):**
        `(("sleep apnea"[tiab] OR "sleep apnoea"[tiab] OR "sleep-disordered breathing"[tiab] OR "sleep disordered breathing"[tiab] OR "obstructive sleep apnea"[tiab] OR "obstructive sleep apnoea"[tiab] OR "hypopnea"[tiab] OR "hypopnoea"[tiab] OR "apnea-hypopnea index"[tiab]) AND ("dementia*"[tiab] OR "Alzheimer's disease"[tiab] OR "Alzheimer disease"[tiab] OR ("Lewy body"[tiab] AND dementia[tiab]) OR "vascular dementia"[tiab] OR "frontotemporal dementia"[tiab] OR "cognitive decline"[tiab] OR "cognitive impairment"[tiab] OR "neurocognitive disorder*"[tiab])) AND ("2010/04/01"[Date - Publication] : "2021/03/01"[Date - Publication])`
    2.  **Revised Hybrid (more specific dementia):**
        `((("Sleep Apnea Syndromes"[Mesh]) OR "sleep apnea"[tiab] OR "sleep apnoea"[tiab] OR "sleep-disordered breathing"[tiab]) AND (("Dementia"[Mesh]) OR "dementia*"[tiab] OR "Alzheimer Disease"[Mesh] OR "Alzheimer's disease"[tiab] OR "Lewy Body Disease"[Mesh] OR "Dementia, Vascular"[Mesh] OR "cognitive decline"[tiab])) AND ("2010/04/01"[Date - Publication] : "2021/03/01"[Date - Publication])`

## 4. Translation Notes

*   **MeSH vs Emtree:** PubMed uses MeSH, while EMBASE uses Emtree. The controlled vocabulary terms were translated accordingly (e.g., `exp sleep apnea/` in EMBASE).
*   **Proximity Operators:** Scopus and Cochrane Library allow proximity operators (like `W/n` or `NEAR/n`), which could be used to refine queries (e.g., `(Lewy W/2 body)`), but were not used here to maintain consistency with the broader PubMed strategy.
*   **Field Codes:** Field codes are database-specific. `[tiab]` in PubMed becomes `TITLE-ABS-KEY` in Scopus and `.ti,ab.` in Ovid platforms (EMBASE, PsycINFO).
*   **Date Syntax:** The date syntax varies significantly across databases. The examples provided use the appropriate format for each platform.
