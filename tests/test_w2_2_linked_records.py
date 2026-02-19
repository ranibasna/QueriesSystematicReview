"""W2.2 unit tests: linked_records in provider_details.

W2.2 adds a `linked_records` key to each provider entry in provider_details
returned by _execute_query_bundle.  The format is:

  PubMed  (id_type='pmid'):   [{'pmid': str,  'doi': str|None}, ...]
    - Paired: _pmid_to_doi_cache entries — correctly linked PMID+DOI articles
    - PMID-only: PMIDs absent from cache — articles whose DOI was not in PubMed XML
  Scopus/WOS (other id_types): [{'pmid': None, 'doi': str}, ...]
    - DOI-only records

Old keys (retrieved_ids, retrieved_dois, id_type …) are untouched — backward compat.
Error providers do NOT get a linked_records key (they are skipped before W2.2 runs).
"""
import json
import sys

sys.path.insert(0, "/Users/ra1077ba/Documents/DataScience/GU/Daniil/LLM/QueriesSystematicReview")
from llm_sr_select_and_score import _execute_query_bundle


# ── Helpers ───────────────────────────────────────────────────────────────────

class FakePubMed:
    name = "pubmed"
    id_type = "pmid"

    def __init__(self, pmid_to_doi: dict, extra_pmid_only: list | None = None):
        self._cache = dict(pmid_to_doi)
        self._extra = set(extra_pmid_only or [])

    def search(self, q, mn, mx, retmax=100000):
        self._pmid_to_doi_cache = self._cache
        dois = set(self._cache.values())
        pmids = set(self._cache.keys()) | self._extra
        return dois, pmids, len(pmids)


class FakeScopus:
    name = "scopus"
    id_type = "scopus_id"

    def __init__(self, dois: list, native_ids: list | None = None):
        self._dois = set(dois)
        self._ids = set(native_ids or [f"s{i}" for i in range(len(dois))])

    def search(self, q, mn, mx, retmax=100000):
        return self._dois, self._ids, len(self._dois)


class FakeWOS:
    name = "wos"
    id_type = "wos_uid"

    def __init__(self, dois: list):
        self._dois = set(dois)

    def search(self, q, mn, mx, retmax=100000):
        return self._dois, {f"w{i}" for i in range(len(self._dois))}, len(self._dois)


def run_bundle(providers, qmap):
    _, _, _, pd = _execute_query_bundle(providers, qmap, "2020/01/01", "2024/12/31")
    return pd


# ── Test 1 ── PubMed: paired and PMID-only records both appear ────────────

def test_pubmed_mixed_linked_records():
    """PMIDs 111 and 222 have DOIs; 333 is PMID-only (no DOI in PubMed XML)."""
    pm = FakePubMed({"111": "10.a/a", "222": "10.b/b"}, extra_pmid_only=["333"])
    pd = run_bundle([pm], {"pubmed": "q"})

    lr = pd["pubmed"]["linked_records"]
    assert isinstance(lr, list)

    by_pmid = {r["pmid"]: r["doi"] for r in lr}
    assert by_pmid["111"] == "10.a/a", f"Expected '10.a/a', got {by_pmid.get('111')}"
    assert by_pmid["222"] == "10.b/b", f"Expected '10.b/b', got {by_pmid.get('222')}"
    assert by_pmid["333"] is None, f"Expected None, got {by_pmid.get('333')}"
    assert len(lr) == 3, f"Expected 3 records, got {len(lr)}: {lr}"
    print("PASS test_pubmed_mixed_linked_records:", lr)


# ── Test 2 ── PubMed: all PMIDs have DOIs — no PMID-only records ──────────

def test_pubmed_all_paired():
    """Every returned PMID has a DOI in the cache → no doi=None entries."""
    pm = FakePubMed({"A": "10.x/1", "B": "10.x/2", "C": "10.x/3"})
    pd = run_bundle([pm], {"pubmed": "q"})

    lr = pd["pubmed"]["linked_records"]
    assert all(r["doi"] is not None for r in lr), f"Unexpected doi=None: {lr}"
    assert len(lr) == 3, lr
    print("PASS test_pubmed_all_paired:", lr)


# ── Test 3 ── PubMed: all PMIDs lack DOI — all records are PMID-only ────

def test_pubmed_all_pmid_only():
    """Cache is empty (no DOIs at all); all articles are PMID-only."""
    pm = FakePubMed({}, extra_pmid_only=["P1", "P2"])
    pd = run_bundle([pm], {"pubmed": "q"})

    lr = pd["pubmed"]["linked_records"]
    assert len(lr) == 2, lr
    assert all(r["pmid"] is not None for r in lr), lr
    assert all(r["doi"] is None for r in lr), lr
    print("PASS test_pubmed_all_pmid_only:", lr)


# ── Test 4 ── Scopus: DOI-only records (no PMIDs) ─────────────────────────

def test_scopus_linked_records():
    sc = FakeScopus(["10.s/1", "10.s/2", "10.s/3"], native_ids=["s001", "s002", "s003"])
    pd = run_bundle([sc], {"scopus": "q"})

    lr = pd["scopus"]["linked_records"]
    assert isinstance(lr, list)
    assert all(r["pmid"] is None for r in lr), f"Scopus must have pmid=None: {lr}"
    assert all(r["doi"] is not None for r in lr), f"Scopus must have doi: {lr}"
    assert len(lr) == 3, f"Expected 3, got {len(lr)}: {lr}"
    print("PASS test_scopus_linked_records:", lr)


# ── Test 5 ── WOS: DOI-only records (same as Scopus) ─────────────────────

def test_wos_linked_records():
    wos = FakeWOS(["10.w/1", "10.w/2"])
    pd = run_bundle([wos], {"wos": "q"})

    lr = pd["wos"]["linked_records"]
    assert all(r["pmid"] is None for r in lr), lr
    assert all(r["doi"] is not None for r in lr), lr
    assert len(lr) == 2, lr
    print("PASS test_wos_linked_records:", lr)


# ── Test 6 ── Backward compat: old keys unchanged alongside linked_records ──

def test_backward_compat_keys_present():
    pm = FakePubMed({"1": "10.a/1"}, extra_pmid_only=["2"])
    pd = run_bundle([pm], {"pubmed": "q"})

    pbd = pd["pubmed"]
    for key in ("query", "results_count", "retrieved_ids", "retrieved_dois", "id_type"):
        assert key in pbd, f"Old key '{key}' missing: {pbd.keys()}"
    assert "linked_records" in pbd, f"New key 'linked_records' missing: {pbd.keys()}"
    print("PASS test_backward_compat_keys_present:", sorted(pbd.keys()))


# ── Test 7 ── Length consistency: linked_records covers all retrieved articles ─

def test_linked_records_length_equals_retrieved_ids():
    """For PubMed: len(linked_records) == len(retrieved_ids) exactly."""
    pm = FakePubMed({"111": "10.a/a", "222": "10.b/b"}, extra_pmid_only=["333", "444"])
    pd = run_bundle([pm], {"pubmed": "q"})

    pbd = pd["pubmed"]
    assert len(pbd["linked_records"]) == len(pbd["retrieved_ids"]), (
        f"linked_records has {len(pbd['linked_records'])} != "
        f"retrieved_ids has {len(pbd['retrieved_ids'])}"
    )
    print("PASS test_linked_records_length_equals_retrieved_ids")


# ── Test 8 ── Multi-provider: each provider has independent linked_records ──

def test_multi_provider_independent_linked_records():
    pm = FakePubMed({"P1": "10.p/1"}, extra_pmid_only=["P2"])
    sc = FakeScopus(["10.s/1", "10.s/2"])
    pd = run_bundle([pm, sc], {"pubmed": "q", "scopus": "q"})

    # PubMed: 1 paired + 1 PMID-only
    pm_lr = pd["pubmed"]["linked_records"]
    assert len(pm_lr) == 2, pm_lr

    # Scopus: 2 DOI-only
    sc_lr = pd["scopus"]["linked_records"]
    assert len(sc_lr) == 2, sc_lr
    assert all(r["pmid"] is None for r in sc_lr), sc_lr
    print("PASS test_multi_provider_independent_linked_records")


# ── Test 9 ── Error provider: no linked_records key (graceful absence) ──────

def test_error_provider_no_linked_records():
    class FailProvider:
        name = "pubmed"
        id_type = "pmid"

        def search(self, q, mn, mx, retmax=100000):
            raise RuntimeError("simulated API error")

    pd = run_bundle([FailProvider()], {"pubmed": "q"})
    pbd = pd.get("pubmed", {})
    assert "error" in pbd, f"Expected 'error' key, got: {pbd.keys()}"
    assert "linked_records" not in pbd, (
        f"Error provider must not have 'linked_records': {pbd.keys()}"
    )
    print("PASS test_error_provider_no_linked_records")


# ── Test 10 ── JSON roundtrip: linked_records survives json.dumps/loads ──────

def test_linked_records_json_roundtrip():
    """None dois survive JSON serialization as JSON null → Python None."""
    pm = FakePubMed({"30": "10.a/b"}, extra_pmid_only=["31"])
    sc = FakeScopus(["10.s/1"])
    pd = run_bundle([pm, sc], {"pubmed": "q", "scopus": "q"})

    serialized = json.dumps(pd)
    restored = json.loads(serialized)

    pm_lr = restored["pubmed"]["linked_records"]
    assert len(pm_lr) == 2, pm_lr
    pmid_only = [r for r in pm_lr if r["doi"] is None]
    assert len(pmid_only) == 1, f"Expected 1 PMID-only record, got: {pm_lr}"
    paired = [r for r in pm_lr if r["doi"] is not None]
    assert len(paired) == 1, f"Expected 1 paired record, got: {pm_lr}"

    sc_lr = restored["scopus"]["linked_records"]
    assert len(sc_lr) == 1
    assert sc_lr[0]["pmid"] is None
    print("PASS test_linked_records_json_roundtrip")


# ── Test 11 ── Correctness: adversarial pairing (validates W2.2 role for W2.5) ─

def test_adversarial_pairing_preserved():
    """Low PMID paired with LATE DOI (alphabetically last).
    Old index-based pairing would swap them. W2.2 preserves the correct pair.
    """
    pm = FakePubMed({
        "0000001": "10.zzz/late",   # low PMID → late DOI
        "9999999": "10.aaa/early",  # high PMID → early DOI
    })
    pd = run_bundle([pm], {"pubmed": "q"})

    lr = pd["pubmed"]["linked_records"]
    by_pmid = {r["pmid"]: r["doi"] for r in lr}

    assert by_pmid["0000001"] == "10.zzz/late",  f"Got: {by_pmid['0000001']}"
    assert by_pmid["9999999"] == "10.aaa/early", f"Got: {by_pmid['9999999']}"

    # Confirm old index-based approach (sorted PMID[i] ↔ sorted DOI[i]) gives WRONG answer
    idx_wrong = dict(zip(sorted(by_pmid.keys()), sorted(by_pmid.values())))
    assert idx_wrong["0000001"] == "10.aaa/early", "sanity: index-based gets early"
    assert idx_wrong["9999999"] == "10.zzz/late",  "sanity: index-based gets late"

    print("PASS test_adversarial_pairing_preserved")
    print(f"  W2.2 correct: {by_pmid}")
    print(f"  Old index (wrong): {idx_wrong}")


if __name__ == "__main__":
    test_pubmed_mixed_linked_records()
    test_pubmed_all_paired()
    test_pubmed_all_pmid_only()
    test_scopus_linked_records()
    test_wos_linked_records()
    test_backward_compat_keys_present()
    test_linked_records_length_equals_retrieved_ids()
    test_multi_provider_independent_linked_records()
    test_error_provider_no_linked_records()
    test_linked_records_json_roundtrip()
    test_adversarial_pairing_preserved()
    print()
    print("All W2.2 tests passed.")
