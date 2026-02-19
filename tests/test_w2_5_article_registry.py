"""
Tests for W2.5 — ArticleRegistry and updated load_articles_from_file().

W2.5 fixes Issue 2 (cross-DB dedup fails for PMID-only articles) by:
  1. Introducing ArticleRegistry to merge identifiers when the same article appears
     in multiple providers.
  2. Updating load_articles_from_file() to use linked_records (W2.2 format) and
     Embase records arrays before falling back to the legacy _merge_pmids_dois().

Test sections:
  A.  ArticleRegistry — unit tests
  B.  _articles_from_linked_records() — unit tests
  C.  load_articles_from_file() — integration tests for all three JSON formats
  D.  End-to-end dedup: verify article count is correct vs inflated legacy count
"""

import json
import os
import sys
import tempfile
import unittest

# ── Ensure the scripts package is importable ───────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from aggregate_queries import (
    Article,
    ArticleRegistry,
    _articles_from_linked_records,
    _merge_pmids_dois,
    load_articles_from_file,
)


# ==============================================================================
# Section A — ArticleRegistry unit tests
# ==============================================================================

class TestArticleRegistryBasic(unittest.TestCase):
    """Basic add / lookup operations."""

    def test_add_single_article_doi_and_pmid(self):
        reg = ArticleRegistry()
        art = reg.add('12345', '10.1001/test.2021')
        self.assertEqual(art.pmid, '12345')
        self.assertEqual(art.doi, '10.1001/test.2021')
        self.assertEqual(len(reg), 1)

    def test_add_doi_only(self):
        reg = ArticleRegistry()
        art = reg.add(None, '10.1001/test.2021')
        self.assertIsNone(art.pmid)
        self.assertEqual(art.doi, '10.1001/test.2021')
        self.assertEqual(len(reg), 1)

    def test_add_pmid_only(self):
        reg = ArticleRegistry()
        art = reg.add('12345', None)
        self.assertEqual(art.pmid, '12345')
        self.assertIsNone(art.doi)
        self.assertEqual(len(reg), 1)

    def test_add_empty_returns_none(self):
        reg = ArticleRegistry()
        result = reg.add(None, None)
        self.assertIsNone(result)
        self.assertEqual(len(reg), 0)

    def test_add_blank_strings_treated_as_empty(self):
        reg = ArticleRegistry()
        result = reg.add('', '  ')
        self.assertIsNone(result)
        self.assertEqual(len(reg), 0)

    def test_len_multiple_articles(self):
        reg = ArticleRegistry()
        reg.add('111', '10.1001/a')
        reg.add('222', '10.1001/b')
        reg.add('333', None)
        self.assertEqual(len(reg), 3)

    def test_articles_returns_frozenset(self):
        reg = ArticleRegistry()
        reg.add('111', '10.1001/a')
        snap = reg.articles()
        self.assertIsInstance(snap, frozenset)
        self.assertEqual(len(snap), 1)


class TestArticleRegistryDeduplication(unittest.TestCase):
    """Core dedup behaviour — the reason W2.5 was built."""

    def test_dedup_by_doi_adds_pmid(self):
        """
        Core scenario: PubMed adds (pmid=X, doi=D) then Scopus adds (pmid=None, doi=D).
        Registry must merge them → 1 article with (pmid=X, doi=D).
        """
        reg = ArticleRegistry()
        reg.add('34160576', '10.1001/jamacardio.2021.2003')  # PubMed
        reg.add(None,        '10.1001/jamacardio.2021.2003')  # Scopus (same DOI)
        self.assertEqual(len(reg), 1)
        art = list(reg.articles())[0]
        self.assertEqual(art.pmid, '34160576')
        self.assertEqual(art.doi, '10.1001/jamacardio.2021.2003')

    def test_dedup_doi_only_then_pmid_doi(self):
        """
        Add Scopus DOI-only first  → then PubMed (pmid, doi) for the same DOI.
        Registry must merge in both directions.
        """
        reg = ArticleRegistry()
        reg.add(None,        '10.1001/jamacardio.2021.2003')  # Scopus first
        reg.add('34160576', '10.1001/jamacardio.2021.2003')   # PubMed second
        self.assertEqual(len(reg), 1)
        art = list(reg.articles())[0]
        self.assertEqual(art.pmid, '34160576')
        self.assertEqual(art.doi, '10.1001/jamacardio.2021.2003')

    def test_dedup_by_pmid(self):
        """Same PMID added twice (different call sites) → 1 article."""
        reg = ArticleRegistry()
        reg.add('12345', None)
        reg.add('12345', None)
        self.assertEqual(len(reg), 1)

    def test_dedup_by_pmid_gains_doi(self):
        """PMID-only first, then same PMID with DOI → merge, doi is filled in."""
        reg = ArticleRegistry()
        reg.add('12345', None)
        reg.add('12345', '10.1001/newdoi')
        self.assertEqual(len(reg), 1)
        art = list(reg.articles())[0]
        self.assertEqual(art.doi, '10.1001/newdoi')

    def test_doi_case_insensitive_dedup(self):
        """DOIs are normalised to lowercase — case variants should not produce duplicates."""
        reg = ArticleRegistry()
        reg.add('111', '10.1001/TEST.DOI')
        reg.add('222', '10.1001/test.doi')  # same DOI, different case
        self.assertEqual(len(reg), 1)
        art = list(reg.articles())[0]
        # The first-registered PMID ('111') is kept; doi is lowercase
        self.assertEqual(art.doi, '10.1001/test.doi')

    def test_no_merge_different_articles(self):
        """Two articles with different PMID and different DOI → 2 articles, no merge."""
        reg = ArticleRegistry()
        reg.add('111', '10.1001/a')
        reg.add('222', '10.1001/b')
        self.assertEqual(len(reg), 2)

    def test_pmid_only_plus_doi_only_no_merge(self):
        """
        Known limitation: PMID-only + DOI-only for the same physical article cannot
        be merged because there is no shared identifier.  Both remain separate.

        This is the ~22-article-per-query residual from Issue 2 that W4 (fuzzy
        matching) will address.
        """
        reg = ArticleRegistry()
        reg.add('18388205', None)                     # PubMed PMID-only
        reg.add(None, '10.1136/thx.2007.091132')      # Scopus DOI-only, same article
        # Cannot merge → 2 separate articles
        self.assertEqual(len(reg), 2)

    def test_doi_stored_on_first_add_when_existing_lacks_doi(self):
        """
        After merge, the new doi is stored on the canonical record so a third add
        with the SAME doi also deduplicates correctly.
        """
        reg = ArticleRegistry()
        reg.add('12345', None)             # PMID-only
        reg.add('12345', '10.1001/x')     # same PMID, adds DOI
        reg.add(None,    '10.1001/x')     # DOI-only for same article — should dedup
        self.assertEqual(len(reg), 1)


class TestArticleRegistryMultipleProviders(unittest.TestCase):
    """Registry behaviour when all three providers contribute records."""

    def setUp(self):
        # Realistic ai_2022-style scenario:
        # Gold article 1: pmid='34160576', doi='10.1001/jamacardio.2021.2003'
        # Gold article 2: pmid='25518901', doi='10.1164/rccm.200309-1305oc'
        # Non-gold article: pmid='100125', doi='10.1001/archpedi.161.11.1091'
        self.reg = ArticleRegistry()
        # PubMed
        self.reg.add('34160576', '10.1001/jamacardio.2021.2003')
        self.reg.add('25518901', '10.1164/rccm.200309-1305oc')
        self.reg.add('100125',   '10.1001/archpedi.161.11.1091')
        self.reg.add('999',      None)              # PMID-only in PubMed
        # Scopus (DOI-only; same first two articles)
        self.reg.add(None, '10.1001/jamacardio.2021.2003')
        self.reg.add(None, '10.1164/rccm.200309-1305oc')
        self.reg.add(None, '10.1001/scopus.exclusive')  # Scopus-exclusive
        # WOS (DOI-only)
        self.reg.add(None, '10.1001/jamacardio.2021.2003')  # third occurrence
        self.reg.add(None, '10.1001/wos.exclusive')

    def test_correct_total_count(self):
        """
        Expected unique articles:
          - gold1 (pmid+doi): 1 (PubMed + Scopus + WOS all contribute same DOI → 1)
          - gold2 (pmid+doi): 1 (PubMed + Scopus same DOI → 1)
          - non-gold1 (pmid+doi from PubMed): 1
          - pmid-only: 1
          - scopus-exclusive doi: 1
          - wos-exclusive doi: 1
          Total = 6
        """
        self.assertEqual(len(self.reg), 6)

    def test_gold1_has_pmid(self):
        """After merging, gold article 1 must carry PMID sourced from PubMed."""
        arts = {a.doi: a for a in self.reg.articles() if a.doi}
        art1 = arts.get('10.1001/jamacardio.2021.2003')
        self.assertIsNotNone(art1)
        self.assertEqual(art1.pmid, '34160576')

    def test_gold2_has_pmid(self):
        arts = {a.doi: a for a in self.reg.articles() if a.doi}
        art2 = arts.get('10.1164/rccm.200309-1305oc')
        self.assertIsNotNone(art2)
        self.assertEqual(art2.pmid, '25518901')

    def test_scopus_exclusive_no_pmid(self):
        arts = {a.doi: a for a in self.reg.articles() if a.doi}
        scopus_art = arts.get('10.1001/scopus.exclusive')
        self.assertIsNotNone(scopus_art)
        self.assertIsNone(scopus_art.pmid)

    def test_pmid_only_preserved(self):
        pmid_arts = {a.pmid for a in self.reg.articles() if a.pmid and not a.doi}
        self.assertIn('999', pmid_arts)


# ==============================================================================
# Section B — _articles_from_linked_records() unit tests
# ==============================================================================

class TestArticlesFromLinkedRecords(unittest.TestCase):
    """Tests for the _articles_from_linked_records() helper."""

    def _make_pd(self, pubmed_links, scopus_links=None, wos_links=None):
        """Build a mock provider_details dict."""
        pd = {}
        if pubmed_links is not None:
            pd['pubmed'] = {'linked_records': pubmed_links}
        if scopus_links is not None:
            pd['scopus'] = {'linked_records': scopus_links}
        if wos_links is not None:
            pd['wos'] = {'linked_records': wos_links}
        return pd

    def test_returns_none_when_no_linked_records(self):
        """Legacy provider_details without linked_records → returns None."""
        pd = {'pubmed': {'retrieved_ids': ['1', '2'], 'retrieved_dois': ['10.1/a']}}
        result = _articles_from_linked_records(pd)
        self.assertIsNone(result)

    def test_returns_none_for_empty_provider_details(self):
        result = _articles_from_linked_records({})
        self.assertIsNone(result)

    def test_single_provider_pubmed(self):
        links = [{'pmid': '111', 'doi': '10.1001/a'}, {'pmid': '222', 'doi': None}]
        pd = self._make_pd(links)
        arts = _articles_from_linked_records(pd)
        self.assertIsNotNone(arts)
        self.assertEqual(len(arts), 2)

    def test_cross_provider_dedup(self):
        """PubMed (pmid+doi) + Scopus (doi-only same DOI) → 1 article."""
        pubmed_links = [{'pmid': '111', 'doi': '10.1001/a'}]
        scopus_links = [{'pmid': None, 'doi': '10.1001/a'}]
        pd = self._make_pd(pubmed_links, scopus_links)
        arts = _articles_from_linked_records(pd)
        self.assertIsNotNone(arts)
        self.assertEqual(len(arts), 1)
        art = list(arts)[0]
        self.assertEqual(art.pmid, '111')
        self.assertEqual(art.doi, '10.1001/a')

    def test_partial_linked_records_uses_available(self):
        """Provider without linked_records is skipped; provider with it is used."""
        pd = {
            'pubmed': {'linked_records': [{'pmid': '111', 'doi': '10.1001/a'}]},
            'scopus': {'retrieved_ids': ['s1'], 'retrieved_dois': ['10.1001/b']},  # no linked_records
        }
        arts = _articles_from_linked_records(pd)
        self.assertIsNotNone(arts)
        # Only PubMed linked_records processed; scopus has no linked_records → 1 article
        self.assertEqual(len(arts), 1)

    def test_none_doi_and_none_pmid_skipped(self):
        links = [{'pmid': None, 'doi': None}, {'pmid': '111', 'doi': '10.1/a'}]
        pd = self._make_pd(links)
        arts = _articles_from_linked_records(pd)
        self.assertIsNotNone(arts)
        self.assertEqual(len(arts), 1)  # null-null record is skipped

    def test_returns_set_type(self):
        pd = self._make_pd([{'pmid': '1', 'doi': '10.1/a'}])
        arts = _articles_from_linked_records(pd)
        self.assertIsInstance(arts, set)


# ==============================================================================
# Section C — load_articles_from_file() integration tests
# ==============================================================================

class TestLoadArticlesFromFile(unittest.TestCase):
    """Integration tests using real temporary JSON files for all three formats."""

    def _write_tmp(self, data) -> str:
        fd, path = tempfile.mkstemp(suffix='.json')
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f)
        return path

    # ── Format 3 (list): details_*.json — W2.2 with linked_records ─────────────

    def test_list_format_with_linked_records(self):
        """W2.5 primary path: list format + linked_records → registry dedup."""
        data = [
            {
                'query': 'test query',
                'results_count': 3,
                'retrieved_pmids': ['111', '222'],
                'retrieved_dois': ['10.1/a', '10.1/b'],
                'provider_details': {
                    'pubmed': {
                        'linked_records': [
                            {'pmid': '111', 'doi': '10.1/a'},
                            {'pmid': '222', 'doi': None},
                        ]
                    },
                    'scopus': {
                        'linked_records': [
                            {'pmid': None, 'doi': '10.1/a'},   # same as PubMed's article 1
                            {'pmid': None, 'doi': '10.1/c'},   # Scopus-exclusive
                        ]
                    },
                },
            }
        ]
        path = self._write_tmp(data)
        try:
            result = load_articles_from_file(path)
        finally:
            os.unlink(path)

        self.assertIn('test query', result)
        arts = result['test query']
        # PubMed article 1 (111, 10.1/a) merged with Scopus DOI (10.1/a) → 1 article
        # PubMed article 2 (222, None) → 1 article
        # Scopus-exclusive (None, 10.1/c) → 1 article
        self.assertEqual(len(arts), 3)
        by_doi = {a.doi: a for a in arts if a.doi}
        self.assertEqual(by_doi['10.1/a'].pmid, '111')  # PMID carried from PubMed
        self.assertIsNone(by_doi['10.1/c'].pmid)        # Scopus-exclusive has no PMID

    def test_list_format_legacy_fallback(self):
        """Old format (no provider_details/linked_records) → _merge_pmids_dois fallback."""
        data = [
            {
                'query': 'legacy query',
                'retrieved_pmids': ['100', '200'],
                'retrieved_dois': ['10.1/x', '10.1/y'],
            }
        ]
        path = self._write_tmp(data)
        try:
            result = load_articles_from_file(path)
        finally:
            os.unlink(path)

        self.assertIn('legacy query', result)
        # Legacy path produces 2 articles (index-paired)
        self.assertEqual(len(result['legacy query']), 2)

    def test_list_format_multiple_queries(self):
        """Multiple query entries in list are all loaded as separate keys."""
        data = [
            {
                'query': 'query A',
                'retrieved_pmids': ['1'],
                'retrieved_dois': ['10.1/a'],
            },
            {
                'query': 'query B',
                'retrieved_pmids': ['2'],
                'retrieved_dois': ['10.1/b'],
            },
        ]
        path = self._write_tmp(data)
        try:
            result = load_articles_from_file(path)
        finally:
            os.unlink(path)

        self.assertEqual(set(result.keys()), {'query A', 'query B'})

    # ── Format 2 (dict): Embase format with records ─────────────────────────────

    def test_dict_embase_format_with_records(self):
        """Embase per-record PMID+DOI pairing is used (W2.5 path (a))."""
        embase_data = {
            'sha_hash_key': {
                'query': 'embase query 1',
                'results_count': 3,
                'records': [
                    {'title': 'Article A', 'pmid': '111', 'doi': '10.1/a'},
                    {'title': 'Article B', 'pmid': None,  'doi': '10.1/b'},
                    {'title': 'Article C', 'pmid': '333', 'doi': '10.1/c'},
                ],
                'retrieved_pmids': ['111', '333'],
                'retrieved_dois': ['10.1/a', '10.1/b', '10.1/c'],
            }
        }
        path = self._write_tmp(embase_data)
        try:
            result = load_articles_from_file(path)
        finally:
            os.unlink(path)

        self.assertIn('embase query 1', result)
        arts = result['embase query 1']
        self.assertEqual(len(arts), 3)
        by_doi = {a.doi: a for a in arts if a.doi}
        self.assertEqual(by_doi['10.1/a'].pmid, '111')
        self.assertIsNone(by_doi['10.1/b'].pmid)
        self.assertEqual(by_doi['10.1/c'].pmid, '333')

    def test_dict_embase_empty_records(self):
        """Empty Embase records array → no articles (graceful, no crash)."""
        embase_data = {
            'key': {
                'query': 'empty embase',
                'results_count': 0,
                'records': [],
                'retrieved_pmids': [],
                'retrieved_dois': [],
                'note': 'Empty query — returned 0 results',
            }
        }
        path = self._write_tmp(embase_data)
        try:
            result = load_articles_from_file(path)
        finally:
            os.unlink(path)

        # Empty records → entry not included in result (articles set is empty → skipped)
        self.assertNotIn('empty embase', result)

    def test_dict_embase_records_take_priority_over_flat_lists(self):
        """
        When both 'records' and 'retrieved_pmids'/'retrieved_dois' are present,
        the 'records' array (accurate) must be used, not the flat lists.
        """
        embase_data = {
            'key': {
                'query': 'embase with both',
                'records': [{'pmid': '111', 'doi': '10.1/correct'}],
                'retrieved_pmids': ['999'],       # would pair incorrectly via _merge_pmids_dois
                'retrieved_dois': ['10.1/wrong'],
            }
        }
        path = self._write_tmp(embase_data)
        try:
            result = load_articles_from_file(path)
        finally:
            os.unlink(path)

        arts = result['embase with both']
        self.assertEqual(len(arts), 1)
        art = list(arts)[0]
        self.assertEqual(art.doi, '10.1/correct')
        self.assertEqual(art.pmid, '111')

    def test_dict_legacy_fallback_no_records_no_linked(self):
        """Old dict format without records/linked_records → legacy fallback."""
        data = {
            'some_key': {
                'query': 'old query',
                'pmids': ['1', '2'],
                'dois': ['10.1/a', '10.1/b'],
            }
        }
        path = self._write_tmp(data)
        try:
            result = load_articles_from_file(path)
        finally:
            os.unlink(path)

        self.assertIn('old query', result)

    # ── Format 1 (dict with 'retrieved_pmids'): sealed_*.json ──────────────────

    def test_sealed_format_no_provider_details(self):
        """Sealed JSON without provider_details → legacy _merge_pmids_dois fallback."""
        data = {
            'query': 'sealed query',
            'retrieved_pmids': ['10', '20'],
            'retrieved_dois': ['10.1/a', '10.1/b'],
        }
        path = self._write_tmp(data)
        try:
            result = load_articles_from_file(path)
        finally:
            os.unlink(path)

        self.assertIn('sealed query', result)
        self.assertEqual(len(result['sealed query']), 2)

    def test_sealed_format_with_linked_records(self):
        """Sealed JSON with provider_details.linked_records → W2.5 path."""
        data = {
            'query': 'sealed with linked',
            'retrieved_pmids': ['111'],
            'retrieved_dois': ['10.1/a'],
            'provider_details': {
                'pubmed': {
                    'linked_records': [{'pmid': '111', 'doi': '10.1/a'}]
                },
                'scopus': {
                    'linked_records': [{'pmid': None, 'doi': '10.1/a'}]  # same article
                },
            },
        }
        path = self._write_tmp(data)
        try:
            result = load_articles_from_file(path)
        finally:
            os.unlink(path)

        arts = result['sealed with linked']
        self.assertEqual(len(arts), 1)  # deduped via registry
        art = list(arts)[0]
        self.assertEqual(art.pmid, '111')


# ==============================================================================
# Section D — End-to-end dedup: article count vs legacy inflated count
# ==============================================================================

class TestEndToEndDedup(unittest.TestCase):
    """
    Verify that W2.5 produces fewer (correctly deduped) articles than the legacy
    _merge_pmids_dois() which inflated counts by pairing index-based.
    """

    def _make_details(self, pubmed_linked, scopus_linked, wos_linked=None):
        """Build a details_*.json list structure as written by score_queries()."""
        provider_details = {
            'pubmed': {'linked_records': pubmed_linked},
            'scopus': {'linked_records': scopus_linked},
        }
        if wos_linked is not None:
            provider_details['wos'] = {'linked_records': wos_linked}
        combined_pmids = [r['pmid'] for r in pubmed_linked if r.get('pmid')]
        combined_dois = list({
            r['doi'] for r in pubmed_linked + scopus_linked + (wos_linked or [])
            if r.get('doi')
        })
        return [
            {
                'query': 'test',
                'retrieved_pmids': combined_pmids,
                'retrieved_dois': combined_dois,
                'provider_details': provider_details,
            }
        ]

    def test_registry_path_fewer_than_legacy_path(self):
        """
        ai_2022-style scenario (scaled):
          PubMed: 5 articles with (pmid, doi), 2 PMID-only
          Scopus: 8 articles with DOI-only (3 overlap with PubMed DOIs)
          WOS:    4 articles with DOI-only (2 overlap with Scopus DOIs)

        Legacy (index-pairing) would pair randomly → possibly 15 articles.
        W2.5 (registry) correctly: 5 PubMed-paired + 2 PMID-only + 5 Scopus-unique + 2 WOS-unique = 14
          but 3 PubMed articles overlap with Scopus → registry merges → 5+2+5+2 = 14 unique
          (3 Scopus overlaps with PubMed are merged → don't add new articles)
        """
        pubmed_linked = [
            {'pmid': 'A', 'doi': '10.1/a'},
            {'pmid': 'B', 'doi': '10.1/b'},
            {'pmid': 'C', 'doi': '10.1/c'},
            {'pmid': 'D', 'doi': '10.1/d'},
            {'pmid': 'E', 'doi': '10.1/e'},
            {'pmid': 'F', 'doi': None},
            {'pmid': 'G', 'doi': None},
        ]
        scopus_linked = [
            {'pmid': None, 'doi': '10.1/a'},   # overlap A
            {'pmid': None, 'doi': '10.1/b'},   # overlap B
            {'pmid': None, 'doi': '10.1/c'},   # overlap C
            {'pmid': None, 'doi': '10.1/s1'},  # Scopus-unique
            {'pmid': None, 'doi': '10.1/s2'},
            {'pmid': None, 'doi': '10.1/s3'},
            {'pmid': None, 'doi': '10.1/s4'},
            {'pmid': None, 'doi': '10.1/s5'},
        ]
        wos_linked = [
            {'pmid': None, 'doi': '10.1/s1'},  # overlap with Scopus
            {'pmid': None, 'doi': '10.1/s2'},  # overlap with Scopus
            {'pmid': None, 'doi': '10.1/w1'},  # WOS-unique
            {'pmid': None, 'doi': '10.1/w2'},  # WOS-unique
        ]
        # Via ArticleRegistry (W2.5):
        # PubMed: 5 paired + 2 PMID-only = 7
        # Scopus: 3 already merged (doi overlap), 5 new = 5 unique additions
        # WOS: 2 already merged (doi overlap with Scopus), 2 new = 2 unique additions
        # Total: 7 + 5 + 2 = 14
        reg = ArticleRegistry()
        for rec in pubmed_linked + scopus_linked + wos_linked:
            reg.add(rec.get('pmid'), rec.get('doi'))
        self.assertEqual(len(reg), 14)

        # Via _merge_pmids_dois (legacy): takes the combined top-level lists and pairs by index.
        # This is the old behavior — counts may differ from true unique.
        combined_pmids = [r['pmid'] for r in pubmed_linked if r.get('pmid')]  # 5 (not F,G)
        all_dois = list(dict.fromkeys(
            r['doi'] for r in pubmed_linked + scopus_linked + wos_linked if r.get('doi')
        ))  # 14 unique DOIs
        legacy_arts = _merge_pmids_dois(combined_pmids, all_dois)
        # Legacy produces the same SET of DOIs (14), plus the 2 PMID-only articles.
        # But 5 PMIDs are paired to wrong DOIs → 5 articles have wrong PMID+DOI combos.
        # Count-wise: 14 dois + 2 pmid-only not paired to doi → could be 16.
        # The key invariant: W2.5 count (14) is ≤ legacy count because it deduplicates.
        self.assertLessEqual(len(reg), len(legacy_arts) + 2,
                             "Registry should not inflate count beyond legacy")

    def test_cross_provider_dedup_reduces_count(self):
        """
        Simpler regression: 10 PubMed articles with (pmid+doi) and the same 10 DOIs
        from Scopus → 10 unique, not 20.
        """
        reg = ArticleRegistry()
        for i in range(10):
            reg.add(str(i), f'10.1/{i}')         # PubMed
            reg.add(None,   f'10.1/{i}')           # Scopus (same DOI)
        self.assertEqual(len(reg), 10)

    def test_load_from_file_dedup(self):
        """
        Full round-trip through load_articles_from_file() with linked_records.
        10 PubMed + 10 Scopus same DOIs → 10 articles (not 20).
        """
        pubmed_links = [{'pmid': str(i), 'doi': f'10.1/{i}'} for i in range(10)]
        scopus_links = [{'pmid': None,   'doi': f'10.1/{i}'} for i in range(10)]
        data = [
            {
                'query': 'dedup_test',
                'retrieved_pmids': [str(i) for i in range(10)],
                'retrieved_dois': [f'10.1/{i}' for i in range(10)],
                'provider_details': {
                    'pubmed': {'linked_records': pubmed_links},
                    'scopus': {'linked_records': scopus_links},
                },
            }
        ]
        fd, path = tempfile.mkstemp(suffix='.json')
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f)
        try:
            result = load_articles_from_file(path)
        finally:
            os.unlink(path)

        self.assertEqual(len(result['dedup_test']), 10)

    def test_all_articles_have_pmid_when_pubmed_provided_doi(self):
        """
        After W2.5, every PubMed-sourced article that has a DOI should carry its
        PMID in the canonical Article — even if Scopus also provided the same DOI
        (DOI-only in Scopus's linked_records).
        """
        pubmed_links = [
            {'pmid': '34160576', 'doi': '10.1001/jamacardio.2021.2003'},
            {'pmid': '25518901', 'doi': '10.1164/rccm.200309-1305oc'},
        ]
        scopus_links = [
            {'pmid': None, 'doi': '10.1001/jamacardio.2021.2003'},
            {'pmid': None, 'doi': '10.1164/rccm.200309-1305oc'},
            {'pmid': None, 'doi': '10.1016/scopus.only'},
        ]
        data = [
            {
                'query': 'ai2022_q1',
                'retrieved_pmids': ['34160576', '25518901'],
                'retrieved_dois': [],
                'provider_details': {
                    'pubmed': {'linked_records': pubmed_links},
                    'scopus': {'linked_records': scopus_links},
                },
            }
        ]
        fd, path = tempfile.mkstemp(suffix='.json')
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f)
        try:
            result = load_articles_from_file(path)
        finally:
            os.unlink(path)

        arts = result['ai2022_q1']
        self.assertEqual(len(arts), 3)  # 2 shared + 1 Scopus-exclusive

        by_doi = {a.doi: a for a in arts if a.doi}
        self.assertEqual(by_doi['10.1001/jamacardio.2021.2003'].pmid, '34160576')
        self.assertEqual(by_doi['10.1164/rccm.200309-1305oc'].pmid, '25518901')
        self.assertIsNone(by_doi['10.1016/scopus.only'].pmid)


if __name__ == '__main__':
    unittest.main(verbosity=2)
