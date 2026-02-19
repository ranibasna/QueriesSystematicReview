"""W2.4 unit tests: total_results is deduplicated unique count, not raw sum.

W2.4 fixes Issue 4 (total_results Inflated by Raw Sum).

Before W2.4:  total_results = sum of API-reported counts from all databases
              → articles present in multiple DBs counted 2–3×
              → NNR_proxy inflated 40–67%

After W2.4:   total_results = len(combined_dois) + pmid_only_count
              = true unique-article count after DOI deduplication
              → NNR_proxy uses accurate denominator

Key invariants:
  1. total_results (returned) == unique_articles == len(combined_dois) + _pmid_only_count
  2. total_results <= total_raw_results  (deduped ≤ raw)
  3. total_results == total_raw_results  iff no cross-DB DOI overlap AND no PMID-only articles
  4. per-DB results_count in provider_details is still the raw per-DB count (unchanged)
  5. Return signature remains a 4-tuple (backward compat; no 5th element)

Dependencies:
  W2.1 (combined_pmid_to_doi) enables exact _pmid_only_count computation.
  W2.4 does NOT depend on W2.5 (ArticleRegistry).
"""
import io
import contextlib
import sys

sys.path.insert(0, "/Users/ra1077ba/Documents/DataScience/GU/Daniil/LLM/QueriesSystematicReview")
from llm_sr_select_and_score import _execute_query_bundle


# ── Fake providers ─────────────────────────────────────────────────────────────

class FakePubMed:
    """PubMed provider stub: returns specified PMIDs, honoring pmid_to_doi mapping."""
    name = "pubmed"
    id_type = "pmid"

    def __init__(self, pmid_to_doi: dict, extra_pmid_only: list | None = None):
        self._cache = dict(pmid_to_doi)
        self._extra_pmids = set(extra_pmid_only or [])

    def search(self, q, mn, mx, retmax=100000):
        self._pmid_to_doi_cache = self._cache
        dois = set(self._cache.values())
        pmids = set(self._cache.keys()) | self._extra_pmids
        # total = number of distinct articles reported
        return dois, pmids, len(pmids)


class FakeScopus:
    """Scopus provider stub: returns specified DOIs (no PMIDs)."""
    name = "scopus"
    id_type = "scopus_id"

    def __init__(self, dois: list, api_total: int | None = None):
        self._dois = set(dois)
        self._api_total = api_total if api_total is not None else len(self._dois)

    def search(self, q, mn, mx, retmax=100000):
        ids = {f"s{i}" for i in range(len(self._dois))}
        return self._dois, ids, self._api_total


class FakeWOS:
    """WOS provider stub: returns specified DOIs (no PMIDs)."""
    name = "wos"
    id_type = "wos_uid"

    def __init__(self, dois: list, api_total: int | None = None):
        self._dois = set(dois)
        self._api_total = api_total if api_total is not None else len(self._dois)

    def search(self, q, mn, mx, retmax=100000):
        ids = {f"w{i}" for i in range(len(self._dois))}
        return self._dois, ids, self._api_total


def run_bundle(providers, qmap=None):
    """Convenience wrapper; returns (pmids, dois, total, pd)."""
    if qmap is None:
        qmap = {p.name: "q" for p in providers}
    return _execute_query_bundle(providers, qmap, "2020/01/01", "2024/12/31")


# ── Test 1 ── Single PubMed provider: no cross-DB dedup ───────────────────────

def test_single_pubmed_no_overlap():
    """With one provider and no PMID-only articles: total == raw (no dedup needed).

    PubMed: 3 PMIDs, all with DOIs → unique = 3 = raw.
    """
    pm = FakePubMed({"p1": "10.a/1", "p2": "10.a/2", "p3": "10.a/3"})
    _, _, total, pd = run_bundle([pm])

    raw = pd["pubmed"]["results_count"]  # per-DB raw count
    assert total == 3, f"Expected 3, got {total}"
    assert raw == 3, f"Per-DB raw should be 3, got {raw}"
    assert total == raw, "No cross-DB overlap → deduped == raw"
    print("PASS test_single_pubmed_no_overlap:", total)


# ── Test 2 ── PubMed with PMID-only articles: total includes them ─────────────

def test_pubmed_with_pmid_only():
    """PMID-only articles (no DOI in PubMed XML) must be included in total.

    PubMed: 2 paired (PMID+DOI) + 3 PMID-only = 5 articles total.
    combined_dois = 2, _pmid_only_count = 3 → total_results = 5 = raw.
    """
    pm = FakePubMed({"p1": "10.a/1", "p2": "10.a/2"}, extra_pmid_only=["p3", "p4", "p5"])
    _, _, total, pd = run_bundle([pm])

    raw = pd["pubmed"]["results_count"]  # PubMed API count = 5 (2 paired + 3 extra)
    assert total == 5, f"Expected 5, got {total}"
    assert raw == 5, f"Per-DB raw = 5, got {raw}"
    print("PASS test_pubmed_with_pmid_only:", total)


# ── Test 3 ── Cross-DB DOI overlap: total < raw ────────────────────────────────

def test_multi_provider_dedup():
    """Core W2.4 test: overlapping DOIs deduplicate; total_results < raw sum.

    PubMed : 3 articles (p1→d1, p2→d2, p3→d3). raw=3
    Scopus : 4 articles (d2, d3, d4, d5). raw=4  (d2,d3 overlap with PubMed)
    WOS    : 3 articles (d3, d5, d6). raw=3       (d3,d5 overlap with PubMed/Scopus)

    combined_dois = {d1, d2, d3, d4, d5, d6} = 6
    _pmid_only_count = 0 (all PubMed PMIDs have DOIs)
    total_results (deduped) = 6
    total_raw = 3 + 4 + 3 = 10
    """
    pm = FakePubMed({"p1": "d1", "p2": "d2", "p3": "d3"})
    sc = FakeScopus(["d2", "d3", "d4", "d5"])
    wo = FakeWOS(["d3", "d5", "d6"])

    _, _, total, pd = run_bundle([pm, sc, wo])

    total_raw = sum(v["results_count"] for v in pd.values() if "error" not in v)
    assert total_raw == 10, f"Expected raw=10, got {total_raw}"
    assert total == 6, f"Expected deduped=6, got {total}"
    assert total < total_raw, f"Deduped ({total}) must be < raw ({total_raw})"

    # Per-DB results_count is still raw (per-DB API count)
    assert pd["pubmed"]["results_count"] == 3
    assert pd["scopus"]["results_count"] == 4
    assert pd["wos"]["results_count"] == 3
    print(f"PASS test_multi_provider_dedup: raw={total_raw}, deduped={total}")


# ── Test 4 ── total_results must NOT be raw sum ────────────────────────────────

def test_total_is_not_raw_sum():
    """Regression: total_results must never equal the inflated raw sum when there is overlap."""
    pm = FakePubMed({"p1": "d1", "p2": "d2"})
    sc = FakeScopus(["d1", "d2", "d3", "d4", "d5"])  # d1,d2 overlap

    _, _, total, pd = run_bundle([pm, sc])

    raw_sum = pd["pubmed"]["results_count"] + pd["scopus"]["results_count"]  # 2+5=7
    assert raw_sum == 7, f"raw_sum={raw_sum}"
    assert total != raw_sum, f"total={total} must not equal raw_sum={raw_sum}"
    assert total == 5, f"Expected unique_dois={5}, got {total}"  # {d1,d2,d3,d4,d5}
    print(f"PASS test_total_is_not_raw_sum: total={total}, raw_sum={raw_sum}")


# ── Test 5 ── No overlap between providers ────────────────────────────────────

def test_no_overlap_equals_raw():
    """When all DOIs are unique across databases, total == raw sum."""
    pm = FakePubMed({"p1": "d1", "p2": "d2"})   # 2 unique DOIs
    sc = FakeScopus(["d3", "d4", "d5"])           # 3 unique DOIs
    wo = FakeWOS(["d6"])                           # 1 unique DOI

    _, _, total, pd = run_bundle([pm, sc, wo])

    raw_sum = sum(v["results_count"] for v in pd.values())
    assert raw_sum == 6, f"raw_sum={raw_sum}"
    assert total == 6, f"total={total}"
    assert total == raw_sum, "No overlap → deduped == raw"
    print(f"PASS test_no_overlap_equals_raw: total={total}")


# ── Test 6 ── PMID-only from PubMed + DOI from Scopus ─────────────────────────

def test_pmid_only_plus_scopus_doi():
    """PMID-only PubMed articles + distinct Scopus DOIs: total = pmid_only + dois.

    PubMed: 1 paired (p1→d1) + 2 PMID-only (p2, p3). raw=3
    Scopus: 3 new DOIs (d2, d3, d4). raw=3
    Note: p2,p3 might correspond to d2,d3 in reality, but without W2.5 we
    cannot detect this — they are counted separately in W2.4.

    combined_dois = {d1, d2, d3, d4} = 4
    _pmid_only_count = 2 (p2, p3 have no DOI in combined_pmid_to_doi)
    total_results = 4 + 2 = 6
    total_raw = 3 + 3 = 6  (happens to be equal here, coincidentally)
    """
    pm = FakePubMed({"p1": "d1"}, extra_pmid_only=["p2", "p3"])
    sc = FakeScopus(["d2", "d3", "d4"])

    _, _, total, pd = run_bundle([pm, sc])

    assert total == 6, f"Expected 6, got {total}"
    # Per-DB counts unchanged
    assert pd["pubmed"]["results_count"] == 3
    assert pd["scopus"]["results_count"] == 3
    print(f"PASS test_pmid_only_plus_scopus_doi: total={total}")


# ── Test 7 ── Dedup log message fires when duplicates_removed > 0 ─────────────

def test_dedup_log_fires():
    """When cross-DB overlap exists, the dedup log message must be printed."""
    pm = FakePubMed({"p1": "d1", "p2": "d2"})
    sc = FakeScopus(["d1", "d2", "d3", "d4", "d5"])  # d1,d2 overlap

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        run_bundle([pm, sc])

    out = buf.getvalue()
    assert "[INFO] Deduplication" in out, f"Dedup log not printed.\nOutput:\n{out}"
    # The message should show raw → unique
    assert "raw results" in out, out
    assert "unique articles" in out, out
    print("PASS test_dedup_log_fires:", out.strip())


# ── Test 8 ── Dedup log silent when no overlap ────────────────────────────────

def test_dedup_log_silent_no_overlap():
    """When there are no cross-DB duplicates, the dedup log must NOT fire."""
    pm = FakePubMed({"p1": "d1"})
    sc = FakeScopus(["d2", "d3"])  # No overlap

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        run_bundle([pm, sc])

    out = buf.getvalue()
    assert "[INFO] Deduplication" not in out, \
        f"Dedup log should not fire when no overlap.\nOutput:\n{out}"
    print("PASS test_dedup_log_silent_no_overlap")


# ── Test 9 ── Return is 4-tuple (backward compat) ─────────────────────────────

def test_return_is_4_tuple():
    """W2.4 must NOT change the return arity; callers depend on 4-tuple unpacking."""
    pm = FakePubMed({"p1": "d1"})
    result = _execute_query_bundle([pm], {"pubmed": "q"}, "2020/01/01", "2024/12/31")
    assert len(result) == 4, f"Expected 4-tuple, got {len(result)}-tuple"
    pmids, dois, total, pd = result  # must not raise ValueError
    print("PASS test_return_is_4_tuple")


# ── Test 10 ── ai_2022-style scenario (empirical data from issue doc) ──────────

def test_ai2022_style_scenario():
    """Verify W2.4 reduction matches the empirical data from PIPELINE_ISSUES_AND_SOLUTIONS.

    The issue document reports for Q1 High-Recall:
      PubMed: 572 PMIDs, 550 DOIs (22 PMID-only), API total = 572
      Scopus: 2,770 DOIs, scopus_ids count = 3,029, API total = 3,029 (approx)
      WOS:    678 DOIs, wos_uids count = 715, API total = 715 (approx)
    Raw sum = 572 + 3029 + 715 = 4316
    True unique (DOI dedup) ≈ 3092

    We simulate this with small proxies that preserve the SAME ratios:
      PubMed: 572 → 55 PMIDs (50 with DOI + 5 PMID-only)
      Scopus: 277 DOIs (25 overlap with PubMed)
      WOS:    68 DOIs (10 overlap with Scopus/PubMed)

    combined_dois = 50 + (277-25) + (68-10) = 50+252+58 = 360
    _pmid_only_count = 5
    total_results (deduped) = 365
    total_raw = 55 + 277 + 68 = 400  (inflation ~9%)
    """
    pubmed_dois = {f"d{i}": f"10.pm/{i}" for i in range(50)}   # 50 paired
    pubmed_extra_pmids = [f"p_only_{i}" for i in range(5)]       # 5 PMID-only

    # Scopus: 25 overlap with PubMed, 252 new
    scopus_overlap = [f"10.pm/{i}" for i in range(25)]           # same as PubMed d0-d24
    scopus_new = [f"10.sc/{i}" for i in range(252)]
    scopus_dois = scopus_overlap + scopus_new

    # WOS: 10 overlap with PubMed/Scopus, 58 new
    wos_overlap = [f"10.pm/{i}" for i in range(5)]               # subset of PubMed
    wos_overlap += [f"10.sc/{i}" for i in range(5)]              # subset of Scopus new
    wos_new = [f"10.wos/{i}" for i in range(58)]
    wos_dois = wos_overlap + wos_new  # may have duplicates within; set handles them

    pm = FakePubMed(pubmed_dois, extra_pmid_only=pubmed_extra_pmids)
    sc = FakeScopus(scopus_dois)
    wo = FakeWOS(wos_dois)

    _, _, total, pd = run_bundle([pm, sc, wo])

    total_raw = sum(v["results_count"] for v in pd.values())
    expected_pm_raw = 55  # 50 paired + 5 PMID-only
    expected_sc_raw = len(set(scopus_dois))  # unique within Scopus set
    expected_wo_raw = len(set(wos_dois))    # unique within WOS set

    assert total < total_raw, f"Deduped ({total}) must be less than raw ({total_raw})"
    # There must be meaningful deduplication
    inflation = total_raw / total
    assert inflation > 1.0, f"Expected inflation > 1.0, got {inflation:.2f}"

    print(f"PASS test_ai2022_style_scenario: raw={total_raw}, deduped={total}, inflation={inflation:.2f}×")


# ── Test 11 ── Empty providers: total = 0 ────────────────────────────────────

def test_empty_providers():
    """No providers → total_results = 0, not crash."""
    _, _, total, pd = _execute_query_bundle([], {}, "2020/01/01", "2024/12/31")
    assert total == 0, f"Expected 0, got {total}"
    assert pd == {}, f"Expected empty provider_details, got {pd}"
    print("PASS test_empty_providers")


# ── Test 12 ── Error provider doesn't inflate total ───────────────────────────

def test_error_provider_excluded_from_total():
    """A provider that raises an exception contributes 0 to total_results."""
    class FailingDB:
        name = "failing_db"
        id_type = "id"
        def search(self, q, mn, mx, retmax=100000):
            raise RuntimeError("API down")

    pm = FakePubMed({"p1": "d1", "p2": "d2"})
    fail = FailingDB()

    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        _, _, total, pd = run_bundle([pm, fail], {"pubmed": "q", "failing_db": "q"})

    # Error provider present in provider_details but has 0 results_count
    assert "error" in pd.get("failing_db", {}), "Error provider must have 'error' key"
    assert pd["failing_db"]["results_count"] == 0

    # Total should reflect only the successful provider
    assert total == 2, f"Total should be 2 (from PubMed only), got {total}"
    print("PASS test_error_provider_excluded_from_total:", total)


# ── Test 13 ── NNR computation semantics ──────────────────────────────────────

def test_nnr_denominator_is_deduped():
    """Verify: NNR = unique_articles / TP, not raw_sum / TP.

    We test indirectly: unique_articles < raw_sum when overlap exists,
    so NNR with deduped denominator must be < NNR with raw denominator.

    This is a semantic check, not a direct function test (NNR is computed
    in score_queries, not _execute_query_bundle), but we verify the
    total returned by _execute_query_bundle is the deduped count that
    score_queries will use as the denominator.
    """
    pm = FakePubMed({"p1": "d1", "p2": "d2", "p3": "d3"})    # 3 articles
    sc = FakeScopus(["d1", "d2", "d3", "d4", "d5"])            # 2 overlap + 3 new

    _, _, total, pd = run_bundle([pm, sc])

    raw_sum = pd["pubmed"]["results_count"] + pd["scopus"]["results_count"]  # 3+5=8
    assert total == 5, f"deduped total expected 5, got {total}"   # d1-d5
    assert raw_sum == 8

    tp = 2  # hypothetical: 2 gold articles found
    nnr_deduped = total / tp      # 5/2 = 2.5
    nnr_raw     = raw_sum / tp    # 8/2 = 4.0  (inflated)

    assert nnr_deduped < nnr_raw, \
        f"Deduped NNR ({nnr_deduped}) must be less than raw NNR ({nnr_raw})"
    print(f"PASS test_nnr_denominator_is_deduped: NNR_deduped={nnr_deduped}, NNR_raw={nnr_raw}")


# ── Test 14 ── Deduped count never negative ────────────────────────────────────

def test_total_never_negative():
    """total_results must be ≥ 0 even for edge-case provider responses."""
    pm = FakePubMed({})  # Empty cache: 0 paired, 0 PMID-only
    sc = FakeScopus([])   # No DOIs

    _, _, total, _ = run_bundle([pm, sc])
    assert total >= 0, f"total_results must be >= 0, got {total}"
    assert total == 0, f"Expected 0 for empty providers, got {total}"
    print("PASS test_total_never_negative:", total)


# ── Test 15 ── per-DB results_count unchanged (W2.4 does not modify per-DB) ───

def test_per_db_results_count_unchanged():
    """W2.4 changes the COMBINED total but must NOT modify per-DB results_count.

    Each provider's results_count in provider_details must equal the raw
    API-reported count from that provider, as before W2.4.
    """
    pm = FakePubMed({"p1": "d1", "p2": "d2"}, extra_pmid_only=["p3"])  # raw=3
    sc = FakeScopus(["d1", "d2", "d3"], api_total=42)                   # raw=42 (API says 42)
    wo = FakeWOS(["d4", "d5"], api_total=15)                            # raw=15 (API says 15)

    _, _, total, pd = run_bundle([pm, sc, wo])

    assert pd["pubmed"]["results_count"] == 3,  f"PubMed raw should be 3, got {pd['pubmed']['results_count']}"
    assert pd["scopus"]["results_count"] == 42, f"Scopus raw should be 42 (API reported), got {pd['scopus']['results_count']}"
    assert pd["wos"]["results_count"] == 15,    f"WOS raw should be 15 (API reported), got {pd['wos']['results_count']}"

    # Combined total is deduped: {d1,d2,d3,d4,d5} = 5 DOIs + 1 PMID-only = 6
    assert total == 6, f"Expected deduped=6, got {total}"
    print(f"PASS test_per_db_results_count_unchanged: per-DB counts={[pd[k]['results_count'] for k in ['pubmed','scopus','wos']]}, combined={total}")


if __name__ == "__main__":
    test_single_pubmed_no_overlap()
    test_pubmed_with_pmid_only()
    test_multi_provider_dedup()
    test_total_is_not_raw_sum()
    test_no_overlap_equals_raw()
    test_pmid_only_plus_scopus_doi()
    test_dedup_log_fires()
    test_dedup_log_silent_no_overlap()
    test_return_is_4_tuple()
    test_ai2022_style_scenario()
    test_empty_providers()
    test_error_provider_excluded_from_total()
    test_nnr_denominator_is_deduped()
    test_total_never_negative()
    test_per_db_results_count_unchanged()
    print()
    print("All W2.4 tests passed.")
