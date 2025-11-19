# Multi-Database Deduplication: Design & Implementation Guide

## Executive Summary

This document explains how articles from multiple databases (PubMed, Scopus, etc.) will be merged, deduplicated, and matched against the gold standard in the proposed enhancement to the systematic review workflow.

**Current State**: Only PubMed articles are aggregated (285 articles from sleep apnea study)  
**Proposed State**: All databases merged with deduplication (~3,782 unique articles)  
**Key Innovation**: DOI-based deduplication with PMID/gold standard compatibility

---

## Problem Statement

### Current Workflow Limitation

The existing workflow queries multiple databases but only uses PubMed results for aggregation:

```python
# Current behavior in _execute_query_bundle()
combined_pmids: Set[str] = set()  # Only populated by PubMed
combined_dois: Set[str] = set()   # Union of all databases, but UNUSED

# Later in aggregate_queries.py
pmids = item.get('retrieved_pmids')  # Only PubMed PMIDs
```

**Result**: 
- Query 1 example: 285 PubMed articles aggregated, 3,486 Scopus articles ignored
- **92% of data is discarded**

### Why This Is a Problem

1. **Lost Coverage**: Scopus finds articles PubMed misses (and vice versa)
2. **Inaccurate Metrics**: Recall/precision calculated only on PubMed subset
3. **Wasted API Calls**: Querying Scopus but not using its results
4. **Scalability**: Adding more databases won't improve coverage

---

## Proposed Solution: DOI-Based Deduplication

### Core Concept

**Primary Key**: DOI (Digital Object Identifier)  
**Rationale**: DOIs are globally unique across all databases

**Algorithm**:
1. Collect articles from all databases (PubMed, Scopus, Web of Science, etc.)
2. Group articles by DOI
3. For articles without DOIs, assign pseudo-IDs based on provider+native_id
4. Create unified article records with provenance tracking
5. Pass unified records to aggregation and scoring

---

## Detailed Design

### 1. Article Representation

**Unified Article Record**:

```python
@dataclass
class Article:
    """Represents a deduplicated article from any database."""
    unified_id: str           # Primary identifier for this article
    doi: str | None           # DOI if available
    pmid: str | None          # PMID if from PubMed
    scopus_id: str | None     # Scopus ID if from Scopus
    wos_id: str | None        # Web of Science ID if from WoS
    sources: List[str]        # Which databases found this article
    metadata: Dict            # Additional fields (title, year, etc.)
```

**Example 1**: Article found in PubMed and Scopus (with DOI):

```python
Article(
    unified_id="10.1016/j.sleep.2023.12.001",  # DOI is the unified ID
    doi="10.1016/j.sleep.2023.12.001",
    pmid="38123456",
    scopus_id="2-s2.0-85176543210",
    wos_id=None,
    sources=["pubmed", "scopus"],
    metadata={"title": "Sleep apnea and dementia risk", "year": 2023}
)
```

**Example 2**: Article found only in PubMed (no DOI):

```python
Article(
    unified_id="pubmed:38123456",  # Pseudo-ID when no DOI available
    doi=None,
    pmid="38123456",
    scopus_id=None,
    wos_id=None,
    sources=["pubmed"],
    metadata={"title": "Case report: Cognitive decline", "year": 2020}
)
```

### 2. Deduplication Algorithm

**Function**: `deduplicate_across_providers()`

```python
def deduplicate_across_providers(provider_results: Dict[str, ProviderResult]) -> List[Article]:
    """
    Merge articles from multiple providers using DOI-based deduplication.
    
    Args:
        provider_results: Dict mapping provider name to (dois, ids, total)
    
    Returns:
        List of deduplicated Article objects with unified IDs
    """
    # Step 1: Group articles by DOI
    doi_groups: Dict[str, List[Tuple[str, str]]] = {}  # doi -> [(provider, native_id), ...]
    
    for provider_name, (dois_set, ids_set) in provider_results.items():
        # Match DOIs with their corresponding IDs
        for doi in dois_set:
            if doi not in doi_groups:
                doi_groups[doi] = []
            # Find the ID that corresponds to this DOI
            # (In practice, providers return parallel lists or dicts)
            corresponding_id = _find_id_for_doi(doi, provider_name, provider_results)
            doi_groups[doi].append((provider_name, corresponding_id))
    
    # Step 2: Create Article records for DOI-based groups
    articles: List[Article] = []
    for doi, provider_id_pairs in doi_groups.items():
        article = Article(
            unified_id=doi,
            doi=doi,
            pmid=None,
            scopus_id=None,
            wos_id=None,
            sources=[],
            metadata={}
        )
        
        # Populate provider-specific IDs
        for provider, native_id in provider_id_pairs:
            article.sources.append(provider)
            if provider == "pubmed":
                article.pmid = native_id
            elif provider == "scopus":
                article.scopus_id = native_id
            elif provider == "web_of_science":
                article.wos_id = native_id
        
        articles.append(article)
    
    # Step 3: Handle articles without DOIs (assign pseudo-IDs)
    for provider_name, (dois_set, ids_set) in provider_results.items():
        ids_with_dois = _get_ids_with_dois(dois_set, ids_set, provider_name)
        ids_without_dois = ids_set - ids_with_dois
        
        for native_id in ids_without_dois:
            pseudo_id = f"{provider_name}:{native_id}"
            article = Article(
                unified_id=pseudo_id,
                doi=None,
                pmid=native_id if provider_name == "pubmed" else None,
                scopus_id=native_id if provider_name == "scopus" else None,
                wos_id=native_id if provider_name == "web_of_science" else None,
                sources=[provider_name],
                metadata={}
            )
            articles.append(article)
    
    return articles
```

### 3. Integration Points

**Modify `_execute_query_bundle()` in `llm_sr_select_and_score.py`**:

```python
def _execute_query_bundle(providers, qmap: Dict[str, str], mindate: str, maxdate: str):
    """Execute queries across all providers and deduplicate results."""
    
    # Collect raw results from each provider
    provider_results: Dict[str, Tuple[Set[str], Set[str], int]] = {}
    provider_details: Dict[str, Dict] = {}
    
    for provider in providers:
        pname = _provider_name(provider)
        query = qmap.get(pname)
        if not query:
            continue
        
        try:
            dois, ids, total = provider.search(query, mindate, maxdate)
            provider_results[pname] = (dois, ids, total)
            provider_details[pname] = {
                'query': query,
                'results_count': total,
                'retrieved_ids': sorted(ids),
                'retrieved_dois': sorted(dois),
            }
        except Exception as exc:
            # Log error and continue
            provider_details[pname] = {'error': str(exc)}
    
    # ✨ NEW: Deduplicate across providers
    articles = deduplicate_across_providers(provider_results)
    
    # ✨ NEW: Extract unified IDs for aggregation
    unified_ids = [article.unified_id for article in articles]
    
    # BACKWARD COMPATIBILITY: Still extract PMIDs for existing gold standard matching
    pmids = set(article.pmid for article in articles if article.pmid)
    
    # Calculate total (sum before deduplication)
    total_results = sum(total for (_, _, total) in provider_results.values())
    
    return pmids, unified_ids, articles, total_results, provider_details
```

**Modify `select_without_gold()` to store unified IDs**:

```python
def select_without_gold(providers, query_bundles, mindate, maxdate, ...):
    """Run selection pipeline with multi-database deduplication."""
    records = []
    for bundle in query_bundles:
        canonical_query = bundle['canonical']
        
        # ✨ NEW: Returns deduplicated articles
        pmids, unified_ids, articles, total, provider_details = \
            _execute_query_bundle(providers, bundle['per_provider'], mindate, maxdate)
        
        # Calculate metrics on canonical query
        cov = concept_coverage(canonical_query, cdict)
        lint = lint_query(canonical_query)
        feats = selector_features(canonical_query, total, cov, lint, ...)
        
        rec = {
            'query': canonical_query,
            'query_sha256': hashlib.sha256(canonical_query.encode()).hexdigest(),
            'results_count': total,
            **feats,
            'retrieved_pmids': sorted(pmids),      # Backward compatibility
            'unified_ids': sorted(unified_ids),    # ✨ NEW
            'dedup_stats': {                       # ✨ NEW: Deduplication diagnostics
                'total_before_dedup': total,
                'unique_after_dedup': len(articles),
                'articles_with_doi': sum(1 for a in articles if a.doi),
                'articles_without_doi': sum(1 for a in articles if not a.doi),
                'multi_source_articles': sum(1 for a in articles if len(a.sources) > 1),
            },
            'provider_details': provider_details,
        }
        records.append(rec)
    
    # Continue with existing selection logic...
```

---

## Gold Standard Matching Strategy

### Challenge: Gold List Uses PMIDs

**Problem**: Gold standard file contains only PMIDs:

```csv
PMID
34567890
34567891
34567892
...
```

**Question**: How do we match Scopus-only articles (no PMID) against this gold list?

### Solution: Two-Phase Matching

#### Phase 1: Direct PMID Matching (Primary)

```python
def match_against_gold(articles: List[Article], gold_pmids: Set[str]) -> Set[str]:
    """Match articles against gold standard PMIDs."""
    matched_unified_ids = set()
    
    # Phase 1: Direct PMID match
    for article in articles:
        if article.pmid and article.pmid in gold_pmids:
            matched_unified_ids.add(article.unified_id)
    
    return matched_unified_ids
```

**Coverage**: This handles:
- ✅ PubMed-only articles (have PMID)
- ✅ Multi-database articles with PMID (found by both PubMed and Scopus)

#### Phase 2: DOI-Based Cross-Reference (Enhanced)

For Scopus-only articles (no PMID), we need to check if their DOI corresponds to a gold PMID:

```python
def enhance_gold_matching(articles: List[Article], gold_pmids: Set[str]) -> Set[str]:
    """Enhanced matching using DOI→PMID lookup."""
    matched_unified_ids = set()
    
    # Phase 1: Direct PMID match (as above)
    for article in articles:
        if article.pmid and article.pmid in gold_pmids:
            matched_unified_ids.add(article.unified_id)
    
    # Phase 2: DOI-based cross-reference for articles without PMIDs
    scopus_only_articles = [a for a in articles if not a.pmid and a.doi]
    
    for article in scopus_only_articles:
        # Query PubMed: "Does this DOI correspond to any gold PMID?"
        try:
            pmid = lookup_pmid_by_doi(article.doi)  # Uses Entrez API
            if pmid in gold_pmids:
                matched_unified_ids.add(article.unified_id)
                article.pmid = pmid  # Cache for future use
        except Exception:
            pass  # DOI not in PubMed
    
    return matched_unified_ids
```

**Implementation of `lookup_pmid_by_doi()`**:

```python
@retry(wait=wait_exponential(multiplier=1, min=1, max=30), stop=stop_after_attempt(3))
def lookup_pmid_by_doi(doi: str) -> str | None:
    """Query PubMed to find PMID for a given DOI."""
    handle = Entrez.esearch(db='pubmed', term=f'{doi}[DOI]', retmax=1)
    record = Entrez.read(handle)
    handle.close()
    time.sleep(RATE_LIMIT_SECONDS)
    
    id_list = record.get('IdList', [])
    return id_list[0] if id_list else None
```

### Example Scenarios

#### Scenario 1: Article found by PubMed only

```python
article = Article(
    unified_id="pubmed:38123456",
    pmid="38123456",
    scopus_id=None,
    sources=["pubmed"]
)

gold_pmids = {"38123456", "38123457", ...}

# Match: article.pmid in gold_pmids → TRUE
# Result: ✅ True Positive
```

#### Scenario 2: Article found by PubMed AND Scopus (with DOI)

```python
article = Article(
    unified_id="10.1016/j.sleep.2023.12.001",
    doi="10.1016/j.sleep.2023.12.001",
    pmid="38123456",
    scopus_id="2-s2.0-85176543210",
    sources=["pubmed", "scopus"]
)

gold_pmids = {"38123456", ...}

# Match: article.pmid in gold_pmids → TRUE
# Result: ✅ True Positive (multi-database contribution)
```

#### Scenario 3: Article found by Scopus only (with DOI)

```python
article = Article(
    unified_id="10.1002/alz.12345",
    doi="10.1002/alz.12345",
    pmid=None,  # Not in PubMed query results
    scopus_id="2-s2.0-85176543210",
    sources=["scopus"]
)

gold_pmids = {"38999999", ...}  # Assume 38999999 has DOI 10.1002/alz.12345

# Phase 1: article.pmid in gold_pmids → FALSE (pmid is None)
# Phase 2: lookup_pmid_by_doi("10.1002/alz.12345") → "38999999"
#          "38999999" in gold_pmids → TRUE
# Result: ✅ True Positive (discovered via DOI cross-reference)
```

#### Scenario 4: Article found by Scopus only (no DOI)

```python
article = Article(
    unified_id="scopus:2-s2.0-85176543210",
    doi=None,
    pmid=None,
    scopus_id="2-s2.0-85176543210",
    sources=["scopus"]
)

gold_pmids = {...}

# Phase 1: article.pmid in gold_pmids → FALSE
# Phase 2: No DOI available for lookup
# Result: ❌ Cannot match (assumed False Negative or True Negative)
```

**Note**: Scenario 4 is rare for published research (most articles have DOIs).

---

## Aggregation Strategy Updates

### Modify `aggregate_queries.py`

**Current Code**:

```python
def load_pmids_from_file(json_path: str) -> Set[str]:
    """Load PMIDs from benchmark JSON."""
    with open(json_path) as f:
        data = json.load(f)
    pmids = set()
    for item in data:
        pmids.update(item.get('retrieved_pmids', []))  # ❌ PubMed only
    return pmids
```

**Updated Code**:

```python
def load_unified_ids_from_file(json_path: str) -> Set[str]:
    """Load unified IDs from benchmark JSON (with backward compatibility)."""
    with open(json_path) as f:
        data = json.load(f)
    
    unified_ids = set()
    for item in data:
        # ✨ NEW: Prefer unified_ids if available
        if 'unified_ids' in item:
            unified_ids.update(item['unified_ids'])
        else:
            # FALLBACK: Use PMIDs for old JSON files
            unified_ids.update(item.get('retrieved_pmids', []))
    
    return unified_ids
```

### Aggregation Strategies Remain Unchanged

The 5 aggregation strategies (consensus_k2, precision_gated_union, etc.) operate on **sets of IDs**. They don't care if IDs are PMIDs, DOIs, or pseudo-IDs:

```python
# Example: Precision-gated union still works
set_a = {"10.1016/...", "pubmed:123", "10.1002/...", ...}
set_b = {"10.1016/...", "scopus:456", "10.1007/...", ...}
union = set_a | set_b  # Works identically
```

**Key Insight**: Aggregation logic is **ID-agnostic**. Only the final scoring step needs to understand ID types for gold matching.

---

## Scoring Updates

### Modify `score_sets` in `llm_sr_select_and_score.py`

**Current Code**:

```python
def score_sets(aggregate_dir: str, gold_csv: str, outdir: str):
    """Score aggregated PMID sets against gold."""
    gold = load_gold_pmids(gold_csv)
    
    for txt_file in aggregate_dir.glob("*.txt"):
        pmids = read_pmids_from_txt(txt_file)
        tp = len(pmids & gold)  # ❌ Assumes both are PMIDs
        # ...
```

**Updated Code**:

```python
def score_sets(aggregate_dir: str, gold_csv: str, outdir: str):
    """Score aggregated unified IDs against gold PMIDs."""
    gold_pmids = load_gold_pmids(gold_csv)
    
    for txt_file in aggregate_dir.glob("*.txt"):
        unified_ids = read_unified_ids_from_txt(txt_file)
        
        # ✨ NEW: Match unified IDs to gold PMIDs
        tp_unified_ids = match_unified_ids_to_gold(unified_ids, gold_pmids)
        
        tp = len(tp_unified_ids)
        recall = tp / max(len(gold_pmids), 1)
        precision = tp / max(len(unified_ids), 1)
        # ...
```

**Helper Function**:

```python
def match_unified_ids_to_gold(unified_ids: Set[str], gold_pmids: Set[str]) -> Set[str]:
    """
    Match unified IDs (DOIs, PMIDs, pseudo-IDs) against gold PMIDs.
    
    Returns:
        Set of unified IDs that matched gold standard
    """
    matched = set()
    doi_cache: Dict[str, str] = {}  # doi -> pmid
    
    for uid in unified_ids:
        # Case 1: unified_id IS a PMID (backward compatibility)
        if uid in gold_pmids:
            matched.add(uid)
            continue
        
        # Case 2: unified_id is a DOI (format: 10.xxxx/...)
        if uid.startswith("10.") and "/" in uid:
            # Look up PMID for this DOI
            if uid not in doi_cache:
                doi_cache[uid] = lookup_pmid_by_doi(uid)
            
            pmid = doi_cache[uid]
            if pmid and pmid in gold_pmids:
                matched.add(uid)
            continue
        
        # Case 3: unified_id is a pseudo-ID (format: provider:native_id)
        if ":" in uid:
            provider, native_id = uid.split(":", 1)
            if provider == "pubmed" and native_id in gold_pmids:
                matched.add(uid)
            # Scopus-only with no DOI: cannot match gold (PMID-based)
            continue
    
    return matched
```

---

## Performance Considerations

### API Call Overhead

**Concern**: Looking up DOIs→PMIDs for Scopus-only articles adds API calls

**Mitigation**:
1. **Batch requests**: Group DOI lookups into batches
2. **Cache results**: Store DOI→PMID mappings for reuse
3. **Lazy evaluation**: Only lookup DOIs when scoring against gold, not during selection

### Example: Batched DOI Lookup

```python
def batch_lookup_pmids_by_dois(dois: List[str], batch_size: int = 50) -> Dict[str, str]:
    """Lookup PMIDs for multiple DOIs in batches."""
    doi_to_pmid: Dict[str, str] = {}
    
    for batch in _chunk_list(dois, batch_size):
        # Build OR query: doi1[DOI] OR doi2[DOI] OR ...
        query = " OR ".join(f'{doi}[DOI]' for doi in batch)
        
        handle = Entrez.esearch(db='pubmed', term=query, retmax=batch_size)
        record = Entrez.read(handle)
        handle.close()
        time.sleep(RATE_LIMIT_SECONDS)
        
        # Fetch details to map DOIs back to PMIDs
        pmids = record.get('IdList', [])
        if pmids:
            handle = Entrez.efetch(db='pubmed', id=pmids, rettype='medline', retmode='xml')
            records = Entrez.read(handle)
            handle.close()
            time.sleep(RATE_LIMIT_SECONDS)
            
            for article in records.get('PubmedArticle', []):
                pmid = str(article['MedlineCitation']['PMID'])
                doi = _extract_doi(article)
                if doi:
                    doi_to_pmid[doi.lower()] = pmid
    
    return doi_to_pmid
```

---

## Database-Agnostic Design

### Principle: No Hard-Coded Database Names

**Bad Example**:

```python
# ❌ Hard-coded providers
if provider == "pubmed":
    # ...
elif provider == "scopus":
    # ...
elif provider == "web_of_science":
    # ...
```

**Good Example**:

```python
# ✅ Registry-based approach
for provider in providers:
    result = provider.search(query, mindate, maxdate)
    # Deduplication logic is the same for ALL providers
```

### Adding New Databases

**To add Web of Science**:

1. Implement `WebOfScienceProvider` in `search_providers.py`:
   ```python
   class WebOfScienceProvider:
       name = "web_of_science"
       id_type = "wos_id"
       
       def search(self, query, mindate, maxdate):
           # WoS-specific API calls
           return dois, wos_ids, total
   ```

2. Register in `PROVIDER_REGISTRY`:
   ```python
   PROVIDER_REGISTRY = {
       "pubmed": PubMedProvider,
       "scopus": ScopusProvider,
       "web_of_science": WebOfScienceProvider,  # ✨ NEW
   }
   ```

3. **That's it!** Deduplication, aggregation, and scoring automatically work

**No changes needed** in:
- ❌ `_execute_query_bundle()` (already database-agnostic)
- ❌ `aggregate_queries.py` (operates on unified IDs)
- ❌ Gold matching logic (handles any ID type)

---

## Migration Strategy

### Backward Compatibility

**Requirement**: Existing workflows must continue to work without changes

**Implementation**:

1. **Default behavior**: If `--databases` not specified, use PubMed only (current behavior)
2. **Output compatibility**: JSON files include both `retrieved_pmids` (old) and `unified_ids` (new)
3. **Aggregation fallback**: If `unified_ids` missing, use `retrieved_pmids`

### Phased Rollout

**Phase 1** (Current commit):
- ✅ Multi-database querying works
- ✅ Provider-specific results stored in JSON
- ❌ Only PubMed used for aggregation (existing behavior)

**Phase 2** (Proposed enhancement):
- ✨ Implement `deduplicate_across_providers()`
- ✨ Add `unified_ids` to output JSON
- ✨ Update aggregation scripts to read `unified_ids`
- ✅ Backward compatibility via fallback

**Phase 3** (Future):
- ✨ Enhanced DOI→PMID lookup with caching
- ✨ Metadata enrichment (titles, abstracts)
- ✨ Fuzzy title matching for DOI-less articles

---

## Testing Plan

### Unit Tests

```python
def test_deduplicate_with_overlapping_dois():
    """Test articles found by multiple databases with same DOI."""
    pubmed_results = (
        {doi1, doi2},  # DOIs
        {pmid1, pmid2},  # PMIDs
        285
    )
    scopus_results = (
        {doi1, doi3},  # Overlaps on doi1
        {scopus1, scopus2},
        3486
    )
    
    articles = deduplicate_across_providers({
        "pubmed": pubmed_results,
        "scopus": scopus_results
    })
    
    # Should have 3 unique articles (doi1, doi2, doi3)
    assert len(articles) == 3
    
    # Article with doi1 should have both sources
    article_doi1 = next(a for a in articles if a.doi == doi1)
    assert set(article_doi1.sources) == {"pubmed", "scopus"}
    assert article_doi1.pmid == pmid1
    assert article_doi1.scopus_id == scopus1
```

### Integration Tests

```python
def test_end_to_end_workflow_with_deduplication():
    """Test full workflow from queries to scored aggregates."""
    providers = [
        PubMedProvider(email="test@example.com"),
        ScopusProvider(api_key="test_key")
    ]
    
    # Run selection
    select_without_gold(providers, query_bundles, ...)
    
    # Run aggregation
    subprocess.run(["python", "scripts/aggregate_queries.py", ...])
    
    # Run scoring
    score_sets(aggregate_dir, gold_csv, outdir)
    
    # Verify results
    summary = pd.read_csv(f"{outdir}/sets_summary.csv")
    assert summary['recall'].max() > 0.5  # Should improve with multi-DB
```

### Manual Validation

**Test Case**: Sleep apnea study with PubMed + Scopus

**Expected Results**:
- Total unique articles: ~3,782 (vs 285 PubMed-only)
- Articles with DOI: ~3,500 (92%)
- Multi-source articles: ~269 (overlapping DOIs)
- Gold standard recall: Should match or exceed PubMed-only recall

---

## FAQ

### Q1: What if an article has no DOI and is found by multiple databases?

**Answer**: Currently, we assign separate unified IDs per database (e.g., `pubmed:123` and `scopus:456`). In Phase 3, we could add fuzzy title matching to merge these.

### Q2: How do we handle pre-prints vs published versions?

**Answer**: DOIs usually differ (pre-print DOI from arXiv vs journal DOI). These would be treated as separate articles unless we add version-aware merging.

### Q3: Can we match gold standard by title instead of PMID?

**Answer**: Possible but risky (title variations, typos). Better to enhance gold list with DOIs upfront or use DOI→PMID lookup.

### Q4: What about databases that don't provide DOIs?

**Answer**: Assign pseudo-IDs (`provider:native_id`). These can't be matched cross-database but still contribute to coverage within that database.

### Q5: How does this affect aggregation strategy performance?

**Answer**: Aggregation logic is unchanged (set operations on IDs). Performance impact is in the initial deduplication (~1-2 seconds for 10,000 articles) and DOI lookup during scoring (~5-10 minutes for 1,000 lookups with rate limiting).

---

## Summary: Implementation Checklist

### Core Changes

- [ ] Implement `Article` dataclass
- [ ] Implement `deduplicate_across_providers()`
- [ ] Modify `_execute_query_bundle()` to call deduplication
- [ ] Update `select_without_gold()` to store `unified_ids`
- [ ] Update `score_queries()` to store `unified_ids`
- [ ] Implement `lookup_pmid_by_doi()` for gold matching
- [ ] Modify `aggregate_queries.py` to read `unified_ids`
- [ ] Implement `match_unified_ids_to_gold()` for scoring

### Testing

- [ ] Unit test for deduplication with overlapping DOIs
- [ ] Unit test for articles without DOIs
- [ ] Unit test for gold matching with DOIs
- [ ] Integration test for full workflow
- [ ] Manual validation with sleep_apnea study

### Documentation

- [x] Design document (this file)
- [ ] Update README with deduplication explanation
- [ ] Add code comments explaining unified_id format
- [ ] Create troubleshooting guide for multi-database issues

---

**Author**: GitHub Copilot  
**Date**: November 19, 2025  
**Status**: Proposed Design (not yet implemented)  
**Context**: Multi-database support on `feature/multi-database-support` branch
