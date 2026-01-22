---
title: "DOI and PMID Extraction Automation - Task Breakdown"
subtitle: "Actionable Tasks and Subtasks for Implementation"
author: "Systematic Review Queries Project"
date: "January 22, 2026"
status: "Planning Phase"
total_estimated_hours: 87
---

# DOI and PMID Extraction Automation - Task Breakdown

This document breaks down the implementation plan into specific, actionable tasks and subtasks with time estimates, dependencies, and success criteria.

---

## Task Organization

**Total Estimated Time**: 87 hours (2-3 weeks for one developer)

**Phases**:
- Phase 1: Reference Extraction (18 hours)
- Phase 2: ID Lookup System (35 hours)
- Phase 3: Workflow Integration (22 hours)
- Phase 4: Documentation & Testing (12 hours)

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
