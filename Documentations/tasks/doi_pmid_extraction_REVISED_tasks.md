# DOI and PMID Extraction Automation - REVISED Task Breakdown

**Project**: Systematic Review Queries  
**Feature**: Automated ID Lookup for Included Studies  
**Approach**: Deterministic Extraction + API Lookups  
**Last Updated**: January 22, 2026

---

## Phase 1: Included Studies Extraction ✅ COMPLETE

### Task 1.1: Implement Table Parser ✅ COMPLETE (4 hours actual)
**Status**: ✅ Done  
**Owner**: System  
**Completion Date**: Jan 22, 2026

**Deliverables**:
- [x] `scripts/extract_included_studies.py` (450 lines)
- [x] Table detection with 5+ heading patterns
- [x] Reference number extraction from table cells
- [x] Citation parsing (author, year, title, journal, volume, pages)
- [x] JSON output with structured data

**Test Coverage**:
- [x] 12 unit tests passing
- [x] Validated on ai_2022 (14/14 studies extracted)
- [x] Processing time: <1 second
- [x] Cost: $0

---

## Phase 2: API-Based ID Lookup (35 hours estimated)

### Task 2.1: Implement PubMed E-utilities Lookup ⏳ IN PROGRESS (8 hours)
**Priority**: HIGHEST  
**Owner**: TBD  
**Target Date**: Jan 23, 2026

**Requirements**:
- Install Biopython: `pip install biopython`
- PubMed API key (optional, for higher rate limits)
- Email address for Entrez API

**Implementation**:

#### Subtask 2.1.1: Create PubMed Search Module (3 hours)
**File**: `scripts/lookup_pmid.py`

**Functions to implement**:
```python
def search_pubmed(
    title: str,
    first_author: str,
    year: int,
    email: str,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search PubMed for studies matching title, author, year.
    
    Returns:
        List of dicts with keys: pmid, doi, title, authors, similarity_score
    """
    pass

def fetch_pubmed_details(
    pmid: str,
    email: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch full metadata for a PMID.
    
    Returns:
        Dict with: pmid, doi, title, authors, journal, year, abstract
    """
    pass

def calculate_title_similarity(title1: str, title2: str) -> float:
    """
    Calculate similarity between two titles using fuzzy matching.
    
    Uses rapidfuzz for comparison.
    Returns: float between 0.0 and 1.0
    """
    pass
```

**Search Strategy**:
1. Clean title (remove special chars, lowercase)
2. Extract last name from first_author
3. Build query: `{title}[Title] AND {last_name}[Author] AND {year}[PDAT]`
4. Execute esearch
5. For each result, fetch details with efetch
6. Calculate title similarity
7. Return matches sorted by similarity

**Rate Limiting**:
- Without API key: 3 requests/second
- With API key: 10 requests/second
- Implement exponential backoff for errors

#### Subtask 2.1.2: Add Fuzzy Matching (2 hours)
**File**: `scripts/lookup_pmid.py`

**Requirements**:
- Install: `pip install rapidfuzz`

**Logic**:
```python
from rapidfuzz import fuzz

def fuzzy_match_study(
    extracted_study: Dict,
    pubmed_results: List[Dict]
) -> Optional[Dict]:
    """
    Find best match using fuzzy string matching.
    
    Scoring:
    - Title similarity: 70% weight
    - Author match: 20% weight
    - Year match: 10% weight
    
    Returns: Best match with confidence score
    """
    pass
```

**Confidence Thresholds**:
- Exact match (1 result, title similarity > 0.95): confidence = 0.95
- Strong match (title similarity > 0.90): confidence = 0.85
- Weak match (title similarity 0.80-0.90): confidence = 0.70
- No good match (similarity < 0.80): confidence = 0.0

#### Subtask 2.1.3: Integration with Extraction Script (2 hours)
**File**: `scripts/extract_included_studies.py`

**Changes**:
1. Add CLI flag: `--lookup-pmid`
2. Add CLI flag: `--pubmed-email` (required for lookup)
3. Add CLI flag: `--pubmed-api-key` (optional)
4. After extraction, if `--lookup-pmid`:
   - For each study without PMID
   - Call `search_pubmed()`
   - Add to output: `pmid_lookup_result`, `pmid_confidence`, `pmid_source`

**Output Format**:
```json
{
  "study_name": "ai_2022",
  "included_studies": [
    {
      "reference_number": 12,
      "first_author": "Li AM",
      "year": 2008,
      "title": "Ambulatory blood pressure...",
      "pmid": null,
      "pmid_lookup": {
        "pmid": "18388205",
        "doi": "10.1136/thx.2007.091132",
        "confidence": 0.95,
        "source": "pubmed_exact",
        "timestamp": "2026-01-22T10:30:00Z"
      }
    }
  ]
}
```

#### Subtask 2.1.4: Unit Tests (1 hour)
**File**: `tests/test_lookup_pmid.py`

**Test Cases**:
- [ ] Test exact title match
- [ ] Test fuzzy match (title with typo)
- [ ] Test no matches found
- [ ] Test multiple matches (disambiguation)
- [ ] Test rate limiting
- [ ] Test API error handling
- [ ] Test with mock PubMed responses

**Deliverable**: PubMed lookup working with >85% success rate

---

### Task 2.2: Implement CrossRef DOI Lookup (6 hours)
**Priority**: MEDIUM  
**Owner**: TBD  
**Target Date**: Jan 24, 2026

**Requirements**:
- No API key needed
- User-Agent header with email (polite pool)

**Implementation**:

#### Subtask 2.2.1: Create CrossRef Search Module (3 hours)
**File**: `scripts/lookup_doi.py`

**Functions**:
```python
def search_crossref(
    title: str,
    author: str,
    year: int,
    email: str
) -> List[Dict[str, Any]]:
    """
    Search CrossRef for DOI.
    
    Returns:
        List of dicts with: doi, title, authors, score
    """
    pass

def fetch_crossref_details(doi: str, email: str) -> Dict[str, Any]:
    """
    Fetch full metadata for a DOI.
    """
    pass

def doi_to_pmid(doi: str, email: str) -> Optional[str]:
    """
    Reverse lookup PMID from DOI using PubMed.
    """
    pass
```

**Search Strategy**:
1. Use `/works` endpoint
2. Query params:
   - `query.title`: cleaned title
   - `query.author`: last name
   - `filter`: `from-pub-date:{year},until-pub-date:{year}`
   - `rows`: 5
3. Filter results with score > 0.85
4. Return top matches

**Rate Limiting**:
- Polite pool: 50 req/second
- Add email to User-Agent header
- Sleep 100ms between requests

#### Subtask 2.2.2: Integration (2 hours)
**File**: `scripts/extract_included_studies.py`

**Changes**:
1. Add CLI flag: `--lookup-doi`
2. Add CLI flag: `--crossref-email` (required)
3. For studies without DOI:
   - Call `search_crossref()`
   - If DOI found, reverse lookup PMID with `doi_to_pmid()`
   - Add results to output

#### Subtask 2.2.3: Unit Tests (1 hour)
**File**: `tests/test_lookup_doi.py`

**Test Cases**:
- [ ] Test DOI lookup
- [ ] Test reverse PMID lookup from DOI
- [ ] Test no matches
- [ ] Test score filtering
- [ ] Test with mock CrossRef API

**Deliverable**: DOI lookup working for non-biomedical papers

---

### Task 2.3: Implement Unified Orchestrator (10 hours)
**Priority**: HIGH  
**Owner**: TBD  
**Target Date**: Jan 25-26, 2026

**Requirements**:
- All lookup modules from 2.1 and 2.2
- Async HTTP library: `pip install aiohttp`

**Implementation**:

#### Subtask 2.3.1: Create Orchestrator Module (5 hours)
**File**: `scripts/enrich_studies.py`

**Main Function**:
```python
async def enrich_study(
    study: Dict,
    methods: List[str],  # ['pubmed', 'crossref', 'web']
    confidence_threshold: float,
    config: Dict
) -> Dict:
    """
    Enrich single study with DOI/PMID using multi-tier fallback.
    
    Logic:
    1. If PMID/DOI already exists, return as-is
    2. Try PubMed lookup
       - If confidence >= threshold, accept and return
    3. Try CrossRef lookup
       - If DOI found, reverse lookup PMID
       - If confidence >= threshold, accept and return
    4. If all methods fail, flag for manual review
    
    Returns:
        Enriched study dict with lookup metadata
    """
    pass

async def enrich_all_studies(
    input_file: str,
    output_file: str,
    methods: List[str],
    confidence_threshold: float,
    config: Dict
) -> Dict[str, Any]:
    """
    Enrich all studies in parallel.
    
    Returns:
        Statistics dict with success rates
    """
    pass
```

**Fallback Strategy**:
```
For each study:
1. Check if PMID/DOI exists → Skip
2. PubMed search → If confidence >= 0.80 → Accept
3. CrossRef search → If score >= 0.85 → Accept
4. Web search (if enabled) → confidence = 0.50 → Manual review
5. No matches → Flag for manual review
```

#### Subtask 2.3.2: CLI Implementation (2 hours)
**File**: `scripts/enrich_studies.py`

**CLI Interface**:
```bash
python scripts/enrich_studies.py <study_name> \
  --methods pubmed,crossref \
  --confidence-threshold 0.80 \
  --pubmed-email your@email.com \
  --pubmed-api-key XXXXXX \
  --crossref-email your@email.com \
  --output studies/{study_name}/enriched_studies.json \
  --parallel 5  # Number of concurrent lookups
```

#### Subtask 2.3.3: Statistics & Reporting (2 hours)
**File**: `scripts/enrich_studies.py`

**Output Statistics**:
```json
{
  "study_name": "ai_2022",
  "processing_time_seconds": 42.5,
  "statistics": {
    "total_studies": 14,
    "already_had_pmid": 0,
    "already_had_doi": 0,
    "pmid_found_pubmed": 12,
    "doi_found_crossref": 2,
    "manual_review_needed": 2,
    "lookup_success_rate": 0.857
  },
  "enriched_studies": [...]
}
```

**Console Output**:
```
🔍 Enriching Studies: ai_2022
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Loading included studies...
✓ Loaded 14 studies from included_studies.json

Step 2: PubMed lookup...
  [1/14] Li AM (2008) → PMID: 18388205 (confidence: 0.95) ✓
  [2/14] Amin RS (2004) → PMID: 14764433 (confidence: 0.93) ✓
  [3/14] Chan KC (2020) → PMID: 32209641 (confidence: 0.96) ✓
  ...
  [14/14] O'Driscoll DM (2011) → PMID: 21521626 (confidence: 0.90) ✓

Step 3: CrossRef fallback...
  [12/14] Study needs DOI lookup...
  → DOI: 10.1136/thx.2007.091132 (score: 0.92) ✓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Results:
   Total studies: 14
   PMID found: 12 (85.7%)
   DOI found: 13 (92.9%)
   Manual review: 2 (14.3%)

✅ Enrichment complete!
✓ Saved to: studies/ai_2022/enriched_studies.json
```

#### Subtask 2.3.4: Integration Tests (1 hour)
**File**: `tests/test_enrich_studies.py`

**Test Cases**:
- [ ] Test full enrichment pipeline
- [ ] Test parallel processing
- [ ] Test fallback logic
- [ ] Test confidence scoring
- [ ] Test error handling
- [ ] Test with mock APIs

**Deliverable**: Complete enrichment pipeline with multi-tier fallback

---

### Task 2.4: Validation & Metrics (4 hours)
**Priority**: HIGH  
**Owner**: TBD  
**Target Date**: Jan 27, 2026

**Implementation**:

#### Subtask 2.4.1: Run Enrichment on ai_2022 (1 hour)
**Action**:
```bash
python scripts/enrich_studies.py ai_2022 \
  --methods pubmed,crossref \
  --confidence-threshold 0.80 \
  --pubmed-email your@email.com
```

**Expected**:
- 14 studies processed
- >12 PMIDs found (85%+ success rate)
- Processing time < 60 seconds

#### Subtask 2.4.2: Create Validation Script (2 hours)
**File**: `scripts/validate_enrichment.py`

**Purpose**: Compare enriched results with manual gold standard (if available)

**Metrics**:
```python
def calculate_metrics(enriched: Dict, gold_standard: Dict) -> Dict:
    """
    Calculate precision, recall, F1 for ID lookups.
    
    Metrics:
    - Precision: correct matches / total matches
    - Recall: found studies / total studies
    - F1: harmonic mean of precision and recall
    - False positives: incorrect PMIDs assigned
    - False negatives: correct PMIDs not found
    """
    pass
```

**Output**:
```
Validation Results: ai_2022
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PMID Lookup:
  Precision: 0.95 (19/20)
  Recall: 0.90 (18/20)
  F1-Score: 0.92

DOI Lookup:
  Precision: 0.93 (14/15)
  Recall: 0.88 (14/16)
  F1-Score: 0.90

Error Analysis:
  False Positives:
    - Study #5: Incorrect PMID (similar title)
  False Negatives:
    - Study #12: PMID not found (title variation)

Confidence Distribution:
  0.90-1.00: 12 studies (85.7%)
  0.80-0.90: 2 studies (14.3%)
  0.00-0.80: 0 studies (0.0%)
```

#### Subtask 2.4.3: Error Analysis & Tuning (1 hour)
**Action**:
1. Analyze failed lookups
2. Identify patterns (title variations, author name formats, etc.)
3. Adjust fuzzy matching thresholds
4. Improve search queries
5. Re-run enrichment and validate

**Deliverable**: Validated system with >85% success rate

---

### Task 2.5: Manual Review Interface (5 hours) - OPTIONAL
**Priority**: LOW  
**Owner**: TBD  
**Target Date**: Jan 28, 2026

**Implementation**:

#### Subtask 2.5.1: Create Review CLI (4 hours)
**File**: `scripts/review_studies.py`

**Interface**:
```bash
python scripts/review_studies.py studies/ai_2022/enriched_studies.json
```

**Workflow**:
```
Manual Review Session
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2 studies need review:

Study #5 (Confidence: 0.72)
─────────────────────────────────────────
Original:
  Title: Ambulatory blood pressure monitoring in children...
  Author: Geng X
  Year: 2019

Candidate Matches:
  [1] PMID: 32851326 (Confidence: 0.72)
      DOI: 10.1002/ped4.12163
      Title: Ambulatory blood pressure monitoring in children...
      Authors: Geng X, Wu Y, Ge W, ...
      Similarity: 0.92

  [2] PMID: 31234567 (Confidence: 0.68)
      DOI: 10.1234/example
      Title: Blood pressure monitoring in pediatric sleep apnea
      Authors: Geng X, Li M, ...
      Similarity: 0.75

  [3] Skip (search manually)

Your choice [1/2/3]: 1

✓ Accepted PMID: 32851326

Study #12 (Confidence: 0.00)
─────────────────────────────────────────
No matches found. Manual search required.

  Title: Central apnoeas have significant effects...
  Author: O'Driscoll DM
  Year: 2009

Enter PMID (or press Enter to skip): 19732317
Enter DOI (or press Enter to skip): 10.1111/j.1365-2869.2009.00766.x

✓ Manual entry saved

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Review complete!
  Reviewed: 2 studies
  Accepted: 1 studies
  Manual entry: 1 studies
  Skipped: 0 studies

✓ Updated: studies/ai_2022/enriched_studies.json
```

#### Subtask 2.5.2: Integration & Testing (1 hour)
**Test**:
- Manual acceptance workflow
- Manual entry workflow
- Skip workflow
- File updates
- Error handling

**Deliverable**: Interactive review interface

---

### Task 2.6: Documentation & Cleanup (2 hours)
**Priority**: MEDIUM  
**Owner**: TBD  
**Target Date**: Jan 28, 2026

**Implementation**:

#### Subtask 2.6.1: Update README (1 hour)
**File**: `README.md`

**Sections to add**:
1. **Included Studies Extraction**
   - Usage examples
   - Output format
2. **ID Enrichment**
   - API key setup (PubMed, CrossRef)
   - Usage examples
   - Confidence thresholds
3. **Validation**
   - How to validate results
   - Metrics interpretation
4. **Troubleshooting**
   - Common errors
   - Rate limiting
   - API key issues

#### Subtask 2.6.2: Create Usage Guide (1 hour)
**File**: `Documentations/USAGE_GUIDE.md`

**Contents**:
1. Complete workflow example
2. Configuration options
3. Best practices
4. Performance tuning
5. Cost estimation

**Deliverable**: Complete documentation

---

## Summary

### Completed
- [x] Phase 1: Deterministic extraction (4 hours actual)
  - [x] Task 1.1: Table parser and citation extraction
  - [x] 12 unit tests
  - [x] Validated on ai_2022

### In Progress
- [ ] Phase 2: API-based ID lookup (35 hours estimated)
  - [ ] Task 2.1: PubMed lookup (8 hours)
  - [ ] Task 2.2: CrossRef lookup (6 hours)
  - [ ] Task 2.3: Unified orchestrator (10 hours)
  - [ ] Task 2.4: Validation (4 hours)
  - [ ] Task 2.5: Review interface (5 hours) - OPTIONAL
  - [ ] Task 2.6: Documentation (2 hours)

### Total Effort
- Phase 1: 4 hours (actual)
- Phase 2: 35 hours (estimated)
- **Total: 39 hours** (~5 days of development)

---

**Status**: Ready to begin Task 2.1 (PubMed Lookup)  
**Blocker**: None  
**Next Action**: Install Biopython and test PubMed E-utilities API

---

## Bug Fixes

### BF-1: Embase Empty-Query CSV Treated as Import Error ✅ FIXED

**Date Fixed**: February 18, 2026  
**File**: `scripts/import_embase_manual.py`

#### Problem

When a proximity-based Embase query (e.g., query 6, Micro-variant 3) returns 0 results,
the exported CSV is empty (header row only or completely empty). The import script could
not distinguish this from a genuinely malformed export (CSV has data rows but missing
DOI/PMID columns), and returned exit code `1` in both cases:

```python
# OLD — no distinction between the two failure modes:
if len(dois) == 0 and len(pmids) == 0:
    print("⚠️  WARNING: No DOIs or PMIDs found!")
    return 1   # ← blocks the whole workflow
```

This caused a cascade failure:
1. `import_embase_manual.py` returned `1` for empty CSV
2. `batch_import_embase.py` counted it as a failed import → returned `1`
3. `run_complete_workflow.sh` called `exit 1` at the Embase import step

Crucially, removing the empty CSV was **not** a safe workaround: `batch_import_embase.py`
pairs CSVs to query text by positional zip-order. Dropping query 3 (balanced) would cause
query 4 (high-precision) to be written as `embase_query3.json` and scored under the wrong
index — silent result mislabeling.

#### Fix

`parse_embase_csv` now tracks `raw_row_count` (data rows seen before DOI/PMID filtering)
and returns it as a 4th value. `main()` then branches on this count:

| Condition | Meaning | Behaviour |
|---|---|---|
| `raw_row_count == 0` and `dois/pmids == 0` | Query returned 0 results on Embase | Create **empty JSON placeholder**, return `0` ✅ |
| `raw_row_count > 0` and `dois/pmids == 0` | Wrong export format (missing columns) | Warn user, return `1` ❌ |

The empty JSON placeholder (`retrieved_dois: [], retrieved_pmids: []`) flows correctly through the rest of the pipeline:
- `batch_import_embase.py` counts the slot as successful → positional ordering preserved
- `score-sets` scores it as Recall=0 / Precision=0 → accurately reflects zero Embase results for that query
- `aggregate_queries.py` adds 0 records from it → harmless

#### Key Code Change

```python
# NEW — distinguishes empty query from bad export format:
dois, pmids, records, raw_row_count = parse_embase_csv(args.input)

if len(dois) == 0 and len(pmids) == 0:
    if raw_row_count == 0:
        # Genuinely empty — create placeholder and succeed
        create_workflow_json(args.query, set(), set(), [], args.output)
        return 0
    else:
        # Has rows but no DOI/PMID columns — bad export format
        print(f"⚠️  WARNING: CSV has {raw_row_count} data rows but no DOI/PMID extracted.")
        return 1
```
