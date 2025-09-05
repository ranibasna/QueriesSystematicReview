# Systematic Review Search Strategy

This document outlines the search strategy for the systematic review on Obstructive Sleep Apnea (OSA) and the human microbiome in case-control studies.

**Date of Search:** To be run on or after 2024-08-05.
**Databases:** PubMed, Embase, Web of Science, Cochrane Library.

---

### 1. Concept → MeSH Table

| Concept | MeSH Heading | Tree Note | Explode? | Rationale & Source |
| :--- | :--- | :--- | :--- | :--- |
| **OSA** | `Sleep Apnea, Obstructive` | C23.888.592.835.750 | Yes | The primary MeSH heading for Obstructive Sleep Apnea. Exploding it includes more specific subheadings. (Source: PubMed MeSH) |
| **OSA** | `Sleep-Disordered Breathing` | C08.858.820 | No | A broader term from PICOS. Not exploded to maintain focus, as it can include central apneas. (Source: User PICOS) |
| **Microbiome** | `Microbiota` | G02.111.570.820.500 | Yes | The core MeSH term for microbial communities. Exploding is crucial for recall to include organ-specific microbiota (e.g., Gastrointestinal, Nasal). (Source: PubMed MeSH) |
| **Microbiome** | `Dysbiosis` | C01.150.333 | Yes | A key outcome concept representing an imbalanced microbiome, often studied in disease states. (Source: PubMed MeSH) |
| **Study Design** | `Case-Control Studies` | E05.318.135 | Yes | The specific study design requested in the PICOS. (Source: PubMed MeSH) |
| **Population** | `Adult` | M01.060.116 | No | Limits the population to adults as specified. (Source: PubMed MeSH) |

### 2. Concept → Textword Table

| Concept | Synonym / Phrase | Field Tag | Truncation? | Source |
| :--- | :--- | :--- | :--- | :--- |
| **OSA** | `obstructive sleep apnea` | `[tiab]` | No | Core phrase. |
| **OSA** | `obstructive sleep apnoea` | `[tiab]` | No | UK spelling variant. |
| **OSA** | `OSA` | `[tiab]` | No | Common acronym. |
| **OSA** | `OSAHS` | `[tiab]` | No | Common acronym for syndrome. |
| **OSA** | `sleep-disordered breathing` | `[tiab]` | No | Broader term from PICOS. |
| **OSA** | `SDB` | `[tiab]` | No | Acronym for broader term. |
| **OSA** | `sleep apnea-hypopnea` | `[tiab]` | No | Variant phrasing. |
| **Microbiome** | `microbiom*` | `[tiab]` | Yes | Captures microbiome, microbiomes. |
| **Microbiome** | `microbiota*` | `[tiab]` | Yes | Captures microbiota, microbiotas. |
| **Microbiome** | `microbial` | `[tiab]` | No | Adjective form. |
| **Microbiome** | `bacteriom*` | `[tiab]` | Yes | Captures bacteriome, bacteriomes. |
| **Microbiome** | `dysbiosis` | `[tiab]` | No | Key outcome term. |
| **Microbiome** | `dysbiotic` | `[tiab]` | No | Adjective form. |
| **Microbiome** | `gut` OR `oral` OR `nasal` OR `airway` OR `pharyngeal` | `[tiab]` | No | Anatomical locations from PICOS. |
| **Microbiome** | `flora` | `[tiab]` | No | Older but still used synonym. |
| **Microbiome** | `alpha diversity` OR `beta diversity` | `[tiab]` | No | Specific outcomes from PICOS. |
| **Microbiome** | `shannon index` OR `simpson index` OR `chao1` | `[tiab]` | No | Specific diversity indices from PICOS. |
| **Microbiome** | `OTU` OR `ASV` | `[tiab]` | No | Specific unit types from PICOS. |
| **Microbiome** | `operational taxonomic unit*` | `[tiab]` | Yes | Full phrase for OTU. |
| **Microbiome** | `amplicon sequence variant*` | `[tiab]` | Yes | Full phrase for ASV. |
| **Study Design**| `case control*` | `[tiab]` | Yes | Captures "case control" and "case controlled". |
| **Study Design**| `case-control*` | `[tiab]` | Yes | Hyphenated variant. |
| **Study Design**| `retrospective study` | `[tiab]` | No | Related study design concept. |

### 3. Boolean Strategies (PubMed Syntax)

**A) High-Recall (Variant B - Text-heavy):**
```
("obstructive sleep apnea"[tiab] OR "obstructive sleep apnoea"[tiab] OR OSA[tiab] OR OSAHS[tiab] OR "sleep-disordered breathing"[tiab] OR SDB[tiab] OR "sleep apnea-hypopnea"[tiab] OR "Sleep Apnea, Obstructive"[mh] OR "Sleep-Disordered Breathing"[mh]) AND (microbiom*[tiab] OR microbiota*[tiab] OR microbial[tiab] OR bacteriom*[tiab] OR dysbiosis[tiab] OR dysbiotic[tiab] OR gut[tiab] OR oral[tiab] OR nasal[tiab] OR airway[tiab] OR pharyngeal[tiab] OR flora[tiab] OR "alpha diversity"[tiab] OR "beta diversity"[tiab] OR "shannon index"[tiab] OR "simpson index"[tiab] OR chao1[tiab] OR OTU[tiab] OR ASV[tiab] OR "operational taxonomic unit*"[tiab] OR "amplicon sequence variant*"[tiab] OR "Microbiota"[mh] OR "Dysbiosis"[mh]) AND ("case control*"[tiab] OR "case-control*"[tiab] OR "retrospective study"[tiab] OR "Case-Control Studies"[mh]) AND "Adult"[mh]
```

**B) Balanced (Variant C - Hybrid):**
```
("obstructive sleep apnea"[tiab] OR "obstructive sleep apnoea"[tiab] OR OSAHS[tiab] OR "Sleep Apnea, Obstructive"[mh]) AND (microbiom*[tiab] OR microbiota*[tiab] OR dysbiosis[tiab] OR gut[tiab] OR oral[tiab] OR nasal[tiab] OR "alpha diversity"[tiab] OR "beta diversity"[tiab] OR "Microbiota"[mh] OR "Dysbiosis"[mh]) AND ("case control"[tiab] OR "case-control"[tiab] OR "Case-Control Studies"[mh]) AND "Adult"[mh]
```

**C) High-Precision (Variant A - MeSH-heavy):**
```
("Sleep Apnea, Obstructive"[mh]) AND ("Microbiota"[mh] OR "Dysbiosis"[mh]) AND ("Case-Control Studies"[mh]) AND "Adult"[mh]
```

### 4. PRESS Self-Check

*   **Issues Found:**
    *   *Logic:* The term `SDB` (Sleep-Disordered Breathing) is broad and could retrieve studies on central sleep apnea, potentially reducing precision in the high-recall search. This is an accepted trade-off for maximizing recall.
    *   *Missing Terms:* The term "control" alone is too ambiguous and was correctly omitted to avoid irrelevant hits (e.g., "infection control"). The combination `case-control` is specific.
    *   *Inappropriate Limits:* No inappropriate limits were identified. The `Adult` MeSH term is correctly applied.
    *   *Spelling:* Both "apnea" and "apnoea" are included.
    *   *Translation:* The queries are PubMed-specific. Direct copy-pasting to other databases will fail. See translation notes.

*   **Minimal Revised Queries:**
    *   The provided queries are robust. No minimal revisions are strictly necessary, as the high-recall strategy intentionally includes broader terms. For a slightly more precise "High-Recall" version, one could remove `SDB[tiab]` and `"Sleep-Disordered Breathing"[mh]`, but this would violate the initial "bias to recall" instruction. The current set of three queries provides a good spectrum from high-recall to high-precision.

### 5. Translation Notes Across Databases

*   **Date Window:** The date limit (`<= 2024-08-05`) should be applied using the database's built-in date filter tools, not as part of the query string itself.

*   **EMBASE:**
    *   **Controlled Vocabulary:** MeSH terms must be translated to Emtree.
        *   `"Sleep Apnea, Obstructive"[mh]` → `'obstructive sleep apnea'/exp`
        *   `"Microbiota"[mh]` → `'microbiota'/exp`
        *   `"Dysbiosis"[mh]` → `'dysbiosis'/exp`
        *   `"Case-Control Studies"[mh]` → `'case control study'/exp`
        *   `"Adult"[mh]` → `'adult'/exp`
    *   **Field Tags:** `[tiab]` becomes `.ti,ab.`.
    *   **Proximity Operators:** Embase supports proximity operators. For higher precision, you could link concepts like `(gut OR oral OR nasal) NEAR/3 (microbiom* OR microbiota*)`.
    *   **Truncation:** Uses `*` (same as PubMed).

*   **Web of Science (WoS):**
    *   **Controlled Vocabulary:** WoS has no comprehensive controlled vocabulary like MeSH or Emtree. All MeSH terms from the PubMed query should be searched as text words.
    *   **Field Tags:** Use `TS=` (Topic) to search in title, abstract, and keywords. E.g., `TS=("obstructive sleep apnea")`.
    *   **Proximity Operators:** Use `NEAR/n`. This is highly recommended. E.g., `TS=(OSA NEAR/5 (microbiom* OR microbiota*))`.
    *   **Truncation:** Uses `*` (same as PubMed).

*   **Cochrane Library:**
    *   **Controlled Vocabulary:** Uses MeSH, so the terms are the same, but the syntax is different.
    *   **Syntax:** Searches are built line-by-line.
    *   **Example (Balanced Strategy):**
        *   `#1. "Sleep Apnea, Obstructive":mexp`
        *   `#2. ("obstructive sleep apnea" OR "obstructive sleep apnoea" OR OSAHS):ti,ab`
        *   `#3. #1 OR #2`
        *   `#4. "Microbiota":mexp OR "Dysbiosis":mexp`
        *   `#5. (microbiom* OR microbiota* OR dysbiosis OR gut OR oral OR nasal OR "alpha diversity" OR "beta diversity"):ti,ab`
        *   `#6. #4 OR #5`
        *   `#7. "Case-Control Studies":mexp`
        *   `#8. ("case control" OR "case-control"):ti,ab`
        *   `#9. #7 OR #8`
        *   `#10. "Adult":mexp`
        *   `#11. #3 AND #6 AND #9 AND #10`

---

## Search Strategy: Multiple Sclerosis & Sleep Disorders (Non-Pharmacological RCTs)

**Date of Search:** 2025-09-05
**Databases:** MEDLINE (via PubMed), Scopus, EMBASE, PsycINFO, Cochrane Library
**Date Window:** Records up to 2024-08-04

### 1) Concept → MeSH Table (for MEDLINE/PubMed)

| Concept | MeSH Term | Tree Note | Explode? | Rationale & Source |
| :--- | :--- | :--- | :--- | :--- |
| **Population** | Multiple Sclerosis | C10.228.140.580 | Yes | Core condition. Exploding includes all subtypes. (Source: MeSH Browser) |
| **Population** | Sleep Wake Disorders | C10.886.735 / F03.870.860 | Yes | Broad category for all sleep disorders, as specified in PICOS. (Source: MeSH Browser, PROSPERO) |
| | Insomnia | C10.886.735.466 | Yes | Specific disorder mentioned in PROSPERO. |
| | Sleep Apnea Syndromes | C10.886.735.780 | Yes | Specific disorder mentioned in PROSPERO. |
| | Restless Legs Syndrome | C10.886.735.730 | Yes | Specific disorder mentioned in PROSPERO. |
| | Narcolepsy | C10.886.735.530 | Yes | Specific disorder mentioned in PROSPERO. |
| | REM Sleep Behavior Disorder | C10.886.735.720 | Yes | Specific disorder mentioned in PROSPERO. |
| **Intervention** | Behavior Therapy | F04.754.200 | Yes | Broad term for non-pharma interventions. (Source: MeSH Browser) |
| | Cognitive Behavioral Therapy | F04.754.200.300 | Yes | Key non-pharma intervention. (Source: MeSH Browser) |
| | Exercise Therapy | E02.779.330 | Yes | Key non-pharma intervention. (Source: MeSH Browser) |
| | Mind-Body Therapies | E02.644 | Yes | Includes mindfulness, meditation, etc. (Source: MeSH Browser) |
| | Rehabilitation | E02.779 | Yes | Broad term for various non-pharma therapies. (Source: MeSH Browser) |
| | Psychotherapy | F04.754 | Yes | Broad term for psychological interventions. (Source: MeSH Browser) |
| **Design** | Randomized Controlled Trial | E05.318.760.535 | No | Specific study design required. (Source: MeSH Browser) |
| | Controlled Clinical Trial | E05.318.760 | No | Broader term for controlled studies. (Source: MeSH Browser) |

### 2) Concept → Textword Table (for MEDLINE/PubMed)

| Concept | Synonym/Phrase | Field Tag | Truncation? | Source |
| :--- | :--- | :--- | :--- | :--- |
| **Population** | "multiple sclerosis" | [tiab] | No | Standard term |
| | "disseminated sclerosis" | [tiab] | No | Synonym |
| | MS | [tiab] | No | Common acronym, combine with context |
| | PwMS | [tiab] | No | Acronym for "People with MS" |
| | sleep | [tiab] | Yes (`sleep*`) | Broad term for the domain |
| | insomnia | [tiab] | Yes (`insomnia*`) | Specific disorder |
| | "sleep apnea" | [tiab] | Yes (`"sleep apnea*"`) | Specific disorder |
| | "obstructive sleep apnea" | [tiab] | Yes (`"obstructive sleep apnea*"`) | Specific disorder |
| | "restless leg" | [tiab] | Yes (`"restless leg*"`) | Specific disorder |
| | narcolepsy | [tiab] | Yes (`narcoleps*`) | Specific disorder |
| | "sleep disorder" | [tiab] | Yes (`"sleep disorder*"`) | General term |
| | somnolence | [tiab] | Yes (`somnolen*`) | Symptom |
| | hypersomnia | [tiab] | Yes (`hypersomni*`) | Symptom |
| **Intervention** | "non-pharmacological" | [tiab] | No | Key intervention descriptor |
| | "non-invasive" | [tiab] | No | Key intervention descriptor |
| | "behavioral therapy" | [tiab] | Yes (`"behavioral therap*"`)| Intervention type |
| | "cognitive behavio* therapy" | [tiab] | Yes | Intervention type (captures UK/US spelling) |
| | CBT | [tiab] | No | Common acronym |
| | exercise | [tiab] | Yes (`exercis*`) | Intervention type |
| | "physical activity" | [tiab] | No | Intervention type |
| | rehabilitation | [tiab] | Yes (`rehabilitat*`) | Intervention type |
| | psychotherapy | [tiab] | Yes (`psychotherap*`) | Intervention type |
| | mindfulness | [tiab] | No | Intervention type |
| | meditation | [tiab] | Yes (`meditat*`) | Intervention type |
| | "health education" | [tiab] | No | Intervention type |
| | "patient education" | [tiab] | No | Intervention type |
| **Design** | "randomized controlled trial" | [pt] | No | Publication Type |
| | "controlled clinical trial" | [pt] | No | Publication Type |
| | randomized | [tiab] | No | Textword |
| | placebo | [tiab] | No | Textword |
| | randomly | [tiab] | No | Textword |
| | trial | [tiab] | No | Textword |
| | groups | [tiab] | No | Textword |

### 3) Boolean Strategies (MEDLINE/PubMed Syntax)

*Note: These strategies are designed for MEDLINE/PubMed and will require translation for other databases. The date filter is applied at the end.*

#### Variant A (MeSH-heavy)
*   **High-Recall:** `((("Multiple Sclerosis"[Mesh]) AND "Sleep Wake Disorders"[Mesh])) AND (("Behavior Therapy"[Mesh]) OR "Cognitive Behavioral Therapy"[Mesh] OR "Exercise Therapy"[Mesh] OR "Mind-Body Therapies"[Mesh] OR "Rehabilitation"[Mesh] OR "Psychotherapy"[Mesh]) AND (("Randomized Controlled Trial"[Publication Type]) OR "Controlled Clinical Trial"[Publication Type] OR random*[tiab] OR placebo[tiab] OR trial[tiab])`
*   **Balanced:** `((("Multiple Sclerosis"[Mesh])) AND ("Sleep Wake Disorders"[Mesh] OR "Insomnia"[Mesh] OR "Sleep Apnea Syndromes"[Mesh] OR "Restless Legs Syndrome"[Mesh])) AND (("Cognitive Behavioral Therapy"[Mesh]) OR "Exercise Therapy"[Mesh] OR "Rehabilitation"[Mesh]) AND (("Randomized Controlled Trial"[Publication Type]) OR "Controlled Clinical Trial"[Publication Type])`
*   **High-Precision:** `((("Multiple Sclerosis"[Majr])) AND ("Sleep Wake Disorders"[Majr])) AND (("Cognitive Behavioral Therapy"[Mesh]) OR "Exercise Therapy"[Mesh]) AND ("Randomized Controlled Trial"[Publication Type])`

#### Variant B (Text-heavy)
*   **High-Recall:** `((("multiple sclerosis"[tiab] OR "disseminated sclerosis"[tiab] OR MS[tiab])) AND (sleep*[tiab] OR insomnia*[tiab] OR "sleep apnea*"[tiab] OR "restless leg*"[tiab] OR narcoleps*[tiab] OR "sleep disorder*"[tiab] OR somnolen*[tiab])) AND ("non-pharmacological"[tiab] OR "non-invasive"[tiab] OR "behavioral therap*"[tiab] OR "cognitive behavio* therapy"[tiab] OR CBT[tiab] OR exercis*[tiab] OR "physical activity"[tiab] OR rehabilitat*[tiab] OR psychotherap*[tiab] OR mindfulness[tiab] OR meditat*[tiab]) AND (randomized[tiab] OR placebo[tiab] OR randomly[tiab] OR trial[tiab] OR groups[tiab])`
*   **Balanced:** `((("multiple sclerosis"[tiab])) AND ("sleep disorder*"[tiab] OR insomnia[tiab] OR "sleep apnea"[tiab] OR "restless legs syndrome"[tiab])) AND (("cognitive behavio* therapy"[tiab]) OR "exercise"[tiab] OR "rehabilitation"[tiab] OR "mindfulness"[tiab]) AND (randomized[tiab] AND trial[tiab])`
*   **High-Precision:** `("multiple sclerosis"[tiab] AND (insomnia[tiab] OR "sleep apnea"[tiab]) AND ("cognitive behavio* therapy"[tiab] OR "exercise"[tiab]) AND "randomized controlled trial"[tiab])`

#### Variant C (Hybrid Balanced - Recommended Best-Practice)
*   **High-Recall (Recommended):** `((("Multiple Sclerosis"[Mesh]) OR "multiple sclerosis"[tiab] OR "disseminated sclerosis"[tiab])) AND (("Sleep Wake Disorders"[Mesh]) OR sleep*[tiab] OR insomnia*[tiab] OR "sleep apnea*"[tiab] OR "restless leg*"[tiab] OR narcoleps*[tiab] OR "sleep disorder*"[tiab]) AND (("Behavior Therapy"[Mesh]) OR "Cognitive Behavioral Therapy"[Mesh] OR "Exercise Therapy"[Mesh] OR "Mind-Body Therapies"[Mesh] OR "Rehabilitation"[Mesh] OR "Psychotherapy"[Mesh] OR "non-pharmacological"[tiab] OR "non-invasive"[tiab] OR "behavioral therap*"[tiab] OR "cognitive behavio* therapy"[tiab] OR exercis*[tiab] OR "physical activity"[tiab] OR rehabilitat*[tiab] OR psychotherap*[tiab] OR mindfulness[tiab])) AND (("Randomized Controlled Trial"[Publication Type]) OR "Controlled Clinical Trial"[Publication Type] OR randomized[tiab] OR placebo[tiab] OR trial[tiab] OR groups[tiab])`
*   **Balanced:** `((("Multiple Sclerosis"[Mesh]) OR "multiple sclerosis"[tiab])) AND (("Sleep Wake Disorders"[Mesh]) OR "insomnia"[tiab] OR "sleep apnea"[tiab] OR "restless legs syndrome"[tiab])) AND (("Cognitive Behavioral Therapy"[Mesh]) OR "Exercise Therapy"[Mesh] OR "Rehabilitation"[Mesh] OR "cognitive behavio* therapy"[tiab] OR "exercise"[tiab]) AND (("Randomized Controlled Trial"[Publication Type]) OR "Controlled Clinical Trial"[Publication Type] OR (randomized[tiab] AND trial[tiab]))`
*   **High-Precision:** `((("Multiple Sclerosis"[Majr]) AND ("Sleep Wake Disorders"[Majr]))) AND (("Cognitive Behavioral Therapy"[Mesh]) OR "Exercise Therapy"[Mesh]) AND ("Randomized Controlled Trial"[Publication Type])`

### 4) PRESS Self-Check

*   **Issues Identified:**
    *   *Logic:* The term "MS" is a very common acronym. Using it alone could retrieve many irrelevant results (e.g., mass spectrometry). In the text-heavy queries, it should be combined with a contextual term like `(MS[tiab] AND sleep[tiab])` or used with caution. The proposed queries keep it simple for clarity but this is a refinement to consider if precision is poor.
    *   *Missing Terms:* The intervention concept is broad. While a good range of terms is included, some specific therapies (e.g., "acceptance and commitment therapy", "yoga") are not explicitly listed to keep the query length manageable but are covered by broader MeSH terms like "Mind-Body Therapies".
    *   *Inappropriate Limits:* No major issues. The use of `[tiab]` and `[pt]` is appropriate for PubMed.
    *   *Spelling:* Handled `behavio*r` with truncation.
    *   *Translation:* The queries are PubMed-specific and require careful translation.

*   **Minimal Revised Queries (Fixes):**
    1.  **Revised High-Recall (Hybrid):** The original is quite comprehensive. No minimal revision is likely to improve it without sacrificing significant recall. The provided hybrid high-recall query is robust.
    2.  **Revised Balanced (Hybrid) with improved MS precision:** `((("Multiple Sclerosis"[Mesh]) OR "multiple sclerosis"[tiab])) AND (("Sleep Wake Disorders"[Mesh]) OR "insomnia"[tiab] OR "sleep apnea"[tiab] OR "restless legs syndrome"[tiab])) AND (("Cognitive Behavioral Therapy"[Mesh]) OR "Exercise Therapy"[Mesh] OR "Rehabilitation"[Mesh] OR "cognitive behavio* therapy"[tiab] OR "exercise"[tiab]) AND (("Randomized Controlled Trial"[Publication Type]) OR "Controlled Clinical Trial"[Publication Type] OR (randomized[tiab] AND trial[tiab]))` - *This is identical to the one above, which is already well-balanced.*
    3.  **Revised High-Precision (Hybrid) with text words:** `((("Multiple Sclerosis"[Majr]) OR "multiple sclerosis"[tiab])) AND (("Sleep Wake Disorders"[Majr]) OR insomnia[tiab]) AND (("Cognitive Behavioral Therapy"[Mesh]) OR "cognitive behavio* therapy"[tiab]) AND (("Randomized Controlled Trial"[Publication Type]) OR "randomized controlled trial"[tiab])`

### 5) Translation Notes Across Databases

*   **EMBASE (Ovid):**
    *   MeSH (`"term"[Mesh]`) → Emtree (`'term'/exp`).
    *   `[tiab]` → `:ti,ab,kw`.
    *   `[pt]` → `:pt`.
    *   Truncation `*` → `$`.
    *   Proximity operators like `ADJ` can be used (e.g., `(cognitive ADJ behavio* ADJ therapy)`).
    *   **Example Translation (Concept):** `"multiple sclerosis"/exp OR ('multiple sclerosis' OR 'disseminated sclerosis'):ti,ab,kw`

*   **Scopus:**
    *   No major controlled vocabulary like MeSH/Emtree. Relies on text words.
    *   `[tiab]` → `TITLE-ABS-KEY(...)`.
    *   `[pt]` is not a standard field; rely on text words for study design.
    *   Date format is `PUBDATETXT("YYYY")`. Use `PUBDATETXT(BEFORE 2024-08-05)`.
    *   **Example Translation (Concept):** `TITLE-ABS-KEY("multiple sclerosis" OR "disseminated sclerosis")`

*   **PsycINFO (Ovid/EBSCO):**
    *   MeSH → APA Thesaurus of Psychological Index Terms (`DE "term"`).
    *   `[tiab]` → `ti,ab,id`.
    *   Syntax is similar to EMBASE on Ovid platform.

*   **Cochrane Library (CENTRAL):**
    *   Uses MeSH, so vocabulary is similar to PubMed.
    *   Syntax is slightly different: `[mh] ^"term"` for MeSH exact, or `[mh] "term"` for explode.
    *   `[tiab]` → `:ti,ab,kw`.
    *   **Example Translation (Concept):** `([mh] "Multiple Sclerosis") OR ("multiple sclerosis":ti,ab,kw)`

---
## Multiple Sclerosis & Sleep Disorders Search Strategy (2025-09-05)

This search strategy was developed based on the PICOS criteria outlined in the PROSPERO registration CRD42024509769 and methodological guidance from "Search filters for systematic reviews and meta-analyses in sleep medicine" (Pires et al.).

### 1) Concept → MeSH Table

| Concept | MeSH Term | Tree Note | Explode? | Rationale & Source |
| :--- | :--- | :--- | :--- | :--- |
| Multiple Sclerosis | Multiple Sclerosis | C10.228.140.100.510 | Yes | Core condition. |
| Sleep Disorders | Sleep Wake Disorders | C10.886.735 | Yes | Broad parent term for all sleep-related disorders. Covers specific disorders mentioned in PROSPERO. |
| | Insomnia | C10.886.735.462 | Yes | Specific disorder mentioned in PROSPERO. |
| | Sleep Apnea Syndromes | C08.854.756 | Yes | Specific disorder mentioned in PROSPERO. |
| | Restless Legs Syndrome | C10.886.735.738 | Yes | Specific disorder mentioned in PROSPERO. |
| | Narcolepsy | C10.886.735.587 | Yes | Specific disorder mentioned in PROSPERO. |
| | REM Sleep Behavior Disorder | C10.886.735.650 | Yes | Specific disorder mentioned in PROSPERO. |
| Non-Pharm Interventions | Cognitive Behavioral Therapy | F04.754.250 | Yes | Key non-pharm intervention for sleep. |
| | Exercise Therapy | E02.303.300 | Yes | Common non-pharm intervention. |
| | Mind-Body Therapies | F04.754.550 | Yes | Broad term for interventions like mindfulness, yoga. |
| | Relaxation Therapy | F04.754.750 | Yes | Common non-pharm intervention. |
| | Phototherapy | E02.830.500 | Yes | Intervention for circadian rhythm disorders. |
| | Sleep Hygiene | F04.754.250.800 | Yes | Specific type of behavioral therapy. |
| RCT | Randomized Controlled Trial | E05.318.760.735 | Yes | Study design filter (publication type). |
| | Controlled Clinical Trial | E05.318.760.250 | Yes | Study design filter (publication type). |

### 2) Concept → Textword Table

| Concept | Synonym/Phrase | Field | Truncation? | Source |
| :--- | :--- | :--- | :--- | :--- |
| Multiple Sclerosis | "multiple sclerosis" | tiab | No | Core condition. |
| | "disseminated sclerosis" | tiab | No | Synonym. |
| | MS | tiab | No | Common acronym, combine with context to ensure specificity. |
| Sleep Disorders | sleep | tiab | Yes (`sleep*`) | Broad term to capture all variations (Pires et al.). |
| | insomnia | tiab | Yes (`insomnia*`) | Specific disorder. |
| | "sleep apnea" | tiab | Yes (`"sleep apnea*"`) | Specific disorder. |
| | "obstructive sleep apnea" | tiab | No | Specific disorder. |
| | OSA | tiab | No | Acronym, use with context. |
| | "restless leg syndrome" | tiab | No | Specific disorder. |
| | RLS | tiab | No | Acronym, use with context. |
| | "Willis-Ekbom disease" | tiab | No | Synonym for RLS. |
| | narcolepsy | tiab | Yes (`narcoleps*`) | Specific disorder. |
| | "REM sleep behavior disorder" | tiab | No | Specific disorder. |
| | RBD | tiab | No | Acronym, use with context. |
| | somnolence | tiab | No | Symptom. |
| | "sleep disturbance" | tiab | Yes (`"sleep disturb*"`) | Common phrase. |
| | "sleep quality" | tiab | No | Outcome and descriptor. |
| | "sleep disorder" | tiab | Yes (`"sleep disorder*"`) | Common phrase. |
| Non-Pharm Interventions | "cognitive behavioral therapy" | tiab | No | |
| | "cognitive behaviour therapy" | tiab | No | UK spelling. |
| | CBT | tiab | No | Acronym, use with context. |
| | exercise | tiab | No | |
| | "physical activity" | tiab | No | |
| | yoga | tiab | No | |
| | mindfulness | tiab | No | |
| | "light therapy" | tiab | No | |
| | phototherapy | tiab | No | |
| | "sleep hygiene" | tiab | No | |
| | "relaxation technique" | tiab | Yes (`"relaxation technique*"`) | |
| | non-pharmacological | tiab | No | |
| | nonpharmacological | tiab | No | |
| | non-invasive | tiab | No | |
| | noninvasive | tiab | No | |
| RCT | randomi*ed | tiab | Yes (`randomi*ed`) | RCT signal word. |
| | controlled trial | tiab | No | RCT signal phrase. |
| | placebo | tiab | No | RCT signal word. |
| | trial | ti | No | RCT signal word (in title for precision). |

### 3) Boolean Strategies per Database

**Date Filter:** `1000/01/01` to `2024/08/04` for all databases.

---
#### **PubMed (MEDLINE)**
*   **Variant A (MeSH-heavy / High-recall):** `((("Multiple Sclerosis"[Mesh]) AND (("Sleep Wake Disorders"[Mesh]) OR ("Insomnia"[Mesh]) OR ("Sleep Apnea Syndromes"[Mesh]) OR ("Restless Legs Syndrome"[Mesh]) OR ("Narcolepsy"[Mesh]) OR ("REM Sleep Behavior Disorder"[Mesh]))) AND (("Cognitive Behavioral Therapy"[Mesh]) OR ("Exercise Therapy"[Mesh]) OR ("Mind-Body Therapies"[Mesh]) OR ("Relaxation Therapy"[Mesh]) OR ("Phototherapy"[Mesh]) OR ("Sleep Hygiene"[Mesh]))) AND (("Randomized Controlled Trial"[Publication Type]) OR ("Controlled Clinical Trial"[Publication Type])) AND (("1000/01/01"[Date - Publication] : "2024/08/04"[Date - Publication]))`
*   **Variant B (Text-heavy / Balanced):** `((("multiple sclerosis"[tiab] OR "disseminated sclerosis"[tiab])) AND (sleep*[tiab] OR insomnia*[tiab] OR "sleep apnea*"[tiab] OR "restless leg syndrome"[tiab] OR "Willis-Ekbom disease"[tiab] OR narcoleps*[tiab] OR "REM sleep behavior disorder"[tiab] OR "sleep disturbance*"[tiab] OR "sleep quality"[tiab])) AND (("cognitive behavioral therapy"[tiab] OR "cognitive behaviour therapy"[tiab] OR exercise[tiab] OR "physical activity"[tiab] OR yoga[tiab] OR mindfulness[tiab] OR "light therapy"[tiab] OR phototherapy[tiab] OR "sleep hygiene"[tiab] OR "relaxation technique*"[tiab] OR non-pharmacological[tiab] OR nonpharmacological[tiab] OR non-invasive[tiab] OR noninvasive[tiab])) AND (randomi*ed[tiab] OR placebo[tiab] OR "controlled trial"[tiab] OR trial[ti])) AND (("1000/01/01"[Date - Publication] : "2024/08/04"[Date - Publication]))`
*   **Variant C (Hybrid / High-precision):** `((("Multiple Sclerosis"[Mesh] OR "multiple sclerosis"[tiab])) AND (("Sleep Wake Disorders"[Mesh:NoExp]) OR "sleep disturbance*"[tiab] OR insomnia[tiab] OR "sleep apnea"[tiab] OR "restless legs syndrome"[tiab] OR narcolepsy[tiab] OR "REM sleep behavior disorder"[tiab])) AND (("Cognitive Behavioral Therapy"[Mesh] OR "Exercise Therapy"[Mesh] OR "Mind-Body Therapies"[Mesh] OR "cognitive behavioral therapy"[tiab] OR "cognitive behaviour therapy"[tiab] OR exercise[tiab] OR "physical activity"[tiab] OR mindfulness[tiab] OR "sleep hygiene"[tiab])) AND (("Randomized Controlled Trial"[Publication Type]) OR randomi*ed[tiab] OR placebo[tiab])) AND (("1000/01/01"[Date - Publication] : "2024/08/04"[Date - Publication]))`

---
#### **PubMed Micro-variant Grid**

*   **Recall_Lock (Invariant Core):** `((("Multiple Sclerosis"[Mesh] OR "multiple sclerosis"[tiab])) AND (("Sleep Wake Disorders"[Mesh]) OR sleep*[tiab])) AND (("Randomized Controlled Trial"[Publication Type]) OR randomi*ed[tiab] OR placebo[tiab] OR trial[tiab]))`
*   **Precision_Knobs List:** `humans`, `english`, `rct_tiab`, `narrow_sleep_block`, `no_exp`, `title_emphasis`, `doc_type_exclusion`

*   **V1 (Add Filters):** `((((("Multiple Sclerosis"[Mesh] OR "multiple sclerosis"[tiab])) AND (("Sleep Wake Disorders"[Mesh]) OR sleep*[tiab])) AND (("Randomized Controlled Trial"[Publication Type]) OR randomi*ed[tiab] OR placebo[tiab] OR trial[tiab]))) AND (English[lang])) AND (humans[mh])`
    *   *Rationale:* Adds standard high-value filters to remove non-human studies and non-English articles, which are exclusion criteria.
    *   *expected_recall_delta:* minimal
*   **V2 (Require TIAB for RCT):** `((("Multiple Sclerosis"[Mesh] OR "multiple sclerosis"[tiab])) AND (("Sleep Wake Disorders"[Mesh]) OR sleep*[tiab])) AND (randomi*ed[tiab] OR placebo[tiab] OR trial[tiab])`
    *   *Rationale:* Strengthens the study design requirement by removing the broad Publication Type and demanding explicit RCT signal words in the title or abstract.
    *   *expected_recall_delta:* minimal
*   **V3 (Narrow Sleep Block):** `((("Multiple Sclerosis"[Mesh] OR "multiple sclerosis"[tiab])) AND (("Insomnia"[Mesh]) OR ("Sleep Apnea Syndromes"[Mesh]) OR ("Restless Legs Syndrome"[Mesh]) OR insomnia[tiab] OR "sleep disturbance"[tiab] OR "sleep quality"[tiab])) AND (("Randomized Controlled Trial"[Publication Type]) OR randomi*ed[tiab] OR placebo[tiab] OR trial[tiab]))`
    *   *Rationale:* Replaces the broad `sleep*` textword and general `Sleep Wake Disorders` MeSH with a more specific list of key disorders and terms.
    *   *expected_recall_delta:* minimal
*   **V4 (Use MeSH:NoExp):** `((("Multiple Sclerosis"[Mesh:NoExp] OR "multiple sclerosis"[tiab])) AND (("Sleep Wake Disorders"[Mesh:NoExp]) OR sleep*[tiab])) AND (("Randomized Controlled Trial"[Publication Type]) OR randomi*ed[tiab] OR placebo[tiab] OR trial[tiab]))`
    *   *Rationale:* Prevents explosion of broad MeSH terms, focusing the search on articles where these are the primary topic.
    *   *expected_recall_delta:* minimal
*   **V5 (Title Emphasis):** `((("Multiple Sclerosis"[Mesh] OR "multiple sclerosis"[tiab] OR "multiple sclerosis"[ti])) AND (("Sleep Wake Disorders"[Mesh]) OR sleep*[tiab])) AND (("Randomized Controlled Trial"[Publication Type]) OR randomi*ed[tiab] OR placebo[tiab] OR trial[ti] OR trial[tiab]))`
    *   *Rationale:* Boosts precision by requiring either "multiple sclerosis" or "trial" to appear in the title, suggesting higher relevance.
    *   *expected_recall_delta:* minimal
*   **V6 (Exclude Doc Types):** `((((("Multiple Sclerosis"[Mesh] OR "multiple sclerosis"[tiab])) AND (("Sleep Wake Disorders"[Mesh]) OR sleep*[tiab])) AND (("Randomized Controlled Trial"[Publication Type]) OR randomi*ed[tiab] OR placebo[tiab] OR trial[tiab]))) NOT (Letter[pt] OR Editorial[pt] OR Comment[pt] OR "Case Reports"[pt]))`
    *   *Rationale:* Excludes common non-research publication types that are unlikely to be RCTs, cleaning the results.
    *   *expected_recall_delta:* none

---
#### **EMBASE (Ovid)**
*   **Variant C (Hybrid / High-precision):** `((exp multiple sclerosis/ or 'multiple sclerosis'.ti,ab.) and (exp sleep disorder/ or 'sleep disturbance*'.ti,ab. or insomnia.ti,ab. or 'sleep apnea'.ti,ab. or 'restless legs syndrome'.ti,ab. or narcolepsy.ti,ab.)) and (exp cognitive behavior therapy/ or exp exercise therapy/ or exp mind body therapy/ or 'cognitive behavioral therapy'.ti,ab. or 'cognitive behaviour therapy'.ti,ab. or exercise.ti,ab. or 'physical activity'.ti,ab. or mindfulness.ti,ab. or 'sleep hygiene'.ti,ab.) and (exp randomized controlled trial/ or randomi*ed.ti,ab. or placebo.ti,ab.)) and (limit to <20240805)`

---
#### **Scopus**
*   **Variant C (Hybrid / High-precision):** `(TITLE-ABS-KEY("multiple sclerosis") AND TITLE-ABS-KEY(sleep* OR insomnia OR "sleep apnea" OR "restless legs syndrome" OR narcolepsy OR "sleep disturbance")) AND (TITLE-ABS-KEY("cognitive behavio* therapy" OR exercise OR "physical activity" OR mindfulness OR "sleep hygiene")) AND (TITLE-ABS-KEY(randomi*ed OR placebo OR "controlled trial")) AND (PUBDATETXT("before 2024-08-05"))`

---
#### **PsycINFO (Ovid)**
*   **Variant C (Hybrid / High-precision):** `((exp Multiple Sclerosis/ or "multiple sclerosis".ti,ab.) and (exp Sleep Disorders/ or sleep*.ti,ab. or insomnia.ti,ab. or "sleep disturbance*".ti,ab.)) and (exp Cognitive Behavior Therapy/ or exp Exercise/ or exp Relaxation/ or "cognitive behavioral therapy".ti,ab. or "cognitive behaviour therapy".ti,ab. or exercise.ti,ab. or mindfulness.ti,ab.) and (exp "treatment effectiveness evaluation"/ or randomi*ed.ti,ab. or placebo.ti,ab.) and (publication year < 2025 and publication month < august and publication day < 5)`

---
#### **Cochrane Library**
*   **Variant C (Hybrid / High-precision):** `([mh "Multiple Sclerosis"] OR "multiple sclerosis":ti,ab) AND ([mh "Sleep Wake Disorders"] OR sleep*:ti,ab OR insomnia:ti,ab OR "sleep disturbance":ti,ab) AND ([mh "Cognitive Behavioral Therapy"] OR "cognitive behavioral therapy":ti,ab OR exercise:ti,ab OR mindfulness:ti,ab) AND (([mh "Randomized Controlled Trials"] OR random*:ti,ab OR placebo:ti,ab)) AND (pubyear < 2025)`

### 4) PRESS Self-Check

*   **Issues:**
    *   The "Non-pharmacological interventions" concept is extremely broad and difficult to capture exhaustively. The current textword list is representative but not exhaustive, which could risk recall.
    *   Using single acronyms like `MS[tiab]` or `RLS[tiab]` without context (e.g., `(MS AND sleep*)`) can retrieve irrelevant results. The hybrid query avoids this, but the text-heavy one is at risk.
    *   The date filtering syntax varies significantly and requires careful application on each platform.

*   **Minimal Revised Queries (for PubMed):**
    1.  **Revised Query 1 (Broader Intervention):** `((("Multiple Sclerosis"[Mesh] OR "multiple sclerosis"[tiab])) AND (("Sleep Wake Disorders"[Mesh:NoExp]) OR "sleep disturbance*"[tiab] OR insomnia[tiab] OR "sleep apnea"[tiab] OR "restless legs syndrome"[tiab])) AND (("Randomized Controlled Trial"[Publication Type]) OR randomi*ed[tiab] OR placebo[tiab])) NOT ("drug therapy"[Subheading] OR "drug therapy"[tiab] OR drug*[tiab] OR pharmaco*[tiab])`
        *   *Rationale:* This query removes the complex intervention block and instead searches for all RCTs on sleep in MS, then excludes studies explicitly mentioning pharmacological therapy, aiming to capture a wider range of non-pharmaceutical interventions.
    2.  **Revised Query 2 (High-Precision Sleep Focus):** `((("Multiple Sclerosis"[Mesh] OR "multiple sclerosis"[tiab])) AND (("Insomnia"[Mesh] OR insomnia[tiab]) OR ("Sleep Apnea Syndromes"[Mesh] OR "sleep apnea"[tiab]) OR ("Restless Legs Syndrome"[Mesh] OR "restless legs syndrome"[tiab]))) AND (("Randomized Controlled Trial"[Publication Type]) OR randomi*ed[tiab] OR placebo[tiab])) AND (English[lang]) AND (humans[mh])`
        *   *Rationale:* Narrows the sleep concept to only the most common, well-defined disorders in MS (Insomnia, Apnea, RLS) to increase precision, while also adding standard filters. This query omits the intervention block to maximize recall for any intervention targeting these specific conditions.

### 5) Translation Notes

*   **Controlled Vocabulary:** MeSH (PubMed) `[Mesh]`, Emtree (EMBASE) `exp/`, PsycINFO Thesaurus `exp/`, and Cochrane `[mh]` are used. Scopus has limited controlled vocabulary, relying on `TITLE-ABS-KEY`.
*   **Field Codes:** `[tiab]` (PubMed) is equivalent to `.ti,ab.` (Ovid platforms like EMBASE/PsycINFO), `TITLE-ABS-KEY` (Scopus), and `:ti,ab` (Cochrane).
*   **Proximity Operators:** Not used in PubMed. EMBASE/Ovid uses `adjN`, Scopus uses `W/N`, and Cochrane uses `NEAR/N`. These were omitted from the main queries for simplicity and cross-database consistency but could be used to refine textword searches (e.g., `(sleep W/2 disturb*)` in Scopus).
*   **Truncation:** `*` is common, but Ovid uses `*` or `$`.
*   **Date Filtering:** Syntax is highly platform-specific. The examples provided are illustrative.

### 6) Date Window

*   All searches should be run to capture publications up to, but not including, **August 5, 2024**. The syntax for this varies by database.