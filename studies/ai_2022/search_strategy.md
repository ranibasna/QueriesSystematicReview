# Search Strategy for ai_2022

## Study Summary

- Topic: Blood pressure outcomes in children and adolescents with sleep-disordered breathing
- Date window: No inline publication-date restriction; the protocol does not specify a date limit
- Databases: pubmed, scopus, wos, embase
- Query level: extended
- Retrieval architecture: single_route
- design_analytic_block: active, but populated conservatively and reserved for bundled precision variants

## PICOS Summary

- Population: Children and adolescents with sleep-disordered breathing, including primary snoring and varying sleep-disordered-breathing severity, without congenital heart disease or prior surgical or CPAP intervention
- Intervention or Exposure: Pediatric sleep-disordered breathing spectrum
- Comparator: Healthy children without sleep disturbance history
- Outcomes: Mean, systolic, and diastolic blood pressure during sleep or wakefulness, ambulatory blood pressure, blood-pressure load, nondipping, and SBP index
- Design: Observational comparative studies, specifically case-control, cross-sectional, and longitudinal cohort studies

## Architecture Selection Summary

- Selected retrieval architecture: `single_route`
- `design_analytic_block`: active

### Concept Roles

| Role | Assigned concepts |
| --- | --- |
| mandatory_core | sleep-disordered breathing spectrum including obstructive sleep apnea and primary snoring; blood-pressure outcomes; pediatric population |
| optional_precision | ambulatory and nocturnal blood-pressure wording; tighter title-only focus; proximity tightening where supported |
| filter_only | observational-study labels; humans or document-type filters where platform-safe; protocol English-language restriction as an interface-level limit |
| screening_only | healthy-control requirement; congenital heart disease exclusion; post-intervention exclusion; subgroup contrasts by SDB severity |

The protocol supports one coherent Boolean route rather than two complementary indexed and free-text routes, so `single_route` is the safer fit. The active `design_analytic_block` is kept conservative: observational-design labels are explicit in the protocol, but many relevant pediatric SDB studies will not foreground those labels in titles or abstracts, so they are reserved for bundled precision variants rather than baseline retrieval.

## Concept Tables

### Concept to MeSH or Emtree

| concept | term | tree note | explode? | rationale and source |
| --- | --- | --- | --- | --- |
| SDB core | Sleep Apnea Syndromes / sleep apnea syndrome | broad indexed representation for pediatric sleep-disordered breathing | Yes | Protocol title, review objective, and condition/domain section |
| SDB core | Sleep Apnea, Obstructive / sleep apnea syndrome | specific indexed support for obstructive sleep apnea within the SDB spectrum | Yes | Protocol exposure includes a spectrum of SDB severity |
| SDB core | Snoring / snoring | indexed support for the primary-snoring end of the spectrum | Yes | Protocol exposure explicitly includes primary snoring |
| Blood-pressure core | Blood Pressure / blood pressure | broad indexed representation for the main outcome domain | Yes | Protocol title and main outcomes |
| Blood-pressure core | Blood Pressure Monitoring, Ambulatory / blood pressure monitoring | indexed support for ambulatory blood-pressure measurement | Yes | Protocol exposure and subgroup wording mention ambulatory blood pressure |
| Pediatric core | Child; Adolescent / child; adolescent | indexed support for the pediatric population | Yes | Protocol population is children and adolescents |
| Design block | Case-Control Studies; Cross-Sectional Studies; Cohort Studies / case control study; cross-sectional study; cohort analysis | observational-comparative design support | Yes | Protocol study-design eligibility |

### Concept to Textword

| concept | synonym or phrase | field | truncation? | source |
| --- | --- | --- | --- | --- |
| SDB core | sleep disordered breathing; sleep-disordered breathing | title/abstract/topic | No | Protocol title and objective |
| SDB core | sleep related breathing disorder; sleep related breathing disorders; sleep-related breathing disorder; sleep-related breathing disorders | title/abstract/topic | No | Protocol-compatible wording supported by domain guidance |
| SDB core | sleep apnea; sleep apnoea; obstructive sleep apnea; obstructive sleep apnoea | title/abstract/topic | No | Protocol condition/domain wording and explicit SDB spectrum |
| SDB core | primary snoring; snor* | title/abstract/topic | Mixed | Protocol exposure includes primary snoring |
| SDB core | OSA; OSAS | title/abstract/topic | No | Domain guidance allows specific acronyms when paired conservatively |
| Blood-pressure core | blood pressure | title/abstract/topic | No | Protocol title and condition/domain wording |
| Blood-pressure core | ambulatory blood pressure; blood pressure monitoring | title/abstract/topic | No | Protocol exposure and subgroup wording |
| Blood-pressure core | systolic blood pressure; diastolic blood pressure; mean blood pressure | title/abstract/topic | No | Protocol main outcomes |
| Blood-pressure core | blood pressure load; BP load; nondipping; non-dipping; SBP index | title/abstract/topic | No | Protocol additional outcomes |
| Pediatric core | child*; adolescen*; pediatric*; paediatric*; youth*; teen* | title/abstract/topic | Mixed | Protocol population |
| Design block | cohort; longitudinal; observational; case-control; case control; cross-sectional; cross sectional | title/abstract/topic | No | Protocol study designs |
| Comparator screening | healthy child*; healthy control*; control group | title/abstract/topic | Mixed | Protocol comparator |

## JSON Query Object

```json
{
	"pubmed": [
		"# Q1: High-recall\n((\"Sleep Apnea Syndromes\"[Mesh] OR \"Sleep Apnea, Obstructive\"[Mesh] OR \"Snoring\"[Mesh] OR \"sleep disordered breathing\"[tiab] OR \"sleep-disordered breathing\"[tiab] OR \"sleep related breathing disorder\"[tiab] OR \"sleep related breathing disorders\"[tiab] OR \"sleep-related breathing disorder\"[tiab] OR \"sleep-related breathing disorders\"[tiab] OR \"sleep apnea\"[tiab] OR \"sleep apnoea\"[tiab] OR \"obstructive sleep apnea\"[tiab] OR \"obstructive sleep apnoea\"[tiab] OR \"primary snoring\"[tiab] OR snor*[tiab] OR ((OSA[tiab] OR OSAS[tiab]) AND sleep[tiab])) AND (\"Blood Pressure\"[Mesh] OR \"Blood Pressure Monitoring, Ambulatory\"[Mesh] OR \"blood pressure\"[tiab] OR \"ambulatory blood pressure\"[tiab] OR \"blood pressure monitoring\"[tiab] OR \"systolic blood pressure\"[tiab] OR \"diastolic blood pressure\"[tiab] OR \"mean blood pressure\"[tiab] OR \"blood pressure load\"[tiab] OR \"BP load\"[tiab] OR nondipping[tiab] OR \"non-dipping\"[tiab] OR \"SBP index\"[tiab]) AND (\"Child\"[Mesh] OR \"Adolescent\"[Mesh] OR child*[tiab] OR adolescen*[tiab] OR pediatric*[tiab] OR paediatric*[tiab] OR youth*[tiab] OR teen*[tiab]))",
		"# Q2: Balanced\n((\"Sleep Apnea Syndromes\"[Mesh] OR \"Sleep Apnea, Obstructive\"[Mesh] OR \"Snoring\"[Mesh] OR \"sleep disordered breathing\"[tiab] OR \"sleep-disordered breathing\"[tiab] OR \"sleep apnea\"[tiab] OR \"sleep apnoea\"[tiab] OR \"obstructive sleep apnea\"[tiab] OR \"obstructive sleep apnoea\"[tiab] OR \"primary snoring\"[tiab]) AND (\"Blood Pressure\"[Mesh] OR \"Blood Pressure Monitoring, Ambulatory\"[Mesh] OR \"blood pressure\"[tiab] OR \"ambulatory blood pressure\"[tiab] OR \"blood pressure monitoring\"[tiab] OR \"systolic blood pressure\"[tiab] OR \"diastolic blood pressure\"[tiab] OR \"mean blood pressure\"[tiab] OR \"blood pressure load\"[tiab] OR nondipping[tiab] OR \"non-dipping\"[tiab] OR \"SBP index\"[tiab]) AND (\"Child\"[Mesh] OR \"Adolescent\"[Mesh] OR child*[tiab] OR adolescen*[tiab] OR pediatric*[tiab] OR paediatric*[tiab] OR youth*[tiab]))",
		"# Q3: High-precision\n((\"Sleep Apnea Syndromes\"[Majr] OR \"Sleep Apnea, Obstructive\"[Majr] OR \"Snoring\"[Majr] OR \"sleep disordered breathing\"[ti] OR \"sleep-disordered breathing\"[ti] OR \"obstructive sleep apnea\"[ti] OR \"obstructive sleep apnoea\"[ti] OR \"primary snoring\"[ti]) AND (\"Blood Pressure\"[Majr] OR \"blood pressure\"[ti] OR \"ambulatory blood pressure\"[ti] OR \"systolic blood pressure\"[ti] OR \"diastolic blood pressure\"[ti] OR \"mean blood pressure\"[ti] OR \"blood pressure load\"[ti] OR \"non-dipping\"[tiab] OR \"SBP index\"[tiab]) AND (\"Child\"[Mesh] OR \"Adolescent\"[Mesh] OR child*[tiab] OR adolescen*[tiab] OR pediatric*[tiab] OR paediatric*[tiab]))",
		"# Q4: Balanced + scope_only\n((\"sleep disordered breathing\"[ti] OR \"sleep-disordered breathing\"[ti] OR \"sleep apnea\"[ti] OR \"sleep apnoea\"[ti] OR \"obstructive sleep apnea\"[ti] OR \"obstructive sleep apnoea\"[ti] OR \"primary snoring\"[ti]) AND (\"blood pressure\"[ti] OR \"ambulatory blood pressure\"[ti] OR \"systolic blood pressure\"[ti] OR \"diastolic blood pressure\"[ti] OR \"mean blood pressure\"[ti] OR \"blood pressure load\"[ti]) AND (child*[tiab] OR adolescen*[tiab] OR pediatric*[tiab] OR paediatric*[tiab]))",
		"# Q5: Balanced + proximity_or_scope_fallback\n((\"Sleep Apnea Syndromes\"[Majr] OR \"Sleep Apnea, Obstructive\"[Majr] OR \"sleep disordered breathing\"[ti] OR \"sleep-disordered breathing\"[ti] OR \"obstructive sleep apnea\"[ti] OR \"obstructive sleep apnoea\"[ti] OR \"primary snoring\"[ti]) AND (\"blood pressure\"[ti] OR \"ambulatory blood pressure\"[ti] OR \"systolic blood pressure\"[ti] OR \"diastolic blood pressure\"[ti] OR \"blood pressure load\"[ti] OR \"non-dipping\"[tiab]) AND (child*[tiab] OR adolescen*[tiab] OR pediatric*[tiab] OR paediatric*[tiab]))",
		"# Q6: Balanced + design_plus_filter\n(((\"Sleep Apnea Syndromes\"[Mesh] OR \"Sleep Apnea, Obstructive\"[Mesh] OR \"Snoring\"[Mesh] OR \"sleep disordered breathing\"[tiab] OR \"sleep-disordered breathing\"[tiab] OR \"sleep apnea\"[tiab] OR \"sleep apnoea\"[tiab] OR \"obstructive sleep apnea\"[tiab] OR \"obstructive sleep apnoea\"[tiab] OR \"primary snoring\"[tiab]) AND (\"Blood Pressure\"[Mesh] OR \"Blood Pressure Monitoring, Ambulatory\"[Mesh] OR \"blood pressure\"[tiab] OR \"ambulatory blood pressure\"[tiab] OR \"blood pressure monitoring\"[tiab] OR \"systolic blood pressure\"[tiab] OR \"diastolic blood pressure\"[tiab] OR \"mean blood pressure\"[tiab] OR \"blood pressure load\"[tiab] OR nondipping[tiab] OR \"non-dipping\"[tiab] OR \"SBP index\"[tiab]) AND (\"Child\"[Mesh] OR \"Adolescent\"[Mesh] OR child*[tiab] OR adolescen*[tiab] OR pediatric*[tiab] OR paediatric*[tiab] OR youth*[tiab]) AND (cohort[tiab] OR longitudinal[tiab] OR observational[tiab] OR \"case-control\"[tiab] OR \"case control\"[tiab] OR \"cross-sectional\"[tiab] OR \"cross sectional\"[tiab])) AND humans[Filter]) NOT (review[pt] OR meta-analysis[pt] OR letter[pt] OR editorial[pt] OR comment[pt])"
	],
	"scopus": [
		"# Q1: High-recall\nTITLE-ABS-KEY(((\"sleep disordered breathing\" OR \"sleep-disordered breathing\" OR \"sleep related breathing disorder\" OR \"sleep related breathing disorders\" OR \"sleep-related breathing disorder\" OR \"sleep-related breathing disorders\" OR \"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\" OR snor* OR ((OSA OR OSAS) W/2 sleep)) AND (\"blood pressure\" OR \"ambulatory blood pressure\" OR \"blood pressure monitoring\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR \"mean blood pressure\" OR \"blood pressure load\" OR \"BP load\" OR nondipping OR \"non-dipping\" OR \"SBP index\") AND (child* OR adolescen* OR pediatric* OR paediatric* OR youth* OR teen*)))",
		"# Q2: Balanced\nTITLE-ABS-KEY(((\"sleep disordered breathing\" OR \"sleep-disordered breathing\" OR \"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\") AND (\"blood pressure\" OR \"ambulatory blood pressure\" OR \"blood pressure monitoring\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR \"mean blood pressure\" OR \"blood pressure load\" OR nondipping OR \"non-dipping\" OR \"SBP index\") AND (child* OR adolescen* OR pediatric* OR paediatric* OR youth*)))",
		"# Q3: High-precision\nTITLE(\"sleep disordered breathing\" OR \"sleep-disordered breathing\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\") AND TITLE(\"blood pressure\" OR \"ambulatory blood pressure\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR \"mean blood pressure\" OR \"blood pressure load\") AND TITLE-ABS-KEY(child* OR adolescen* OR pediatric* OR paediatric*)",
		"# Q4: Balanced + scope_only\nTITLE(\"sleep disordered breathing\" OR \"sleep-disordered breathing\" OR \"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\") AND TITLE(\"blood pressure\" OR \"ambulatory blood pressure\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR \"blood pressure load\") AND TITLE-ABS-KEY(child* OR adolescen* OR pediatric* OR paediatric*)",
		"# Q5: Balanced + proximity_or_scope_fallback\nTITLE-ABS-KEY((((\"sleep disordered breathing\" OR \"sleep-disordered breathing\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\" OR snor*) W/5 (\"blood pressure\" OR \"ambulatory blood pressure\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR \"blood pressure load\" OR \"non-dipping\")) AND (child* OR adolescen* OR pediatric* OR paediatric*)))",
		"# Q6: Balanced + design_plus_filter\nTITLE-ABS-KEY(((\"sleep disordered breathing\" OR \"sleep-disordered breathing\" OR \"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\") AND (\"blood pressure\" OR \"ambulatory blood pressure\" OR \"blood pressure monitoring\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR \"mean blood pressure\" OR \"blood pressure load\" OR nondipping OR \"non-dipping\" OR \"SBP index\") AND (child* OR adolescen* OR pediatric* OR paediatric* OR youth*))) AND TITLE-ABS-KEY(cohort OR longitudinal OR observational OR \"case-control\" OR \"case control\" OR \"cross-sectional\" OR \"cross sectional\") AND DOCTYPE(ar)"
	],
	"wos": [
		"# Q1: High-recall\nTS=(((\"sleep disordered breathing\" OR \"sleep-disordered breathing\" OR \"sleep related breathing disorder\" OR \"sleep related breathing disorders\" OR \"sleep-related breathing disorder\" OR \"sleep-related breathing disorders\" OR \"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\" OR snor* OR ((OSA OR OSAS) NEAR/2 sleep)) AND (\"blood pressure\" OR \"ambulatory blood pressure\" OR \"blood pressure monitoring\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR \"mean blood pressure\" OR \"blood pressure load\" OR \"BP load\" OR nondipping OR \"non-dipping\" OR \"SBP index\") AND (child* OR adolescen* OR pediatric* OR paediatric* OR youth* OR teen*)))",
		"# Q2: Balanced\nTS=(((\"sleep disordered breathing\" OR \"sleep-disordered breathing\" OR \"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\") AND (\"blood pressure\" OR \"ambulatory blood pressure\" OR \"blood pressure monitoring\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR \"mean blood pressure\" OR \"blood pressure load\" OR nondipping OR \"non-dipping\" OR \"SBP index\") AND (child* OR adolescen* OR pediatric* OR paediatric* OR youth*)))",
		"# Q3: High-precision\nTI=(\"sleep disordered breathing\" OR \"sleep-disordered breathing\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\") AND TI=(\"blood pressure\" OR \"ambulatory blood pressure\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR \"mean blood pressure\" OR \"blood pressure load\") AND TS=(child* OR adolescen* OR pediatric* OR paediatric*)",
		"# Q4: Balanced + scope_only\nTI=(\"sleep disordered breathing\" OR \"sleep-disordered breathing\" OR \"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\") AND TI=(\"blood pressure\" OR \"ambulatory blood pressure\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR \"blood pressure load\") AND TS=(child* OR adolescen* OR pediatric* OR paediatric*)",
		"# Q5: Balanced + proximity_or_scope_fallback\nTS=((((\"sleep disordered breathing\" OR \"sleep-disordered breathing\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\" OR snor*) NEAR/5 (\"blood pressure\" OR \"ambulatory blood pressure\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR \"blood pressure load\" OR \"non-dipping\")) AND (child* OR adolescen* OR pediatric* OR paediatric*)))",
		"# Q6: Balanced + design_plus_filter\nTS=(((\"sleep disordered breathing\" OR \"sleep-disordered breathing\" OR \"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\") AND (\"blood pressure\" OR \"ambulatory blood pressure\" OR \"blood pressure monitoring\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR \"mean blood pressure\" OR \"blood pressure load\" OR nondipping OR \"non-dipping\" OR \"SBP index\") AND (child* OR adolescen* OR pediatric* OR paediatric* OR youth*))) AND TS=(cohort OR longitudinal OR observational OR \"case-control\" OR \"case control\" OR \"cross-sectional\" OR \"cross sectional\") AND DT=(Article)"
	],
	"embase": [
		"# Q1: High-recall\n(('sleep apnea syndrome'/exp OR 'snoring'/exp OR 'sleep disordered breathing':ti,ab OR 'sleep-disordered breathing':ti,ab OR 'sleep related breathing disorder':ti,ab OR 'sleep related breathing disorders':ti,ab OR 'sleep-related breathing disorder':ti,ab OR 'sleep-related breathing disorders':ti,ab OR 'sleep apnea':ti,ab OR 'sleep apnoea':ti,ab OR 'obstructive sleep apnea':ti,ab OR 'obstructive sleep apnoea':ti,ab OR 'primary snoring':ti,ab OR snor*:ti,ab) AND ('blood pressure'/exp OR 'blood pressure monitoring'/exp OR 'blood pressure':ti,ab OR 'ambulatory blood pressure':ti,ab OR 'blood pressure monitoring':ti,ab OR 'systolic blood pressure':ti,ab OR 'diastolic blood pressure':ti,ab OR 'mean blood pressure':ti,ab OR 'blood pressure load':ti,ab OR 'bp load':ti,ab OR nondipping:ti,ab OR 'non-dipping':ti,ab OR 'sbp index':ti,ab) AND ('child'/exp OR 'adolescent'/exp OR child*:ti,ab OR adolescen*:ti,ab OR pediatric*:ti,ab OR paediatric*:ti,ab OR youth*:ti,ab OR teen*:ti,ab))",
		"# Q2: Balanced\n(('sleep apnea syndrome'/exp OR 'snoring'/exp OR 'sleep disordered breathing':ti,ab OR 'sleep-disordered breathing':ti,ab OR 'sleep apnea':ti,ab OR 'sleep apnoea':ti,ab OR 'obstructive sleep apnea':ti,ab OR 'obstructive sleep apnoea':ti,ab OR 'primary snoring':ti,ab) AND ('blood pressure'/exp OR 'blood pressure monitoring'/exp OR 'blood pressure':ti,ab OR 'ambulatory blood pressure':ti,ab OR 'blood pressure monitoring':ti,ab OR 'systolic blood pressure':ti,ab OR 'diastolic blood pressure':ti,ab OR 'mean blood pressure':ti,ab OR 'blood pressure load':ti,ab OR nondipping:ti,ab OR 'non-dipping':ti,ab OR 'sbp index':ti,ab) AND ('child'/exp OR 'adolescent'/exp OR child*:ti,ab OR adolescen*:ti,ab OR pediatric*:ti,ab OR paediatric*:ti,ab OR youth*:ti,ab))",
		"# Q3: High-precision\n(('sleep apnea syndrome'/mj OR 'snoring'/mj OR 'sleep disordered breathing':ti OR 'sleep-disordered breathing':ti OR 'obstructive sleep apnea':ti OR 'obstructive sleep apnoea':ti OR 'primary snoring':ti) AND ('blood pressure'/mj OR 'blood pressure':ti OR 'ambulatory blood pressure':ti OR 'systolic blood pressure':ti OR 'diastolic blood pressure':ti OR 'mean blood pressure':ti OR 'blood pressure load':ti OR 'non-dipping':ti,ab OR 'sbp index':ti,ab) AND ('child'/exp OR 'adolescent'/exp OR child*:ti,ab OR adolescen*:ti,ab OR pediatric*:ti,ab OR paediatric*:ti,ab))",
		"# Q4: Balanced + scope_only\n(('sleep disordered breathing':ti OR 'sleep-disordered breathing':ti OR 'sleep apnea':ti OR 'sleep apnoea':ti OR 'obstructive sleep apnea':ti OR 'obstructive sleep apnoea':ti OR 'primary snoring':ti) AND ('blood pressure':ti OR 'ambulatory blood pressure':ti OR 'systolic blood pressure':ti OR 'diastolic blood pressure':ti OR 'mean blood pressure':ti OR 'blood pressure load':ti) AND ('child'/exp OR 'adolescent'/exp OR child*:ti,ab OR adolescen*:ti,ab OR pediatric*:ti,ab OR paediatric*:ti,ab))",
		"# Q5: Balanced + proximity_or_scope_fallback\n(((('sleep disordered breathing' OR 'sleep-disordered breathing' OR 'obstructive sleep apnea' OR 'obstructive sleep apnoea' OR 'primary snoring' OR snor*) ADJ5 ('blood pressure' OR 'ambulatory blood pressure' OR 'systolic blood pressure' OR 'diastolic blood pressure' OR 'blood pressure load' OR 'non-dipping')):ti,ab AND ('child'/exp OR 'adolescent'/exp OR child*:ti,ab OR adolescen*:ti,ab OR pediatric*:ti,ab OR paediatric*:ti,ab)))",
		"# Q6: Balanced + design_plus_filter\n(('sleep apnea syndrome'/exp OR 'snoring'/exp OR 'sleep disordered breathing':ti,ab OR 'sleep-disordered breathing':ti,ab OR 'sleep apnea':ti,ab OR 'sleep apnoea':ti,ab OR 'obstructive sleep apnea':ti,ab OR 'obstructive sleep apnoea':ti,ab OR 'primary snoring':ti,ab) AND ('blood pressure'/exp OR 'blood pressure monitoring'/exp OR 'blood pressure':ti,ab OR 'ambulatory blood pressure':ti,ab OR 'blood pressure monitoring':ti,ab OR 'systolic blood pressure':ti,ab OR 'diastolic blood pressure':ti,ab OR 'mean blood pressure':ti,ab OR 'blood pressure load':ti,ab OR nondipping:ti,ab OR 'non-dipping':ti,ab OR 'sbp index':ti,ab) AND ('child'/exp OR 'adolescent'/exp OR child*:ti,ab OR adolescen*:ti,ab OR pediatric*:ti,ab OR paediatric*:ti,ab OR youth*:ti,ab) AND (cohort:ti,ab OR longitudinal:ti,ab OR observational:ti,ab OR 'case-control':ti,ab OR 'case control':ti,ab OR 'cross-sectional':ti,ab OR 'cross sectional':ti,ab))"
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

- Q1 and Q2 preserve the same mandatory-core route across all databases: pediatric sleep-disordered breathing AND blood-pressure outcomes AND pediatric age wording.
- Healthy-control wording, congenital-heart-disease exclusions, prior intervention exclusions, and severity subgroup contrasts were kept out of baseline retrieval because the protocol treats them as eligibility or subgroup rules better handled during screening.
- The bundled variants use only approved cases: `scope_only`, `proximity_or_scope_fallback`, and `design_plus_filter`.
- PubMed uses a scope fallback rather than proximity in Q5 because proximity operators are unavailable.
- Embase is translated in Embase.com syntax to stay consistent with repository guidance.
- The protocol names MEDLINE, Web of Science, and PubMed, but the repository workflow expects the standard four output files for pubmed, scopus, wos, and embase, so the query family was translated to that standard set.
- The protocol's English-language restriction is best applied as an interface-level limit rather than embedded inline across all database strings.# Search Strategy for ai_2022

## Study Summary

- Topic: Blood pressure outcomes in children and adolescents with sleep-disordered breathing
- Date window: No inline publication-date restriction; the protocol states no date restriction and English-language searching
- Databases: pubmed, scopus, wos, embase
- Query level: extended
- Retrieval architecture: single_route
- design_analytic_block: active, but populated conservatively and used only in bundled precision variants

## PICOS Summary

- Population: Children and adolescents aged 0 to 18 years with sleep-disordered breathing
- Intervention or Exposure: Sleep-disordered breathing spectrum, including primary snoring and mild, moderate, or severe SDB
- Comparator: Healthy children or adolescents without sleep disturbance history
- Outcomes: Mean blood pressure, systolic blood pressure, diastolic blood pressure, awake or sleep blood pressure, blood pressure load, nondipping blood pressure, and SBP index
- Design: Observational comparisons, especially case-control, cross-sectional, and longitudinal cohort studies

## Architecture Selection Summary

- Selected retrieval architecture: `single_route`
- `design_analytic_block`: active

### Concept Roles

| Role | Assigned concepts |
| --- | --- |
| mandatory_core | pediatric population; sleep-disordered breathing spectrum; blood pressure outcomes |
| optional_precision | primary snoring; obstructive sleep apnea wording; OAHI phrasing; ambulatory or nondipping blood pressure wording; title-only or proximity tightening |
| filter_only | English-language restriction; observational-study labels; article-type restriction; human-only filter where supported |
| screening_only | healthy-control requirement; congenital heart disease exclusion; post-intervention exclusion; other non-SDB pathology exclusions |

## Concept Tables

### Concept to MeSH or Emtree

| concept | term | tree note | explode? | rationale and source |
| --- | --- | --- | --- | --- |
| pediatric population | Child / child | core pediatric population | Yes | Protocol population states children and adolescents |
| pediatric population | Adolescent / adolescent | older pediatric subgroup | Yes | Protocol population states children and adolescents |
| sleep-disordered breathing spectrum | Sleep Apnea Syndromes / sleep disordered breathing | broad indexed representation for SDB | Yes | Protocol domain is sleep-disordered breathing in children |
| sleep-disordered breathing spectrum | Obstructive Sleep Apnea / obstructive sleep apnea | narrower indexed representation within SDB | Yes | Acceptable indexed subtype inside protocol-defined SDB spectrum |
| sleep-disordered breathing spectrum | Snoring / snoring | supports explicit primary snoring subgroup | Database dependent | Protocol subgroup analysis explicitly includes primary snoring |
| blood pressure outcomes | Blood Pressure / blood pressure | direct indexed representation of main outcome | Yes | Protocol main and additional outcomes center on blood pressure measures |

### Concept to Textword

| concept | synonym or phrase | field | truncation? | source |
| --- | --- | --- | --- | --- |
| sleep-disordered breathing spectrum | sleep-disordered breathing | title/abstract/topic | No | Protocol wording |
| sleep-disordered breathing spectrum | sleep disordered breathing | title/abstract/topic | No | Spelling variant from protocol wording |
| sleep-disordered breathing spectrum | sleep-related breathing disorder | title/abstract/topic | No | Protocol-compatible wording |
| sleep-disordered breathing spectrum | sleep related breathing disorder | title/abstract/topic | No | Protocol-compatible wording |
| sleep-disordered breathing spectrum | obstructive sleep apnea | title/abstract/topic | No | Domain-consistent subtype wording inside protocol SDB spectrum |
| sleep-disordered breathing spectrum | obstructive sleep apnoea | title/abstract/topic | No | Spelling variant |
| sleep-disordered breathing spectrum | primary snoring | title/abstract/topic | No | Explicit protocol subgroup |
| sleep-disordered breathing spectrum | OAHI | title/abstract/topic | No | Protocol-compatible precision term for severity framing |
| sleep-disordered breathing spectrum | obstructive apnea hypopnea index | title/abstract/topic | No | Expanded form of OAHI |
| blood pressure outcomes | blood pressure | title/abstract/topic | No | Protocol main outcome |
| blood pressure outcomes | systolic blood pressure | title/abstract/topic | No | Protocol main outcome |
| blood pressure outcomes | diastolic blood pressure | title/abstract/topic | No | Protocol main outcome |
| blood pressure outcomes | mean blood pressure | title/abstract/topic | No | Protocol main outcome |
| blood pressure outcomes | SBP | title/abstract/topic | No | Protocol outcome abbreviation |
| blood pressure outcomes | DBP | title/abstract/topic | No | Protocol outcome abbreviation |
| blood pressure outcomes | MBP | title/abstract/topic | No | Protocol outcome abbreviation |
| blood pressure outcomes | blood pressure load | title/abstract/topic | No | Protocol additional outcome |
| blood pressure outcomes | ambulatory blood pressure | title/abstract/topic | No | Protocol measurement description |
| blood pressure outcomes | non-dipping | title/abstract/topic | No | Protocol additional outcome |
| blood pressure outcomes | nondipp* | title/abstract/topic | Yes | Protocol additional outcome with lexical variation |
| pediatric population | child* | title/abstract/topic | Yes | Protocol population |
| pediatric population | adolescen* | title/abstract/topic | Yes | Protocol population |
| pediatric population | pediatric* | title/abstract/topic | Yes | Standard age wording |
| pediatric population | paediatric* | title/abstract/topic | Yes | Spelling variant |
| pediatric population | teen* | title/abstract/topic | Yes | Adolescent recall support |

## JSON Query Object

```json
{
  "pubmed": [
    "# Q1: High-recall\n((\"Sleep Apnea Syndromes\"[Mesh] OR \"Sleep Apnea, Obstructive\"[Mesh] OR \"Snoring\"[Mesh] OR \"sleep-disordered breathing\"[tiab] OR \"sleep disordered breathing\"[tiab] OR \"sleep-related breathing disorder\"[tiab] OR \"sleep related breathing disorder\"[tiab] OR \"obstructive sleep apnea\"[tiab] OR \"obstructive sleep apnoea\"[tiab] OR \"primary snoring\"[tiab]) AND (\"Blood Pressure\"[Mesh] OR \"blood pressure\"[tiab] OR \"systolic blood pressure\"[tiab] OR \"diastolic blood pressure\"[tiab] OR SBP[tiab] OR DBP[tiab] OR \"mean blood pressure\"[tiab] OR MBP[tiab] OR \"blood pressure load\"[tiab] OR \"ambulatory blood pressure\"[tiab] OR \"non-dipping\"[tiab] OR nondipp*[tiab]) AND (\"Child\"[Mesh] OR \"Adolescent\"[Mesh] OR child*[tiab] OR adolescen*[tiab] OR pediatric*[tiab] OR paediatric*[tiab] OR teen*[tiab]))",
    "# Q2: Balanced\n((\"Sleep Apnea Syndromes\"[Mesh] OR \"Sleep Apnea, Obstructive\"[Mesh] OR \"sleep-disordered breathing\"[tiab] OR \"sleep disordered breathing\"[tiab] OR \"obstructive sleep apnea\"[tiab] OR \"obstructive sleep apnoea\"[tiab] OR \"primary snoring\"[tiab] OR OAHI[tiab] OR \"obstructive apnea hypopnea index\"[tiab]) AND (\"Blood Pressure\"[Mesh] OR \"blood pressure\"[tiab] OR \"systolic blood pressure\"[tiab] OR \"diastolic blood pressure\"[tiab] OR SBP[tiab] OR DBP[tiab] OR \"ambulatory blood pressure\"[tiab] OR \"blood pressure load\"[tiab] OR \"non-dipping\"[tiab] OR nondipp*[tiab]) AND (\"Child\"[Mesh] OR \"Adolescent\"[Mesh] OR child*[tiab] OR adolescen*[tiab] OR pediatric*[tiab] OR paediatric*[tiab]))",
    "# Q3: High-precision\n(((\"Sleep Apnea Syndromes\"[Majr] OR \"Sleep Apnea, Obstructive\"[Majr]) OR \"sleep-disordered breathing\"[ti] OR \"obstructive sleep apnea\"[ti] OR \"obstructive sleep apnoea\"[ti]) AND (\"Blood Pressure\"[Majr] OR \"blood pressure\"[ti] OR \"systolic blood pressure\"[tiab] OR \"diastolic blood pressure\"[tiab] OR SBP[tiab] OR DBP[tiab]) AND (\"Child\"[Mesh] OR \"Adolescent\"[Mesh] OR child*[tiab] OR adolescen*[tiab] OR pediatric*[tiab] OR paediatric*[tiab]))",
    "# Q4: Balanced + scope_only\n(((\"sleep-disordered breathing\"[ti] OR \"sleep disordered breathing\"[ti] OR \"obstructive sleep apnea\"[ti] OR \"obstructive sleep apnoea\"[ti] OR \"primary snoring\"[ti]) OR \"Sleep Apnea Syndromes\"[Majr]) AND (\"blood pressure\"[ti] OR \"Blood Pressure\"[Majr] OR SBP[tiab] OR DBP[tiab]) AND (\"Child\"[Mesh] OR \"Adolescent\"[Mesh] OR child*[tiab] OR adolescen*[tiab] OR pediatric*[tiab] OR paediatric*[tiab]))",
    "# Q5: Balanced + proximity_or_scope_fallback\n(((\"sleep-disordered breathing\"[tiab] OR \"sleep disordered breathing\"[tiab] OR \"obstructive sleep apnea\"[tiab] OR \"obstructive sleep apnoea\"[tiab] OR \"primary snoring\"[tiab]) AND (\"blood pressure\"[tiab] OR \"systolic blood pressure\"[tiab] OR \"diastolic blood pressure\"[tiab] OR SBP[tiab] OR DBP[tiab] OR \"ambulatory blood pressure\"[tiab] OR \"blood pressure load\"[tiab] OR nondipp*[tiab])) AND (\"Child\"[Mesh] OR \"Adolescent\"[Mesh] OR child*[tiab] OR adolescen*[tiab] OR pediatric*[tiab] OR paediatric*[tiab]))",
    "# Q6: Balanced + design_plus_filter\n((((\"Sleep Apnea Syndromes\"[Mesh] OR \"Sleep Apnea, Obstructive\"[Mesh] OR \"sleep-disordered breathing\"[tiab] OR \"sleep disordered breathing\"[tiab] OR \"obstructive sleep apnea\"[tiab] OR \"obstructive sleep apnoea\"[tiab] OR \"primary snoring\"[tiab] OR OAHI[tiab] OR \"obstructive apnea hypopnea index\"[tiab]) AND (\"Blood Pressure\"[Mesh] OR \"blood pressure\"[tiab] OR \"systolic blood pressure\"[tiab] OR \"diastolic blood pressure\"[tiab] OR SBP[tiab] OR DBP[tiab] OR \"ambulatory blood pressure\"[tiab] OR \"blood pressure load\"[tiab] OR \"non-dipping\"[tiab] OR nondipp*[tiab]) AND (\"Child\"[Mesh] OR \"Adolescent\"[Mesh] OR child*[tiab] OR adolescen*[tiab] OR pediatric*[tiab] OR paediatric*[tiab])) AND english[Filter] AND humans[Filter] AND (cohort[tiab] OR longitudinal[tiab] OR observational[tiab] OR \"case-control\"[tiab] OR \"cross-sectional\"[tiab])) NOT (letter[pt] OR editorial[pt] OR comment[pt])"
  ],
  "scopus": [
    "# Q1: High-recall\nTITLE-ABS-KEY((\"sleep-disordered breathing\" OR \"sleep disordered breathing\" OR \"sleep-related breathing disorder\" OR \"sleep related breathing disorder\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\") AND (\"blood pressure\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR sbp OR dbp OR \"mean blood pressure\" OR mbp OR \"blood pressure load\" OR \"ambulatory blood pressure\" OR nondipp* OR \"non-dipping\") AND (child* OR adolescen* OR pediatric* OR paediatric* OR teen*))",
    "# Q2: Balanced\nTITLE-ABS-KEY((\"sleep-disordered breathing\" OR \"sleep disordered breathing\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\" OR oahi OR \"obstructive apnea hypopnea index\") AND (\"blood pressure\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR sbp OR dbp OR \"ambulatory blood pressure\" OR \"blood pressure load\" OR nondipp* OR \"non-dipping\") AND (child* OR adolescen* OR pediatric* OR paediatric*))",
    "# Q3: High-precision\nTITLE(\"sleep-disordered breathing\" OR \"sleep disordered breathing\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\") AND TITLE-ABS-KEY(\"blood pressure\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR sbp OR dbp) AND TITLE-ABS-KEY(child* OR adolescen* OR pediatric* OR paediatric*)",
    "# Q4: Balanced + scope_only\nTITLE(\"sleep-disordered breathing\" OR \"sleep disordered breathing\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\") AND TITLE(\"blood pressure\") AND TITLE-ABS-KEY(child* OR adolescen* OR pediatric* OR paediatric*)",
    "# Q5: Balanced + proximity_or_scope_fallback\nTITLE-ABS-KEY(((sleep W/3 breathing) OR (sleep W/2 apnea*) OR (sleep W/2 apnoea*) OR (primary W/1 snoring) OR oahi) AND (\"blood pressure\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR sbp OR dbp OR \"ambulatory blood pressure\" OR \"blood pressure load\" OR nondipp*) AND (child* OR adolescen* OR pediatric* OR paediatric*))",
    "# Q6: Balanced + design_plus_filter\nTITLE-ABS-KEY((\"sleep-disordered breathing\" OR \"sleep disordered breathing\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\" OR oahi OR \"obstructive apnea hypopnea index\") AND (\"blood pressure\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR sbp OR dbp OR \"ambulatory blood pressure\" OR \"blood pressure load\" OR nondipp* OR \"non-dipping\") AND (child* OR adolescen* OR pediatric* OR paediatric*)) AND TITLE-ABS-KEY(cohort OR longitudinal OR observational OR \"case-control\" OR \"cross-sectional\") AND DOCTYPE(ar)"
  ],
  "wos": [
    "# Q1: High-recall\nTS=((\"sleep-disordered breathing\" OR \"sleep disordered breathing\" OR \"sleep-related breathing disorder\" OR \"sleep related breathing disorder\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\") AND (\"blood pressure\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR SBP OR DBP OR \"mean blood pressure\" OR MBP OR \"blood pressure load\" OR \"ambulatory blood pressure\" OR nondipp* OR \"non-dipping\") AND (child* OR adolescen* OR pediatric* OR paediatric* OR teen*))",
    "# Q2: Balanced\nTS=((\"sleep-disordered breathing\" OR \"sleep disordered breathing\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\" OR OAHI OR \"obstructive apnea hypopnea index\") AND (\"blood pressure\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR SBP OR DBP OR \"ambulatory blood pressure\" OR \"blood pressure load\" OR nondipp* OR \"non-dipping\") AND (child* OR adolescen* OR pediatric* OR paediatric*))",
    "# Q3: High-precision\nTI=(\"sleep-disordered breathing\" OR \"sleep disordered breathing\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\") AND TS=(\"blood pressure\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR SBP OR DBP) AND TS=(child* OR adolescen* OR pediatric* OR paediatric*)",
    "# Q4: Balanced + scope_only\nTI=(\"sleep-disordered breathing\" OR \"sleep disordered breathing\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\") AND TI=(\"blood pressure\") AND TS=(child* OR adolescen* OR pediatric* OR paediatric*)",
    "# Q5: Balanced + proximity_or_scope_fallback\nTS=(((sleep NEAR/3 breathing) OR (sleep NEAR/2 apnea*) OR (sleep NEAR/2 apnoea*) OR (primary NEAR/1 snoring) OR OAHI) AND (\"blood pressure\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR SBP OR DBP OR \"ambulatory blood pressure\" OR \"blood pressure load\" OR nondipp*) AND (child* OR adolescen* OR pediatric* OR paediatric*))",
    "# Q6: Balanced + design_plus_filter\nTS=((\"sleep-disordered breathing\" OR \"sleep disordered breathing\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"primary snoring\" OR OAHI OR \"obstructive apnea hypopnea index\") AND (\"blood pressure\" OR \"systolic blood pressure\" OR \"diastolic blood pressure\" OR SBP OR DBP OR \"ambulatory blood pressure\" OR \"blood pressure load\" OR nondipp* OR \"non-dipping\") AND (child* OR adolescen* OR pediatric* OR paediatric*)) AND TS=(cohort OR longitudinal OR observational OR \"case-control\" OR \"cross-sectional\") AND DT=(Article)"
  ],
  "embase": [
    "# Q1: High-recall\n('sleep disordered breathing'/exp OR 'obstructive sleep apnea'/exp OR 'snoring'/exp OR 'sleep-disordered breathing':ti,ab OR 'sleep disordered breathing':ti,ab OR 'sleep-related breathing disorder':ti,ab OR 'sleep related breathing disorder':ti,ab OR 'obstructive sleep apnea':ti,ab OR 'obstructive sleep apnoea':ti,ab OR 'primary snoring':ti,ab) AND ('blood pressure'/exp OR 'blood pressure':ti,ab OR 'systolic blood pressure':ti,ab OR 'diastolic blood pressure':ti,ab OR sbp:ti,ab OR dbp:ti,ab OR 'mean blood pressure':ti,ab OR mbp:ti,ab OR 'blood pressure load':ti,ab OR 'ambulatory blood pressure':ti,ab OR 'non-dipping':ti,ab OR nondipp*:ti,ab) AND ('child'/exp OR 'adolescent'/exp OR child*:ti,ab OR adolescen*:ti,ab OR pediatric*:ti,ab OR paediatric*:ti,ab OR teen*:ti,ab)",
    "# Q2: Balanced\n('sleep disordered breathing'/exp OR 'obstructive sleep apnea'/exp OR 'sleep-disordered breathing':ti,ab OR 'sleep disordered breathing':ti,ab OR 'obstructive sleep apnea':ti,ab OR 'obstructive sleep apnoea':ti,ab OR 'primary snoring':ti,ab OR oahi:ti,ab OR 'obstructive apnea hypopnea index':ti,ab) AND ('blood pressure'/exp OR 'blood pressure':ti,ab OR 'systolic blood pressure':ti,ab OR 'diastolic blood pressure':ti,ab OR sbp:ti,ab OR dbp:ti,ab OR 'ambulatory blood pressure':ti,ab OR 'blood pressure load':ti,ab OR 'non-dipping':ti,ab OR nondipp*:ti,ab) AND ('child'/exp OR 'adolescent'/exp OR child*:ti,ab OR adolescen*:ti,ab OR pediatric*:ti,ab OR paediatric*:ti,ab)",
    "# Q3: High-precision\n(('sleep disordered breathing'/mj OR 'obstructive sleep apnea'/mj OR 'sleep-disordered breathing':ti OR 'sleep disordered breathing':ti OR 'obstructive sleep apnea':ti OR 'obstructive sleep apnoea':ti) AND ('blood pressure'/mj OR 'blood pressure':ti OR 'systolic blood pressure':ti,ab OR 'diastolic blood pressure':ti,ab OR sbp:ti,ab OR dbp:ti,ab) AND ('child'/exp OR 'adolescent'/exp OR child*:ti,ab OR adolescen*:ti,ab OR pediatric*:ti,ab OR paediatric*:ti,ab))",
    "# Q4: Balanced + scope_only\n(('sleep-disordered breathing':ti OR 'sleep disordered breathing':ti OR 'obstructive sleep apnea':ti OR 'obstructive sleep apnoea':ti OR 'primary snoring':ti) AND ('blood pressure':ti OR 'blood pressure'/mj OR sbp:ti,ab OR dbp:ti,ab) AND ('child'/exp OR 'adolescent'/exp OR child*:ti,ab OR adolescen*:ti,ab OR pediatric*:ti,ab OR paediatric*:ti,ab))",
    "# Q5: Balanced + proximity_or_scope_fallback\n(((sleep ADJ3 breathing):ti,ab OR (sleep ADJ2 apnea*):ti,ab OR (sleep ADJ2 apnoea*):ti,ab OR (primary ADJ1 snoring):ti,ab OR oahi:ti,ab) AND ('blood pressure':ti,ab OR 'systolic blood pressure':ti,ab OR 'diastolic blood pressure':ti,ab OR sbp:ti,ab OR dbp:ti,ab OR 'ambulatory blood pressure':ti,ab OR 'blood pressure load':ti,ab OR nondipp*:ti,ab) AND ('child'/exp OR 'adolescent'/exp OR child*:ti,ab OR adolescen*:ti,ab OR pediatric*:ti,ab OR paediatric*:ti,ab))",
    "# Q6: Balanced + design_plus_filter\n(('sleep disordered breathing'/exp OR 'obstructive sleep apnea'/exp OR 'sleep-disordered breathing':ti,ab OR 'sleep disordered breathing':ti,ab OR 'obstructive sleep apnea':ti,ab OR 'obstructive sleep apnoea':ti,ab OR 'primary snoring':ti,ab OR oahi:ti,ab OR 'obstructive apnea hypopnea index':ti,ab) AND ('blood pressure'/exp OR 'blood pressure':ti,ab OR 'systolic blood pressure':ti,ab OR 'diastolic blood pressure':ti,ab OR sbp:ti,ab OR dbp:ti,ab OR 'ambulatory blood pressure':ti,ab OR 'blood pressure load':ti,ab OR 'non-dipping':ti,ab OR nondipp*:ti,ab) AND ('child'/exp OR 'adolescent'/exp OR child*:ti,ab OR adolescen*:ti,ab OR pediatric*:ti,ab OR paediatric*:ti,ab) AND (cohort:ti,ab OR longitudinal:ti,ab OR observational:ti,ab OR 'case-control':ti,ab OR 'cross-sectional':ti,ab))"
  ]
}
```

## PRESS Self-Check

```json
{
  "json_patch": {}
}
```

- Q1 and Q2 preserve the same mandatory-core block structure across all databases.
- Comparator language, congenital-heart-disease exclusion, and post-intervention exclusion were kept out of baseline retrieval because the protocol presents them as eligibility restrictions rather than subject-matter concepts.
- Q4 to Q6 use only approved bundled cases.
- No inline publication-date limits were added because the protocol states no date restriction.
- Embase queries use Embase.com syntax consistently.

## Translation Notes

- The protocol supports a `single_route` architecture because it defines one coherent AND structure: pediatric population plus sleep-disordered breathing plus blood pressure outcomes.
- `design_analytic_block` stays active by rule, but the protocol supports only conservative use of design and filter restrictions; these are therefore confined to bundled precision variants rather than baseline Q1.
- `primary snoring` is retained because it is an explicit planned subgroup within the protocol-defined SDB spectrum.
- Healthy-control wording is not used as a mandatory retrieval block because it is more safely enforced during screening.
- English-language restriction is explicit in the protocol but remains `filter_only` to avoid overconstraining baseline retrieval.