# Phase 1: Reference Extraction - Testing & Validation Guide

## Overview

This document provides comprehensive testing procedures for the reference extraction system (Phase 1, Task 1.4).

**Status**: Ready for testing once API keys are configured  
**Estimated Time**: 2 hours  
**Target Accuracy**: >90% for reference detection and field extraction

---

## Prerequisites

### 1. API Key Configuration

Set up at least one LLM provider API key:

```bash
# Option 1: Anthropic Claude (recommended)
export ANTHROPIC_API_KEY="your-key-here"

# Option 2: OpenAI GPT
export OPENAI_API_KEY="your-key-here"

# Option 3: Google Gemini
export GOOGLE_API_KEY="your-key-here"
```

**Cost Estimates** (for typical systematic review with 50-100 references):
- Claude 3.5 Sonnet: $0.10 - $0.30 per paper
- GPT-4 Turbo: $0.15 - $0.40 per paper  
- Gemini 1.5 Pro: $0.05 - $0.15 per paper

### 2. Install API Client Libraries

```bash
conda activate systematic_review_queries

# For Claude
pip install anthropic

# For GPT
pip install openai

# For Gemini
pip install google-generativeai
```

---

## Test Suite 1: Unit Tests (Completed ✅)

**Status**: 24/24 tests passing

Run unit tests:
```bash
conda run -n systematic_review_queries pytest tests/test_extract_references.py -v
```

**Coverage**:
- ✅ Markdown file reading (UTF-8, latin-1, errors)
- ✅ Section identification (5+ heading patterns)
- ✅ JSON parsing (clean, wrapped, with text, invalid)
- ✅ Reference validation (valid, minimal, errors)
- ✅ Prompt template loading

---

## Test Suite 2: Integration Tests (Manual)

### Test Case 1: Godos_2024 Study

**Objective**: Extract references from Mediterranean diet systematic review

**Command**:
```bash
python scripts/extract_references.py Godos_2024 --llm-model claude-3-5-sonnet-20241022 --debug
```

**Expected Output**:
- ✅ References section identified successfully
- ✅ 20-40 references extracted
- ✅ JSON file created: `studies/Godos_2024/extracted_references.json`
- ✅ DOI coverage: >50% (nutritional studies typically have DOIs)
- ✅ PMID coverage: >30% (biomedical journals)
- ✅ Average confidence: >0.85
- ✅ Processing time: <2 minutes

**Validation Checklist**:
```
[ ] Section was correctly identified
[ ] All references were extracted (compare with original paper)
[ ] No false positives (non-references included)
[ ] Author names correctly parsed (Last Initial format)
[ ] Journal names extracted without abbreviation issues
[ ] Years are valid (1900-2026)
[ ] DOIs are valid format (10.xxxx/...)
[ ] PMIDs are numeric only
[ ] Confidence scores reflect extraction quality
[ ] Raw citations preserved for verification
```

**Manual Review**:
1. Open `studies/Godos_2024/paper_Godos_2024.md`
2. Count total references in paper: ______
3. Open `studies/Godos_2024/extracted_references.json`
4. Count extracted references: ______
5. Calculate accuracy: ______ / ______ = _____%

**Spot Check** (select 5 random references):
```
Ref #1: [ ] Correct  [ ] Minor errors  [ ] Major errors
Ref #2: [ ] Correct  [ ] Minor errors  [ ] Major errors
Ref #3: [ ] Correct  [ ] Minor errors  [ ] Major errors
Ref #4: [ ] Correct  [ ] Minor errors  [ ] Major errors
Ref #5: [ ] Correct  [ ] Minor errors  [ ] Major errors
```

---

### Test Case 2: ai_2022 Study

**Objective**: Extract references from AI in healthcare systematic review

**Command**:
```bash
python scripts/extract_references.py ai_2022 --llm-model claude-3-5-sonnet-20241022 --debug
```

**Expected Output**:
- ✅ References section identified
- ✅ 30-60 references extracted
- ✅ JSON file created: `studies/ai_2022/extracted_references.json`
- ✅ DOI coverage: >60% (computer science journals)
- ✅ PMID coverage: >20% (healthcare subset)
- ✅ Average confidence: >0.85
- ✅ Processing time: <2 minutes

**Validation Checklist**: (Same as Test Case 1)

---

### Test Case 3: Edge Cases & Error Handling

#### Test 3a: Non-existent Study
```bash
python scripts/extract_references.py nonexistent_study
```
**Expected**: ❌ Error message: "File not found: studies/nonexistent_study/paper_nonexistent_study.md"

#### Test 3b: File Without References Section
Create a test markdown file without references:
```bash
echo "# Test Paper\n\nNo references here." > /tmp/test_no_refs.md
python scripts/extract_references.py test --markdown-file /tmp/test_no_refs.md
```
**Expected**: ❌ Error message: "Could not find references section in document"

#### Test 3c: Invalid API Key
```bash
ANTHROPIC_API_KEY="invalid" python scripts/extract_references.py Godos_2024
```
**Expected**: ❌ Error message: "API call failed: Invalid API key"

#### Test 3d: Different LLM Models
```bash
# Test with GPT-4
python scripts/extract_references.py Godos_2024 --llm-model gpt-4-turbo

# Test with Gemini
python scripts/extract_references.py Godos_2024 --llm-model gemini-1.5-pro
```
**Expected**: ✅ Similar extraction quality across models

---

## Test Suite 3: Performance Testing

### Metrics to Record

| Study | Total Refs | Extracted | Accuracy | Processing Time | Cost | DOI % | PMID % |
|-------|-----------|-----------|----------|-----------------|------|-------|--------|
| Godos_2024 | | | | | | | |
| ai_2022 | | | | | | | |

**Target Metrics**:
- Accuracy: >90%
- Processing Time: <2 min per paper
- Cost: <$0.30 per paper
- DOI Coverage: >50%
- PMID Coverage: >30%

---

## Test Suite 4: Quality Assurance

### Common Extraction Errors to Check

**Author Name Issues**:
- [ ] Authors with special characters (é, ñ, ö, etc.)
- [ ] Corporate authors (organizations, consortia)
- [ ] "et al." handling
- [ ] Missing first names

**Journal Name Issues**:
- [ ] Abbreviated journal names
- [ ] Non-English journal names
- [ ] Journal name with special punctuation

**Year Issues**:
- [ ] Years outside valid range (1900-2026)
- [ ] Missing years
- [ ] Years in parentheses or brackets

**DOI Issues**:
- [ ] DOI URLs instead of plain DOI (should normalize)
- [ ] Invalid DOI format
- [ ] Missing DOIs for recent papers

**Citation Format Variations**:
- [ ] APA format
- [ ] Vancouver format
- [ ] Chicago format
- [ ] Harvard format
- [ ] Custom/mixed formats

---

## Test Suite 5: Regression Testing

After any code changes, re-run:

```bash
# 1. Unit tests
pytest tests/test_extract_references.py -v

# 2. Full extraction on reference studies
python scripts/extract_references.py Godos_2024
python scripts/extract_references.py ai_2022

# 3. Compare outputs with baseline
diff studies/Godos_2024/extracted_references.json studies/Godos_2024/extracted_references_baseline.json
```

**Save baselines**:
```bash
cp studies/Godos_2024/extracted_references.json studies/Godos_2024/extracted_references_baseline.json
cp studies/ai_2022/extracted_references.json studies/ai_2022/extracted_references_baseline.json
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'anthropic'"
**Solution**: Install API client: `pip install anthropic`

### Issue: "API call failed: Rate limit exceeded"
**Solution**: Wait 60 seconds and retry, or use `--debug` to see API call details

### Issue: "JSON parsing error"
**Solution**: 
1. Check LLM response with `--debug` flag
2. Verify prompt template includes clear JSON formatting instructions
3. Try different LLM model (Claude typically has best JSON adherence)

### Issue: "Low extraction accuracy (<80%)"
**Solution**:
1. Check if references section was correctly identified
2. Verify citation format is recognized in prompt
3. Add more citation format examples to prompt
4. Try higher-capability model (e.g., Claude 3.5 Sonnet vs Claude 3 Haiku)

### Issue: "High cost per paper (>$0.50)"
**Solution**:
1. Use section identification to extract only references (not full paper)
2. Switch to more cost-effective model (Gemini Pro)
3. Reduce prompt length by removing examples

---

## Success Criteria (Task 1.4)

Phase 1 testing is complete when:

- [x] All 24 unit tests passing
- [ ] Extraction tested on Godos_2024 with >90% accuracy
- [ ] Extraction tested on ai_2022 with >90% accuracy
- [ ] Processing time <2 minutes per paper
- [ ] Cost <$0.30 per paper
- [ ] Edge cases handled gracefully (no crashes)
- [ ] Common extraction errors documented
- [ ] Baseline outputs saved for regression testing

---

## Next Steps (Phase 2)

Once testing is complete and extraction quality is validated:

1. **Phase 2.1**: Implement CrossRef API lookup for DOIs
2. **Phase 2.2**: Implement PubMed E-utilities for PMIDs
3. **Phase 2.3**: Build unified lookup orchestrator
4. **Phase 2.4**: Add confidence scoring for lookups
5. **Phase 2.5**: Create manual review interface
6. **Phase 2.6**: End-to-end integration testing

---

## Testing Log Template

```
Date: __________
Tester: __________
API Key Used: [ ] Claude  [ ] GPT  [ ] Gemini

Test Case: Godos_2024
- References in paper: ______
- References extracted: ______
- Accuracy: ______%
- Processing time: ______ seconds
- Cost: $______
- DOI coverage: ______%
- PMID coverage: ______%
- Issues found: _______________________________

Test Case: ai_2022
- References in paper: ______
- References extracted: ______
- Accuracy: ______%
- Processing time: ______ seconds
- Cost: $______
- DOI coverage: ______%
- PMID coverage: ______%
- Issues found: _______________________________

Overall Assessment:
[ ] PASS - Ready for Phase 2
[ ] PARTIAL - Minor issues to address
[ ] FAIL - Major issues require rework

Notes:
________________________________________
________________________________________
________________________________________
```

---

## Approval

Testing completed by: ________________  
Date: ________________  
Status: [ ] Approved  [ ] Revisions needed  

Approved by: ________________  
Date: ________________  
