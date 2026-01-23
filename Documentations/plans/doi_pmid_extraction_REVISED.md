# DOI and PMID Extraction Automation - REVISED Implementation Plan

**Date**: January 22, 2026  
**Status**: Phase 1 Complete, Phase 2 Planning  
**Approach**: Deterministic Parsing + API Lookups (No LLM APIs)

---

## Executive Summary

This plan outlines a **deterministic, API-based system** to extract included studies from systematic review papers and automatically lookup DOIs and PMIDs using public databases.

**Key Revision**: We extract **INCLUDED STUDIES** from systematic reviews (not all references), using deterministic table parsing instead of LLM APIs.

**Current Status**:
- ✅ Phase 1 Complete: Deterministic included studies extraction (0 cost, <1s processing)
- 🔄 Phase 2 In Progress: API-based ID lookup system

---

## 1. Problem Reframing

### Original Problem
Manual PMID lookup takes 5-30 minutes per systematic review study.

### Critical Insight
Systematic reviews don't need ALL references extracted - they need the **INCLUDED STUDIES** (those that passed screening and were analyzed). These are typically listed in a table like "Table 1: Characteristics of Included Studies".

### Solution Architecture
1. **Parse included studies table** from markdown (deterministic, no LLM needed)
2. **Match to references section** to get full citation
3. **Lookup DOI/PMID** via public APIs (PubMed, CrossRef, Scopus, WoS)
4. **Manual review** for ambiguous cases

---

## 2. Phase 1: Included Studies Extraction ✅ COMPLETE

### Implementation
- **Script**: `scripts/extract_included_studies.py`
- **Method**: Deterministic pattern matching (no LLM APIs)
- **Input**: `studies/{study_name}/paper_{study_name}.md`
- **Output**: `studies/{study_name}/included_studies.json`

### How It Works
1. Find table with heading matching `"Table.*[Ii]ncluded [Ss]tudies"` or `"Characteristics"`
2. Extract reference numbers from table (e.g., `[12]`, `[13]`, `Author et al. [28]`)
3. Parse references section to get full citations
4. Extract: first_author, year, title, journal, volume, pages, doi, pmid
5. Output structured JSON

### Results (ai_2022 validation)
- ✅ Extracted 14 included studies
- ✅ Reference numbers: [12, 13, 17, 18, 28-37]
- ✅ All fields captured: author, year, title, journal
- ✅ Processing time: <1 second
- ✅ Cost: $0 (no APIs)
- ✅ 12 unit tests passing

### Limitations
- DOI/PMID not in citations (need Phase 2 lookup)
- Some journals abbreviated (need normalization)
- No author disambiguation

---

## 3. Phase 2: API-Based ID Lookup (IN PROGRESS)

### Goal
For each included study without DOI/PMID, lookup identifiers using public APIs.

### API Options (Ranked by Priority)

#### 1. **PubMed E-utilities API** (HIGHEST PRIORITY)
- **Why**: Biomedical focus, most reliable for health sciences
- **Endpoint**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi`
- **Search Strategy**: `title[Title] AND first_author[Author] AND year[PDAT]`
- **Rate Limit**: 3 req/sec (10 req/sec with API key)
- **Cost**: FREE
- **Returns**: PMID + DOI (via efetch)
- **Python Library**: `Biopython` (Bio.Entrez)

**Example Query**:
```python
from Bio import Entrez
Entrez.email = "your@email.com"
handle = Entrez.esearch(db="pubmed", term="Childhood OSA[Title] AND Chan[Author] AND 2020[PDAT]")
```

#### 2. **CrossRef API** (MEDIUM PRIORITY)
- **Why**: Comprehensive DOI coverage across all disciplines
- **Endpoint**: `https://api.crossref.org/works`
- **Search Strategy**: `query.title={title}&query.author={author}&filter=from-pub-date:{year}`
- **Rate Limit**: 50 req/sec (with polite pool)
- **Cost**: FREE
- **Returns**: DOI + rich metadata
- **Python Library**: `habanero` or `requests`

**Example Query**:
```python
import requests
url = "https://api.crossref.org/works"
params = {
    "query.title": "Childhood OSA independent determinant blood pressure",
    "query.author": "Chan",
    "filter": "from-pub-date:2020,until-pub-date:2020",
    "rows": 5
}
headers = {"User-Agent": "YourProject/1.0 (mailto:your@email.com)"}
```

#### 3. **Scopus Search API** (CONDITIONAL)
- **Why**: Comprehensive coverage, useful for non-biomedical fields
- **Endpoint**: `https://api.elsevier.com/content/search/scopus`
- **Search Strategy**: `TITLE("{title}") AND AUTHOR({last_name}) AND PUBYEAR IS {year}`
- **Rate Limit**: 20,000 req/week (depends on institutional access)
- **Cost**: Requires API key (may need institutional access)
- **Returns**: Scopus ID, DOI, PubMed ID (if linked)
- **Python Library**: `pybliometrics`

**Note**: Only use if institutional access available.

#### 4. **Web of Science API** (CONDITIONAL)
- **Why**: Comprehensive citation network
- **Endpoint**: WoS Starter API or Expanded API
- **Rate Limit**: Varies by subscription
- **Cost**: Requires API key (may need institutional access)
- **Returns**: WoS Accession Number, DOI
- **Python Library**: `woslite` or direct REST calls

**Note**: Only use if institutional access available.

#### 5. **Web Search Fallback** (LAST RESORT)
- **Method**: Use `fetch_webpage` tool to search Google Scholar or PubMed web interface
- **Strategy**: Parse HTML results for DOI/PMID
- **Rate Limit**: Manual throttling required (1-2 req/min)
- **Reliability**: LOW (HTML changes, CAPTCHAs)
- **Use Case**: Only for high-value studies not found via APIs

---

## 4. Recommended Lookup Strategy

### Multi-Tier Fallback System

```
For each included study without DOI/PMID:

1. PubMed E-utilities Search (Primary)
   ├─ Search: title + first_author + year
   ├─ If 1 result → confidence = 0.95
   ├─ If 2-3 results → fuzzy match title → confidence = 0.80
   └─ If >3 or 0 results → proceed to step 2

2. CrossRef API Search (Secondary)
   ├─ Search: title + author + year
   ├─ Filter by similarity score > 0.85
   ├─ If DOI found → lookup PMID via PubMed (DOI query)
   └─ If not found → proceed to step 3

3. Scopus/WoS API (Tertiary - if available)
   ├─ Search: title + author + year
   ├─ Extract DOI/PMID from metadata
   └─ If not found → proceed to step 4

4. Web Search Fallback (Last Resort)
   ├─ Google Scholar: "title" author year
   ├─ Parse first result for DOI
   ├─ Lookup PMID via PubMed (DOI query)
   ├─ Confidence = 0.50
   └─ Flag for manual review

5. Manual Review Queue
   ├─ Studies with confidence < 0.80
   ├─ Studies with no matches found
   └─ Studies with ambiguous matches
```

### Confidence Scoring

| Scenario | Confidence | Action |
|----------|-----------|--------|
| PubMed exact match (1 result) | 0.95 | Auto-accept |
| PubMed fuzzy match (title similarity > 0.90) | 0.85 | Auto-accept |
| CrossRef match (score > 0.85) | 0.80 | Auto-accept |
| CrossRef match (score 0.70-0.85) | 0.70 | Manual review |
| Web search result | 0.50 | Manual review |
| No matches | 0.00 | Manual search |

---

## 5. Implementation Phases

### Phase 2.1: PubMed Lookup (8 hours) - HIGHEST PRIORITY
**Goal**: Implement PubMed E-utilities lookup

**Tasks**:
1. Install Biopython: `pip install biopython`
2. Create `scripts/lookup_pmid.py`:
   - Function: `search_pubmed(title, first_author, year) -> List[PMID]`
   - Function: `fetch_pubmed_details(pmid) -> Dict[metadata]`
   - Fuzzy matching for title similarity (using `rapidfuzz`)
   - Rate limiting (3 req/sec)
3. Integration with `extract_included_studies.py`:
   - Add `--lookup-pmid` flag
   - For each study without PMID, call PubMed search
   - Save results with confidence scores
4. Unit tests:
   - Test exact match
   - Test fuzzy match
   - Test no match
   - Test rate limiting

**Deliverable**: PMID lookup for biomedical papers

### Phase 2.2: CrossRef Lookup (6 hours)
**Goal**: Implement CrossRef API lookup for DOI

**Tasks**:
1. Create `scripts/lookup_doi.py`:
   - Function: `search_crossref(title, author, year) -> List[DOI]`
   - Score filtering (> 0.85)
   - Rate limiting with polite pool
2. Integration:
   - Add `--lookup-doi` flag
   - For each study without DOI, call CrossRef
   - Reverse lookup PMID from DOI via PubMed
3. Unit tests

**Deliverable**: DOI lookup for all disciplines

### Phase 2.3: Unified Orchestrator (10 hours)
**Goal**: Integrate all lookup methods with fallback logic

**Tasks**:
1. Create `scripts/enrich_studies.py`:
   - Main orchestrator function
   - Multi-tier fallback (PubMed → CrossRef → Web)
   - Confidence scoring
   - Parallel processing (asyncio)
2. Output format:
   ```json
   {
     "study_name": "ai_2022",
     "enriched_studies": [
       {
         "reference_number": 12,
         "original_data": {...},
         "pmid": "18388205",
         "doi": "10.1136/thx.2007.091132",
         "lookup_source": "pubmed",
         "confidence": 0.95,
         "lookup_timestamp": "2026-01-22T10:30:00Z"
       }
     ],
     "statistics": {
       "total_studies": 14,
       "pmid_found": 12,
       "doi_found": 13,
       "manual_review_needed": 2
     }
   }
   ```
3. CLI:
   ```bash
   python scripts/enrich_studies.py ai_2022 \
     --methods pubmed,crossref \
     --confidence-threshold 0.80 \
     --output studies/ai_2022/enriched_studies.json
   ```

**Deliverable**: Complete enrichment pipeline

### Phase 2.4: Validation & Testing (4 hours)
**Goal**: Validate against gold standards

**Tasks**:
1. Run enrichment on ai_2022
2. Compare with manual gold standard (if available)
3. Calculate metrics:
   - Precision: (correct matches) / (total matches)
   - Recall: (found studies) / (total studies)
   - F1-score
4. Error analysis for failures
5. Tune confidence thresholds

**Deliverable**: Validated system with metrics

### Phase 2.5: Manual Review Interface (5 hours) - OPTIONAL
**Goal**: Simple CLI for reviewing ambiguous matches

**Tasks**:
1. Create `scripts/review_studies.py`:
   - Display study with multiple matches
   - Show metadata for each candidate
   - Prompt user to select correct match
   - Save corrections
2. Integration:
   - Filter studies with confidence < 0.80
   - Interactive review session
   - Update enriched_studies.json

**Deliverable**: Human-in-the-loop validation

### Phase 2.6: Documentation (2 hours)
**Goal**: Complete documentation

**Tasks**:
1. Update README with usage examples
2. Create API key setup guide (PubMed, CrossRef)
3. Document lookup strategy and confidence scoring
4. Add troubleshooting section

**Deliverable**: Production-ready documentation

---

## 6. Technical Decisions

### Why No LLMs for Extraction?
- **Deterministic parsing is sufficient**: Tables have consistent structure
- **Cost**: $0 vs $0.10-$0.30 per paper
- **Speed**: <1s vs 30-90s
- **Reliability**: 100% reproducible vs variable LLM responses
- **Offline**: Works without API keys

### Why PubMed First?
- Biomedical focus (matches most systematic reviews)
- Most reliable for health sciences
- Free with high rate limits
- Returns both PMID and DOI
- Authoritative source (NLM)

### Why DOI + PMID (not just PMID)?
- DOIs more universal (not database-specific)
- Better for deduplication across sources
- CrossRef has broader coverage
- Many papers have DOI but no PMID (e.g., social sciences)

### Why Multi-Tier Fallback?
- No single API has 100% coverage
- Different databases have different strengths
- Balances speed, cost, and coverage
- Confidence scores enable quality control

---

## 7. Success Metrics

### Phase 1 (✅ Complete)
- [x] Extract 14/14 included studies from ai_2022
- [x] Processing time < 5 seconds
- [x] Cost = $0
- [x] 12 unit tests passing

### Phase 2 (Target)
- [ ] Lookup success rate > 85%
- [ ] Average lookup time < 3 seconds per study
- [ ] Precision > 90% (correct matches / total matches)
- [ ] Recall > 85% (found studies / total studies)
- [ ] Cost < $0.05 per study (if any paid APIs used)

### Overall System
- [ ] End-to-end time: < 5 minutes per systematic review
- [ ] Manual intervention: < 15% of studies
- [ ] Error rate: < 5%

---

## 8. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| API rate limits | Medium | Medium | Implement throttling, use multiple APIs |
| Ambiguous matches | High | Low | Confidence scoring + manual review |
| Missing metadata | Medium | Medium | Multi-tier fallback, web search |
| API key requirements | Low | Low | Use free APIs first (PubMed, CrossRef) |
| Title variations | Medium | Medium | Fuzzy matching (rapidfuzz) |
| Non-biomedical papers | Low | Low | CrossRef as fallback |

---

## 9. Dependencies

### Required Packages
```bash
pip install biopython      # PubMed E-utilities
pip install requests       # HTTP requests
pip install rapidfuzz      # Fuzzy string matching
pip install aiohttp        # Async HTTP (for parallel lookups)
```

### Optional Packages (if using Scopus/WoS)
```bash
pip install pybliometrics  # Scopus API
pip install woslite        # Web of Science API
```

### API Keys Needed
- **PubMed**: Optional (increases rate limit from 3 to 10 req/sec)
  - Sign up: https://www.ncbi.nlm.nih.gov/account/
- **CrossRef**: None (use polite pool with email in User-Agent)
- **Scopus**: Institutional access required
- **WoS**: Institutional access required

---

## 10. Timeline

| Phase | Duration | Completion Date |
|-------|----------|----------------|
| Phase 1: Extraction | ✅ Complete | Jan 22, 2026 |
| Phase 2.1: PubMed Lookup | 8 hours | Jan 23, 2026 |
| Phase 2.2: CrossRef Lookup | 6 hours | Jan 24, 2026 |
| Phase 2.3: Orchestrator | 10 hours | Jan 25-26, 2026 |
| Phase 2.4: Validation | 4 hours | Jan 27, 2026 |
| Phase 2.5: Review Interface | 5 hours | Jan 28, 2026 |
| Phase 2.6: Documentation | 2 hours | Jan 28, 2026 |
| **Total** | **35 hours** | **~1 week** |

---

## 11. Next Steps

1. **Immediate** (Today):
   - Install Biopython
   - Test PubMed E-utilities with sample queries
   - Design lookup_pmid.py API

2. **Short-term** (This Week):
   - Implement Phase 2.1 (PubMed lookup)
   - Test on ai_2022 dataset
   - Measure success rate

3. **Medium-term** (Next Week):
   - Add CrossRef fallback
   - Implement orchestrator
   - Complete validation

---

## 12. References

- PubMed E-utilities: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- CrossRef API: https://api.crossref.org/swagger-ui/index.html
- Biopython Tutorial: https://biopython.org/DIST/docs/tutorial/Tutorial.html
- CrossRef REST API: https://github.com/CrossRef/rest-api-doc

---

**Status**: Ready to begin Phase 2.1 (PubMed Lookup)  
**Blockers**: None  
**Owner**: Systematic Review Queries Project  
**Last Updated**: January 22, 2026
