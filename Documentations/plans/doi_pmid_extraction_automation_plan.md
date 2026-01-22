---
title: "DOI and PMID Extraction Automation - Implementation Plan"
subtitle: "Automated Reference Extraction and Identifier Lookup for Systematic Reviews"
author: "Systematic Review Queries Project"
date: "January 22, 2026"
status: "Planning Phase"
priority: "High"
estimated_duration: "2-3 weeks (87 hours)"
---

# DOI and PMID Extraction Automation - Implementation Plan

## Executive Summary

This plan outlines the implementation of an automated system to extract references from systematic review papers (converted to markdown) and automatically lookup DOIs and PMIDs for those references. This feature addresses the most time-consuming manual step in the current workflow: creating gold standard PMID lists.

**Current State**: Manual PMID lookup takes 5-30 minutes per study and is error-prone.

**Proposed State**: Automated extraction and lookup reduces this to 2-5 minutes with 70-90% automation rate.

**Expected ROI**: Positive after processing 4-6 systematic reviews (assuming 2-3 weeks development time).

---

## 1. Motivation and Business Case

### 1.1 Problem Statement

The current systematic review workflow requires manual creation of gold standard PMID lists. Researchers must:

1. Read through published systematic review papers
2. Identify the "Included Studies" section
3. Manually extract each reference citation
4. Search PubMed for each citation to find the PMID
5. Copy-paste PMIDs into a CSV file

This process is:
- **Time-consuming**: 5-30 minutes per study
- **Error-prone**: Copy-paste errors, incorrect PMID associations
- **Non-scalable**: Linear time increase with number of studies
- **Tedious**: Demotivating for researchers

### 1.2 Solution Overview

Implement a four-phase automated system:

1. **Phase 1**: LLM-based reference extraction from markdown papers
2. **Phase 2**: Multi-tier API lookup system (PubMed → CrossRef → Web fallback)
3. **Phase 3**: Integration with existing workflow
4. **Phase 4**: Manual review interface for low-confidence matches

### 1.3 Expected Benefits

**Time Savings:**
- Current: 5-30 minutes manual work per study
- Automated: 2-5 minutes (mostly API wait time)
- **Reduction: 75-85% time savings**

**Quality Improvements:**
- Eliminates manual copy-paste errors
- Systematic validation via authoritative APIs
- Complete audit trail (lookup sources, confidence scores)

**Scalability:**
- Process multiple studies in parallel
- Batch processing for large-scale reviews
- Reusable components for other projects

**DOI-First Architecture:**
- Better than PMID-only approach (DOIs more universal)
- Enables improved deduplication across databases
- Future-proof (DOIs more stable than database-specific IDs)

---

## 2. Technical Architecture

### 2.1 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT LAYER                               │
│  • paper_<study>.md (from docling conversion)               │
│  • PROSPERO protocol (optional, for validation)             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              EXTRACTION LAYER (Phase 1)                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  LLM-Based Reference Extraction                    │    │
│  │  • Identify "References" / "Included Studies"      │    │
│  │  • Parse citations (any format)                    │    │
│  │  • Structure: title, authors, journal, year        │    │
│  │  • Output: extracted_references.json               │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               LOOKUP LAYER (Phase 2)                         │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Multi-Tier Identifier Lookup                      │    │
│  │                                                     │    │
│  │  Tier 1: PubMed E-utilities                       │    │
│  │  • Search by: title + first author + year         │    │
│  │  • Returns: PMID, DOI (if available)              │    │
│  │  • Coverage: ~36M biomedical articles             │    │
│  │  • Cost: Free                                      │    │
│  │                                                     │    │
│  │  Tier 2: CrossRef API                             │    │
│  │  • Search by: title + authors + year              │    │
│  │  • Returns: DOI, metadata                         │    │
│  │  • Coverage: ~140M scholarly works                │    │
│  │  • Cost: Free                                      │    │
│  │                                                     │    │
│  │  Tier 3: Web Search (Optional)                    │    │
│  │  • Fallback for unresolved references             │    │
│  │  • Lower confidence, requires review              │    │
│  │                                                     │    │
│  │  Output: references_with_ids.json                 │    │
│  │  • Each reference tagged with:                    │    │
│  │    - doi, pmid (if found)                         │    │
│  │    - confidence score (0-1)                       │    │
│  │    - lookup_source (pubmed|crossref|web)          │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            VALIDATION LAYER (Phase 2.5)                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Manual Review Interface                           │    │
│  │  • Export low-confidence matches to CSV           │    │
│  │  • Researcher reviews and corrects                │    │
│  │  • Re-import validated data                       │    │
│  │  • Threshold: confidence < 0.85                   │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            INTEGRATION LAYER (Phase 3)                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Gold Standard Generator                           │    │
│  │  • Filter validated references (conf > 0.85)       │    │
│  │  • Extract PMIDs (or DOIs if PMID unavailable)    │    │
│  │  • Format: gold_pmids_<study>.csv                 │    │
│  │                                                     │    │
│  │  DOI Enrichment                                    │    │
│  │  • Enrich query results with DOIs                 │    │
│  │  • Improve deduplication accuracy                 │    │
│  │                                                     │    │
│  │  Updated Deduplication                             │    │
│  │  • Primary key: DOI (if available)                │    │
│  │  • Secondary key: PMID                            │    │
│  │  • Tertiary: Title fuzzy match                    │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT LAYER                              │
│  • gold_pmids_<study>.csv (automated)                       │
│  • references_with_ids.json (audit trail)                   │
│  • lookup_report.txt (statistics)                           │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

**Input:**
```markdown
# paper_godos_2024.md

## References
1. Smith J, et al. Mediterranean diet and cognitive function. 
   Am J Clin Nutr. 2020;112(3):580-589.
2. Jones M, et al. Olive oil consumption and dementia risk. 
   Neurology. 2019;93(15):e1431-e1439.
...
```

**Phase 1 Output (extracted_references.json):**
```json
[
  {
    "reference_id": 1,
    "title": "Mediterranean diet and cognitive function",
    "authors": ["Smith J", "..."],
    "journal": "Am J Clin Nutr",
    "year": 2020,
    "volume": "112",
    "issue": "3",
    "pages": "580-589",
    "doi": null,
    "pmid": null,
    "raw_citation": "Smith J, et al. Mediterranean diet...",
    "confidence": 0.95
  },
  ...
]
```

**Phase 2 Output (references_with_ids.json):**
```json
[
  {
    "reference_id": 1,
    "title": "Mediterranean diet and cognitive function",
    "authors": ["Smith J", "..."],
    "journal": "Am J Clin Nutr",
    "year": 2020,
    "doi": "10.1093/ajcn/nqaa123",
    "pmid": "32648899",
    "confidence": 0.98,
    "lookup_source": "pubmed",
    "lookup_timestamp": "2026-01-22T10:30:00Z"
  },
  {
    "reference_id": 2,
    "title": "Olive oil consumption and dementia risk",
    "authors": ["Jones M", "..."],
    "journal": "Neurology",
    "year": 2019,
    "doi": "10.1212/WNL.0000000000008235",
    "pmid": null,
    "confidence": 0.92,
    "lookup_source": "crossref",
    "lookup_timestamp": "2026-01-22T10:30:05Z"
  }
]
```

**Phase 3 Output (gold_pmids_godos_2024.csv):**
```csv
PMID
32648899
31467292
...
```

### 2.3 Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Reference Extraction** | LLM (Claude/GPT/Gemini) | Handles variable citation formats, no regex brittleness |
| **PubMed Lookup** | Biopython (Entrez) | Already in project, free, well-documented |
| **CrossRef Lookup** | `requests` + CrossRef REST API | Free, 140M records, 50 req/sec with polite pool |
| **Fuzzy Matching** | `fuzzywuzzy` or `rapidfuzz` | Fast string similarity for disambiguation |
| **JSON Storage** | Python `json` module | Simple, human-readable, easy debugging |
| **CSV Export** | Python `csv` module | Compatible with Excel for manual review |
| **Workflow Integration** | Bash scripts | Consistent with existing `run_complete_workflow.sh` |

---

## 3. Implementation Phases

### Phase 1: LLM-Based Reference Extraction (18 hours)

**Goal**: Extract structured reference data from markdown papers.

**Key Components:**

1. **JSON Schema Design (2 hours)**
   - Define output structure
   - Include confidence scoring
   - Handle missing fields gracefully

2. **LLM Prompt Engineering (6 hours)**
   - Design comprehensive extraction prompt
   - Include examples of various citation formats (APA, Vancouver, etc.)
   - Handle edge cases (preprints, conference papers, missing data)
   - Test across multiple paper formats

3. **Extraction Script (`scripts/extract_references.py`) (8 hours)**
   - Read markdown file
   - Identify references section (pattern matching or LLM)
   - Batch references if paper is large (context limits)
   - Parse LLM JSON output with error handling
   - Validate extracted data (year range, author format)
   - Save to `studies/{study_name}/extracted_references.json`

4. **Testing (2 hours)**
   - Test on ai_2022, Godos_2024, sleep_apnea studies
   - Validate accuracy manually
   - Measure extraction success rate

**Deliverables:**
- `scripts/extract_references.py`
- `prompts/extract_references_prompt.md`
- `studies/{study}/extracted_references.json` (example outputs)

**Success Criteria:**
- >90% of references correctly extracted
- <5% malformed JSON responses
- Average processing time: <2 minutes per paper

---

### Phase 2: Multi-Tier Identifier Lookup (35 hours)

**Goal**: Automatically find DOIs and PMIDs for extracted references.

**Key Components:**

1. **CrossRef API Integration (8 hours)**
   - Register for CrossRef API (mailto policy)
   - Create `scripts/crossref_lookup.py`
   - Implement search by title + author + year
   - Fuzzy matching with confidence scoring
   - Rate limiting (50 req/sec with polite pool)
   - Comprehensive error handling

2. **PubMed Lookup Enhancement (6 hours)**
   - Extend existing `search_providers.py` PubMed class
   - Add metadata-to-PMID search function
   - Search by title + first author + year
   - Extract both PMID and DOI from results
   - Implement retry logic with exponential backoff

3. **Unified Lookup Orchestrator (`scripts/id_lookup.py`) (10 hours)**
   - Input: `extracted_references.json`
   - For each reference:
     1. Check if DOI/PMID already in extracted data
     2. Try PubMed lookup (prioritize biomedical journals)
     3. If no DOI, try CrossRef lookup
     4. If still unresolved, mark for manual review
   - Track statistics (success rate, API source, confidence)
   - Save to `references_with_ids.json`
   - Generate `lookup_report.txt` with statistics

4. **Fuzzy Matching Logic (5 hours)**
   - Title similarity scoring (Levenshtein distance)
   - Author name matching (handle initials, order variations)
   - Year validation (allow ±1 year for epub ahead of print)
   - Combined confidence score calculation
   - Threshold tuning based on test data

5. **Manual Review Interface (4 hours)**
   - Export low-confidence matches (<0.85) to CSV
   - Columns: original_citation, suggested_doi, suggested_pmid, confidence, lookup_source
   - Import corrections from reviewed CSV
   - Merge corrections back into `references_with_ids.json`

6. **Testing & Optimization (2 hours)**
   - Test on multiple studies
   - Measure lookup success rate
   - Optimize API request patterns (parallel where possible)
   - Fine-tune confidence thresholds

**Deliverables:**
- `scripts/crossref_lookup.py`
- `scripts/id_lookup.py`
- `scripts/review_low_confidence.py`
- `studies/{study}/references_with_ids.json`
- `studies/{study}/lookup_report.txt`
- `studies/{study}/references_to_verify.csv` (if needed)

**Success Criteria:**
- >85% automatic resolution rate (conf > 0.85)
- >70% overall coverage (at least DOI or PMID found)
- <5% false positive rate (wrong ID assigned)
- Average processing time: <5 minutes for 50 references

---

### Phase 3: Workflow Integration (22 hours)

**Goal**: Integrate automated extraction into existing workflow.

**Key Components:**

1. **Gold Standard Generator (`scripts/create_gold_standard_auto.py`) (4 hours)**
   - Input: `references_with_ids.json`
   - Filter to validated references (confidence > threshold)
   - Prefer PMID, fallback to DOI
   - Format as `gold_pmids_{study_name}.csv`
   - Generate summary report

2. **DOI-Based Deduplication Update (8 hours)**
   - Modify `llm_sr_select_and_score.py`:
     - Primary deduplication key: DOI
     - Secondary key: PMID
     - Tertiary key: Title fuzzy match (>90% similarity)
   - Update aggregation scripts similarly
   - Comprehensive testing on existing studies

3. **DOI Enrichment Script (`scripts/enrich_with_dois.py`) (6 hours)**
   - Input: Query results from any database
   - For records without DOI:
     - Use metadata to lookup DOI (CrossRef/PubMed)
   - Update result files with DOIs
   - Use case: Enriching Scopus/WOS results

4. **Testing & Validation (4 hours)**
   - Test complete workflow on all existing studies
   - Verify deduplication improvements
   - Measure end-to-end time savings
   - Document any breaking changes

**Deliverables:**
- `scripts/create_gold_standard_auto.py`
- `scripts/enrich_with_dois.py`
- Updated `llm_sr_select_and_score.py`
- Test results on existing studies

**Success Criteria:**
- Automated gold standard creation works for all test studies
- DOI-based deduplication reduces duplicates by >10%
- No regressions in existing functionality
- Clear error messages for edge cases

---

### Phase 4: Workflow & Documentation (12 hours)

**Goal**: Integrate with bash workflow and update documentation.

**Key Components:**

1. **Workflow Script Updates (`run_complete_workflow.sh`) (3 hours)**
   - Add new optional step after PDF conversion:
   ```bash
   # Step 1.5: Extract references and lookup IDs (NEW)
   if [[ "$AUTO_GOLD_STANDARD" == "true" ]]; then
     echo "🔍 Step 1.5: Automated Gold Standard Generation"
     python scripts/extract_references.py "$STUDY_NAME"
     python scripts/id_lookup.py "$STUDY_NAME" --confidence-threshold 0.85
     python scripts/create_gold_standard_auto.py "$STUDY_NAME"
   fi
   ```
   - Add command-line flags:
     - `--auto-gold-standard`: Enable automated extraction
     - `--skip-manual-review`: Skip low-confidence review
     - `--id-confidence-threshold`: Minimum confidence (default 0.85)

2. **Documentation Updates (6 hours)**
   - **AUTOMATION_GUIDE.md**: Add "Automated Gold Standard Generation" section
   - **complete_pipeline_guide.md**: Update Step 5 with automation option
   - **New file**: `Documentations/doi_pmid_extraction_guide.md`
     - How to use the new features
     - Troubleshooting low match rates
     - Manual review workflow
     - JSON output format reference
   - **README.md**: Add feature to highlights

3. **Example Outputs & Tutorials (2 hours)**
   - Create example JSON files for documentation
   - Screenshot of manual review CSV
   - Example `lookup_report.txt`

4. **Code Documentation (1 hour)**
   - Add docstrings to all new functions
   - Inline comments for complex logic
   - Type hints for function signatures

**Deliverables:**
- Updated `run_complete_workflow.sh`
- Updated `AUTOMATION_GUIDE.md`
- Updated `complete_pipeline_guide.md`
- New `Documentations/doi_pmid_extraction_guide.md`
- Example outputs in `studies/examples/`

**Success Criteria:**
- Users can enable automation with single flag
- Documentation is clear and comprehensive
- All new code has proper documentation
- Tutorial successfully followed by test user

---

## 4. Risk Management

### 4.1 High-Risk Areas

**Risk 1: LLM Extraction Accuracy (Impact: High, Probability: Medium)**

*Description:* LLM fails to correctly parse references from varied citation formats.

*Potential Issues:*
- Different papers use different citation styles (APA, Vancouver, numbered, etc.)
- Some papers don't have dedicated "included studies" sections
- References may be in tables, supplementary materials, or scattered

*Mitigation Strategies:*
1. **Extensive Prompt Engineering**
   - Test prompt on 10+ different paper formats before deployment
   - Include explicit examples of each common citation style
   - Add format detection to prompt ("First, identify the citation style used")

2. **Confidence Scoring**
   - LLM assigns confidence to each extracted reference
   - Low-confidence extractions flagged for manual review
   - Track extraction accuracy over time

3. **Validation Rules**
   - Year must be 1900-2026
   - Authors must have recognizable format
   - Journal name length > 3 characters
   - Reject malformed extractions early

4. **Fallback to Manual**
   - If extraction success rate <70%, halt and request manual input
   - User can override with manual reference list

*Contingency Plan:* If LLM extraction proves unreliable (<80% accuracy), implement a hybrid approach where LLM identifies the references section and user manually reviews each extraction.

---

**Risk 2: API Rate Limits & Costs (Impact: Medium, Probability: Medium)**

*Description:* CrossRef/PubMed rate limits hit during batch processing, or LLM API costs exceed budget.

*Potential Issues:*
- PubMed: 10 req/sec with API key, 3 req/sec without
- CrossRef: 50 req/sec with polite pool, 1 req/sec without
- LLM API costs: $0.50-2.00 per study for extraction (depending on paper length)

*Mitigation Strategies:*
1. **Aggressive Caching**
   - Cache all API responses locally
   - Never re-lookup same reference twice
   - Share cache across studies

2. **Exponential Backoff**
   - Implement retry logic with exponential backoff
   - Respect `Retry-After` headers
   - Add random jitter to avoid thundering herd

3. **Progress Checkpoints**
   - Save progress after every 10 references
   - Allow resume from checkpoint on failure
   - Don't lose work on rate limit errors

4. **Batch Optimization**
   - Process references in optimal batch sizes
   - Parallel API requests where allowed
   - Prioritize faster APIs (PubMed) first

5. **Cost Monitoring**
   - Track LLM token usage per study
   - Alert if extraction exceeds budget
   - Implement token limit safeguards

*Contingency Plan:* If rate limits become problematic, implement a queuing system that processes references overnight. For cost issues, switch to cheaper LLM models or implement local extraction with regex (less accurate but free).

---

**Risk 3: Fuzzy Matching False Positives (Impact: High, Probability: Low-Medium)**

*Description:* Wrong DOI/PMID assigned to reference due to ambiguous metadata.

*Potential Issues:*
- Common author names (e.g., "Wang Y", "Kim S")
- Generic titles (e.g., "A systematic review")
- Pre-print vs published versions (same title, different DOI)
- Errata/corrections (linked to original article)

*Mitigation Strategies:*
1. **Multi-Field Matching**
   - Require match on: title (>90% similarity) + first author + year (±1)
   - Never match on title alone
   - Increase threshold if journal name matches

2. **Confidence Scoring**
   - Perfect match (title + all authors + year + journal): confidence = 0.99
   - Good match (title + first author + year): confidence = 0.90
   - Weak match (title similar, year off): confidence = 0.70
   - Require manual review for confidence <0.85

3. **Validation Checks**
   - Verify journal name matches (fuzzy)
   - Check author count is close (±2)
   - Flag if publication year differs by >1 year
   - Reject if title similarity <80%

4. **Manual Review**
   - Export all matches with confidence <0.85 to CSV
   - User reviews and corrects
   - Track false positive rate over time

5. **Audit Trail**
   - Log all lookup decisions
   - Include match scores for each field
   - Allow manual inspection of ambiguous cases

*Contingency Plan:* If false positive rate exceeds 5%, increase confidence threshold to 0.90 or 0.95. This will increase manual review burden but ensure data integrity.

---

### 4.2 Medium-Risk Areas

**Risk 4: Integration Breaking Existing Workflow (Impact: Medium, Probability: Low)**

*Mitigation:*
- Make automation opt-in via flag (not default)
- Run comprehensive tests on all existing studies before merge
- Version control allows easy rollback
- Keep manual workflow as fallback

**Risk 5: Scalability Issues (Impact: Medium, Probability: Low)**

*Mitigation:*
- Test on papers with 100+ references
- Implement batching for large papers
- Add progress bars and time estimates
- Use streaming responses for LLM

---

## 5. Testing Strategy

### 5.1 Unit Tests

**Phase 1: Reference Extraction**
- Test extraction on 5 different citation styles
- Test handling of missing fields (no year, no journal, etc.)
- Test edge cases (preprints, conference papers, books)
- Validate JSON schema compliance

**Phase 2: ID Lookup**
- Test PubMed lookup with known PMIDs
- Test CrossRef lookup with known DOIs
- Test fuzzy matching with intentional typos
- Test disambiguation (multiple matches)
- Test error handling (API timeouts, malformed responses)

**Phase 3: Integration**
- Test gold standard generation with various confidence thresholds
- Test DOI-based deduplication vs PMID-based
- Test enrichment on Scopus/WOS results without DOIs

### 5.2 Integration Tests

**End-to-End Test 1: Godos_2024**
- Extract references from `paper_godos_2024.md`
- Lookup DOIs/PMIDs automatically
- Generate gold standard CSV
- Compare to manually created gold standard
- Measure accuracy and time savings

**End-to-End Test 2: Sleep Apnea**
- Run complete automated workflow
- Verify deduplication improvements
- Check aggregation strategy performance
- Ensure no regressions in recall/precision

**End-to-End Test 3: ai_2022**
- Test on older study with different paper format
- Verify backward compatibility
- Check manual fallback works correctly

### 5.3 Acceptance Criteria

✅ **Extraction Accuracy**: >90% of references correctly extracted

✅ **Lookup Coverage**: >70% of references resolved automatically (DOI or PMID)

✅ **Lookup Accuracy**: >95% correct assignments (low false positive rate)

✅ **Time Savings**: >50% reduction in gold standard creation time

✅ **Reliability**: <5% unrecoverable errors (errors that require code fixes)

✅ **No Regressions**: All existing studies produce same results (within 1% variance)

---

## 6. Success Metrics and KPIs

### 6.1 Performance Metrics

| Metric | Current (Manual) | Target (Automated) | Measurement Method |
|--------|------------------|--------------------|--------------------|
| **Gold Standard Creation Time** | 5-30 min | 2-5 min | Timed end-to-end |
| **Human Effort** | 100% manual | 15-30% review | % of manual steps |
| **Error Rate** | 2-5% (copy-paste) | <1% (validated) | Spot checks |
| **Coverage** | 100% (manual) | 70-90% (auto) | % resolved refs |
| **Processing Speed** | 1 ref/min | 10 refs/min | Refs processed/time |

### 6.2 Quality Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Extraction Accuracy** | >90% | Manual validation on sample |
| **Lookup Precision** | >95% | False positive rate check |
| **Confidence Calibration** | ±5% | High-conf matches should have >95% accuracy |
| **User Satisfaction** | >80% | Post-deployment survey |

### 6.3 Adoption Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| **Feature Usage Rate** | >75% of new studies use automation | 3 months post-launch |
| **Time to First Use** | <5 minutes (after reading docs) | Immediate |
| **Support Requests** | <2 per week | 1 month post-launch |
| **Manual Override Rate** | <25% (most users trust automation) | 3 months post-launch |

---

## 7. Deployment Plan

### 7.1 Phased Rollout

**Phase A: MVP (Weeks 1-2, ~40 hours)**
- Core extraction and lookup functionality
- Manual review interface
- Basic gold standard generator
- Testing on existing studies

*Release as:* `v0.1.0-alpha` (opt-in via flag)

**Phase B: Production-Ready (Week 3, ~30 hours)**
- Comprehensive error handling
- DOI-based deduplication integration
- Complete workflow integration
- Full documentation

*Release as:* `v0.2.0-beta` (recommended for new studies)

**Phase C: Enhancements (Future, ~20 hours)**
- Web search fallback
- Real-time confidence visualization
- Parallel processing optimization
- DOI enrichment for query results

*Release as:* `v1.0.0` (default behavior)

### 7.2 Launch Checklist

**Pre-Launch:**
- [ ] All unit tests passing
- [ ] Integration tests on 3+ studies completed
- [ ] Documentation complete and reviewed
- [ ] Beta testing by 2+ users completed
- [ ] Performance benchmarks documented
- [ ] Error handling tested with intentional failures

**Launch Day:**
- [ ] Merge to `main` branch
- [ ] Tag release (`v0.2.0-beta`)
- [ ] Update README with new feature
- [ ] Send announcement to users
- [ ] Monitor for issues (first 48 hours)

**Post-Launch (Week 1):**
- [ ] Collect user feedback
- [ ] Address any critical bugs
- [ ] Improve documentation based on questions
- [ ] Measure adoption rate

**Post-Launch (Month 1):**
- [ ] Analyze success metrics
- [ ] Plan enhancements for Phase C
- [ ] Write case study on time savings

---

## 8. Maintenance and Support

### 8.1 Ongoing Maintenance

**Weekly:**
- Monitor API status (PubMed, CrossRef)
- Check error logs for patterns
- Review low-confidence matches (improve prompts)

**Monthly:**
- Update citation format examples in prompt
- Tune confidence thresholds based on false positive rate
- Update documentation with new edge cases

**Quarterly:**
- Performance review (time savings, accuracy)
- User satisfaction survey
- Plan feature enhancements

### 8.2 Support Resources

**User Documentation:**
- Quick start guide (5 minutes)
- Comprehensive guide (20 minutes)
- Troubleshooting FAQ
- Video tutorial (optional)

**Developer Documentation:**
- API integration guide
- Prompt engineering guide
- Fuzzy matching algorithm explanation
- Testing guide

**Support Channels:**
- GitHub Issues for bug reports
- Discussions for questions
- Email for urgent issues

---

## 9. Future Enhancements (Post-v1.0)

### 9.1 Short-Term (3-6 months)

**Web Search Fallback:**
- Google Scholar API for unresolved references
- Semantic Scholar API for better metadata
- Requires: API keys, additional error handling
- Benefit: Increases coverage from 70-90% to 85-95%

**Parallel Processing:**
- Process multiple references simultaneously
- Requires: Async/await refactoring, rate limit pooling
- Benefit: 2-3x faster processing

**Real-Time Confidence UI:**
- Web interface showing extraction/lookup progress
- Live confidence scores during processing
- Requires: Flask/FastAPI backend, simple frontend
- Benefit: Better user experience, transparency

### 9.2 Long-Term (6-12 months)

**Machine Learning Enhancement:**
- Train ML model on validated matches to improve confidence scoring
- Learn from user corrections (manual reviews)
- Requires: Training data collection, model development
- Benefit: Adaptive system that improves over time

**Multi-Language Support:**
- Extract references from non-English papers
- Requires: Multi-language LLM prompts, internationalized APIs
- Benefit: Broader applicability

**Automated Data Validation:**
- Cross-check extracted studies against PROSPERO protocol
- Flag if included studies don't match eligibility criteria
- Requires: PICOS parsing, semantic matching
- Benefit: Quality control for systematic reviews

---

## 10. Decision Points

### 10.1 Go/No-Go Criteria

**PROCEED with implementation if:**
✅ Budget available for LLM API calls ($5-15 per study)
✅ Process ≥3 systematic reviews per month (ROI positive after 6 studies)
✅ Stable access to CrossRef and PubMed APIs
✅ Development time available (2-3 weeks)
✅ Beta testers available for validation

**RECONSIDER if:**
❌ Budget constraints (cost per study must be <$5)
❌ Process <2 reviews per year (manual faster overall)
❌ Domain has <50% DOI coverage (rare in modern literature)
❌ Most sources are grey literature (non-indexed)
❌ No LLM API access available

### 10.2 Milestone Reviews

**After Phase 1 (Week 1):**
- Review extraction accuracy on test studies
- If <85% accurate, invest more in prompt engineering before proceeding
- Decision: Continue to Phase 2 or iterate on Phase 1?

**After Phase 2 (Week 2):**
- Review lookup success rate and false positive rate
- If false positive rate >5%, increase confidence threshold
- Decision: Proceed to integration or add more validation?

**After Phase 3 (Week 3):**
- Review end-to-end workflow on all test studies
- Measure actual time savings vs. target
- Decision: Launch beta or delay for refinement?

---

## 11. Conclusion

The DOI and PMID Extraction Automation feature represents a significant enhancement to the systematic review workflow. With an estimated development time of 2-3 weeks (87 hours) and expected time savings of 75-85% per study, the return on investment is compelling for research teams conducting multiple systematic reviews.

**Key Success Factors:**
1. **Robust LLM Prompt Engineering**: The foundation of accurate extraction
2. **Multi-Tier Fallback System**: Ensures high coverage without sacrificing accuracy
3. **Comprehensive Error Handling**: Graceful degradation and clear error messages
4. **Thorough Testing**: Validation on diverse study types before deployment
5. **User-Friendly Manual Review**: Makes low-confidence cases easy to resolve

**Next Steps:**
1. Secure approval and budget allocation
2. Begin Phase 1 implementation
3. Recruit beta testers
4. Schedule milestone reviews
5. Document lessons learned for future features

This plan provides a clear roadmap from current manual process to automated, validated, and integrated solution. The phased approach allows for iterative improvement and de-risks the implementation.

---

## Appendix A: Example Workflows

### A.1 Current Manual Workflow

```
Time: 5-30 minutes

1. Open paper_godos_2024.md
2. Scroll to "Included Studies" section
3. For each reference (n=50):
   a. Copy first author name
   b. Open PubMed in browser
   c. Search for author + key terms from title
   d. Identify correct article
   e. Copy PMID
   f. Paste into gold_pmids_godos_2024.csv
4. Review CSV for errors
5. Save and commit

Errors: ~2-5% (wrong PMID, typo, missing entry)
```

### A.2 Proposed Automated Workflow

```
Time: 2-5 minutes

1. Run command:
   python scripts/extract_references.py Godos_2024
   python scripts/id_lookup.py Godos_2024
   python scripts/create_gold_standard_auto.py Godos_2024

2. Review lookup_report.txt:
   - 50 references extracted
   - 45 automatically resolved (90%)
   - 5 flagged for manual review (10%)

3. Open references_to_verify.csv (5 entries)
4. Verify and correct if needed
5. Re-run gold standard generator
6. Done!

Errors: <1% (validated by API)
Automation rate: 90%
```

### A.3 Future Fully-Automated Workflow

```
Time: <2 minutes

1. Run workflow with flag:
   bash scripts/run_complete_workflow.sh Godos_2024 \
     --databases pubmed,scopus,wos \
     --auto-gold-standard

2. System automatically:
   - Converts PDFs to markdown
   - Extracts references
   - Looks up DOIs/PMIDs
   - Creates gold standard CSV
   - Runs complete workflow
   - Generates results

3. Review final report
4. Done!

Automation rate: 100% (with confidence-based validation)
```

---

## Appendix B: Risk Matrix

| Risk | Impact | Probability | Severity | Mitigation Priority |
|------|--------|-------------|----------|---------------------|
| LLM extraction errors | High | Medium | **HIGH** | 🔴 Critical - Address first |
| API rate limits | Medium | Medium | **MEDIUM** | 🟡 Important - Plan ahead |
| False positive matches | High | Low | **MEDIUM** | 🟡 Important - Validate thoroughly |
| Integration breakage | Medium | Low | **LOW** | 🟢 Monitor - Test extensively |
| Scalability issues | Low | Low | **LOW** | 🟢 Monitor - Optimize if needed |

---

## Appendix C: Technology Evaluation

### C.1 LLM Selection

| LLM | Pros | Cons | Cost per Study | Recommendation |
|-----|------|------|----------------|----------------|
| **Claude 3.5 Sonnet** | Excellent at structured extraction, 200K context | $3-5 per study | $$$ | ⭐ **Recommended for accuracy** |
| **GPT-4 Turbo** | Good accuracy, wide availability | $4-6 per study | $$$$ | 🟡 Good alternative |
| **GPT-3.5 Turbo** | Fast, cheap | Lower accuracy for complex citations | $0.50-1 | ⭐ **Recommended for cost** |
| **Gemini Pro** | Free (limited), good quality | Rate limits on free tier | $ (Free-$$) | 🟢 Good for testing |

**Recommendation**: Use **Claude 3.5 Sonnet** for production (best accuracy), **GPT-3.5 Turbo** for cost-sensitive scenarios.

### C.2 API Selection

| API | Coverage | Cost | Rate Limit | Data Quality | Recommendation |
|-----|----------|------|------------|--------------|----------------|
| **PubMed E-utilities** | 36M biomedical | Free | 10 req/sec (with key) | Excellent | ⭐ **Primary for biomedical** |
| **CrossRef** | 140M scholarly | Free | 50 req/sec (polite) | Excellent | ⭐ **Primary for DOIs** |
| **Semantic Scholar** | 200M+ papers | Free | 100 req/sec | Good | 🟢 Future enhancement |
| **Google Scholar** | Largest | Unofficial API | Unreliable | Good | 🔴 Avoid (ToS violation) |
| **OpenAlex** | 250M+ works | Free | No limit | Good | 🟢 Future enhancement |

**Recommendation**: **PubMed** + **CrossRef** as core, expand to **Semantic Scholar** or **OpenAlex** in Phase C.

---

*Document Version: 1.0*  
*Last Updated: January 22, 2026*  
*Next Review: Before Phase 1 implementation*
