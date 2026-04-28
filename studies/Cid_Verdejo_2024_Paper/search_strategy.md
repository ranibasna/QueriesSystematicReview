# Search Strategy for Cid_Verdejo_2024_Paper

## Study Summary

- Topic: Instrumental assessment validity for sleep bruxism, comparing portable electromyography devices against polysomnography
- Date window: No inline publication-date restriction; the protocol allows all publication years
- Databases: pubmed, scopus, wos, embase
- Query level: extended
- Retrieval architecture: single_route
- design_analytic_block: active, but populated conservatively and reserved for the final bundled precision variant

## PICOS Summary

- Population: Patients with sleep bruxism and related rhythmic oromotor activity constructs including RMMA, MMA, and OMA
- Intervention or Exposure: Instrumental assessment using portable electromyography devices
- Comparator: Polysomnography as the reference standard
- Outcomes: Diagnostic yield and validity measures for sleep bruxism assessment, including sensitivity, specificity, agreement, and related diagnostic metrics
- Design: Observational and nonrandomized studies

## Architecture Selection Summary

- Selected retrieval architecture: `single_route`
- `design_analytic_block`: active

### Concept Roles

| Role | Assigned concepts |
| --- | --- |
| mandatory_core | sleep bruxism and closely related oromotor activity terms; portable electromyography assessment terms; polysomnography reference-standard terms |
| optional_precision | diagnostic validity and diagnostic-yield wording; method-comparison and agreement wording; tighter title-only or proximity-based scope |
| filter_only | publication-type and human-study limits, if applied later in database interfaces; low-risk document-type narrowing |
| screening_only | full-night PSG requirement, duplicated samples, sex restrictions, language restrictions, and other eligibility details handled during screening |

The protocol supports one coherent Boolean route rather than two protocol-justified parallel routes, so `single_route` is the safer fit. The comparator is not merely an eligibility detail here: polysomnography is part of the substantive review target, so the reference-standard block remains mandatory in Q1 and Q2. The active `design_analytic_block` is populated conservatively from the explicit observational and nonrandomized study-design constraint, and it is delayed to a bundled precision variant rather than baseline retrieval.

## Concept Tables

### Concept to MeSH or Emtree

| concept | term | tree note | explode? | rationale and source |
| --- | --- | --- | --- | --- |
| Sleep bruxism core | Bruxism / bruxism | indexed representation for the core condition | Yes | Protocol title, condition description, and Medical Subject Headings listing |
| EMG assessment core | Electromyography / electromyography | indexed representation for the portable EMG assessment method | Yes | Protocol intervention and keyword list |
| PSG reference core | Polysomnography / polysomnography | indexed representation for the reference-standard sleep study | Yes | Protocol comparator and keyword list |
| Diagnostic precision | Sensitivity and Specificity / diagnostic accuracy wording translated in text | optional precision support for validity-focused variants | Mixed | Protocol outcomes include diagnostic yield, sensitivity, specificity, kappa, and ICC |

### Concept to Textword

| concept | synonym or phrase | field | truncation? | source |
| --- | --- | --- | --- | --- |
| Sleep bruxism core | sleep bruxism | title/abstract/topic | No | Protocol title and objectives |
| Sleep bruxism core | sleep-related bruxism; sleep related bruxism | title/abstract/topic | No | Protocol-compatible phrasing |
| Sleep bruxism core | bruxism | title/abstract/topic | No | Core disorder wording in protocol context |
| Sleep bruxism core | rhythmic masticatory muscle activity; RMMA | title/abstract/topic | Mixed | Explicit protocol population wording |
| Sleep bruxism core | masticatory muscle activity; MMA | title/abstract/topic | Mixed | Explicit protocol population wording |
| Sleep bruxism core | oromotor activity; oral motor activity; OMA | title/abstract/topic | Mixed | Explicit protocol population wording |
| Sleep bruxism core | sleep-related oromotor activity; sleep related oromotor activity | title/abstract/topic | No | Explicit protocol objective wording |
| EMG assessment core | electromyograph*; EMG | title/abstract/topic | Yes | Protocol intervention and keyword list |
| EMG assessment core | portable electromyograph*; portable EMG | title/abstract/topic | Yes | Protocol objective and keywords |
| EMG assessment core | ambulatory electromyograph* | title/abstract/topic | Yes | Protocol-compatible portable-device wording |
| EMG assessment core | portable device; portable devices | title/abstract/topic | No | Explicit protocol keyword list |
| PSG reference core | polysomnograph*; PSG | title/abstract/topic | Yes | Protocol comparator and keyword list |
| PSG reference core | audio-video; audio video | title/abstract/topic | No | Protocol context describing definitive PSG diagnosis |
| Diagnostic precision | diagnos*; valid*; accuracy | title/abstract/topic | Mixed | Protocol objective and outcomes |
| Diagnostic precision | diagnostic yield; sensitivity; specificity | title/abstract/topic | Mixed | Explicit protocol outcome wording |
| Diagnostic precision | compar*; agreement; reference standard; gold standard | title/abstract/topic | Mixed | Protocol comparison framing |
| Diagnostic precision | intraclass correlation; kappa | title/abstract/topic | No | Explicit protocol measures of effect |
| Design block | observational; nonrandomized; non-randomized | title/abstract/topic | No | Explicit protocol study-design restriction |

## JSON Query Object

```json
{
  "pubmed": [
    "# Q1: High-recall\n((\"Bruxism\"[Mesh] OR \"sleep bruxism\"[tiab] OR \"sleep-related bruxism\"[tiab] OR \"sleep related bruxism\"[tiab] OR bruxism[tiab] OR \"rhythmic masticatory muscle activity\"[tiab] OR RMMA[tiab] OR \"masticatory muscle activity\"[tiab] OR MMA[tiab] OR \"oromotor activity\"[tiab] OR \"oral motor activity\"[tiab] OR OMA[tiab] OR \"sleep-related oromotor activity\"[tiab] OR \"sleep related oromotor activity\"[tiab]) AND (\"Electromyography\"[Mesh] OR electromyograph*[tiab] OR EMG[tiab] OR \"portable electromyography\"[tiab] OR \"portable electromyographic\"[tiab] OR \"portable EMG\"[tiab] OR \"ambulatory electromyography\"[tiab] OR \"ambulatory electromyographic\"[tiab] OR \"portable device\"[tiab] OR \"portable devices\"[tiab]) AND (\"Polysomnography\"[Mesh] OR polysomnograph*[tiab] OR PSG[tiab] OR \"audio-video\"[tiab] OR \"audio video\"[tiab]))",
    "# Q2: Balanced\n((\"Bruxism\"[Mesh] OR \"sleep bruxism\"[tiab] OR \"sleep-related bruxism\"[tiab] OR \"sleep related bruxism\"[tiab] OR bruxism[tiab] OR \"rhythmic masticatory muscle activity\"[tiab] OR RMMA[tiab] OR \"masticatory muscle activity\"[tiab] OR MMA[tiab] OR \"oromotor activity\"[tiab] OR \"oral motor activity\"[tiab] OR OMA[tiab] OR \"sleep-related oromotor activity\"[tiab] OR \"sleep related oromotor activity\"[tiab]) AND (\"Electromyography\"[Mesh] OR electromyograph*[tiab] OR EMG[tiab] OR \"portable electromyography\"[tiab] OR \"portable electromyographic\"[tiab] OR \"portable EMG\"[tiab] OR \"ambulatory electromyography\"[tiab] OR \"ambulatory electromyographic\"[tiab] OR \"portable device\"[tiab] OR \"portable devices\"[tiab]) AND (\"Polysomnography\"[Mesh] OR polysomnograph*[tiab] OR PSG[tiab]) AND (\"Sensitivity and Specificity\"[Mesh] OR diagnos*[tiab] OR valid*[tiab] OR accuracy[tiab] OR \"diagnostic yield\"[tiab] OR sensitivity[tiab] OR specificity[tiab] OR compar*[tiab] OR agreement[tiab] OR \"reference standard\"[tiab] OR \"gold standard\"[tiab] OR \"intraclass correlation\"[tiab] OR kappa[tiab]))",
    "# Q3: High-precision\n((\"sleep bruxism\"[ti] OR \"sleep-related bruxism\"[ti] OR \"sleep related bruxism\"[ti] OR \"rhythmic masticatory muscle activity\"[ti] OR RMMA[ti] OR \"masticatory muscle activity\"[ti] OR MMA[ti] OR \"sleep-related oromotor activity\"[ti] OR \"sleep related oromotor activity\"[ti]) AND (electromyograph*[tiab] OR EMG[tiab] OR \"portable electromyography\"[tiab] OR \"portable electromyographic\"[tiab] OR \"portable EMG\"[tiab] OR \"portable device\"[tiab] OR \"portable devices\"[tiab]) AND (\"Polysomnography\"[Mesh] OR polysomnograph*[tiab] OR PSG[tiab]) AND (diagnos*[tiab] OR valid*[tiab] OR accuracy[tiab] OR \"diagnostic yield\"[tiab] OR sensitivity[tiab] OR specificity[tiab] OR compar*[tiab] OR agreement[tiab] OR \"reference standard\"[tiab] OR \"gold standard\"[tiab]))",
    "# Q4: Balanced + scope_only\n((\"sleep bruxism\"[ti] OR \"sleep-related bruxism\"[ti] OR \"sleep related bruxism\"[ti] OR \"rhythmic masticatory muscle activity\"[ti] OR RMMA[ti] OR \"sleep-related oromotor activity\"[ti] OR \"sleep related oromotor activity\"[ti]) AND (electromyograph*[tiab] OR EMG[tiab] OR \"portable electromyography\"[tiab] OR \"portable electromyographic\"[tiab] OR \"portable EMG\"[tiab] OR \"portable device\"[tiab] OR \"portable devices\"[tiab]) AND (polysomnograph*[tiab] OR PSG[tiab]) AND (diagnos*[tiab] OR valid*[tiab] OR accuracy[tiab] OR \"diagnostic yield\"[tiab] OR sensitivity[tiab] OR specificity[tiab] OR compar*[tiab] OR agreement[tiab]))",
    "# Q5: Balanced + proximity_or_scope_fallback\n((\"sleep bruxism\"[ti] OR \"sleep-related bruxism\"[ti] OR \"sleep related bruxism\"[ti] OR \"rhythmic masticatory muscle activity\"[ti] OR RMMA[ti] OR \"sleep-related oromotor activity\"[ti] OR \"sleep related oromotor activity\"[ti]) AND (electromyograph*[ti] OR \"portable electromyography\"[ti] OR \"portable electromyographic\"[ti] OR \"portable EMG\"[ti] OR \"portable device\"[ti] OR \"portable devices\"[ti]) AND (polysomnograph*[ti] OR PSG[ti]) AND (diagnos*[tiab] OR valid*[tiab] OR \"diagnostic yield\"[tiab] OR sensitivity[tiab] OR specificity[tiab] OR agreement[tiab] OR \"reference standard\"[tiab] OR \"gold standard\"[tiab]))",
    "# Q6: Balanced + design_plus_scope\n((\"sleep bruxism\"[ti] OR \"sleep-related bruxism\"[ti] OR \"sleep related bruxism\"[ti] OR \"rhythmic masticatory muscle activity\"[tiab] OR RMMA[tiab] OR \"sleep-related oromotor activity\"[tiab] OR \"sleep related oromotor activity\"[tiab]) AND (electromyograph*[tiab] OR EMG[tiab] OR \"portable electromyography\"[tiab] OR \"portable electromyographic\"[tiab] OR \"portable EMG\"[tiab] OR \"portable device\"[tiab] OR \"portable devices\"[tiab]) AND (polysomnograph*[tiab] OR PSG[tiab]) AND (diagnos*[tiab] OR valid*[tiab] OR accuracy[tiab] OR \"diagnostic yield\"[tiab] OR sensitivity[tiab] OR specificity[tiab] OR compar*[tiab] OR agreement[tiab] OR \"reference standard\"[tiab] OR \"gold standard\"[tiab]) AND (observational[tiab] OR nonrandomized[tiab] OR non-randomized[tiab]))"
  ],
  "scopus": [
    "# Q1: High-recall\nTITLE-ABS-KEY(((\"sleep bruxism\" OR \"sleep-related bruxism\" OR \"sleep related bruxism\" OR bruxism OR \"rhythmic masticatory muscle activity\" OR RMMA OR \"masticatory muscle activity\" OR MMA OR \"oromotor activity\" OR \"oral motor activity\" OR OMA OR \"sleep-related oromotor activity\" OR \"sleep related oromotor activity\") AND (electromyograph* OR EMG OR \"portable electromyography\" OR \"portable electromyographic\" OR \"portable EMG\" OR \"ambulatory electromyography\" OR \"ambulatory electromyographic\" OR \"portable device\" OR \"portable devices\") AND (polysomnograph* OR PSG OR \"audio-video\" OR \"audio video\")))",
    "# Q2: Balanced\nTITLE-ABS-KEY(((\"sleep bruxism\" OR \"sleep-related bruxism\" OR \"sleep related bruxism\" OR bruxism OR \"rhythmic masticatory muscle activity\" OR RMMA OR \"masticatory muscle activity\" OR MMA OR \"oromotor activity\" OR \"oral motor activity\" OR OMA OR \"sleep-related oromotor activity\" OR \"sleep related oromotor activity\") AND (electromyograph* OR EMG OR \"portable electromyography\" OR \"portable electromyographic\" OR \"portable EMG\" OR \"ambulatory electromyography\" OR \"ambulatory electromyographic\" OR \"portable device\" OR \"portable devices\") AND (polysomnograph* OR PSG) AND (diagnos* OR valid* OR accuracy OR \"diagnostic yield\" OR sensitivity OR specificity OR compar* OR agreement OR \"reference standard\" OR \"gold standard\" OR \"intraclass correlation\" OR kappa)))",
    "# Q3: High-precision\nTITLE(\"sleep bruxism\" OR \"sleep-related bruxism\" OR \"sleep related bruxism\" OR \"rhythmic masticatory muscle activity\" OR RMMA OR \"sleep-related oromotor activity\" OR \"sleep related oromotor activity\") AND TITLE-ABS-KEY(electromyograph* OR EMG OR \"portable electromyography\" OR \"portable electromyographic\" OR \"portable EMG\" OR \"portable device\" OR \"portable devices\") AND TITLE-ABS-KEY(polysomnograph* OR PSG) AND TITLE-ABS-KEY(diagnos* OR valid* OR accuracy OR \"diagnostic yield\" OR sensitivity OR specificity OR compar* OR agreement OR \"reference standard\" OR \"gold standard\")",
    "# Q4: Balanced + scope_only\nTITLE(\"sleep bruxism\" OR \"sleep-related bruxism\" OR \"sleep related bruxism\" OR \"rhythmic masticatory muscle activity\" OR RMMA OR \"sleep-related oromotor activity\" OR \"sleep related oromotor activity\") AND TITLE(electromyograph* OR \"portable electromyography\" OR \"portable electromyographic\" OR \"portable EMG\") AND TITLE-ABS-KEY(polysomnograph* OR PSG) AND TITLE-ABS-KEY(diagnos* OR valid* OR accuracy OR \"diagnostic yield\" OR sensitivity OR specificity OR compar* OR agreement)",
    "# Q5: Balanced + proximity_or_scope_fallback\nTITLE-ABS-KEY((((\"sleep bruxism\" OR \"sleep-related bruxism\" OR \"sleep related bruxism\" OR \"rhythmic masticatory muscle activity\" OR RMMA OR \"sleep-related oromotor activity\" OR \"sleep related oromotor activity\") W/5 (electromyograph* OR \"portable electromyography\" OR \"portable electromyographic\" OR \"portable EMG\" OR \"portable device\" OR \"portable devices\")) AND (polysomnograph* OR PSG) AND (diagnos* OR valid* OR \"diagnostic yield\" OR sensitivity OR specificity OR agreement OR \"reference standard\" OR \"gold standard\")))",
    "# Q6: Balanced + design_plus_scope\nTITLE(\"sleep bruxism\" OR \"sleep-related bruxism\" OR \"sleep related bruxism\") AND TITLE-ABS-KEY(electromyograph* OR EMG OR \"portable electromyography\" OR \"portable electromyographic\" OR \"portable EMG\" OR \"portable device\" OR \"portable devices\") AND TITLE-ABS-KEY(polysomnograph* OR PSG) AND TITLE-ABS-KEY(diagnos* OR valid* OR accuracy OR \"diagnostic yield\" OR sensitivity OR specificity OR compar* OR agreement OR \"reference standard\" OR \"gold standard\") AND TITLE-ABS-KEY(observational OR nonrandomized OR non-randomized)"
  ],
  "wos": [
    "# Q1: High-recall\nTS=(((\"sleep bruxism\" OR \"sleep-related bruxism\" OR \"sleep related bruxism\" OR bruxism OR \"rhythmic masticatory muscle activity\" OR RMMA OR \"masticatory muscle activity\" OR MMA OR \"oromotor activity\" OR \"oral motor activity\" OR OMA OR \"sleep-related oromotor activity\" OR \"sleep related oromotor activity\") AND (electromyograph* OR EMG OR \"portable electromyography\" OR \"portable electromyographic\" OR \"portable EMG\" OR \"ambulatory electromyography\" OR \"ambulatory electromyographic\" OR \"portable device\" OR \"portable devices\") AND (polysomnograph* OR PSG OR \"audio-video\" OR \"audio video\")))",
    "# Q2: Balanced\nTS=(((\"sleep bruxism\" OR \"sleep-related bruxism\" OR \"sleep related bruxism\" OR bruxism OR \"rhythmic masticatory muscle activity\" OR RMMA OR \"masticatory muscle activity\" OR MMA OR \"oromotor activity\" OR \"oral motor activity\" OR OMA OR \"sleep-related oromotor activity\" OR \"sleep related oromotor activity\") AND (electromyograph* OR EMG OR \"portable electromyography\" OR \"portable electromyographic\" OR \"portable EMG\" OR \"ambulatory electromyography\" OR \"ambulatory electromyographic\" OR \"portable device\" OR \"portable devices\") AND (polysomnograph* OR PSG) AND (diagnos* OR valid* OR accuracy OR \"diagnostic yield\" OR sensitivity OR specificity OR compar* OR agreement OR \"reference standard\" OR \"gold standard\" OR \"intraclass correlation\" OR kappa)))",
    "# Q3: High-precision\nTI=(\"sleep bruxism\" OR \"sleep-related bruxism\" OR \"sleep related bruxism\" OR \"rhythmic masticatory muscle activity\" OR RMMA OR \"sleep-related oromotor activity\" OR \"sleep related oromotor activity\") AND TS=(electromyograph* OR EMG OR \"portable electromyography\" OR \"portable electromyographic\" OR \"portable EMG\" OR \"portable device\" OR \"portable devices\") AND TS=(polysomnograph* OR PSG) AND TS=(diagnos* OR valid* OR accuracy OR \"diagnostic yield\" OR sensitivity OR specificity OR compar* OR agreement OR \"reference standard\" OR \"gold standard\")",
    "# Q4: Balanced + scope_only\nTI=(\"sleep bruxism\" OR \"sleep-related bruxism\" OR \"sleep related bruxism\" OR \"rhythmic masticatory muscle activity\" OR RMMA OR \"sleep-related oromotor activity\" OR \"sleep related oromotor activity\") AND TI=(electromyograph* OR \"portable electromyography\" OR \"portable electromyographic\" OR \"portable EMG\") AND TS=(polysomnograph* OR PSG) AND TS=(diagnos* OR valid* OR accuracy OR \"diagnostic yield\" OR sensitivity OR specificity OR compar* OR agreement)",
    "# Q5: Balanced + proximity_or_scope_fallback\nTS=((((\"sleep bruxism\" OR \"sleep-related bruxism\" OR \"sleep related bruxism\" OR \"rhythmic masticatory muscle activity\" OR RMMA OR \"sleep-related oromotor activity\" OR \"sleep related oromotor activity\") NEAR/5 (electromyograph* OR \"portable electromyography\" OR \"portable electromyographic\" OR \"portable EMG\" OR \"portable device\" OR \"portable devices\")) AND (polysomnograph* OR PSG) AND (diagnos* OR valid* OR \"diagnostic yield\" OR sensitivity OR specificity OR agreement OR \"reference standard\" OR \"gold standard\")))",
    "# Q6: Balanced + design_plus_scope\nTI=(\"sleep bruxism\" OR \"sleep-related bruxism\" OR \"sleep related bruxism\") AND TS=(electromyograph* OR EMG OR \"portable electromyography\" OR \"portable electromyographic\" OR \"portable EMG\" OR \"portable device\" OR \"portable devices\") AND TS=(polysomnograph* OR PSG) AND TS=(diagnos* OR valid* OR accuracy OR \"diagnostic yield\" OR sensitivity OR specificity OR compar* OR agreement OR \"reference standard\" OR \"gold standard\") AND TS=(observational OR nonrandomized OR non-randomized)"
  ],
  "embase": [
    "# Q1: High-recall\n(('bruxism'/exp OR 'sleep bruxism':ti,ab OR 'sleep-related bruxism':ti,ab OR 'sleep related bruxism':ti,ab OR bruxism:ti,ab OR 'rhythmic masticatory muscle activity':ti,ab OR RMMA:ti,ab OR 'masticatory muscle activity':ti,ab OR MMA:ti,ab OR 'oromotor activity':ti,ab OR 'oral motor activity':ti,ab OR OMA:ti,ab OR 'sleep-related oromotor activity':ti,ab OR 'sleep related oromotor activity':ti,ab) AND ('electromyography'/exp OR electromyograph*:ti,ab OR EMG:ti,ab OR 'portable electromyography':ti,ab OR 'portable electromyographic':ti,ab OR 'portable EMG':ti,ab OR 'ambulatory electromyography':ti,ab OR 'ambulatory electromyographic':ti,ab OR 'portable device':ti,ab OR 'portable devices':ti,ab) AND ('polysomnography'/exp OR polysomnograph*:ti,ab OR PSG:ti,ab OR 'audio-video':ti,ab OR 'audio video':ti,ab))",
    "# Q2: Balanced\n(('bruxism'/exp OR 'sleep bruxism':ti,ab OR 'sleep-related bruxism':ti,ab OR 'sleep related bruxism':ti,ab OR bruxism:ti,ab OR 'rhythmic masticatory muscle activity':ti,ab OR RMMA:ti,ab OR 'masticatory muscle activity':ti,ab OR MMA:ti,ab OR 'oromotor activity':ti,ab OR 'oral motor activity':ti,ab OR OMA:ti,ab OR 'sleep-related oromotor activity':ti,ab OR 'sleep related oromotor activity':ti,ab) AND ('electromyography'/exp OR electromyograph*:ti,ab OR EMG:ti,ab OR 'portable electromyography':ti,ab OR 'portable electromyographic':ti,ab OR 'portable EMG':ti,ab OR 'ambulatory electromyography':ti,ab OR 'ambulatory electromyographic':ti,ab OR 'portable device':ti,ab OR 'portable devices':ti,ab) AND ('polysomnography'/exp OR polysomnograph*:ti,ab OR PSG:ti,ab) AND (diagnos*:ti,ab OR valid*:ti,ab OR accuracy:ti,ab OR 'diagnostic yield':ti,ab OR sensitivity:ti,ab OR specificity:ti,ab OR compar*:ti,ab OR agreement:ti,ab OR 'reference standard':ti,ab OR 'gold standard':ti,ab OR 'intraclass correlation':ti,ab OR kappa:ti,ab))",
    "# Q3: High-precision\n(('sleep bruxism':ti OR 'sleep-related bruxism':ti OR 'sleep related bruxism':ti OR 'rhythmic masticatory muscle activity':ti OR RMMA:ti OR 'sleep-related oromotor activity':ti OR 'sleep related oromotor activity':ti) AND (electromyograph*:ti,ab OR EMG:ti,ab OR 'portable electromyography':ti,ab OR 'portable electromyographic':ti,ab OR 'portable EMG':ti,ab OR 'portable device':ti,ab OR 'portable devices':ti,ab) AND ('polysomnography'/exp OR polysomnograph*:ti,ab OR PSG:ti,ab) AND (diagnos*:ti,ab OR valid*:ti,ab OR accuracy:ti,ab OR 'diagnostic yield':ti,ab OR sensitivity:ti,ab OR specificity:ti,ab OR compar*:ti,ab OR agreement:ti,ab OR 'reference standard':ti,ab OR 'gold standard':ti,ab))",
    "# Q4: Balanced + scope_only\n(('sleep bruxism':ti OR 'sleep-related bruxism':ti OR 'sleep related bruxism':ti OR 'rhythmic masticatory muscle activity':ti OR RMMA:ti OR 'sleep-related oromotor activity':ti OR 'sleep related oromotor activity':ti) AND (electromyograph*:ti OR 'portable electromyography':ti OR 'portable electromyographic':ti OR 'portable EMG':ti) AND (polysomnograph*:ti,ab OR PSG:ti,ab) AND (diagnos*:ti,ab OR valid*:ti,ab OR accuracy:ti,ab OR 'diagnostic yield':ti,ab OR sensitivity:ti,ab OR specificity:ti,ab OR compar*:ti,ab OR agreement:ti,ab))",
    "# Q5: Balanced + proximity_or_scope_fallback\n(((('sleep bruxism' OR 'sleep-related bruxism' OR 'sleep related bruxism' OR 'rhythmic masticatory muscle activity' OR RMMA OR 'sleep-related oromotor activity' OR 'sleep related oromotor activity') ADJ5 (electromyograph* OR 'portable electromyography' OR 'portable electromyographic' OR 'portable EMG' OR 'portable device' OR 'portable devices')):ti,ab AND (polysomnograph*:ti,ab OR PSG:ti,ab) AND (diagnos*:ti,ab OR valid*:ti,ab OR 'diagnostic yield':ti,ab OR sensitivity:ti,ab OR specificity:ti,ab OR agreement:ti,ab OR 'reference standard':ti,ab OR 'gold standard':ti,ab)))",
    "# Q6: Balanced + design_plus_scope\n(('sleep bruxism':ti OR 'sleep-related bruxism':ti OR 'sleep related bruxism':ti) AND (electromyograph*:ti,ab OR EMG:ti,ab OR 'portable electromyography':ti,ab OR 'portable electromyographic':ti,ab OR 'portable EMG':ti,ab OR 'portable device':ti,ab OR 'portable devices':ti,ab) AND (polysomnograph*:ti,ab OR PSG:ti,ab) AND (diagnos*:ti,ab OR valid*:ti,ab OR accuracy:ti,ab OR 'diagnostic yield':ti,ab OR sensitivity:ti,ab OR specificity:ti,ab OR compar*:ti,ab OR agreement:ti,ab OR 'reference standard':ti,ab OR 'gold standard':ti,ab) AND (observational:ti,ab OR nonrandomized:ti,ab OR 'non-randomized':ti,ab))"
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

- Q1 and Q2 preserve the same mandatory-core structure across databases: a sleep-bruxism block AND a portable-EMG block AND a polysomnography block.
- The diagnostic-validity block is held out of Q1 and added in Q2 because the protocol makes validity the outcome of interest, but many relevant validation studies may foreground the methods more clearly than the metric labels in titles and abstracts.
- The bundled variants use only approved cases: `scope_only`, `proximity_or_scope_fallback`, and `design_plus_scope`.
- Publication-year and language filters were omitted because the protocol allows all years and all languages.
- Comparator language remains in baseline retrieval because polysomnography is part of the substantive review target, not merely a screening criterion.
- Embase is translated in Embase.com syntax to match the strategy-aware database guidance file used by this skill.