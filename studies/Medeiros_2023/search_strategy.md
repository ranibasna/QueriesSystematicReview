# Search Strategy for Medeiros_2023

## Study Summary

- Topic: Sleep duration and sleep quality in relation to inflammatory biomarkers in children and adolescents
- Date window: No inline publication-date restriction; the protocol does not specify a date limit
- Databases: pubmed, scopus, wos, embase
- Query level: extended
- Retrieval architecture: single_route
- design_analytic_block: active, but populated conservatively and reserved for high-precision and bundled variants

## PICOS Summary

- Population: Children aged at least 2 years and adolescents up to 19 years
- Intervention or Exposure: Sleep duration, sleep time, sleep quality, and sleep disturbance measured subjectively or objectively
- Comparator: Children with adequate sleep time
- Outcomes: Inflammatory biomarkers, especially C-reactive protein, interleukin-6, adiponectin, and TNF-alpha blood levels
- Design: Observational epidemiological studies, especially cross-sectional, cohort, and case-control studies

## Architecture Selection Summary

- Selected retrieval architecture: `single_route`
- `design_analytic_block`: active

### Concept Roles

| Role | Assigned concepts |
| --- | --- |
| mandatory_core | pediatric population; sleep duration or sleep quality exposure; inflammatory biomarkers or inflammation outcome domain |
| optional_precision | short or long sleep duration wording; poor sleep quality and sleep disturbance wording; named biomarker terms such as CRP, IL-6, TNF-alpha, and adiponectin |
| filter_only | observational-study labels; original-article limits where platform-safe; protocol language limits in English, Spanish, and Portuguese as interface-applied limits |
| screening_only | adequate-sleep comparator wording; device or questionnaire requirements; exclusions for medical conditions or medication use that may affect sleep |

The protocol supports one coherent Boolean route rather than a protocol-justified split into indexed and textword routes, so `single_route` is the safer fit. The active `design_analytic_block` is explicit in the protocol because eligible studies are observational, but those labels are not retrieval-defining enough for baseline Q1 and are therefore reserved for Q3 and the bundled `design_plus_scope` variant.

## Concept Tables

### Concept to MeSH or Emtree

| concept | term | tree note | explode? | rationale and source |
| --- | --- | --- | --- | --- |
| pediatric population | Child; Preschool Child; Adolescent / child; adolescent | indexed support for the protocol age range | Yes | Protocol population and inclusion criteria |
| sleep exposure core | Sleep / sleep | broad indexed anchor for the sleep domain | Yes | Protocol title, objective, and condition section |
| sleep exposure core | Sleep Deprivation / sleep deprivation | indexed support for short sleep or sleep restriction framing | Yes | Protocol exposure description discusses sleep restriction and short sleep duration |
| sleep exposure core | Sleep Quality / sleep quality | indexed support for the named sleep-quality construct | Mixed | Protocol title and exposure description |
| inflammation outcome core | Inflammation / inflammation | broad indexed anchor for inflammatory outcomes | Yes | Protocol objective and main outcomes |
| inflammation outcome core | C-Reactive Protein; Interleukin-6; Tumor Necrosis Factor-alpha; Adiponectin / c reactive protein; interleukin 6; tumor necrosis factor alpha; adiponectin | indexed support for the protocol-named biomarkers | Yes | Protocol keywords and main outcomes |
| design block | Cohort Studies; Cross-Sectional Studies; Case-Control Studies / cohort analysis; cross-sectional study; case control study | observational-design support | Yes | Protocol study design eligibility |

### Concept to Textword

| concept | synonym or phrase | field | truncation? | source |
| --- | --- | --- | --- | --- |
| pediatric population | child*; adolescen*; teen*; teenager*; youth; preschool* | title/abstract/topic | Mixed | Protocol population and keywords |
| sleep exposure core | sleep duration; sleep time; sleep quality | title/abstract/topic | No | Protocol title, objective, and exposure section |
| sleep exposure core | short sleep duration; long sleep duration | title/abstract/topic | No | Protocol keywords |
| sleep exposure core | poor sleep quality; sleep disturbance; sleep disturbances; sleep restriction | title/abstract/topic | Mixed | Protocol exposure and condition descriptions |
| inflammation outcome core | inflammation; inflammatory profile; inflammatory biomarker; inflammatory biomarkers | title/abstract/topic | Mixed | Protocol objective and keywords |
| inflammation outcome core | C-reactive protein; CRP; interleukin 6; IL-6; adiponectin; TNF alpha; TNF-alpha; tumor necrosis factor alpha | title/abstract/topic | No | Protocol keywords and main outcomes |
| design block | observational; cohort; prospective; cross-sectional; case-control; case control | title/abstract/topic | No | Protocol study-design eligibility |
| comparator screening | adequate sleep time; adequate sleep duration | title/abstract/topic | No | Protocol comparator |

## JSON Query Object

```json
{
  "pubmed": [
    "# Q1: High-recall\n((\"Child\"[Mesh] OR \"Preschool Child\"[Mesh] OR \"Adolescent\"[Mesh] OR child*[tiab] OR adolescen*[tiab] OR teen*[tiab] OR teenager*[tiab] OR youth[tiab] OR preschool*[tiab]) AND (\"Sleep\"[Mesh] OR \"Sleep Deprivation\"[Mesh] OR \"Sleep Quality\"[Mesh] OR \"sleep duration\"[tiab] OR \"sleep time\"[tiab] OR \"sleep quality\"[tiab] OR \"short sleep duration\"[tiab] OR \"long sleep duration\"[tiab] OR \"poor sleep quality\"[tiab] OR \"sleep disturbance\"[tiab] OR \"sleep disturbances\"[tiab] OR \"sleep restriction\"[tiab] OR ((sleep[tiab] OR sleeping[tiab]) AND (duration[tiab] OR time[tiab] OR quality[tiab]))) AND (\"Inflammation\"[Mesh] OR \"C-Reactive Protein\"[Mesh] OR \"Interleukin-6\"[Mesh] OR \"Tumor Necrosis Factor-alpha\"[Mesh] OR \"Adiponectin\"[Mesh] OR inflammation[tiab] OR \"inflammatory profile\"[tiab] OR \"inflammatory biomarker\"[tiab] OR \"inflammatory biomarkers\"[tiab] OR \"C-reactive protein\"[tiab] OR CRP[tiab] OR \"interleukin 6\"[tiab] OR \"IL-6\"[tiab] OR adiponectin[tiab] OR \"TNF alpha\"[tiab] OR \"TNF-alpha\"[tiab] OR \"tumor necrosis factor alpha\"[tiab]))",
    "# Q2: Balanced\n((\"Child\"[Mesh] OR \"Preschool Child\"[Mesh] OR \"Adolescent\"[Mesh] OR child*[tiab] OR adolescen*[tiab] OR teen*[tiab] OR teenager*[tiab] OR youth[tiab] OR preschool*[tiab]) AND (\"Sleep Deprivation\"[Mesh] OR \"Sleep Quality\"[Mesh] OR \"sleep duration\"[tiab] OR \"sleep time\"[tiab] OR \"sleep quality\"[tiab] OR \"short sleep duration\"[tiab] OR \"long sleep duration\"[tiab] OR \"poor sleep quality\"[tiab] OR \"sleep disturbance\"[tiab] OR \"sleep disturbances\"[tiab] OR \"sleep restriction\"[tiab]) AND (\"C-Reactive Protein\"[Mesh] OR \"Interleukin-6\"[Mesh] OR \"Tumor Necrosis Factor-alpha\"[Mesh] OR \"Adiponectin\"[Mesh] OR \"inflammatory biomarker\"[tiab] OR \"inflammatory biomarkers\"[tiab] OR \"C-reactive protein\"[tiab] OR CRP[tiab] OR \"interleukin 6\"[tiab] OR \"IL-6\"[tiab] OR adiponectin[tiab] OR \"TNF alpha\"[tiab] OR \"TNF-alpha\"[tiab] OR \"tumor necrosis factor alpha\"[tiab]))",
    "# Q3: High-precision\n(((\"Sleep Quality\"[Mesh] OR \"Sleep Deprivation\"[Mesh] OR \"sleep duration\"[tiab] OR \"sleep time\"[tiab] OR \"sleep quality\"[tiab] OR \"short sleep duration\"[tiab] OR \"long sleep duration\"[tiab] OR \"poor sleep quality\"[tiab] OR \"sleep disturbance\"[tiab]) AND (\"C-Reactive Protein\"[Majr] OR \"Interleukin-6\"[Majr] OR \"Tumor Necrosis Factor-alpha\"[Majr] OR \"Adiponectin\"[Majr] OR \"C-reactive protein\"[tiab] OR CRP[tiab] OR \"interleukin 6\"[tiab] OR \"IL-6\"[tiab] OR adiponectin[tiab] OR \"TNF alpha\"[tiab] OR \"TNF-alpha\"[tiab] OR \"tumor necrosis factor alpha\"[tiab]) AND (\"Child\"[Mesh] OR \"Preschool Child\"[Mesh] OR \"Adolescent\"[Mesh] OR child*[tiab] OR adolescen*[tiab] OR teen*[tiab] OR teenager*[tiab] OR youth[tiab] OR preschool*[tiab]) AND (\"Cohort Studies\"[Mesh] OR \"Cross-Sectional Studies\"[Mesh] OR \"Case-Control Studies\"[Mesh] OR observational[tiab] OR cohort[tiab] OR prospective[tiab] OR \"cross-sectional\"[tiab] OR \"case-control\"[tiab] OR \"case control\"[tiab])) AND humans[Filter])",
    "# Q4: Balanced + scope_only\n((\"sleep duration\"[ti] OR \"sleep time\"[ti] OR \"sleep quality\"[ti] OR \"short sleep duration\"[ti] OR \"long sleep duration\"[ti] OR \"poor sleep quality\"[ti] OR \"sleep disturbance\"[ti]) AND (\"C-reactive protein\"[ti] OR CRP[ti] OR \"interleukin 6\"[ti] OR \"IL-6\"[ti] OR adiponectin[ti] OR \"TNF alpha\"[ti] OR \"TNF-alpha\"[ti] OR \"tumor necrosis factor alpha\"[ti] OR inflammation[ti]) AND (child*[tiab] OR adolescen*[tiab] OR teen*[tiab] OR teenager*[tiab] OR youth[tiab] OR preschool*[tiab]))",
    "# Q5: Balanced + proximity_or_scope_fallback\n(((\"Sleep Quality\"[Majr] OR \"Sleep Deprivation\"[Majr] OR \"sleep duration\"[ti] OR \"sleep time\"[ti] OR \"sleep quality\"[ti] OR \"sleep disturbance\"[ti]) AND (\"C-Reactive Protein\"[Majr] OR \"Interleukin-6\"[Majr] OR \"Tumor Necrosis Factor-alpha\"[Majr] OR \"Adiponectin\"[Majr] OR \"C-reactive protein\"[ti] OR CRP[ti] OR \"interleukin 6\"[ti] OR \"IL-6\"[ti] OR adiponectin[ti] OR \"TNF alpha\"[ti] OR \"TNF-alpha\"[ti] OR \"tumor necrosis factor alpha\"[ti]) AND (child*[tiab] OR adolescen*[tiab] OR teen*[tiab] OR teenager*[tiab] OR youth[tiab] OR preschool*[tiab])) AND humans[Filter])",
    "# Q6: Balanced + design_plus_scope\n((\"sleep duration\"[ti] OR \"sleep time\"[ti] OR \"sleep quality\"[ti] OR \"short sleep duration\"[ti] OR \"long sleep duration\"[ti] OR \"poor sleep quality\"[ti] OR \"sleep disturbance\"[ti]) AND (\"C-reactive protein\"[ti] OR CRP[ti] OR \"interleukin 6\"[ti] OR \"IL-6\"[ti] OR adiponectin[ti] OR \"TNF alpha\"[ti] OR \"TNF-alpha\"[ti] OR \"tumor necrosis factor alpha\"[ti] OR inflammation[ti]) AND (child*[tiab] OR adolescen*[tiab] OR teen*[tiab] OR teenager*[tiab] OR youth[tiab] OR preschool*[tiab]) AND (observational[tiab] OR cohort[tiab] OR prospective[tiab] OR \"cross-sectional\"[tiab] OR \"case-control\"[tiab] OR \"case control\"[tiab]))"
  ],
  "scopus": [
    "# Q1: High-recall\nTITLE-ABS-KEY((child* OR adolescen* OR teen* OR teenager* OR youth OR preschool*) AND (\"sleep duration\" OR \"sleep time\" OR \"sleep quality\" OR \"short sleep duration\" OR \"long sleep duration\" OR \"poor sleep quality\" OR \"sleep disturbance\" OR \"sleep disturbances\" OR \"sleep restriction\" OR (sleep W/2 duration) OR (sleep W/2 quality)) AND (inflammation OR \"inflammatory profile\" OR \"inflammatory biomarker\" OR \"inflammatory biomarkers\" OR \"c-reactive protein\" OR CRP OR \"interleukin 6\" OR \"IL-6\" OR adiponectin OR \"TNF alpha\" OR \"TNF-alpha\" OR \"tumor necrosis factor alpha\"))",
    "# Q2: Balanced\nTITLE-ABS-KEY((child* OR adolescen* OR teen* OR teenager* OR youth OR preschool*) AND (\"sleep duration\" OR \"sleep time\" OR \"sleep quality\" OR \"short sleep duration\" OR \"long sleep duration\" OR \"poor sleep quality\" OR \"sleep disturbance\" OR \"sleep disturbances\" OR \"sleep restriction\") AND (\"c-reactive protein\" OR CRP OR \"interleukin 6\" OR \"IL-6\" OR adiponectin OR \"TNF alpha\" OR \"TNF-alpha\" OR \"tumor necrosis factor alpha\" OR \"inflammatory biomarker\" OR \"inflammatory biomarkers\"))",
    "# Q3: High-precision\nTITLE(\"sleep duration\" OR \"sleep time\" OR \"sleep quality\" OR \"short sleep duration\" OR \"long sleep duration\" OR \"poor sleep quality\" OR \"sleep disturbance\") AND TITLE(\"c-reactive protein\" OR CRP OR \"interleukin 6\" OR \"IL-6\" OR adiponectin OR \"TNF alpha\" OR \"TNF-alpha\") AND TITLE-ABS-KEY(child* OR adolescen* OR teen* OR teenager* OR youth OR preschool*) AND TITLE-ABS-KEY(observational OR cohort OR prospective OR \"cross-sectional\" OR \"case-control\" OR \"case control\") AND DOCTYPE(ar)",
    "# Q4: Balanced + scope_only\nTITLE(\"sleep duration\" OR \"sleep time\" OR \"sleep quality\" OR \"short sleep duration\" OR \"long sleep duration\" OR \"poor sleep quality\" OR \"sleep disturbance\") AND TITLE(\"c-reactive protein\" OR CRP OR \"interleukin 6\" OR \"IL-6\" OR adiponectin OR \"TNF alpha\" OR \"TNF-alpha\" OR inflammation) AND TITLE-ABS-KEY(child* OR adolescen* OR teen* OR teenager* OR youth OR preschool*)",
    "# Q5: Balanced + proximity_or_scope_fallback\nTITLE-ABS-KEY((child* OR adolescen* OR teen* OR teenager* OR youth OR preschool*) AND ((sleep W/2 duration) OR (sleep W/2 time) OR (sleep W/2 quality) OR (\"short sleep\" W/2 duration) OR (\"long sleep\" W/2 duration) OR (sleep W/2 disturbance) OR (sleep W/2 restriction)) AND (\"c-reactive protein\" OR CRP OR \"interleukin 6\" OR \"IL-6\" OR adiponectin OR \"TNF alpha\" OR \"TNF-alpha\" OR \"tumor necrosis factor alpha\"))",
    "# Q6: Balanced + design_plus_scope\nTITLE(\"sleep duration\" OR \"sleep time\" OR \"sleep quality\" OR \"short sleep duration\" OR \"long sleep duration\" OR \"poor sleep quality\" OR \"sleep disturbance\") AND TITLE(\"c-reactive protein\" OR CRP OR \"interleukin 6\" OR \"IL-6\" OR adiponectin OR \"TNF alpha\" OR \"TNF-alpha\" OR inflammation) AND TITLE-ABS-KEY(child* OR adolescen* OR teen* OR teenager* OR youth OR preschool*) AND TITLE-ABS-KEY(observational OR cohort OR prospective OR \"cross-sectional\" OR \"case-control\" OR \"case control\") AND DOCTYPE(ar)"
  ],
  "wos": [
    "# Q1: High-recall\nTS=((child* OR adolescen* OR teen* OR teenager* OR youth OR preschool*) AND (\"sleep duration\" OR \"sleep time\" OR \"sleep quality\" OR \"short sleep duration\" OR \"long sleep duration\" OR \"poor sleep quality\" OR \"sleep disturbance\" OR \"sleep disturbances\" OR \"sleep restriction\" OR (sleep NEAR/2 duration) OR (sleep NEAR/2 quality)) AND (inflammation OR \"inflammatory profile\" OR \"inflammatory biomarker\" OR \"inflammatory biomarkers\" OR \"c-reactive protein\" OR CRP OR \"interleukin 6\" OR \"IL-6\" OR adiponectin OR \"TNF alpha\" OR \"TNF-alpha\" OR \"tumor necrosis factor alpha\"))",
    "# Q2: Balanced\nTS=((child* OR adolescen* OR teen* OR teenager* OR youth OR preschool*) AND (\"sleep duration\" OR \"sleep time\" OR \"sleep quality\" OR \"short sleep duration\" OR \"long sleep duration\" OR \"poor sleep quality\" OR \"sleep disturbance\" OR \"sleep disturbances\" OR \"sleep restriction\") AND (\"c-reactive protein\" OR CRP OR \"interleukin 6\" OR \"IL-6\" OR adiponectin OR \"TNF alpha\" OR \"TNF-alpha\" OR \"tumor necrosis factor alpha\" OR \"inflammatory biomarker\" OR \"inflammatory biomarkers\"))",
    "# Q3: High-precision\nTI=(\"sleep duration\" OR \"sleep time\" OR \"sleep quality\" OR \"short sleep duration\" OR \"long sleep duration\" OR \"poor sleep quality\" OR \"sleep disturbance\") AND TI=(\"c-reactive protein\" OR CRP OR \"interleukin 6\" OR \"IL-6\" OR adiponectin OR \"TNF alpha\" OR \"TNF-alpha\") AND TS=(child* OR adolescen* OR teen* OR teenager* OR youth OR preschool*) AND TS=(observational OR cohort OR prospective OR \"cross-sectional\" OR \"case-control\" OR \"case control\") AND DT=(Article)",
    "# Q4: Balanced + scope_only\nTI=(\"sleep duration\" OR \"sleep time\" OR \"sleep quality\" OR \"short sleep duration\" OR \"long sleep duration\" OR \"poor sleep quality\" OR \"sleep disturbance\") AND TI=(\"c-reactive protein\" OR CRP OR \"interleukin 6\" OR \"IL-6\" OR adiponectin OR \"TNF alpha\" OR \"TNF-alpha\" OR inflammation) AND TS=(child* OR adolescen* OR teen* OR teenager* OR youth OR preschool*)",
    "# Q5: Balanced + proximity_or_scope_fallback\nTS=((child* OR adolescen* OR teen* OR teenager* OR youth OR preschool*) AND ((sleep NEAR/2 duration) OR (sleep NEAR/2 time) OR (sleep NEAR/2 quality) OR (\"short sleep\" NEAR/2 duration) OR (\"long sleep\" NEAR/2 duration) OR (sleep NEAR/2 disturbance) OR (sleep NEAR/2 restriction)) AND (\"c-reactive protein\" OR CRP OR \"interleukin 6\" OR \"IL-6\" OR adiponectin OR \"TNF alpha\" OR \"TNF-alpha\" OR \"tumor necrosis factor alpha\"))",
    "# Q6: Balanced + design_plus_scope\nTI=(\"sleep duration\" OR \"sleep time\" OR \"sleep quality\" OR \"short sleep duration\" OR \"long sleep duration\" OR \"poor sleep quality\" OR \"sleep disturbance\") AND TI=(\"c-reactive protein\" OR CRP OR \"interleukin 6\" OR \"IL-6\" OR adiponectin OR \"TNF alpha\" OR \"TNF-alpha\" OR inflammation) AND TS=(child* OR adolescen* OR teen* OR teenager* OR youth OR preschool*) AND TS=(observational OR cohort OR prospective OR \"cross-sectional\" OR \"case-control\" OR \"case control\") AND DT=(Article)"
  ],
  "embase": [
    "# Q1: High-recall\n(('child'/exp OR 'adolescent'/exp OR child*:ti,ab OR adolescen*:ti,ab OR teen*:ti,ab OR teenager*:ti,ab OR youth:ti,ab OR preschool*:ti,ab) AND ('sleep'/exp OR 'sleep deprivation'/exp OR 'sleep quality'/exp OR 'sleep duration':ti,ab OR 'sleep time':ti,ab OR 'sleep quality':ti,ab OR 'short sleep duration':ti,ab OR 'long sleep duration':ti,ab OR 'poor sleep quality':ti,ab OR 'sleep disturbance':ti,ab OR 'sleep disturbances':ti,ab OR 'sleep restriction':ti,ab) AND ('inflammation'/exp OR 'c reactive protein'/exp OR 'interleukin 6'/exp OR 'tumor necrosis factor alpha'/exp OR 'adiponectin'/exp OR inflammation:ti,ab OR 'inflammatory profile':ti,ab OR 'inflammatory biomarker':ti,ab OR 'inflammatory biomarkers':ti,ab OR 'c-reactive protein':ti,ab OR crp:ti,ab OR 'interleukin 6':ti,ab OR 'il-6':ti,ab OR adiponectin:ti,ab OR 'tnf alpha':ti,ab OR 'tnf-alpha':ti,ab OR 'tumor necrosis factor alpha':ti,ab))",
    "# Q2: Balanced\n(('child'/exp OR 'adolescent'/exp OR child*:ti,ab OR adolescen*:ti,ab OR teen*:ti,ab OR teenager*:ti,ab OR youth:ti,ab OR preschool*:ti,ab) AND ('sleep deprivation'/exp OR 'sleep quality'/exp OR 'sleep duration':ti,ab OR 'sleep time':ti,ab OR 'sleep quality':ti,ab OR 'short sleep duration':ti,ab OR 'long sleep duration':ti,ab OR 'poor sleep quality':ti,ab OR 'sleep disturbance':ti,ab OR 'sleep disturbances':ti,ab OR 'sleep restriction':ti,ab) AND ('c reactive protein'/exp OR 'interleukin 6'/exp OR 'tumor necrosis factor alpha'/exp OR 'adiponectin'/exp OR 'inflammatory biomarker':ti,ab OR 'inflammatory biomarkers':ti,ab OR 'c-reactive protein':ti,ab OR crp:ti,ab OR 'interleukin 6':ti,ab OR 'il-6':ti,ab OR adiponectin:ti,ab OR 'tnf alpha':ti,ab OR 'tnf-alpha':ti,ab OR 'tumor necrosis factor alpha':ti,ab))",
    "# Q3: High-precision\n((('sleep quality'/exp OR 'sleep deprivation'/exp OR 'sleep duration':ti,ab OR 'sleep time':ti,ab OR 'sleep quality':ti,ab OR 'short sleep duration':ti,ab OR 'long sleep duration':ti,ab OR 'poor sleep quality':ti,ab OR 'sleep disturbance':ti,ab) AND ('c reactive protein'/mj OR 'interleukin 6'/mj OR 'tumor necrosis factor alpha'/mj OR 'adiponectin'/mj OR 'c-reactive protein':ti,ab OR crp:ti,ab OR 'interleukin 6':ti,ab OR 'il-6':ti,ab OR adiponectin:ti,ab OR 'tnf alpha':ti,ab OR 'tnf-alpha':ti,ab OR 'tumor necrosis factor alpha':ti,ab) AND ('child'/exp OR 'adolescent'/exp OR child*:ti,ab OR adolescen*:ti,ab OR teen*:ti,ab OR teenager*:ti,ab OR youth:ti,ab OR preschool*:ti,ab) AND ('cohort analysis'/exp OR 'cross-sectional study'/exp OR 'case control study'/exp OR observational:ti,ab OR cohort:ti,ab OR prospective:ti,ab OR 'cross-sectional':ti,ab OR 'case-control':ti,ab OR 'case control':ti,ab)))",
    "# Q4: Balanced + scope_only\n(('sleep duration':ti OR 'sleep time':ti OR 'sleep quality':ti OR 'short sleep duration':ti OR 'long sleep duration':ti OR 'poor sleep quality':ti OR 'sleep disturbance':ti) AND ('c-reactive protein':ti OR crp:ti OR 'interleukin 6':ti OR 'il-6':ti OR adiponectin:ti OR 'tnf alpha':ti OR 'tnf-alpha':ti OR inflammation:ti) AND (child*:ti,ab OR adolescen*:ti,ab OR teen*:ti,ab OR teenager*:ti,ab OR youth:ti,ab OR preschool*:ti,ab))",
    "# Q5: Balanced + proximity_or_scope_fallback\n((('child'/exp OR 'adolescent'/exp OR child*:ti,ab OR adolescen*:ti,ab OR teen*:ti,ab OR teenager*:ti,ab OR youth:ti,ab OR preschool*:ti,ab) AND (((sleep ADJ2 duration):ti,ab OR (sleep ADJ2 time):ti,ab OR (sleep ADJ2 quality):ti,ab OR (('short sleep' ADJ2 duration):ti,ab) OR (('long sleep' ADJ2 duration):ti,ab) OR (sleep ADJ2 disturbance):ti,ab OR (sleep ADJ2 restriction):ti,ab)) AND ('c-reactive protein':ti,ab OR crp:ti,ab OR 'interleukin 6':ti,ab OR 'il-6':ti,ab OR adiponectin:ti,ab OR 'tnf alpha':ti,ab OR 'tnf-alpha':ti,ab OR 'tumor necrosis factor alpha':ti,ab)))",
    "# Q6: Balanced + design_plus_scope\n(('sleep duration':ti OR 'sleep time':ti OR 'sleep quality':ti OR 'short sleep duration':ti OR 'long sleep duration':ti OR 'poor sleep quality':ti OR 'sleep disturbance':ti) AND ('c-reactive protein':ti OR crp:ti OR 'interleukin 6':ti OR 'il-6':ti OR adiponectin:ti OR 'tnf alpha':ti OR 'tnf-alpha':ti OR inflammation:ti) AND (child*:ti,ab OR adolescen*:ti,ab OR teen*:ti,ab OR teenager*:ti,ab OR youth:ti,ab OR preschool*:ti,ab) AND (observational:ti,ab OR cohort:ti,ab OR prospective:ti,ab OR 'cross-sectional':ti,ab OR 'case-control':ti,ab OR 'case control':ti,ab))"
  ]
}
```

## PRESS Self-Check

```json
{
  "json_patch": {}
}
```

## Translation Notes

- Q1 and Q2 preserve the same three mandatory-core blocks across all databases: pediatric population, sleep duration or quality exposure, and inflammatory biomarker outcomes.
- The protocol comparator of adequate sleep time is treated as `screening_only` because using it in retrieval would risk suppressing relevant observational studies that do not foreground the comparator in titles, abstracts, or indexing.
- The protocol language restriction to English, Spanish, and Portuguese is retained as an interface-applied limit rather than embedded inline in all database strings.
- The bundled variants use only approved cases: `scope_only`, `proximity_or_scope_fallback`, and `design_plus_scope`.
- PubMed uses a scope fallback rather than true proximity for Q5 because proximity operators are unavailable.
- The protocol names PubMed, Web of Science, and Scopus, but the repository workflow expects the standard four output files, so an Embase translation is included to match the project convention.
