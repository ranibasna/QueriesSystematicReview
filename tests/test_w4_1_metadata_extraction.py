"""W4.1 unit tests: per-provider metadata extraction and propagation.

W4.1 adds article-level metadata (title, first_author, year, journal) extraction
to all four search providers and propagates the data to provider_details[pname]['metadata']
inside _execute_query_bundle. The metadata is stored in a separate dict (keyed by DOI
or "pmid:XXXX"), NOT inlined into linked_records entries, to avoid ~3× JSON size inflation.

W4.0 (co-delivered here): RichGoldArticle dataclass and load_rich_gold_rows().

Test categories
---------------
 Cat-1  PubMedProvider._extract_article_metadata()
 Cat-2  PubMedProvider._get_dois_from_pmids() — _metadata_cache side effect
 Cat-3  ScopusProvider.search() — _metadata_cache population
 Cat-4  WebOfScienceProvider.search() — _metadata_cache population
 Cat-5  EmbaseLocalProvider.search() — _metadata_cache population
 Cat-6  _execute_query_bundle() — metadata in provider_details
 Cat-7  RichGoldArticle dataclass (W4.0)
 Cat-8  load_rich_gold_rows() (W4.0)
 Cat-9  import_embase_manual.py — first_author extraction
 Cat-10 Backward-compatibility: linked_records unchanged, old code unaffected
"""
import csv
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Set
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from search_providers import EmbaseLocalProvider
from llm_sr_select_and_score import (
    _execute_query_bundle,
    GoldArticle,
    RichGoldArticle,
    load_rich_gold_rows,
)
from import_embase_manual import parse_embase_csv


# ──────────────────────────────────────────────────────────────────────────────
# Minimal Biopython-like record builder for PubMed XML mocking
# ──────────────────────────────────────────────────────────────────────────────

class _StringElement(str):
    """Minimal stand-in for Bio.Entrez StringElement (str with optional attributes)."""
    def __new__(cls, value: str, attributes=None):
        obj = super().__new__(cls, value)
        obj.attributes = attributes or {}
        return obj


def _make_pubmed_record(pmid: str, doi: Optional[str] = None, title: str = "",
                         last_name: str = "", year: str = "", journal: str = "") -> dict:
    """Build a minimal PubmedArticle dict mimicking the Biopython Entrez.read() output."""
    article_ids = []
    if doi:
        doi_id = _StringElement(doi, {"IdType": "doi"})
        article_ids.append(doi_id)
    pmid_id = _StringElement(pmid, {"IdType": "pubmed"})
    article_ids.append(pmid_id)

    author_list = []
    if last_name:
        author_list = [{"LastName": last_name, "ForeName": "A"}]

    pub_date: Dict = {}
    if year:
        pub_date["Year"] = year

    return {
        "MedlineCitation": {
            "PMID": pmid,
            "Article": {
                "ArticleTitle": title,
                "AuthorList": author_list,
                "Journal": {
                    "Title": journal,
                    "JournalIssue": {"PubDate": pub_date},
                },
                "ELocationID": [],
            },
        },
        "PubmedData": {"ArticleIdList": article_ids},
    }


# ──────────────────────────────────────────────────────────────────────────────
# Fake providers for _execute_query_bundle tests
# ──────────────────────────────────────────────────────────────────────────────

class FakePubMedWithMeta:
    name = "pubmed"
    id_type = "pmid"

    def __init__(self, pmid_to_doi: dict, metadata_cache: dict,
                 extra_pmids: Optional[set] = None):
        self._pmid_doi = dict(pmid_to_doi)
        self._meta = dict(metadata_cache)
        self._extra = set(extra_pmids or [])

    def search(self, q, mn, mx, retmax=100000):
        self._pmid_to_doi_cache = self._pmid_doi
        self._metadata_cache = self._meta
        dois = set(self._pmid_doi.values())
        pmids = set(self._pmid_doi.keys()) | self._extra
        return dois, pmids, len(pmids)


class FakeScopusWithMeta:
    name = "scopus"
    id_type = "scopus_id"

    def __init__(self, dois: list, metadata_cache: dict):
        self._dois = set(dois)
        self._meta = dict(metadata_cache)

    def search(self, q, mn, mx, retmax=100000):
        self._metadata_cache = self._meta
        return self._dois, {f"s{i}" for i in range(len(self._dois))}, len(self._dois)


class FakeProviderNoMeta:
    """Provider that deliberately does NOT set _metadata_cache — backward compat test."""
    name = "legacy_db"
    id_type = "id"

    def search(self, q, mn, mx, retmax=100000):
        return {"10.x/1"}, {"sid1"}, 1


# ──────────────────────────────────────────────────────────────────────────────
# Cat-1  PubMedProvider._extract_article_metadata
# ──────────────────────────────────────────────────────────────────────────────

class TestPubMedExtractMetadata:
    """Unit tests for PubMedProvider._extract_article_metadata."""

    def _get_provider(self):
        from search_providers import PubMedProvider
        p = PubMedProvider.__new__(PubMedProvider)
        return p

    def test_all_fields_extracted(self):
        rec = _make_pubmed_record("111", doi="10.x/1", title="Sleep Apnea Study",
                                   last_name="Smith", year="2021", journal="Sleep")
        p = self._get_provider()
        meta = p._extract_article_metadata(rec)

        assert meta.get("title") == "Sleep Apnea Study"
        assert meta.get("first_author") == "Smith"
        assert meta.get("year") == 2021
        assert meta.get("journal") == "Sleep"

    def test_missing_doi_does_not_affect_metadata(self):
        """Metadata extraction succeeds even when no DOI is present."""
        rec = _make_pubmed_record("222", doi=None, title="Title Only",
                                   last_name="Jones", year="2019", journal="Nature")
        p = self._get_provider()
        meta = p._extract_article_metadata(rec)
        assert meta.get("title") == "Title Only"
        assert meta.get("first_author") == "Jones"
        assert meta.get("year") == 2019

    def test_empty_author_list_no_first_author(self):
        rec = _make_pubmed_record("333", title="No Author", year="2020", journal="BMJ")
        p = self._get_provider()
        meta = p._extract_article_metadata(rec)
        assert "first_author" not in meta
        assert meta.get("title") == "No Author"

    def test_medline_date_fallback_for_year(self):
        """When Year is absent, MedlineDate[:4] is used."""
        rec = _make_pubmed_record("444", title="Old Article", journal="Lancet")
        # Inject MedlineDate into PubDate
        rec["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]["PubDate"] = {
            "MedlineDate": "2015 Jan-Feb"
        }
        p = self._get_provider()
        meta = p._extract_article_metadata(rec)
        assert meta.get("year") == 2015

    def test_non_digit_year_omitted(self):
        rec = _make_pubmed_record("555", title="Bad Year", journal="NEJM")
        rec["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]["PubDate"] = {
            "Year": "unknown"
        }
        p = self._get_provider()
        meta = p._extract_article_metadata(rec)
        assert "year" not in meta

    def test_malformed_record_returns_empty(self):
        """Completely broken record should not raise; returns {}."""
        p = self._get_provider()
        meta = p._extract_article_metadata({"garbage": True})
        assert isinstance(meta, dict)

    def test_empty_title_not_stored(self):
        rec = _make_pubmed_record("666", title="", last_name="Brown",
                                   year="2022", journal="Cell")
        p = self._get_provider()
        meta = p._extract_article_metadata(rec)
        assert "title" not in meta
        assert meta.get("first_author") == "Brown"

    def test_empty_string_fields_omitted(self):
        """None / empty strings for all fields → empty dict returned."""
        rec = _make_pubmed_record("777", title="", last_name="", year="", journal="")
        p = self._get_provider()
        meta = p._extract_article_metadata(rec)
        assert meta == {}


# ──────────────────────────────────────────────────────────────────────────────
# Cat-2  PubMedProvider._get_dois_from_pmids — _metadata_cache side effect
# ──────────────────────────────────────────────────────────────────────────────

class TestPubMedMetadataCache:
    """_get_dois_from_pmids must populate _metadata_cache as a side effect."""

    def _provider_with_mock_fetch(self, articles: list):
        from search_providers import PubMedProvider
        p = PubMedProvider.__new__(PubMedProvider)
        # Patch Entrez.efetch to return a fake record set
        mock_records = {"PubmedArticle": articles}
        mock_handle = MagicMock()
        mock_handle.__enter__ = lambda s: s
        mock_handle.__exit__ = MagicMock(return_value=False)

        with patch("search_providers.Entrez.efetch", return_value=mock_handle), \
             patch("search_providers.Entrez.read", return_value=mock_records), \
             patch("search_providers.time.sleep"):
            result = p._get_dois_from_pmids(["111", "222"])
        return p, result

    def test_metadata_cache_populated_and_doi_keyed(self):
        articles = [
            _make_pubmed_record("111", doi="10.a/1", title="Title One",
                                 last_name="Alpha", year="2020", journal="J1"),
            _make_pubmed_record("222", doi="10.a/2", title="Title Two",
                                 last_name="Beta",  year="2021", journal="J2"),
        ]
        p, pmid_to_doi = self._provider_with_mock_fetch(articles)

        assert hasattr(p, "_metadata_cache"), "_metadata_cache not set"
        cache = p._metadata_cache

        # Keys should be DOIs (lowercase), not PMIDs
        assert "10.a/1" in cache, f"DOI key '10.a/1' missing from cache: {list(cache.keys())}"
        assert "10.a/2" in cache

        assert cache["10.a/1"]["title"] == "Title One"
        assert cache["10.a/1"]["first_author"] == "Alpha"
        assert cache["10.a/1"]["year"] == 2020
        assert cache["10.a/1"]["journal"] == "J1"

    def test_pmid_only_article_uses_pmid_key(self):
        """Articles without DOI in the PubMed XML → keyed as 'pmid:XXXX'."""
        articles = [
            _make_pubmed_record("333", doi=None, title="PMID-Only Article",
                                 last_name="Gamma", year="2018", journal="Old"),
        ]
        p, pmid_to_doi = self._provider_with_mock_fetch(articles)

        cache = p._metadata_cache
        assert "pmid:333" in cache, f"Expected 'pmid:333' key; found: {list(cache.keys())}"
        assert cache["pmid:333"]["title"] == "PMID-Only Article"

    def test_empty_pmids_gives_empty_metadata_cache(self):
        from search_providers import PubMedProvider
        p = PubMedProvider.__new__(PubMedProvider)
        result = p._get_dois_from_pmids([])
        assert result == {}
        assert hasattr(p, "_metadata_cache")
        assert p._metadata_cache == {}

    def test_article_with_no_metadata_not_in_cache(self):
        """Article with empty title/author/year/journal → absent from cache."""
        articles = [
            _make_pubmed_record("444", doi="10.a/3", title="", last_name="",
                                 year="", journal=""),
        ]
        p, _ = self._provider_with_mock_fetch(articles)
        # DOI was found, but metadata is empty → key should not appear
        cache = p._metadata_cache
        assert "10.a/3" not in cache, f"Unexpected entry: {cache.get('10.a/3')}"


# ──────────────────────────────────────────────────────────────────────────────
# Cat-3  ScopusProvider.search() — _metadata_cache population
# ──────────────────────────────────────────────────────────────────────────────

class TestScopusMetadataCache:

    def _run_search(self, entries: list):
        """Mock a Scopus search and return (provider, dois, metadata_cache)."""
        from search_providers import ScopusProvider
        p = ScopusProvider.__new__(ScopusProvider)
        p.api_key = "fake_key"
        p.insttoken = None
        p.view = "STANDARD"
        p.apply_year_filter = False
        p.session = MagicMock()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "search-results": {
                "opensearch:totalResults": str(len(entries)),
                "entry": entries,
            }
        }
        p.session.get.return_value = mock_resp

        with patch("search_providers.time.sleep"):
            dois, ids, total = p.search("q", "", "", retmax=100)

        return p, dois, p._metadata_cache

    def test_metadata_populated_from_entries(self):
        entries = [
            {
                "dc:identifier": "SCOPUS_ID:123",
                "prism:doi": "10.x/1",
                "dc:title": "Scopus Article One",
                "dc:creator": "Smith, John",
                "prism:coverDate": "2021-06-01",
                "prism:publicationName": "Nature",
            },
        ]
        p, dois, cache = self._run_search(entries)

        assert "10.x/1" in cache
        assert cache["10.x/1"]["title"] == "Scopus Article One"
        # dc:creator split on "," → "Smith"
        assert cache["10.x/1"]["first_author"] == "Smith"
        assert cache["10.x/1"]["year"] == 2021
        assert cache["10.x/1"]["journal"] == "Nature"

    def test_creator_without_comma_takes_first_token(self):
        """dc:creator "Jones PH." (no comma) → first_author="Jones PH." (kept as-is)."""
        entries = [
            {
                "dc:identifier": "SCOPUS_ID:456",
                "prism:doi": "10.x/2",
                "dc:title": "Article Two",
                "dc:creator": "Jones PH.",
                "prism:coverDate": "2019-01-01",
            },
        ]
        _, _, cache = self._run_search(entries)
        # No comma → take everything before first comma = full string
        assert cache["10.x/2"]["first_author"] == "Jones PH."

    def test_entry_without_doi_not_in_cache(self):
        """Entries missing prism:doi cannot be keyed → absent from metadata cache."""
        entries = [
            {
                "dc:identifier": "SCOPUS_ID:789",
                "dc:title": "No DOI Article",
                "dc:creator": "NoDOI A.",
                "prism:coverDate": "2020-03-01",
                "prism:publicationName": "Lancet",
            }
        ]
        _, _, cache = self._run_search(entries)
        assert len(cache) == 0, f"Unexpected entries in cache: {cache}"

    def test_year_from_four_char_coverdate(self):
        """prism:coverDate '2022' (just year) → year=2022."""
        entries = [
            {
                "dc:identifier": "SCOPUS_ID:11",
                "prism:doi": "10.x/3",
                "dc:title": "T",
                "prism:coverDate": "2022",
            }
        ]
        _, _, cache = self._run_search(entries)
        assert cache.get("10.x/3", {}).get("year") == 2022

    def test_metadata_cache_reset_on_each_search(self):
        """_metadata_cache must be reset at search() start, not accumulated across calls."""
        entries1 = [{"dc:identifier": "SCOPUS_ID:A1", "prism:doi": "10.a/1",
                     "dc:title": "T1", "prism:coverDate": "2020"}]
        entries2 = [{"dc:identifier": "SCOPUS_ID:A2", "prism:doi": "10.a/2",
                     "dc:title": "T2", "prism:coverDate": "2021"}]
        _, _, cache1 = self._run_search(entries1)
        _, _, cache2 = self._run_search(entries2)

        # Second call's cache should not contain first call's entry
        assert "10.a/1" not in cache2
        assert "10.a/2" in cache2


# ──────────────────────────────────────────────────────────────────────────────
# Cat-4  WebOfScienceProvider.search() — _metadata_cache population
# ──────────────────────────────────────────────────────────────────────────────

class TestWOSMetadataCache:

    def _run_search(self, hits: list):
        from search_providers import WebOfScienceProvider
        p = WebOfScienceProvider.__new__(WebOfScienceProvider)
        p.api_key = "fake_wos_key"
        p.db = "WOS"
        p.session = MagicMock()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "metadata": {"total": len(hits)},
            "hits": hits,
        }
        p.session.get.return_value = mock_resp

        with patch("search_providers.time.sleep"):
            dois, uids, total = p.search("q", "", "", retmax=100)

        return p, dois, p._metadata_cache

    def test_metadata_populated_from_hits(self):
        hits = [
            {
                "uid": "WOS:000001",
                "title": "WOS Article Title",
                "identifiers": {"doi": "10.w/1"},
                "names": {"authors": [{"displayName": "Brown, Alice"}]},
                "source": {"publishYear": 2022, "sourceTitle": "Science"},
            }
        ]
        _, dois, cache = self._run_search(hits)
        assert "10.w/1" in cache
        assert cache["10.w/1"]["title"] == "WOS Article Title"
        assert cache["10.w/1"]["first_author"] == "Brown"
        assert cache["10.w/1"]["year"] == 2022
        assert cache["10.w/1"]["journal"] == "Science"

    def test_author_without_comma_kept_as_is(self):
        """displayName without comma → entire string used as first_author."""
        hits = [
            {
                "uid": "WOS:000002",
                "title": "T",
                "identifiers": {"doi": "10.w/2"},
                "names": {"authors": [{"displayName": "Zhang W"}]},
                "source": {"publishYear": 2019, "sourceTitle": "Cell"},
            }
        ]
        _, _, cache = self._run_search(hits)
        # No comma → split(",")[0] = full string
        assert cache["10.w/2"]["first_author"] == "Zhang W"

    def test_no_authors_field_no_first_author(self):
        hits = [
            {
                "uid": "WOS:3",
                "title": "No Authors",
                "identifiers": {"doi": "10.w/3"},
                "names": {},
                "source": {"publishYear": 2020, "sourceTitle": "PNAS"},
            }
        ]
        _, _, cache = self._run_search(hits)
        assert "first_author" not in cache.get("10.w/3", {})

    def test_publish_year_as_string_converted_to_int(self):
        """publishYear may arrive as a string in some API responses."""
        hits = [
            {
                "uid": "WOS:4",
                "title": "Year as String",
                "identifiers": {"doi": "10.w/4"},
                "names": {"authors": [{"displayName": "Kim J"}]},
                "source": {"publishYear": "2023", "sourceTitle": "BMJ"},
            }
        ]
        _, _, cache = self._run_search(hits)
        assert cache.get("10.w/4", {}).get("year") == 2023

    def test_doi_less_hit_not_in_cache(self):
        hits = [
            {
                "uid": "WOS:5",
                "title": "No DOI",
                "identifiers": {},
                "names": {"authors": [{"displayName": "Xu P"}]},
                "source": {"publishYear": 2018, "sourceTitle": "JAMA"},
            }
        ]
        _, _, cache = self._run_search(hits)
        assert len(cache) == 0


# ──────────────────────────────────────────────────────────────────────────────
# Cat-5  EmbaseLocalProvider.search() — _metadata_cache population
# ──────────────────────────────────────────────────────────────────────────────

def _embase_json(query: str, records=None, dois=None, pmids=None) -> bytes:
    h = hashlib.sha256(query.encode()).hexdigest()
    entry: dict = {
        "query": query,
        "provider": "embase_manual",
        "results_count": len(records or dois or []),
        "records": records or [],
        "retrieved_dois": dois or [],
        "retrieved_pmids": pmids or [],
        "pmids": pmids or [],
    }
    return json.dumps({h: entry}).encode()


class TestEmbaseMetadataCache:

    def test_metadata_cache_from_records_doi_keyed(self, tmp_path):
        query = "sleep AND child"
        data = _embase_json(query, records=[
            {"pmid": "111", "doi": "10.e/1", "title": "Embase Title One",
             "first_author": "Garcia"},
            {"pmid": "222", "doi": "10.e/2", "title": "Embase Title Two"},
        ], dois=["10.e/1", "10.e/2"], pmids=["111", "222"])
        f = tmp_path / "embase.json"
        f.write_bytes(data)

        p = EmbaseLocalProvider(str(f))
        p.search(query, "", "")

        cache = p._metadata_cache
        assert "10.e/1" in cache
        assert cache["10.e/1"]["title"] == "Embase Title One"
        assert cache["10.e/1"]["first_author"] == "Garcia"
        # No journal/year → not in cache for this record
        assert "journal" not in cache["10.e/1"]
        assert "10.e/2" in cache
        assert cache["10.e/2"]["title"] == "Embase Title Two"

    def test_metadata_pmid_only_record_uses_pmid_key(self, tmp_path):
        query = "asthma"
        data = _embase_json(query, records=[
            {"pmid": "333", "title": "PMID-Only Article"},
        ], pmids=["333"])
        f = tmp_path / "embase.json"
        f.write_bytes(data)

        p = EmbaseLocalProvider(str(f))
        p.search(query, "", "")

        cache = p._metadata_cache
        assert "pmid:333" in cache
        assert cache["pmid:333"]["title"] == "PMID-Only Article"

    def test_metadata_with_year_stored_as_int(self, tmp_path):
        query = "diabetes"
        data = _embase_json(query, records=[
            {"doi": "10.e/3", "title": "With Year", "year": "2021"},
        ], dois=["10.e/3"])
        f = tmp_path / "embase.json"
        f.write_bytes(data)

        p = EmbaseLocalProvider(str(f))
        p.search(query, "", "")

        assert p._metadata_cache.get("10.e/3", {}).get("year") == 2021

    def test_metadata_record_no_identifiers_skipped(self, tmp_path):
        query = "obesity"
        data = _embase_json(query, records=[
            {"title": "No Identifier Article"},  # no pmid, no doi
        ])
        f = tmp_path / "embase.json"
        f.write_bytes(data)

        p = EmbaseLocalProvider(str(f))
        p.search(query, "", "")

        assert p._metadata_cache == {}

    def test_metadata_cache_empty_for_legacy_format_no_records(self, tmp_path):
        """Legacy JSON without 'records' list → _metadata_cache is {}."""
        query = "insomnia"
        h = hashlib.sha256(query.encode()).hexdigest()
        entry = {
            "query": query, "provider": "embase_manual", "results_count": 1,
            "retrieved_dois": ["10.e/old"], "retrieved_pmids": ["999"],
            "pmids": ["999"],
        }
        f = tmp_path / "legacy.json"
        f.write_bytes(json.dumps({h: entry}).encode())

        p = EmbaseLocalProvider(str(f))
        p.search(query, "", "")
        # No records list → metadata cache empty
        assert p._metadata_cache == {}

    def test_metadata_cache_attribute_always_present_on_empty_result(self, tmp_path):
        """Even when the JSON file is missing, _metadata_cache must be set to {}."""
        p = EmbaseLocalProvider(str(tmp_path / "does_not_exist.json"))
        p.search("some query", "", "")
        assert hasattr(p, "_metadata_cache")
        assert p._metadata_cache == {}


# ──────────────────────────────────────────────────────────────────────────────
# Cat-6  _execute_query_bundle — metadata in provider_details
# ──────────────────────────────────────────────────────────────────────────────

def _run(providers, qmap):
    _, _, _, pd = _execute_query_bundle(providers, qmap, "2020/01/01", "2024/12/31")
    return pd


class TestExecuteBundleMetadata:

    def test_metadata_key_present_in_provider_details(self):
        pm = FakePubMedWithMeta(
            pmid_to_doi={"111": "10.p/1"},
            metadata_cache={"10.p/1": {"title": "PubMed Article", "year": 2021}},
        )
        pd = _run([pm], {"pubmed": "q"})
        assert "metadata" in pd["pubmed"], "metadata key absent from provider_details"
        assert pd["pubmed"]["metadata"]["10.p/1"]["title"] == "PubMed Article"

    def test_metadata_additive_linked_records_unchanged(self):
        """linked_records must be identical to a pre-W4.1 run."""
        pm = FakePubMedWithMeta(
            pmid_to_doi={"111": "10.p/1"},
            metadata_cache={"10.p/1": {"title": "T"}},
        )
        pd = _run([pm], {"pubmed": "q"})
        lr = pd["pubmed"]["linked_records"]
        assert any(r["pmid"] == "111" and r["doi"] == "10.p/1" for r in lr), lr

    def test_metadata_empty_dict_for_provider_without_cache(self):
        """Provider lacking _metadata_cache → metadata key is {} (not KeyError)."""
        legacy = FakeProviderNoMeta()
        pd = _run([legacy], {"legacy_db": "q"})
        assert "metadata" in pd["legacy_db"]
        assert pd["legacy_db"]["metadata"] == {}

    def test_scopus_metadata_stored_separately(self):
        sc = FakeScopusWithMeta(
            dois=["10.s/1"],
            metadata_cache={"10.s/1": {"title": "Scopus Title", "year": 2022}},
        )
        pd = _run([sc], {"scopus": "q"})
        assert pd["scopus"]["metadata"].get("10.s/1", {}).get("title") == "Scopus Title"

    def test_multi_provider_metadata_per_provider(self):
        """Each provider's metadata appears only in its own provider_details entry."""
        pm = FakePubMedWithMeta(
            pmid_to_doi={"100": "10.p/100"},
            metadata_cache={"10.p/100": {"title": "PubMed Article 100"}},
        )
        sc = FakeScopusWithMeta(
            dois=["10.s/200"],
            metadata_cache={"10.s/200": {"title": "Scopus Article 200"}},
        )
        pd = _run([pm, sc], {"pubmed": "q", "scopus": "q"})

        assert "10.p/100" in pd["pubmed"]["metadata"]
        assert "10.s/200" in pd["scopus"]["metadata"]
        # Cross-contamination check
        assert "10.s/200" not in pd["pubmed"]["metadata"]
        assert "10.p/100" not in pd["scopus"]["metadata"]

    def test_error_provider_has_no_metadata_key(self):
        """Providers that raise during search() get an error entry without metadata."""
        class FailingProvider:
            name = "failed_db"
            id_type = "id"
            def search(self, q, mn, mx, retmax=100000):
                raise RuntimeError("simulated failure")

        pd = _run([FailingProvider()], {"failed_db": "q"})
        assert "error" in pd["failed_db"]
        assert "metadata" not in pd["failed_db"]  # error path skips metadata

    def test_metadata_is_json_serialisable(self):
        """provider_details including metadata can round-trip through json.dumps."""
        pm = FakePubMedWithMeta(
            pmid_to_doi={"111": "10.p/1"},
            metadata_cache={"10.p/1": {"title": "Test", "year": 2021,
                                        "first_author": "Doe", "journal": "J"}},
        )
        pd = _run([pm], {"pubmed": "q"})
        serialised = json.dumps(pd)  # must not raise
        loaded = json.loads(serialised)
        assert loaded["pubmed"]["metadata"]["10.p/1"]["year"] == 2021


# ──────────────────────────────────────────────────────────────────────────────
# Cat-7  RichGoldArticle dataclass (W4.0)
# ──────────────────────────────────────────────────────────────────────────────

class TestRichGoldArticle:

    def test_all_fields_settable(self):
        r = RichGoldArticle(
            pmid="123", doi="10.x/1", title="Title", year=2021,
            first_author="Smith", journal="Sleep"
        )
        assert r.pmid == "123"
        assert r.doi == "10.x/1"
        assert r.title == "Title"
        assert r.year == 2021
        assert r.first_author == "Smith"
        assert r.journal == "Sleep"

    def test_defaults_are_none(self):
        r = RichGoldArticle()
        assert r.pmid is None
        assert r.doi is None
        assert r.title is None
        assert r.year is None
        assert r.first_author is None
        assert r.journal is None

    def test_partial_construction_leaves_unset_as_none(self):
        r = RichGoldArticle(pmid="456", doi="10.x/2")
        assert r.title is None
        assert r.year is None

    def test_not_equal_to_gold_article_namedtuple(self):
        """RichGoldArticle is a separate type — must not accidentally equal GoldArticle."""
        ga = GoldArticle(pmid="111", doi="10.x/1")
        ra = RichGoldArticle(pmid="111", doi="10.x/1")
        assert type(ga) is not type(ra)


# ──────────────────────────────────────────────────────────────────────────────
# Cat-8  load_rich_gold_rows (W4.0)
# ──────────────────────────────────────────────────────────────────────────────

class TestLoadRichGoldRows:

    def _write_detailed_csv(self, tmp_path, rows_dicts: list, *, header=None) -> Path:
        if header is None:
            header = ["pmid", "first_author", "year", "title", "journal", "doi"]
        p = tmp_path / "gold_detailed.csv"
        with p.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            for row in rows_dicts:
                writer.writerow(row)
        return p

    def test_reads_all_columns(self, tmp_path):
        p = self._write_detailed_csv(tmp_path, [
            {"pmid": "100", "first_author": "Smith", "year": "2021",
             "title": "Article A", "journal": "Sleep", "doi": "10.x/a"},
        ])
        rows = load_rich_gold_rows(str(p))
        assert len(rows) == 1
        r = rows[0]
        assert r.pmid == "100"
        assert r.first_author == "Smith"
        assert r.year == 2021
        assert r.title == "Article A"
        assert r.journal == "Sleep"
        assert r.doi == "10.x/a"

    def test_doi_normalised_to_lowercase(self, tmp_path):
        p = self._write_detailed_csv(tmp_path, [
            {"pmid": "200", "first_author": "Doe", "year": "2020",
             "title": "T", "journal": "J", "doi": "10.X/UPPER"},
        ])
        rows = load_rich_gold_rows(str(p))
        assert rows[0].doi == "10.x/upper"

    def test_empty_cells_normalised_to_none(self, tmp_path):
        p = self._write_detailed_csv(tmp_path, [
            {"pmid": "300", "first_author": "", "year": "nan",
             "title": "No extras", "journal": "None", "doi": ""},
        ])
        rows = load_rich_gold_rows(str(p))
        r = rows[0]
        assert r.first_author is None
        assert r.year is None
        assert r.doi is None
        assert r.journal is None

    def test_missing_optional_columns_handled(self, tmp_path):
        """CSV with only pmid+doi (no title/year/author/journal) → fields are None."""
        p = self._write_detailed_csv(tmp_path, [
            {"pmid": "400", "doi": "10.x/d"},
        ], header=["pmid", "doi"])
        rows = load_rich_gold_rows(str(p))
        r = rows[0]
        assert r.pmid == "400"
        assert r.doi == "10.x/d"
        assert r.title is None
        assert r.year is None

    def test_multiple_rows_all_loaded(self, tmp_path):
        p = self._write_detailed_csv(tmp_path, [
            {"pmid": "1", "first_author": "A", "year": "2010",
             "title": "T1", "journal": "J1", "doi": "10.x/1"},
            {"pmid": "2", "first_author": "B", "year": "2015",
             "title": "T2", "journal": "J2", "doi": "10.x/2"},
            {"pmid": "3", "first_author": "C", "year": "2020",
             "title": "T3", "journal": "J3", "doi": "10.x/3"},
        ])
        rows = load_rich_gold_rows(str(p))
        assert len(rows) == 3
        assert rows[1].pmid == "2"
        assert rows[2].year == 2020

    def test_returns_rich_gold_article_instances(self, tmp_path):
        p = self._write_detailed_csv(tmp_path, [
            {"pmid": "500", "first_author": "X", "year": "2019",
             "title": "T", "journal": "J", "doi": "10.x/x"},
        ])
        rows = load_rich_gold_rows(str(p))
        assert isinstance(rows[0], RichGoldArticle)

    def test_column_order_independent(self, tmp_path):
        """Column detection is by name, not position."""
        p = self._write_detailed_csv(tmp_path, [
            {"doi": "10.x/rev", "year": "2022", "pmid": "600",
             "journal": "Cell", "title": "Reversed", "first_author": "Rev"},
        ], header=["doi", "year", "pmid", "journal", "title", "first_author"])
        rows = load_rich_gold_rows(str(p))
        assert rows[0].pmid == "600"
        assert rows[0].doi == "10.x/rev"
        assert rows[0].year == 2022


# ──────────────────────────────────────────────────────────────────────────────
# Cat-9  import_embase_manual — first_author extraction
# ──────────────────────────────────────────────────────────────────────────────

class TestImportEmbaseFirstAuthor:

    def _write_vertical(self, tmp_path, content: str) -> Path:
        p = tmp_path / "embase.csv"
        p.write_text(content, encoding="utf-8")
        return p

    def test_vertical_format_first_author_extracted(self, tmp_path):
        csv_content = (
            '"TITLE","Sleep Apnea in Children"\n'
            '"AUTHOR NAMES","Shi X.","Jiang P.","Wang P."\n'
            '"MEDLINE PMID","12345678","http://www.ncbi.nlm.nih.gov/pubmed/12345678"\n'
            '"DOI","10.1186/test-doi"\n'
        )
        f = self._write_vertical(tmp_path, csv_content)
        _, _, records, _ = parse_embase_csv(str(f))

        assert len(records) >= 1
        rec = records[0]
        assert rec.get("first_author") == "Shi", \
            f"Expected 'Shi', got {rec.get('first_author')!r}. Full record: {rec}"

    def test_vertical_format_single_author(self, tmp_path):
        csv_content = (
            '"TITLE","Effect of CPAP"\n'
            '"AUTHOR NAMES","Brown A.B."\n'
            '"DOI","10.x/cpap"\n'
        )
        f = self._write_vertical(tmp_path, csv_content)
        _, _, records, _ = parse_embase_csv(str(f))
        assert records[0].get("first_author") == "Brown"

    def test_vertical_format_no_author_names_field(self, tmp_path):
        """CSV without AUTHOR NAMES → first_author key absent from record."""
        csv_content = (
            '"TITLE","No Author Article"\n'
            '"DOI","10.x/noauth"\n'
        )
        f = self._write_vertical(tmp_path, csv_content)
        _, _, records, _ = parse_embase_csv(str(f))
        assert "first_author" not in records[0]

    def test_vertical_format_title_still_present(self, tmp_path):
        """Adding first_author extraction must not break existing title/doi extraction."""
        csv_content = (
            '"TITLE","Some Child Study"\n'
            '"AUTHOR NAMES","Rodriguez M.","Lopez A."\n'
            '"MEDLINE PMID","99999999","http://www.ncbi.nlm.nih.gov/pubmed/99999999"\n'
            '"DOI","10.x/xyz"\n'
        )
        f = self._write_vertical(tmp_path, csv_content)
        dois, pmids, records, _ = parse_embase_csv(str(f))
        assert "10.x/xyz" in dois
        assert "99999999" in pmids
        assert records[0]["title"] == "Some Child Study"
        assert records[0]["first_author"] == "Rodriguez"


# ──────────────────────────────────────────────────────────────────────────────
# Cat-10  Backward-compatibility
# ──────────────────────────────────────────────────────────────────────────────

class TestBackwardCompatibility:

    def test_gold_article_namedtuple_unchanged(self):
        """GoldArticle(pmid=..., doi=...) must still work exactly as before."""
        ga = GoldArticle(pmid="111", doi="10.x/1")
        assert ga.pmid == "111"
        assert ga.doi == "10.x/1"
        assert len(ga) == 2  # NamedTuple still has 2 fields

    def test_existing_linked_records_format_unchanged(self):
        """W4.1 must not change the structure of linked_records entries."""
        pm = FakePubMedWithMeta(
            pmid_to_doi={"A": "10.x/a"},
            metadata_cache={"10.x/a": {"title": "T"}},
        )
        _, _, _, pd = _execute_query_bundle(
            [pm], {"pubmed": "q"}, "2020/01/01", "2024/12/31"
        )
        for rec in pd["pubmed"]["linked_records"]:
            assert set(rec.keys()) == {"pmid", "doi"}, \
                f"linked_records entry has unexpected keys: {rec.keys()}"

    def test_old_keys_still_present_in_provider_details(self):
        """query, results_count, retrieved_ids, retrieved_dois, id_type, linked_records
        must all be present alongside the new metadata key."""
        pm = FakePubMedWithMeta(
            pmid_to_doi={"100": "10.x/100"},
            metadata_cache={"10.x/100": {"title": "T"}},
        )
        _, _, _, pd = _execute_query_bundle(
            [pm], {"pubmed": "q"}, "2020/01/01", "2024/12/31"
        )
        for required_key in ("query", "results_count", "retrieved_ids",
                              "retrieved_dois", "id_type", "linked_records", "metadata"):
            assert required_key in pd["pubmed"], \
                f"Key '{required_key}' missing from provider_details"
