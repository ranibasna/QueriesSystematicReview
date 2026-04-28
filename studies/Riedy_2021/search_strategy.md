# Search Strategy for Riedy_2021

## Study Summary

- Topic: Continuous broadband acoustic noise as a sleep aid, including white noise, pink noise, masking noise, and protocol-explicit natural-sound variants
- Date window: Database inception to 2019-02-28; the protocol reports searching in February 2019, so PubMed uses an end-of-month upper bound, Scopus and Web of Science use year-level approximations, and Embase should apply the same cutoff as an interface limit
- Databases: pubmed, scopus, wos, embase
- Query level: extended
- Retrieval architecture: single_route
- design_analytic_block: active, but limited to late-stage human, language, and document-type constraints because the protocol imposes no study-design restrictions

## PICOS Summary

- Population: Human subjects only, including neonates, infants, children, and adults
- Intervention or Exposure: Continuous broadband acoustic noise played during sleep or sleep onset, including white noise, pink noise, broadband noise, masking noise, and protocol-explicit natural sounds such as ocean waves, rainfall, waterfalls, and flowing water
- Comparator: Sleep without the noise intervention
- Outcomes: Sleep onset latency, sleep continuity, sleep quality, arousals, awakenings, wakefulness after sleep onset, total sleep time, sleep efficiency, sleep fragmentation, and sleep architecture
- Design: No study-design restrictions; journal articles and conference proceedings only, English language only

## Architecture Selection Summary

- Selected retrieval architecture: `single_route`
- `design_analytic_block`: active

### Concept Roles

| Role | Assigned concepts |
| --- | --- |
| mandatory_core | Intervention block for continuous broadband acoustic noise used during sleep or sleep onset; sleep-outcome block for sleep and wakefulness outcomes including latency, continuity, quality, awakenings, arousals, WASO, total sleep time, sleep efficiency, fragmentation, and architecture |
| optional_precision | Device wording such as noise machine or sound machine; tighter title-only scope; proximity coupling between intervention and sleep-outcome wording where the database supports it |
| filter_only | Humans restriction; English-language limit; article or proceedings-document restriction; review or editorial publication-type exclusions where platform-safe |
| screening_only | No-noise comparator wording; setting terms such as hospital, home, travel, or laboratory; exclusion of intermittent or burst noise used to disturb sleep or enhance slow-wave sleep; quality-assessment features such as sample size or statistical rigor |

The protocol describes one coherent Boolean route linking a noise-intervention concept block to a sleep-outcome concept block. It does not justify separate indexed and textword retrieval routes for the same subject matter, so `dual_route_union` is not warranted. The active `design_analytic_block` remains conservative because the protocol explicitly allows all study designs, while humans, English-language, and document-type restrictions are retrieval-safe only in later balanced or precision variants.

## Concept Tables

### Concept to MeSH or Emtree

| concept | term | tree note | explode? | rationale and source |
| --- | --- | --- | --- | --- |
| intervention core | Noise / noise | indexed umbrella for acoustic-noise exposure | Yes | PROSPERO MeSH list, keywords, and intervention description |
| outcome core | Sleep / sleep | indexed umbrella for the sleep-outcome domain | Yes | Review objective, keywords, and main outcomes |
| outcome core | Wakefulness / wakefulness | indexed counterpart for wakefulness and WASO outcomes | Yes | Review objective and main outcomes |
| outcome core | Sleep Initiation and Maintenance Disorders / text-led maintenance wording in non-PubMed translations | indexed proxy for sleep latency and sleep-maintenance outcomes | Yes where supported | PROSPERO MeSH list and objective wording |
| filter block | Humans / human | population limiter rather than a topic concept | No | Protocol population restriction |

### Concept to Textword

| concept | synonym or phrase | field | truncation? | source |
| --- | --- | --- | --- | --- |
| intervention core | white noise; pink noise; broadband noise; broad band noise; masking noise; acoustic noise; continuous noise; continuous broadband acoustic noise | title, abstract, topic | No | Protocol objective, keywords, and intervention description |
| intervention core | natural sound*; nature sound*; ocean wave*; rainfall; waterfall*; flowing water; water sound* | title, abstract, topic | Mixed | Protocol intervention description |
| optional precision | noise machine*; sound machine*; sleep sound* | title, abstract, topic | Mixed | Protocol objective and condition description |
| outcome core | sleep; sleep onset; sleep onset latency; sleep latency; sleep continuity; sleep quality; sleep efficiency; total sleep time | title, abstract, topic | No | Protocol objective and main outcomes |
| outcome core | wakefulness after sleep onset; WASO; wakefulness; awakening*; arousal*; sleep fragmentation; sleep architecture; sleep maintenance | title, abstract, topic | Mixed | Protocol main outcomes |
| screening only | hospital; home; travel; laboratory; control; comparator; crossover; randomized; slow wave sleep enhancement; burst noise | title, abstract, topic | Mixed | Protocol context, comparator, and exclusion wording |

## JSON Query Object

```json
{
  "pubmed": [
    "# Q1: High-recall\n((\"Noise\"[Mesh] OR \"white noise\"[tiab] OR \"pink noise\"[tiab] OR \"broadband noise\"[tiab] OR \"broad band noise\"[tiab] OR \"masking noise\"[tiab] OR \"acoustic noise\"[tiab] OR \"continuous noise\"[tiab] OR \"continuous broadband acoustic noise\"[tiab] OR \"noise machine*\"[tiab] OR \"sound machine*\"[tiab] OR \"sleep sound*\"[tiab] OR \"natural sound*\"[tiab] OR \"nature sound*\"[tiab] OR \"ocean wave*\"[tiab] OR rainfall[tiab] OR waterfall*[tiab] OR \"flowing water\"[tiab] OR \"water sound*\"[tiab] OR \"broadband acoustic noise\"[tiab]) AND (\"Sleep\"[Mesh] OR \"Wakefulness\"[Mesh] OR \"Sleep Initiation and Maintenance Disorders\"[Mesh] OR \"Sleep Stages\"[Mesh] OR sleep[tiab] OR \"sleep onset\"[tiab] OR \"sleep onset latency\"[tiab] OR \"sleep latency\"[tiab] OR \"sleep continuity\"[tiab] OR \"sleep quality\"[tiab] OR \"sleep efficiency\"[tiab] OR \"total sleep time\"[tiab] OR \"wakefulness after sleep onset\"[tiab] OR WASO[tiab] OR wakefulness[tiab] OR awakening*[tiab] OR arousal*[tiab] OR \"sleep fragmentation\"[tiab] OR \"sleep architecture\"[tiab] OR \"sleep maintenance\"[tiab])) AND (\"0001/01/01\"[Date - Publication] : \"2019/02/28\"[Date - Publication])",
    "# Q2: Balanced\n((\"Noise\"[Mesh] OR \"white noise\"[tiab] OR \"pink noise\"[tiab] OR \"broadband noise\"[tiab] OR \"masking noise\"[tiab] OR \"acoustic noise\"[tiab] OR \"continuous noise\"[tiab] OR \"noise machine*\"[tiab] OR \"sound machine*\"[tiab] OR \"natural sound*\"[tiab] OR \"broadband acoustic noise\"[tiab]) AND (\"Sleep\"[Mesh] OR \"Wakefulness\"[Mesh] OR \"Sleep Initiation and Maintenance Disorders\"[Mesh] OR \"sleep onset latency\"[tiab] OR \"sleep latency\"[tiab] OR \"sleep continuity\"[tiab] OR \"sleep quality\"[tiab] OR \"sleep efficiency\"[tiab] OR \"total sleep time\"[tiab] OR \"wakefulness after sleep onset\"[tiab] OR WASO[tiab] OR wakefulness[tiab] OR awakening*[tiab] OR arousal*[tiab] OR \"sleep fragmentation\"[tiab] OR \"sleep architecture\"[tiab])) AND humans[Filter] AND (\"0001/01/01\"[Date - Publication] : \"2019/02/28\"[Date - Publication])",
    "# Q3: High-precision\n((((\"Noise\"[Majr] OR \"white noise\"[ti] OR \"pink noise\"[ti] OR \"broadband noise\"[ti] OR \"masking noise\"[ti] OR \"noise machine\"[ti] OR \"sound machine\"[ti] OR \"acoustic noise\"[ti] OR \"continuous noise\"[ti]) AND (\"Sleep\"[Majr] OR \"Wakefulness\"[Majr] OR \"sleep onset latency\"[ti] OR \"sleep latency\"[ti] OR \"sleep quality\"[ti] OR \"sleep efficiency\"[ti] OR \"wakefulness after sleep onset\"[ti] OR \"sleep continuity\"[ti] OR \"sleep fragmentation\"[ti] OR \"sleep architecture\"[ti])) AND humans[Filter] AND english[Filter]) NOT (review[pt] OR meta-analysis[pt] OR letter[pt] OR editorial[pt] OR comment[pt])) AND (\"0001/01/01\"[Date - Publication] : \"2019/02/28\"[Date - Publication])",
    "# Q4: Balanced + scope_only\n((\"white noise\"[ti] OR \"pink noise\"[ti] OR \"broadband noise\"[ti] OR \"masking noise\"[ti] OR \"noise machine\"[ti] OR \"sound machine\"[ti] OR \"acoustic noise\"[ti] OR \"continuous noise\"[ti]) AND (sleep[ti] OR \"sleep onset\"[ti] OR \"sleep latency\"[ti] OR \"sleep quality\"[ti] OR \"sleep efficiency\"[ti] OR wakefulness[ti] OR WASO[ti] OR \"sleep fragmentation\"[ti] OR \"sleep continuity\"[ti])) AND (\"0001/01/01\"[Date - Publication] : \"2019/02/28\"[Date - Publication])",
    "# Q5: Balanced + scope_plus_filter\n(((\"white noise\"[ti] OR \"pink noise\"[ti] OR \"broadband noise\"[ti] OR \"masking noise\"[ti] OR \"noise machine\"[ti] OR \"sound machine\"[ti] OR \"acoustic noise\"[ti] OR \"continuous noise\"[ti]) AND (\"Sleep\"[Mesh] OR \"Wakefulness\"[Mesh] OR \"sleep onset latency\"[tiab] OR \"sleep latency\"[tiab] OR \"sleep quality\"[tiab] OR \"sleep efficiency\"[tiab] OR \"wakefulness after sleep onset\"[tiab] OR WASO[tiab] OR \"sleep continuity\"[tiab] OR \"sleep fragmentation\"[tiab])) AND humans[Filter] AND english[Filter]) AND (\"0001/01/01\"[Date - Publication] : \"2019/02/28\"[Date - Publication])",
    "# Q6: Balanced + proximity_or_scope_fallback\n(((\"Noise\"[Majr] OR \"white noise\"[ti] OR \"pink noise\"[ti] OR \"broadband noise\"[ti] OR \"masking noise\"[ti] OR \"noise machine\"[ti] OR \"sound machine\"[ti] OR \"acoustic noise\"[ti] OR \"continuous noise\"[ti]) AND (\"Sleep\"[Majr] OR \"Wakefulness\"[Majr] OR \"sleep latency\"[ti] OR \"sleep quality\"[ti] OR \"sleep efficiency\"[ti] OR \"wakefulness after sleep onset\"[ti] OR \"sleep continuity\"[ti] OR \"sleep fragmentation\"[ti])) AND humans[Filter]) AND (\"0001/01/01\"[Date - Publication] : \"2019/02/28\"[Date - Publication])"
  ],
  "scopus": [
    "# Q1: High-recall\nTITLE-ABS-KEY(((\"white noise\" OR \"pink noise\" OR \"broadband noise\" OR \"broad band noise\" OR \"masking noise\" OR \"acoustic noise\" OR \"continuous noise\" OR \"continuous broadband acoustic noise\" OR \"noise machine*\" OR \"sound machine*\" OR \"sleep sound*\" OR \"natural sound*\" OR \"nature sound*\" OR \"ocean wave*\" OR rainfall OR waterfall* OR \"flowing water\" OR \"water sound*\" OR \"broadband acoustic noise\" OR (noise W/3 (white OR pink OR broadband OR acoustic OR masking OR continuous OR machine* OR sound*))) AND (sleep OR \"sleep onset\" OR \"sleep onset latency\" OR \"sleep latency\" OR \"sleep continuity\" OR \"sleep quality\" OR \"sleep efficiency\" OR \"total sleep time\" OR \"wakefulness after sleep onset\" OR WASO OR wakefulness OR awakening* OR arousal* OR \"sleep fragmentation\" OR \"sleep architecture\" OR \"sleep maintenance\"))) AND PUBYEAR < 2020",
    "# Q2: Balanced\nTITLE-ABS-KEY(((\"white noise\" OR \"pink noise\" OR \"broadband noise\" OR \"masking noise\" OR \"acoustic noise\" OR \"continuous noise\" OR \"noise machine*\" OR \"sound machine*\" OR \"natural sound*\" OR \"broadband acoustic noise\") AND (\"sleep onset latency\" OR \"sleep latency\" OR \"sleep continuity\" OR \"sleep quality\" OR \"sleep efficiency\" OR \"total sleep time\" OR \"wakefulness after sleep onset\" OR WASO OR wakefulness OR awakening* OR arousal* OR \"sleep fragmentation\" OR \"sleep architecture\" OR sleep))) AND DOCTYPE(ar OR cp) AND PUBYEAR < 2020",
    "# Q3: High-precision\nTITLE(\"white noise\" OR \"pink noise\" OR \"broadband noise\" OR \"masking noise\" OR \"noise machine\" OR \"sound machine\" OR \"acoustic noise\" OR \"continuous noise\") AND TITLE(\"sleep latency\" OR \"sleep quality\" OR \"sleep efficiency\" OR \"sleep fragmentation\" OR \"sleep continuity\" OR wakefulness OR sleep) AND DOCTYPE(ar OR cp) AND PUBYEAR < 2020",
    "# Q4: Balanced + scope_only\nTITLE(\"white noise\" OR \"pink noise\" OR \"broadband noise\" OR \"masking noise\" OR \"noise machine\" OR \"sound machine\" OR \"acoustic noise\" OR \"continuous noise\") AND TITLE(sleep OR \"sleep latency\" OR \"sleep quality\" OR \"sleep efficiency\" OR \"sleep fragmentation\" OR \"sleep continuity\" OR wakefulness) AND PUBYEAR < 2020",
    "# Q5: Balanced + scope_plus_filter\nTITLE(\"white noise\" OR \"pink noise\" OR \"broadband noise\" OR \"masking noise\" OR \"noise machine\" OR \"sound machine\" OR \"acoustic noise\" OR \"continuous noise\") AND TITLE-ABS-KEY(\"sleep onset latency\" OR \"sleep latency\" OR \"sleep quality\" OR \"sleep efficiency\" OR \"wakefulness after sleep onset\" OR WASO OR \"sleep continuity\" OR \"sleep fragmentation\" OR wakefulness OR sleep) AND DOCTYPE(ar OR cp) AND PUBYEAR < 2020",
    "# Q6: Balanced + proximity_or_scope_fallback\nTITLE-ABS-KEY(((\"white noise\" OR \"pink noise\" OR \"broadband noise\" OR \"masking noise\" OR \"noise machine*\" OR \"sound machine*\" OR \"acoustic noise\" OR \"continuous noise\") W/5 (sleep OR latency OR quality OR efficiency OR wakefulness OR awakening* OR arousal* OR fragmentation OR continuity))) AND DOCTYPE(ar OR cp) AND PUBYEAR < 2020"
  ],
  "wos": [
    "# Q1: High-recall\nTS=(((\"white noise\" OR \"pink noise\" OR \"broadband noise\" OR \"broad band noise\" OR \"masking noise\" OR \"acoustic noise\" OR \"continuous noise\" OR \"continuous broadband acoustic noise\" OR \"noise machine*\" OR \"sound machine*\" OR \"sleep sound*\" OR \"natural sound*\" OR \"nature sound*\" OR \"ocean wave*\" OR rainfall OR waterfall* OR \"flowing water\" OR \"water sound*\" OR \"broadband acoustic noise\") AND (sleep OR \"sleep onset\" OR \"sleep onset latency\" OR \"sleep latency\" OR \"sleep continuity\" OR \"sleep quality\" OR \"sleep efficiency\" OR \"total sleep time\" OR \"wakefulness after sleep onset\" OR WASO OR wakefulness OR awakening* OR arousal* OR \"sleep fragmentation\" OR \"sleep architecture\" OR \"sleep maintenance\"))) AND PY=(1900-2019)",
    "# Q2: Balanced\nTS=(((\"white noise\" OR \"pink noise\" OR \"broadband noise\" OR \"masking noise\" OR \"acoustic noise\" OR \"continuous noise\" OR \"noise machine*\" OR \"sound machine*\" OR \"natural sound*\" OR \"broadband acoustic noise\") AND (\"sleep onset latency\" OR \"sleep latency\" OR \"sleep continuity\" OR \"sleep quality\" OR \"sleep efficiency\" OR \"total sleep time\" OR \"wakefulness after sleep onset\" OR WASO OR wakefulness OR awakening* OR arousal* OR \"sleep fragmentation\" OR \"sleep architecture\" OR sleep))) AND DT=(Article OR Proceedings Paper) AND PY=(1900-2019)",
    "# Q3: High-precision\nTI=(\"white noise\" OR \"pink noise\" OR \"broadband noise\" OR \"masking noise\" OR \"noise machine\" OR \"sound machine\" OR \"acoustic noise\" OR \"continuous noise\") AND TI=(\"sleep latency\" OR \"sleep quality\" OR \"sleep efficiency\" OR \"sleep fragmentation\" OR \"sleep continuity\" OR wakefulness OR sleep) AND DT=(Article OR Proceedings Paper) AND PY=(1900-2019)",
    "# Q4: Balanced + scope_only\nTI=(\"white noise\" OR \"pink noise\" OR \"broadband noise\" OR \"masking noise\" OR \"noise machine\" OR \"sound machine\" OR \"acoustic noise\" OR \"continuous noise\") AND TI=(sleep OR \"sleep latency\" OR \"sleep quality\" OR \"sleep efficiency\" OR \"sleep fragmentation\" OR \"sleep continuity\" OR wakefulness) AND PY=(1900-2019)",
    "# Q5: Balanced + scope_plus_filter\nTI=(\"white noise\" OR \"pink noise\" OR \"broadband noise\" OR \"masking noise\" OR \"noise machine\" OR \"sound machine\" OR \"acoustic noise\" OR \"continuous noise\") AND TS=(\"sleep onset latency\" OR \"sleep latency\" OR \"sleep quality\" OR \"sleep efficiency\" OR \"wakefulness after sleep onset\" OR WASO OR \"sleep continuity\" OR \"sleep fragmentation\" OR wakefulness OR sleep) AND DT=(Article OR Proceedings Paper) AND PY=(1900-2019)",
    "# Q6: Balanced + proximity_or_scope_fallback\nTS=(((\"white noise\" OR \"pink noise\" OR \"broadband noise\" OR \"masking noise\" OR \"noise machine*\" OR \"sound machine*\" OR \"acoustic noise\" OR \"continuous noise\") NEAR/5 (sleep OR latency OR quality OR efficiency OR wakefulness OR awakening* OR arousal* OR fragmentation OR continuity))) AND DT=(Article OR Proceedings Paper) AND PY=(1900-2019)"
  ],
  "embase": [
    "# Q1: High-recall\n(('noise'/exp OR 'white noise':ti,ab OR 'pink noise':ti,ab OR 'broadband noise':ti,ab OR 'broad band noise':ti,ab OR 'masking noise':ti,ab OR 'acoustic noise':ti,ab OR 'continuous noise':ti,ab OR 'continuous broadband acoustic noise':ti,ab OR 'noise machine*':ti,ab OR 'sound machine*':ti,ab OR 'sleep sound*':ti,ab OR 'natural sound*':ti,ab OR 'nature sound*':ti,ab OR 'ocean wave*':ti,ab OR rainfall:ti,ab OR waterfall*:ti,ab OR 'flowing water':ti,ab OR 'water sound*':ti,ab OR 'broadband acoustic noise':ti,ab) AND ('sleep'/exp OR 'wakefulness'/exp OR 'sleep onset':ti,ab OR 'sleep onset latency':ti,ab OR 'sleep latency':ti,ab OR 'sleep continuity':ti,ab OR 'sleep quality':ti,ab OR 'sleep efficiency':ti,ab OR 'total sleep time':ti,ab OR 'wakefulness after sleep onset':ti,ab OR waso:ti,ab OR wakefulness:ti,ab OR awakening*:ti,ab OR arousal*:ti,ab OR 'sleep fragmentation':ti,ab OR 'sleep architecture':ti,ab OR 'sleep maintenance':ti,ab))",
    "# Q2: Balanced\n((('noise'/exp OR 'white noise':ti,ab OR 'pink noise':ti,ab OR 'broadband noise':ti,ab OR 'masking noise':ti,ab OR 'acoustic noise':ti,ab OR 'continuous noise':ti,ab OR 'noise machine*':ti,ab OR 'sound machine*':ti,ab OR 'natural sound*':ti,ab OR 'broadband acoustic noise':ti,ab) AND ('sleep'/exp OR 'wakefulness'/exp OR 'sleep onset latency':ti,ab OR 'sleep latency':ti,ab OR 'sleep continuity':ti,ab OR 'sleep quality':ti,ab OR 'sleep efficiency':ti,ab OR 'total sleep time':ti,ab OR 'wakefulness after sleep onset':ti,ab OR waso:ti,ab OR wakefulness:ti,ab OR awakening*:ti,ab OR arousal*:ti,ab OR 'sleep fragmentation':ti,ab OR 'sleep architecture':ti,ab)) NOT ('review'/it OR 'systematic review'/it OR 'meta analysis'/it OR 'letter'/it OR 'editorial'/it))",
    "# Q3: High-precision\n((('noise'/mj OR 'white noise':ti OR 'pink noise':ti OR 'broadband noise':ti OR 'masking noise':ti OR 'noise machine':ti OR 'sound machine':ti OR 'acoustic noise':ti OR 'continuous noise':ti) AND ('sleep'/mj OR 'wakefulness'/mj OR 'sleep latency':ti OR 'sleep quality':ti OR 'sleep efficiency':ti OR 'wakefulness after sleep onset':ti OR 'sleep continuity':ti OR 'sleep fragmentation':ti OR 'sleep architecture':ti)) NOT ('review'/it OR 'systematic review'/it OR 'meta analysis'/it OR 'letter'/it OR 'editorial'/it OR 'case report'/it))",
    "# Q4: Balanced + scope_only\n(('white noise':ti OR 'pink noise':ti OR 'broadband noise':ti OR 'masking noise':ti OR 'noise machine':ti OR 'sound machine':ti OR 'acoustic noise':ti OR 'continuous noise':ti) AND (sleep:ti OR 'sleep latency':ti OR 'sleep quality':ti OR 'sleep efficiency':ti OR 'sleep fragmentation':ti OR 'sleep continuity':ti OR wakefulness:ti))",
    "# Q5: Balanced + scope_plus_filter\n((('white noise':ti OR 'pink noise':ti OR 'broadband noise':ti OR 'masking noise':ti OR 'noise machine':ti OR 'sound machine':ti OR 'acoustic noise':ti OR 'continuous noise':ti) AND ('sleep onset latency':ti,ab OR 'sleep latency':ti,ab OR 'sleep quality':ti,ab OR 'sleep efficiency':ti,ab OR 'wakefulness after sleep onset':ti,ab OR waso:ti,ab OR 'sleep continuity':ti,ab OR 'sleep fragmentation':ti,ab OR wakefulness:ti,ab OR sleep:ti,ab)) NOT ('review'/it OR 'systematic review'/it OR 'meta analysis'/it OR 'letter'/it OR 'editorial'/it))",
    "# Q6: Balanced + proximity_or_scope_fallback\n((((('white noise' OR 'pink noise' OR 'broadband noise' OR 'masking noise' OR 'noise machine*' OR 'sound machine*' OR 'acoustic noise' OR 'continuous noise') ADJ5 (sleep OR latency OR quality OR efficiency OR wakefulness OR awakening* OR arousal* OR fragmentation OR continuity)):ti,ab)) NOT ('review'/it OR 'systematic review'/it OR 'meta analysis'/it OR 'letter'/it OR 'editorial'/it))"
  ]
}
```

## PRESS Self-Check

```json
{
  "json_patch": {}
}
```

- Q1 and Q2 preserve the same mandatory-core route for all databases: a continuous-noise intervention block and a sleep-outcome block.
- The protocol's natural-sound exemplars are retained in Q1 because they are explicit eligibility content, then reduced in Q2 and later variants to avoid drift into broader sound-therapy literature.
- Humans, English, and document-type restrictions are delayed until balanced or precision variants because the protocol imposes no design restrictions and does not justify narrowing baseline Q1.
- The bundled cases use only approved variants: `scope_only`, `scope_plus_filter`, and `proximity_or_scope_fallback`.

## Translation Notes

- The protocol gives only `February 2019` as the search month, so PubMed uses `2019/02/28` as a concrete upper bound, Scopus uses `PUBYEAR < 2020`, and Web of Science uses `PY=(1900-2019)`.
- Embase is translated consistently in Embase.com syntax. The date cutoff should be applied as an interface limit rather than an inline date clause.
- No comparator wording was placed in baseline retrieval because the comparator is an eligibility condition, not a topic-defining concept block.
- Intermittent or burst noise used to disturb sleep or enhance slow-wave sleep remains a screening-stage exclusion rather than a retrieval constraint, which preserves recall within the protocol-supported intervention block.