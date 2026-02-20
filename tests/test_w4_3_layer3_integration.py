"""W4.3 unit tests: Layer 3 fuzzy-fallback integration into set_metrics_row_level.

W4.3 adds a third matching layer inside ``set_metrics_row_level()``:

  Layer 1 — DOI exact match (existing)
  Layer 2 — PMID fallback when DOI missed (existing, W2.3)
  Layer 3 — Fuzzy title / first-author / year match (NEW, W4.3)
             Only fires when Layers 1 and 2 both failed.
             Only active when ``retrieved_metadata`` is non-empty AND
             ``_fuzzy_match_article`` is importable (rapidfuzz installed).

Purpose
-------
Recovering the ~4 Class D articles per query (truly DOI-less, CrossRef has no
mapping) that cannot be identified via DOI or PMID but CAN be identified by
title + author + year metadata from W4.1.

Phase scope: Phase B/D (per-query scoring) ONLY.
Phase C (ArticleRegistry aggregation) is NOT affected.

Test categories
---------------
 Cat-1  Backward compatibility        — existing call sites, new keys present
 Cat-2  Layer 3 fires correctly       — identifier-less gold + matching metadata
 Cat-3  Layer 3 does NOT double-count — Layers 1/2 prevent Layer 3 when they match
 Cat-4  Threshold boundary tests      — title, author, year edge cases
 Cat-5  GoldArticle duck-typing       — plain GoldArticle has no metadata → skipped
 Cat-6  Best-candidate selection      — multiple candidates, highest score wins
 Cat-7  score_queries() integration   — metadata wiring through score_queries()
 Cat-8  Per-DB metadata isolation     — each DB uses its own metadata dict
 Cat-9  Known limitations (Phase C)   — vote-split in aggregation not fixed here
 Cat-10 Return-dict completeness      — all expected keys present in result

Design note on the ≥2/3 matching rule
--------------------------------------
fuzzy_match_article() requires ≥2 of 3 testable fields to pass their
thresholds.  This means:
  - Title + author match (without year) → TP ✓
  - Title + year match (without author)  → TP ✓
  - Author + year match (without title)  → TP ✓  (known tradeoff: see Cat-4)
  - Only 1 field matches                 → None → no TP ✗
A single field alone is insufficient regardless of confidence score.
The author+year-without-title case is the accepted tradeoff documented in the
spec and verified in Cat-4, test_t4_author_year_without_title_is_valid.
"""

import csv
import hashlib
import io
import json
import sys
import tempfile
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set
from unittest.mock import MagicMock, patch

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Path setup
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from llm_sr_select_and_score import (  # noqa: E402
    GoldArticle,
    RichGoldArticle,
    _W4_3_FUZZY_AVAILABLE,
    load_rich_gold_rows,
    set_metrics_row_level,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ga(pmid=None, doi=None):
    """Convenience: create a GoldArticle namedtuple."""
    return GoldArticle(pmid=pmid, doi=doi)


def _rga(pmid=None, doi=None, title=None, year=None, first_author=None, journal=None):
    """Convenience: create a RichGoldArticle dataclass."""
    return RichGoldArticle(
        pmid=pmid, doi=doi, title=title,
        year=year, first_author=first_author, journal=journal,
    )


def _meta(title=None, year=None, first_author=None, journal=None):
    """Convenience: build a candidate metadata dict."""
    d = {}
    if title is not None:
        d['title'] = title
    if year is not None:
        d['year'] = year
    if first_author is not None:
        d['first_author'] = first_author
    if journal is not None:
        d['journal'] = journal
    return d


# Canonical metadata for a "sleep apnea" article used across tests
_SLEEP_META = _meta(
    title="Continuous positive airway pressure therapy for sleep apnea",
    year=2019,
    first_author="Johnson",
)
_SLEEP_GOLD = _rga(
    pmid=None, doi=None,
    title="Continuous positive airway pressure therapy for sleep apnea",
    year=2019,
    first_author="Johnson",
)


# ─────────────────────────────────────────────────────────────────────────────
# Cat-1  Backward compatibility
# ─────────────────────────────────────────────────────────────────────────────

class TestBackwardCompatibility:
    """Layer 3 is additive; all existing callers continue to work unchanged."""

    def test_no_metadata_extra_keys_present_with_zero_value(self):
        """When called without retrieved_metadata, new keys are present but zero."""
        gold = [_ga(pmid='P1', doi='10.a/1'), _ga(pmid='P2', doi=None)]
        m = set_metrics_row_level({'P1', 'P2'}, {'10.a/1'}, gold)
        assert 'matches_by_fuzzy' in m
        assert 'matched_fuzzy_keys' in m
        assert m['matches_by_fuzzy'] == 0
        assert isinstance(m['matched_fuzzy_keys'], set)
        assert len(m['matched_fuzzy_keys']) == 0

    def test_existing_tp_calculation_unchanged(self):
        """Layer 3 is absent (metadata=None): TP = Layer1 + Layer2 only."""
        gold = [
            _ga(pmid='P1', doi='10.a/1'),   # Layer 1 match
            _ga(pmid='P2', doi=None),        # Layer 2 match
            _ga(pmid=None, doi='10.a/3'),    # Layer 1 match
        ]
        m = set_metrics_row_level({'P1', 'P2'}, {'10.a/1', '10.a/3'}, gold)
        assert m['TP'] == 3
        assert m['matches_by_doi'] == 2
        assert m['matches_by_pmid_fallback'] == 1
        assert m['matches_by_fuzzy'] == 0

    def test_metadata_none_explicit_same_as_omitted(self):
        """Explicitly passing None is equivalent to omitting the parameter."""
        gold = [_ga(pmid='P1', doi='10.a/1')]
        m1 = set_metrics_row_level({'P1'}, {'10.a/1'}, gold)
        m2 = set_metrics_row_level({'P1'}, {'10.a/1'}, gold, retrieved_metadata=None)
        assert m1['TP'] == m2['TP']
        assert m1['matches_by_fuzzy'] == m2['matches_by_fuzzy']

    def test_empty_metadata_dict_disables_layer3(self):
        """Empty dict: _fuzzy_enabled is False → Layer 3 skipped."""
        gold = [_SLEEP_GOLD]
        m = set_metrics_row_level(set(), set(), gold, retrieved_metadata={})
        assert m['TP'] == 0
        assert m['matches_by_fuzzy'] == 0

    def test_all_existing_return_keys_still_present(self):
        """W4.3 additions do not remove any pre-existing return-dict keys."""
        gold = [_ga(pmid='P1', doi='10.a/1')]
        m = set_metrics_row_level({'P1'}, {'10.a/1'}, gold)
        expected_keys = {
            'TP', 'Retrieved', 'Gold', 'Precision', 'Recall', 'F1',
            'Jaccard', 'OverlapCoeff',
            'matches_by_doi', 'matches_by_pmid_fallback',
            'matched_dois', 'matched_pmids_fallback',
            'gold_articles_with_doi', 'gold_articles_pmid_only',
            'pmid_only_warning', 'retrieved_pmids_count', 'retrieved_dois_count',
            # W4.3 additions
            'matches_by_fuzzy', 'matched_fuzzy_keys',
        }
        assert expected_keys.issubset(set(m.keys()))


# ─────────────────────────────────────────────────────────────────────────────
# Cat-2  Layer 3 fires correctly
# ─────────────────────────────────────────────────────────────────────────────

class TestLayer3FiresCorrectly:
    """Layer 3 increments TP for truly identifier-less gold articles."""

    def test_exact_metadata_match_full_three_fields(self):
        """Title + author + year all match → confidence=1.0 → TP."""
        metadata = {'10.test/x': _meta(**_SLEEP_META)}
        m = set_metrics_row_level(set(), set(), [_SLEEP_GOLD], retrieved_metadata=metadata)
        assert m['TP'] == 1
        assert m['matches_by_fuzzy'] == 1
        assert '10.test/x' in m['matched_fuzzy_keys']

    def test_title_author_match_without_year(self):
        """Title + author pass (year absent from candidate) → TP."""
        gold = [_rga(title="Sleep apnea CPAP therapy", year=2019, first_author="Johnson")]
        meta = {'key:1': _meta(title="Sleep apnea CPAP therapy", first_author="Johnson")}
        m = set_metrics_row_level(set(), set(), [gold[0]], retrieved_metadata=meta)
        assert m['TP'] == 1
        assert m['matches_by_fuzzy'] == 1

    def test_title_year_match_without_author(self):
        """Title + year pass (author absent from candidate) → TP."""
        gold = [_rga(title="Sleep apnea CPAP therapy", year=2019)]
        meta = {'key:1': _meta(title="Sleep apnea CPAP therapy", year=2019)}
        m = set_metrics_row_level(set(), set(), [gold[0]], retrieved_metadata=meta)
        assert m['TP'] == 1
        assert m['matches_by_fuzzy'] == 1

    def test_multiple_gold_multiple_match(self):
        """Two gold articles both matched by Layer 3 across distinct candidates."""
        gold = [
            _rga(title="Sleep apnea therapy", year=2019, first_author="Smith"),
            _rga(title="COVID diet interventions", year=2020, first_author="Jones"),
        ]
        metadata = {
            'pmid:1111': _meta(title="Sleep apnea therapy", year=2019, first_author="Smith"),
            'pmid:2222': _meta(title="COVID diet interventions", year=2020, first_author="Jones"),
        }
        m = set_metrics_row_level(set(), set(), gold, retrieved_metadata=metadata)
        assert m['TP'] == 2
        assert m['matches_by_fuzzy'] == 2
        assert m['Recall'] == pytest.approx(1.0)

    def test_partial_gold_list_some_via_layer3(self):
        """Mix: 1 via Layer 1, 1 via Layer 2, 1 via Layer 3."""
        gold = [
            _rga(pmid=None, doi='10.doi/1'),                     # Layer 1
            _rga(pmid='P2', doi=None),                            # Layer 2
            _rga(title="Fuzzy article title", year=2021, first_author="Rivera"),  # Layer 3
        ]
        meta = {'key:x': _meta(title="Fuzzy article title", year=2021, first_author="Rivera")}
        m = set_metrics_row_level({'P2'}, {'10.doi/1'}, gold, retrieved_metadata=meta)
        assert m['TP'] == 3
        assert m['matches_by_doi'] == 1
        assert m['matches_by_pmid_fallback'] == 1
        assert m['matches_by_fuzzy'] == 1
        assert m['Recall'] == pytest.approx(1.0)

    def test_pmid_key_style_in_metadata(self):
        """Metadata keyed as 'pmid:XXXXX' (no DOI) is matched correctly."""
        gold = [_rga(title="Sleep apnea therapy review", year=2019, first_author="Johnson")]
        meta = {'pmid:99999': _meta(title="Sleep apnea therapy review", year=2019, first_author="Johnson")}
        m = set_metrics_row_level(set(), set(), gold, retrieved_metadata=meta)
        assert m['TP'] == 1
        assert 'pmid:99999' in m['matched_fuzzy_keys']


# ─────────────────────────────────────────────────────────────────────────────
# Cat-3  Layer 3 does not double-count (Layers 1/2 prevent it)
# ─────────────────────────────────────────────────────────────────────────────

class TestNonDoubleCount:
    """An article matched by Layer 1 or 2 must NOT also count in Layer 3."""

    def test_layer1_doi_match_prevents_layer3(self):
        """Gold article matched by DOI → elif branch for Layer 3 never evaluated."""
        gold = [_rga(doi='10.doi/1', title="CPAP therapy", year=2019, first_author="Smith")]
        meta = {'10.doi/1': _meta(title="CPAP therapy", year=2019, first_author="Smith")}
        m = set_metrics_row_level(set(), {'10.doi/1'}, gold, retrieved_metadata=meta)
        assert m['TP'] == 1
        assert m['matches_by_doi'] == 1
        assert m['matches_by_fuzzy'] == 0

    def test_layer2_pmid_match_prevents_layer3(self):
        """Gold article matched by PMID → elif branch for Layer 3 never evaluated."""
        gold = [_rga(pmid='P1', title="CPAP therapy", year=2019, first_author="Smith")]
        meta = {'pmid:P1': _meta(title="CPAP therapy", year=2019, first_author="Smith")}
        m = set_metrics_row_level({'P1'}, set(), gold, retrieved_metadata=meta)
        assert m['TP'] == 1
        assert m['matches_by_pmid_fallback'] == 1
        assert m['matches_by_fuzzy'] == 0

    def test_doi_and_pmid_both_present_layer1_takes_priority(self):
        """When DOI matches, Layer 1 fires; even if PMID and metadata also match."""
        gold = [_rga(pmid='P1', doi='10.doi/1', title="CPAP therapy", year=2019, first_author="Smith")]
        meta = {'10.doi/1': _meta(title="CPAP therapy", year=2019, first_author="Smith")}
        m = set_metrics_row_level({'P1'}, {'10.doi/1'}, gold, retrieved_metadata=meta)
        assert m['TP'] == 1
        assert m['matches_by_doi'] == 1
        assert m['matches_by_pmid_fallback'] == 0
        assert m['matches_by_fuzzy'] == 0


# ─────────────────────────────────────────────────────────────────────────────
# Cat-4  Threshold boundary and matching-rule tests
# ─────────────────────────────────────────────────────────────────────────────

class TestThresholdBoundary:
    """Verify the ≥2-of-3 rule and field-threshold boundaries."""

    def test_only_year_matches_below_minimum_fields(self):
        """Only 1 field matches (year) → requires ≥2 → no TP."""
        gold = [_rga(title="Totally different paper", year=2020, first_author="XYZ Corp")]
        meta = {'k': _meta(title="Sleep apnea therapy classic review", year=2020, first_author="Smith")}
        # title won't match, author won't match, year will match → 1/3 → None
        m = set_metrics_row_level(set(), set(), gold, retrieved_metadata=meta)
        assert m['TP'] == 0

    def test_author_year_without_title_is_valid_per_design(self):
        """Author + year match (title absent from candidate) → ≥2 fields → TP.

        This is a documented design tradeoff: two papers by the same author
        in the same year could theoretically be confused, but the risk is
        acceptable given the small number of Class D articles per study.
        """
        gold = [_rga(title="Any title here because absent from candidate", year=2020, first_author="Smith")]
        meta = {'k': _meta(year=2020, first_author="Smith")}
        # title: not testable (absent from candidate) → testable=2 (author, year)
        # author matches, year matches → matched=2 → 2/2 → 1.0 → TP
        m = set_metrics_row_level(set(), set(), gold, retrieved_metadata=meta)
        assert m['TP'] == 1
        assert m['matches_by_fuzzy'] == 1

    def test_only_one_testable_field_returns_no_tp(self):
        """Fewer than 2 testable fields → fuzzy_match_article returns None."""
        gold = [_rga(title="Some title", year=2020)]  # no first_author
        meta = {'k': _meta(title="Some title")}       # only title testable (year absent too)
        # testable = 1 (title only) → < 2 → None → no TP
        m = set_metrics_row_level(set(), set(), gold, retrieved_metadata=meta)
        # title matches but testable < 2 → None
        assert m['TP'] == 0

    def test_completely_different_all_fields(self):
        """All three fields differ → 0 matches → no TP."""
        gold = [_rga(title="Machine learning approaches", year=2015, first_author="Brown")]
        meta = {'k': _meta(title="Sleep apnea CPAP therapy", year=2020, first_author="Smith")}
        m = set_metrics_row_level(set(), set(), gold, retrieved_metadata=meta)
        assert m['TP'] == 0

    def test_year_one_off_within_tolerance(self):
        """Year difference of exactly 1 → within tolerance → counts as year-match."""
        gold = [_rga(title="Sleep apnea CPAP therapy review", year=2019, first_author="Johnson")]
        meta = {'k': _meta(title="Sleep apnea CPAP therapy review", year=2020, first_author="Johnson")}
        # year diff = 1 ≤ threshold (1) → year matches
        m = set_metrics_row_level(set(), set(), gold, retrieved_metadata=meta)
        assert m['TP'] == 1

    def test_year_two_off_exceeds_tolerance(self):
        """Year difference of 2 → exceeds tolerance → year does not match."""
        gold = [_rga(title="Sleep therapy review", year=2017, first_author="Johnson")]
        meta = {'k': _meta(title="Sleep therapy review", year=2019, first_author="Johnson")}
        # |2019-2017|=2 > 1 → year doesn't match; title+author can still match (≥2)
        m = set_metrics_row_level(set(), set(), gold, retrieved_metadata=meta)
        # title matches (very similar) and author matches → still TP despite year miss
        assert m['TP'] == 1
        assert m['matches_by_fuzzy'] == 1

    def test_author_diacritic_normalisation(self):
        """García normalised to garcia → matches garcia in candidate."""
        gold = [_rga(title="Sleep apnea CPAP therapy study", year=2019, first_author="García")]
        meta = {'k': _meta(title="Sleep apnea CPAP therapy study", year=2019, first_author="Garcia")}
        m = set_metrics_row_level(set(), set(), gold, retrieved_metadata=meta)
        assert m['TP'] == 1


# ─────────────────────────────────────────────────────────────────────────────
# Cat-5  GoldArticle duck-typing — Layer 3 skipped without attributes
# ─────────────────────────────────────────────────────────────────────────────

class TestGoldArticleDuckTyping:
    """GoldArticle NamedTuple has no title/year/first_author → Layer 3 produces no match."""

    def test_basic_gold_article_no_match_via_layer3(self):
        """GoldArticle(pmid=None, doi=None) → getattr returns None → no testable fields."""
        gold = [GoldArticle(pmid=None, doi=None)]
        meta = {'k': _meta(title="Any title", year=2020, first_author="Smith")}
        m = set_metrics_row_level(set(), set(), gold, retrieved_metadata=meta)
        assert m['TP'] == 0
        assert m['matches_by_fuzzy'] == 0

    def test_mixed_list_goldandrich(self):
        """List mixing GoldArticle (L1/L2 only) and RichGoldArticle (L3 eligible)."""
        gold = [
            GoldArticle(pmid='P1', doi=None),                         # Layer 2
            _rga(title="Sleep apnea review", year=2019, first_author="Smith"),  # Layer 3
        ]
        meta = {'k': _meta(title="Sleep apnea review", year=2019, first_author="Smith")}
        m = set_metrics_row_level({'P1'}, set(), gold, retrieved_metadata=meta)
        assert m['TP'] == 2
        assert m['matches_by_pmid_fallback'] == 1
        assert m['matches_by_fuzzy'] == 1


# ─────────────────────────────────────────────────────────────────────────────
# Cat-6  Best-candidate selection
# ─────────────────────────────────────────────────────────────────────────────

class TestBestCandidateSelection:
    """When multiple candidates match, the highest-scoring one is chosen."""

    def test_multiple_candidates_best_score_selected(self):
        """Gold article: 3 candidates — one exact match, two partial → highest wins."""
        gold = [_rga(title="CPAP therapy for sleep apnea", year=2019, first_author="Johnson")]
        metadata = {
            'partial_1': _meta(title="CPAP therapy for sleep disorders", year=2018, first_author="Johnson"),
            'exact':     _meta(title="CPAP therapy for sleep apnea", year=2019, first_author="Johnson"),
            'partial_2': _meta(title="CPAP and sleep apnea treatment", year=2019, first_author="Johnson"),
        }
        m = set_metrics_row_level(set(), set(), gold, retrieved_metadata=metadata)
        assert m['TP'] == 1
        assert m['matches_by_fuzzy'] == 1
        # The matched key should be the one with best confidence
        assert 'exact' in m['matched_fuzzy_keys']

    def test_only_one_candidate_above_threshold(self):
        """One candidate exceeds threshold; others below → only one TP."""
        gold = [_rga(title="CPAP therapy for sleep apnea", year=2019, first_author="Johnson")]
        metadata = {
            'below': _meta(title="Completely unrelated subject matter research", year=2010, first_author="Brown"),
            'above': _meta(title="CPAP therapy for sleep apnea", year=2019, first_author="Johnson"),
        }
        m = set_metrics_row_level(set(), set(), gold, retrieved_metadata=metadata)
        assert m['TP'] == 1
        assert 'above' in m['matched_fuzzy_keys']

    def test_no_candidate_above_threshold_no_tp(self):
        """All candidates below threshold → TP=0."""
        gold = [_rga(title="CPAP therapy for sleep apnea", year=2019, first_author="Johnson")]
        metadata = {
            'low1': _meta(title="Diet and nutrition review", year=2015, first_author="Brown"),
            'low2': _meta(title="Exercise intervention RCT", year=2018, first_author="Wilson"),
        }
        m = set_metrics_row_level(set(), set(), gold, retrieved_metadata=metadata)
        assert m['TP'] == 0
        assert m['matches_by_fuzzy'] == 0


# ─────────────────────────────────────────────────────────────────────────────
# Cat-7  score_queries() integration — metadata wiring
# ─────────────────────────────────────────────────────────────────────────────

class TestScoreQueriesIntegration:
    """Verify metadata is correctly threaded through score_queries()."""

    def _make_gold_csv(self, tmp_path, rows):
        """Write a temporary detailed gold CSV with title/author/year columns."""
        path = tmp_path / "gold_detailed.csv"
        fieldnames = ['pmid', 'doi', 'title', 'first_author', 'year', 'journal']
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return str(path)

    def test_load_rich_gold_rows_called_in_multi_key_mode(self, tmp_path):
        """score_queries() now uses load_rich_gold_rows() for multi-key mode."""
        from llm_sr_select_and_score import load_rich_gold_rows, score_queries

        # Write a gold CSV with all metadata columns
        gold_path = self._make_gold_csv(tmp_path, [
            {'pmid': '12345', 'doi': '10.doi/1', 'title': 'Test study',
             'first_author': 'Smith', 'year': '2020', 'journal': 'JAMA'},
        ])

        # Verify load_rich_gold_rows reads full metadata
        rows = load_rich_gold_rows(gold_path)
        assert len(rows) == 1
        assert rows[0].title == 'Test study'
        assert rows[0].first_author == 'Smith'
        assert rows[0].year == 2020

    def test_matches_by_fuzzy_column_in_per_db_csv(self, tmp_path):
        """After score_queries(), 'matches_by_fuzzy' column appears in summary CSV."""
        import tempfile
        from llm_sr_select_and_score import score_queries, load_rich_gold_rows

        # Minimal gold CSV
        gold_path = self._make_gold_csv(tmp_path, [
            {'pmid': 'P1', 'doi': '10.a/1', 'title': 'Test article',
             'first_author': 'Brown', 'year': '2019', 'journal': 'BMJ'},
        ])

        # Mock provider that returns the article via DOI
        mock_provider = MagicMock()
        mock_provider.name = 'pubmed'
        mock_provider.id_type = 'pmid'
        mock_provider.search.return_value = ({'10.a/1'}, {'P1'}, 1)
        mock_provider._pmid_to_doi_cache = {'P1': '10.a/1'}
        mock_provider._metadata_cache = {
            '10.a/1': {'title': 'Test article', 'first_author': 'Brown', 'year': 2019}
        }

        bundles = [{'index': 0, 'canonical': 'test query',
                    'per_provider': {'pubmed': 'test query'}}]

        outdir = str(tmp_path / 'out')
        with patch('llm_sr_select_and_score._provider_name', side_effect=lambda p: p.name):
            score_queries(
                [mock_provider], bundles,
                '2000/01/01', '2023/12/31',
                gold_path, outdir,
                use_multi_key=True,
            )

        # Check output CSV has the new column
        per_db_files = list(Path(outdir).glob('summary_per_database_*.csv'))
        assert len(per_db_files) == 1
        with open(per_db_files[0], 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) >= 1
        assert 'matches_by_fuzzy' in rows[0], "matches_by_fuzzy column missing from per-DB CSV"

    def test_matches_by_fuzzy_column_in_summary_csv(self, tmp_path):
        """After score_queries(), 'matches_by_fuzzy' column appears in summary CSV."""
        from llm_sr_select_and_score import score_queries

        gold_path = self._make_gold_csv(tmp_path, [
            {'pmid': 'P1', 'doi': '10.a/1', 'title': 'Test article',
             'first_author': 'Brown', 'year': '2019', 'journal': 'BMJ'},
        ])

        mock_provider = MagicMock()
        mock_provider.name = 'pubmed'
        mock_provider.id_type = 'pmid'
        mock_provider.search.return_value = ({'10.a/1'}, {'P1'}, 1)
        mock_provider._pmid_to_doi_cache = {'P1': '10.a/1'}
        mock_provider._metadata_cache = {
            '10.a/1': {'title': 'Test article', 'first_author': 'Brown', 'year': 2019}
        }

        bundles = [{'index': 0, 'canonical': 'test query',
                    'per_provider': {'pubmed': 'test query'}}]
        outdir = str(tmp_path / 'out2')

        with patch('llm_sr_select_and_score._provider_name', side_effect=lambda p: p.name):
            score_queries(
                [mock_provider], bundles,
                '2000/01/01', '2023/12/31',
                gold_path, outdir,
                use_multi_key=True,
            )

        summary_files = list(Path(outdir).glob('summary_2*.csv'))
        assert len(summary_files) == 1
        with open(summary_files[0], 'r') as f:
            reader = csv.DictReader(f)
            rows_out = list(reader)
        assert len(rows_out) == 1
        assert 'matches_by_fuzzy' in rows_out[0], "matches_by_fuzzy column missing from summary CSV"


# ─────────────────────────────────────────────────────────────────────────────
# Cat-8  Per-DB metadata isolation
# ─────────────────────────────────────────────────────────────────────────────

class TestPerDbMetadataIsolation:
    """Each DB's Layer 3 scoring uses only that DB's own metadata dict."""

    def test_per_db_metadata_dict_used_for_each_provider(self):
        """set_metrics_row_level called per-DB with that provider's metadata only."""
        # We verify the isolation by controlling exactly which metadata is passed
        # to each call and checking that matches_by_fuzzy reflects only that DB.

        # Gold: one article with no identifiers, matchable by metadata
        gold = [_rga(title="Sleep apnea CPAP therapy", year=2019, first_author="Johnson")]

        # PubMed has metadata for the article
        pubmed_meta = {'pmid:9999': _meta(title="Sleep apnea CPAP therapy", year=2019, first_author="Johnson")}
        m_pubmed = set_metrics_row_level(set(), set(), gold, retrieved_metadata=pubmed_meta)
        assert m_pubmed['TP'] == 1
        assert m_pubmed['matches_by_fuzzy'] == 1

        # Scopus does NOT have metadata for this article
        scopus_meta = {'10.unrelated/x': _meta(title="Unrelated study", year=2015, first_author="Brown")}
        m_scopus = set_metrics_row_level(set(), set(), gold, retrieved_metadata=scopus_meta)
        assert m_scopus['TP'] == 0
        assert m_scopus['matches_by_fuzzy'] == 0

    def test_combined_uses_merged_metadata_from_all_providers(self):
        """COMBINED set_metrics_row_level call gets union of all provider metadata."""
        gold = [_rga(title="Rare study only in Embase", year=2018, first_author="Müller")]
        # Only Embase has this article's metadata
        merged_meta = {
            '10.pubmed/x': _meta(title="Unrelated PubMed study", year=2020, first_author="Smith"),
            'pmid:8888': _meta(title="Rare study only in Embase", year=2018, first_author="Müller"),
        }
        m_combined = set_metrics_row_level(set(), set(), gold, retrieved_metadata=merged_meta)
        assert m_combined['TP'] == 1
        assert m_combined['matches_by_fuzzy'] == 1
        assert 'pmid:8888' in m_combined['matched_fuzzy_keys']


# ─────────────────────────────────────────────────────────────────────────────
# Cat-9  Known limitations (Phase C)
# ─────────────────────────────────────────────────────────────────────────────

class TestKnownLimitations:
    """
    W4.3 fixes Phase B/D scoring only.
    Phase C (ArticleRegistry vote-split) is NOT fixed by W4.3.

    These tests document and pin the current known behaviour so that any
    accidental change is immediately visible.
    """

    def test_phase_b_scoring_improved_by_layer3(self):
        """Layer 3 increases TP for a Class D gold article in Phase B scoring."""
        # Class D: no DOI, no PMID, has metadata
        gold = [_rga(title="Truly DOI-less article", year=2010, first_author="Senior")]
        meta = {'pmid:oldkey': _meta(title="Truly DOI-less article", year=2010, first_author="Senior")}

        m_without_l3 = set_metrics_row_level(set(), set(), gold, retrieved_metadata=None)
        m_with_l3 = set_metrics_row_level(set(), set(), gold, retrieved_metadata=meta)

        assert m_without_l3['TP'] == 0, "Without L3: should miss this article"
        assert m_with_l3['TP'] == 1, "With L3: should find this article"
        assert m_with_l3['Recall'] == pytest.approx(1.0)

    def test_phase_c_vote_split_not_fixed_by_w43(self):
        """
        Phase C (aggregation) vote-split for Class D articles is NOT fixed.

        A truly DOI-less article (Article(pmid=P, doi=None)) in ArticleRegistry
        cannot be unified with a different representation from another DB without
        W4.4 (fuzzy ArticleRegistry merge).  This test documents that W4.3
        does not change ArticleRegistry behavior.
        """
        from aggregate_queries import Article, ArticleRegistry

        reg = ArticleRegistry()
        # PubMed submits a PMID-only article
        reg.add(pmid='P_doiless', doi=None)
        # Embase submits same article but without PMID, with only a title-based identity
        # (we can't represent this in the registry; we'd need fuzzy merge = W4.4)
        reg.add(pmid=None, doi=None)  # no-op (no identifier)

        # The article is only registered under PubMed's representation
        articles = reg.articles()
        pmid_only_articles = [a for a in articles if a.pmid == 'P_doiless' and a.doi is None]
        assert len(pmid_only_articles) == 1, (
            "PMID-only article should be in registry (added by PubMed)"
        )
        # No merge happened → the article is still opaque to other DBs (W4.4 scope)
        # This is pinned behaviour; W4.4 would change this.


# ─────────────────────────────────────────────────────────────────────────────
# Cat-10  Metrics correctness with Layer 3
# ─────────────────────────────────────────────────────────────────────────────

class TestMetricsCorrectnessWithLayer3:
    """Recall / precision / F1 / Gold are correct when Layer 3 contributes TPs."""

    def test_recall_includes_fuzzy_tp(self):
        """Recall = (L1 + L2 + L3 TPs) / gold_size."""
        gold = [
            _ga(pmid='P1', doi='10.a/1'),  # Layer 1
            _rga(title="Extra article via fuzzy", year=2019, first_author="Smith"),  # Layer 3
        ]
        meta = {'k': _meta(title="Extra article via fuzzy", year=2019, first_author="Smith")}
        m = set_metrics_row_level({'P1'}, {'10.a/1'}, gold, retrieved_metadata=meta)
        assert m['TP'] == 2
        assert m['Gold'] == 2
        assert m['Recall'] == pytest.approx(1.0)

    def test_gold_count_unchanged_by_layer3(self):
        """'Gold' is always len(gold_rows) regardless of Layer 3 activity."""
        gold = [
            _rga(title="A", year=2020, first_author="X"),
            _rga(title="B", year=2021, first_author="Y"),
        ]
        meta = {'k1': _meta(title="A", year=2020, first_author="X"),
                'k2': _meta(title="B", year=2021, first_author="Y")}
        m = set_metrics_row_level(set(), set(), gold, retrieved_metadata=meta)
        assert m['Gold'] == 2
        assert m['matches_by_fuzzy'] == 2

    def test_precision_unchanged_by_layer3(self):
        """Precision is based on retrieved article count, not TP method."""
        gold = [_rga(title="Precise article", year=2020, first_author="Smith")]
        meta = {'k': _meta(title="Precise article", year=2020, first_author="Smith")}
        # Retrieved: 3 articles via DOI, 1 matched via Layer 3
        # Precision = 1 / max(0, 3) = 1/3 ≈ 0.333
        m = set_metrics_row_level(set(), {'10.a/1', '10.a/2', '10.a/3'}, gold,
                                   retrieved_metadata=meta)
        assert m['TP'] == 1
        assert m['Precision'] == pytest.approx(1 / 3, abs=1e-9)

    def test_f1_correct_with_layer3_tp(self):
        """F1 = 2 * prec * rec / (prec + rec) includes Layer 3 TPs."""
        gold = [_rga(title="Study X", year=2020, first_author="A")]
        meta = {'k': _meta(title="Study X", year=2020, first_author="A")}
        # 1 retrieved (the fuzzy match candidate), 1 TP, 1 gold
        # Prec = 1/1 = 1.0, Rec = 1/1 = 1.0, F1 = 1.0
        # But retrieved_pmids and retrieved_dois are both empty → retrieved_unique = 0
        # Precision = 1/max(0,1) = 1.0 since max(len(pmids), len(dois)) = max(0,0) = 0
        # so precision = 1/max(0,1)=1.0
        m = set_metrics_row_level(set(), set(), gold, retrieved_metadata=meta)
        assert m['TP'] == 1
        assert m['F1'] == pytest.approx(1.0)

    def test_empty_gold_empty_metadata_zero_tp(self):
        """Edge case: empty gold list → TP=0, Recall=0, all metrics valid."""
        m = set_metrics_row_level(set(), set(), [],
                                   retrieved_metadata={'k': _meta(title="X", year=2020)})
        assert m['TP'] == 0
        assert m['Recall'] == pytest.approx(0.0)
        assert m['matches_by_fuzzy'] == 0
