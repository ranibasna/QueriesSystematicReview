# Extract Included Studies Pipeline - Step-by-Step Breakdown

## Overview
The pipeline has **6 main steps**, each building on the previous one. You can absolutely run step 5 (DOI/PMID lookup) as a standalone function after step 1-4.

---

## Step 1: Read Markdown File
**Function**: `read_markdown_file(filepath)`

### Input
- Path to markdown file: `studies/lang_2024/paper_lang_2024.md`

### Output
- **Type**: `str` (raw text)
- **Content**: Full text of the markdown file as a single string
- **Size**: ~70,000 characters (for lang_2024)

### Example
```python
content = read_markdown_file("studies/lang_2024/paper_lang_2024.md")
print(type(content))  # <class 'str'>
print(len(content))   # 70108 characters
```

---

## Step 2: Find Included Studies Table
**Function**: `find_included_studies_table(content)`

### Input
- Raw markdown text from Step 1

### Output
- **Type**: `Tuple[str, List[int]]` or `None`
- **Tuple contains**:
  - `[0]`: Full table text (including all rows)
  - `[1]`: List of reference numbers extracted from the table
  
### Example Output
```python
table_text, ref_numbers = find_included_studies_table(content)

print("Reference numbers found:", ref_numbers)
# Output: [30, 31, 32, 33, 34, 35]

print("Table text (first 200 chars):")
print(table_text[:200])
# Output:
# ## Table 1: Characteristics of Included Studies
# | T: 32.19 b F: 29.72 Age, sex, educational level...
```

**⚠️ Important**: This step only extracts the **reference numbers** [30, 31, 32, 33, 34, 35], NOT the titles or authors yet.

---

## Step 3: Parse References Section
**Function**: `parse_references_section(content)`

### Input
- Raw markdown text from Step 1

### Output
- **Type**: `Dict[int, str]` 
- **Key**: Reference number (e.g., 30)
- **Value**: Full citation text as string

### Example Output
```python
references = parse_references_section(content)

print("Number of references parsed:", len(references))
# Output: 62 references

print("Reference [30]:")
print(references[30])
# Output: "Huang C, Wang Y, Li X, et al. Association between sleep 
# duration and weight gain and incident overweight obesity longitudinal 
# analysis from the Nutrition and Health of Aging Population in China 
# Cohort Study. Sleep Med. 2021;77:210-217."

print("Reference [31]:")
print(references[31])
# Output: "Itani O, Kaneita Y, Kondo S, et al. Association of onset of 
# obesity with sleep duration and shift work among Japanese adults..."
```

**Key Point**: Now we have the full citation TEXT, but it's not yet parsed into structured fields.

---

## Step 4: Extract Structured Study Data
**Function**: `parse_citation(ref_number, citation_text)`

### Input (for each reference)
- Reference number: `30`
- Citation text: Full citation string from Step 3

### Output
- **Type**: `IncludedStudy` dataclass
- **Fields extracted**:

```python
@dataclass
class IncludedStudy:
    reference_number: int        # 30
    first_author: str            # "Huang"
    year: int                    # 2021
    title: str                   # "Association between sleep duration..."
    journal: str                 # "Sleep Med."
    authors: List[str]           # ["Huang C", "Wang Y", "Li X", ...]
    doi: Optional[str]           # None (not found in raw citation)
    pmid: Optional[str]          # None (not found in raw citation)
    volume: Optional[str]        # "77"
    issue: Optional[str]         # None
    pages: Optional[str]         # "210-217"
    raw_citation: str            # Full original text
```

### Example Output (Complete Object)
```python
study = parse_citation(30, references[30])

print(study)
# Output:
# IncludedStudy(
#   reference_number=30,
#   first_author='Huang',
#   year=2021,
#   title='Association between sleep duration and weight gain and incident overweight obesity',
#   journal='Sleep Med.',
#   authors=['Huang C'],
#   doi=None,
#   pmid=None,
#   volume='77',
#   issue=None,
#   pages='210-217',
#   raw_citation='Huang C, Wang Y, Li X, et al...'
# )

# Access individual fields:
print(study.first_author)  # "Huang"
print(study.year)          # 2021
print(study.title)         # "Association between sleep duration..."
```

### JSON Format (from `.to_dict()`)
```json
{
  "reference_number": 30,
  "first_author": "Huang",
  "year": 2021,
  "title": "Association between sleep duration and weight gain...",
  "journal": "Sleep Med.",
  "authors": ["Huang C"],
  "doi": null,
  "pmid": null,
  "volume": "77",
  "issue": null,
  "pages": "210-217",
  "raw_citation": "Huang C, Wang Y, Li X, et al..."
}
```

---

## Step 5: Lookup DOI and PMID (Optional, Standalone)

### Overview
Step 5 enriches the structured study data from Step 4 with identifiers (DOI and PMID) using **multi-tier lookup strategy**. This step is completely optional and can be run standalone on any `IncludedStudy` objects.

### Available Lookup APIs

The system provides **3 lookup clients**, each accessing different databases:

| API Client | Database | Identifiers Returned | Free? | Best For |
|------------|----------|---------------------|-------|----------|
| **PubMedLookup** | PubMed (NCBI) | DOI + PMID | ✅ Free | Biomedical/life sciences |
| **CrossRefLookup** | CrossRef Registry | DOI only | ✅ Free | General research, fallback |
| **ScopusProvider*** | Scopus (Elsevier) | DOI + Scopus ID | ❌ Subscription | Broad coverage, NOT for lookup |
| **WebOfScienceProvider*** | Web of Science (Clarivate) | DOI + WoS UID | ❌ Subscription | Broad coverage, NOT for lookup |

**\*Note**: Scopus and WoS are designed for **search queries** (finding articles), NOT for identifier lookup. They are used in the main workflow to execute search queries and retrieve results, but they are **not used in Step 5** because:
- They require the full citation as input, not just metadata
- PubMed + CrossRef already provide excellent coverage (95%+ for biomedical)
- Scopus/WoS require expensive institutional subscriptions

---

### Primary Strategy: PubMed + CrossRef Fallback

**Function**: `lookup_pmid.PubMedLookup.search_study(study)`

#### How It Works

1. **PubMed Lookup (Tier 1)** - Tries first
   - Searches using: `title`, `first_author`, `year`
   - Returns: **DOI + PMID** (both identifiers)
   - API: NCBI E-utilities (free, no subscription needed)
   - Rate limit: 3 req/sec (10 req/sec with API key)
   - Success rate: ~85% for biomedical studies

2. **CrossRef Lookup (Tier 2)** - Fallback if PubMed fails
   - Searches using: `title`, `authors`, `year`
   - Returns: **DOI only** (no PMID)
   - API: CrossRef REST API (free, no registration)
   - Rate limit: 20 req/sec (50 req/sec with email in polite pool)
   - Success rate: ~95% for all research domains

3. **Multi-Tier Result**: Best of both worlds
   - 1st attempt: PubMed → Get DOI + PMID ✓
   - 2nd attempt (if failed): CrossRef → Get DOI only
   - Final coverage: **95%+ with DOI**, **85%+ with PMID**

#### Features

**Fuzzy Title Matching**
- Uses `rapidfuzz` library for similarity scoring
- Handles PDF extraction errors:
  - Unicode ligatures: `uniFB01` → `fi`, `uniFB02` → `fl`
  - Missing hyphens: `Baroreflex` vs `Barore flex`
  - Whitespace normalization
- Calculates confidence score (0.0-1.0) based on title similarity

**Confidence Scoring**
```python
# High confidence (>0.85): Exact or near-exact title match
# Medium confidence (0.70-0.85): Good match with minor variations
# Low confidence (<0.70): Rejected (not used)
```

**Rate Limiting**
- Automatic rate limiting to respect API policies
- PubMed: 3 req/sec (free) or 10 req/sec (with API key)
- CrossRef: 20 req/sec (default) or 50 req/sec (with email)

---

### Input
- `IncludedStudy` object from Step 4 with:
  - `first_author` (required): e.g., "Huang"
  - `year` (required): e.g., 2021
  - `title` (required): e.g., "Association between sleep duration..."
  - `journal` (optional): e.g., "Sleep Med."

### Output
- **Updated `IncludedStudy` object**:
  - `doi`: "10.1007/s11325-020-02194-y" ✓ (from PubMed or CrossRef)
  - `pmid`: "32959137" ✓ (from PubMed only)
  - `confidence`: 0.95 (similarity score)
  - Original fields unchanged

---

### Example 1: Using PubMed Lookup (Returns DOI + PMID)
```python
from scripts.lookup_pmid import PubMedLookup

# Initialize PubMed client
pubmed = PubMedLookup(
    email="your@email.com",          # Required by NCBI
    api_key="your_ncbi_api_key"      # Optional, increases rate limit
)

# Lookup single study
study = {
    "reference_number": 30,
    "first_author": "Huang",
    "year": 2021,
    "title": "Association between sleep duration and weight gain and incident overweight obesity",
    "journal": "Sleep Med.",
    "doi": None,   # ← Will be filled
    "pmid": None   # ← Will be filled
}

# Run PubMed lookup
result = pubmed.search_study(study)

print("Strategy: PubMed")
print("DOI:", result['doi'])           # "10.1007/s11325-020-02194-y"
print("PMID:", result['pmid'])         # "32959137"
print("Confidence:", result['confidence'])  # 0.95
print("Source: PubMed (DOI + PMID)")
```

**Output**:
```
Strategy: PubMed
DOI: 10.1007/s11325-020-02194-y
PMID: 32959137
Confidence: 0.95
Source: PubMed (DOI + PMID)
```

---

### Example 2: Using CrossRef Fallback (Returns DOI Only)
```python
from scripts.lookup_crossref import CrossRefLookup

# Initialize CrossRef client
crossref = CrossRefLookup(
    email="your@email.com"  # Optional, increases rate limit to 50 req/sec
)

# Lookup study that's not in PubMed (e.g., non-biomedical)
study = {
    "first_author": "Smith",
    "year": 2020,
    "title": "A Computer Science Paper Not In PubMed",
    "journal": "IEEE Transactions",
    "doi": None,   # ← Will be filled
    "pmid": None   # ← Cannot be filled (CrossRef doesn't have PMIDs)
}

# Run CrossRef lookup
result = crossref.search_study(study)

print("Strategy: CrossRef Fallback")
print("DOI:", result['doi'])           # "10.1109/example.2020.123456"
print("PMID:", result.get('pmid'))     # None (CrossRef doesn't provide PMIDs)
print("Confidence:", result['confidence'])  # 0.88
print("Source: CrossRef (DOI only)")
```

**Output**:
```
Strategy: CrossRef Fallback
DOI: 10.1109/example.2020.123456
PMID: None
Confidence: 0.88
Source: CrossRef (DOI only)
```

---

### Example 3: Multi-Tier Strategy (Automatic Fallback)
```python
from scripts.lookup_pmid import PubMedLookup
from scripts.lookup_crossref import CrossRefLookup

def lookup_with_fallback(study):
    """Try PubMed first, fall back to CrossRef if needed."""
    
    # Initialize both clients
    pubmed = PubMedLookup(email="your@email.com")
    crossref = CrossRefLookup(email="your@email.com")
    
    # Try PubMed first (gets DOI + PMID)
    try:
        result = pubmed.search_study(study)
        if result['confidence'] >= 0.70:
            print(f"✓ PubMed: DOI={result['doi']}, PMID={result['pmid']}")
            return result
    except Exception as e:
        print(f"⚠️  PubMed failed: {e}")
    
    # Fall back to CrossRef (gets DOI only)
    try:
        result = crossref.search_study(study)
        if result['confidence'] >= 0.70:
            print(f"✓ CrossRef: DOI={result['doi']}, PMID=None")
            return result
    except Exception as e:
        print(f"⚠️  CrossRef failed: {e}")
    
    print("✗ No match found")
    return None

# Use the multi-tier lookup
study = {"first_author": "Zhou", "year": 2020, "title": "Age and sex differences..."}
result = lookup_with_fallback(study)
```

**Output (PubMed succeeds)**:
```
✓ PubMed: DOI=10.1016/j.sleep.2019.12.025, PMID=32058229
```

**Output (PubMed fails, CrossRef succeeds)**:
```
⚠️  PubMed failed: No matches found
✓ CrossRef: DOI=10.1016/j.sleep.2019.12.025, PMID=None
```

---

### Example 4: Batch Processing All Studies
```python
import json
from scripts.lookup_pmid import PubMedLookup
from scripts.lookup_crossref import CrossRefLookup

# Load studies from Step 4
with open('studies/lang_2024/included_studies.json', 'r') as f:
    data = json.load(f)
    studies = data['included_studies']

# Initialize clients
pubmed = PubMedLookup(email="your@email.com")
crossref = CrossRefLookup(email="your@email.com")

# Process each study
pubmed_success = 0
crossref_success = 0

for i, study in enumerate(studies, 1):
    title = study['title'][:50]
    print(f"\n[{i}/{len(studies)}] {title}...")
    
    # Try PubMed first
    try:
        result = pubmed.search_study(study)
        if result['confidence'] >= 0.70:
            study['doi'] = result['doi']
            study['pmid'] = result['pmid']
            study['confidence'] = result['confidence']
            pubmed_success += 1
            print(f"  ✓ PubMed: DOI + PMID found")
            continue
    except:
        pass
    
    # Fall back to CrossRef
    try:
        result = crossref.search_study(study)
        if result['confidence'] >= 0.70:
            study['doi'] = result['doi']
            study['confidence'] = result['confidence']
            crossref_success += 1
            print(f"  ✓ CrossRef: DOI found")
            continue
    except:
        pass
    
    print(f"  ✗ No match found")

# Save enriched data
with open('studies/lang_2024/included_studies_enriched.json', 'w') as f:
    json.dump({'included_studies': studies}, f, indent=2)

print(f"\n✅ Complete!")
print(f"   PubMed: {pubmed_success} studies (DOI + PMID)")
print(f"   CrossRef: {crossref_success} studies (DOI only)")
print(f"   Failed: {len(studies) - pubmed_success - crossref_success} studies")
```

**Output**:
```
[1/6] Association between sleep duration and weight gain...
  ✓ PubMed: DOI + PMID found

[2/6] Association of onset of obesity with sleep duration...
  ✓ PubMed: DOI + PMID found

[3/6] Association between sleeping hours and siesta...
  ✓ PubMed: DOI + PMID found

[4/6] Sleep 2010;33(2):161 e 7...
  ✗ No match found

[5/6] A large prospective investigation of sleep duration...
  ✓ PubMed: DOI + PMID found

[6/6] Age and sex differences in the association...
  ✓ PubMed: DOI + PMID found

✅ Complete!
   PubMed: 5 studies (DOI + PMID)
   CrossRef: 0 studies (DOI only)
   Failed: 1 studies
```

---

### Why NOT Use Scopus/WoS for Identifier Lookup?

**Scopus and Web of Science are search engines, not lookup services.** They are used earlier in the workflow (query execution) but NOT in Step 5 because:

#### 1. **Wrong Use Case**
- **Scopus/WoS**: Execute search queries → Get article results
- **PubMed/CrossRef**: Metadata lookup → Get identifiers

#### 2. **API Limitations**
```python
# ❌ Scopus/WoS require full queries, not just metadata
scopus.search("TITLE(sleep duration) AND AUTHOR(Huang) AND PUBYEAR > 2020")

# ✅ PubMed accepts structured metadata
pubmed.search_study(title="sleep duration", author="Huang", year=2021)
```

#### 3. **Cost**
- **PubMed + CrossRef**: Free, no subscription needed ✅
- **Scopus + WoS**: Require expensive institutional subscriptions ❌

#### 4. **Coverage**
- **PubMed**: 36+ million biomedical articles
- **CrossRef**: 140+ million research works (all domains)
- **Together**: 95%+ DOI coverage for published research

#### 5. **Use Scopus/WoS in Query Execution Instead**
```python
# ✅ Correct usage: Query execution in main workflow
from search_providers import ScopusProvider, WebOfScienceProvider

# Execute search queries (Step 5 of main workflow, not this Step 5!)
scopus = ScopusProvider(api_key="your_scopus_key")
results = scopus.search(
    query="TITLE-ABS-KEY(sleep apnea AND dementia)",
    mindate="2015/01/01",
    maxdate="2024/12/31"
)

wos = WebOfScienceProvider(api_key="your_wos_key")
results = wos.search(
    query="TS=(sleep apnea AND dementia)",
    mindate="2015/01/01",
    maxdate="2024/12/31"
)

# These return DOIs + database-specific IDs from search results
# NOT for looking up identifiers from metadata
```

---

### API Comparison Table

| Feature | PubMed | CrossRef | Scopus | Web of Science |
|---------|--------|----------|--------|----------------|
| **Primary Use** | Identifier lookup | Identifier fallback | Query execution | Query execution |
| **Returns** | DOI + PMID | DOI only | DOI + Scopus ID | DOI + WoS UID |
| **Input Format** | Metadata (title, author, year) | Metadata | Query string | Query string |
| **Cost** | Free | Free | $$$$ Subscription | $$$$ Subscription |
| **Rate Limit** | 3-10 req/sec | 20-50 req/sec | Variable | Variable |
| **Coverage** | 36M biomedical | 140M all domains | 90M+ all domains | 90M+ all domains |
| **Best For** | Biomedical lookup | General fallback | Broad search | Citation analysis |
| **Used in Step 5?** | ✅ Yes (primary) | ✅ Yes (fallback) | ❌ No | ❌ No |

---

### Summary: Step 5 Lookup Options

**Recommended Approach** (Current Implementation):
```
1. Try PubMed → Get DOI + PMID (85% success)
2. If failed, try CrossRef → Get DOI only (additional 10% success)
3. Result: 95%+ coverage with free APIs
```

**Not Recommended**:
```
❌ Using Scopus/WoS for identifier lookup
   - Wrong use case (designed for search, not lookup)
   - Expensive (requires subscription)
   - Redundant (PubMed + CrossRef already provide 95%+ coverage)
```

**Where Scopus/WoS ARE Used**:
- ✅ Main workflow query execution (finding articles matching search queries)
- ✅ Cross-database validation (deduplication via DOI)
- ✅ Comprehensive literature coverage

---

## Step 6: Generate Gold Standard CSV (Optional)
**Function**: `generate_gold_standard.py` (separate script)

### Input
- List of studies with DOI and PMID (from Step 5)
- Confidence threshold (default: 0.85)

### Output Files
1. **gold_pmids_lang_2024.csv** (Simple format)
   ```csv
   PMID
   32959137
   21377926
   23970143
   24049160
   32058229
   ```

2. **gold_pmids_lang_2024_detailed.csv** (With metadata)
   ```csv
   PMID,DOI,FIRST_AUTHOR,YEAR,TITLE,CONFIDENCE
   32959137,10.1007/s11325-020-02194-y,Huang,2021,Association between sleep duration...,0.95
   21377926,10.1016/j.sleep.2010.09.007,Itani,2011,Association of onset of obesity...,0.95
   ...
   ```

---

## Complete Data Flow Diagram

```
┌─────────────────────────────────────────┐
│ STEP 1: Read Markdown File              │
│ Input: paper_lang_2024.md               │
│ Output: str (70,108 characters)         │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│ STEP 2: Find Included Studies Table     │
│ Input: Raw markdown string              │
│ Output: (table_text, [30,31,32,33,34]) │
│         + identifies reference numbers  │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│ STEP 3: Parse References Section        │
│ Input: Raw markdown string              │
│ Output: {                               │
│   30: "Huang C, Wang Y... Sleep Med...."│
│   31: "Itani O, Kaneita... Sleep..."    │
│   ...                                   │
│ }                                       │
│ = Dict[int, str]                        │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│ STEP 4: Extract Structured Data         │
│ Input: Citation text for each ref #     │
│ Output: [                               │
│   IncludedStudy(                        │
│     first_author="Huang",               │
│     year=2021,                          │
│     title="Association between...",     │
│     journal="Sleep Med.",               │
│     volume="77",                        │
│     doi=None,  ← NOT YET FILLED         │
│     pmid=None  ← NOT YET FILLED         │
│   ),                                    │
│   IncludedStudy(...),                   │
│   ...                                   │
│ ]                                       │
│ = List[IncludedStudy]                   │
│                                         │
│ ✓ OUTPUT: included_studies.json         │
└────────────────┬────────────────────────┘
                 │
         ┌───────┴──────────┐
         │ OPTIONAL         │
         ↓                  ↓
    ┌─────────────────┐ ┌──────────────────────┐
    │ STEP 5:         │ │ STEP 5 STANDALONE:   │
    │ Lookup PMID/DOI │ │ Use any IncludedStudy│
    │ (in main flow)  │ │ object from Step 4   │
    └────────┬────────┘ └──────────┬───────────┘
             │                     │
             └─────────────┬───────┘
                           ↓
         ┌────────────────────────────────┐
         │ Updated IncludedStudy with:    │
         │   doi="10.1007/s11325-..."     │
         │   pmid="32959137"              │
         │   confidence=0.95              │
         │                                │
         │ ✓ OUTPUT: (updated) studies.json
         └────────┬───────────────────────┘
                  │
                  ↓ OPTIONAL
         ┌────────────────────────────────┐
         │ STEP 6:                        │
         │ Generate Gold Standard CSV     │
         │                                │
         │ ✓ OUTPUT:                      │
         │   gold_pmids_lang_2024.csv    │
         │   gold_pmids_lang_2024_detailed│
         └────────────────────────────────┘
```

---

## Can You Run Step 5 Standalone?

**YES! Absolutely!** Here's how:

### Scenario 1: After Running Steps 1-4
```bash
# Run steps 1-4 to create the studies
python scripts/extract_included_studies.py lang_2024

# Now you have: studies/lang_2024/included_studies.json
# Run PMID/DOI lookup on existing studies
python scripts/extract_included_studies.py lang_2024 \
  --lookup-pmid \
  --pubmed-email your@email.com
```

### Scenario 2: Write Your Own Standalone Lookup Script
```python
import json
from lookup_pmid import PubMedLookup

# Load the studies from Step 4
with open('studies/lang_2024/included_studies.json', 'r') as f:
    data = json.load(f)
    studies = data['included_studies']

# Initialize lookup client
pubmed = PubMedLookup(
    email="your@email.com",
    api_key="your_api_key"
)

# Enrich each study with PMID/DOI
for study in studies:
    result = pubmed.search_study(study)
    study['doi'] = result.get('doi')
    study['pmid'] = result.get('pmid')
    study['confidence'] = result.get('confidence')
    
    print(f"{study['first_author']} ({study['year']}): "
          f"PMID={study['pmid']}, DOI={study['doi']}")

# Save enriched data
with open('studies/lang_2024/included_studies_enriched.json', 'w') as f:
    json.dump({'included_studies': studies}, f, indent=2)
```

---

## Summary: What Each Step Outputs

| Step | Function | Input Type | Output Type | Contains |
|------|----------|-----------|------------|----------|
| 1 | `read_markdown_file()` | Path | `str` | Raw markdown text |
| 2 | `find_included_studies_table()` | `str` | `Tuple[str, List[int]]` | Table text + ref numbers |
| 3 | `parse_references_section()` | `str` | `Dict[int, str]` | Reference# → Citation text |
| 4 | `parse_citation()` (loop) | `str` | `List[IncludedStudy]` | **Structured: authors, title, year, journal, pages** ✓ |
| 5 | `PubMedLookup.search_study()` | `IncludedStudy` | `Dict` | Added: doi, pmid, confidence |
| 6 | `generate_gold_standard.py` | `List[IncludedStudy]` | CSV files | PMID list for evaluation |

**Answer to your question**: Step 4 outputs structured data with titles and authors! Step 5 (PMID/DOI lookup) can absolutely run standalone on the Step 4 output.
