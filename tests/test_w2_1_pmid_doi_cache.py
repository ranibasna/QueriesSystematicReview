"""W2.1 unit tests: _get_dois_from_pmids returns Dict[str,str] and
PubMedProvider.search() sets _pmid_to_doi_cache."""
import sys
from unittest.mock import patch

sys.path.insert(0, "/Users/ra1077ba/Documents/DataScience/GU/Daniil/LLM/QueriesSystematicReview")
from search_providers import PubMedProvider
from llm_sr_select_and_score import _execute_query_bundle


class SE(str):
    """Minimal stand-in for Bio.Entrez StringElement."""
    pass


def make_article(pmid, doi=None):
    art = {"MedlineCitation": {"PMID": SE(pmid)}, "PubmedData": {"ArticleIdList": []}}
    if doi:
        e = SE(doi)
        e.attributes = {"IdType": "doi"}
        art["PubmedData"]["ArticleIdList"] = [e]
    return art


class FH:
    """Fake Entrez handle."""
    def __init__(self, *, articles=None, sr=None):
        self._a = articles or []
        self._sr = sr

    def close(self):
        pass

    def read_result(self):
        return self._sr if self._sr is not None else {"PubmedArticle": self._a}


# ── Test 1 ── _get_dois_from_pmids returns dict, absent entry for no-DOI ────

def test_returns_dict():
    p = PubMedProvider(email="x@x.com")
    arts = [make_article("1", "10.a/b"), make_article("2", "10.c/d"), make_article("3")]
    h = FH(articles=arts)
    with patch("search_providers.Entrez.efetch", return_value=h), \
         patch("search_providers.Entrez.read", side_effect=lambda h: h.read_result()), \
         patch("search_providers.time.sleep"):
        r = p._get_dois_from_pmids(["1", "2", "3"])
    assert isinstance(r, dict), type(r)
    assert r == {"1": "10.a/b", "2": "10.c/d"}, r
    assert "3" not in r, "PMID with no DOI must not appear in mapping"
    print("PASS test_returns_dict:", r)


# ── Test 2 ── DOI values are lowercased ────────────────────────────────────

def test_lowercase():
    p = PubMedProvider(email="x@x.com")
    h = FH(articles=[make_article("9", "10.X/Y")])
    with patch("search_providers.Entrez.efetch", return_value=h), \
         patch("search_providers.Entrez.read", side_effect=lambda h: h.read_result()), \
         patch("search_providers.time.sleep"):
        r = p._get_dois_from_pmids(["9"])
    assert r == {"9": "10.x/y"}, r
    print("PASS test_lowercase:", r)


# ── Test 3 ── empty pmids returns empty dict ───────────────────────────────

def test_empty():
    p = PubMedProvider(email="x@x.com")
    assert p._get_dois_from_pmids([]) == {}
    print("PASS test_empty")


# ── Test 4 ── search() sets _pmid_to_doi_cache; dois == set(cache.values()) ─

def test_cache_and_signature():
    p = PubMedProvider(email="x@x.com")
    arts = [make_article("1", "10.a/b"), make_article("2", "10.c/d"), make_article("3")]
    sr = {"Count": "3", "IdList": ["1", "2", "3"]}
    with patch("search_providers.Entrez.esearch", return_value=FH(sr=sr)), \
         patch("search_providers.Entrez.efetch", return_value=FH(articles=arts)), \
         patch("search_providers.Entrez.read", side_effect=lambda h: h.read_result()), \
         patch("search_providers.time.sleep"):
        result = p.search("q", "2020/01/01", "2024/12/31")

    # Return signature must be unchanged: (set, set, int)
    assert len(result) == 3, len(result)
    dois, pmids, total = result
    assert isinstance(dois, set), type(dois)
    assert isinstance(pmids, set), type(pmids)
    assert isinstance(total, int), type(total)

    # Cache must be set as instance attribute
    assert hasattr(p, "_pmid_to_doi_cache"), "search() must set _pmid_to_doi_cache"
    cache = p._pmid_to_doi_cache
    assert isinstance(cache, dict), type(cache)

    # dois must equal set of cache values
    assert dois == set(cache.values()), (dois, cache)

    # PMID "3" has no DOI: absent from cache but present in pmids
    assert "3" not in cache
    assert "3" in pmids
    print("PASS test_cache_and_signature: cache=", cache)


# ── Test 5 ── per-article pairing correctness (the core value of W2.1) ─────

def test_pairing_adversarial():
    """Low PMID gets LATE DOI, high PMID gets EARLY DOI.

    Index-based pairing (old wrong approach):
      sorted PMIDs: ['0000001', '9999999']
      sorted DOIs:  ['10.aaa/early', '10.zzz/late']
      => 0000001 -> 10.aaa/early  (WRONG)
         9999999 -> 10.zzz/late   (WRONG)

    Dict-based pairing (W2.1):
      0000001 -> 10.zzz/late   (CORRECT, from same article record)
      9999999 -> 10.aaa/early  (CORRECT, from same article record)
    """
    p = PubMedProvider(email="x@x.com")
    arts = [
        make_article("0000001", "10.zzz/late"),
        make_article("9999999", "10.aaa/early"),
    ]
    h = FH(articles=arts)
    with patch("search_providers.Entrez.efetch", return_value=h), \
         patch("search_providers.Entrez.read", side_effect=lambda h: h.read_result()), \
         patch("search_providers.time.sleep"):
        r = p._get_dois_from_pmids(["0000001", "9999999"])

    assert r["0000001"] == "10.zzz/late",  r
    assert r["9999999"] == "10.aaa/early", r

    # Confirm the old index-based approach would give the WRONG answer here
    idx_wrong = dict(zip(sorted(r.keys()), sorted(r.values())))
    assert idx_wrong["0000001"] == "10.aaa/early", "sanity: index-based gives early"
    assert idx_wrong["9999999"] == "10.zzz/late",  "sanity: index-based gives late"

    print("PASS test_pairing_adversarial")
    print("  Correct (W2.1):", r)
    print("  Wrong (old index):", idx_wrong)


# ── Test 6 ── _execute_query_bundle reads _pmid_to_doi_cache ─────────────

def test_execute_reads_cache():
    class FakePubMed:
        name = "pubmed"
        id_type = "pmid"

        def search(self, q, mn, mx, retmax=100000):
            # 3 PMIDs, only 2 have DOIs
            self._pmid_to_doi_cache = {"111": "10.a/a", "222": "10.b/b"}
            dois = set(self._pmid_to_doi_cache.values())
            pmids = {"111", "222", "333"}
            return dois, pmids, 3

    p_pmids, p_dois, total, pd = _execute_query_bundle(
        [FakePubMed()], {"pubmed": "q"}, "2020/01/01", "2024/12/31"
    )
    assert p_dois == {"10.a/a", "10.b/b"}, p_dois
    assert p_pmids == {"111", "222", "333"}, p_pmids
    pbd = pd.get("pubmed", {})
    assert set(pbd["retrieved_dois"]) == {"10.a/a", "10.b/b"}
    assert set(pbd["retrieved_ids"]) == {"111", "222", "333"}
    print("PASS test_execute_reads_cache: dois=", p_dois, " pmids=", p_pmids)


# ── Test 7 ── _pmid_only_count uses exact cache (not approximation) ─────────

def test_pmid_only_count_exact():
    """When cache is available, pmid_only_count = len(pmids - cache.keys()).

    Scenario with genuine cross-DB duplication so the dedup log fires:
      PubMed:  5 PMIDs (A,B,C have DOIs; D,E are PMID-only), 3 DOIs, total=5
      Scopus:  4 DOIs (10.a/1, 10.a/2, 10.a/3 overlap with PubMed + 10.s/x new),
               total=4
    Combined:
      combined_dois = {10.a/1, 10.a/2, 10.a/3, 10.s/x} = 4
      combined_pmids = {A, B, C, D, E} = 5
      pmid_only = {D, E} = 2  (exact, using cache)
      unique = 4 + 2 = 6
      raw = 5 + 4 = 9  =>  duplicates_removed = 3 > 0 => log fires
    """
    class FakePubMed:
        name = "pubmed"
        id_type = "pmid"

        def search(self, q, mn, mx, retmax=100000):
            self._pmid_to_doi_cache = {"A": "10.a/1", "B": "10.a/2", "C": "10.a/3"}
            dois = set(self._pmid_to_doi_cache.values())
            pmids = {"A", "B", "C", "D", "E"}
            return dois, pmids, 5

    class FakeScopus:
        name = "scopus"
        id_type = "scopus_id"

        def search(self, q, mn, mx, retmax=100000):
            # overlaps with PubMed on 3 DOIs, adds 1 new
            dois = {"10.a/1", "10.a/2", "10.a/3", "10.s/x"}
            ids = {"s001", "s002", "s003", "s004"}
            return dois, ids, 4

    import io, contextlib

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _execute_query_bundle(
            [FakePubMed(), FakeScopus()],
            {"pubmed": "q", "scopus": "q"},
            "2020/01/01", "2024/12/31",
        )

    out = buf.getvalue()
    # The dedup log must mention "2 PubMed PMID-only" (D and E)
    assert "2 PubMed PMID-only" in out, \
        f"Expected '2 PubMed PMID-only' in dedup log. Got:\n{out}"
    print("PASS test_pmid_only_count_exact")
    print("  Dedup log:", out.strip())


if __name__ == "__main__":
    test_returns_dict()
    test_lowercase()
    test_empty()
    test_cache_and_signature()
    test_pairing_adversarial()
    test_execute_reads_cache()
    test_pmid_only_count_exact()
    print()
    print("All W2.1 tests passed.")
