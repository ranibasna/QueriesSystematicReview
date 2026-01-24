---
title: "DOI and PMID Extraction Automation - Task Breakdown"
subtitle: "Actionable Tasks and Subtasks for Implementation"
author: "Systematic Review Queries Project"
date: "January 24, 2026"
status: "Wave 1 Complete | Wave 2 Planning"
wave_1_hours: 87
wave_2_hours: 37-48
total_estimated_hours: 124-135
---

# DOI and PMID Extraction Automation - Task Breakdown

This document breaks down the implementation plan into specific, actionable tasks and subtasks with time estimates, dependencies, and success criteria.

**Implementation is organized into two waves:**
- **Wave 1 (Core)**: Basic extraction and workflow automation - **COMPLETE** ✅
- **Wave 2 (Enhancement)**: Quality improvements and DOI-aware evaluation - **IN PLANNING** 📋

---

## Task Organization

### Wave 1: Core Implementation (87 hours) ✅ **COMPLETE**

**Phases**:
- Phase 1: Reference Extraction (18 hours) ✅
- Phase 2: ID Lookup System (35 hours) ✅
- Phase 3: Workflow Integration (22 hours) ⏸️ **PARTIAL** (Gold CSV generation pending)
- Phase 4: Documentation & Testing (12 hours) ⏸️ **PARTIAL**

**Status**: 85% complete - extraction and lookup working, needs final integration

### Wave 2: Enhancements (37-48 hours) 📋 **PLANNED**

**Phases**:
- Phase 5: Quality Assurance Enhancements (12-18 hours)
  - Multi-agent validation
  - Sampling-based extraction
  - Multi-source API integration
- Phase 6: DOI-Aware Evaluation (10-12 hours)
  - Enhanced gold standard format
  - Multi-key matching
  - Aggregation updates
- Phase 7: Advanced Features (15-18 hours)
  - Fuzzy title matching
  - Manual review interface
  - Performance optimization

---

## Phase 1: Reference Extraction (18 hours)

### Task 1.1: Design JSON Schema
**Estimated Time**: 2 hours  
**Priority**: High (blocking)  
**Dependencies**: None

**Subtasks**:
- [ ] 1.1.1 Define reference object schema (30 min)
  - Fields: title, authors, journal, year, volume, issue, pages, doi, pmid
  - Include raw_citation for debugging
  - Add confidence and metadata fields
  
- [ ] 1.1.2 Create JSON schema documentation (30 min)
  - Write schema in JSON Schema format
  - Document each field's purpose and format
  - Include validation rules (e.g., year: 1900-2026)
  
- [ ] 1.1.3 Implement Python dataclass (30 min)
  - Create `models.py` with Reference dataclass
  - Add validation methods
  - Add JSON serialization/deserialization
  
- [ ] 1.1.4 Write unit tests for schema (30 min)
  - Test valid reference objects
  - Test missing optional fields
  - Test invalid data (reject gracefully)

**Deliverables**:
- `models.py` with Reference dataclass
- `schemas/reference_schema.json`
- Unit tests in `tests/test_reference_schema.py`

**Success Criteria**:
- Schema validates all test cases correctly
- Dataclass properly handles missing fields
- JSON serialization roundtrip works

---

### Task 1.2: Engineer LLM Extraction Prompt
**Estimated Time**: 6 hours  
**Priority**: High (blocking)  
**Dependencies**: Task 1.1

**Subtasks**:
- [ ] 1.2.1 Research citation format types (1 hour)
  - APA, Vancouver, Harvard, Chicago, numbered
  - Collect examples from systematic review papers
  - Document format patterns
  
- [ ] 1.2.2 Write base extraction prompt (2 hours)
  - System message: "You are an expert librarian..."
  - Instructions: "Extract all references from the provided systematic review..."
  - Output format: "Return a JSON array of reference objects..."
  - Include JSON schema in prompt
  
- [ ] 1.2.3 Add citation format examples (1.5 hours)
  - Include 2-3 examples of each format type
  - Show both input (raw citation) and output (JSON)
  - Cover edge cases: missing author, preprint, etc.
  
- [ ] 1.2.4 Design section identification strategy (1 hour)
  - Pattern matching: "References", "Included Studies", "Bibliography"
  - Fuzzy heading detection
  - Fallback: LLM identifies section boundaries
  
- [ ] 1.2.5 Test prompt on sample papers (30 min)
  - Test on Godos_2024, ai_2022, sleep_apnea papers
  - Measure extraction accuracy manually
  - Iterate based on failures

**Deliverables**:
- `prompts/extract_references_prompt.md`
- Test results document (accuracy per paper)

**Success Criteria**:
- >85% extraction accuracy on test papers
- Handles all citation format types
- Gracefully handles edge cases

---

### Task 1.3: Implement Extraction Script
**Estimated Time**: 8 hours  
**Priority**: High (blocking)  
**Dependencies**: Tasks 1.1, 1.2

**Subtasks**:
- [ ] 1.3.1 Create script skeleton (1 hour)
  ```python
  # scripts/extract_references.py
  # Functions: read_markdown, identify_references_section, 
  #           call_llm, parse_json, validate, save_output
  ```
  
- [ ] 1.3.2 Implement markdown reader (1 hour)
  - Read file from `studies/{study_name}/paper_{study_name}.md`
  - Handle encoding issues (UTF-8)
  - Preserve formatting for debugging
  
- [ ] 1.3.3 Implement section identification (1.5 hours)
  - Pattern matching with regex
  - Fallback to LLM if patterns fail
  - Extract section content
  
- [ ] 1.3.4 Implement LLM API integration (2 hours)
  - Support Claude, GPT, Gemini (config-based selection)
  - Add context length checking (batch if exceeds limit)
  - Implement retry logic with exponential backoff
  - Error handling (malformed responses, timeouts)
  
- [ ] 1.3.5 Implement JSON parser (1 hour)
  - Parse LLM output as JSON
  - Validate against schema
  - Handle common errors (trailing commas, unescaped quotes)
  
- [ ] 1.3.6 Implement validation (1 hour)
  - Year range check (1900-2026)
  - Author format validation
  - Title length validation
  - Flag suspicious entries (low confidence)
  
- [ ] 1.3.7 Add CLI interface (30 min)
  - Accept study_name as argument
  - Optional flags: --llm-model, --debug, --output-path
  - Progress bar for long papers

**Deliverables**:
- `scripts/extract_references.py`
- Unit tests in `tests/test_extract_references.py`

**Success Criteria**:
- Successfully extracts references from all test papers
- Handles errors gracefully (doesn't crash)
- Average processing time <2 minutes per paper
- Saves valid JSON to correct location

---

### Task 1.4: Testing & Validation
**Estimated Time**: 2 hours  
**Priority**: Medium  
**Dependencies**: Task 1.3

**Subtasks**:
- [ ] 1.4.1 Run extraction on all test studies (30 min)
  - Godos_2024 (expected: ~50 references)
  - ai_2022 (expected: ~30 references)
  - sleep_apnea (expected: ~15 references)
  
- [ ] 1.4.2 Manual validation (1 hour)
  - For each study, manually count references in paper
  - Check if all were extracted
  - Check if any false positives (non-references extracted)
  - Calculate extraction accuracy
  
- [ ] 1.4.3 Document failures and edge cases (30 min)
  - Note any systematic errors
  - Document papers that failed
  - Plan prompt improvements if needed

**Deliverables**:
- Test results spreadsheet
- `studies/{study_name}/extracted_references.json` for each study

**Success Criteria**:
- >90% extraction accuracy across all test studies
- <5% false positive rate
- All test studies processed without crashes

---

## Phase 2: ID Lookup System (35 hours)

### Task 2.1: Implement CrossRef API Integration
**Estimated Time**: 8 hours  
**Priority**: High  
**Dependencies**: Phase 1 complete

**Subtasks**:
- [ ] 2.1.1 Register for CrossRef API (15 min)
  - Implement mailto: policy (add to User-Agent header)
  - Document API key (if using paid tier)
  - Test basic API access
  
- [ ] 2.1.2 Create CrossRef lookup module (3 hours)
  ```python
  # scripts/crossref_lookup.py
  # Functions: search_by_metadata, parse_results, 
  #           calculate_confidence, handle_rate_limits
  ```
  - Implement search by title + author + year
  - Parse response JSON
  - Extract DOI and metadata
  
- [ ] 2.1.3 Implement fuzzy matching (2.5 hours)
  - Install `rapidfuzz` library
  - Title similarity (Levenshtein distance, threshold: 90%)
  - Author matching (handle initials, order variations)
  - Year validation (±1 year tolerance)
  - Combined confidence score (weighted average)
  
- [ ] 2.1.4 Implement rate limiting (1.5 hours)
  - Track requests per second
  - Implement token bucket algorithm
  - Respect polite pool (50 req/sec) or standard (1 req/sec)
  - Add exponential backoff on 429 errors
  
- [ ] 2.1.5 Add error handling (30 min)
  - Network errors (timeout, connection refused)
  - API errors (404, 500, rate limit)
  - Malformed responses
  - Log all errors with context
  
- [ ] 2.1.6 Write unit tests (30 min)
  - Test with known DOIs (verify correctness)
  - Test with ambiguous queries (check disambiguation)
  - Test error scenarios (mock API failures)

**Deliverables**:
- `scripts/crossref_lookup.py`
- Unit tests in `tests/test_crossref_lookup.py`
- Configuration file for API settings

**Success Criteria**:
- Successfully looks up DOIs for 95% of test references
- Fuzzy matching accuracy >95% (low false positive rate)
- Respects rate limits (no 429 errors in testing)
- Handles network errors gracefully

---

### Task 2.2: Enhance PubMed Lookup
**Estimated Time**: 6 hours  
**Priority**: High  
**Dependencies**: Phase 1 complete

**Subtasks**:
- [ ] 2.2.1 Review existing PubMed code (30 min)
  - Examine `search_providers.py` PubMedProvider class
  - Identify reusable methods
  - Document current capabilities
  
- [ ] 2.2.2 Implement metadata-to-PMID search (2.5 hours)
  - Create search query from title + first author + year
  - Use Entrez.esearch with appropriate filters
  - Parse ESearch results (PMIDs)
  - Fetch metadata with Entrez.efetch
  
- [ ] 2.2.3 Implement DOI extraction (1 hour)
  - Extract DOI from PubMed record (if present)
  - Handle multiple DOI formats
  - Validate DOI format (regex)
  
- [ ] 2.2.4 Add fuzzy matching (1.5 hours)
  - Similar to CrossRef (title + author + year)
  - Disambiguate multiple results
  - Return best match with confidence score
  
- [ ] 2.2.5 Implement retry logic (30 min)
  - Exponential backoff on HTTP errors
  - Respect NCBI rate limits (10 req/sec with key)
  - Add delay between requests
  
- [ ] 2.2.6 Write unit tests (1 hour)
  - Test with known PMIDs
  - Test edge cases (multiple matches, no matches)
  - Test error handling

**Deliverables**:
- Enhanced `search_providers.py` or new `pubmed_lookup.py`
- Unit tests

**Success Criteria**:
- Successfully looks up PMIDs for 90% of biomedical references
- Extracts DOIs when available (>60% of modern articles)
- Respects NCBI rate limits
- Handles errors gracefully

---

### Task 2.3: Create Unified Lookup Orchestrator
**Estimated Time**: 10 hours  
**Priority**: High (critical path)  
**Dependencies**: Tasks 2.1, 2.2

**Subtasks**:
- [ ] 2.3.1 Design orchestration logic (1 hour)
  - Decision tree: Check extracted data → PubMed → CrossRef → Mark unresolved
  - Journal-based routing (biomedical → PubMed first, others → CrossRef first)
  - Document fallback strategy
  
- [ ] 2.3.2 Implement main orchestrator (3 hours)
  ```python
  # scripts/id_lookup.py
  # Main function: process_references(study_name, confidence_threshold)
  # For each reference:
  #   1. Check if DOI/PMID already in extracted data
  #   2. Determine lookup order (journal-based)
  #   3. Try primary API
  #   4. Try secondary API if primary fails
  #   5. Mark as unresolved if both fail
  #   6. Track statistics
  ```
  
- [ ] 2.3.3 Implement statistics tracking (1 hour)
  - Count: total refs, resolved, unresolved, by source
  - Track: average confidence, processing time
  - Generate report dictionary
  
- [ ] 2.3.4 Implement caching (1.5 hours)
  - Cache API responses to avoid duplicate lookups
  - Use persistent cache (JSON file or SQLite)
  - Cache key: normalized metadata (title + first author + year)
  - Invalidation: manual or time-based
  
- [ ] 2.3.5 Add progress tracking (1 hour)
  - Progress bar (tqdm library)
  - Logging: INFO for progress, DEBUG for detailed info
  - Estimated time remaining
  
- [ ] 2.3.6 Implement checkpoint/resume (1.5 hours)
  - Save progress every 10 references
  - Detect incomplete runs and resume
  - Useful for long papers or API failures
  
- [ ] 2.3.7 Add CLI interface (1 hour)
  - Arguments: study_name, --confidence-threshold, --cache-dir
  - Flags: --resume, --force-rerun, --verbose
  - Output: references_with_ids.json, lookup_report.txt

**Deliverables**:
- `scripts/id_lookup.py`
- Unit and integration tests
- Example output files

**Success Criteria**:
- Processes 50 references in <5 minutes
- >85% automatic resolution rate
- Checkpoint/resume works correctly
- Clear progress feedback to user

---

### Task 2.4: Implement Confidence Scoring
**Estimated Time**: 5 hours  
**Priority**: Medium-High  
**Dependencies**: Tasks 2.1, 2.2

**Subtasks**:
- [ ] 2.4.1 Design confidence score formula (1 hour)
  - Factors: title similarity (40%), author match (30%), year match (20%), journal match (10%)
  - Thresholds: Perfect match (0.99), Good (0.90), Acceptable (0.85), Low (<0.85)
  - Document rationale
  
- [ ] 2.4.2 Implement scoring function (2 hours)
  ```python
  def calculate_confidence(reference, api_result):
      title_score = fuzzy_ratio(reference.title, api_result.title) / 100
      author_score = match_authors(reference.authors, api_result.authors)
      year_score = 1.0 if abs(reference.year - api_result.year) <= 1 else 0.5
      journal_score = fuzzy_ratio(reference.journal, api_result.journal) / 100
      return weighted_average(...)
  ```
  
- [ ] 2.4.3 Calibrate thresholds (1.5 hours)
  - Run on test dataset with known correct matches
  - Adjust weights to optimize precision/recall
  - Set confidence threshold (recommend 0.85)
  
- [ ] 2.4.4 Write unit tests (30 min)
  - Test perfect matches (should return ~0.99)
  - Test partial matches (should return 0.85-0.95)
  - Test poor matches (should return <0.80)

**Deliverables**:
- `utils/confidence_scoring.py`
- Calibration report with optimal thresholds
- Unit tests

**Success Criteria**:
- High-confidence matches (>0.90) have >98% accuracy
- Medium-confidence matches (0.85-0.90) have >95% accuracy
- Low-confidence matches (<0.85) flagged for review

---

### Task 2.5: Build Manual Review Interface
**Estimated Time**: 4 hours  
**Priority**: Medium  
**Dependencies**: Task 2.3

**Subtasks**:
- [ ] 2.5.1 Implement CSV export (1.5 hours)
  - Filter references with confidence < threshold (default 0.85)
  - Export to `studies/{study_name}/references_to_verify.csv`
  - Columns: ref_id, original_citation, suggested_doi, suggested_pmid, confidence, lookup_source, match_details
  - Add instructions in header row
  
- [ ] 2.5.2 Implement CSV import (1.5 hours)
  - Read corrected CSV
  - Validate corrections (DOI format, PMID format)
  - Merge corrections back into `references_with_ids.json`
  - Mark corrected entries as manually_verified=true
  
- [ ] 2.5.3 Create review script (1 hour)
  ```bash
  # scripts/review_low_confidence.py
  # Export: python scripts/review_low_confidence.py export Godos_2024
  # Import: python scripts/review_low_confidence.py import Godos_2024
  ```
  - Export command generates CSV
  - Import command merges corrections
  - Validate data integrity

**Deliverables**:
- `scripts/review_low_confidence.py`
- Example CSV with instructions
- Documentation on review workflow

**Success Criteria**:
- CSV is easy to read and edit in Excel/Google Sheets
- Import validates and rejects malformed data
- Corrections properly merged into main data
- Process takes <5 minutes for 10 low-confidence refs

---

### Task 2.6: Integration Testing & Optimization
**Estimated Time**: 2 hours  
**Priority**: Medium  
**Dependencies**: All Phase 2 tasks

**Subtasks**:
- [ ] 2.6.1 End-to-end testing (1 hour)
  - Run complete Phase 2 pipeline on all test studies
  - Extract → Lookup → Review → Validate
  - Measure: success rate, processing time, error rate
  
- [ ] 2.6.2 Performance optimization (30 min)
  - Profile bottlenecks (API calls likely slowest)
  - Consider parallel requests (if rate limits allow)
  - Optimize fuzzy matching (use faster algorithms)
  
- [ ] 2.6.3 Fine-tune confidence thresholds (30 min)
  - Analyze false positives vs false negatives
  - Adjust threshold to balance automation vs accuracy
  - Document recommended settings

**Deliverables**:
- Integration test results
- Performance report
- Optimized configuration

**Success Criteria**:
- >85% automatic resolution rate
- >95% accuracy for high-confidence matches
- <5% false positive rate
- Processing time <5 min for 50 references

---

## Phase 3: Workflow Integration (22 hours)

### Task 3.1: Create Automated Gold Standard Generator
**Estimated Time**: 4 hours  
**Priority**: High  
**Dependencies**: Phase 2 complete

**Subtasks**:
- [ ] 3.1.1 Implement gold standard generator (2 hours)
  ```python
  # scripts/create_gold_standard_auto.py
  # Read: references_with_ids.json
  # Filter: confidence >= threshold
  # Extract: PMIDs (prefer) or DOIs (fallback)
  # Format: gold_pmids_{study_name}.csv (single column: PMID)
  ```
  
- [ ] 3.1.2 Add report generation (1 hour)
  - Summary: Total refs, PMIDs extracted, DOI-only, failed
  - Statistics: Confidence distribution, lookup sources
  - Warnings: Low coverage (<70%), many DOI-only entries
  
- [ ] 3.1.3 Add CLI interface and validation (1 hour)
  - Arguments: study_name, --confidence-threshold
  - Validate PMID format (all digits, reasonable length)
  - De-duplicate PMIDs (if multiple refs point to same article)
  - Compare to existing gold standard (if exists)

**Deliverables**:
- `scripts/create_gold_standard_auto.py`
- Example gold standard CSV
- Report templates

**Success Criteria**:
- Generates valid CSV compatible with existing workflow
- Report clearly shows coverage and quality metrics
- Warns user if coverage is low (<70%)
- Matches manually created gold standards (within 95%)

---

### Task 3.2: Implement DOI-Based Deduplication
**Estimated Time**: 8 hours  
**Priority**: High (affects existing functionality)  
**Dependencies**: None (parallel to Phase 2)

**Subtasks**:
- [ ] 3.2.1 Analyze current deduplication logic (1 hour)
  - Review `llm_sr_select_and_score.py`
  - Identify deduplication functions
  - Document current PMID-only approach
  
- [ ] 3.2.2 Design DOI-first deduplication (1 hour)
  - Primary key: DOI (case-insensitive, normalized)
  - Secondary key: PMID
  - Tertiary key: Title fuzzy match (>90% similarity)
  - Handle missing DOIs/PMIDs gracefully
  
- [ ] 3.2.3 Implement deduplication function (3 hours)
  ```python
  def deduplicate_results(results):
      # Step 1: Group by DOI (if present)
      # Step 2: Group remaining by PMID (if present)
      # Step 3: Fuzzy match remaining by title
      # Step 4: Merge metadata from all sources
      # Return: Deduplicated list with source tracking
  ```
  
- [ ] 3.2.4 Update aggregation scripts (2 hours)
  - Apply new deduplication to aggregation strategies
  - Update consensus_k2, precision_gated_union, etc.
  - Ensure backward compatibility
  
- [ ] 3.2.5 Write comprehensive tests (1 hour)
  - Test with duplicate DOIs from different databases
  - Test with DOI in one source, PMID in another (should merge)
  - Test with no DOI/PMID (title matching)
  - Verify no regressions on existing studies

**Deliverables**:
- Updated `llm_sr_select_and_score.py`
- Updated aggregation scripts
- Comprehensive unit tests
- Before/after comparison on test studies

**Success Criteria**:
- DOI-based deduplication reduces duplicates by >10%
- No false merges (different articles merged as same)
- All existing studies produce same results (±1% variance)
- Clear documentation of new logic

---

### Task 3.3: Create DOI Enrichment Script
**Estimated Time**: 6 hours  
**Priority**: Medium  
**Dependencies**: Tasks 2.1, 2.2

**Subtasks**:
- [ ] 3.3.1 Design enrichment workflow (1 hour)
  - Input: Query results CSV (any database)
  - Process: For records without DOI, use metadata to lookup
  - Output: Enriched CSV with DOIs added
  - Use case: Scopus/WOS results often lack DOIs
  
- [ ] 3.3.2 Implement enrichment script (3 hours)
  ```python
  # scripts/enrich_with_dois.py
  # Read CSV, identify records without DOI
  # For each record:
  #   Try CrossRef lookup by title+authors+year
  #   If found, add DOI to record
  # Write enriched CSV
  ```
  
- [ ] 3.3.3 Add batch processing (1 hour)
  - Process in batches of 50 to avoid rate limits
  - Progress bar and time estimates
  - Checkpoint/resume for large datasets
  
- [ ] 3.3.4 Test on real data (1 hour)
  - Run on Scopus results from test studies
  - Measure enrichment rate (% of records enriched)
  - Validate DOIs (spot check 10 random entries)

**Deliverables**:
- `scripts/enrich_with_dois.py`
- Example enriched CSV
- Documentation on usage

**Success Criteria**:
- Enriches >50% of records missing DOIs
- <2% false positive rate (wrong DOI assigned)
- Processes 100 records in <3 minutes
- Doesn't modify records that already have DOIs

---

### Task 3.4: Integration Testing
**Estimated Time**: 4 hours  
**Priority**: High  
**Dependencies**: All Phase 3 tasks

**Subtasks**:
- [ ] 3.4.1 Run complete workflow on Godos_2024 (1 hour)
  - Automated extraction + lookup + gold standard generation
  - Run complete workflow with new gold standard
  - Compare results to manual gold standard run
  
- [ ] 3.4.2 Run on all test studies (1.5 hours)
  - ai_2022, sleep_apnea, Godos_2024
  - Verify no regressions in recall/precision
  - Check deduplication improvements
  
- [ ] 3.4.3 Performance benchmarking (1 hour)
  - Measure time savings vs manual workflow
  - Document before/after metrics
  - Calculate ROI
  
- [ ] 3.4.4 Fix bugs and document issues (30 min)
  - Address any failures found in testing
  - Document known limitations
  - Create issue tickets for future improvements

**Deliverables**:
- Integration test report
- Performance benchmarks
- Bug fix commits

**Success Criteria**:
- All test studies complete successfully
- No regressions (recall/precision within 1%)
- Time savings >50% vs manual
- Clear documentation of any issues

---

## Phase 4: Documentation & Deployment (12 hours)

### Task 4.1: Update Workflow Scripts
**Estimated Time**: 3 hours  
**Priority**: High  
**Dependencies**: Phase 3 complete

**Subtasks**:
- [ ] 4.1.1 Update run_complete_workflow.sh (1.5 hours)
  - Add Step 1.5: Automated gold standard generation
  - Add flags: --auto-gold-standard, --skip-manual-review, --id-confidence-threshold
  - Add conditional logic (only run if flag enabled)
  - Add error handling (fall back to manual if automation fails)
  
- [ ] 4.1.2 Create standalone automation script (1 hour)
  ```bash
  # scripts/create_gold_standard_pipeline.sh
  # Runs: extract_references → id_lookup → create_gold_standard_auto
  # Easier for users who only want this feature
  ```
  
- [ ] 4.1.3 Test workflow integration (30 min)
  - Run complete workflow with new flag
  - Verify it works end-to-end
  - Test without flag (ensure backward compatibility)

**Deliverables**:
- Updated `run_complete_workflow.sh`
- New `scripts/create_gold_standard_pipeline.sh`
- Updated configuration files

**Success Criteria**:
- Flag enables automation seamlessly
- Without flag, workflow behaves as before
- Clear error messages if automation fails
- Backward compatible with existing studies

---

### Task 4.2: Write Comprehensive Documentation
**Estimated Time**: 6 hours  
**Priority**: High  
**Dependencies**: All previous tasks

**Subtasks**:
- [ ] 4.2.1 Update AUTOMATION_GUIDE.md (1.5 hours)
  - Add new section: "Automated Gold Standard Generation"
  - Update Step 5 with automation option
  - Add examples of automated vs manual workflow
  - Include troubleshooting subsection
  
- [ ] 4.2.2 Update complete_pipeline_guide.md (1 hour)
  - Update Step 5 description
  - Add decision tree: "When to use automated vs manual"
  - Update workflow diagrams
  
- [ ] 4.2.3 Create new detailed guide (2 hours)
  ```markdown
  # Documentations/doi_pmid_extraction_guide.md
  - How the feature works (architecture)
  - Step-by-step usage instructions
  - Understanding output files (JSON, reports)
  - Manual review workflow
  - Troubleshooting common issues
  - Advanced configuration options
  ```
  
- [ ] 4.2.4 Update README.md (30 min)
  - Add feature to highlights
  - Update "Getting Started" with new flag
  - Add link to detailed guide
  
- [ ] 4.2.5 Create code documentation (1 hour)
  - Add docstrings to all new functions
  - Add inline comments for complex logic
  - Add type hints (Python 3.10+ style)

**Deliverables**:
- Updated AUTOMATION_GUIDE.md
- Updated complete_pipeline_guide.md
- New doi_pmid_extraction_guide.md
- Updated README.md
- Fully documented code

**Success Criteria**:
- A new user can follow docs to use the feature in <10 minutes
- All common questions are answered in docs
- Code is self-documenting with clear docstrings
- Troubleshooting section covers common errors

---

### Task 4.3: Create Examples and Tutorials
**Estimated Time**: 2 hours  
**Priority**: Medium  
**Dependencies**: Task 4.2

**Subtasks**:
- [ ] 4.3.1 Create example output files (30 min)
  - `studies/examples/extracted_references.json` (sample)
  - `studies/examples/references_with_ids.json` (sample)
  - `studies/examples/lookup_report.txt` (sample)
  - `studies/examples/references_to_verify.csv` (sample)
  
- [ ] 4.3.2 Create step-by-step tutorial (1 hour)
  - Markdown document: `Documentations/tutorials/automated_gold_standard.md`
  - Includes screenshots (optional) or ASCII diagrams
  - Covers: extraction, review, gold standard generation
  
- [ ] 4.3.3 Create troubleshooting examples (30 min)
  - Common error messages and solutions
  - Low match rate scenario and remediation
  - Manual review examples

**Deliverables**:
- Example files in `studies/examples/`
- Tutorial document
- Troubleshooting guide

**Success Criteria**:
- Examples are realistic and helpful
- Tutorial can be followed independently
- Troubleshooting covers >80% of expected issues

---

### Task 4.4: Final Testing and Deployment
**Estimated Time**: 1 hour  
**Priority**: High  
**Dependencies**: All tasks

**Subtasks**:
- [ ] 4.4.1 Final integration test (30 min)
  - Fresh clone of repository
  - Run complete automated workflow on new study
  - Verify all documentation links work
  
- [ ] 4.4.2 Pre-launch checklist (20 min)
  - [ ] All unit tests passing
  - [ ] Integration tests passing on 3+ studies
  - [ ] Documentation complete and reviewed
  - [ ] No critical bugs in issue tracker
  - [ ] Performance benchmarks documented
  
- [ ] 4.4.3 Merge and release (10 min)
  - Merge feature branch to main
  - Tag release (v0.2.0-beta)
  - Update changelog
  - Create GitHub release with notes

**Deliverables**:
- Merged code in main branch
- Tagged release
- Release notes

**Success Criteria**:
- All checklist items completed
- No merge conflicts

---

---

# WAVE 2: ENHANCEMENTS (37-48 hours)

**Prerequisites**: Wave 1 must be complete and tested on all datasets

**Motivation**: Wave 1 provides 90% time savings with 100% accuracy on ai_2022. Wave 2 adds quality assurance mechanisms and improves evaluation accuracy for multi-database queries.

---

## Phase 5: Quality Assurance Enhancements (12-18 hours)

### Task 5.1: Multi-Agent Validation System
**Estimated Time**: 4-6 hours  
**Priority**: Medium (Optional Enhancement)  
**Dependencies**: Wave 1 complete

**Purpose**: Use multiple LLMs (Claude, GPT-4, Gemini) to extract references and cross-validate results via consensus voting.

**Subtasks**:
- [ ] 5.1.1 Design multi-agent architecture (1 hour)
  - Three-agent system: Claude, GPT-4, Gemini
  - Consensus threshold: 2 out of 3 must agree
  - Similarity matching: title + author (≥0.85 similarity)
  - Confidence levels: High (3/3), Medium (2/3), Low (1/3)

- [ ] 5.1.2 Implement agent orchestrator (2 hours)
  ```python
  class MultiAgentExtractor:
      def __init__(self, agents=['claude', 'gpt4', 'gemini']):
          self.agents = [self._init_agent(a) for a in agents]
      
      def extract_with_consensus(self, markdown_path):
          # Run all agents in parallel
          results = [agent.extract(markdown_path) for agent in self.agents]
          
          # Match studies across agents by similarity
          matched_groups = self._match_across_agents(results)
          
          # Apply consensus voting
          consensus = self._vote_consensus(matched_groups)
          return consensus
  ```

- [ ] 5.1.3 Implement study matching logic (1.5 hours)
  - Title similarity using rapidfuzz (≥0.85)
  - Author matching (first author + year)
  - Group studies found by multiple agents
  - Handle agent-specific errors gracefully

- [ ] 5.1.4 Integrate with existing workflow (30 min)
  ```bash
  python scripts/extract_included_studies.py ai_2022 \
    --multi-agent-validation \
    --agents claude,gpt4,gemini \
    --consensus-threshold 0.66
  ```

- [ ] 5.1.5 Add review queue for low-consensus items (30 min)
  - Export studies with <2/3 agreement to CSV
  - Include all agent versions for manual inspection
  - Allow user to select correct version

- [ ] 5.1.6 Test and benchmark (30 min)
  - Test on ai_2022, Godos_2024
  - Measure agreement rate between agents
  - Calculate accuracy improvement vs single agent

**Deliverables**:
- `scripts/multi_agent_extractor.py`
- Updated `extract_included_studies.py` with `--multi-agent` flag
- Consensus report template
- Documentation on agent setup (API keys required)

**Success Criteria**:
- ≥95% agreement between agents on test data
- Low-consensus items (<2/3) correctly flagged
- +5-10% accuracy improvement demonstrated
- Processing time ≤3x single agent

**When to Use**:
- High-stakes systematic reviews (clinical, policy)
- Complex table formats prone to parsing errors
- Budget allows 3x LLM costs
- Multiple API keys available

---

### Task 5.2: Sampling-Based Extraction
**Estimated Time**: 3-4 hours  
**Priority**: Medium (Optional Enhancement)  
**Dependencies**: Wave 1 complete

**Purpose**: Run extraction multiple times with different parameters and use majority voting to catch intermittent errors.

**Subtasks**:
- [ ] 5.2.1 Design sampling strategy (30 min)
  - 5 runs with varying temperature (0.3, 0.5, 0.7, 0.3, 0.5)
  - Different random seeds per run
  - Majority voting: ≥3/5 runs must agree
  - Track: consistency score per study

- [ ] 5.2.2 Implement sampling orchestrator (1.5 hours)
  ```python
  class SamplingExtractor:
      def extract_with_sampling(self, markdown_path, n_samples=5):
          results = []
          for i in range(n_samples):
              temp = [0.3, 0.5, 0.7, 0.3, 0.5][i]
              seed = 42 + i * 100
              result = self._extract_once(markdown_path, temp, seed)
              results.append(result)
          
          # Majority voting
          consensus = self._majority_vote(results)
          return consensus
  ```

- [ ] 5.2.3 Implement voting logic (1 hour)
  - Match studies across runs (title + author similarity)
  - Count votes per study
  - Accept if ≥60% runs agree (3/5)
  - Flag inconsistent extractions

- [ ] 5.2.4 Add parallel execution (30 min)
  - Run 5 extractions in parallel (if resources allow)
  - Reduce total time from 5x to ~1.5x

- [ ] 5.2.5 Test and analyze (30 min)
  - Test on papers with known parsing issues
  - Measure: consistency rate, error catch rate
  - Compare accuracy vs single extraction

**Deliverables**:
- `scripts/sampling_extractor.py`
- Voting configuration file
- Consistency analysis report

**Success Criteria**:
- Catches ≥80% of intermittent PDF parsing errors
- Processing time ≤2x single extraction (with parallelization)
- Consistency score reported per study
- False rejection rate <5%

**When to Use**:
- PDFs with complex tables or formatting
- Known unreliable text extraction
- High accuracy requirements
- Cost/time not primary constraint

---

### Task 5.3: Multi-Source API Integration
**Estimated Time**: 8-10 hours  
**Priority**: Medium (Future-Proofing)  
**Dependencies**: Wave 1 complete

**Purpose**: Design provider pattern to support lookup from multiple sources (PubMed, Scopus, WoS, CrossRef) with DOI-based merging.

**Subtasks**:
- [ ] 5.3.1 Design provider interface (1 hour)
  ```python
  from abc import ABC, abstractmethod
  
  class LookupProvider(ABC):
      @abstractmethod
      def search(self, study: IncludedStudy) -> Optional[dict]:
          """Return {pmid, doi, scopus_id, wos_id, confidence, source}"""
          pass
  ```

- [ ] 5.3.2 Implement provider classes (3 hours)
  - PubMedProvider (refactor from existing code)
  - CrossRefProvider (refactor from existing code)
  - ScopusProvider (NEW - requires Scopus API)
  - WoSProvider (NEW - requires WoS API)

- [ ] 5.3.3 Implement multi-source orchestrator (2 hours)
  ```python
  class MultiSourceOrchestrator:
      def __init__(self, providers: List[LookupProvider]):
          self.providers = providers
      
      def lookup(self, study: IncludedStudy) -> dict:
          results = []
          for provider in self.providers:
              try:
                  result = provider.search(study)
                  if result:
                      results.append(result)
              except Exception as e:
                  logging.warning(f"{provider} failed: {e}")
          
          # Merge by DOI
          merged = self._merge_by_doi(results)
          return merged
  ```

- [ ] 5.3.4 Implement DOI-based merging (1.5 hours)
  - Group results by DOI
  - Take highest confidence value for each field
  - Collect all identifier types (PMID, Scopus ID, WoS ID, DOI)
  - Track which sources contributed

- [ ] 5.3.5 Add graceful degradation (30 min)
  - Continue if one provider fails
  - Log provider failures
  - Return partial results if available

- [ ] 5.3.6 Add CLI configuration (1 hour)
  ```bash
  python scripts/extract_included_studies.py ai_2022 \
    --lookup-sources pubmed,scopus,wos,crossref \
    --pubmed-email user@example.com \
    --scopus-api-key YOUR_KEY \
    --wos-api-key YOUR_KEY
  ```

- [ ] 5.3.7 Test with mock providers (1 hour)
  - Create mock Scopus/WoS responses
  - Test merging logic
  - Test error handling

**Deliverables**:
- `scripts/lookup_orchestrator.py`
- `scripts/providers/` directory with all provider classes
- Provider configuration file
- Documentation on API setup

**Success Criteria**:
- All 4 providers implement common interface
- Merging correctly deduplicates by DOI
- Graceful failure when provider unavailable
- Easy to add new providers (10 lines of code)

**When to Use**:
- Using Scopus/WoS queries in workflow
- Need multiple identifier types
- Want cross-validation of IDs
- Long-term tool development

---

## Phase 6: DOI-Aware Evaluation (10-12 hours)

### Task 6.1: Enhanced Gold Standard Format
**Estimated Time**: 2 hours  
**Priority**: High (if using Scopus/WoS)  
**Dependencies**: Wave 1 complete

**Purpose**: Add DOI column to gold standard CSV to enable multi-key matching.

**Subtasks**:
- [ ] 6.1.1 Update gold standard generator (1 hour)
  ```python
  def generate_gold_pmids_csv(included_studies, output_path):
      with open(output_path, 'w', newline='') as f:
          writer = csv.DictWriter(f, fieldnames=['pmid', 'doi', 'title', 'confidence'])
          writer.writeheader()
          for study in included_studies:
              writer.writerow({
                  'pmid': study.pmid,
                  'doi': study.doi,
                  'title': study.title[:100],  # Truncate for readability
                  'confidence': study.lookup_metadata.get('confidence', 1.0)
              })
  ```

- [ ] 6.1.2 Update gold loader with format detection (1 hour)
  ```python
  def load_gold_pmids(path: str) -> tuple[set[str], set[str]]:
      """Returns (gold_pmids, gold_dois)"""
      # Auto-detect format and load both identifiers
      # See DOI_PMID_FEATURE_STATUS_ANALYSIS.md for full implementation
  ```

**Deliverables**:
- Updated `scripts/generate_gold_pmids.py`
- Updated `load_gold_pmids()` in `llm_sr_select_and_score.py`
- Migration script for existing gold CSVs

**Success Criteria**:
- Backward compatible (handles old PMID-only format)
- New format includes DOI column
- Both identifiers loaded correctly

---

### Task 6.2: Multi-Key Matching Implementation
**Estimated Time**: 3-4 hours  
**Priority**: High (if using Scopus/WoS)  
**Dependencies**: Task 6.1

**Purpose**: Match query results against gold standard using PMID or DOI.

**Subtasks**:
- [ ] 6.2.1 Implement multi-key metrics function (2 hours)
  ```python
  def set_metrics_multi_key(
      retrieved_pmids: Set[str],
      retrieved_dois: Set[str],
      gold_pmids: Set[str],
      gold_dois: Set[str],
      detailed: bool = False
  ) -> dict:
      # See DOI_PMID_FEATURE_STATUS_ANALYSIS.md for full implementation
  ```

- [ ] 6.2.2 Update query execution to track DOIs (1 hour)
  - Modify `_execute_query_bundle()` to return both PMIDs and DOIs
  - Update all callers to handle dict return value

- [ ] 6.2.3 Add evaluation breakdown report (1 hour)
  - Show: X matched by PMID, Y by DOI, Z missed
  - Export detailed match report to JSON

**Deliverables**:
- `set_metrics_multi_key()` function
- Updated `_execute_query_bundle()`
- Match breakdown report template

**Success Criteria**:
- Recall improvement: +5-15% on Scopus queries
- Detailed breakdown shows match source
- No false positives (same article matched twice)

---

### Task 6.3: Aggregation Strategy Updates
**Estimated Time**: 3 hours  
**Priority**: High (if using Scopus/WoS)  
**Dependencies**: Task 6.2

**Purpose**: Update aggregation to use DOI-aware deduplication.

**Subtasks**:
- [ ] 6.3.1 Update aggregation loader (1 hour)
  ```python
  def load_identifiers_from_file(path: str) -> dict[str, dict]:
      # Load both PMIDs and DOIs
      # See DOI_PMID_FEATURE_STATUS_ANALYSIS.md for implementation
  ```

- [ ] 6.3.2 Update all aggregation strategies (1.5 hours)
  - consensus_k2, precision_gated_union, weighted_vote, etc.
  - Use DOI + PMID union for deduplication
  - Maintain backward compatibility

- [ ] 6.3.3 Update output format (30 min)
  - Text files: PMIDs only (backward compatible)
  - New JSON files: Include DOIs
  - Example: `consensus_k2.txt` + `consensus_k2_details.json`

**Deliverables**:
- Updated `scripts/aggregate_queries.py`
- Enhanced JSON output format
- Backward compatibility maintained

**Success Criteria**:
- Existing tools still work (text files unchanged)
- New evaluation uses DOI data
- All aggregation strategies updated

---

### Task 6.4: Integration Testing for DOI-Aware Evaluation
**Estimated Time**: 2 hours  
**Priority**: High  
**Dependencies**: Tasks 6.1, 6.2, 6.3

**Subtasks**:
- [ ] 6.4.1 Test on ai_2022 with enhanced gold (1 hour)
  - Regenerate gold CSV with DOI column
  - Run evaluation with multi-key matching
  - Compare recall: old vs new

- [ ] 6.4.2 Test on Scopus-heavy queries (1 hour)
  - Create test case with Scopus-only articles
  - Verify DOI matching works
  - Measure recall improvement

**Deliverables**:
- Test results report
- Before/after comparison

**Success Criteria**:
- No regressions on existing datasets
- Measurable recall improvement on Scopus queries

---

## Phase 7: Advanced Features (15-18 hours)

### Task 7.1: Fuzzy Title Matching
**Estimated Time**: 4-5 hours  
**Priority**: Low (Optional)  
**Dependencies**: Phase 6 complete

**Purpose**: Handle articles without DOI/PMID using title similarity.

**Subtasks**:
- [ ] 7.1.1 Implement title normalization (1 hour)
  - Remove punctuation, lowercase, stemming
  - Handle Unicode characters
  - Strip common words

- [ ] 7.1.2 Implement fuzzy matching (2 hours)
  - Use rapidfuzz for similarity scoring
  - Threshold: ≥0.90 for match
  - Include author + year in scoring

- [ ] 7.1.3 Integrate with evaluation (1 hour)
  - Add as tertiary match method (after PMID and DOI)
  - Report fuzzy matches separately

- [ ] 7.1.4 Test on edge cases (1 hour)
  - Preprints, non-indexed journals
  - Measure false positive rate

**Deliverables**:
- `utils/fuzzy_title_matcher.py`
- Integration with evaluation

**Success Criteria**:
- Handles articles without DOI/PMID
- False positive rate <5%
- +2-5% recall improvement

---

### Task 7.2: Enhanced Manual Review Interface
**Estimated Time**: 5 hours  
**Priority**: Medium  
**Dependencies**: Wave 1 complete

**Purpose**: Interactive interface for reviewing and correcting low-confidence matches.

**Subtasks**:
- [ ] 7.2.1 Design review UI (1 hour)
  - CLI or web-based (recommend CLI for simplicity)
  - Show: extracted metadata, API results, confidence
  - Actions: Accept, Reject, Edit, Skip

- [ ] 7.2.2 Implement review CLI (2.5 hours)
  ```python
  class ReviewInterface:
      def review_low_confidence(self, threshold=0.85):
          for study in self._get_low_confidence(threshold):
              self._display_study(study)
              action = self._prompt_action()
              self._apply_action(study, action)
  ```

- [ ] 7.2.3 Add batch operations (1 hour)
  - Accept/reject all
  - Filter by confidence range
  - Search functionality

- [ ] 7.2.4 Test usability (30 min)
  - User testing with 10-20 low-confidence studies
  - Measure time per study
  - Collect feedback

**Deliverables**:
- `scripts/review_interface.py`
- User guide

**Success Criteria**:
- <30 seconds per study review
- Clear display of relevant information
- Changes saved correctly

---

### Task 7.3: Performance Optimization
**Estimated Time**: 3 hours  
**Priority**: Low  
**Dependencies**: All previous tasks

**Subtasks**:
- [ ] 7.3.1 Profile bottlenecks (1 hour)
  - Use cProfile on full pipeline
  - Identify slow functions
  - Measure API call time vs processing time

- [ ] 7.3.2 Implement parallel lookups (1.5 hours)
  - Use asyncio for concurrent API calls
  - Batch lookups where possible
  - Maintain rate limits

- [ ] 7.3.3 Optimize fuzzy matching (30 min)
  - Cache normalized titles
  - Use faster algorithms
  - Batch similarity calculations

**Deliverables**:
- Performance report
- Optimized code

**Success Criteria**:
- 50% reduction in processing time
- No accuracy loss
- Rate limits respected

---

### Task 7.4: Wave 2 Documentation and Testing
**Estimated Time**: 3 hours  
**Priority**: High  
**Dependencies**: All Wave 2 tasks

**Subtasks**:
- [ ] 7.4.1 Update documentation (1.5 hours)
  - Add Wave 2 features to guides
  - Update decision matrix
  - Add new examples

- [ ] 7.4.2 Integration testing (1 hour)
  - Test all enhancements together
  - Verify no conflicts
  - Measure combined impact

- [ ] 7.4.3 Create Wave 2 release notes (30 min)
  - Document new features
  - Migration guide for Wave 1 users
  - Performance improvements

**Deliverables**:
- Updated documentation
- Release notes
- Migration guide

**Success Criteria**:
- All documentation current
- Clear upgrade path from Wave 1
- Examples for all new features

---

## Wave 2 Summary

**Total Time**: 37-48 hours (1-1.5 weeks)

**When to Implement Wave 2**:
- Wave 1 complete and stable
- Using multi-database queries (Scopus/WoS)
- Need higher quality assurance
- Have budget for multiple LLM calls
- Long-term systematic review program

**Expected Benefits**:
- +5-10% extraction accuracy (multi-agent/sampling)
- +5-15% evaluation recall (DOI matching)
- Future-proof architecture (extensible providers)
- Better error detection and handling
- More robust for complex reviews

**Can Skip Wave 2 If**:
- PubMed-only queries
- Wave 1 accuracy sufficient (100% on ai_2022)
- Time/cost constraints
- Simple systematic reviews
- Release notes are clear and comprehensive
- Beta tag indicates users should report issues

---

## Priority Matrix

### Critical Path (Must Complete First)
1. Task 1.1: JSON Schema (blocks all extraction work)
2. Task 1.2: LLM Prompt (blocks extraction script)
3. Task 1.3: Extraction Script (blocks Phase 2)
4. Task 2.1: CrossRef Integration (critical for lookups)
5. Task 2.3: Orchestrator (integrates all lookups)
6. Task 3.1: Gold Standard Generator (primary deliverable)

### High Priority (Complete Early)
- Task 1.4: Testing (validates Phase 1)
- Task 2.2: PubMed Enhancement (improves coverage)
- Task 2.4: Confidence Scoring (ensures quality)
- Task 3.2: DOI Deduplication (improves existing workflow)
- Task 4.1: Workflow Integration (makes feature accessible)
- Task 4.2: Documentation (enables user adoption)

### Medium Priority (Can Be Parallel or Later)
- Task 2.5: Manual Review Interface (enhances UX)
- Task 3.3: DOI Enrichment (nice-to-have bonus feature)
- Task 4.3: Examples and Tutorials (improves onboarding)

### Lower Priority (Optional or Post-Launch)
- Task 2.6: Optimization (can be done post-beta)
- Advanced features (parallel processing, web search fallback)

---

## Weekly Milestones

### Week 1 (40 hours)
**Goal**: Complete Phase 1 and start Phase 2

**Days 1-2 (16 hours)**:
- Complete Task 1.1: JSON Schema
- Complete Task 1.2: LLM Prompt
- Start Task 1.3: Extraction Script

**Days 3-4 (16 hours)**:
- Complete Task 1.3: Extraction Script
- Complete Task 1.4: Testing
- Start Task 2.1: CrossRef Integration

**Day 5 (8 hours)**:
- Complete Task 2.1: CrossRef Integration
- Start Task 2.2: PubMed Enhancement

**Deliverables**:
- Functional reference extraction (Phase 1 complete)
- CrossRef integration working

---

### Week 2 (40 hours)
**Goal**: Complete Phase 2 and start Phase 3

**Days 1-2 (16 hours)**:
- Complete Task 2.2: PubMed Enhancement
- Complete Task 2.3: Orchestrator (critical)
- Start Task 2.4: Confidence Scoring

**Days 3-4 (16 hours)**:
- Complete Task 2.4: Confidence Scoring
- Complete Task 2.5: Manual Review Interface
- Start Task 3.1: Gold Standard Generator

**Day 5 (8 hours)**:
- Complete Task 3.1: Gold Standard Generator
- Start Task 3.2: DOI Deduplication

**Deliverables**:
- Complete ID lookup system (Phase 2 complete)
- Automated gold standard generation working

---

### Week 3 (7 hours + buffer)
**Goal**: Complete Phase 3, Phase 4, and deployment

**Days 1-2 (14 hours + overflow from Week 2)**:
- Complete Task 3.2: DOI Deduplication
- Complete Task 3.3: DOI Enrichment (if time)
- Complete Task 3.4: Integration Testing

**Days 3-4 (12 hours)**:
- Complete Task 4.1: Workflow Scripts
- Complete Task 4.2: Documentation
- Complete Task 4.3: Examples

**Day 5 (2 hours)**:
- Complete Task 4.4: Final Testing and Deployment
- Launch beta release!

**Deliverables**:
- Fully integrated feature
- Complete documentation
- Beta release (v0.2.0-beta)

---

## Resource Requirements

### Software / Tools
- [ ] Python 3.11+ environment
- [ ] LLM API access (Claude/GPT/Gemini)
- [ ] CrossRef API access (mailto policy)
- [ ] PubMed API key (optional but recommended)
- [ ] Git for version control
- [ ] Text editor / IDE (VS Code recommended)

### Libraries / Dependencies
```txt
# Add to requirements.txt
rapidfuzz>=3.0.0           # Fast fuzzy string matching
requests>=2.31.0           # HTTP requests for APIs
tqdm>=4.66.0               # Progress bars
python-dotenv>=1.0.0       # Environment variable management
biopython>=1.81            # Already in project (PubMed)
```

### Test Data
- [ ] Existing studies: Godos_2024, ai_2022, sleep_apnea
- [ ] Manually created gold standards (for validation)
- [ ] Sample papers with various citation formats

### Human Resources
- **Developer**: 1 person, 2-3 weeks full-time (87 hours)
- **Beta Testers**: 2-3 users (optional, 2-4 hours each)
- **Reviewer**: 1 person (review documentation, 2-3 hours)

---

## Tracking Progress

### Checklist Format

Use this checklist to track progress:

```markdown
## Phase 1: Reference Extraction
- [ ] Task 1.1: JSON Schema (2h) - Status: Not Started
- [ ] Task 1.2: LLM Prompt (6h) - Status: Not Started
- [ ] Task 1.3: Extraction Script (8h) - Status: Not Started
- [ ] Task 1.4: Testing (2h) - Status: Not Started

## Phase 2: ID Lookup System
- [ ] Task 2.1: CrossRef Integration (8h) - Status: Not Started
- [ ] Task 2.2: PubMed Enhancement (6h) - Status: Not Started
- [ ] Task 2.3: Orchestrator (10h) - Status: Not Started
- [ ] Task 2.4: Confidence Scoring (5h) - Status: Not Started
- [ ] Task 2.5: Manual Review (4h) - Status: Not Started
- [ ] Task 2.6: Testing & Optimization (2h) - Status: Not Started

## Phase 3: Workflow Integration
- [ ] Task 3.1: Gold Standard Generator (4h) - Status: Not Started
- [ ] Task 3.2: DOI Deduplication (8h) - Status: Not Started
- [ ] Task 3.3: DOI Enrichment (6h) - Status: Not Started
- [ ] Task 3.4: Integration Testing (4h) - Status: Not Started

## Phase 4: Documentation & Deployment
- [ ] Task 4.1: Workflow Scripts (3h) - Status: Not Started
- [ ] Task 4.2: Documentation (6h) - Status: Not Started
- [ ] Task 4.3: Examples & Tutorials (2h) - Status: Not Started
- [ ] Task 4.4: Deployment (1h) - Status: Not Started
```

### Status Values
- **Not Started**: Task not yet begun
- **In Progress**: Currently working on task
- **Blocked**: Waiting on dependency or external factor
- **Testing**: Implementation complete, in testing phase
- **Complete**: Task finished and validated

---

## Next Steps

1. **Review this task breakdown** with stakeholders
2. **Secure approvals** and budget allocation
3. **Set up development environment** (APIs, libraries)
4. **Begin Task 1.1** (JSON Schema Design)
5. **Update this document** as tasks are completed

---

*Document Version: 1.0*  
*Last Updated: January 22, 2026*  
*Next Review: After Week 1 milestone*
