---
title: "DOI and PMID Extraction Automation - Implementation Plan"
subtitle: "Automated Reference Extraction and Identifier Lookup for Systematic Reviews"
author: "Systematic Review Queries Project"
date: "January 24, 2026"
status: "Wave 1: 85% Complete | Wave 2: Planning"
priority: "High"
wave_1_duration: "2-3 weeks (87 hours)"
wave_2_duration: "1-1.5 weeks (37-48 hours)"
---

# DOI and PMID Extraction Automation - Implementation Plan

## Executive Summary

This plan outlines a **two-wave implementation strategy** for automated reference extraction and identifier lookup for systematic reviews.

### Wave 1: Core Functionality (87 hours) - **85% COMPLETE** ✅

**Goal**: Automate gold standard PMID list creation

**Current State**: Manual PMID lookup takes 5-30 minutes per study and is error-prone.

**Implemented State**: Automated extraction and lookup achieves 100% coverage on ai_2022 test data in <2 minutes.

**Status**: 
- ✅ Reference extraction working
- ✅ PMID/DOI lookup working  
- ⏸️ Workflow integration partial (needs gold CSV generation)
- ⏸️ Documentation partial

**Expected ROI**: Positive after processing 4-6 systematic reviews.

### Wave 2: Enhancements (37-48 hours) - **PLANNED** 📋

**Goal**: Quality assurance and DOI-aware evaluation

**Proposed Enhancements**:
1. **Multi-agent validation** (4-6h): Cross-validation with multiple LLMs (+5-10% accuracy)
2. **Sampling-based extraction** (3-4h): Majority voting across multiple runs (catches intermittent errors)
3. **Multi-source API integration** (8-10h): Extensible provider pattern for Scopus/WoS
4. **DOI-aware evaluation** (10-12h): Multi-key matching improves recall by +5-15%
5. **Advanced features** (15-18h): Fuzzy matching, review interface, optimization

**When to Implement Wave 2**:
- Wave 1 stable and tested on all datasets
- Using multi-database queries (Scopus/WoS)
- Need higher quality assurance
- Budget allows multiple LLM calls

**Can Skip Wave 2 If**:
- PubMed-only queries sufficient
- Wave 1 accuracy meets requirements (100% on ai_2022)
- Time/cost constraints

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

**Two-Wave Implementation Strategy:**

#### Wave 1: Core Automation (87 hours)
1. **Phase 1**: LLM-based reference extraction from markdown papers
2. **Phase 2**: Multi-tier API lookup system (PubMed → CrossRef)
3. **Phase 3**: Integration with existing workflow
4. **Phase 4**: Documentation and testing

**Status**: 85% complete, tested successfully on ai_2022 (14/14 studies, 100% coverage)

#### Wave 2: Enhancements (37-48 hours)
5. **Phase 5**: Quality assurance (multi-agent, sampling, multi-source APIs)
6. **Phase 6**: DOI-aware evaluation (multi-key matching)
7. **Phase 7**: Advanced features (fuzzy matching, review interface, optimization)

**Status**: Planning phase, ready to implement after Wave 1 completion

### 1.3 Expected Benefits

**Wave 1 Benefits (Core):**

**Time Savings:**
- Current: 5-30 minutes manual work per study
- Automated: <2 minutes (mostly API wait time)
- **Reduction: 90%+ time savings** (demonstrated on ai_2022)

**Quality Improvements:**
- Eliminates manual copy-paste errors
- Systematic validation via authoritative APIs
- Complete audit trail (lookup sources, confidence scores)
- **100% accuracy** achieved on ai_2022 test data

**Scalability:**
- Process multiple studies in parallel
- Batch processing for large-scale reviews
- Reusable components for other projects

**DOI-First Architecture:**
- Better than PMID-only approach (DOIs more universal)
- Enables improved deduplication across databases
- Future-proof (DOIs more stable than database-specific IDs)

**Wave 2 Benefits (Enhancements):**

**Improved Accuracy:**
- Multi-agent validation: +5-10% accuracy via consensus
- Sampling-based extraction: Catches intermittent PDF parsing errors
- Fuzzy title matching: Handles non-indexed articles

**Better Evaluation:**
- DOI-aware matching: +5-15% recall improvement on Scopus/WoS queries
- Multi-key evaluation: Reduces false negatives
- Detailed match reporting: Better debugging and validation

**Future-Proofing:**
- Extensible provider pattern: Easy to add new databases
- Multi-source API support: Scopus, WoS, PubMed, CrossRef
- Robust for complex systematic reviews

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

### Implementation Strategy: Two-Wave Approach

This implementation is divided into two waves to balance immediate value delivery with long-term quality improvements.

#### Wave 1: Core Functionality (87 hours) - **85% COMPLETE** ✅

**Goal**: Deliver working automation that saves 90%+ of manual effort

**Status**: 
- ✅ Extraction implemented and tested (14/14 studies on ai_2022)
- ✅ Lookup implemented with 100% coverage
- ⏸️ Gold CSV generation pending (4-6 hours remaining)
- ⏸️ Documentation updates pending

**Remaining Work**: See [IMPLEMENTATION_STATUS.md](../../IMPLEMENTATION_STATUS.md) for details

#### Wave 2: Enhancements (37-48 hours) - **PLANNED** 📋

**Goal**: Add quality assurance and support for multi-database workflows

**Justification**: Wave 1 achieves 100% accuracy on ai_2022. Wave 2 adds:
- Redundancy for edge cases (multi-agent, sampling)
- Support for Scopus/WoS queries (DOI-aware evaluation)
- Future extensibility (provider pattern)

**Decision Point**: Implement Wave 2 only if:
- Wave 1 tested on all datasets (Godos_2024, sleep_apnea)
- Multi-database queries are primary use case
- Budget allows enhanced quality assurance
- Long-term tool development justified

---

## Wave 1 Implementation (REFERENCE)

*Note: Wave 1 is 85% complete. This section documents the original plan for reference. See [IMPLEMENTATION_STATUS.md](../../IMPLEMENTATION_STATUS.md) for current status.*
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


## Wave 2 Implementation (PLANNED)

**Prerequisites**: 
- Wave 1 complete and tested on all datasets
- Decision made to implement enhancements based on project needs

### Phase 5: Quality Assurance Enhancements (12-18 hours)

**Goal**: Add redundancy and validation mechanisms for higher accuracy.

**Key Components:**

1. **Multi-Agent Validation (4-6 hours)**
   - Run extraction with Claude, GPT-4, and Gemini simultaneously
   - Cross-validate results using title/author similarity matching
   - Consensus voting: require 2/3 agreement
   - Flag low-consensus items for manual review
   - **Benefit**: +5-10% accuracy improvement
   - **Cost**: 3x LLM API calls
   - **When to use**: High-stakes reviews, complex PDFs

2. **Sampling-Based Extraction (3-4 hours)**
   - **Concept**: Run same extraction pipeline 5 times with different LLM parameters (temperature, seed)
   - **Voting Strategy**: Majority voting - include studies found in ≥60% of runs (3 out of 5)
   - **Parameter Variation**:
     - Run 1: temperature=0.3, seed=42
     - Run 2: temperature=0.5, seed=123
     - Run 3: temperature=0.7, seed=456
     - Run 4: temperature=0.3, seed=789
     - Run 5: temperature=0.5, seed=999
   - **Implementation**: Add `--sampling-runs 5 --voting-threshold 0.60` flags to extraction script
   - **Output**: Includes confidence scores (5/5, 4/5, 3/5) for each study
   - **Benefit**: Catches intermittent PDF parsing errors (garbled text, complex tables)
   - **Cost**: 5x LLM API calls (but can parallelize to reduce wall-clock time)
   - **Trade-off**: Higher cost for higher reliability
   - **When to use**: 
     - PDF extraction is unreliable (complex tables, garbled text)
     - High-stakes systematic reviews (clinical, safety-critical)
     - Known problematic PDFs with intermittent extraction issues
     - Cost/time is not a constraint

3. **Multi-Source API Integration (8-10 hours)**
   - Design provider pattern for extensibility
   - Implement: PubMedProvider, ScopusProvider, WoSProvider, CrossRefProvider
   - Orchestrator merges results by DOI
   - **Benefit**: Future-proof, cross-validation, multiple identifiers
   - **When to use**: Multi-database queries, need Scopus/WoS IDs

**Deliverables:**
- `scripts/multi_agent_extractor.py`
- `scripts/sampling_extractor.py`
- `scripts/lookup_orchestrator.py`
- `scripts/providers/` directory
- Configuration files for each enhancement
- Documentation on setup and usage

**Success Criteria:**
- Multi-agent: ≥95% agreement, +5-10% accuracy
- Sampling: Catches ≥80% of intermittent errors
- Multi-source: Easy to add new providers (10 lines of code)

---

### Phase 6: DOI-Aware Evaluation (10-12 hours)

**Goal**: Improve evaluation accuracy for multi-database queries.

**Problem**: Current evaluation only matches by PMID, missing Scopus-only articles that have DOI but no PMID.

**Key Components:**

1. **Enhanced Gold Standard Format (2 hours)**
   - Add DOI column to gold CSV
   - Update loader to return (pmids, dois)
   - Maintain backward compatibility with old format

2. **Multi-Key Matching (3-4 hours)**
   - Implement `set_metrics_multi_key()` function
   - Match using PMID OR DOI
   - Report detailed breakdown (X by PMID, Y by DOI, Z missed)
   - **Benefit**: +5-15% recall improvement on Scopus queries

3. **Query Execution Updates (2 hours)**
   - Modify `_execute_query_bundle()` to track DOIs
   - Update all callers to handle both identifiers
   - Update JSON output format

4. **Aggregation Updates (3 hours)**
   - Load DOIs from query results
   - Aggregate by DOI + PMID union
   - Output: backward-compatible text files + enhanced JSON
   - Update all strategies: consensus_k2, precision_gated_union, etc.

**Deliverables:**
- Enhanced gold CSV format
- `set_metrics_multi_key()` function
- Updated query execution pipeline
- Updated aggregation strategies
- Migration guide for existing users

**Success Criteria:**
- +5-15% recall improvement on Scopus queries
- No regressions on existing datasets
- Backward compatible with existing tools
- Detailed match reporting

---

### Phase 7: Advanced Features (15-18 hours)

**Goal**: Additional quality-of-life improvements and edge case handling.

**Key Components:**

1. **Fuzzy Title Matching (4-5 hours)**
   - Handle articles without DOI/PMID
   - Use rapidfuzz for similarity scoring (≥0.90 threshold)
   - Include author + year in scoring
   - **Benefit**: +2-5% recall for non-indexed articles

2. **Enhanced Manual Review Interface (5 hours)**
   - Interactive CLI for reviewing low-confidence matches
   - Show: extracted metadata, API results, confidence
   - Actions: Accept, Reject, Edit, Skip
   - Batch operations support
   - **Benefit**: <30 seconds per study review

3. **Performance Optimization (3 hours)**
   - Profile and identify bottlenecks
   - Implement parallel API lookups with asyncio
   - Optimize fuzzy matching
   - **Benefit**: 50% reduction in processing time

4. **Documentation and Testing (3 hours)**
   - Update all guides with Wave 2 features
   - Integration testing of all enhancements
   - Create Wave 2 release notes
   - Migration guide from Wave 1

**Deliverables:**
- `utils/fuzzy_title_matcher.py`
- `scripts/review_interface.py`
- Performance-optimized code
- Comprehensive Wave 2 documentation

**Success Criteria:**
- Fuzzy matching: <5% false positive rate
- Review interface: Clear and efficient
- Performance: 50% faster processing
- Documentation: All features documented

---

## Wave 2 Decision Framework

### When to Implement Wave 2

**Implement If:**
- ✅ Using Scopus/WoS in addition to PubMed
- ✅ Need higher quality assurance (clinical reviews)
- ✅ Budget allows 3-5x LLM costs for validation
- ✅ Long-term tool development (multi-year project)
- ✅ Complex PDFs with known parsing issues
- ✅ Need cross-database validation of identifiers

**Can Skip If:**
- ⏸️ PubMed-only queries sufficient
- ⏸️ Wave 1 accuracy meets requirements (100% on ai_2022)
- ⏸️ Time or cost constraints
- ⏸️ Short-term project (one-off reviews)
- ⏸️ Simple, clean PDFs
- ⏸️ Single database queries

### Partial Implementation Options

Wave 2 features are modular and can be implemented independently:

**Option A: DOI-Aware Evaluation Only (10-12 hours)**
- Essential if using Scopus/WoS
- Skip quality assurance features
- Best ROI for multi-database queries

**Option B: Quality Assurance Only (12-18 hours)**
- Choose: Multi-agent OR Sampling (not both)
- Skip DOI-aware evaluation if PubMed-only
- Best for high-accuracy requirements

**Option C: Future-Proofing Only (8-10 hours)**
- Implement provider pattern only
- Skip immediate quality features
- Best for long-term extensibility

---

## Implementation Roadmap Summary

```
Wave 1 (Core) - 87 hours
├─ Phase 1: Reference Extraction (18h) ✅
├─ Phase 2: ID Lookup System (35h) ✅
├─ Phase 3: Workflow Integration (22h) ⏸️ 85% complete
└─ Phase 4: Documentation (12h) ⏸️ Partial

             ↓ Decision Point

Wave 2 (Enhancements) - 37-48 hours 📋
├─ Phase 5: Quality Assurance (12-18h)
│  ├─ Multi-agent validation (4-6h)
│  ├─ Sampling-based extraction (3-4h)
│  └─ Multi-source API integration (8-10h)
├─ Phase 6: DOI-Aware Evaluation (10-12h)
│  ├─ Enhanced gold format (2h)
│  ├─ Multi-key matching (3-4h)
│  ├─ Query execution updates (2h)
│  └─ Aggregation updates (3h)
└─ Phase 7: Advanced Features (15-18h)
   ├─ Fuzzy title matching (4-5h)
   ├─ Review interface (5h)
   ├─ Performance optimization (3h)
   └─ Documentation (3h)
```

**Total Effort**:
- Wave 1 Only: 87 hours (2-3 weeks)
- Wave 1 + Wave 2: 124-135 hours (3-4 weeks)

**Recommended Approach**:
1. Complete Wave 1 (4-6 hours remaining)
2. Test on all datasets (Godos_2024, sleep_apnea)
3. Evaluate if Wave 2 is needed based on use case
4. If implementing Wave 2, start with Phase 6 (DOI-aware evaluation) if using multi-database queries

---
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
