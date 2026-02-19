#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aggregate PMIDs from multiple queries using several ensemble strategies and optional
PROSPERO-aligned gates. Inputs are JSON details files (from score/select) or sealed files.

Usage (examples):
  python scripts/aggregate_queries.py \
    --inputs benchmark_outputs/details_*.json sealed_outputs/sealed_*.json \
    --outdir aggregates \
    --prospero-gates

  python scripts/aggregate_queries.py \
    --inputs benchmark_outputs/details_*.json \
    --topk 3 --consensus-k 2 --outdir aggregates

  python aggregate_queries.py \
    --inputs details_20250904-200512.json \
    --outdir aggregates_families \
    --families Population Sleep Intervention Design

  python aggregate_queries.py \
    --inputs details_20250904-200512.json \
    --outdir aggregates_weighted \
    --weights 1.0 0.7 0.5 0.5

    python scripts/aggregate_queries.py \
    --inputs benchmark_outputs/details_20250904-200512.json \
    --outdir aggregates \
    --topk 3 \
    --prospero-gates

    What two_stage_screen (the code just above this) is
        Stage 1: Take the union of the first topk queries (default topk=3).
        Stage 2: Apply PROSPERO-aligned text gates (MS + sleep + RCT + non-pharma) only if you pass --prospero-gates.
        There is no --two_stage_screen flag. The script always writes aggregates/two_stage_screen.txt; adding --prospero-gates decides whether Stage 2 filtering is applied.
        
        This writes: consensus_k2.txt, precision_gated_union.txt, weighted_vote.txt, concept_family_consensus.txt (if families provided), two_stage_screen.txt, time_stratified_hybrid.txt.
        Omit --prospero-gates if you want Stage 1 only (no filtering).
        Brief code walkthrough (relevant lines)
        stage1 = union of the first topk queries:
        stage1 = set().union(*[s for _, s in list(pmids_by_query.items())[:args.topk]])
        tss = two_stage_screen(stage1, args.prospero_gates)
        If filters_use_titles is False → return stage1 unchanged.
        If True → fetch titles/abstracts and keep only records passing passes_prospero_gates().
    
Outputs:
  - aggregates/consensus_k{K}.txt           (PMIDs appearing in >=K of top-K queries)
  - aggregates/precision_gated_union.txt    (Union filtered by protocol gates)
  - aggregates/weighted_vote.txt            (Weighted voting)
  - aggregates/concept_family_consensus.txt (By concept families)
  - aggregates/two_stage_screen.txt         (Stage1 broad -> Stage2 gates)
  - aggregates/time_stratified_hybrid.txt   (Split by year strategy)
  
What you’ll get (in aggregates/)

    consensus_k2.txt
    PMIDs that appear in at least 2 of the first top-3 queries. Good precision bump with small recall loss.
    precision_gated_union.txt
    Union of all PMIDs filtered by PROSPERO-aligned textual gates (MS + sleep + RCT signal + non-pharma keywords). If you omit --prospero-gates, this is just the union.
    weighted_vote.txt
    Union where each query contributes a weight; PMIDs whose total weight reaches the threshold are kept (default threshold ≈ median weight). Use --weights to tune.
    concept_family_consensus.txt
    If you provide --families with one label per query, keeps PMIDs that appear in at least 2 distinct families (e.g., Population and Design). Aligns with the protocol’s concept structure.
    two_stage_screen.txt
    Stage 1 = union of the first topk queries (default 3). Stage 2 = apply the PROSPERO gates (if --prospero-gates). This mimics a recall-first then filter workflow.
    time_stratified_hybrid.txt
    Approximate blend of “first half” vs “second half” queries to mimic MeSH-heavy vs text-heavy mixing when date metadata isn’t available. Useful as a diversity baseline.
"""

from __future__ import annotations
import argparse, csv, glob, json, os, re, sys, time
from collections import Counter, defaultdict
from typing import Dict, Iterable, Set, Tuple, List, NamedTuple

# Use Entrez directly to avoid depending on llm_sr_select_and_score for gating
try:
    from Bio import Entrez  # type: ignore
except Exception:  # biopython missing will degrade gates; we handle gracefully below
    Entrez = None  # type: ignore


class Article(NamedTuple):
    """Represents an article with optional identifiers."""
    pmid: str | None
    doi: str | None
    
    def __hash__(self):
        # Use DOI as primary key if available, else PMID
        if self.doi:
            return hash(('doi', self.doi.lower()))
        return hash(('pmid', self.pmid))
    
    def __eq__(self, other):
        if not isinstance(other, Article):
            return False
        # Match by DOI if both have it
        if self.doi and other.doi:
            return self.doi.lower() == other.doi.lower()
        # Otherwise match by PMID
        if self.pmid and other.pmid:
            return self.pmid == other.pmid
        return False


class ArticleRegistry:
    """
    Maintains canonical Article records, merging identifiers from multiple sources.

    When the same article appears in more than one database provider (W2.5 / Issue 2):

      PubMed  → linked_records: {pmid: "34160576", doi: "10.1001/jamacardio.2021.2003"}
      Scopus  → linked_records: {pmid: null,       doi: "10.1001/jamacardio.2021.2003"}

    Without this class, _merge_pmids_dois() would produce two Article objects (because
    Article.__eq__ returns False when one side has only PMID and the other only DOI).
    The registry sees the shared DOI and merges them into ONE Article(pmid="34160576",
    doi="10.1001/jamacardio.2021.2003"), which is the canonical representation that every
    downstream strategy and aggregation step should see.

    Limitation (known, Issue 2 partial fix):
      If PubMed returned a PMID-only record (doi=None in its XML) AND Scopus returned the
      same article as DOI-only (pmid=None), there is no shared identifier to match on, so
      the registry cannot merge them — they remain as two separate Article objects.  This
      affects ~22 articles per query for ai_2022 and is addressed separately by W4
      (title/author/date fuzzy matching).

    Design:
      • _by_doi  — primary index: normalized DOI  → canonical Article
      • _by_pmid — secondary index: PMID          → canonical Article
      • _articles — the full set of canonical Article objects (used by articles())

    Thread safety: not thread-safe (single-threaded aggregation scripts).
    """

    def __init__(self):
        self._by_doi: dict[str, Article] = {}
        self._by_pmid: dict[str, Article] = {}
        self._articles: set[Article] = set()

    def add(self, pmid: str | None, doi: str | None) -> Article:
        """
        Add an article by its identifiers, merging with any existing record
        that shares a DOI or PMID.

        Returns the canonical Article object (merged if applicable, new otherwise).
        Records where both pmid and doi are absent/empty are silently ignored
        and None is returned.
        """
        doi_norm = doi.strip().lower() if doi and doi.strip() else None
        pmid_clean = pmid.strip() if pmid and pmid.strip() else None

        if not doi_norm and not pmid_clean:
            return None  # type: ignore[return-value]  # nothing to add

        # Look up existing canonical record by DOI first, then PMID
        existing: Article | None = None
        if doi_norm and doi_norm in self._by_doi:
            existing = self._by_doi[doi_norm]
        elif pmid_clean and pmid_clean in self._by_pmid:
            existing = self._by_pmid[pmid_clean]

        if existing is not None:
            # Merge: fill in whichever identifier is missing on the existing record.
            merged_pmid = existing.pmid or pmid_clean
            merged_doi = existing.doi or doi_norm
            merged = Article(pmid=merged_pmid, doi=merged_doi)

            if merged != existing:
                # The canonical record gained a new identifier; update everything.
                self._articles.discard(existing)
                self._articles.add(merged)
                # Re-index under both identifiers so future lookups find the merged record.
                if merged.doi:
                    self._by_doi[merged.doi] = merged
                if merged.pmid:
                    self._by_pmid[merged.pmid] = merged
            return merged
        else:
            art = Article(pmid=pmid_clean, doi=doi_norm)
            if art.doi:
                self._by_doi[art.doi] = art
            if art.pmid:
                self._by_pmid[art.pmid] = art
            self._articles.add(art)
            return art

    def articles(self) -> frozenset[Article]:
        """Return an immutable snapshot of all canonical articles."""
        return frozenset(self._articles)

    def __len__(self) -> int:
        return len(self._articles)


def _articles_from_provider_details_per_source(
    provider_details: dict, query_key: str
) -> dict[str, set[Article]]:
    """
    Build **one Article set per database provider** from a ``provider_details`` block.

    Used by ``--split-by-provider`` (W3.4) to give each database its own vote in
    aggregation strategies for a single query.  This transforms the query-by-query
    aggregation question from "API vs Embase" to "which databases agree?", enabling
    ``consensus_k2`` to mean "retrieved by ≥2 databases for this query".

    Each returned key is ``"{provider_name}_{query_key}"`` so that keys remain unique
    across multiple queries when inputs contain more than one bundle.

    Only providers with ``linked_records`` data and at least one valid article are
    included; error providers (those with an ``error`` key) are skipped.
    """
    result: dict[str, set[Article]] = {}
    for pname, pd in provider_details.items():
        if not isinstance(pd, dict) or "error" in pd:
            continue
        linked = pd.get("linked_records")
        if not linked:
            continue
        registry = ArticleRegistry()
        for rec in linked:
            if isinstance(rec, dict):
                registry.add(rec.get("pmid"), rec.get("doi"))
        arts = set(registry.articles())
        if arts:
            result[f"{pname}_{query_key}"] = arts
    return result




def _articles_from_linked_records(provider_details: dict) -> 'set[Article] | None':
    """
    Build an Article set from provider_details when W2.2-format linked_records are
    present.  Returns None when no provider has linked_records so the caller can fall
    back to _merge_pmids_dois() for legacy JSON files.

    Each provider's linked_records is a list of {pmid, doi} dicts.  All providers are
    fed into a single ArticleRegistry so that cross-database duplicates (e.g. PubMed
    returns (pmid=X, doi=Y) and Scopus returns (pmid=None, doi=Y)) are merged into one
    canonical Article rather than counted twice.

    This is the primary W2.5 code path for details_*.json files produced after W2.2.
    """
    has_linked = any(
        isinstance(pd, dict) and 'linked_records' in pd
        for pd in provider_details.values()
    )
    if not has_linked:
        return None

    registry = ArticleRegistry()
    for pd in provider_details.values():
        if not isinstance(pd, dict):
            continue
        for rec in pd.get('linked_records', []):
            registry.add(rec.get('pmid'), rec.get('doi'))
    return set(registry.articles())


def load_articles_from_file(path: str) -> dict[str, set[Article]]:
    """
    Load articles (PMID + DOI pairs) from a JSON file.

    Supports three JSON schemas (in priority order for each item):

    1. **W2.2 provider_details with linked_records** (details_*.json produced after W2.2):
       Each top-level item has a ``provider_details`` dict whose provider entries carry a
       ``linked_records`` list of {pmid, doi} pairs.  These are fed into an
       ``ArticleRegistry`` so that per-provider duplicate articles are merged — e.g. PubMed
       returning (pmid=X, doi=Y) and Scopus returning (pmid=None, doi=Y) collapse into one
       canonical Article(pmid=X, doi=Y).  This is the W2.5 primary path.

    2. **Embase per-record format** (embase_query*.json produced by import_embase_manual.py):
       Each entry has a ``records`` list of {pmid, doi, title, ...} dicts with accurate
       per-record PMID↔DOI pairing.  An ``ArticleRegistry`` is used here too, so Embase
       articles that also appear in the API results are correctly deduplicated in downstream
       aggregation.

    3. **Legacy flat-list format** (details_*.json produced before W2.2, sealed_*.json):
       Falls back to ``_merge_pmids_dois()`` which pairs by index position.  This is the
       pre-W2.5 behavior; it produces Article objects with random PMID↔DOI pairings but
       the output is still correct for DOI-based matching (the dominant case).

    Returns:
        Dict mapping query strings to sets of Article objects.
    """
    articles_by_query: dict[str, set[Article]] = {}
    with open(path, 'r') as f:
        data = json.load(f)

    # ── Format 1: sealed_*.json ─────────────────────────────────────────────────
    # Top-level has 'retrieved_pmids' directly (single-query sealed output).
    if isinstance(data, dict) and 'retrieved_pmids' in data:
        q = data.get('query', f"sealed:{os.path.basename(path)}")
        # W2.5: prefer linked_records when the sealed file includes provider_details.
        provider_details = data.get('provider_details', {})
        articles = _articles_from_linked_records(provider_details)
        if articles is None:
            pmids = data.get('retrieved_pmids', [])
            dois = data.get('retrieved_dois', [])
            articles = _merge_pmids_dois(pmids, dois)
        if articles:
            articles_by_query[q] = articles

    # ── Format 2: dict of entries ────────────────────────────────────────────────
    # Could be:
    #   (a) Embase JSON:  {sha_or_key: {records: [...], retrieved_pmids: [...], ...}}
    #   (b) Old details JSON (dict form): {some_key: {query, pmids, dois, ...}}
    elif isinstance(data, dict):
        for key, item in data.items():
            if not isinstance(item, dict):
                continue

            # W2.5 path (a): Embase format — use accurate per-record PMID+DOI pairs.
            embase_records = item.get('records')
            if embase_records is not None:
                registry = ArticleRegistry()
                for rec in embase_records:
                    if isinstance(rec, dict):
                        registry.add(rec.get('pmid'), rec.get('doi'))
                articles: set[Article] = set(registry.articles())
            else:
                # W2.5 path (b): check for provider_details with linked_records.
                provider_details = item.get('provider_details', {})
                articles = _articles_from_linked_records(provider_details)
                if articles is None:
                    # Legacy fallback.
                    pmids = item.get('pmids') or item.get('retrieved_pmids') or []
                    dois = item.get('dois') or item.get('retrieved_dois') or []
                    articles = _merge_pmids_dois(pmids, dois)

            if articles:
                q = item.get('query', key)
                articles_by_query[q] = articles

    # ── Format 3: list of entries ────────────────────────────────────────────────
    # details_*.json written by score_queries() is always a list.
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                continue

            # W2.5: use provider_details.linked_records when present (W2.2 format).
            provider_details = item.get('provider_details', {})
            articles = _articles_from_linked_records(provider_details)
            if articles is None:
                # Legacy fallback: index-based pairing (Issue 3 known limitation).
                pmids = item.get('pmids') or item.get('retrieved_pmids') or []
                dois = item.get('dois') or item.get('retrieved_dois') or []
                articles = _merge_pmids_dois(pmids, dois)

            if articles:
                q = item.get('query', f"item_{i}")
                articles_by_query[q] = articles

    return articles_by_query


def _merge_pmids_dois(pmids: list, dois: list) -> set[Article]:
    """
    .. deprecated::
       **W2.6 — Legacy fallback only.** This function is retained solely for backward
       compatibility with JSON files produced before W2.2 (i.e. before the
       ``linked_records`` field was added to ``provider_details``).

       **Do not use for new code.** For current-format ``details_*.json`` files (W2.2+)
       use ``_articles_from_linked_records()`` which feeds an ``ArticleRegistry`` and
       correctly deduplicates cross-provider duplicates.  For Embase JSONs, use the
       ``records`` array path in ``load_articles_from_file()``.

    Root problem (Issue 3):
       PMIDs in the JSON are sorted numerically; DOIs are sorted alphabetically.
       Pairing them by index position produces wrong PMID↔DOI associations for
       every single article.  0 of N pairs are correct for typical PubMed outputs.
       DOI-based matching still works (DOI is correct even if paired with wrong PMID),
       but PMID-based matching and cross-DB deduplication (Issue 2) both fail.

    When this function is called it means the caller is processing a legacy JSON file.
    A ``[WARN]`` message is printed so that stale files are visible in run logs.
    """
    if pmids and dois:
        import sys
        print(
            "[WARN] _merge_pmids_dois: using legacy index-based PMID↔DOI pairing "
            "(Issue 3 known limitation). Re-run the query to generate a JSON with "
            "linked_records for accurate pairing.",
            file=sys.stderr,
        )
    articles = set()
    
    # Create paired articles up to min length
    min_len = min(len(pmids), len(dois))
    for i in range(min_len):
        pmid = str(pmids[i]).strip() if pmids[i] else None
        doi = str(dois[i]).strip().lower() if dois[i] else None
        if pmid or doi:
            articles.add(Article(pmid=pmid, doi=doi))
    
    # Add remaining PMIDs
    for i in range(min_len, len(pmids)):
        pmid = str(pmids[i]).strip()
        if pmid:
            articles.add(Article(pmid=pmid, doi=None))
    
    # Add remaining DOIs
    for i in range(min_len, len(dois)):
        doi = str(dois[i]).strip().lower()
        if doi:
            articles.add(Article(pmid=None, doi=doi))
    
    return articles


def load_articles_from_file_split(path: str) -> dict[str, set[Article]]:
    """
    Like :func:`load_articles_from_file` but in **split-by-provider mode** (W3.4):
    each database provider in ``provider_details`` becomes its own pool keyed as
    ``"{provider}_{query}"`` instead of collapsing all providers into one combined pool.

    This enables ``consensus_k2`` to mean "retrieved by ≥2 databases for this query"
    rather than "retrieved by the combined API pool in ≥2 query strategies".

    Only ``details_*.json`` list entries with ``provider_details.linked_records`` data
    benefit from per-source splitting.  Entries without ``linked_records`` (legacy format
    or error providers) fall back to the combined pool via :func:`load_articles_from_file`.

    Non-list JSON schemas (sealed files, Embase imports, old dict-format details) are
    forwarded to :func:`load_articles_from_file` unchanged.
    """
    articles_by_query: dict[str, set[Article]] = {}
    with open(path, "r") as f:
        data = json.load(f)

    if not isinstance(data, list):
        # Sealed / Embase / old dict-format: use the standard combined loader.
        return load_articles_from_file(path)

    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        q = item.get("query", f"item_{i}")
        provider_details = item.get("provider_details", {})
        per_source = _articles_from_provider_details_per_source(provider_details, q)
        if per_source:
            articles_by_query.update(per_source)
        else:
            # Fallback: no per-provider linked_records — use combined pool.
            articles = _articles_from_linked_records(provider_details)
            if articles is None:
                pmids = item.get("pmids") or item.get("retrieved_pmids") or []
                dois = item.get("dois") or item.get("retrieved_dois") or []
                articles = _merge_pmids_dois(pmids, dois)
            if articles:
                articles_by_query[q] = articles

    return articles_by_query


def load_all_articles_split(inputs: list[str]) -> dict[str, set[Article]]:
    """Load articles in split-by-provider mode from multiple input files."""
    merged: dict[str, set[Article]] = {}
    paths: list[str] = []
    for pat in inputs:
        paths.extend(glob.glob(pat))
    for p in paths:
        for q, articles in load_articles_from_file_split(p).items():
            merged.setdefault(q, set()).update(articles)
    return merged


def load_pmids_from_file(path: str) -> dict[str, set[str]]:
    """
    Legacy function: Load PMIDs only (backward compatibility).
    """
    pmids_by_query: dict[str, set[str]] = {}
    with open(path, 'r') as f:
        data = json.load(f)
    # Handle formats:
    # 1) sealed_*.json: single object with 'retrieved_pmids'
    # 2) details_*.json (dict): {id: {query, pmids}}
    # 3) details_*.json (list): [ {query, retrieved_pmids|pmids, ...}, ... ]
    if isinstance(data, dict) and 'retrieved_pmids' in data:
        q = data.get('query', f"sealed:{os.path.basename(path)}")
        pmids_by_query[q] = set(data.get('retrieved_pmids', []))
    elif isinstance(data, dict):
        for key, item in data.items():
            if isinstance(item, dict):
                pmids = item.get('pmids') or item.get('retrieved_pmids') or []
                if pmids:
                    q = item.get('query', key)
                    pmids_by_query[q] = set(pmids)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                pmids = item.get('pmids') or item.get('retrieved_pmids') or []
                if pmids:
                    q = item.get('query', f"item_{i}")
                    pmids_by_query[q] = set(pmids)
    return pmids_by_query


def load_all_articles(inputs: list[str]) -> dict[str, set[Article]]:
    """Load articles (PMID + DOI pairs) from multiple input files.

    W3.2 double-counting guard: if any ``details_*.json`` file has entries with
    ``'embase'`` in ``providers_included`` (i.e. Embase was integrated via
    ``--embase-jsons`` during scoring), AND the same ``inputs`` list also contains
    standalone ``embase_query*.json`` files, a clear warning is printed because each
    Embase article will receive two votes in consensus strategies.  The caller is
    responsible for not passing both; the shell workflow handles this automatically.
    """
    merged: dict[str, set[Article]] = {}
    paths: list[str] = []
    for pat in inputs:
        paths.extend(glob.glob(pat))

    # --- W3.2: double-counting guard -------------------------------------------
    standalone_embase = [
        p for p in paths
        if os.path.basename(p).startswith("embase_query") and p.endswith(".json")
    ]
    if standalone_embase:
        for p in paths:
            if not (os.path.basename(p).startswith("details_") and p.endswith(".json")):
                continue
            try:
                with open(p) as _f:
                    _d = json.load(_f)
                if isinstance(_d, list) and any(
                    "embase" in item.get("providers_included", [])
                    for item in _d
                    if isinstance(item, dict)
                ):
                    import sys as _sys
                    print(
                        f"[WARN] Double-counting risk detected: {len(standalone_embase)} standalone "
                        "Embase JSON file(s) are being loaded alongside details_*.json files that "
                        "already contain Embase results (field 'providers_included' contains 'embase'). "
                        "Each Embase article will receive two votes in consensus strategies. "
                        "Remove standalone Embase JSONs from AGGREGATE_INPUTS, or re-run scoring "
                        "without --embase-jsons to use the standalone approach.",
                        file=_sys.stderr,
                    )
                    break
            except Exception:
                pass
    # ---------------------------------------------------------------------------

    for p in paths:
        for q, articles in load_articles_from_file(p).items():
            merged.setdefault(q, set()).update(articles)
    return merged


def load_all(inputs: list[str]) -> dict[str, set[str]]:
    """Legacy function: Load PMIDs only (backward compatibility)."""
    merged: dict[str, set[str]] = {}
    paths: list[str] = []
    for pat in inputs:
        paths.extend(glob.glob(pat))
    for p in paths:
        for q, pmids in load_pmids_from_file(p).items():
            merged.setdefault(q, set()).update(pmids)
    return merged


def prospero_gate_predicates() -> list[re.Pattern]:
    # Kept for backward-compat; not used by the relaxed gate below.
    pats = [
        re.compile(r"\bmultiple sclerosis\b", re.I),
        re.compile(r"\bsleep\b|insomnia|sleep apnea|restless leg|narcolep|REM sleep behavior", re.I),
        re.compile(r"randomi[sz]ed|trial|placebo|randomly", re.I),
        re.compile(r"non[- ]?pharmacolog|non[- ]?invas|behavior|cognitive|exercise|rehabilitation|psychotherap|mindfulness|meditation", re.I),
    ]
    return pats

# Relaxed gate regexes (compiled once)
_MS_RX = re.compile(r"\bmultiple sclerosis\b", re.I)
_SLEEP_RX = re.compile(r"\bsleep\b|insomnia|apnea|restless\s*leg|narcolep|REM sleep", re.I)
_RCT_RX = re.compile(r"randomi[sz]ed|trial|placebo|randomly", re.I)
_NONPHARMA_RX = re.compile(r"non[- ]?pharmacolog|non[- ]?invas|behavior|cognitive|exercise|rehabilitation|psychotherap|mindfulness|meditation", re.I)

_RATE_LIMIT = 0.34

def set_ncbi_identity(email: str | None = None, api_key: str | None = None):
    if Entrez is None:
        return
    Entrez.email = email or os.getenv('NCBI_EMAIL', 'you@example.com')
    Entrez.api_key = api_key or os.getenv('NCBI_API_KEY')


def fetch_min_titles(pmids: set[str]) -> dict[str, dict]:
    """Fetch minimal metadata from PubMed: Title and Abstract for the given PMIDs.

    Returns a mapping: { pmid: { 'Title': str, 'Abstract': str } }
    If biopython is unavailable or an error occurs, returns an empty dict.
    """
    if Entrez is None or not pmids:
        return {}

    # Parse MEDLINE text capturing TI and AB with continuation lines
    def parse_medline(text: str) -> Dict[str, dict]:
        out: Dict[str, dict] = {}
        cur: Dict[str, str] | None = None
        cur_field: str | None = None
        for raw in text.splitlines():
            line = raw.rstrip("\n")
            if line.startswith('PMID- '):
                if cur and cur.get('PMID'):
                    out[str(cur['PMID'])] = cur
                cur = {'PMID': line.split('- ', 1)[1].strip(), 'Title': '', 'Abstract': ''}
                cur_field = None
            elif cur is not None and line.startswith('TI  - '):
                cur['Title'] = line.split('- ', 1)[1].strip()
                cur_field = 'Title'
            elif cur is not None and line.startswith('AB  - '):
                cur['Abstract'] = line.split('- ', 1)[1].strip()
                cur_field = 'Abstract'
            elif cur is not None and line.startswith('      ') and cur_field:
                cur[cur_field] = (cur[cur_field] + ' ' + line.strip()).strip()
        if cur and cur.get('PMID'):
            out[str(cur['PMID'])] = cur
        return out

    ids = [str(p).strip() for p in pmids if str(p).strip()]
    meta: Dict[str, dict] = {}
    BATCH = 200
    for i in range(0, len(ids), BATCH):
        chunk = ids[i:i+BATCH]
        try:
            h = Entrez.efetch(db='pubmed', id=','.join(chunk), rettype='medline', retmode='text')
            txt = h.read(); h.close(); time.sleep(_RATE_LIMIT)
            meta.update(parse_medline(txt))
        except Exception:
            # best-effort: skip bad batch
            time.sleep(_RATE_LIMIT)
            continue
    return meta


def passes_prospero_gates(rec: dict) -> bool:
    """Relaxed gate: require (MS AND Sleep) AND (RCT OR Non‑pharma). Works on Title+Abstract."""
    text = ' '.join(str(rec.get(k, '')) for k in ('title','Title','abstract','Abstract'))
    if not text.strip():
        return False
    if not (_MS_RX.search(text) and _SLEEP_RX.search(text)):
        return False
    if not (_RCT_RX.search(text) or _NONPHARMA_RX.search(text)):
        return False
    return True


def write_list(path: str, ids: set[str]):
    """Write PMID list to text file (legacy format)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        for x in sorted(ids, key=lambda s: int(re.sub(r"\D","", s) or 0)):
            f.write(f"{x}\n")


def write_articles_csv(path: str, articles: set[Article]):
    """
    Write articles to CSV file with pmid,doi columns.
    
    This format enables multi-key matching during evaluation,
    improving recall by 5-15% for Scopus/WoS queries.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Sort by PMID if available, else by DOI
    def sort_key(a: Article):
        if a.pmid:
            return (0, int(re.sub(r"\D", "", a.pmid) or 0), a.pmid)
        return (1, 0, a.doi or "")
    
    sorted_articles = sorted(articles, key=sort_key)
    
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['pmid', 'doi'])
        for a in sorted_articles:
            writer.writerow([a.pmid or '', a.doi or ''])


def articles_to_pmids(articles: set[Article]) -> set[str]:
    """Extract PMIDs from articles (for legacy compatibility)."""
    return {a.pmid for a in articles if a.pmid}


# ============================================================================
# Multi-key (Article-based) aggregation strategies
# ============================================================================

def consensus_k_articles(articles_by_query: dict[str, set[Article]], topk: int, k: int) -> set[Article]:
    """Consensus strategy using Article objects."""
    items = list(articles_by_query.items())[:topk]
    cnt = Counter()
    for _, s in items:
        cnt.update(s)
    return {article for article, c in cnt.items() if c >= k}


def precision_gated_union_articles(articles_by_query: dict[str, set[Article]], use_titles: bool) -> set[Article]:
    """Precision-gated union using Article objects."""
    universe = set().union(*articles_by_query.values()) if articles_by_query else set()
    if not use_titles or not universe:
        return universe
    
    # For gating, we need PMIDs to fetch metadata
    pmids = articles_to_pmids(universe)
    meta = fetch_min_titles(pmids)
    
    if not meta:
        return universe
    
    # Keep articles that pass gates (by PMID) or have no PMID (DOI-only kept)
    return {a for a in universe if a.pmid is None or (a.pmid in meta and passes_prospero_gates(meta[a.pmid]))}


def weighted_vote_articles(articles_by_query: dict[str, set[Article]], weights: list[float]) -> set[Article]:
    """Weighted voting using Article objects."""
    qs = list(articles_by_query.items())
    w = weights or [1.0] * len(qs)
    total = defaultdict(float)
    for (i, (_q, s)) in enumerate(qs):
        wi = w[i] if i < len(w) else w[-1]
        for article in s:
            total[article] += wi
    thr = sorted(w)[len(w)//2] if w else 1.0
    return {article for article, score in total.items() if score >= thr}


def concept_family_consensus_articles(articles_by_family: dict[str, dict[str, set[Article]]], required_families: int = 2) -> set[Article]:
    """Concept family consensus using Article objects."""
    families = list(articles_by_family.keys())
    all_articles = set().union(*[set().union(*articles_by_family[fam].values()) for fam in families]) if families else set()
    result = set()
    for article in all_articles:
        hit_fams = sum(1 for fam in families if any(article in s for s in articles_by_family[fam].values()))
        if hit_fams >= required_families:
            result.add(article)
    return result


def two_stage_screen_articles(high_recall: set[Article], filters_use_titles: bool) -> set[Article]:
    """Two-stage screen using Article objects."""
    if not filters_use_titles or not high_recall:
        return set(high_recall)
    
    pmids = articles_to_pmids(high_recall)
    meta = fetch_min_titles(pmids)
    
    if not meta:
        return set(high_recall)
    
    # Keep articles that pass gates (by PMID) or have no PMID (DOI-only kept)
    return {a for a in high_recall if a.pmid is None or (a.pmid in meta and passes_prospero_gates(meta[a.pmid]))}


def time_stratified_hybrid_articles(articles_by_query: dict[str, set[Article]]) -> set[Article]:
    """Time-stratified hybrid using Article objects."""
    qs = list(articles_by_query.items())
    mid = len(qs) // 2
    a = set().union(*[s for _, s in qs[:mid]]) if mid else set()
    b = set().union(*[s for _, s in qs[mid:]]) if mid else set()
    return a.union(b)


# ============================================================================
# Legacy (PMID-only) aggregation strategies
# ============================================================================

def consensus_k(pmids_by_query: dict[str,set[str]], topk: int, k: int) -> set[str]:
    items = list(pmids_by_query.items())[:topk]
    cnt = Counter()
    for _, s in items:
        cnt.update(s)
    return {pid for pid, c in cnt.items() if c >= k}


def precision_gated_union(pmids_by_query: dict[str,set[str]], use_titles: bool) -> set[str]:
    universe = set().union(*pmids_by_query.values()) if pmids_by_query else set()
    if not use_titles or not universe:
        return universe
    meta = fetch_min_titles(universe)
    # Safe fallback: if metadata can't be fetched, return ungated universe
    if not meta:
        return universe
    return {pid for pid in universe if pid in meta and passes_prospero_gates(meta[pid])}


def weighted_vote(pmids_by_query: dict[str,set[str]], weights: list[float]) -> set[str]:
    qs = list(pmids_by_query.items())
    w = weights or [1.0] * len(qs)
    total = defaultdict(float)
    for (i, (_q, s)) in enumerate(qs):
        wi = w[i] if i < len(w) else w[-1]
        for pid in s:
            total[pid] += wi
    # default threshold is median of weights
    thr = sorted(w)[len(w)//2] if w else 1.0
    return {pid for pid, score in total.items() if score >= thr}


def concept_family_consensus(pmids_by_family: dict[str, dict[str,set[str]]], required_families: int = 2) -> set[str]:
    # pmids_by_family: {family: {query: set(pmids)}}
    votes = Counter()
    families = list(pmids_by_family.keys())
    all_pmids = set().union(*[set().union(*pmids_by_family[fam].values()) for fam in families]) if families else set()
    for pid in all_pmids:
        hit_fams = sum(1 for fam in families if any(pid in s for s in pmids_by_family[fam].values()))
        if hit_fams >= required_families:
            votes[pid] += 1
    return set(votes.keys())


def two_stage_screen(high_recall: set[str], filters_use_titles: bool) -> set[str]:
    if not filters_use_titles or not high_recall:
        return set(high_recall)
    meta = fetch_min_titles(high_recall)
    # Safe fallback: if metadata can't be fetched, return stage1 unchanged
    if not meta:
        return set(high_recall)
    return {pid for pid in high_recall if pid in meta and passes_prospero_gates(meta[pid])}


def time_stratified_hybrid(pmids_by_query: dict[str,set[str]]) -> set[str]:
    # Without metadata dates, approximate by mixing top-half queries (treat as MeSH-heavy) and bottom-half (text-heavy)
    qs = list(pmids_by_query.items())
    mid = len(qs)//2
    a = set().union(*[s for _, s in qs[:mid]]) if mid else set()
    b = set().union(*[s for _, s in qs[mid:]]) if mid else set()
    return a.union(b)


def main():
    ap = argparse.ArgumentParser(description="Aggregate PMIDs from multiple query outputs")
    ap.add_argument('--inputs', nargs='+', required=True, help='details_*.json and/or sealed_*.json globs')
    ap.add_argument('--outdir', default='aggregates')
    ap.add_argument('--topk', type=int, default=3)
    ap.add_argument('--consensus-k', type=int, default=2)
    ap.add_argument('--prospero-gates', action='store_true', help='Filter using PROSPERO-aligned textual gates (requires fetch_titles)')
    ap.add_argument('--weights', nargs='*', type=float, help='Weights for weighted voting (order = as loaded)')
    ap.add_argument('--families', nargs='*', help='Family labels per query, same order as loaded (e.g., Population Sleep Intervention Design ...)')
    ap.add_argument('--multi-key', action='store_true', 
                    help='Use multi-key mode: output CSV with pmid,doi columns for multi-key evaluation. '
                         'This improves recall by 5-15%% for Scopus/WoS queries.')
    # W3.4: per-provider pool splitting for query-by-query aggregation.
    # When active, each database (pubmed, scopus, wos, embase …) in provider_details
    # becomes its own pool keyed as "{provider}_{query}".  consensus_k2 then means
    # "articles retrieved by ≥2 databases for this query" rather than "found in ≥2
    # query strategies", which is semantically correct for single-query bundled inputs.
    # Use in query-by-query mode ONLY; in normal mode it changes the consensus semantics
    # from "across query variants" to "across databases across query variants".
    ap.add_argument('--split-by-provider', action='store_true',
                    help='Load each database provider as its own pool (W3.4). '
                         'In query-by-query mode this makes consensus_k2 mean '
                         '“retrieved by ≥2 databases for this query”. '
                         'Requires details_*.json files with provider_details.linked_records.')
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    # Initialize NCBI identity only if gates are used (to support Entrez calls)
    if args.prospero_gates:
        try:
            set_ncbi_identity(os.getenv('NCBI_EMAIL', 'you@example.com'), os.getenv('NCBI_API_KEY'))
        except Exception:
            pass

    # Use multi-key mode if requested
    use_multi_key = getattr(args, 'multi_key', False)
    split_by_provider = getattr(args, 'split_by_provider', False)

    if split_by_provider:
        print("[INFO] --split-by-provider active: each database provider forms its own pool.")
        if not use_multi_key:
            print(
                "[WARN] --split-by-provider has no effect without --multi-key: "
                "per-provider pooling requires linked_records (W2.2+ format). "
                "Add --multi-key to activate split-by-provider mode.",
                file=sys.stderr,
            )

    if use_multi_key:
        # Multi-key mode: track both PMIDs and DOIs
        if split_by_provider:
            articles_by_query = load_all_articles_split(args.inputs)
            # Use ALL pools for consensus when split-by-provider: topk defaults to 3
            # but with 4 providers (pubmed/scopus/wos/embase) we want all pools considered.
            effective_topk = max(len(articles_by_query), args.topk)
            print(
                f"[INFO] split-by-provider: {len(articles_by_query)} provider pool(s) loaded; "
                f"using topk={effective_topk} for consensus strategies."
            )
        else:
            articles_by_query = load_all_articles(args.inputs)
            effective_topk = args.topk
        if not articles_by_query:
            print('No inputs loaded', file=sys.stderr)
            sys.exit(1)
        
        print(f"[INFO] Multi-key mode enabled. Loaded {len(articles_by_query)} queries with PMID+DOI tracking.")
        
        # 1) consensus ≥K of top-K
        cset = consensus_k_articles(articles_by_query, effective_topk, args.consensus_k)
        write_articles_csv(os.path.join(args.outdir, f'consensus_k{args.consensus_k}.csv'), cset)
        print(f"  ✓ consensus_k{args.consensus_k}: {len(cset)} articles")
        
        # 2) precision-gated union
        pgun = precision_gated_union_articles(articles_by_query, args.prospero_gates)
        write_articles_csv(os.path.join(args.outdir, 'precision_gated_union.csv'), pgun)
        print(f"  ✓ precision_gated_union: {len(pgun)} articles")
        
        # 3) weighted voting
        wv = weighted_vote_articles(articles_by_query, args.weights or [])
        write_articles_csv(os.path.join(args.outdir, 'weighted_vote.csv'), wv)
        print(f"  ✓ weighted_vote: {len(wv)} articles")
        
        # 4) concept-family consensus
        fams = args.families or []
        articles_by_family: dict[str, dict[str, set[Article]]] = defaultdict(dict)
        if fams and len(fams) == len(articles_by_query):
            for (fam, (q, s)) in zip(fams, articles_by_query.items()):
                articles_by_family[fam][q] = s
        cfc = concept_family_consensus_articles(articles_by_family, required_families=2) if articles_by_family else set()
        if cfc:
            write_articles_csv(os.path.join(args.outdir, 'concept_family_consensus.csv'), cfc)
            print(f"  ✓ concept_family_consensus: {len(cfc)} articles")
        
        # 5) two-stage screen
        stage1 = set().union(*[s for _, s in list(articles_by_query.items())[:effective_topk]])
        tss = two_stage_screen_articles(stage1, args.prospero_gates)
        write_articles_csv(os.path.join(args.outdir, 'two_stage_screen.csv'), tss)
        print(f"  ✓ two_stage_screen: {len(tss)} articles")
        
        # 6) time-stratified hybrid
        tsh = time_stratified_hybrid_articles(articles_by_query)
        write_articles_csv(os.path.join(args.outdir, 'time_stratified_hybrid.csv'), tsh)
        print(f"  ✓ time_stratified_hybrid: {len(tsh)} articles")
        
        print(f"\nWrote multi-key aggregates (CSV format) in {args.outdir}")
    
    else:
        # Legacy mode: PMID-only
        pmids_by_query = load_all(args.inputs)
        if not pmids_by_query:
            print('No inputs loaded', file=sys.stderr)
            sys.exit(1)
        
        # 1) consensus ≥K of top-K
        cset = consensus_k(pmids_by_query, args.topk, args.consensus_k)
        write_list(os.path.join(args.outdir, f'consensus_k{args.consensus_k}.txt'), cset)

        # 2) precision-gated union
        pgun = precision_gated_union(pmids_by_query, args.prospero_gates)
        write_list(os.path.join(args.outdir, 'precision_gated_union.txt'), pgun)

        # 3) weighted voting
        wv = weighted_vote(pmids_by_query, args.weights or [])
        write_list(os.path.join(args.outdir, 'weighted_vote.txt'), wv)

        # 4) concept-family consensus
        fams = args.families or []
        pmids_by_family: dict[str, dict[str,set[str]]] = defaultdict(dict)
        if fams and len(fams) == len(pmids_by_query):
            for (fam, (q, s)) in zip(fams, pmids_by_query.items()):
                pmids_by_family[fam][q] = s
        cfc = concept_family_consensus(pmids_by_family, required_families=2) if pmids_by_family else set()
        if cfc:
            write_list(os.path.join(args.outdir, 'concept_family_consensus.txt'), cfc)

        # 5) two-stage screen
        stage1 = set().union(*[s for _, s in list(pmids_by_query.items())[:args.topk]])
        tss = two_stage_screen(stage1, args.prospero_gates)
        write_list(os.path.join(args.outdir, 'two_stage_screen.txt'), tss)

        # 6) time-stratified hybrid (approximate)
        tsh = time_stratified_hybrid(pmids_by_query)
        write_list(os.path.join(args.outdir, 'time_stratified_hybrid.txt'), tsh)

        print(f"Wrote aggregates in {args.outdir}")


if __name__ == '__main__':
    main()
