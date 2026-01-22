### 1. Concept Tables (Markdown)

#### Concept→MeSH/Emtree Table

| Concept                   | Term                               | Tree Note                        | Explode? | Rationale & Source                               |
| ------------------------- | ---------------------------------- | -------------------------------- | -------- | ------------------------------------------------ |
| **SDB**                   | `Sleep Apnea Syndromes`            | MeSH C08.795.790                 | Yes      | Broad parent term for all sleep apnea types.     |
| **SDB**                   | `Snoring`                          | MeSH C08.795.760                 | Yes      | Key component of SDB spectrum.                   |
| **SDB**                   | `'sleep disordered breathing'/exp` | Emtree                           | Yes      | Most direct mapping for the core concept.        |
| **SDB**                   | `'obstructive sleep apnea'/exp`    | Emtree                           | Yes      | Essential specific type of SDB.                  |
| **Blood Pressure**        | `Blood Pressure`                   | MeSH G09.330.120.150             | Yes      | Core outcome measure.                            |
| **Blood Pressure**        | `Hypertension`                     | MeSH C23.888.592.510.450         | Yes      | Key clinical outcome related to high BP.         |
| **Blood Pressure**        | `'blood pressure'/exp`             | Emtree                           | Yes      | Core outcome measure.                            |
| **Blood Pressure**        | `'hypertension'/exp`               | Emtree                           | Yes      | Key clinical outcome.                            |
| **Population**            | `Child`                            | MeSH M01.050.150.125.120         | Yes      | Core population group.                           |
| **Population**            | `Adolescent`                       | MeSH M01.050.150.125.050         | Yes      | Core population group.                           |
| **Population**            | `'child'/exp`                      | Emtree                           | Yes      | Core population group (includes infants).        |
| **Population**            | `'adolescent'/exp`                 | Emtree                           | Yes      | Core population group.                           |

#### Concept→Textword Table

| Concept                   | Synonym/Phrase                          | Field      | Truncation? | Rationale & Source                                        |
| ------------------------- | --------------------------------------- | ---------- | ----------- | --------------------------------------------------------- |
| **SDB**                   | `sleep disordered breathing`            | tiab/Title-Abs-Key/TS | No          | Exact phrase for the main concept.                        |
| **SDB**                   | `SDB`                                   | tiab/Title-Abs-Key/TS | No          | Common acronym.                                           |
| **SDB**                   | `sleep apnea`                           | tiab/Title-Abs-Key/TS | Yes (`apnea*`) | Captures singular and plural forms (apnea, apneas).       |
| **SDB**                   | `obstructive sleep apnea`               | tiab/Title-Abs-Key/TS | No          | Specific and common form of SDB.                          |
| **SDB**                   | `OSA`                                   | tiab/Title-Abs-Key/TS | No          | Common acronym.                                           |
| **SDB**                   | `snoring`                               | tiab/Title-Abs-Key/TS | No          | A primary symptom and condition in the SDB spectrum.      |
| **Blood Pressure**        | `blood pressure`                        | tiab/Title-Abs-Key/TS | No          | The primary outcome of interest.                          |
| **Blood Pressure**        | `hypertension`                          | tiab/Title-Abs-Key/TS | Yes (`hypertens*`) | Captures hypertension, hypertensive.                      |
| **Blood Pressure**        | `BP`                                    | tiab/Title-Abs-Key/TS | No          | Common acronym.                                           |
| **Blood Pressure**        | `nondipping`                            | tiab/Title-Abs-Key/TS | No          | Specific outcome from PICOS.                              |
| **Blood Pressure**        | `non-dipping`                           | tiab/Title-Abs-Key/TS | No          | Common variant spelling.                                  |
| **Population**            | `child`                                 | tiab/Title-Abs-Key/TS | Yes (`child*`) | Captures child, children.                                 |
| **Population**            | `adolescent`                            | tiab/Title-Abs-Key/TS | Yes (`adolescen*`) | Captures adolescent, adolescence.                         |
| **Population**            | `pediatric`                             | tiab/Title-Abs-Key/TS | Yes (`p*ediatric*`) | Captures pediatric, paediatric.                           |
| **Population**            | `infant`                                | tiab/Title-Abs-Key/TS | Yes (`infan*`) | Captures infant, infancy.                                 |
| **Population**            | `teenager`                              | tiab/Title-Abs-Key/TS | Yes (`teen*`) | Captures teen, teens, teenager.                           |

### 2. JSON Query Object

```json
{
  "pubmed": [
    "# High-recall: Emphasizes broad MeSH terms and extensive synonyms to maximize retrieval.",
    "(((\"Sleep Apnea Syndromes\"[Mesh] OR \"Snoring\"[Mesh]) OR (\"sleep disordered breathing\"[tiab] OR \"sleep apnea\"[tiab] OR \"SDB\"[tiab] OR \"obstructive sleep apnea\"[tiab] OR \"OSA\"[tiab] OR \"snoring\"[tiab])) AND ((\"Blood Pressure\"[Mesh] OR \"Hypertension\"[Mesh]) OR (\"blood pressure\"[tiab] OR \"hypertension\"[tiab] OR \"BP\"[tiab] OR \"nondipping\"[tiab] OR \"non-dipping\"[tiab])) AND ((\"Child\"[Mesh] OR \"Adolescent\"[Mesh] OR \"Infant\"[Mesh]) OR (\"child*\"[tiab] OR \"adolescen*\"[tiab] OR \"p*ediatric\"[tiab] OR \"infan*\"[tiab] OR \"teen*\"[tiab]))) AND (\"1990/01/01\"[Date - Publication] : \"2024/12/31\"[Date - Publication])",
    "# Balanced: A hybrid of key MeSH terms and essential free-text synonyms for a mix of recall and precision.",
    "(((\"Sleep Apnea Syndromes\"[Mesh]) OR (\"sleep disordered breathing\"[tiab] OR \"sleep apnea\"[tiab] OR \"snoring\"[tiab])) AND ((\"Blood Pressure\"[Mesh]) OR (\"blood pressure\"[tiab] OR \"hypertension\"[tiab])) AND ((\"Child\"[Mesh] OR \"Adolescent\"[Mesh]) OR (\"child*\"[tiab] OR \"adolescen*\"[tiab] OR \"pediatric\"[tiab]))) AND (\"1990/01/01\"[Date - Publication] : \"2024/12/31\"[Date - Publication])",
    "# High-precision: Emphasizes major MeSH headings and title-only searches for core concepts.",
    "(((\"Sleep Apnea, Obstructive\"[majr] OR \"Snoring\"[majr]) OR (\"sleep disordered breathing\"[ti] OR \"obstructive sleep apnea\"[ti])) AND ((\"Hypertension\"[majr]) OR (\"blood pressure\"[ti] OR \"hypertension\"[ti])) AND ((\"Child\"[majr] OR \"Adolescent\"[majr]) OR (\"pediatric\"[ti] OR \"child\"[ti]))) AND (\"1990/01/01\"[Date - Publication] : \"2024/12/31\"[Date - Publication])",
    "# Micro-variant 1 (Filter-based): Starts with the 'Balanced' query and adds human and English language filters.",
    "(((\"Sleep Apnea Syndromes\"[Mesh]) OR (\"sleep disordered breathing\"[tiab] OR \"sleep apnea\"[tiab] OR \"snoring\"[tiab])) AND ((\"Blood Pressure\"[Mesh]) OR (\"blood pressure\"[tiab] OR \"hypertension\"[tiab])) AND ((\"Child\"[Mesh] OR \"Adolescent\"[Mesh]) OR (\"child*\"[tiab] OR \"adolescen*\"[tiab] OR \"pediatric\"[tiab]))) AND (\"1990/01/01\"[Date - Publication] : \"2024/12/31\"[Date - Publication]) AND (humans[Filter] AND english[Filter])",
    "# Micro-variant 2 (Field/Scope-based): Starts with the 'Balanced' query and restricts key concepts to the title field for higher specificity.",
    "(((\"Sleep Apnea Syndromes\"[Mesh]) OR (\"sleep disordered breathing\"[ti] OR \"sleep apnea\"[ti] OR \"snoring\"[ti])) AND ((\"Blood Pressure\"[Mesh]) OR (\"blood pressure\"[ti] OR \"hypertension\"[ti])) AND ((\"Child\"[Mesh] OR \"Adolescent\"[Mesh]) OR (\"child*\"[tiab] OR \"adolescen*\"[tiab] OR \"pediatric\"[tiab]))) AND (\"1990/01/01\"[Date - Publication] : \"2024/12/31\"[Date - Publication])",
    "# Micro-variant 3 (Proximity-based Fallback): Starts with the 'Balanced' query and uses major MeSH headings for core concepts as a fallback for proximity.",
    "(((\"Sleep Apnea Syndromes\"[majr]) OR (\"sleep disordered breathing\"[tiab] OR \"sleep apnea\"[tiab] OR \"snoring\"[tiab])) AND ((\"Blood Pressure\"[majr]) OR (\"blood pressure\"[tiab] OR \"hypertension\"[tiab])) AND ((\"Child\"[Mesh] OR \"Adolescent\"[Mesh]) OR (\"child*\"[tiab] OR \"adolescen*\"[tiab] OR \"pediatric\"[tiab]))) AND (\"1990/01/01\"[Date - Publication] : \"2024/12/31\"[Date - Publication])"
  ],
  "scopus": [
    "# High-recall: Broad search using TITLE-ABS-KEY for all synonyms and acronyms.",
    "(TITLE-ABS-KEY(\"sleep disordered breathing\" OR \"sleep apnea\" OR SDB OR \"obstructive sleep apnea\" OR OSA OR snoring) AND TITLE-ABS-KEY(\"blood pressure\" OR hypertension OR BP OR nondipping OR \"non-dipping\") AND TITLE-ABS-KEY(child* OR adolescen* OR p*ediatric OR infan* OR teen*)) AND (PUBYEAR > 1989 AND PUBYEAR < 2025)",
    "# Balanced: A hybrid using proximity for key concepts while still capturing major synonyms.",
    "(TITLE-ABS-KEY((\"sleep apnea\" OR \"sleep disordered breathing\") W/5 (child* OR adolescen* OR pediatric*)) AND TITLE-ABS-KEY(snoring OR \"obstructive sleep apnea\") AND TITLE-ABS-KEY(\"blood pressure\" OR hypertension)) AND (PUBYEAR > 1989 AND PUBYEAR < 2025)",
    "# High-precision: Tighter proximity (W/2) and title-only searches for core concepts.",
    "(TITLE((\"sleep apnea\" OR snoring) AND (\"blood pressure\" OR hypertension)) AND TITLE-ABS-KEY((\"sleep disordered breathing\" W/2 (child* OR adolescen*)))) AND (PUBYEAR > 1989 AND PUBYEAR < 2025)",
    "# Micro-variant 1 (Filter-based): Starts with the 'Balanced' query and limits to articles, reviews, and the medicine subject area.",
    "(TITLE-ABS-KEY((\"sleep apnea\" OR \"sleep disordered breathing\") W/5 (child* OR adolescen* OR pediatric*)) AND TITLE-ABS-KEY(snoring OR \"obstructive sleep apnea\") AND TITLE-ABS-KEY(\"blood pressure\" OR hypertension)) AND (DOCTYPE(ar OR re)) AND (SUBJAREA(MEDI)) AND (PUBYEAR > 1989 AND PUBYEAR < 2025)",
    "# Micro-variant 2 (Field/Scope-based): Starts with the 'Balanced' query and restricts the SDB and BP concepts to the title field.",
    "(TITLE((\"sleep apnea\" OR \"sleep disordered breathing\") AND (\"blood pressure\" OR hypertension)) AND TITLE-ABS-KEY(child* OR adolescen* OR pediatric*) AND TITLE-ABS-KEY(snoring OR \"obstructive sleep apnea\")) AND (PUBYEAR > 1989 AND PUBYEAR < 2025)",
    "# Micro-variant 3 (Proximity-based): Starts with the 'Balanced' query and tightens proximity to W/3 for the main concepts.",
    "(TITLE-ABS-KEY((\"sleep apnea\" OR \"sleep disordered breathing\") W/3 (child* OR adolescen* OR pediatric*)) AND TITLE-ABS-KEY(snoring OR \"obstructive sleep apnea\") AND TITLE-ABS-KEY(\"blood pressure\" OR hypertension)) AND (PUBYEAR > 1989 AND PUBYEAR < 2025)"
  ],
  "embase": [
    "# High-recall: Emphasizes broad, exploded Emtree terms and extensive synonyms in title/abstract.",
    "('sleep disordered breathing'/exp OR 'snoring'/exp OR 'obstructive sleep apnea'/exp OR 'sleep apnea':ti,ab OR 'snoring':ti,ab) AND ('blood pressure'/exp OR 'hypertension'/exp OR 'blood pressure':ti,ab OR 'hypertension':ti,ab) AND ('child'/exp OR 'adolescent'/exp OR 'pediatric':ti,ab OR 'child':ti,ab OR 'adolescent':ti,ab) AND limit to yr=\"1990-2024\"",
    "# Balanced: A hybrid of exploded Emtree terms and key free-text synonyms for a mix of recall and precision.",
    "('sleep disordered breathing'/exp OR 'sleep apnea':ti,ab OR 'snoring':ti,ab) AND ('blood pressure'/exp OR 'hypertension':ti,ab) AND ('child'/exp OR 'adolescent'/exp OR 'pediatric':ti,ab) AND limit to yr=\"1990-2024\"",
    "# High-precision: Uses major focus Emtree terms and adjacent proximity for key free-text words.",
    "(*'obstructive sleep apnea'/exp OR *'snoring'/exp OR ('sleep' ADJ2 'apnea'):ti,ab) AND (*'hypertension'/exp OR 'blood pressure':ti,ab) AND (*'child'/exp OR *'adolescent'/exp) AND limit to yr=\"1990-2024\"",
    "# Micro-variant 1 (Filter-based): Starts with the 'Balanced' query and limits results to articles and reviews.",
    "('sleep disordered breathing'/exp OR 'sleep apnea':ti,ab OR 'snoring':ti,ab) AND ('blood pressure'/exp OR 'hypertension':ti,ab) AND ('child'/exp OR 'adolescent'/exp OR 'pediatric':ti,ab) AND (limit to (article or review)) AND limit to yr=\"1990-2024\"",
    "# Micro-variant 2 (Field/Scope-based): Starts with the 'Balanced' query and restricts key free-text terms to the title field.",
    "('sleep disordered breathing'/exp OR 'sleep apnea':ti OR 'snoring':ti) AND ('blood pressure'/exp OR 'hypertension':ti) AND ('child'/exp OR 'adolescent'/exp OR 'pediatric':ti,ab) AND limit to yr=\"1990-2024\"",
    "# Micro-variant 3 (Proximity-based): Starts with the 'Balanced' query and requires SDB and BP concepts to be adjacent within 5 words.",
    "((('sleep disordered breathing'/exp) OR 'sleep apnea':ti,ab OR 'snoring':ti,ab) ADJ5 (('blood pressure'/exp) OR 'hypertension':ti,ab)) AND ('child'/exp OR 'adolescent'/exp OR 'pediatric':ti,ab) AND limit to yr=\"1990-2024\""
  ],
  "wos": [
    "# High-recall: Broad search using Topic (TS) for all synonyms and truncated terms.",
    "TS=(\"sleep disordered breathing\" OR \"sleep apne*\" OR SDB OR \"obstructive sleep apnea\" OR OSA OR snoring) AND TS=(\"blood pressure\" OR hypertens* OR BP OR nondipping OR \"non-dipping\") AND TS=(child* OR adolescen* OR p*ediatric OR infan* OR teen*) AND PY=(1990-2024)",
    "# Balanced: A hybrid using proximity (NEAR/5) for core concepts while still capturing major synonyms.",
    "TS=((\"sleep apne*\" OR \"sleep disordered breathing\") NEAR/5 (child* OR adolescen* OR pediatric*)) AND TS=(\"blood pressure\" OR hypertens*) AND PY=(1990-2024)",
    "# High-precision: Tighter proximity (NEAR/3) and title-only (TI) searches for core concepts.",
    "TI=((\"sleep apne*\" OR snoring) AND (\"blood pressure\" OR hypertens*)) AND TS=(child* OR adolescen*) AND PY=(1990-2024)",
    "# Micro-variant 1 (Filter-based): Starts with the 'Balanced' query and limits to articles and reviews.",
    "TS=((\"sleep apne*\" OR \"sleep disordered breathing\") NEAR/5 (child* OR adolescen* OR pediatric*)) AND TS=(\"blood pressure\" OR hypertens*) AND DT=(Article OR Review) AND PY=(1990-2024)",
    "# Micro-variant 2 (Field/Scope-based): Starts with the 'Balanced' query and restricts the main SDB and BP concepts to the title field.",
    "TI=((\"sleep apne*\" OR \"sleep disordered breathing\") AND (\"blood pressure\" OR hypertens*)) AND TS=(child* OR adolescen* OR pediatric*) AND PY=(1990-2024)",
    "# Micro-variant 3 (Proximity-based): Starts with the 'Balanced' query and tightens the proximity operator to NEAR/3.",
    "TS=((\"sleep apne*\" OR \"sleep disordered breathing\") NEAR/3 (child* OR adolescen* OR pediatric*)) AND TS=(\"blood pressure\" OR hypertens*) AND PY=(1990-2024)"
  ]
}
```
```json
{
  "json_patch": {
    "scopus": {
      "1": "# Balanced (revised): Added 'UARS' (Upper Airway Resistance Syndrome) for better recall, as it's part of the SDB spectrum.",
      "(TITLE-ABS-KEY((\"sleep apnea\" OR \"sleep disordered breathing\" OR UARS) W/5 (child* OR adolescen* OR pediatric*)) AND TITLE-ABS-KEY(snoring OR \"obstructive sleep apnea\") AND TITLE-ABS-KEY(\"blood pressure\" OR hypertension)) AND (PUBYEAR > 1989 AND PUBYEAR < 2025)"
    }
  }
}
```