# Search Strategy for Godos_2024

## Study Summary

- Topic: Association between Mediterranean diet exposure or Mediterranean-diet component intake and sleep features in adults
- Date window: No inline publication-date restriction; the protocol specifies searching from database inception
- Databases: pubmed, scopus, wos, embase
- Query level: extended

## PICOS Summary

- Population: Adults aged 18 years or older
- Intervention or Exposure: Adherence to the Mediterranean diet and intake of Mediterranean-diet components including fruit, vegetables, cereals, legumes, dairy products, fish, meat, olive oil, and alcohol
- Comparator: Different levels of Mediterranean-diet adherence or different categories of component intake
- Outcomes: Sleep features including sleep quality, sleep duration, and daytime sleepiness
- Design: Observational studies with a comparison group, including cohort, cross-sectional, and case-control studies

## Architecture Selection Summary

- Selected retrieval architecture: `single_route`
- `design_analytic_block`: active
- Rationale: The protocol describes one coherent keyword strategy combining Mediterranean-diet exposure or named components with sleep outcomes. It does not justify separate indexed and textword routes, so `dual_route_union` is not warranted.

### Concept Roles

| Role | Assigned concepts |
| --- | --- |
| mandatory_core | Mediterranean-diet exposure or named component intake; sleep features |
| optional_precision | Mediterranean-diet adherence wording; specific sleep-feature labels; title-only scope; proximity tightening where supported |
| filter_only | adult population restriction; humans or article-type limits; observational-study labels |
| screening_only | comparator strata; exclusions for children, pregnancy, and end-stage degenerative diseases |

## Concept Tables

### Concept to MeSH or Emtree

| concept | term | tree note | explode? | rationale and source |
| --- | --- | --- | --- | --- |
| Mediterranean-diet exposure | Diet, Mediterranean / mediterranean diet | Core indexed representation of the named exposure | Yes | Explicit protocol exposure |
| sleep features | Sleep / sleep | Broad indexed representation of the named outcome domain | Yes | Explicit protocol outcome domain |
| sleep features | Somnolence / somnolence | Indexed representation of daytime sleepiness | Yes | Explicit protocol example outcome |
| adult population | Adult / adult | Indexed age-group restriction kept out of baseline retrieval and used as a low-risk filter layer | Yes | Explicit protocol population restriction |

### Concept to Textword

| concept | synonym or phrase | field | truncation? | source |
| --- | --- | --- | --- | --- |
| Mediterranean-diet exposure | mediterranean diet | title/abstract/topic | No | Explicit protocol wording |
| Mediterranean-diet exposure | mediterranean diet adherence | title/abstract/topic | No | Explicit protocol wording |
| Mediterranean-diet exposure | fruit*; vegetable*; cereal*; legume*; dairy product; dairy products; fish; meat; olive oil; alcohol | title/abstract/topic | Mixed | Explicit protocol component list |
| Mediterranean-diet exposure | diet*; intake; consumption | title/abstract/topic | Mixed | Explicit protocol wording about adherence and intake |
| sleep features | sleep | title/abstract/topic | No | Explicit protocol domain |
| sleep features | sleep quality | title/abstract/topic | No | Explicit protocol example outcome |
| sleep features | sleep duration | title/abstract/topic | No | Explicit protocol example outcome |
| sleep features | daytime sleepiness | title/abstract/topic | No | Explicit protocol example outcome |
| sleep features | sleepiness; somnolence | title/abstract/topic | No | Protocol-compatible wording for daytime sleepiness |
| adult population | adult* | title/abstract/topic | Yes | Explicit protocol population restriction |
| observational design | cohort; observational; cross-sectional; case-control | title/abstract/topic | No | Explicit protocol study-design restriction |

## JSON Query Object

```json
{
  "pubmed": [
    "# Q1: High-recall\n((\"Diet, Mediterranean\"[Mesh] OR \"mediterranean diet\"[tiab] OR \"mediterranean diet adherence\"[tiab] OR ((fruit*[tiab] OR vegetable*[tiab] OR cereal*[tiab] OR legume*[tiab] OR \"dairy product\"[tiab] OR \"dairy products\"[tiab] OR fish[tiab] OR meat[tiab] OR \"olive oil\"[tiab] OR alcohol[tiab]) AND (diet*[tiab] OR intake[tiab] OR consumption[tiab]))) AND (\"Sleep\"[Mesh] OR \"Somnolence\"[Mesh] OR sleep[tiab] OR \"sleep quality\"[tiab] OR \"sleep duration\"[tiab] OR \"daytime sleepiness\"[tiab] OR sleepiness[tiab] OR somnolence[tiab]))",
    "# Q2: Balanced\n((\"Diet, Mediterranean\"[Mesh] OR \"mediterranean diet\"[tiab] OR \"mediterranean diet adherence\"[tiab] OR ((legume*[tiab] OR fish[tiab] OR \"olive oil\"[tiab] OR alcohol[tiab]) AND (diet*[tiab] OR intake[tiab] OR consumption[tiab]))) AND (\"Sleep\"[Mesh] OR sleep[tiab] OR \"sleep quality\"[tiab] OR \"sleep duration\"[tiab] OR \"daytime sleepiness\"[tiab] OR sleepiness[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab]))",
    "# Q3: High-precision\n(((\"Diet, Mediterranean\"[Majr] OR \"mediterranean diet\"[ti] OR \"mediterranean diet adherence\"[ti]) AND (\"sleep quality\"[ti] OR \"sleep duration\"[ti] OR \"daytime sleepiness\"[ti] OR sleep[ti])) AND (\"Adult\"[Mesh] OR adult*[tiab]))",
    "# Q4: Balanced + scope_only\n((\"mediterranean diet\"[ti] OR \"mediterranean diet adherence\"[ti]) AND (\"sleep quality\"[ti] OR \"sleep duration\"[ti] OR \"daytime sleepiness\"[ti] OR sleep[ti]) AND (\"Adult\"[Mesh] OR adult*[tiab]))",
    "# Q5: Balanced + filter_only\n(((\"Diet, Mediterranean\"[Mesh] OR \"mediterranean diet\"[tiab] OR \"mediterranean diet adherence\"[tiab] OR ((legume*[tiab] OR fish[tiab] OR \"olive oil\"[tiab] OR alcohol[tiab]) AND (diet*[tiab] OR intake[tiab] OR consumption[tiab]))) AND (\"Sleep\"[Mesh] OR sleep[tiab] OR \"sleep quality\"[tiab] OR \"sleep duration\"[tiab] OR \"daytime sleepiness\"[tiab] OR sleepiness[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab])) AND humans[Filter]) NOT (review[pt] OR meta-analysis[pt] OR letter[pt] OR editorial[pt] OR comment[pt])",
    "# Q6: Balanced + design_plus_filter\n((((\"Diet, Mediterranean\"[Mesh] OR \"mediterranean diet\"[tiab] OR \"mediterranean diet adherence\"[tiab] OR ((legume*[tiab] OR fish[tiab] OR \"olive oil\"[tiab] OR alcohol[tiab]) AND (diet*[tiab] OR intake[tiab] OR consumption[tiab]))) AND (\"Sleep\"[Mesh] OR sleep[tiab] OR \"sleep quality\"[tiab] OR \"sleep duration\"[tiab] OR \"daytime sleepiness\"[tiab] OR sleepiness[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab])) AND (cohort[tiab] OR observational[tiab] OR \"cross-sectional\"[tiab] OR \"case-control\"[tiab])) AND humans[Filter]) NOT (review[pt] OR meta-analysis[pt] OR letter[pt] OR editorial[pt] OR comment[pt])"
  ],
  "scopus": [
    "# Q1: High-recall\nTITLE-ABS-KEY((\"mediterranean diet\" OR \"mediterranean diet adherence\" OR ((fruit* OR vegetable* OR cereal* OR legume* OR \"dairy product\" OR \"dairy products\" OR fish OR meat OR \"olive oil\" OR alcohol) AND (diet* OR intake OR consumption))) AND (sleep OR \"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR sleepiness OR somnolence))",
    "# Q2: Balanced\nTITLE-ABS-KEY((\"mediterranean diet\" OR \"mediterranean diet adherence\" OR ((legume* OR fish OR \"olive oil\" OR alcohol) AND (diet* OR intake OR consumption))) AND (sleep OR \"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR sleepiness) AND adult*)",
    "# Q3: High-precision\nTITLE(\"mediterranean diet\" OR \"mediterranean diet adherence\") AND TITLE-ABS-KEY(\"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR sleep) AND TITLE-ABS-KEY(adult*) AND DOCTYPE(ar)",
    "# Q4: Balanced + scope_only\nTITLE(\"mediterranean diet\" OR \"mediterranean diet adherence\") AND TITLE(\"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR sleep) AND TITLE-ABS-KEY(adult*)",
    "# Q5: Balanced + proximity_or_scope_fallback\nTITLE-ABS-KEY(((mediterranean W/2 diet) OR ((\"olive oil\" OR fish OR legume*) W/3 (diet* OR intake OR consumption))) AND ((sleep W/2 quality) OR (sleep W/2 duration) OR (daytime W/1 sleepiness) OR sleepiness OR somnolence OR sleep) AND adult*)",
    "# Q6: Balanced + design_plus_filter\nTITLE-ABS-KEY((\"mediterranean diet\" OR \"mediterranean diet adherence\" OR ((legume* OR fish OR \"olive oil\" OR alcohol) AND (diet* OR intake OR consumption))) AND (sleep OR \"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR sleepiness) AND adult* AND (cohort OR observational OR \"cross-sectional\" OR \"case-control\")) AND DOCTYPE(ar)"
  ],
  "wos": [
    "# Q1: High-recall\nTS=((\"mediterranean diet\" OR \"mediterranean diet adherence\" OR ((fruit* OR vegetable* OR cereal* OR legume* OR \"dairy product\" OR \"dairy products\" OR fish OR meat OR \"olive oil\" OR alcohol) AND (diet* OR intake OR consumption))) AND (sleep OR \"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR sleepiness OR somnolence))",
    "# Q2: Balanced\nTS=((\"mediterranean diet\" OR \"mediterranean diet adherence\" OR ((legume* OR fish OR \"olive oil\" OR alcohol) AND (diet* OR intake OR consumption))) AND (sleep OR \"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR sleepiness) AND adult*)",
    "# Q3: High-precision\nTI=(\"mediterranean diet\" OR \"mediterranean diet adherence\") AND TS=(\"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR sleep) AND TS=(adult*) AND DT=(Article)",
    "# Q4: Balanced + scope_only\nTI=(\"mediterranean diet\" OR \"mediterranean diet adherence\") AND TI=(\"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR sleep) AND TS=(adult*)",
    "# Q5: Balanced + proximity_or_scope_fallback\nTS=(((mediterranean NEAR/2 diet) OR ((\"olive oil\" OR fish OR legume*) NEAR/3 (diet* OR intake OR consumption))) AND ((sleep NEAR/2 quality) OR (sleep NEAR/2 duration) OR (daytime NEAR/1 sleepiness) OR sleepiness OR somnolence OR sleep) AND adult*)",
    "# Q6: Balanced + design_plus_filter\nTS=((\"mediterranean diet\" OR \"mediterranean diet adherence\" OR ((legume* OR fish OR \"olive oil\" OR alcohol) AND (diet* OR intake OR consumption))) AND (sleep OR \"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR sleepiness) AND adult* AND (cohort OR observational OR \"cross-sectional\" OR \"case-control\")) AND DT=(Article)"
  ],
  "embase": [
    "# Q1: High-recall\n(('mediterranean diet'/exp OR 'mediterranean diet':ti,ab OR 'mediterranean diet adherence':ti,ab OR ((fruit*:ti,ab OR vegetable*:ti,ab OR cereal*:ti,ab OR legume*:ti,ab OR 'dairy product':ti,ab OR 'dairy products':ti,ab OR fish:ti,ab OR meat:ti,ab OR 'olive oil':ti,ab OR alcohol:ti,ab) AND (diet*:ti,ab OR intake:ti,ab OR consumption:ti,ab))) AND ('sleep'/exp OR 'somnolence'/exp OR sleep:ti,ab OR 'sleep quality':ti,ab OR 'sleep duration':ti,ab OR 'daytime sleepiness':ti,ab OR sleepiness:ti,ab OR somnolence:ti,ab))",
    "# Q2: Balanced\n(('mediterranean diet'/exp OR 'mediterranean diet':ti,ab OR 'mediterranean diet adherence':ti,ab OR ((legume*:ti,ab OR fish:ti,ab OR 'olive oil':ti,ab OR alcohol:ti,ab) AND (diet*:ti,ab OR intake:ti,ab OR consumption:ti,ab))) AND ('sleep'/exp OR sleep:ti,ab OR 'sleep quality':ti,ab OR 'sleep duration':ti,ab OR 'daytime sleepiness':ti,ab OR sleepiness:ti,ab) AND ('adult'/exp OR adult*:ti,ab))",
    "# Q3: High-precision\n((('mediterranean diet'/mj OR 'mediterranean diet':ti OR 'mediterranean diet adherence':ti) AND ('sleep quality':ti OR 'sleep duration':ti OR 'daytime sleepiness':ti OR sleep:ti)) AND ('adult'/exp OR adult*:ti,ab))",
    "# Q4: Balanced + scope_only\n(('mediterranean diet':ti OR 'mediterranean diet adherence':ti) AND ('sleep quality':ti OR 'sleep duration':ti OR 'daytime sleepiness':ti OR sleep:ti) AND ('adult'/exp OR adult*:ti,ab))",
    "# Q5: Balanced + proximity_or_scope_fallback\n((((mediterranean ADJ2 diet):ti,ab OR (('olive oil' OR fish OR legume*) ADJ3 (diet* OR intake OR consumption)):ti,ab) AND ((sleep ADJ2 quality):ti,ab OR (sleep ADJ2 duration):ti,ab OR (daytime ADJ1 sleepiness):ti,ab OR sleepiness:ti,ab OR somnolence:ti,ab OR sleep:ti,ab) AND ('adult'/exp OR adult*:ti,ab))",
    "# Q6: Balanced + design_plus_filter\n((('mediterranean diet'/exp OR 'mediterranean diet':ti,ab OR 'mediterranean diet adherence':ti,ab OR ((legume*:ti,ab OR fish:ti,ab OR 'olive oil':ti,ab OR alcohol:ti,ab) AND (diet*:ti,ab OR intake:ti,ab OR consumption:ti,ab))) AND ('sleep'/exp OR sleep:ti,ab OR 'sleep quality':ti,ab OR 'sleep duration':ti,ab OR 'daytime sleepiness':ti,ab OR sleepiness:ti,ab) AND ('adult'/exp OR adult*:ti,ab) AND (cohort:ti,ab OR observational:ti,ab OR 'cross-sectional':ti,ab OR 'case-control':ti,ab)))"
  ]
}
```

## PRESS Self-Check

```json
{
  "json_patch": {}
}
```

- Q1 and Q2 preserve the same mandatory-core structure across databases: Mediterranean-diet exposure and sleep outcomes.
- Adult and observational-study constraints are explicit in the protocol but are safer as filter layers than as baseline Boolean concepts, so they were demoted out of Q1.
- Q4 to Q6 use only approved bundled cases, with proximity used only for databases that support it.
- Embase translation uses Embase.com / Elsevier syntax consistently.
- No inline publication-date restriction was added because the protocol specifies searching from inception.

## Translation Notes

- The protocol supports `single_route` because it defines one combined keyword strategy rather than separate indexed and textword routes.
- The `design_analytic_block` remains active by workflow rule, but its explicit candidate constraints were used conservatively as bundled precision layers.
- Scopus is included as a repo-standard translated output even though the protocol explicitly names PubMed, EMBASE, and Web of Science.
- Component terms remain linked to diet, intake, or consumption wording so the query does not drift into generic fruit-or-sleep retrieval.# Search Strategy for Godos_2024

## Study Summary

- Topic: Association between Mediterranean diet exposure, Mediterranean-style component intake, and sleep features in adults
- Date window: No inline publication-date restriction; the protocol states searching from database inception
- Databases: pubmed, scopus, wos, embase
- Query level: extended
- Retrieval architecture: single_route
- design_analytic_block: active, but populated conservatively and reserved for bundled precision variants

## PICOS Summary

- Population: Adults aged 18 years or older
- Intervention or Exposure: Adherence to the Mediterranean diet and intake of Mediterranean-diet components such as fruit, vegetables, cereals, legumes, dairy products, fish, meat, olive oil, and alcohol
- Comparator: Different levels of Mediterranean-diet adherence or different categories of component intake
- Outcomes: Sleep features, including sleep quality, sleep duration, daytime sleepiness, and related sleep outcomes
- Design: Observational studies with a comparison group, especially cohort, cross-sectional, and case-control studies

## Architecture Selection Summary

- Selected retrieval architecture: `single_route`
- `design_analytic_block`: active

### Concept Roles

| Role | Assigned concepts |
| --- | --- |
| mandatory_core | Mediterranean-diet exposure or Mediterranean-style component intake; sleep features; adult population |
| optional_precision | Mediterranean adherence or score wording; title-only focus; proximity tightening where supported; narrower sleep-feature labels |
| filter_only | human-only limits; document-type exclusions; observational-study labels used only in bundled variants |
| screening_only | comparator strata; exclusions for children, pregnancy, and end-stage degenerative disease |

## Concept Tables

### Concept to MeSH or Emtree

| concept | term | tree note | explode? | rationale and source |
| --- | --- | --- | --- | --- |
| Mediterranean-diet exposure | Diet, Mediterranean / mediterranean diet | core indexed representation for Mediterranean-diet adherence | Yes | Explicit protocol exposure |
| sleep features | Sleep / sleep | broad indexed representation for sleep outcomes | Yes | Protocol targets diverse sleep features |
| sleep features | Sleep Wake Disorders / sleep disorder | indexed representation for sleep disorders or disturbances | Yes | Protocol names diverse sleep features rather than one single sleep endpoint |
| sleep features | Somnolence / somnolence | indexed representation for daytime sleepiness | Yes | Explicit protocol example outcome |
| adult population | Adult / adult | indexed adult population limiter | Yes | Explicit protocol population restriction |

### Concept to Textword

| concept | synonym or phrase | field | truncation? | source |
| --- | --- | --- | --- | --- |
| Mediterranean-diet exposure | mediterranean diet | title/abstract/topic | No | Explicit protocol wording |
| Mediterranean-diet exposure | mediterranean dietary pattern | title/abstract/topic | No | Protocol-compatible phrasing |
| Mediterranean-diet exposure | mediterranean-style diet | title/abstract/topic | No | Protocol-compatible phrasing |
| Mediterranean-diet exposure | mediterranean diet adherence | title/abstract/topic | No | Explicit protocol framing |
| Mediterranean-diet exposure | mediterranean diet score | title/abstract/topic | No | Protocol-compatible adherence wording |
| Mediterranean-diet exposure | mediterranean dietary score | title/abstract/topic | No | Protocol-compatible adherence wording |
| Mediterranean-diet exposure | MedDiet | title/abstract/topic | No | Common shorthand for the named diet |
| Mediterranean-diet exposure | fruit*; vegetable*; cereal*; grain*; legume*; dairy; dairy product; dairy products; fish; meat; olive oil; alcohol; wine | title/abstract/topic | Mixed | Explicit component examples listed in the protocol |
| Mediterranean-diet exposure | diet*; dietary; intake; consumption | title/abstract/topic | Mixed | Protocol states diet adherence and component intake |
| sleep features | sleep | title/abstract/topic | No | Explicit protocol domain |
| sleep features | sleep quality | title/abstract/topic | No | Explicit protocol example outcome |
| sleep features | sleep duration | title/abstract/topic | No | Explicit protocol example outcome |
| sleep features | daytime sleepiness | title/abstract/topic | No | Explicit protocol example outcome |
| sleep features | sleepiness | title/abstract/topic | No | Protocol-compatible shorter wording |
| sleep features | somnolence | title/abstract/topic | No | Protocol-compatible clinical wording |
| sleep features | insomnia | title/abstract/topic | No | Protocol-compatible sleep-feature wording |
| sleep features | sleep disturbance; sleep disturbances; sleep disorder; sleep disorders; sleep feature; sleep features; sleep parameter; sleep parameters | title/abstract/topic | No | Protocol says diverse sleep features |
| adult population | adult* | title/abstract/topic | Yes | Explicit protocol population restriction |
| adult population | older adult; older adults | title/abstract/topic | No | Protocol-compatible age wording |

## JSON Query Object

```json
{
	"pubmed": [
		"# Q1: High-recall\n(((\"Diet, Mediterranean\"[Mesh] OR \"mediterranean diet\"[tiab] OR \"mediterranean dietary pattern\"[tiab] OR \"mediterranean-style diet\"[tiab] OR \"mediterranean diet adherence\"[tiab] OR \"mediterranean diet score\"[tiab] OR \"mediterranean dietary score\"[tiab] OR MedDiet[tiab] OR (((fruit*[tiab] OR vegetable*[tiab] OR cereal*[tiab] OR grain*[tiab] OR legume*[tiab] OR dairy[tiab] OR \"dairy product\"[tiab] OR \"dairy products\"[tiab] OR fish[tiab] OR meat[tiab] OR \"olive oil\"[tiab] OR alcohol[tiab] OR wine[tiab]) AND (diet*[tiab] OR dietary[tiab] OR intake[tiab] OR consumption[tiab])))) AND (\"Sleep\"[Mesh] OR \"Sleep Wake Disorders\"[Mesh] OR sleep[tiab] OR \"sleep quality\"[tiab] OR \"sleep duration\"[tiab] OR \"daytime sleepiness\"[tiab] OR sleepiness[tiab] OR somnolence[tiab] OR insomnia[tiab] OR \"sleep disturbance\"[tiab] OR \"sleep disturbances\"[tiab] OR \"sleep disorder\"[tiab] OR \"sleep disorders\"[tiab] OR \"sleep feature\"[tiab] OR \"sleep features\"[tiab] OR \"sleep parameter\"[tiab] OR \"sleep parameters\"[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab] OR \"older adult\"[tiab] OR \"older adults\"[tiab])))",
		"# Q2: Balanced\n(((\"Diet, Mediterranean\"[Mesh] OR \"mediterranean diet\"[tiab] OR \"mediterranean dietary pattern\"[tiab] OR \"mediterranean-style diet\"[tiab] OR \"mediterranean diet adherence\"[tiab] OR \"mediterranean diet score\"[tiab] OR \"mediterranean dietary score\"[tiab] OR MedDiet[tiab] OR (((legume*[tiab] OR fish[tiab] OR \"olive oil\"[tiab] OR alcohol[tiab] OR wine[tiab]) AND (diet*[tiab] OR dietary[tiab] OR intake[tiab] OR consumption[tiab])))) AND (\"Sleep\"[Mesh] OR \"Sleep Wake Disorders\"[Mesh] OR sleep[ti] OR \"sleep quality\"[tiab] OR \"sleep duration\"[tiab] OR \"daytime sleepiness\"[tiab] OR sleepiness[tiab] OR insomnia[tiab] OR \"sleep disorder\"[tiab] OR \"sleep disorders\"[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab] OR \"older adult\"[tiab] OR \"older adults\"[tiab])))",
		"# Q3: High-precision\n(((\"Diet, Mediterranean\"[Majr] OR \"mediterranean diet\"[ti] OR \"mediterranean dietary pattern\"[ti] OR \"mediterranean-style diet\"[ti] OR \"mediterranean diet score\"[tiab] OR MedDiet[tiab] OR (((\"olive oil\"[ti] OR legume*[ti] OR wine[ti]) AND (diet*[tiab] OR dietary[tiab] OR intake[tiab])))) AND (\"Sleep\"[Majr] OR \"Sleep Wake Disorders\"[Majr] OR sleep[ti] OR \"sleep quality\"[ti] OR \"sleep duration\"[ti] OR insomnia[ti] OR sleepiness[ti]) AND (\"Adult\"[Mesh] OR adult*[tiab] OR \"older adult\"[tiab] OR \"older adults\"[tiab])))",
		"# Q4: Balanced + scope_only\n((((\"mediterranean diet\"[ti] OR \"mediterranean dietary pattern\"[ti] OR \"mediterranean-style diet\"[ti] OR MedDiet[ti]) OR \"Diet, Mediterranean\"[Majr]) AND (sleep[ti] OR \"sleep quality\"[ti] OR \"sleep duration\"[ti] OR insomnia[ti] OR sleepiness[ti]) AND (\"Adult\"[Mesh] OR adult*[tiab] OR \"older adult\"[tiab] OR \"older adults\"[tiab])))",
		"# Q5: Balanced + filter_only\n((((\"Diet, Mediterranean\"[Mesh] OR \"mediterranean diet\"[tiab] OR \"mediterranean dietary pattern\"[tiab] OR \"mediterranean-style diet\"[tiab] OR \"mediterranean diet adherence\"[tiab] OR \"mediterranean diet score\"[tiab] OR \"mediterranean dietary score\"[tiab] OR MedDiet[tiab] OR (((legume*[tiab] OR fish[tiab] OR \"olive oil\"[tiab] OR alcohol[tiab] OR wine[tiab]) AND (diet*[tiab] OR dietary[tiab] OR intake[tiab] OR consumption[tiab])))) AND (\"Sleep\"[Mesh] OR \"Sleep Wake Disorders\"[Mesh] OR sleep[ti] OR \"sleep quality\"[tiab] OR \"sleep duration\"[tiab] OR \"daytime sleepiness\"[tiab] OR sleepiness[tiab] OR insomnia[tiab] OR \"sleep disorder\"[tiab] OR \"sleep disorders\"[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab] OR \"older adult\"[tiab] OR \"older adults\"[tiab])) AND humans[Filter]) NOT (review[pt] OR meta-analysis[pt] OR letter[pt] OR editorial[pt] OR comment[pt]))",
		"# Q6: Balanced + design_plus_filter\n((((\"Diet, Mediterranean\"[Mesh] OR \"mediterranean diet\"[tiab] OR \"mediterranean dietary pattern\"[tiab] OR \"mediterranean-style diet\"[tiab] OR \"mediterranean diet adherence\"[tiab] OR \"mediterranean diet score\"[tiab] OR \"mediterranean dietary score\"[tiab] OR MedDiet[tiab] OR (((legume*[tiab] OR fish[tiab] OR \"olive oil\"[tiab] OR alcohol[tiab] OR wine[tiab]) AND (diet*[tiab] OR dietary[tiab] OR intake[tiab] OR consumption[tiab])))) AND (\"Sleep\"[Mesh] OR \"Sleep Wake Disorders\"[Mesh] OR sleep[ti] OR \"sleep quality\"[tiab] OR \"sleep duration\"[tiab] OR \"daytime sleepiness\"[tiab] OR sleepiness[tiab] OR insomnia[tiab] OR \"sleep disorder\"[tiab] OR \"sleep disorders\"[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab] OR \"older adult\"[tiab] OR \"older adults\"[tiab]) AND (cohort[tiab] OR observational[tiab] OR longitudinal[tiab] OR \"cross-sectional\"[tiab] OR \"case-control\"[tiab])) AND humans[Filter]) NOT (review[pt] OR meta-analysis[pt] OR letter[pt] OR editorial[pt] OR comment[pt]))"
	],
	"scopus": [
		"# Q1: High-recall\nTITLE-ABS-KEY(((\"mediterranean diet\" OR \"mediterranean dietary pattern\" OR \"mediterranean-style diet\" OR \"mediterranean diet adherence\" OR \"mediterranean diet score\" OR \"mediterranean dietary score\" OR meddiet OR (((fruit* OR vegetable* OR cereal* OR grain* OR legume* OR dairy OR \"dairy product\" OR \"dairy products\" OR fish OR meat OR \"olive oil\" OR alcohol OR wine) AND (diet* OR dietary OR intake OR consumption)))) AND (sleep OR \"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR sleepiness OR somnolence OR insomnia OR \"sleep disturbance\" OR \"sleep disturbances\" OR \"sleep disorder\" OR \"sleep disorders\" OR \"sleep feature\" OR \"sleep features\" OR \"sleep parameter\" OR \"sleep parameters\") AND (adult* OR \"older adult\" OR \"older adults\")))",
		"# Q2: Balanced\nTITLE-ABS-KEY(((\"mediterranean diet\" OR \"mediterranean dietary pattern\" OR \"mediterranean-style diet\" OR \"mediterranean diet adherence\" OR \"mediterranean diet score\" OR \"mediterranean dietary score\" OR meddiet OR (((legume* OR fish OR \"olive oil\" OR alcohol OR wine) AND (diet* OR dietary OR intake OR consumption)))) AND (sleep OR \"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR sleepiness OR insomnia OR \"sleep disorder\" OR \"sleep disorders\") AND (adult* OR \"older adult\" OR \"older adults\")))",
		"# Q3: High-precision\nTITLE(\"mediterranean diet\" OR \"mediterranean dietary pattern\" OR \"mediterranean-style diet\" OR meddiet) AND TITLE-ABS-KEY(\"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR insomnia OR sleepiness OR sleep) AND TITLE-ABS-KEY(adult* OR \"older adult\" OR \"older adults\")",
		"# Q4: Balanced + scope_only\nTITLE(\"mediterranean diet\" OR \"mediterranean dietary pattern\" OR \"mediterranean-style diet\" OR meddiet) AND TITLE(sleep OR \"sleep quality\" OR \"sleep duration\" OR insomnia) AND TITLE-ABS-KEY(adult* OR \"older adult\" OR \"older adults\")",
		"# Q5: Balanced + proximity_or_scope_fallback\nTITLE-ABS-KEY((((mediterranean W/2 diet*) OR (mediterranean W/2 pattern*) OR meddiet OR (((\"olive oil\" OR legume* OR fish OR wine OR alcohol) W/3 (diet* OR dietary OR intake OR consumption)))) AND ((sleep W/2 quality) OR (sleep W/2 duration) OR (daytime W/1 sleepiness) OR insomnia OR sleepiness OR somnolence OR sleep) AND (adult* OR \"older adult\" OR \"older adults\")))",
		"# Q6: Balanced + design_plus_filter\nTITLE-ABS-KEY(((\"mediterranean diet\" OR \"mediterranean dietary pattern\" OR \"mediterranean-style diet\" OR \"mediterranean diet adherence\" OR \"mediterranean diet score\" OR \"mediterranean dietary score\" OR meddiet OR (((legume* OR fish OR \"olive oil\" OR alcohol OR wine) AND (diet* OR dietary OR intake OR consumption)))) AND (sleep OR \"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR sleepiness OR insomnia OR \"sleep disorder\" OR \"sleep disorders\") AND (adult* OR \"older adult\" OR \"older adults\"))) AND TITLE-ABS-KEY(cohort OR observational OR longitudinal OR \"cross-sectional\" OR \"case-control\") AND DOCTYPE(ar)"
	],
	"wos": [
		"# Q1: High-recall\nTS=(((\"mediterranean diet\" OR \"mediterranean dietary pattern\" OR \"mediterranean-style diet\" OR \"mediterranean diet adherence\" OR \"mediterranean diet score\" OR \"mediterranean dietary score\" OR meddiet OR (((fruit* OR vegetable* OR cereal* OR grain* OR legume* OR dairy OR \"dairy product\" OR \"dairy products\" OR fish OR meat OR \"olive oil\" OR alcohol OR wine) AND (diet* OR dietary OR intake OR consumption)))) AND (sleep OR \"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR sleepiness OR somnolence OR insomnia OR \"sleep disturbance\" OR \"sleep disturbances\" OR \"sleep disorder\" OR \"sleep disorders\" OR \"sleep feature\" OR \"sleep features\" OR \"sleep parameter\" OR \"sleep parameters\") AND (adult* OR \"older adult\" OR \"older adults\")))",
		"# Q2: Balanced\nTS=(((\"mediterranean diet\" OR \"mediterranean dietary pattern\" OR \"mediterranean-style diet\" OR \"mediterranean diet adherence\" OR \"mediterranean diet score\" OR \"mediterranean dietary score\" OR meddiet OR (((legume* OR fish OR \"olive oil\" OR alcohol OR wine) AND (diet* OR dietary OR intake OR consumption)))) AND (sleep OR \"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR sleepiness OR insomnia OR \"sleep disorder\" OR \"sleep disorders\") AND (adult* OR \"older adult\" OR \"older adults\")))",
		"# Q3: High-precision\nTI=(\"mediterranean diet\" OR \"mediterranean dietary pattern\" OR \"mediterranean-style diet\" OR meddiet) AND TS=(\"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR insomnia OR sleepiness OR sleep) AND TS=(adult* OR \"older adult\" OR \"older adults\")",
		"# Q4: Balanced + scope_only\nTI=(\"mediterranean diet\" OR \"mediterranean dietary pattern\" OR \"mediterranean-style diet\" OR meddiet) AND TI=(sleep OR \"sleep quality\" OR \"sleep duration\" OR insomnia) AND TS=(adult* OR \"older adult\" OR \"older adults\")",
		"# Q5: Balanced + proximity_or_scope_fallback\nTS=((((mediterranean NEAR/2 diet*) OR (mediterranean NEAR/2 pattern*) OR meddiet OR (((\"olive oil\" OR legume* OR fish OR wine OR alcohol) NEAR/3 (diet* OR dietary OR intake OR consumption)))) AND ((sleep NEAR/2 quality) OR (sleep NEAR/2 duration) OR (daytime NEAR/1 sleepiness) OR insomnia OR sleepiness OR somnolence OR sleep) AND (adult* OR \"older adult\" OR \"older adults\")))",
		"# Q6: Balanced + design_plus_filter\nTS=(((\"mediterranean diet\" OR \"mediterranean dietary pattern\" OR \"mediterranean-style diet\" OR \"mediterranean diet adherence\" OR \"mediterranean diet score\" OR \"mediterranean dietary score\" OR meddiet OR (((legume* OR fish OR \"olive oil\" OR alcohol OR wine) AND (diet* OR dietary OR intake OR consumption)))) AND (sleep OR \"sleep quality\" OR \"sleep duration\" OR \"daytime sleepiness\" OR sleepiness OR insomnia OR \"sleep disorder\" OR \"sleep disorders\") AND (adult* OR \"older adult\" OR \"older adults\"))) AND TS=(cohort OR observational OR longitudinal OR \"cross-sectional\" OR \"case-control\") AND DT=(Article)"
	],
	"embase": [
		"# Q1: High-recall\n(('mediterranean diet'/exp OR 'mediterranean diet':ti,ab OR 'mediterranean dietary pattern':ti,ab OR 'mediterranean-style diet':ti,ab OR 'mediterranean diet adherence':ti,ab OR 'mediterranean diet score':ti,ab OR 'mediterranean dietary score':ti,ab OR meddiet:ti,ab OR (((fruit*:ti,ab OR vegetable*:ti,ab OR cereal*:ti,ab OR grain*:ti,ab OR legume*:ti,ab OR dairy:ti,ab OR 'dairy product':ti,ab OR 'dairy products':ti,ab OR fish:ti,ab OR meat:ti,ab OR 'olive oil':ti,ab OR alcohol:ti,ab OR wine:ti,ab) AND (diet*:ti,ab OR dietary:ti,ab OR intake:ti,ab OR consumption:ti,ab)))) AND ('sleep'/exp OR 'sleep disorder'/exp OR 'somnolence'/exp OR sleep:ti,ab OR 'sleep quality':ti,ab OR 'sleep duration':ti,ab OR 'daytime sleepiness':ti,ab OR sleepiness:ti,ab OR somnolence:ti,ab OR insomnia:ti,ab OR 'sleep disturbance':ti,ab OR 'sleep disturbances':ti,ab OR 'sleep disorder':ti,ab OR 'sleep disorders':ti,ab OR 'sleep feature':ti,ab OR 'sleep features':ti,ab OR 'sleep parameter':ti,ab OR 'sleep parameters':ti,ab) AND ('adult'/exp OR adult*:ti,ab OR 'older adult':ti,ab OR 'older adults':ti,ab))",
		"# Q2: Balanced\n(('mediterranean diet'/exp OR 'mediterranean diet':ti,ab OR 'mediterranean dietary pattern':ti,ab OR 'mediterranean-style diet':ti,ab OR 'mediterranean diet adherence':ti,ab OR 'mediterranean diet score':ti,ab OR 'mediterranean dietary score':ti,ab OR meddiet:ti,ab OR (((legume*:ti,ab OR fish:ti,ab OR 'olive oil':ti,ab OR alcohol:ti,ab OR wine:ti,ab) AND (diet*:ti,ab OR dietary:ti,ab OR intake:ti,ab OR consumption:ti,ab)))) AND ('sleep'/exp OR 'sleep disorder'/exp OR sleep:ti OR 'sleep quality':ti,ab OR 'sleep duration':ti,ab OR 'daytime sleepiness':ti,ab OR sleepiness:ti,ab OR insomnia:ti,ab OR 'sleep disorder':ti,ab OR 'sleep disorders':ti,ab) AND ('adult'/exp OR adult*:ti,ab OR 'older adult':ti,ab OR 'older adults':ti,ab))",
		"# Q3: High-precision\n(('mediterranean diet'/mj OR 'mediterranean diet':ti OR 'mediterranean dietary pattern':ti OR 'mediterranean-style diet':ti OR meddiet:ti OR (((('olive oil':ti OR legume*:ti OR wine:ti) AND (diet*:ti,ab OR dietary:ti,ab OR intake:ti,ab)))) AND ('sleep'/mj OR 'sleep disorder'/mj OR sleep:ti OR 'sleep quality':ti OR 'sleep duration':ti OR insomnia:ti OR sleepiness:ti) AND ('adult'/exp OR adult*:ti,ab OR 'older adult':ti,ab OR 'older adults':ti,ab))",
		"# Q4: Balanced + scope_only\n((('mediterranean diet':ti OR 'mediterranean dietary pattern':ti OR 'mediterranean-style diet':ti OR meddiet:ti) OR 'mediterranean diet'/mj) AND (sleep:ti OR 'sleep quality':ti OR 'sleep duration':ti OR insomnia:ti) AND ('adult'/exp OR adult*:ti,ab OR 'older adult':ti,ab OR 'older adults':ti,ab))",
		"# Q5: Balanced + proximity_or_scope_fallback\n((((mediterranean ADJ2 diet*):ti,ab OR (mediterranean ADJ2 pattern*):ti,ab OR meddiet:ti,ab OR ((((('olive oil' OR legume* OR fish OR wine OR alcohol) ADJ3 (diet* OR dietary OR intake OR consumption))):ti,ab)) AND (((sleep ADJ2 quality):ti,ab OR (sleep ADJ2 duration):ti,ab OR (daytime ADJ1 sleepiness):ti,ab OR insomnia:ti,ab OR sleepiness:ti,ab OR somnolence:ti,ab OR sleep:ti,ab)) AND ('adult'/exp OR adult*:ti,ab OR 'older adult':ti,ab OR 'older adults':ti,ab))",
		"# Q6: Balanced + design_plus_filter\n(('mediterranean diet'/exp OR 'mediterranean diet':ti,ab OR 'mediterranean dietary pattern':ti,ab OR 'mediterranean-style diet':ti,ab OR 'mediterranean diet adherence':ti,ab OR 'mediterranean diet score':ti,ab OR 'mediterranean dietary score':ti,ab OR meddiet:ti,ab OR (((legume*:ti,ab OR fish:ti,ab OR 'olive oil':ti,ab OR alcohol:ti,ab OR wine:ti,ab) AND (diet*:ti,ab OR dietary:ti,ab OR intake:ti,ab OR consumption:ti,ab)))) AND ('sleep'/exp OR 'sleep disorder'/exp OR sleep:ti OR 'sleep quality':ti,ab OR 'sleep duration':ti,ab OR 'daytime sleepiness':ti,ab OR sleepiness:ti,ab OR insomnia:ti,ab OR 'sleep disorder':ti,ab OR 'sleep disorders':ti,ab) AND ('adult'/exp OR adult*:ti,ab OR 'older adult':ti,ab OR 'older adults':ti,ab) AND (cohort:ti,ab OR observational:ti,ab OR longitudinal:ti,ab OR 'cross-sectional':ti,ab OR 'case-control':ti,ab))"
	]
}
```

## PRESS Self-Check

```json
{
	"json_patch": {}
}
```

- Q1 and Q2 preserve the same mandatory-core block structure across all databases: Mediterranean-diet exposure, sleep features, and adult population.
- Comparator strata and population exclusions were kept out of baseline retrieval because the protocol frames them as eligibility rules rather than subject-matter concepts.
- Observational-study labels remain outside baseline Q1 and Q2 and are introduced only in the bundled design variant.
- Q4 to Q6 use only approved bundled cases.
- No inline publication-date limits were added because the protocol specifies searching from inception.
- Embase queries use Embase.com syntax consistently.

## Translation Notes

- The protocol supports a `single_route` architecture because it defines one coherent Boolean route linking exposure, sleep outcomes, and adult population.
- `design_analytic_block` remains active by workflow rule, but the protocol supports only conservative use of design restrictions; those were therefore confined to bundled variants.
- The component list was retained in Q1 and kept narrower in Q2 and Q3 to avoid drifting into generic diet-and-sleep retrieval while still honoring the protocol's explicit component examples.
- Adult-population wording remains in baseline retrieval because the protocol makes adulthood an inclusion-defining population concept.