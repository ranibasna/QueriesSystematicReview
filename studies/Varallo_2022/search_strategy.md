# Search Strategy for Varallo_2022

## Study Summary

- Topic: Preoperative and perioperative sleep disturbances as risk factors for chronic post-surgical pain
- Date window: No inline publication-date restriction; the protocol states no publication date restrictions
- Databases: pubmed, scopus, wos, embase
- Query level: extended
- Retrieval architecture: single_route
- design_analytic_block: active, but populated conservatively and reserved for the higher-precision bundled variant

## PICOS Summary

- Population: Adults undergoing any type of surgical intervention
- Intervention or Exposure: Preoperative and perioperative sleep disturbances, sleep quality, sleep quantity, and clinically diagnosed sleep disorders or polysomnography-assessed disturbance
- Comparator: None
- Outcomes: Chronic post-surgical pain presence or intensity, with analgesic use as a secondary outcome, assessed at follow-up after at least 3 months
- Design: Longitudinal prospective studies

## Architecture Selection Summary

- Selected retrieval architecture: `single_route`
- `design_analytic_block`: active

### Concept Roles

| Role | Assigned concepts |
| --- | --- |
| mandatory_core | sleep disturbance exposure; post-surgical pain outcome domain |
| optional_precision | preoperative or perioperative timing wording; chronic or persistent follow-up phrasing; specific diagnosed sleep-disorder and sleep-quality or sleep-quantity wording; title or proximity tightening where supported |
| filter_only | prospective or longitudinal or cohort labels; adult-only wording; humans or article-type or interface-applied language limits where platform-safe |
| screening_only | country or socioeconomic context; surgery-type subgrouping; explicit effect-size terminology; comparator handling |

The protocol supports one coherent Boolean route rather than complementary indexed and free-text routes, so `single_route` is the safer fit. The protocol also makes preoperative or perioperative timing and long-term follow-up central to the question, but those phrases are likely to be inconsistently reported in titles and abstracts. For that reason, baseline Q1 keeps the mandatory route broad on sleep disturbance exposure plus post-surgical pain outcomes, while Q2 to Q6 tighten timing, chronicity, adult population, and prospective-design cues in recall-aware stages.

## Concept Tables

### Concept to MeSH or Emtree

| concept | term | tree note | explode? | rationale and source |
| --- | --- | --- | --- | --- |
| sleep disturbance exposure | Sleep Wake Disorders / sleep disorder | broad indexed representation of sleep disturbance and clinically diagnosed sleep disorders | Yes | Protocol keywords and exposure description |
| sleep disturbance exposure | Sleep Initiation and Maintenance Disorders / insomnia | indexed support for insomnia-related sleep disturbance | Yes | Protocol exposure includes sleep disturbance and clinically diagnosed sleep disorders |
| sleep disturbance exposure | Sleep Apnea Syndromes / sleep apnea syndrome | indexed support for OSA and related breathing-disorder exposure | Yes | Protocol exposure examples explicitly include OSA |
| sleep disturbance exposure | Narcolepsy / narcolepsy | indexed support for narcolepsy-related exposure | Yes | Protocol exposure examples explicitly include narcolepsy |
| post-surgical pain outcomes | Pain, Postoperative / postoperative pain | indexed representation of the surgical pain outcome domain | Yes | Review title, objectives, and main outcomes |
| design block | Prospective Studies / prospective study | indexed support for the protocol-required longitudinal prospective design | Yes | Protocol study-design eligibility |

### Concept to Textword

| concept | synonym or phrase | field | truncation? | source |
| --- | --- | --- | --- | --- |
| sleep disturbance exposure | sleep disturbance* | title/abstract/topic | Yes | Protocol keywords |
| sleep disturbance exposure | sleep disorder* | title/abstract/topic | Yes | Protocol exposure description |
| sleep disturbance exposure | sleep quality | title/abstract/topic | No | Review objective |
| sleep disturbance exposure | sleep quantity | title/abstract/topic | No | Review objective |
| sleep disturbance exposure | sleep duration | title/abstract/topic | No | Protocol-compatible quantity wording |
| sleep disturbance exposure | insomnia | title/abstract/topic | No | Explicit protocol example |
| sleep disturbance exposure | hypersomnia | title/abstract/topic | No | Explicit protocol example |
| sleep disturbance exposure | narcolep* | title/abstract/topic | Yes | Explicit protocol example |
| sleep disturbance exposure | sleep apnea; sleep apnoea; obstructive sleep apnea; obstructive sleep apnoea | title/abstract/topic | No | Explicit protocol example |
| sleep disturbance exposure | polysomnograph* | title/abstract/topic | Yes | Protocol exposure-assessment method |
| post-surgical pain outcomes | postoperative pain; post-operative pain; postsurgical pain; post-surgical pain | title/abstract/topic | No | Review title and objectives |
| post-surgical pain outcomes | chronic postoperative pain; chronic post-operative pain; chronic postsurgical pain; chronic post-surgical pain | title/abstract/topic | No | Review title and main outcomes |
| post-surgical pain outcomes | persistent postoperative pain; persistent post-operative pain; persistent postsurgical pain; persistent post-surgical pain | title/abstract/topic | No | Protocol condition/domain wording |
| post-surgical pain outcomes | CPSP | title/abstract/topic | No | Standard acronym for chronic post-surgical pain |
| timing precision | preoperat*; presurg*; perioperat*; pre-operative; peri-operative | title/abstract/topic | Mixed | Protocol exposure timing |
| outcome timing precision | follow-up; 3 month*; three month* | title/abstract/topic | Mixed | Protocol outcome timing |
| design block | prospective; longitudinal; cohort | title/abstract/topic | No | Protocol study design |
| adult filter | adult* | title/abstract/topic | Yes | Protocol population restriction |

## JSON Query Object

```json
{
  "pubmed": [
    "# Q1: High-recall\n((\"Sleep Wake Disorders\"[Mesh] OR \"Sleep Initiation and Maintenance Disorders\"[Mesh] OR \"Sleep Apnea Syndromes\"[Mesh] OR \"Narcolepsy\"[Mesh] OR sleep disturbance*[tiab] OR sleep disorder*[tiab] OR insomnia[tiab] OR hypersomnia[tiab] OR narcolep*[tiab] OR \"sleep apnea\"[tiab] OR \"sleep apnoea\"[tiab] OR \"obstructive sleep apnea\"[tiab] OR \"obstructive sleep apnoea\"[tiab] OR \"sleep quality\"[tiab] OR \"sleep quantity\"[tiab] OR \"sleep duration\"[tiab] OR polysomnograph*[tiab]) AND (\"Pain, Postoperative\"[Mesh] OR \"postoperative pain\"[tiab] OR \"post-operative pain\"[tiab] OR \"postsurgical pain\"[tiab] OR \"post-surgical pain\"[tiab] OR \"persistent postoperative pain\"[tiab] OR \"persistent post-operative pain\"[tiab] OR \"persistent postsurgical pain\"[tiab] OR \"persistent post-surgical pain\"[tiab] OR \"chronic postoperative pain\"[tiab] OR \"chronic post-operative pain\"[tiab] OR \"chronic postsurgical pain\"[tiab] OR \"chronic post-surgical pain\"[tiab] OR CPSP[tiab]))",
    "# Q2: Balanced\n((\"Sleep Wake Disorders\"[Mesh] OR \"Sleep Initiation and Maintenance Disorders\"[Mesh] OR \"Sleep Apnea Syndromes\"[Mesh] OR \"Narcolepsy\"[Mesh] OR sleep disturbance*[tiab] OR sleep disorder*[tiab] OR insomnia[tiab] OR hypersomnia[tiab] OR narcolep*[tiab] OR \"sleep apnea\"[tiab] OR \"sleep apnoea\"[tiab] OR \"obstructive sleep apnea\"[tiab] OR \"obstructive sleep apnoea\"[tiab] OR \"sleep quality\"[tiab] OR \"sleep quantity\"[tiab] OR \"sleep duration\"[tiab]) AND (\"Pain, Postoperative\"[Mesh] OR \"postoperative pain\"[tiab] OR \"post-operative pain\"[tiab] OR \"postsurgical pain\"[tiab] OR \"post-surgical pain\"[tiab] OR \"persistent postoperative pain\"[tiab] OR \"persistent postsurgical pain\"[tiab] OR \"chronic postoperative pain\"[tiab] OR \"chronic postsurgical pain\"[tiab] OR CPSP[tiab]) AND (preoperat*[tiab] OR presurg*[tiab] OR perioperat*[tiab] OR \"pre-operative\"[tiab] OR \"peri-operative\"[tiab]) AND (chronic*[tiab] OR persistent*[tiab] OR \"3 month*\"[tiab] OR \"three month*\"[tiab] OR \"follow-up\"[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab]))",
    "# Q3: High-precision\n(((\"Sleep Initiation and Maintenance Disorders\"[Majr] OR \"Sleep Apnea Syndromes\"[Majr] OR \"Narcolepsy\"[Majr]) OR sleep disturbance*[ti] OR sleep disorder*[ti] OR insomnia[ti] OR hypersomnia[ti] OR narcolep*[ti] OR \"sleep apnea\"[ti] OR \"obstructive sleep apnea\"[ti] OR \"sleep quality\"[ti]) AND ((\"Pain, Postoperative\"[Majr] OR \"postoperative pain\"[ti] OR \"postsurgical pain\"[ti] OR \"persistent postoperative pain\"[ti] OR \"chronic postsurgical pain\"[ti] OR CPSP[tiab]) AND (chronic*[tiab] OR persistent*[tiab] OR \"3 month*\"[tiab] OR \"follow-up\"[tiab])) AND (preoperat*[tiab] OR presurg*[tiab] OR perioperat*[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab]) AND (prospective[tiab] OR longitudinal[tiab] OR cohort[tiab] OR \"follow-up\"[tiab]))",
    "# Q4: Balanced + scope_only\n((sleep disturbance*[ti] OR sleep disorder*[ti] OR insomnia[ti] OR \"sleep apnea\"[ti] OR \"obstructive sleep apnea\"[ti] OR \"sleep quality\"[ti]) AND (\"postoperative pain\"[ti] OR \"postsurgical pain\"[ti] OR \"persistent postoperative pain\"[ti] OR \"chronic postsurgical pain\"[ti] OR CPSP[ti]) AND (preoperat*[tiab] OR presurg*[tiab] OR perioperat*[tiab]))",
    "# Q5: Balanced + proximity_or_scope_fallback\n((sleep disturbance*[ti] OR sleep disorder*[ti] OR insomnia[ti] OR \"sleep apnea\"[ti] OR \"obstructive sleep apnea\"[ti]) AND (\"persistent postoperative pain\"[ti] OR \"persistent postsurgical pain\"[ti] OR \"chronic postoperative pain\"[ti] OR \"chronic postsurgical pain\"[ti] OR CPSP[tiab]) AND (preoperat*[tiab] OR presurg*[tiab] OR perioperat*[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab]))",
    "# Q6: Balanced + design_plus_filter\n((((\"Sleep Wake Disorders\"[Mesh] OR \"Sleep Initiation and Maintenance Disorders\"[Mesh] OR \"Sleep Apnea Syndromes\"[Mesh] OR \"Narcolepsy\"[Mesh] OR sleep disturbance*[tiab] OR sleep disorder*[tiab] OR insomnia[tiab] OR hypersomnia[tiab] OR narcolep*[tiab] OR \"sleep apnea\"[tiab] OR \"sleep apnoea\"[tiab] OR \"obstructive sleep apnea\"[tiab] OR \"obstructive sleep apnoea\"[tiab] OR \"sleep quality\"[tiab] OR \"sleep quantity\"[tiab] OR \"sleep duration\"[tiab]) AND (\"Pain, Postoperative\"[Mesh] OR \"postoperative pain\"[tiab] OR \"post-operative pain\"[tiab] OR \"postsurgical pain\"[tiab] OR \"post-surgical pain\"[tiab] OR \"persistent postoperative pain\"[tiab] OR \"persistent postsurgical pain\"[tiab] OR \"chronic postoperative pain\"[tiab] OR \"chronic postsurgical pain\"[tiab] OR CPSP[tiab]) AND (preoperat*[tiab] OR presurg*[tiab] OR perioperat*[tiab] OR \"pre-operative\"[tiab] OR \"peri-operative\"[tiab]) AND (chronic*[tiab] OR persistent*[tiab] OR \"3 month*\"[tiab] OR \"three month*\"[tiab] OR \"follow-up\"[tiab]) AND (\"Adult\"[Mesh] OR adult*[tiab]) AND (prospective[tiab] OR longitudinal[tiab] OR cohort[tiab] OR \"follow-up\"[tiab])) AND humans[Filter]) NOT (review[pt] OR meta-analysis[pt] OR letter[pt] OR editorial[pt] OR comment[pt])"
  ],
  "scopus": [
    "# Q1: High-recall\nTITLE-ABS-KEY((sleep disturbance* OR sleep disorder* OR insomnia OR hypersomnia OR narcolep* OR \"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"sleep quality\" OR \"sleep quantity\" OR \"sleep duration\" OR polysomnograph*) AND (\"postoperative pain\" OR \"post-operative pain\" OR \"postsurgical pain\" OR \"post-surgical pain\" OR \"persistent postoperative pain\" OR \"persistent post-operative pain\" OR \"persistent postsurgical pain\" OR \"persistent post-surgical pain\" OR \"chronic postoperative pain\" OR \"chronic post-operative pain\" OR \"chronic postsurgical pain\" OR \"chronic post-surgical pain\" OR cpsp))",
    "# Q2: Balanced\nTITLE-ABS-KEY((sleep disturbance* OR sleep disorder* OR insomnia OR hypersomnia OR narcolep* OR \"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"sleep quality\" OR \"sleep quantity\" OR \"sleep duration\") AND (\"postoperative pain\" OR \"post-operative pain\" OR \"postsurgical pain\" OR \"post-surgical pain\" OR \"persistent postoperative pain\" OR \"persistent postsurgical pain\" OR \"chronic postoperative pain\" OR \"chronic postsurgical pain\" OR cpsp) AND (preoperat* OR presurg* OR perioperat* OR \"pre-operative\" OR \"peri-operative\") AND (chronic* OR persistent* OR \"3 month*\" OR \"three month*\" OR \"follow-up\") AND adult*)",
    "# Q3: High-precision\nTITLE(sleep disturbance* OR sleep disorder* OR insomnia OR hypersomnia OR narcolep* OR \"sleep apnea\" OR \"obstructive sleep apnea\" OR \"sleep quality\") AND TITLE(\"postoperative pain\" OR \"postsurgical pain\" OR \"persistent postoperative pain\" OR \"chronic postsurgical pain\" OR cpsp) AND TITLE-ABS-KEY(preoperat* OR presurg* OR perioperat*) AND TITLE-ABS-KEY(chronic* OR persistent* OR \"follow-up\") AND TITLE-ABS-KEY(adult*) AND TITLE-ABS-KEY(prospective OR longitudinal OR cohort)",
    "# Q4: Balanced + scope_only\nTITLE(sleep disturbance* OR sleep disorder* OR insomnia OR \"sleep apnea\" OR \"obstructive sleep apnea\" OR \"sleep quality\") AND TITLE(\"postoperative pain\" OR \"postsurgical pain\" OR \"persistent postoperative pain\" OR \"chronic postsurgical pain\" OR cpsp) AND TITLE-ABS-KEY(preoperat* OR presurg* OR perioperat*)",
    "# Q5: Balanced + proximity_or_scope_fallback\nTITLE-ABS-KEY(((sleep disturbance* OR sleep disorder* OR insomnia OR hypersomnia OR narcolep* OR \"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"sleep quality\" OR \"sleep quantity\" OR \"sleep duration\") W/10 (\"postoperative pain\" OR \"post-operative pain\" OR \"postsurgical pain\" OR \"post-surgical pain\" OR \"persistent postoperative pain\" OR \"chronic postoperative pain\" OR \"persistent postsurgical pain\" OR \"chronic postsurgical pain\" OR cpsp)) AND (preoperat* OR presurg* OR perioperat*) AND adult*)",
    "# Q6: Balanced + design_plus_filter\nTITLE-ABS-KEY((sleep disturbance* OR sleep disorder* OR insomnia OR hypersomnia OR narcolep* OR \"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"sleep quality\" OR \"sleep quantity\" OR \"sleep duration\") AND (\"postoperative pain\" OR \"post-operative pain\" OR \"postsurgical pain\" OR \"post-surgical pain\" OR \"persistent postoperative pain\" OR \"persistent postsurgical pain\" OR \"chronic postoperative pain\" OR \"chronic postsurgical pain\" OR cpsp) AND (preoperat* OR presurg* OR perioperat* OR \"pre-operative\" OR \"peri-operative\") AND (chronic* OR persistent* OR \"3 month*\" OR \"three month*\" OR \"follow-up\") AND adult*) AND TITLE-ABS-KEY(prospective OR longitudinal OR cohort) AND DOCTYPE(ar)"
  ],
  "wos": [
    "# Q1: High-recall\nTS=((sleep disturbance* OR sleep disorder* OR insomnia OR hypersomnia OR narcolep* OR \"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"sleep quality\" OR \"sleep quantity\" OR \"sleep duration\" OR polysomnograph*) AND (\"postoperative pain\" OR \"post-operative pain\" OR \"postsurgical pain\" OR \"post-surgical pain\" OR \"persistent postoperative pain\" OR \"persistent post-operative pain\" OR \"persistent postsurgical pain\" OR \"persistent post-surgical pain\" OR \"chronic postoperative pain\" OR \"chronic post-operative pain\" OR \"chronic postsurgical pain\" OR \"chronic post-surgical pain\" OR CPSP))",
    "# Q2: Balanced\nTS=((sleep disturbance* OR sleep disorder* OR insomnia OR hypersomnia OR narcolep* OR \"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"sleep quality\" OR \"sleep quantity\" OR \"sleep duration\") AND (\"postoperative pain\" OR \"post-operative pain\" OR \"postsurgical pain\" OR \"post-surgical pain\" OR \"persistent postoperative pain\" OR \"persistent postsurgical pain\" OR \"chronic postoperative pain\" OR \"chronic postsurgical pain\" OR CPSP) AND (preoperat* OR presurg* OR perioperat* OR \"pre-operative\" OR \"peri-operative\") AND (chronic* OR persistent* OR \"3 month*\" OR \"three month*\" OR \"follow-up\") AND adult*)",
    "# Q3: High-precision\nTI=(sleep disturbance* OR sleep disorder* OR insomnia OR hypersomnia OR narcolep* OR \"sleep apnea\" OR \"obstructive sleep apnea\" OR \"sleep quality\") AND TI=(\"postoperative pain\" OR \"postsurgical pain\" OR \"persistent postoperative pain\" OR \"chronic postsurgical pain\" OR CPSP) AND TS=(preoperat* OR presurg* OR perioperat*) AND TS=(chronic* OR persistent* OR \"follow-up\") AND TS=(adult*) AND TS=(prospective OR longitudinal OR cohort)",
    "# Q4: Balanced + scope_only\nTI=(sleep disturbance* OR sleep disorder* OR insomnia OR \"sleep apnea\" OR \"obstructive sleep apnea\" OR \"sleep quality\") AND TI=(\"postoperative pain\" OR \"postsurgical pain\" OR \"persistent postoperative pain\" OR \"chronic postsurgical pain\" OR CPSP) AND TS=(preoperat* OR presurg* OR perioperat*)",
    "# Q5: Balanced + proximity_or_scope_fallback\nTS=(((sleep disturbance* OR sleep disorder* OR insomnia OR hypersomnia OR narcolep* OR \"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"sleep quality\" OR \"sleep quantity\" OR \"sleep duration\") NEAR/10 (\"postoperative pain\" OR \"post-operative pain\" OR \"postsurgical pain\" OR \"post-surgical pain\" OR \"persistent postoperative pain\" OR \"chronic postoperative pain\" OR \"persistent postsurgical pain\" OR \"chronic postsurgical pain\" OR CPSP)) AND (preoperat* OR presurg* OR perioperat*) AND adult*)",
    "# Q6: Balanced + design_plus_filter\nTS=((sleep disturbance* OR sleep disorder* OR insomnia OR hypersomnia OR narcolep* OR \"sleep apnea\" OR \"sleep apnoea\" OR \"obstructive sleep apnea\" OR \"obstructive sleep apnoea\" OR \"sleep quality\" OR \"sleep quantity\" OR \"sleep duration\") AND (\"postoperative pain\" OR \"post-operative pain\" OR \"postsurgical pain\" OR \"post-surgical pain\" OR \"persistent postoperative pain\" OR \"persistent postsurgical pain\" OR \"chronic postoperative pain\" OR \"chronic postsurgical pain\" OR CPSP) AND (preoperat* OR presurg* OR perioperat* OR \"pre-operative\" OR \"peri-operative\") AND (chronic* OR persistent* OR \"3 month*\" OR \"three month*\" OR \"follow-up\") AND adult*) AND TS=(prospective OR longitudinal OR cohort) AND DT=(Article)"
  ],
  "embase": [
    "# Q1: High-recall\n(('sleep disorder'/exp OR 'sleep apnea syndrome'/exp OR 'narcolepsy'/exp OR sleep disturbance*:ti,ab OR sleep disorder*:ti,ab OR insomnia:ti,ab OR hypersomnia:ti,ab OR narcolep*:ti,ab OR 'sleep apnea':ti,ab OR 'sleep apnoea':ti,ab OR 'obstructive sleep apnea':ti,ab OR 'obstructive sleep apnoea':ti,ab OR 'sleep quality':ti,ab OR 'sleep quantity':ti,ab OR 'sleep duration':ti,ab OR polysomnograph*:ti,ab) AND ('postoperative pain'/exp OR 'postoperative pain':ti,ab OR 'post-operative pain':ti,ab OR 'postsurgical pain':ti,ab OR 'post-surgical pain':ti,ab OR 'persistent postoperative pain':ti,ab OR 'persistent post-operative pain':ti,ab OR 'persistent postsurgical pain':ti,ab OR 'persistent post-surgical pain':ti,ab OR 'chronic postoperative pain':ti,ab OR 'chronic post-operative pain':ti,ab OR 'chronic postsurgical pain':ti,ab OR 'chronic post-surgical pain':ti,ab OR cpsp:ti,ab))",
    "# Q2: Balanced\n(('sleep disorder'/exp OR 'sleep apnea syndrome'/exp OR 'narcolepsy'/exp OR sleep disturbance*:ti,ab OR sleep disorder*:ti,ab OR insomnia:ti,ab OR hypersomnia:ti,ab OR narcolep*:ti,ab OR 'sleep apnea':ti,ab OR 'sleep apnoea':ti,ab OR 'obstructive sleep apnea':ti,ab OR 'obstructive sleep apnoea':ti,ab OR 'sleep quality':ti,ab OR 'sleep quantity':ti,ab OR 'sleep duration':ti,ab) AND ('postoperative pain'/exp OR 'postoperative pain':ti,ab OR 'post-operative pain':ti,ab OR 'postsurgical pain':ti,ab OR 'post-surgical pain':ti,ab OR 'persistent postoperative pain':ti,ab OR 'persistent postsurgical pain':ti,ab OR 'chronic postoperative pain':ti,ab OR 'chronic postsurgical pain':ti,ab OR cpsp:ti,ab) AND (preoperat*:ti,ab OR presurg*:ti,ab OR perioperat*:ti,ab OR 'pre-operative':ti,ab OR 'peri-operative':ti,ab) AND (chronic*:ti,ab OR persistent*:ti,ab OR '3 month*':ti,ab OR 'three month*':ti,ab OR 'follow-up':ti,ab) AND ('adult'/exp OR adult*:ti,ab))",
    "# Q3: High-precision\n((('sleep disorder'/mj OR 'sleep apnea syndrome'/mj OR 'narcolepsy'/mj) OR sleep disturbance*:ti OR sleep disorder*:ti OR insomnia:ti OR hypersomnia:ti OR narcolep*:ti OR 'sleep apnea':ti OR 'obstructive sleep apnea':ti OR 'sleep quality':ti) AND (('postoperative pain'/mj OR 'postoperative pain':ti OR 'postsurgical pain':ti OR 'persistent postoperative pain':ti OR 'chronic postsurgical pain':ti OR cpsp:ti,ab) AND (chronic*:ti,ab OR persistent*:ti,ab OR '3 month*':ti,ab OR 'follow-up':ti,ab)) AND (preoperat*:ti,ab OR presurg*:ti,ab OR perioperat*:ti,ab) AND ('adult'/exp OR adult*:ti,ab) AND (prospective:ti,ab OR longitudinal:ti,ab OR cohort:ti,ab OR 'follow-up':ti,ab))",
    "# Q4: Balanced + scope_only\n((sleep disturbance*:ti OR sleep disorder*:ti OR insomnia:ti OR 'sleep apnea':ti OR 'obstructive sleep apnea':ti OR 'sleep quality':ti) AND ('postoperative pain':ti OR 'postsurgical pain':ti OR 'persistent postoperative pain':ti OR 'chronic postsurgical pain':ti OR cpsp:ti) AND (preoperat*:ti,ab OR presurg*:ti,ab OR perioperat*:ti,ab))",
    "# Q5: Balanced + proximity_or_scope_fallback\n((((sleep disturbance* OR sleep disorder* OR insomnia OR hypersomnia OR narcolep* OR 'sleep apnea' OR 'sleep apnoea' OR 'obstructive sleep apnea' OR 'obstructive sleep apnoea' OR 'sleep quality' OR 'sleep quantity' OR 'sleep duration') ADJ10 ('postoperative pain' OR 'post-operative pain' OR 'postsurgical pain' OR 'post-surgical pain' OR 'persistent postoperative pain' OR 'chronic postoperative pain' OR 'persistent postsurgical pain' OR 'chronic postsurgical pain' OR cpsp)):ti,ab AND (preoperat*:ti,ab OR presurg*:ti,ab OR perioperat*:ti,ab) AND ('adult'/exp OR adult*:ti,ab))",
    "# Q6: Balanced + design_plus_filter\n(('sleep disorder'/exp OR 'sleep apnea syndrome'/exp OR 'narcolepsy'/exp OR sleep disturbance*:ti,ab OR sleep disorder*:ti,ab OR insomnia:ti,ab OR hypersomnia:ti,ab OR narcolep*:ti,ab OR 'sleep apnea':ti,ab OR 'sleep apnoea':ti,ab OR 'obstructive sleep apnea':ti,ab OR 'obstructive sleep apnoea':ti,ab OR 'sleep quality':ti,ab OR 'sleep quantity':ti,ab OR 'sleep duration':ti,ab) AND ('postoperative pain'/exp OR 'postoperative pain':ti,ab OR 'post-operative pain':ti,ab OR 'postsurgical pain':ti,ab OR 'post-surgical pain':ti,ab OR 'persistent postoperative pain':ti,ab OR 'persistent postsurgical pain':ti,ab OR 'chronic postoperative pain':ti,ab OR 'chronic postsurgical pain':ti,ab OR cpsp:ti,ab) AND (preoperat*:ti,ab OR presurg*:ti,ab OR perioperat*:ti,ab OR 'pre-operative':ti,ab OR 'peri-operative':ti,ab) AND (chronic*:ti,ab OR persistent*:ti,ab OR '3 month*':ti,ab OR 'three month*':ti,ab OR 'follow-up':ti,ab) AND ('adult'/exp OR adult*:ti,ab) AND (prospective:ti,ab OR longitudinal:ti,ab OR cohort:ti,ab))"
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

- Q1 and Q2 preserve the same mandatory-core route across all databases: sleep disturbance exposure AND post-surgical pain outcomes.
- Preoperative or perioperative timing, chronic or persistent follow-up cues, and adult population wording were treated as recall-aware tightening layers rather than baseline retrieval-defining blocks because many relevant prognostic studies may report them inconsistently in titles or abstracts.
- The bundled variants use only approved cases: `scope_only`, `proximity_or_scope_fallback`, and `design_plus_filter`.
- PubMed uses a scope fallback for Q5 because proximity operators are unavailable.
- Embase is translated consistently in Embase.com syntax.
- The protocol names five acceptable publication languages; those are better applied as interface limits rather than embedded inline across all database strings.
- The secondary outcome of analgesic use was not promoted into the baseline Boolean route because the protocol's main question is centered on chronic post-surgical pain and the analgesic signal is more safely recovered through screening from the broader pain-focused set.