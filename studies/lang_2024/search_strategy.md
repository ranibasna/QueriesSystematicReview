# Search Strategy for lang_2024

## Study Summary

- Topic: Short sleep duration and incident obesity in adults, with sex-specific or sex-stratified estimates
- Date window: Database inception to January 2023; inline publication-date restriction is omitted so the protocol end date can be applied in the database interface if needed
- Databases: pubmed, scopus, wos, embase
- Query level: extended
- Retrieval architecture: single_route
- design_analytic_block: active, but populated conservatively and reserved for bundled precision variants

## PICOS Summary

- Population: Adults aged 18 years or older in the general population
- Intervention or Exposure: Sleep duration or sleep quantity measured at baseline, especially short sleep duration
- Comparator: Men versus women, or studies reporting sex-stratified estimates that allow comparison
- Outcomes: Incident obesity, new obesity, changes in body mass index, and BMI z-scores
- Design: Longitudinal cohort evidence, primarily prospective cohort studies, with later protocol broadening to retrospective cohorts that preserve baseline exposure before outcome onset

## Architecture Selection Summary

- Selected retrieval architecture: `single_route`
- `design_analytic_block`: active
- Rationale: The protocol supports one coherent retrieval route that combines a sleep-duration exposure block with an obesity-outcome block. Sex-specific reporting and longitudinal design are explicit review targets, but they are safer as precision layers than as baseline mandatory concepts because relevant cohort studies may not foreground those features consistently in titles or abstracts.

### Concept Roles

| Role | Assigned concepts |
| --- | --- |
| mandatory_core | sleep duration or short sleep exposure; obesity or adiposity outcome |
| optional_precision | sex-difference or sex-stratified wording; adult population wording; incident-obesity and BMI-change phrasing; tighter title-only scope; proximity tightening where supported |
| filter_only | humans or article-type limits where platform-safe; cohort, longitudinal, prospective, or retrospective design labels when used as later precision layers |
| screening_only | exclusions for children, patient populations, shift workers, pre-diagnosed sleep disorders, unpublished studies, and exact minimum follow-up thresholds |

## Concept Tables

### Concept to MeSH or Emtree

| concept | term | tree note | explode? | rationale and source |
| --- | --- | --- | --- | --- |
| Sleep-duration exposure | Sleep / sleep | Broad indexed representation of the protocol exposure domain | Yes | Protocol title, objective, and exposure definition |
| Sleep-duration exposure | Sleep Deprivation / sleep deprivation | Indexed support for short or insufficient sleep framing | Yes | Protocol focus on short sleep duration |
| Obesity outcome | Obesity / obesity | Core indexed representation of the main outcome | Yes | Protocol condition and main outcome |
| Obesity outcome | Overweight / overweight | Indexed support because obesity and overweight framing appear in keywords | Yes | Protocol keywords |
| Obesity outcome | Body Mass Index / body mass index | Indexed support for BMI and BMI z-score outcomes | Yes | Protocol main outcomes |
| Adult precision | Adult / adult | Indexed age-group restriction used as a low-risk precision layer | Yes | Protocol population |
| Sex precision | Sex Factors / sex factor | Indexed support for sex-specific analysis | Yes | Protocol objective and comparator |

### Concept to Textword

| concept | synonym or phrase | field | truncation? | source |
| --- | --- | --- | --- | --- |
| Sleep-duration exposure | sleep duration | title/abstract/topic | No | Explicit protocol wording |
| Sleep-duration exposure | short sleep; short sleep duration | title/abstract/topic | No | Protocol title and objective |
| Sleep-duration exposure | sleep quantity | title/abstract/topic | No | Explicit protocol exposure wording |
| Sleep-duration exposure | habitual sleep duration | title/abstract/topic | No | Protocol-compatible exposure wording |
| Sleep-duration exposure | total sleep time | title/abstract/topic | No | Protocol-compatible sleep-duration wording |
| Sleep-duration exposure | insufficient sleep; sleep curtailment | title/abstract/topic | No | Protocol-compatible short-sleep wording |
| Obesity outcome | obesity; overweight | title/abstract/topic | No | Protocol keywords and outcome framing |
| Obesity outcome | incident obesity; obesity incidence; new obesity | title/abstract/topic | No | Protocol primary outcome |
| Obesity outcome | body mass index; BMI; BMI z-score; BMI z-scores | title/abstract/topic | Mixed | Protocol primary outcome |
| Obesity outcome | weight gain; adiposity | title/abstract/topic | No | Protocol-compatible obesity-outcome wording |
| Sex precision | sex difference*; sex-specific; sex stratified; sex-stratified | title/abstract/topic | Mixed | Protocol objective |
| Sex precision | gender difference*; male; female; men; women | title/abstract/topic | Mixed | Protocol comparator wording |
| Adult precision | adult* | title/abstract/topic | Yes | Explicit protocol population |
| Design block | cohort; longitudinal; prospective; retrospective; follow-up; incident | title/abstract/topic | No | Explicit protocol study-design and outcome timing |

## JSON Query Object

```json
{
  "pubmed": [
    "# Q1: High-recall\n((\"Sleep\"[Mesh] OR \"Sleep Deprivation\"[Mesh] OR \"sleep duration\"[tiab] OR \"short sleep\"[tiab] OR \"short sleep duration\"[tiab] OR \"sleep quantity\"[tiab] OR \"habitual sleep duration\"[tiab] OR \"total sleep time\"[tiab] OR \"insufficient sleep\"[tiab] OR \"sleep curtailment\"[tiab]) AND (\"Obesity\"[Mesh] OR \"Overweight\"[Mesh] OR \"Body Mass Index\"[Mesh] OR obesity[tiab] OR overweight[tiab] OR \"body mass index\"[tiab] OR BMI[tiab] OR \"BMI z-score\"[tiab] OR \"BMI z-scores\"[tiab] OR \"weight gain\"[tiab] OR adiposity[tiab]))",
    "# Q2: Balanced\n((\"Sleep\"[Mesh] OR \"Sleep Deprivation\"[Mesh] OR \"sleep duration\"[tiab] OR \"short sleep\"[tiab] OR \"short sleep duration\"[tiab] OR \"sleep quantity\"[tiab] OR \"habitual sleep duration\"[tiab] OR \"total sleep time\"[tiab] OR \"insufficient sleep\"[tiab]) AND (\"Obesity\"[Mesh] OR \"Overweight\"[Mesh] OR \"Body Mass Index\"[Mesh] OR obesity[tiab] OR overweight[tiab] OR \"incident obesity\"[tiab] OR \"obesity incidence\"[tiab] OR \"new obesity\"[tiab] OR \"body mass index\"[tiab] OR BMI[tiab] OR \"weight gain\"[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab]) AND (\"Sex Factors\"[Mesh] OR sex[tiab] OR gender[tiab] OR male[tiab] OR female[tiab] OR men[tiab] OR women[tiab] OR \"sex-specific\"[tiab] OR \"sex stratified\"[tiab] OR \"sex-stratified\"[tiab]))",
    "# Q3: High-precision\n(((\"Sleep\"[Majr] OR \"sleep duration\"[ti] OR \"short sleep\"[ti] OR \"short sleep duration\"[ti] OR \"sleep quantity\"[ti] OR \"total sleep time\"[ti]) AND (\"Obesity\"[Majr] OR obesity[ti] OR overweight[ti] OR \"incident obesity\"[tiab] OR \"body mass index\"[tiab] OR BMI[tiab])) AND (\"Adult\"[Mesh] OR adult*[tiab]) AND (\"Sex Factors\"[Mesh] OR sex[tiab] OR gender[tiab] OR male[tiab] OR female[tiab] OR men[tiab] OR women[tiab]))",
    "# Q4: Balanced + scope_only\n((\"sleep duration\"[ti] OR \"short sleep\"[ti] OR \"short sleep duration\"[ti] OR \"sleep quantity\"[ti] OR \"total sleep time\"[ti]) AND (obesity[ti] OR overweight[ti] OR \"incident obesity\"[ti] OR \"body mass index\"[ti] OR BMI[ti]) AND (adult*[tiab]) AND (sex[tiab] OR gender[tiab] OR male[tiab] OR female[tiab] OR men[tiab] OR women[tiab]))",
    "# Q5: Balanced + proximity_or_scope_fallback\n(((\"sleep duration\"[ti] OR \"short sleep\"[ti] OR \"short sleep duration\"[ti] OR \"sleep quantity\"[ti] OR \"total sleep time\"[ti] OR \"insufficient sleep\"[ti]) AND (obesity[ti] OR overweight[ti] OR \"incident obesity\"[ti] OR \"body mass index\"[ti] OR BMI[ti] OR \"weight gain\"[ti])) AND (adult*[tiab]) AND (sex[tiab] OR gender[tiab] OR male[tiab] OR female[tiab] OR men[tiab] OR women[tiab]))",
    "# Q6: Balanced + design_plus_filter\n((((\"Sleep\"[Mesh] OR \"Sleep Deprivation\"[Mesh] OR \"sleep duration\"[tiab] OR \"short sleep\"[tiab] OR \"short sleep duration\"[tiab] OR \"sleep quantity\"[tiab] OR \"habitual sleep duration\"[tiab] OR \"total sleep time\"[tiab] OR \"insufficient sleep\"[tiab]) AND (\"Obesity\"[Mesh] OR \"Overweight\"[Mesh] OR \"Body Mass Index\"[Mesh] OR obesity[tiab] OR overweight[tiab] OR \"incident obesity\"[tiab] OR \"obesity incidence\"[tiab] OR \"new obesity\"[tiab] OR \"body mass index\"[tiab] OR BMI[tiab] OR \"weight gain\"[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab]) AND (\"Sex Factors\"[Mesh] OR sex[tiab] OR gender[tiab] OR male[tiab] OR female[tiab] OR men[tiab] OR women[tiab] OR \"sex-specific\"[tiab] OR \"sex stratified\"[tiab] OR \"sex-stratified\"[tiab])) AND (cohort[tiab] OR longitudinal[tiab] OR prospective[tiab] OR retrospective[tiab] OR \"follow-up\"[tiab] OR incident[tiab])) AND humans[Filter]) NOT (review[pt] OR meta-analysis[pt] OR letter[pt] OR editorial[pt] OR comment[pt])"
  ],
  "scopus": [
    "# Q1: High-recall\nTITLE-ABS-KEY((\"sleep duration\" OR \"short sleep\" OR \"short sleep duration\" OR \"sleep quantity\" OR \"habitual sleep duration\" OR \"total sleep time\" OR \"insufficient sleep\" OR \"sleep curtailment\") AND (obesity OR overweight OR \"body mass index\" OR BMI OR \"BMI z-score\" OR \"BMI z-scores\" OR \"weight gain\" OR adiposity))",
    "# Q2: Balanced\nTITLE-ABS-KEY((\"sleep duration\" OR \"short sleep\" OR \"short sleep duration\" OR \"sleep quantity\" OR \"habitual sleep duration\" OR \"total sleep time\" OR \"insufficient sleep\") AND (obesity OR overweight OR \"incident obesity\" OR \"obesity incidence\" OR \"new obesity\" OR \"body mass index\" OR BMI OR \"weight gain\") AND (adult*) AND (sex OR gender OR male OR female OR men OR women OR \"sex-specific\" OR \"sex stratified\" OR \"sex-stratified\"))",
    "# Q3: High-precision\nTITLE(\"sleep duration\" OR \"short sleep\" OR \"short sleep duration\" OR \"sleep quantity\" OR \"total sleep time\") AND TITLE-ABS-KEY(obesity OR overweight OR \"incident obesity\" OR \"body mass index\" OR BMI) AND TITLE-ABS-KEY(adult*) AND TITLE-ABS-KEY(sex OR gender OR male OR female OR men OR women) AND DOCTYPE(ar)",
    "# Q4: Balanced + scope_only\nTITLE(\"sleep duration\" OR \"short sleep\" OR \"short sleep duration\" OR \"sleep quantity\" OR \"total sleep time\") AND TITLE(obesity OR overweight OR \"incident obesity\" OR \"body mass index\" OR BMI) AND TITLE-ABS-KEY(adult*) AND TITLE-ABS-KEY(sex OR gender OR male OR female OR men OR women)",
    "# Q5: Balanced + proximity_or_scope_fallback\nTITLE-ABS-KEY((((\"short sleep\" OR \"short sleep duration\" OR \"sleep duration\" OR \"sleep quantity\" OR \"total sleep time\") W/5 (obesity OR overweight OR \"body mass index\" OR BMI OR \"weight gain\")) AND adult* AND (sex OR gender OR male OR female OR men OR women OR \"sex-specific\")))",
    "# Q6: Balanced + design_plus_filter\nTITLE-ABS-KEY((\"sleep duration\" OR \"short sleep\" OR \"short sleep duration\" OR \"sleep quantity\" OR \"habitual sleep duration\" OR \"total sleep time\" OR \"insufficient sleep\") AND (obesity OR overweight OR \"incident obesity\" OR \"obesity incidence\" OR \"new obesity\" OR \"body mass index\" OR BMI OR \"weight gain\") AND adult* AND (sex OR gender OR male OR female OR men OR women OR \"sex-specific\" OR \"sex stratified\" OR \"sex-stratified\") AND (cohort OR longitudinal OR prospective OR retrospective OR \"follow-up\" OR incident)) AND DOCTYPE(ar)"
  ],
  "wos": [
    "# Q1: High-recall\nTS=((\"sleep duration\" OR \"short sleep\" OR \"short sleep duration\" OR \"sleep quantity\" OR \"habitual sleep duration\" OR \"total sleep time\" OR \"insufficient sleep\" OR \"sleep curtailment\") AND (obesity OR overweight OR \"body mass index\" OR BMI OR \"BMI z-score\" OR \"BMI z-scores\" OR \"weight gain\" OR adiposity))",
    "# Q2: Balanced\nTS=((\"sleep duration\" OR \"short sleep\" OR \"short sleep duration\" OR \"sleep quantity\" OR \"habitual sleep duration\" OR \"total sleep time\" OR \"insufficient sleep\") AND (obesity OR overweight OR \"incident obesity\" OR \"obesity incidence\" OR \"new obesity\" OR \"body mass index\" OR BMI OR \"weight gain\") AND (adult*) AND (sex OR gender OR male OR female OR men OR women OR \"sex-specific\" OR \"sex stratified\" OR \"sex-stratified\"))",
    "# Q3: High-precision\nTI=(\"sleep duration\" OR \"short sleep\" OR \"short sleep duration\" OR \"sleep quantity\" OR \"total sleep time\") AND TS=(obesity OR overweight OR \"incident obesity\" OR \"body mass index\" OR BMI) AND TS=(adult*) AND TS=(sex OR gender OR male OR female OR men OR women) AND DT=(Article)",
    "# Q4: Balanced + scope_only\nTI=(\"sleep duration\" OR \"short sleep\" OR \"short sleep duration\" OR \"sleep quantity\" OR \"total sleep time\") AND TI=(obesity OR overweight OR \"incident obesity\" OR \"body mass index\" OR BMI) AND TS=(adult*) AND TS=(sex OR gender OR male OR female OR men OR women)",
    "# Q5: Balanced + proximity_or_scope_fallback\nTS=((((\"short sleep\" OR \"short sleep duration\" OR \"sleep duration\" OR \"sleep quantity\" OR \"total sleep time\") NEAR/5 (obesity OR overweight OR \"body mass index\" OR BMI OR \"weight gain\")) AND adult* AND (sex OR gender OR male OR female OR men OR women OR \"sex-specific\")))",
    "# Q6: Balanced + design_plus_filter\nTS=((\"sleep duration\" OR \"short sleep\" OR \"short sleep duration\" OR \"sleep quantity\" OR \"habitual sleep duration\" OR \"total sleep time\" OR \"insufficient sleep\") AND (obesity OR overweight OR \"incident obesity\" OR \"obesity incidence\" OR \"new obesity\" OR \"body mass index\" OR BMI OR \"weight gain\") AND adult* AND (sex OR gender OR male OR female OR men OR women OR \"sex-specific\" OR \"sex stratified\" OR \"sex-stratified\") AND (cohort OR longitudinal OR prospective OR retrospective OR \"follow-up\" OR incident)) AND DT=(Article)"
  ],
  "embase": [
    "# Q1: High-recall\n(('sleep'/exp OR 'sleep deprivation'/exp OR 'sleep duration':ti,ab OR 'short sleep':ti,ab OR 'short sleep duration':ti,ab OR 'sleep quantity':ti,ab OR 'habitual sleep duration':ti,ab OR 'total sleep time':ti,ab OR 'insufficient sleep':ti,ab OR 'sleep curtailment':ti,ab) AND ('obesity'/exp OR 'overweight'/exp OR 'body mass index'/exp OR obesity:ti,ab OR overweight:ti,ab OR 'body mass index':ti,ab OR bmi:ti,ab OR 'bmi z-score':ti,ab OR 'bmi z-scores':ti,ab OR 'weight gain':ti,ab OR adiposity:ti,ab))",
    "# Q2: Balanced\n(('sleep'/exp OR 'sleep deprivation'/exp OR 'sleep duration':ti,ab OR 'short sleep':ti,ab OR 'short sleep duration':ti,ab OR 'sleep quantity':ti,ab OR 'habitual sleep duration':ti,ab OR 'total sleep time':ti,ab OR 'insufficient sleep':ti,ab) AND ('obesity'/exp OR 'overweight'/exp OR 'body mass index'/exp OR obesity:ti,ab OR overweight:ti,ab OR 'incident obesity':ti,ab OR 'obesity incidence':ti,ab OR 'new obesity':ti,ab OR 'body mass index':ti,ab OR bmi:ti,ab OR 'weight gain':ti,ab) AND ('adult'/exp OR adult*:ti,ab) AND ('sex factor'/exp OR sex:ti,ab OR gender:ti,ab OR male:ti,ab OR female:ti,ab OR men:ti,ab OR women:ti,ab OR 'sex-specific':ti,ab OR 'sex stratified':ti,ab OR 'sex-stratified':ti,ab))",
    "# Q3: High-precision\n((('sleep'/mj OR 'sleep duration':ti OR 'short sleep':ti OR 'short sleep duration':ti OR 'sleep quantity':ti OR 'total sleep time':ti) AND ('obesity'/mj OR obesity:ti OR overweight:ti OR 'incident obesity':ti,ab OR 'body mass index':ti,ab OR bmi:ti,ab)) AND ('adult'/exp OR adult*:ti,ab) AND ('sex factor'/exp OR sex:ti,ab OR gender:ti,ab OR male:ti,ab OR female:ti,ab OR men:ti,ab OR women:ti,ab))",
    "# Q4: Balanced + scope_only\n(('sleep duration':ti OR 'short sleep':ti OR 'short sleep duration':ti OR 'sleep quantity':ti OR 'total sleep time':ti) AND (obesity:ti OR overweight:ti OR 'incident obesity':ti OR 'body mass index':ti OR bmi:ti) AND ('adult'/exp OR adult*:ti,ab) AND (sex:ti,ab OR gender:ti,ab OR male:ti,ab OR female:ti,ab OR men:ti,ab OR women:ti,ab))",
    "# Q5: Balanced + proximity_or_scope_fallback\n((((('short sleep' OR 'short sleep duration' OR 'sleep duration' OR 'sleep quantity' OR 'total sleep time') ADJ5 (obesity OR overweight OR 'body mass index' OR bmi OR 'weight gain')):ti,ab AND ('adult'/exp OR adult*:ti,ab) AND (sex:ti,ab OR gender:ti,ab OR male:ti,ab OR female:ti,ab OR men:ti,ab OR women:ti,ab OR 'sex-specific':ti,ab)))",
    "# Q6: Balanced + design_plus_filter\n((('sleep'/exp OR 'sleep deprivation'/exp OR 'sleep duration':ti,ab OR 'short sleep':ti,ab OR 'short sleep duration':ti,ab OR 'sleep quantity':ti,ab OR 'habitual sleep duration':ti,ab OR 'total sleep time':ti,ab OR 'insufficient sleep':ti,ab) AND ('obesity'/exp OR 'overweight'/exp OR 'body mass index'/exp OR obesity:ti,ab OR overweight:ti,ab OR 'incident obesity':ti,ab OR 'obesity incidence':ti,ab OR 'new obesity':ti,ab OR 'body mass index':ti,ab OR bmi:ti,ab OR 'weight gain':ti,ab) AND ('adult'/exp OR adult*:ti,ab) AND ('sex factor'/exp OR sex:ti,ab OR gender:ti,ab OR male:ti,ab OR female:ti,ab OR men:ti,ab OR women:ti,ab OR 'sex-specific':ti,ab OR 'sex stratified':ti,ab OR 'sex-stratified':ti,ab) AND (cohort:ti,ab OR longitudinal:ti,ab OR prospective:ti,ab OR retrospective:ti,ab OR 'follow-up':ti,ab OR incident:ti,ab)))"
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

- Q1 and Q2 preserve the same mandatory-core route across all databases: sleep-duration exposure AND obesity outcome.
- Sex-specific reporting and adult-population wording are explicit in the protocol, but they were kept out of Q1 to avoid unnecessary recall loss and introduced as conservative precision layers from Q2 onward.
- The bundled variants use only approved cases: `scope_only`, `proximity_or_scope_fallback`, and `design_plus_filter`.
- Longitudinal, prospective, retrospective, follow-up, and incident wording were reserved for the design-plus-filter variant because relevant cohort studies do not always advertise those labels consistently in titles or abstracts.
- Embase is translated in Embase.com / Elsevier syntax consistently.# Search Strategy for lang_2024

## Architecture Selection Summary

- Selected retrieval architecture: `single_route`
- `design_analytic_block`: active
- Date window: inception through January 2023
- Relaxation profile used for baseline generation: `recall_soft`

| Role | Concepts |
| --- | --- |
| mandatory_core | Short sleep duration or reduced sleep quantity; obesity or overweight outcomes |
| optional_precision | Sex comparison terms; BMI wording; tighter title scope |
| filter_only | English-language limit; humans limit; article-only or document-type limits where platform-safe |
| screening_only | General-population framing, exclusion of shift-work and sleep-disorder populations, exact follow-up threshold, separate extractability of male and female estimates |

The protocol supports one coherent Boolean route rather than separate indexed and textword routes, so `single_route` is the safer fit. The active `design_analytic_block` is limited to adult longitudinal cohort or incidence language because those are explicit eligibility constraints that shape retrieval without forcing protocol exclusions that are better handled during screening.

## Concept Tables (Markdown)

### Concept to MeSH or Emtree Table

| concept | term | tree note | explode? | rationale and source |
| --- | --- | --- | --- | --- |
| Sleep exposure | Sleep / sleep | Broad indexed sleep concept when duration wording is not indexed separately | Yes | Protocol title and keyword `Sleep duration`; MeSH listed in PROSPERO record |
| Sleep exposure | Sleep Deprivation / sleep deprivation | Closest indexed analogue to short or insufficient sleep exposure | Yes | Protocol exposure is short sleep duration or quantity |
| Obesity outcome | Obesity / obesity | Core adiposity outcome term | Yes | Protocol condition and primary outcome are obesity incidence and BMI change |
| Obesity outcome | Overweight / overweight | Adjacent indexed adiposity term often paired with obesity | Yes | Protocol keywords include overweight and BMI-related outcomes |
| Design block | Cohort Studies / cohort analysis | Core longitudinal observational design concept | Yes | Protocol includes longitudinal cohort studies only |
| Design block | Prospective Studies / prospective study | Prospective longitudinal indexing support | Yes | Protocol names prospective studies explicitly and later broadens to retrospective cohorts |
| Population block | Adult / adult | Adult population limiter | No | Protocol restricts to adults aged 18 years or older |

### Concept to textword Table

| concept | synonym or phrase | field | truncation? | source |
| --- | --- | --- | --- | --- |
| Sleep exposure | `sleep duration` | ti,ab or topic | No | Protocol title and keywords |
| Sleep exposure | `sleep quantity` | ti,ab or topic | No | Protocol exposure definition |
| Sleep exposure | `short sleep` | ti,ab or topic | No | Protocol title and objective |
| Sleep exposure | `short sleep duration` | ti,ab or topic | No | Protocol title |
| Sleep exposure | `insufficient sleep` | ti,ab or topic | No | Conservative protocol-consistent variant for reduced sleep quantity |
| Sleep exposure | `sleep restriction` | ti,ab or topic | No | Conservative protocol-consistent variant for reduced sleep quantity |
| Sleep exposure | `reduced sleep` | ti,ab or topic | No | Conservative protocol-consistent variant for reduced sleep quantity |
| Obesity outcome | `obes*` | ti,ab or topic | Yes | Protocol condition obesity |
| Obesity outcome | `overweight` | ti,ab or topic | No | Protocol keywords |
| Obesity outcome | `adiposity` | ti,ab or topic | No | Outcome-adjacent wording consistent with obesity phenotype description |
| Obesity outcome | `body mass index` | ti,ab or topic | No | Primary and secondary outcomes mention BMI |
| Obesity outcome | `BMI` | ti,ab or topic | No | Protocol outcomes |
| Obesity outcome | `weight gain` | ti,ab or topic | No | Conservative outcome wording tied to obesity incidence context |
| Optional precision | `sex`, `gender`, `male`, `female`, `men`, `women` | ti,ab or topic | No | Protocol objective and comparator section |
| Optional precision | `sex difference*`, `sex-specific` | ti,ab or topic | Yes | Protocol review title |
| Design block | `cohort`, `longitudinal`, `prospective`, `retrospective`, `incidence`, `follow-up` | ti,ab or topic | No | Protocol study design and synthesis sections |
| Population block | `adult*` | ti,ab or topic | Yes | Protocol population definition |

## JSON Query Object

```json
{
	"pubmed": [
		"# Q1: High-recall\n((\"Sleep\"[Mesh] OR \"Sleep Deprivation\"[Mesh] OR \"sleep duration\"[tiab] OR \"sleep quantity\"[tiab] OR \"short sleep\"[tiab] OR \"short sleep duration\"[tiab] OR \"insufficient sleep\"[tiab] OR \"sleep restriction\"[tiab] OR \"reduced sleep\"[tiab]) AND (\"Obesity\"[Mesh] OR \"Overweight\"[Mesh] OR obes*[tiab] OR overweight[tiab] OR adiposity[tiab] OR \"body mass index\"[tiab] OR BMI[tiab] OR \"weight gain\"[tiab]) AND (\"Cohort Studies\"[Mesh] OR \"Prospective Studies\"[Mesh] OR cohort[tiab] OR longitudinal[tiab] OR prospective[tiab] OR retrospective[tiab] OR incidence[tiab] OR \"follow-up\"[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab])) AND (\"1900/01/01\"[Date - Publication] : \"2023/01/31\"[Date - Publication])",
		"# Q2: Balanced\n((\"Sleep\"[Mesh] OR \"Sleep Deprivation\"[Mesh] OR \"sleep duration\"[tiab] OR \"sleep quantity\"[tiab] OR \"short sleep\"[tiab] OR \"short sleep duration\"[tiab] OR \"insufficient sleep\"[tiab] OR \"sleep restriction\"[tiab]) AND (\"Obesity\"[Mesh] OR \"Overweight\"[Mesh] OR obes*[tiab] OR overweight[tiab] OR \"body mass index\"[tiab] OR BMI[tiab]) AND (\"Cohort Studies\"[Mesh] OR \"Prospective Studies\"[Mesh] OR cohort[tiab] OR longitudinal[tiab] OR prospective[tiab] OR retrospective[tiab] OR incidence[tiab] OR \"follow-up\"[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab]) AND (sex[tiab] OR gender[tiab] OR male[tiab] OR female[tiab] OR men[tiab] OR women[tiab] OR \"sex difference*\"[tiab] OR \"sex-specific\"[tiab])) AND (\"1900/01/01\"[Date - Publication] : \"2023/01/31\"[Date - Publication])",
		"# Q3: High-precision\n((\"Sleep Deprivation\"[majr] OR \"Sleep\"[majr]) AND (\"Obesity\"[majr] OR \"Overweight\"[majr]) AND (\"sleep duration\"[ti] OR \"short sleep\"[ti] OR \"insufficient sleep\"[ti]) AND (obes*[ti] OR overweight[ti] OR \"body mass index\"[ti] OR BMI[ti]) AND (cohort[tiab] OR longitudinal[tiab] OR prospective[tiab]) AND (sex[tiab] OR gender[tiab] OR male[tiab] OR female[tiab] OR men[tiab] OR women[tiab])) AND (\"1900/01/01\"[Date - Publication] : \"2023/01/31\"[Date - Publication])",
		"# Q4: Balanced + filter_only\n((\"Sleep\"[Mesh] OR \"Sleep Deprivation\"[Mesh] OR \"sleep duration\"[tiab] OR \"sleep quantity\"[tiab] OR \"short sleep\"[tiab] OR \"short sleep duration\"[tiab] OR \"insufficient sleep\"[tiab] OR \"sleep restriction\"[tiab]) AND (\"Obesity\"[Mesh] OR \"Overweight\"[Mesh] OR obes*[tiab] OR overweight[tiab] OR \"body mass index\"[tiab] OR BMI[tiab]) AND (\"Cohort Studies\"[Mesh] OR \"Prospective Studies\"[Mesh] OR cohort[tiab] OR longitudinal[tiab] OR prospective[tiab] OR retrospective[tiab] OR incidence[tiab] OR \"follow-up\"[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab]) AND (sex[tiab] OR gender[tiab] OR male[tiab] OR female[tiab] OR men[tiab] OR women[tiab] OR \"sex difference*\"[tiab] OR \"sex-specific\"[tiab]) AND humans[Filter] AND english[Filter]) NOT (comment[pt] OR editorial[pt] OR letter[pt]) AND (\"1900/01/01\"[Date - Publication] : \"2023/01/31\"[Date - Publication])",
		"# Q5: Balanced + scope_only\n((\"Sleep Deprivation\"[Mesh] OR \"Sleep\"[Mesh] OR \"sleep duration\"[ti] OR \"short sleep\"[ti] OR \"insufficient sleep\"[ti]) AND (\"Obesity\"[Mesh] OR \"Overweight\"[Mesh] OR obes*[ti] OR overweight[ti] OR \"body mass index\"[ti] OR BMI[ti]) AND (\"Cohort Studies\"[Mesh] OR \"Prospective Studies\"[Mesh] OR cohort[tiab] OR longitudinal[tiab] OR prospective[tiab] OR retrospective[tiab] OR incidence[tiab] OR \"follow-up\"[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab]) AND (sex[tiab] OR gender[tiab] OR male[tiab] OR female[tiab] OR men[tiab] OR women[tiab])) AND (\"1900/01/01\"[Date - Publication] : \"2023/01/31\"[Date - Publication])",
		"# Q6: Balanced + design_plus_scope\n((\"Sleep Deprivation\"[Mesh] OR \"Sleep\"[Mesh] OR \"sleep duration\"[ti] OR \"short sleep\"[ti] OR \"insufficient sleep\"[ti]) AND (\"Obesity\"[Mesh] OR \"Overweight\"[Mesh] OR obes*[ti] OR overweight[ti] OR \"body mass index\"[ti] OR BMI[ti]) AND (\"Cohort Studies\"[majr] OR \"Prospective Studies\"[majr] OR cohort[ti] OR longitudinal[ti] OR prospective[ti]) AND (\"Adult\"[Mesh] OR adult*[ti]) AND (sex[tiab] OR gender[tiab] OR male[tiab] OR female[tiab] OR men[tiab] OR women[tiab])) AND (\"1900/01/01\"[Date - Publication] : \"2023/01/31\"[Date - Publication])"
	],
	"scopus": [
		"# Q1: High-recall\nTITLE-ABS-KEY(\"sleep duration\" OR \"sleep quantity\" OR \"short sleep\" OR \"short sleep duration\" OR \"insufficient sleep\" OR \"sleep restriction\" OR \"reduced sleep\" OR \"sleep deprivation\") AND TITLE-ABS-KEY(obes* OR overweight OR adiposity OR \"body mass index\" OR bmi OR \"weight gain\") AND TITLE-ABS-KEY(cohort OR longitudinal OR prospective OR retrospective OR incidence OR \"follow-up\") AND TITLE-ABS-KEY(adult*) AND PUBYEAR < 2024",
		"# Q2: Balanced\nTITLE-ABS-KEY(\"sleep duration\" OR \"sleep quantity\" OR \"short sleep\" OR \"short sleep duration\" OR \"insufficient sleep\" OR \"sleep restriction\") AND TITLE-ABS-KEY(obes* OR overweight OR \"body mass index\" OR bmi) AND TITLE-ABS-KEY(cohort OR longitudinal OR prospective OR retrospective OR incidence OR \"follow-up\") AND TITLE-ABS-KEY(adult*) AND TITLE-ABS-KEY(sex OR gender OR male* OR female* OR men OR women OR \"sex difference*\" OR \"sex-specific\") AND PUBYEAR < 2024",
		"# Q3: High-precision\nTITLE(\"sleep duration\" OR \"short sleep\" OR \"insufficient sleep\") AND TITLE(obes* OR overweight OR \"body mass index\" OR bmi) AND TITLE-ABS-KEY(cohort OR longitudinal OR prospective) AND TITLE-ABS-KEY(sex OR gender OR male* OR female* OR men OR women) AND TITLE-ABS-KEY(adult*) AND PUBYEAR < 2024",
		"# Q4: Balanced + filter_only\nTITLE-ABS-KEY(\"sleep duration\" OR \"sleep quantity\" OR \"short sleep\" OR \"short sleep duration\" OR \"insufficient sleep\" OR \"sleep restriction\") AND TITLE-ABS-KEY(obes* OR overweight OR \"body mass index\" OR bmi) AND TITLE-ABS-KEY(cohort OR longitudinal OR prospective OR retrospective OR incidence OR \"follow-up\") AND TITLE-ABS-KEY(adult*) AND TITLE-ABS-KEY(sex OR gender OR male* OR female* OR men OR women OR \"sex difference*\" OR \"sex-specific\") AND DOCTYPE(ar) AND PUBYEAR < 2024",
		"# Q5: Balanced + scope_only\nTITLE(\"sleep duration\" OR \"short sleep\" OR \"insufficient sleep\") AND TITLE(obes* OR overweight OR \"body mass index\" OR bmi) AND TITLE-ABS-KEY(cohort OR longitudinal OR prospective OR retrospective OR incidence OR \"follow-up\") AND TITLE-ABS-KEY(adult*) AND TITLE-ABS-KEY(sex OR gender OR male* OR female* OR men OR women) AND PUBYEAR < 2024",
		"# Q6: Balanced + proximity_or_scope_fallback\nTITLE-ABS-KEY(((\"short sleep\" OR \"sleep duration\" OR \"insufficient sleep\" OR \"sleep deprivation\") W/3 (obes* OR overweight OR adiposity OR \"body mass index\" OR bmi)) AND (cohort OR longitudinal OR prospective OR retrospective OR incidence OR \"follow-up\") AND (sex OR gender OR male* OR female* OR men OR women)) AND TITLE-ABS-KEY(adult*) AND PUBYEAR < 2024"
	],
	"wos": [
		"# Q1: High-recall\nTS=(\"sleep duration\" OR \"sleep quantity\" OR \"short sleep\" OR \"short sleep duration\" OR \"insufficient sleep\" OR \"sleep restriction\" OR \"reduced sleep\" OR \"sleep deprivation\") AND TS=(obes* OR overweight OR adiposity OR \"body mass index\" OR bmi OR \"weight gain\") AND TS=(cohort OR longitudinal OR prospective OR retrospective OR incidence OR \"follow-up\") AND TS=(adult*) AND PY=(1900-2023)",
		"# Q2: Balanced\nTS=(\"sleep duration\" OR \"sleep quantity\" OR \"short sleep\" OR \"short sleep duration\" OR \"insufficient sleep\" OR \"sleep restriction\") AND TS=(obes* OR overweight OR \"body mass index\" OR bmi) AND TS=(cohort OR longitudinal OR prospective OR retrospective OR incidence OR \"follow-up\") AND TS=(adult*) AND TS=(sex OR gender OR male* OR female* OR men OR women OR \"sex difference*\" OR \"sex-specific\") AND PY=(1900-2023)",
		"# Q3: High-precision\nTI=(\"sleep duration\" OR \"short sleep\" OR \"insufficient sleep\") AND TI=(obes* OR overweight OR \"body mass index\" OR bmi) AND TS=(cohort OR longitudinal OR prospective) AND TS=(sex OR gender OR male* OR female* OR men OR women) AND TS=(adult*) AND PY=(1900-2023)",
		"# Q4: Balanced + filter_only\nTS=(\"sleep duration\" OR \"sleep quantity\" OR \"short sleep\" OR \"short sleep duration\" OR \"insufficient sleep\" OR \"sleep restriction\") AND TS=(obes* OR overweight OR \"body mass index\" OR bmi) AND TS=(cohort OR longitudinal OR prospective OR retrospective OR incidence OR \"follow-up\") AND TS=(adult*) AND TS=(sex OR gender OR male* OR female* OR men OR women OR \"sex difference*\" OR \"sex-specific\") AND DT=(Article) AND PY=(1900-2023)",
		"# Q5: Balanced + scope_only\nTI=(\"sleep duration\" OR \"short sleep\" OR \"insufficient sleep\") AND TI=(obes* OR overweight OR \"body mass index\" OR bmi) AND TS=(cohort OR longitudinal OR prospective OR retrospective OR incidence OR \"follow-up\") AND TS=(adult*) AND TS=(sex OR gender OR male* OR female* OR men OR women) AND PY=(1900-2023)",
		"# Q6: Balanced + proximity_or_scope_fallback\nTS=((\"short sleep\" OR \"sleep duration\" OR \"insufficient sleep\" OR \"sleep deprivation\") NEAR/3 (obes* OR overweight OR adiposity OR \"body mass index\" OR bmi)) AND TS=(cohort OR longitudinal OR prospective OR retrospective OR incidence OR \"follow-up\") AND TS=(adult*) AND TS=(sex OR gender OR male* OR female* OR men OR women) AND PY=(1900-2023)"
	],
	"embase": [
		"# Q1: High-recall\n('sleep'/exp OR 'sleep deprivation'/exp OR 'sleep duration':ti,ab OR 'sleep quantity':ti,ab OR 'short sleep':ti,ab OR 'short sleep duration':ti,ab OR 'insufficient sleep':ti,ab OR 'sleep restriction':ti,ab OR 'reduced sleep':ti,ab) AND ('obesity'/exp OR 'overweight'/exp OR obes*:ti,ab OR overweight:ti,ab OR adiposity:ti,ab OR 'body mass index':ti,ab OR bmi:ti,ab OR 'weight gain':ti,ab) AND ('cohort analysis'/exp OR 'prospective study'/exp OR cohort:ti,ab OR longitudinal:ti,ab OR prospective:ti,ab OR retrospective:ti,ab OR incidence:ti,ab OR 'follow-up':ti,ab) AND ('adult'/de OR adult*:ti,ab)",
		"# Q2: Balanced\n('sleep'/exp OR 'sleep deprivation'/exp OR 'sleep duration':ti,ab OR 'sleep quantity':ti,ab OR 'short sleep':ti,ab OR 'short sleep duration':ti,ab OR 'insufficient sleep':ti,ab OR 'sleep restriction':ti,ab) AND ('obesity'/exp OR 'overweight'/exp OR obes*:ti,ab OR overweight:ti,ab OR 'body mass index':ti,ab OR bmi:ti,ab) AND ('cohort analysis'/exp OR 'prospective study'/exp OR cohort:ti,ab OR longitudinal:ti,ab OR prospective:ti,ab OR retrospective:ti,ab OR incidence:ti,ab OR 'follow-up':ti,ab) AND ('adult'/de OR adult*:ti,ab) AND (sex:ti,ab OR gender:ti,ab OR male:ti,ab OR female:ti,ab OR men:ti,ab OR women:ti,ab OR 'sex difference*':ti,ab OR 'sex-specific':ti,ab)",
		"# Q3: High-precision\n('sleep deprivation'/mj OR 'sleep'/mj) AND ('obesity'/mj OR 'overweight'/mj) AND ('sleep duration':ti OR 'short sleep':ti OR 'insufficient sleep':ti) AND (obes*:ti OR overweight:ti OR 'body mass index':ti OR bmi:ti) AND (cohort:ti,ab OR longitudinal:ti,ab OR prospective:ti,ab) AND (sex:ti,ab OR gender:ti,ab OR male:ti,ab OR female:ti,ab OR men:ti,ab OR women:ti,ab) AND ('adult'/de OR adult*:ti,ab)",
		"# Q4: Balanced + scope_only\n('sleep'/exp OR 'sleep deprivation'/exp OR 'sleep duration':ti OR 'short sleep':ti OR 'insufficient sleep':ti) AND ('obesity'/exp OR 'overweight'/exp OR obes*:ti OR overweight:ti OR 'body mass index':ti OR bmi:ti) AND ('cohort analysis'/exp OR 'prospective study'/exp OR cohort:ti,ab OR longitudinal:ti,ab OR prospective:ti,ab OR retrospective:ti,ab OR incidence:ti,ab OR 'follow-up':ti,ab) AND ('adult'/de OR adult*:ti,ab) AND (sex:ti,ab OR gender:ti,ab OR male:ti,ab OR female:ti,ab OR men:ti,ab OR women:ti,ab)",
		"# Q5: Balanced + design_plus_scope\n('sleep deprivation'/mj OR 'sleep'/mj OR 'sleep duration':ti OR 'short sleep':ti OR 'insufficient sleep':ti) AND ('obesity'/mj OR 'overweight'/mj OR obes*:ti OR overweight:ti OR 'body mass index':ti OR bmi:ti) AND ('cohort analysis'/mj OR 'prospective study'/mj OR cohort:ti OR longitudinal:ti OR prospective:ti) AND ('adult'/de OR adult*:ti) AND (sex:ti,ab OR gender:ti,ab OR male:ti,ab OR female:ti,ab OR men:ti,ab OR women:ti,ab)",
		"# Q6: Balanced + proximity_or_scope_fallback\n((('short sleep':ti,ab OR 'sleep duration':ti,ab OR 'insufficient sleep':ti,ab OR 'sleep deprivation':ti,ab) ADJ3 (obes*:ti,ab OR overweight:ti,ab OR adiposity:ti,ab OR 'body mass index':ti,ab OR bmi:ti,ab)) AND ('cohort analysis'/exp OR 'prospective study'/exp OR cohort:ti,ab OR longitudinal:ti,ab OR prospective:ti,ab OR retrospective:ti,ab OR incidence:ti,ab OR 'follow-up':ti,ab) AND ('adult'/de OR adult*:ti,ab) AND (sex:ti,ab OR gender:ti,ab OR male:ti,ab OR female:ti,ab OR men:ti,ab OR women:ti,ab))"
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

- PubMed keeps the baseline architecture intact and uses title narrowing in `scope_only` and `design_plus_scope` because proximity is unavailable.
- Scopus and Web of Science use `proximity_or_scope_fallback` as the third bundle because both platforms support proximity operators that can tighten the sleep-obesity relation without changing the selected `single_route` architecture.
- Embase stays on Embase.com syntax throughout and omits inline date limits, consistent with repository guidance to apply year limits in the interface when executing the search.
- English-language and article-only constraints are treated as `filter_only` rather than mandatory baseline logic because they are explicit protocol restrictions but not necessary to preserve the core retrieval route.
- Sex-comparison terms are handled as `optional_precision` so Q1 does not lose cohort studies that report male and female estimates without foregrounding sex wording in the title or abstract.