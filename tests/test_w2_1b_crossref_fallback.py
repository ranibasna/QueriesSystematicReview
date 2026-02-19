"""W2.1b unit tests: CrossRef DOI fallback in PubMedProvider._get_dois_from_pmids().

Covers:
  1. CrossRef resolves a previously DOI-less PMID → appears in returned dict
  2. CrossRef PMID round-trip mismatch guard (Class E) → DOI rejected
  3. CrossRef HTTP error / empty response → graceful None, PMID absent from dict
  4. PMIDs that already got a DOI from efetch → CrossRef is NOT called for them
  5. _crossref_lookup parses the CrossRef response format correctly
"""
import sys
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, "/Users/ra1077ba/Documents/DataScience/GU/Daniil/LLM/QueriesSystematicReview")
from search_providers import PubMedProvider


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
    def __init__(self, *, articles=None, sr=None):
        self._a = articles or []
        self._sr = sr

    def close(self):
        pass

    def read_result(self):
        return self._sr if self._sr is not None else {"PubmedArticle": self._a}


def _make_crossref_response(doi, pmid=None):
    """Build a minimal CrossRef /works response with optional PMID field."""
    item = {"DOI": doi}
    if pmid is not None:
        item["PMID"] = pmid
    return {"message": {"items": [item]}}


# ── Test 1 ── CrossRef resolves a DOI-less PMID ──────────────────────────────

def test_crossref_resolves_missing_doi():
    """PMID '3' returns no DOI from efetch. CrossRef supplies '10.crossref/xxx'.
    The final dict must contain PMID '3' → '10.crossref/xxx'."""
    p = PubMedProvider(email="test@example.com")
    arts = [make_article("1", "10.a/b"), make_article("3")]  # "3" has no DOI
    h = FH(articles=arts)

    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = _make_crossref_response("10.CrossRef/xxx", pmid="3")

    with patch("search_providers.Entrez.efetch", return_value=h), \
         patch("search_providers.Entrez.read", side_effect=lambda h: h.read_result()), \
         patch("search_providers.time.sleep"), \
         patch("search_providers.requests.get", return_value=mock_resp) as mock_get:
        r = p._get_dois_from_pmids(["1", "3"])

    # DOI must be lowercased
    assert r == {"1": "10.a/b", "3": "10.crossref/xxx"}, r
    # CrossRef must only have been called for "3", not for "1" (which had a DOI)
    assert mock_get.call_count == 1
    call_kwargs = mock_get.call_args
    assert "pmid:3" in str(call_kwargs)
    print("PASS test_crossref_resolves_missing_doi:", r)


# ── Test 2 ── Class E guard: PMID mismatch → DOI rejected ───────────────────

def test_class_e_pmid_mismatch_guard():
    """CrossRef returns a DOI but with a different PMID (erratum scenario).
    The returned DOI must be rejected; PMID '3' must NOT appear in the result."""
    p = PubMedProvider(email="test@example.com")
    arts = [make_article("3")]  # no DOI from efetch
    h = FH(articles=arts)

    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    # CrossRef returns a DOI but the item's PMID is a different article (9999)
    mock_resp.json.return_value = _make_crossref_response("10.erratum/yyy", pmid="9999")

    with patch("search_providers.Entrez.efetch", return_value=h), \
         patch("search_providers.Entrez.read", side_effect=lambda h: h.read_result()), \
         patch("search_providers.time.sleep"), \
         patch("search_providers.requests.get", return_value=mock_resp):
        r = p._get_dois_from_pmids(["3"])

    assert "3" not in r, f"Mismatched PMID DOI must be rejected; got {r}"
    assert r == {}, r
    print("PASS test_class_e_pmid_mismatch_guard:", r)


# ── Test 3a ── CrossRef HTTP error → graceful None ───────────────────────────

def test_crossref_http_error_graceful():
    """CrossRef returns a non-200 status. PMID '3' must be absent from result (no crash)."""
    p = PubMedProvider(email="test@example.com")
    arts = [make_article("3")]
    h = FH(articles=arts)

    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = Exception("503 Service Unavailable")

    with patch("search_providers.Entrez.efetch", return_value=h), \
         patch("search_providers.Entrez.read", side_effect=lambda h: h.read_result()), \
         patch("search_providers.time.sleep"), \
         patch("search_providers.requests.get", return_value=mock_resp):
        r = p._get_dois_from_pmids(["3"])

    assert r == {}, r
    print("PASS test_crossref_http_error_graceful:", r)


# ── Test 3b ── CrossRef returns empty items list → graceful None ─────────────

def test_crossref_empty_items():
    """CrossRef returns an empty items list (no record registered for this PMID).
    PMID '3' must be absent from result."""
    p = PubMedProvider(email="test@example.com")
    arts = [make_article("3")]
    h = FH(articles=arts)

    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"message": {"items": []}}

    with patch("search_providers.Entrez.efetch", return_value=h), \
         patch("search_providers.Entrez.read", side_effect=lambda h: h.read_result()), \
         patch("search_providers.time.sleep"), \
         patch("search_providers.requests.get", return_value=mock_resp):
        r = p._get_dois_from_pmids(["3"])

    assert r == {}, r
    print("PASS test_crossref_empty_items:", r)


# ── Test 4 ── PMIDs with efetch DOIs are NOT passed to CrossRef ──────────────

def test_crossref_not_called_when_doi_from_efetch():
    """All three PMIDs resolve via efetch. CrossRef must not be called at all."""
    p = PubMedProvider(email="test@example.com")
    arts = [make_article("1", "10.a/a"), make_article("2", "10.b/b"), make_article("3", "10.c/c")]
    h = FH(articles=arts)

    with patch("search_providers.Entrez.efetch", return_value=h), \
         patch("search_providers.Entrez.read", side_effect=lambda h: h.read_result()), \
         patch("search_providers.time.sleep"), \
         patch("search_providers.requests.get") as mock_get:
        r = p._get_dois_from_pmids(["1", "2", "3"])

    assert mock_get.call_count == 0, f"CrossRef should not be called; call_count={mock_get.call_count}"
    assert r == {"1": "10.a/a", "2": "10.b/b", "3": "10.c/c"}, r
    print("PASS test_crossref_not_called_when_doi_from_efetch:", r)


# ── Test 5 ── _crossref_lookup matches polite-pool mailto parameter ───────────

def test_crossref_uses_mailto():
    """_crossref_lookup must include 'mailto' in the request params."""
    p = PubMedProvider(email="polite@example.com")

    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"message": {"items": []}}

    with patch("search_providers.requests.get", return_value=mock_resp) as mock_get:
        result = p._crossref_lookup("12345")

    assert result is None  # empty items → None
    call_kwargs = mock_get.call_args[1] if mock_get.call_args[1] else {}
    params = call_kwargs.get("params", {}) or (mock_get.call_args[0][1] if len(mock_get.call_args[0]) > 1 else {})
    # Check params dict directly
    actual_params = mock_get.call_args.kwargs.get("params") or mock_get.call_args.args[1] if len(mock_get.call_args.args) > 1 else None
    # Fallback: inspect the call string
    call_str = str(mock_get.call_args)
    assert "mailto" in call_str, f"'mailto' missing from CrossRef request params: {call_str}"
    assert "polite@example.com" in call_str, f"email missing from CrossRef params: {call_str}"
    print("PASS test_crossref_uses_mailto")


if __name__ == "__main__":
    test_crossref_resolves_missing_doi()
    test_class_e_pmid_mismatch_guard()
    test_crossref_http_error_graceful()
    test_crossref_empty_items()
    test_crossref_not_called_when_doi_from_efetch()
    test_crossref_uses_mailto()
    print()
    print("All W2.1b tests passed.")
