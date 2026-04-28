# Search Strategy for Nexha_2024

## Study Summary

- Topic: Biological rhythm disruptions in women with premenstrual syndrome or premenstrual dysphoric disorder
- Date window: Database inception to 2019-07-31; inline upper bounds are applied where platform-safe, and the same cutoff should be used as an interface limit for Embase
- Databases: pubmed, scopus, wos, embase
- Query level: extended
- Retrieval architecture: single_route
- design_analytic_block: active, but populated conservatively and reserved for the bundled precision variant rather than baseline Q1

## PICOS Summary

- Population: Women of reproductive age with PMS or PMDD
- Intervention or Exposure: PMS or PMDD diagnosis
- Comparator: Healthy women without PMS or PMDD
- Outcomes: Biological rhythm measurements, especially circadian rhythm, sleep disruption or sleep quality, melatonin, sleep EEG or polysomnography, hormonal rhythm measures, and body temperature
- Design: Cross-sectional and longitudinal studies, with clinical trials included only when baseline biological-rhythm measurements are available

## Architecture Selection Summary

- Selected retrieval architecture: `single_route`
- `design_analytic_block`: active

### Concept Roles

| Role | Assigned concepts |
| --- | --- |
| mandatory_core | PMS or PMDD; biological-rhythm disruption domain including circadian rhythm, sleep disturbance or sleep quality, melatonin, and protocol-explicit rhythm measurements |
| optional_precision | chronobiology wording; polysomnography or sleep-EEG wording; title-only scope tightening; proximity tightening where supported |
| filter_only | observational or longitudinal design labels; humans or article-type limits where platform-safe; the review-date cutoff when expressed as a database limit |
| screening_only | healthy-control requirement; exclusion of primary psychiatric comorbidity; the baseline-only condition for clinical trials; case-report or review exclusion when not safely supported inline |

The protocol defines one coherent Boolean route linking a PMS or PMDD condition block to a biological-rhythm outcome block. It does not justify two complementary indexed and textword routes for the same concepts, so `dual_route_union` is not warranted. The active `design_analytic_block` is kept conservative because the protocol's design constraints are eligibility rules that are useful for later precision tightening, but risky as baseline high-recall requirements.

## Concept Tables

### Concept to MeSH or Emtree

| concept | term | tree note | explode? | rationale and source |
| --- | --- | --- | --- | --- |
| PMS or PMDD core | Premenstrual Syndrome / premenstrual syndrome | umbrella indexed representation for the PMS block | Yes | Protocol population, exposure, and PROSPERO MeSH list |
| PMS or PMDD core | Premenstrual Dysphoric Disorder / premenstrual dysphoric disorder | indexed representation for the PMDD block | Yes | Protocol title, objective, population, and PROSPERO MeSH list |
| biological-rhythm core | Circadian Rhythm / circadian rhythm | indexed circadian representation | Yes | Protocol search fragment and review objective |
| biological-rhythm core | Biological Clocks / text only in Embase translation | indexed biological-rhythm representation where supported | Yes where supported | Protocol objective and explicit biological-rhythm wording |
| biological-rhythm core | Melatonin / melatonin | indexed hormonal rhythm marker | Yes | Protocol search fragment and data-synthesis description |
| design block | Cross-Sectional Studies; Longitudinal Studies / cross-sectional study; longitudinal study | indexed design layer for later precision variants | Yes where supported | Protocol study-design eligibility |

### Concept to Textword

| concept | synonym or phrase | field | truncation? | source |
| --- | --- | --- | --- | --- |
| PMS or PMDD core | premenstrual syndrome; premenstrual syndromes; PMS | title/abstract/topic | Mixed | Protocol search fragment and population |
| PMS or PMDD core | premenstrual dysphoric disorder; PMDD | title/abstract/topic | No | Protocol title, objective, and population |
| biological-rhythm core | biological rhythm; biological rhythms | title/abstract/topic | No | Protocol search fragment |
| biological-rhythm core | circadian rhythm; circadian rhythms; chronobiolog* | title/abstract/topic | Mixed | Protocol search fragment plus protocol-consistent chronobiology wording |
| biological-rhythm core | melatonin | title/abstract/topic | No | Protocol search fragment |
| biological-rhythm core | sleep disruption; sleep disruptions; sleep disturbance; sleep disturbances; sleep quality | title/abstract/topic | No | Protocol search fragment and data-synthesis description |
| biological-rhythm core | sleep EEG; polysomnograph* | title/abstract/topic | Mixed | Protocol data-synthesis description |
| biological-rhythm core | body temperature | title/abstract/topic | No | Protocol data-synthesis description |
| biological-rhythm core | cortisol; prolactin; TSH; thyroid stimulating hormone, when paired with circadian, diurnal, or rhythm wording | title/abstract/topic | No | Protocol data-synthesis description |
| design block | cross-sectional; longitudinal; prospective; observational; clinical trial; trial | title/abstract/topic | No | Protocol study-design eligibility |

## JSON Query Object

```json
{
  "pubmed": [
    "# Q1: High-recall\n(((\"Premenstrual Syndrome\"[Mesh] OR \"Premenstrual Dysphoric Disorder\"[Mesh] OR PMS[tiab] OR PMDD[tiab] OR \"premenstrual syndrome\"[tiab] OR \"premenstrual syndromes\"[tiab] OR \"premenstrual dysphoric disorder\"[tiab]) AND (\"Circadian Rhythm\"[Mesh] OR \"Biological Clocks\"[Mesh] OR \"Melatonin\"[Mesh] OR \"biological rhythm\"[tiab] OR \"biological rhythms\"[tiab] OR \"circadian rhythm\"[tiab] OR \"circadian rhythms\"[tiab] OR chronobiolog*[tiab] OR melatonin[tiab] OR \"sleep disruption\"[tiab] OR \"sleep disruptions\"[tiab] OR \"sleep disturbance\"[tiab] OR \"sleep disturbances\"[tiab] OR \"sleep quality\"[tiab] OR polysomnograph*[tiab] OR \"sleep EEG\"[tiab] OR diurnal[tiab] OR \"body temperature\"[tiab] OR ((cortisol[tiab] OR prolactin[tiab] OR TSH[tiab] OR \"thyroid stimulating hormone\"[tiab]) AND (circadian[tiab] OR diurnal[tiab] OR rhythm*[tiab])))) AND (\"0001/01/01\"[Date - Publication] : \"2019/07/31\"[Date - Publication]))",
    "# Q2: Balanced\n(((\"Premenstrual Syndrome\"[Mesh] OR \"Premenstrual Dysphoric Disorder\"[Mesh] OR PMS[tiab] OR PMDD[tiab] OR \"premenstrual syndrome\"[tiab] OR \"premenstrual syndromes\"[tiab] OR \"premenstrual dysphoric disorder\"[tiab]) AND (\"Circadian Rhythm\"[Mesh] OR \"Melatonin\"[Mesh] OR \"biological rhythm\"[tiab] OR \"biological rhythms\"[tiab] OR \"circadian rhythm\"[tiab] OR \"circadian rhythms\"[tiab] OR chronobiolog*[tiab] OR melatonin[tiab] OR \"sleep disturbance\"[tiab] OR \"sleep disturbances\"[tiab] OR \"sleep quality\"[tiab] OR polysomnograph*[tiab] OR \"sleep EEG\"[tiab] OR \"body temperature\"[tiab] OR ((cortisol[tiab] OR prolactin[tiab] OR TSH[tiab] OR \"thyroid stimulating hormone\"[tiab]) AND (circadian[tiab] OR diurnal[tiab] OR rhythm*[tiab])))) AND (\"0001/01/01\"[Date - Publication] : \"2019/07/31\"[Date - Publication]))",
    "# Q3: High-precision\n((((\"Premenstrual Syndrome\"[Majr] OR \"Premenstrual Dysphoric Disorder\"[Majr] OR \"premenstrual syndrome\"[ti] OR \"premenstrual dysphoric disorder\"[ti] OR PMS[ti] OR PMDD[ti]) AND (\"Circadian Rhythm\"[Majr] OR \"Melatonin\"[Majr] OR \"biological rhythm\"[ti] OR \"biological rhythms\"[ti] OR \"circadian rhythm\"[ti] OR \"circadian rhythms\"[ti] OR chronobiolog*[ti] OR melatonin[ti] OR \"sleep quality\"[ti] OR polysomnograph*[ti] OR \"body temperature\"[ti])) AND humans[Filter]) NOT (case reports[pt] OR review[pt] OR meta-analysis[pt] OR letter[pt] OR editorial[pt] OR comment[pt])) AND (\"0001/01/01\"[Date - Publication] : \"2019/07/31\"[Date - Publication]))",
    "# Q4: Balanced + scope_only\n(((\"premenstrual syndrome\"[ti] OR \"premenstrual dysphoric disorder\"[ti] OR PMS[ti] OR PMDD[ti]) AND (\"biological rhythm\"[ti] OR \"biological rhythms\"[ti] OR \"circadian rhythm\"[ti] OR \"circadian rhythms\"[ti] OR chronobiolog*[ti] OR melatonin[ti] OR \"sleep disturbance\"[ti] OR \"sleep disturbances\"[ti] OR \"sleep quality\"[ti] OR polysomnograph*[ti] OR \"body temperature\"[ti])) AND (\"0001/01/01\"[Date - Publication] : \"2019/07/31\"[Date - Publication]))",
    "# Q5: Balanced + proximity_or_scope_fallback\n((((\"Premenstrual Syndrome\"[Majr] OR \"Premenstrual Dysphoric Disorder\"[Majr] OR \"premenstrual syndrome\"[ti] OR \"premenstrual dysphoric disorder\"[ti] OR PMS[ti] OR PMDD[ti]) AND (\"biological rhythm\"[ti] OR \"biological rhythms\"[ti] OR \"circadian rhythm\"[ti] OR \"circadian rhythms\"[ti] OR chronobiolog*[ti] OR melatonin[ti] OR \"sleep disturbance\"[ti] OR \"sleep quality\"[ti] OR polysomnograph*[ti])) AND humans[Filter]) AND (\"0001/01/01\"[Date - Publication] : \"2019/07/31\"[Date - Publication]))",
    "# Q6: Balanced + design_plus_filter\n(((((\"Premenstrual Syndrome\"[Mesh] OR \"Premenstrual Dysphoric Disorder\"[Mesh] OR PMS[tiab] OR PMDD[tiab] OR \"premenstrual syndrome\"[tiab] OR \"premenstrual syndromes\"[tiab] OR \"premenstrual dysphoric disorder\"[tiab]) AND (\"Circadian Rhythm\"[Mesh] OR \"Melatonin\"[Mesh] OR \"biological rhythm\"[tiab] OR \"biological rhythms\"[tiab] OR \"circadian rhythm\"[tiab] OR \"circadian rhythms\"[tiab] OR chronobiolog*[tiab] OR melatonin[tiab] OR \"sleep disturbance\"[tiab] OR \"sleep disturbances\"[tiab] OR \"sleep quality\"[tiab] OR polysomnograph*[tiab] OR \"sleep EEG\"[tiab] OR \"body temperature\"[tiab] OR ((cortisol[tiab] OR prolactin[tiab] OR TSH[tiab] OR \"thyroid stimulating hormone\"[tiab]) AND (circadian[tiab] OR diurnal[tiab] OR rhythm*[tiab])))) AND (cross-sectional[tiab] OR longitudinal[tiab] OR prospective[tiab] OR observational[tiab] OR \"clinical trial\"[tiab] OR trial[tiab] OR \"Clinical Trial\"[Publication Type])) AND humans[Filter]) NOT (case reports[pt] OR review[pt] OR meta-analysis[pt] OR letter[pt] OR editorial[pt] OR comment[pt])) AND (\"0001/01/01\"[Date - Publication] : \"2019/07/31\"[Date - Publication]))"
  ],
  "scopus": [
    "# Q1: High-recall\nTITLE-ABS-KEY(((\"premenstrual syndrome\" OR \"premenstrual syndromes\" OR \"premenstrual dysphoric disorder\" OR PMS OR PMDD) AND (\"biological rhythm\" OR \"biological rhythms\" OR \"circadian rhythm\" OR \"circadian rhythms\" OR chronobiolog* OR melatonin OR \"sleep disruption\" OR \"sleep disruptions\" OR \"sleep disturbance\" OR \"sleep disturbances\" OR \"sleep quality\" OR polysomnograph* OR \"sleep eeg\" OR diurnal OR \"body temperature\" OR ((cortisol OR prolactin OR TSH OR \"thyroid stimulating hormone\") AND (circadian OR diurnal OR rhythm*))))) AND PUBYEAR < 2020",
    "# Q2: Balanced\nTITLE-ABS-KEY(((\"premenstrual syndrome\" OR \"premenstrual syndromes\" OR \"premenstrual dysphoric disorder\" OR PMS OR PMDD) AND (\"biological rhythm\" OR \"biological rhythms\" OR \"circadian rhythm\" OR \"circadian rhythms\" OR chronobiolog* OR melatonin OR \"sleep disturbance\" OR \"sleep disturbances\" OR \"sleep quality\" OR polysomnograph* OR \"sleep eeg\" OR \"body temperature\" OR ((cortisol OR prolactin OR TSH OR \"thyroid stimulating hormone\") AND (circadian OR diurnal OR rhythm*))))) AND PUBYEAR < 2020",
    "# Q3: High-precision\nTITLE(\"premenstrual syndrome\" OR \"premenstrual dysphoric disorder\" OR PMS OR PMDD) AND TITLE(\"biological rhythm\" OR \"biological rhythms\" OR \"circadian rhythm\" OR \"circadian rhythms\" OR chronobiolog* OR melatonin OR \"sleep quality\" OR polysomnograph* OR \"body temperature\") AND TITLE-ABS-KEY(cross-sectional OR longitudinal OR prospective OR observational OR \"clinical trial\" OR trial) AND PUBYEAR < 2020 AND DOCTYPE(ar)",
    "# Q4: Balanced + scope_only\nTITLE(\"premenstrual syndrome\" OR \"premenstrual dysphoric disorder\" OR PMS OR PMDD) AND TITLE(\"biological rhythm\" OR \"biological rhythms\" OR \"circadian rhythm\" OR \"circadian rhythms\" OR chronobiolog* OR melatonin OR \"sleep disturbance\" OR \"sleep quality\" OR polysomnograph* OR \"body temperature\") AND PUBYEAR < 2020",
    "# Q5: Balanced + proximity_or_scope_fallback\nTITLE-ABS-KEY(((\"premenstrual syndrome\" OR \"premenstrual dysphoric disorder\" OR PMS OR PMDD) AND ((biological W/1 rhythm*) OR (circadian W/1 rhythm*) OR chronobiolog* OR melatonin OR (sleep W/2 (disruption* OR disturbance* OR quality OR eeg)) OR (body W/1 temperature) OR ((cortisol OR prolactin OR TSH OR \"thyroid stimulating hormone\") W/3 (circadian OR diurnal OR rhythm*))))) AND PUBYEAR < 2020",
    "# Q6: Balanced + design_plus_filter\nTITLE-ABS-KEY(((\"premenstrual syndrome\" OR \"premenstrual syndromes\" OR \"premenstrual dysphoric disorder\" OR PMS OR PMDD) AND (\"biological rhythm\" OR \"biological rhythms\" OR \"circadian rhythm\" OR \"circadian rhythms\" OR chronobiolog* OR melatonin OR \"sleep disturbance\" OR \"sleep disturbances\" OR \"sleep quality\" OR polysomnograph* OR \"sleep eeg\" OR \"body temperature\" OR ((cortisol OR prolactin OR TSH OR \"thyroid stimulating hormone\") AND (circadian OR diurnal OR rhythm*))))) AND TITLE-ABS-KEY(cross-sectional OR longitudinal OR prospective OR observational OR \"clinical trial\" OR trial) AND DOCTYPE(ar) AND PUBYEAR < 2020"
  ],
  "wos": [
    "# Q1: High-recall\nTS=(((\"premenstrual syndrome\" OR \"premenstrual syndromes\" OR \"premenstrual dysphoric disorder\" OR PMS OR PMDD) AND (\"biological rhythm\" OR \"biological rhythms\" OR \"circadian rhythm\" OR \"circadian rhythms\" OR chronobiolog* OR melatonin OR \"sleep disruption\" OR \"sleep disruptions\" OR \"sleep disturbance\" OR \"sleep disturbances\" OR \"sleep quality\" OR polysomnograph* OR \"sleep eeg\" OR diurnal OR \"body temperature\" OR ((cortisol OR prolactin OR TSH OR \"thyroid stimulating hormone\") AND (circadian OR diurnal OR rhythm*))))) AND PY=(1900-2019)",
    "# Q2: Balanced\nTS=(((\"premenstrual syndrome\" OR \"premenstrual syndromes\" OR \"premenstrual dysphoric disorder\" OR PMS OR PMDD) AND (\"biological rhythm\" OR \"biological rhythms\" OR \"circadian rhythm\" OR \"circadian rhythms\" OR chronobiolog* OR melatonin OR \"sleep disturbance\" OR \"sleep disturbances\" OR \"sleep quality\" OR polysomnograph* OR \"sleep eeg\" OR \"body temperature\" OR ((cortisol OR prolactin OR TSH OR \"thyroid stimulating hormone\") AND (circadian OR diurnal OR rhythm*))))) AND PY=(1900-2019)",
    "# Q3: High-precision\nTI=(\"premenstrual syndrome\" OR \"premenstrual dysphoric disorder\" OR PMS OR PMDD) AND TI=(\"biological rhythm\" OR \"biological rhythms\" OR \"circadian rhythm\" OR \"circadian rhythms\" OR chronobiolog* OR melatonin OR \"sleep quality\" OR polysomnograph* OR \"body temperature\") AND TS=(cross-sectional OR longitudinal OR prospective OR observational OR \"clinical trial\" OR trial) AND DT=(Article) AND PY=(1900-2019)",
    "# Q4: Balanced + scope_only\nTI=(\"premenstrual syndrome\" OR \"premenstrual dysphoric disorder\" OR PMS OR PMDD) AND TI=(\"biological rhythm\" OR \"biological rhythms\" OR \"circadian rhythm\" OR \"circadian rhythms\" OR chronobiolog* OR melatonin OR \"sleep disturbance\" OR \"sleep quality\" OR polysomnograph* OR \"body temperature\") AND PY=(1900-2019)",
    "# Q5: Balanced + proximity_or_scope_fallback\nTS=(((\"premenstrual syndrome\" OR \"premenstrual dysphoric disorder\" OR PMS OR PMDD) AND ((biological NEAR/1 rhythm*) OR (circadian NEAR/1 rhythm*) OR chronobiolog* OR melatonin OR (sleep NEAR/2 (disruption* OR disturbance* OR quality OR eeg)) OR (body NEAR/1 temperature) OR ((cortisol OR prolactin OR TSH OR \"thyroid stimulating hormone\") NEAR/3 (circadian OR diurnal OR rhythm*))))) AND PY=(1900-2019)",
    "# Q6: Balanced + design_plus_filter\nTS=(((\"premenstrual syndrome\" OR \"premenstrual syndromes\" OR \"premenstrual dysphoric disorder\" OR PMS OR PMDD) AND (\"biological rhythm\" OR \"biological rhythms\" OR \"circadian rhythm\" OR \"circadian rhythms\" OR chronobiolog* OR melatonin OR \"sleep disturbance\" OR \"sleep disturbances\" OR \"sleep quality\" OR polysomnograph* OR \"sleep eeg\" OR \"body temperature\" OR ((cortisol OR prolactin OR TSH OR \"thyroid stimulating hormone\") AND (circadian OR diurnal OR rhythm*))))) AND TS=(cross-sectional OR longitudinal OR prospective OR observational OR \"clinical trial\" OR trial) AND DT=(Article) AND PY=(1900-2019)"
  ],
  "embase": [
    "# Q1: High-recall\n(('premenstrual syndrome'/exp OR 'premenstrual dysphoric disorder'/exp OR pms:ti,ab OR pmdd:ti,ab OR 'premenstrual syndrome':ti,ab OR 'premenstrual syndromes':ti,ab OR 'premenstrual dysphoric disorder':ti,ab) AND ('circadian rhythm'/exp OR 'melatonin'/exp OR 'biological rhythm':ti,ab OR 'biological rhythms':ti,ab OR 'circadian rhythm':ti,ab OR 'circadian rhythms':ti,ab OR chronobiolog*:ti,ab OR melatonin:ti,ab OR 'sleep disruption':ti,ab OR 'sleep disruptions':ti,ab OR 'sleep disturbance':ti,ab OR 'sleep disturbances':ti,ab OR 'sleep quality':ti,ab OR polysomnograph*:ti,ab OR 'sleep eeg':ti,ab OR diurnal:ti,ab OR 'body temperature':ti,ab OR (((cortisol OR prolactin OR TSH OR 'thyroid stimulating hormone') ADJ3 (circadian OR diurnal OR rhythm*)):ti,ab)))",
    "# Q2: Balanced\n(('premenstrual syndrome'/exp OR 'premenstrual dysphoric disorder'/exp OR pms:ti,ab OR pmdd:ti,ab OR 'premenstrual syndrome':ti,ab OR 'premenstrual syndromes':ti,ab OR 'premenstrual dysphoric disorder':ti,ab) AND ('circadian rhythm'/exp OR 'melatonin'/exp OR 'biological rhythm':ti,ab OR 'biological rhythms':ti,ab OR 'circadian rhythm':ti,ab OR 'circadian rhythms':ti,ab OR chronobiolog*:ti,ab OR melatonin:ti,ab OR 'sleep disturbance':ti,ab OR 'sleep disturbances':ti,ab OR 'sleep quality':ti,ab OR polysomnograph*:ti,ab OR 'sleep eeg':ti,ab OR 'body temperature':ti,ab OR (((cortisol OR prolactin OR TSH OR 'thyroid stimulating hormone') ADJ3 (circadian OR diurnal OR rhythm*)):ti,ab)))",
    "# Q3: High-precision\n((('premenstrual syndrome'/mj OR 'premenstrual dysphoric disorder'/mj OR 'premenstrual syndrome':ti OR 'premenstrual dysphoric disorder':ti OR pms:ti OR pmdd:ti) AND ('circadian rhythm'/mj OR 'melatonin'/mj OR 'biological rhythm':ti OR 'biological rhythms':ti OR 'circadian rhythm':ti OR 'circadian rhythms':ti OR chronobiolog*:ti OR melatonin:ti OR 'sleep quality':ti OR polysomnograph*:ti OR 'body temperature':ti)) AND (cross-sectional:ti,ab OR longitudinal:ti,ab OR prospective:ti,ab OR observational:ti,ab OR 'clinical trial':ti,ab OR trial:ti,ab))",
    "# Q4: Balanced + scope_only\n(('premenstrual syndrome':ti OR 'premenstrual dysphoric disorder':ti OR pms:ti OR pmdd:ti) AND ('biological rhythm':ti OR 'biological rhythms':ti OR 'circadian rhythm':ti OR 'circadian rhythms':ti OR chronobiolog*:ti OR melatonin:ti OR 'sleep disturbance':ti OR 'sleep quality':ti OR polysomnograph*:ti OR 'body temperature':ti))",
    "# Q5: Balanced + proximity_or_scope_fallback\n(('premenstrual syndrome':ti,ab OR 'premenstrual dysphoric disorder':ti,ab OR pms:ti,ab OR pmdd:ti,ab) AND (((biological ADJ1 rhythm*):ti,ab OR (circadian ADJ1 rhythm*):ti,ab OR chronobiolog*:ti,ab OR melatonin:ti,ab OR ((sleep ADJ2 (disruption* OR disturbance* OR quality OR eeg)):ti,ab) OR ((body ADJ1 temperature):ti,ab) OR (((cortisol OR prolactin OR TSH OR 'thyroid stimulating hormone') ADJ3 (circadian OR diurnal OR rhythm*)):ti,ab)))",
    "# Q6: Balanced + design_plus_filter\n(('premenstrual syndrome'/exp OR 'premenstrual dysphoric disorder'/exp OR pms:ti,ab OR pmdd:ti,ab OR 'premenstrual syndrome':ti,ab OR 'premenstrual syndromes':ti,ab OR 'premenstrual dysphoric disorder':ti,ab) AND ('circadian rhythm'/exp OR 'melatonin'/exp OR 'biological rhythm':ti,ab OR 'biological rhythms':ti,ab OR 'circadian rhythm':ti,ab OR 'circadian rhythms':ti,ab OR chronobiolog*:ti,ab OR melatonin:ti,ab OR 'sleep disturbance':ti,ab OR 'sleep disturbances':ti,ab OR 'sleep quality':ti,ab OR polysomnograph*:ti,ab OR 'sleep eeg':ti,ab OR 'body temperature':ti,ab OR (((cortisol OR prolactin OR TSH OR 'thyroid stimulating hormone') ADJ3 (circadian OR diurnal OR rhythm*)):ti,ab)) AND (cross-sectional:ti,ab OR longitudinal:ti,ab OR prospective:ti,ab OR observational:ti,ab OR 'clinical trial':ti,ab OR trial:ti,ab))"
  ]
}
```

## PRESS Self-Check

```json
{
  "json_patch": {}
}
```

- Q1 and Q2 preserve the same mandatory-core route across all databases: PMS or PMDD and a biological-rhythm disruption block.
- Healthy-control wording, psychiatric-disorder exclusions, and the baseline-only rule for clinical trials were kept out of baseline retrieval because the protocol treats them as screening or eligibility constraints rather than core subject-matter concepts.
- Q4 to Q6 use only approved bundled cases: `scope_only`, `proximity_or_scope_fallback`, and `design_plus_filter`.
- The July 2019 search date is represented inline for PubMed, Scopus, and Web of Science, while Embase follows the repository guidance to keep the cutoff as an interface-level limit rather than a platform-specific inline date clause.

## Translation Notes

- The protocol's explicit search fragment is the anchor for the mandatory biological-rhythm block, and the added sleep-quality, polysomnography, hormonal-rhythm, and body-temperature wording comes only from the protocol's own planned data-synthesis description.
- `design_analytic_block` remains active by rule, but its contents are conservative because adding design labels earlier than Q6 would create avoidable recall loss.
- Web of Science can only express the 2019 boundary at the publication-year level, so `PY=(1900-2019)` is the closest platform-safe approximation to the July 31, 2019 search date.
- Embase is translated in Embase.com syntax consistently, with the date cutoff intended as an interface-applied limit to match the repository guidance.