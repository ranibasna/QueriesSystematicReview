"""W3.1 unit tests: EmbaseLocalProvider

Tests cover:
  1. Basic search() return contract (set, set, int)
  2. PMID↔DOI cache is built from records list (per-record pairing)
  3. PMID-only articles (no DOI) are in pmids but absent from _pmid_to_doi_cache
  4. DOI-only articles (no PMID in record) are in dois but absent from cache
  5. Legacy format fallback (no 'records' list, flat dois/pmids lists)
  6. Hash mismatch with single-entry JSON → single-entry fallback succeeds
  7. Hash mismatch with multi-entry JSON → empty result + warning
  8. Missing JSON file → empty result + warning (no exception)
  9. Date bounds are informational and do not filter results
 10. _execute_query_bundle integrates EmbaseLocalProvider correctly:
     - Embase PMIDs enter combined_pmids (id_type='pmid')
     - Embase DOIs enter combined_dois
     - linked_records are built (same logic as PubMed path)
     - _pmid_to_doi_cache propagates to combined_pmid_to_doi
 11. Real file smoke test against studies/ai_2022/embase_query1.json
"""
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Set

import pytest

sys.path.insert(
    0,
    str(Path(__file__).parent.parent),
)
from search_providers import EmbaseLocalProvider
from llm_sr_select_and_score import _execute_query_bundle


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_json(query: str, records=None, dois=None, pmids=None,
               use_records_key=True) -> bytes:
    """Build a minimal Embase JSON payload and return as bytes."""
    query_hash = hashlib.sha256(query.encode()).hexdigest()
    entry: Dict = {
        "query": query,
        "provider": "embase_manual",
        "results_count": len(records or dois or []),
    }
    if use_records_key and records is not None:
        entry["records"] = records
    if dois is not None:
        entry["retrieved_dois"] = dois
    if pmids is not None:
        entry["retrieved_pmids"] = pmids
        entry["pmids"] = pmids  # legacy alias

    return json.dumps({query_hash: entry}).encode()


def _write_json(tmp_path: Path, query: str, **kwargs) -> Path:
    data = _make_json(query, **kwargs)
    p = tmp_path / "embase_query.json"
    p.write_bytes(data)
    return p


# ── Test 1 ── return signature ─────────────────────────────────────────────

def test_search_returns_correct_types(tmp_path):
    query = "sleep apnea AND child"
    f = _write_json(
        tmp_path, query,
        records=[{"pmid": "11111", "doi": "10.a/b"}],
        dois=["10.a/b"],
        pmids=["11111"],
    )
    p = EmbaseLocalProvider(str(f))
    result = p.search(query, "2010/01/01", "2024/12/31")

    assert len(result) == 3, f"Expected 3-tuple, got {len(result)}-tuple"
    dois, pmids, total = result
    assert isinstance(dois, set), f"dois must be set, got {type(dois)}"
    assert isinstance(pmids, set), f"pmids must be set, got {type(pmids)}"
    assert isinstance(total, int), f"total must be int, got {type(total)}"
    print("PASS test_search_returns_correct_types")


# ── Test 2 ── PMID↔DOI cache from records list ────────────────────────────

def test_cache_built_from_records(tmp_path):
    """Correct per-record pairing is preserved in _pmid_to_doi_cache."""
    query = "q"
    records = [
        {"pmid": "111", "doi": "10.x/1"},
        {"pmid": "222", "doi": "10.x/2"},
    ]
    f = _write_json(tmp_path, query, records=records, dois=["10.x/1", "10.x/2"], pmids=["111", "222"])
    p = EmbaseLocalProvider(str(f))
    p.search(query, "", "")

    assert hasattr(p, "_pmid_to_doi_cache"), "_pmid_to_doi_cache must be set after search()"
    cache = p._pmid_to_doi_cache
    assert cache == {"111": "10.x/1", "222": "10.x/2"}, f"Unexpected cache: {cache}"
    print("PASS test_cache_built_from_records:", cache)


# ── Test 3 ── PMID-only articles ─────────────────────────────────────────

def test_pmid_only_absent_from_cache(tmp_path):
    """Article with PMID but no DOI: appears in pmids return but not in cache."""
    query = "q"
    records = [
        {"pmid": "999", "doi": None},     # no DOI
        {"pmid": "888", "doi": "10.z/z"},
    ]
    dois = ["10.z/z"]
    pmids_ = ["999", "888"]
    f = _write_json(tmp_path, query, records=records, dois=dois, pmids=pmids_)
    p = EmbaseLocalProvider(str(f))
    dois_ret, pmids_ret, total = p.search(query, "", "")

    assert "999" in pmids_ret, "PMID-only article must be in pmids"
    assert "999" not in p._pmid_to_doi_cache, "PMID-only article must NOT be in cache"
    assert "888" in p._pmid_to_doi_cache, "Paired article must be in cache"
    print("PASS test_pmid_only_absent_from_cache")


# ── Test 4 ── DOI normalisation ─────────────────────────────────────────

def test_dois_normalised_to_lowercase(tmp_path):
    """DOIs must be lowercased in both the return set and the cache."""
    query = "q"
    records = [{"pmid": "100", "doi": "10.A/UPPER"}]
    f = _write_json(tmp_path, query, records=records, dois=["10.A/UPPER"], pmids=["100"])
    p = EmbaseLocalProvider(str(f))
    dois_ret, _, _ = p.search(query, "", "")

    assert "10.a/upper" in dois_ret, f"DOI should be lowercased in return set: {dois_ret}"
    assert p._pmid_to_doi_cache.get("100") == "10.a/upper", \
        f"DOI should be lowercased in cache: {p._pmid_to_doi_cache}"
    print("PASS test_dois_normalised_to_lowercase")


# ── Test 5 ── Legacy format (no records list) ─────────────────────────────

def test_legacy_format_flat_lists(tmp_path):
    """Without a 'records' key, flat doi/pmid lists are used (legacy import)."""
    query = "legacy query"
    # Write JSON without 'records': use retrieved_pmids and retrieved_dois
    hash_key = hashlib.sha256(query.encode()).hexdigest()
    entry = {
        "query": query,
        "provider": "embase_manual",
        "results_count": 2,
        "retrieved_dois": ["10.leg/1", "10.leg/2"],
        "retrieved_pmids": ["AAA", "BBB"],
        "pmids": ["AAA", "BBB"],
    }
    f = tmp_path / "embase.json"
    f.write_text(json.dumps({hash_key: entry}))
    p = EmbaseLocalProvider(str(f))
    dois_ret, pmids_ret, total = p.search(query, "", "")

    assert "10.leg/1" in dois_ret
    assert "10.leg/2" in dois_ret
    assert "AAA" in pmids_ret
    assert "BBB" in pmids_ret
    assert total == 2

    # Cache is built from zip of flat lists
    cache = p._pmid_to_doi_cache
    assert isinstance(cache, dict)
    # Both PMIDs should be paired (in zip order)
    assert cache.get("AAA") == "10.leg/1"
    assert cache.get("BBB") == "10.leg/2"
    print("PASS test_legacy_format_flat_lists:", cache)


# ── Test 6 ── Single-entry fallback on hash miss ─────────────────────────

def test_single_entry_fallback_on_hash_miss(tmp_path):
    """If the query hash misses but the file has exactly one entry, use it."""
    stored_query = "exact query text"
    # Caller passes a slightly different text (e.g., double-space stripped)
    caller_query = "different query text"

    records = [{"pmid": "77", "doi": "10.fb/1"}]
    hash_key = hashlib.sha256(stored_query.encode()).hexdigest()
    entry = {
        "query": stored_query,
        "provider": "embase_manual",
        "results_count": 1,
        "records": records,
        "retrieved_dois": ["10.fb/1"],
        "retrieved_pmids": ["77"],
    }
    f = tmp_path / "embase.json"
    f.write_text(json.dumps({hash_key: entry}))

    p = EmbaseLocalProvider(str(f))
    dois_ret, pmids_ret, total = p.search(caller_query, "", "")

    # Should have fallen back to the single entry
    assert "10.fb/1" in dois_ret, f"Expected doi in fallback: {dois_ret}"
    assert "77" in pmids_ret, f"Expected pmid in fallback: {pmids_ret}"
    print("PASS test_single_entry_fallback_on_hash_miss")


# ── Test 7 ── Hash miss with multiple entries → empty ────────────────────

def test_hash_miss_multi_entry_returns_empty(tmp_path, capsys):
    """If hash misses and the file has >1 entry, return empty results."""
    q1 = "query one"
    q2 = "query two"
    h1 = hashlib.sha256(q1.encode()).hexdigest()
    h2 = hashlib.sha256(q2.encode()).hexdigest()
    data = {
        h1: {"query": q1, "provider": "embase_manual", "results_count": 1,
             "records": [{"pmid": "1", "doi": "10.a/b"}],
             "retrieved_dois": ["10.a/b"], "retrieved_pmids": ["1"]},
        h2: {"query": q2, "provider": "embase_manual", "results_count": 1,
             "records": [{"pmid": "2", "doi": "10.c/d"}],
             "retrieved_dois": ["10.c/d"], "retrieved_pmids": ["2"]},
    }
    f = tmp_path / "embase.json"
    f.write_text(json.dumps(data))

    p = EmbaseLocalProvider(str(f))
    dois_ret, pmids_ret, total = p.search("unknown query", "", "")

    assert dois_ret == set(), f"Expected empty dois: {dois_ret}"
    assert pmids_ret == set(), f"Expected empty pmids: {pmids_ret}"
    assert total == 0, f"Expected total=0: {total}"
    assert p._pmid_to_doi_cache == {}

    captured = capsys.readouterr()
    assert "WARN" in captured.err, "Expected WARN in stderr"
    print("PASS test_hash_miss_multi_entry_returns_empty")


# ── Test 8 ── Missing file → empty result + warning ──────────────────────

def test_missing_file_returns_empty(capsys):
    """A non-existent JSON path must return empty results, not raise."""
    p = EmbaseLocalProvider("/does/not/exist.json")
    dois_ret, pmids_ret, total = p.search("q", "", "")

    assert dois_ret == set()
    assert pmids_ret == set()
    assert total == 0
    assert p._pmid_to_doi_cache == {}

    captured = capsys.readouterr()
    assert "WARN" in captured.err
    print("PASS test_missing_file_returns_empty")


# ── Test 9 ── Date bounds are informational only ──────────────────────────

def test_date_bounds_do_not_filter(tmp_path):
    """Providing narrow date bounds does NOT reduce the returned article set."""
    query = "any query"
    records = [
        {"pmid": "1", "doi": "10.a/1"},
        {"pmid": "2", "doi": "10.a/2"},
        {"pmid": "3", "doi": "10.a/3"},
    ]
    f = _write_json(tmp_path, query,
                    records=records,
                    dois=["10.a/1", "10.a/2", "10.a/3"],
                    pmids=["1", "2", "3"])
    p = EmbaseLocalProvider(str(f))

    # Narrow date bounds that would exclude all articles if filtering were applied
    dois_all, pmids_all, _ = p.search(query, "2099/01/01", "2099/12/31")

    assert len(dois_all) == 3, (
        "Date bounds must NOT filter Embase results — they are pre-filtered at export time."
        f" Got {len(dois_all)} dois instead of 3."
    )
    print("PASS test_date_bounds_do_not_filter")


# ── Test 10 ── Integration with _execute_query_bundle ─────────────────────

def test_execute_query_bundle_integrates_embase(tmp_path):
    """
    EmbaseLocalProvider plugs into _execute_query_bundle:
    - Embase PMIDs enter combined_pmids (because id_type='pmid')
    - Embase DOIs enter combined_dois
    - linked_records are present in provider_details['embase']
    - Embase _pmid_to_doi_cache propagates to combined_pmid_to_doi
    - A PubMed-only PMID and an Embase-only PMID both appear in combined_pmids
    """
    query = "bundle integration test"
    # Embase has article A (pmid=A, doi=10.A) and article B (pmid=B, no doi)
    records = [
        {"pmid": "emb_A", "doi": "10.embase/a"},
        {"pmid": "emb_B", "doi": None},
    ]
    f = _write_json(tmp_path, query,
                    records=records,
                    dois=["10.embase/a"],
                    pmids=["emb_A", "emb_B"])
    embase_provider = EmbaseLocalProvider(str(f))

    class FakePubMed:
        name = "pubmed"
        id_type = "pmid"

        def search(self, q, mn, mx, retmax=100000):
            self._pmid_to_doi_cache = {"pub_A": "10.pubmed/a"}
            return {"10.pubmed/a"}, {"pub_A", "pub_only"}, 2

    pm = FakePubMed()
    qmap = {
        "pubmed": query,
        "embase": query,
    }
    combined_pmids, combined_dois, total, provider_details = _execute_query_bundle(
        [pm, embase_provider],
        qmap,
        "2010/01/01",
        "2024/12/31",
    )

    # --- combined_pmids must include both PubMed and Embase PMIDs -----------
    assert "pub_A" in combined_pmids, f"PubMed PMID missing: {combined_pmids}"
    assert "pub_only" in combined_pmids, f"PubMed-only PMID missing: {combined_pmids}"
    assert "emb_A" in combined_pmids, f"Embase PMID A missing: {combined_pmids}"
    assert "emb_B" in combined_pmids, f"Embase PMID-only B missing: {combined_pmids}"

    # --- combined_dois must include both PubMed and Embase DOIs --------------
    assert "10.pubmed/a" in combined_dois, f"PubMed DOI missing: {combined_dois}"
    assert "10.embase/a" in combined_dois, f"Embase DOI missing: {combined_dois}"

    # --- provider_details['embase'] must exist and contain linked_records ----
    assert "embase" in provider_details, f"'embase' key missing from provider_details: {list(provider_details.keys())}"
    embase_pd = provider_details["embase"]
    assert "linked_records" in embase_pd, "'linked_records' missing from embase provider_details"
    lr = embase_pd["linked_records"]
    assert isinstance(lr, list)

    by_pmid = {r["pmid"]: r["doi"] for r in lr if r.get("pmid")}
    assert by_pmid.get("emb_A") == "10.embase/a", f"emb_A pairing wrong: {by_pmid}"
    assert by_pmid.get("emb_B") is None, f"emb_B should be pmid-only: {by_pmid}"

    # --- id_type must be 'pmid' -----------------------------------------------
    assert embase_pd.get("id_type") == "pmid", f"Expected id_type='pmid': {embase_pd.get('id_type')}"

    print("PASS test_execute_query_bundle_integrates_embase")
    print(f"  combined_pmids: {combined_pmids}")
    print(f"  combined_dois: {combined_dois}")
    print(f"  linked_records: {lr}")


# ── Test 10b ── total_results counts Embase unique articles ───────────────

def test_total_results_includes_embase(tmp_path):
    """
    After W2.4, total_results = unique deduplicated articles.
    Embase-unique articles (different doi from PubMed) must contribute to total.
    
    PubMed:  1 article  (pmid=p1, doi=10.pub/1)
    Embase:  2 articles (pmid=e1, doi=10.emb/1) and (pmid=e2, doi=10.emb/2)
    Overlap: zero (different DOIs)
    Expected total: 3 unique articles
    """
    query = "total count test"
    records = [
        {"pmid": "e1", "doi": "10.emb/1"},
        {"pmid": "e2", "doi": "10.emb/2"},
    ]
    f = _write_json(tmp_path, query,
                    records=records,
                    dois=["10.emb/1", "10.emb/2"],
                    pmids=["e1", "e2"])
    embase_prov = EmbaseLocalProvider(str(f))

    class FakePubMed:
        name = "pubmed"
        id_type = "pmid"

        def search(self, q, mn, mx, retmax=100000):
            self._pmid_to_doi_cache = {"p1": "10.pub/1"}
            return {"10.pub/1"}, {"p1"}, 1

    _, _, total, _ = _execute_query_bundle(
        [FakePubMed(), embase_prov],
        {"pubmed": query, "embase": query},
        "2010/01/01",
        "2024/12/31",
    )
    # 3 unique DOIs → total_results = 3 (all have DOIs, _pmid_only_count = 0)
    assert total == 3, f"Expected total=3, got {total}"
    print("PASS test_total_results_includes_embase:", total)


# ── Test 11 ── Real file smoke test ──────────────────────────────────────

REAL_FILE = Path(__file__).parent.parent / "studies" / "ai_2022" / "embase_query1.json"
REAL_QUERY_FILE = Path(__file__).parent.parent / "studies" / "ai_2022" / "queries_embase.txt"


def _read_embase_queries(path: Path):
    """Read queries_embase.txt using the same parser as the main script."""
    queries = []
    buf = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                if buf:
                    queries.append(" ".join(buf))
                    buf = []
            elif not line.startswith("#"):
                buf.append(line)
    if buf:
        queries.append(" ".join(buf))
    return queries


@pytest.mark.skipif(
    not REAL_FILE.exists() or not REAL_QUERY_FILE.exists(),
    reason="Real Embase fixture not available",
)
def test_real_file_smoke():
    """
    Smoke test against the actual studies/ai_2022/embase_query1.json.
    Verifies:
    - search() returns non-empty results
    - Hash matching works against queries_embase.txt query 1
    - _pmid_to_doi_cache is populated from records
    - All returned DOIs are lowercase
    """
    queries = _read_embase_queries(REAL_QUERY_FILE)
    assert len(queries) >= 1, "Expected at least one query"

    p = EmbaseLocalProvider(str(REAL_FILE))
    dois_ret, pmids_ret, total = p.search(queries[0], "2000/01/01", "2024/12/31")

    assert len(dois_ret) > 0, "Expected non-empty DOIs from real Embase file"
    assert len(pmids_ret) > 0, "Expected non-empty PMIDs from real Embase file"
    assert total > 0, f"Expected total > 0: {total}"

    # All DOIs must be lowercase
    for doi in dois_ret:
        assert doi == doi.lower(), f"DOI not lowercased: {doi!r}"

    cache = p._pmid_to_doi_cache
    assert isinstance(cache, dict)
    assert len(cache) > 0, "Expected non-empty _pmid_to_doi_cache from real Embase file"

    # Every cached DOI must be present in dois_ret
    cached_dois = set(cache.values())
    missing = cached_dois - dois_ret
    assert not missing, (
        f"Cache contains DOIs not in return set: {list(missing)[:5]}"
    )

    print(
        f"PASS test_real_file_smoke: "
        f"dois={len(dois_ret)}, pmids={len(pmids_ret)}, "
        f"total={total}, cache_entries={len(cache)}"
    )


# ── run as script ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import tempfile
    import pathlib

    _tmp = pathlib.Path(tempfile.mkdtemp())

    # Simple manual test runner — pytest is preferred, but this supports direct run
    class _Capsys:
        """Minimal stand-in for pytest capsys when running directly."""
        def readouterr(self):
            class R:
                out = ""
                err = ""
            return R()

    test_search_returns_correct_types(_tmp)
    test_cache_built_from_records(_tmp)
    test_pmid_only_absent_from_cache(_tmp)
    test_dois_normalised_to_lowercase(_tmp)
    test_legacy_format_flat_lists(_tmp)
    test_single_entry_fallback_on_hash_miss(_tmp)
    test_hash_miss_multi_entry_returns_empty(_tmp, _Capsys())
    test_missing_file_returns_empty(_Capsys())
    test_date_bounds_do_not_filter(_tmp)
    test_execute_query_bundle_integrates_embase(_tmp)
    test_total_results_includes_embase(_tmp)

    if REAL_FILE.exists() and REAL_QUERY_FILE.exists():
        test_real_file_smoke()
    else:
        print("SKIP test_real_file_smoke (real fixture not available)")

    print()
    print("All W3.1 tests passed.")
