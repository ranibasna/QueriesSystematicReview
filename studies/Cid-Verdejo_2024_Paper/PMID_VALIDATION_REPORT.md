# Multi-Source PMID Validation Report: Cid-Verdejo_2024_Paper Study

## Executive Summary

Two AI agents (ChatGPT, Gemini) were used to identify PMIDs for the 10 included studies in the Cid-Verdejo_2024_Paper systematic review. Direct validation against PubMed revealed significant differences in accuracy:

| Source | Correct | Incorrect | Accuracy |
|--------|---------|-----------|----------|
| **ChatGPT** | 10 | 0 | **100%** |
| **Gemini** | 0 | 10 | **0%** |

## Key Finding

**Gemini completely hallucinated all 10 PMIDs.** The PMIDs provided by Gemini:
- Were all valid PubMed IDs (they exist in PubMed)
- But referred to completely different studies than claimed
- Had DOIs that did not match the papers

### Example Discrepancies (Gemini)

| Study | DOI Claimed by Gemini | PMID Given | Actual DOI of that PMID |
|-------|----------------------|------------|-------------------------|
| Castroflorio 2014 | 10.1111/joor.12191 | 24941918 | 10.1159/000362761 (Bolla 2014) |
| Maeda 2019 | 10.1111/joor.12782 | 30810243 | 10.1002/hep.30593 (Wu 2019) |
| Mainieri 2012 | 10.1111/j.1365-2842.2012.02287.x | 22353147 | 10.1111/j.1475-6773.2012.01387.x (Cook 2012) |

**Pattern observed**: Gemini appears to fabricate DOIs with similar patterns to real journal articles (e.g., `10.1111/joor.*` for Journal of Oral Rehabilitation) but assigns them to completely unrelated PMIDs.

## Validation Method - Detailed Explanation

### Overview
The validation process treats **PubMed as ground truth** and uses **DOIs as unique identifiers** to verify that each claimed PMID actually matches the intended study.

### Step-by-Step Process

#### Step 1: Organize Source Files
```bash
# Place AI-collected CSVs in: studies/Cid-Verdejo_2024_Paper/pmids_multiple_sources/
ls -1 studies/Cid-Verdejo_2024_Paper/pmids_multiple_sources/
# Output:
#   Cid-Verdejo_2024_included_studies_pmids_chatgpt.csv
#   Cid-Verdejo_2024_included_studies_pmids_gemini.csv
```

#### Step 2: Run Validation
```bash
conda run -n systematic_review_queries \
    python scripts/validate_pmids_direct.py Cid-Verdejo_2024_Paper --json-report
```

#### Step 3: Validation Logic
For each study:
1. **Load** PMIDs and DOIs from both sources (ChatGPT and Gemini)
2. **Fetch** actual metadata from PubMed for each unique PMID
3. **Compare** claimed DOI vs actual DOI from PubMed
4. **Score** each source: correct if DOI matches, incorrect if different

#### Step 4: Select Best Source
The script automatically selects PMIDs from the most accurate source (ChatGPT: 100% vs Gemini: 0%)

## Generated Files

| File | Description |
|------|-------------|
| `gold_pmids_Cid-Verdejo_2024_Paper.csv` | Simple format (pmid column only) for workflow |
| `gold_pmids_Cid-Verdejo_2024_Paper_detailed.csv` | Full metadata (pmid, doi, author, year, title) |
| `pmid_validation_report_Cid-Verdejo_2024_Paper.json` | Complete validation details |

## Validated Gold PMIDs

All 10 studies have been validated:

| PMID | First Author | Year | Title (truncated) |
|------|-------------|------|-------------------|
| 24374575 | Deregibus | 2014 | Reliability of a portable device for the detection of sleep bruxism |
| 9493526 | Gallo | 1997 | Reliability of scoring EMG orofacial events... |
| 31085074 | Maeda | 2020 | Validity of single-channel masseteric electromyography... |
| 22668619 | Mainieri | 2012 | Validation of the Bitestrip versus polysomnography... |
| 28513083 | Miettinen | 2018 | Screen-printed ambulatory electrode set enables accurate diagnostics... |
| 35095085 | Sakuma | 2022 | Comparison of the occurrence of sleep bruxism under accustomed conditions... |
| 17618147 | Shochat | 2007 | Validation of the BiteStrip screener for sleep bruxism |
| 26527206 | Stuginski-Barbosa | 2016 | Diagnostic validity of the use of a portable single-channel... |
| 21707698 | Yamaguchi | 2012 | Comparison of ambulatory and polysomnographic recording... |
| 36648354 | Yanez-Regonesi | 2023 | Diagnostic accuracy of a portable device (Bruxoff®)... |

## Workflow Integration

### Using Generated Gold File

```bash
# The gold file is ready for use in the systematic review workflow
python llm_sr_select_and_score.py \
    --gold-csv studies/Cid-Verdejo_2024_Paper/gold_pmids_Cid-Verdejo_2024_Paper.csv \
    ...
```

### Verification

```bash
# Verify the gold file loads correctly
conda run -n systematic_review_queries python -c "
from llm_sr_select_and_score import load_gold_pmids

gold = load_gold_pmids('studies/Cid-Verdejo_2024_Paper/gold_pmids_Cid-Verdejo_2024_Paper.csv')
print(f'✅ Loaded {len(gold)} gold PMIDs')
for pmid in sorted(gold, key=int):
    print(f'   {pmid}')
"
```

## Key Insights

### Gemini's Hallucination Pattern

Gemini consistently:
1. **Fabricated plausible-looking DOIs** with correct journal prefixes
2. **Found valid PMIDs** from PubMed (not random numbers)
3. **Failed to verify** that DOI → PMID mapping was correct
4. **Year and domain matched loosely** (e.g., all dental/medical, around same years)

This makes Gemini's hallucinations **particularly dangerous** because:
- The PMIDs look legitimate (they're real PubMed IDs)
- The DOIs have correct format (10.XXXX/journal.YYYY)
- Only DOI verification reveals the mismatch

### ChatGPT's Success

ChatGPT provided:
- Exact DOI matches for all 10 studies
- Correct PMID for each DOI
- Consistent, verifiable data

## Recommendations

### For This Study (Cid-Verdejo_2024_Paper)
✅ Use the validated `gold_pmids_Cid-Verdejo_2024_Paper.csv` file  
✅ All 10 PMIDs have been verified via PubMed API  
✅ Ready for systematic review workflow

### General Recommendations

| Recommendation | Priority | Rationale |
|---------------|----------|-----------|
| **DO NOT use Gemini for PMID extraction** | Critical | 0% accuracy across both studies tested |
| **Prefer ChatGPT** | High | 100% accuracy in both ai_2022 and Cid-Verdejo studies |
| **Always validate PMIDs** | High | Run validation script before trusting any AI-collected PMIDs |
| **Require DOI+PMID pairs** | High | DOIs enable verification against PubMed |
| **Cross-check with 2+ sources** | Medium | Provides confidence and catches errors |

### Validation Workflow

```bash
# Standard workflow for any new study:

# 1. Collect PMIDs from AI agents (require Title + PMID + DOI + Authors)
#    - ChatGPT: ✅ Reliable
#    - Sciespace: ✅ Reliable (if available)
#    - Gemini: ❌ DO NOT USE

# 2. Place CSVs in: studies/<study_name>/pmids_multiple_sources/

# 3. Run validation
conda run -n systematic_review_queries \
    python scripts/validate_pmids_direct.py <study_name> --json-report

# 4. Review validation report and use generated gold_pmids_<study>.csv
```

## Comparison: ai_2022 vs Cid-Verdejo_2024_Paper

| Metric | ai_2022 | Cid-Verdejo_2024_Paper |
|--------|---------|------------------------|
| **Total Studies** | 14 | 10 |
| **Sources** | ChatGPT, Gemini, Sciespace | ChatGPT, Gemini |
| **ChatGPT Accuracy** | 100% (14/14) | 100% (10/10) |
| **Gemini Accuracy** | 0% (0/14) | 0% (0/10) |
| **Gemini Hallucinations** | All 14 PMIDs wrong | All 10 PMIDs wrong |

**Conclusion**: Gemini consistently hallucinates PMIDs across different systematic reviews and topics. This is a systematic failure, not a random error.

## Scripts Used

| Script | Purpose |
|--------|---------|
| `scripts/validate_pmids_direct.py` | **Primary validation** - verifies PMIDs via PubMed API |
| `scripts/validate_pmids_multi_source.py` | Cross-source comparison by title matching |
| `scripts/validate_pmids_by_doi.py` | DOI→PMID lookup (alternative approach) |

## Conclusion

The PMID validation workflow successfully identified that:
- ✅ **ChatGPT is reliable** (100% accuracy across 24 total studies)
- ❌ **Gemini is unreliable** (0% accuracy across 24 total studies)

**The Cid-Verdejo_2024_Paper study now has a validated gold standard of 10 PMIDs ready for use in the systematic review workflow.**
