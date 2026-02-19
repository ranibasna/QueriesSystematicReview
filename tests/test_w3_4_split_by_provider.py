"""W3.4 Tests: Per-Provider Aggregation Pool Mode (split-by-provider)

Task summary
------------
W3.4 adds a ``--split-by-provider`` flag to ``aggregate_queries.py``.  When
active, each database provider in ``provider_details`` (pubmed, scopus, wos,
embase) becomes its own aggregation pool keyed as ``"{provider}_{query}"``.
This transforms query-by-query aggregation from:

    • "1 combined API pool per query"  → ``consensus_k2`` always empty (1 pool)

to:

    • "1 pool per database per query" → ``consensus_k2`` = articles found by
      ≥2 databases for this query  (semantically correct cross-database confirmation)

Problem addressed
-----------------
After W3 (EmbaseLocalProvider integrated into scoring), a query-by-query
``details_*.json`` contains ONE entry whose ``provider_details`` bundles
PubMed + Scopus + WOS + Embase into a single combined pool.  Without
``--split-by-provider`` the combined pool is the only pool → consensus_k2
requires ≥2 pools but there is only 1 → always returns empty set.  All
vote-based strategies collapse to the full union.

Test coverage
-------------
  Cat-1  Bug fix: load_pmids_from_file def was missing — legacy load_all() works
  Cat-2  _articles_from_provider_details_per_source edge cases
  Cat-3  load_articles_from_file_split forward/fallback behaviour
  Cat-4  effective_topk correctness in split mode
  Cat-5  Strategy semantics in split mode (consensus, union, two-stage)
  Cat-6  Normal mode is unchanged by the new flag
  Cat-7  --split-by-provider without --multi-key emits [WARN]
  Cat-8  End-to-end aggregate_queries.main() in split mode
  Cat-9  Known limitation (W4.4 scope): PMID-only vs PMID+DOI cross-provider
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import tempfile
from collections import Counter
from io import StringIO
from pathlib import Path
from typing import Dict, Set
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from aggregate_queries import (
    Article,
    ArticleRegistry,
    _articles_from_provider_details_per_source,
    consensus_k_articles,
    load_all,
    load_all_articles,
    load_all_articles_split,
    load_articles_from_file,
    load_articles_from_file_split,
    load_pmids_from_file,
    precision_gated_union_articles,
    time_stratified_hybrid_articles,
    two_stage_screen_articles,
    weighted_vote_articles,
)


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────

def _details_list(bundles: list[dict]) -> list[dict]:
    """Minimal details_*.json list structure as written by score_queries."""
    result = []
    for b in bundles:
        result.append(
            {
                "query": b["query"],
                "results_count": 0,
                "TP": 0,
                "gold_size": 1,
                "recall": 0.0,
                "NNR_proxy": 0.0,
                "retrieved_pmids": [],
                "retrieved_dois": [],
                "tp_pmids": [],
                "provider_details": b.get("provider_details", {}),
                "providers_included": b.get("providers_included", []),
            }
        )
    return result


def _write_details(path: Path, bundles: list[dict]) -> Path:
    path.write_text(json.dumps(_details_list(bundles)), encoding="utf-8")
    return path


def _pd_block(pmid_doi_pairs: list[tuple[str | None, str | None]]) -> dict:
    """Build a minimal provider_details entry with linked_records."""
    return {
        "linked_records": [{"pmid": p, "doi": d} for p, d in pmid_doi_pairs],
        "id_type": "pmid",
        "results_count": len(pmid_doi_pairs),
    }


# ════════════════════════════════════════════════════════════════════════════
# Category 1 — Bug fix: load_pmids_from_file was missing its def header
# ════════════════════════════════════════════════════════════════════════════

def test_load_pmids_from_file_is_callable():
    """load_pmids_from_file must exist as a callable (missing def header was removed)."""
    assert callable(load_pmids_from_file), (
        "load_pmids_from_file is not callable — the def header is still missing"
    )


def test_load_all_legacy_pmid_path_works(tmp_path):
    """load_all() (the legacy PMID-only path) must not raise NameError."""
    f = tmp_path / "details_legacy.json"
    f.write_text(json.dumps([
        {"query": "q1", "retrieved_pmids": ["111", "222"]},
        {"query": "q2", "retrieved_pmids": ["333"]},
    ]))
    result = load_all([str(f)])
    assert "q1" in result and "q2" in result
    assert result["q1"] == {"111", "222"}
    assert result["q2"] == {"333"}


def test_load_pmids_from_file_all_formats(tmp_path):
    """load_pmids_from_file handles all three JSON schemas."""
    # Format 1: list
    f1 = tmp_path / "list.json"
    f1.write_text(json.dumps([{"query": "q1", "retrieved_pmids": ["1", "2"]}]))
    r1 = load_pmids_from_file(str(f1))
    assert r1 == {"q1": {"1", "2"}}

    # Format 2: dict-of-entries (old details_*.json dict form)
    f2 = tmp_path / "dict.json"
    f2.write_text(json.dumps({"abc": {"query": "q2", "pmids": ["3", "4"]}}))
    r2 = load_pmids_from_file(str(f2))
    assert r2 == {"q2": {"3", "4"}}

    # Format 3: sealed (single object with retrieved_pmids at top level)
    f3 = tmp_path / "sealed.json"
    f3.write_text(json.dumps({"query": "q3", "retrieved_pmids": ["5"]}))
    r3 = load_pmids_from_file(str(f3))
    assert r3 == {"q3": {"5"}}


# ════════════════════════════════════════════════════════════════════════════
# Category 2 — _articles_from_provider_details_per_source edge cases
# ════════════════════════════════════════════════════════════════════════════

def test_per_source_empty_provider_details():
    """Empty provider_details → empty dict returned."""
    result = _articles_from_provider_details_per_source({}, "Q1")
    assert result == {}


def test_per_source_error_provider_skipped():
    """Provider entries with an 'error' key are excluded from per-source pools."""
    pd = {
        "pubmed": _pd_block([("1", "10.a/1")]),
        "wos": {"error": "API timeout", "results_count": 0},
    }
    result = _articles_from_provider_details_per_source(pd, "Q1")
    assert "pubmed_Q1" in result
    assert "wos_Q1" not in result, "Error providers must be excluded"


def test_per_source_provider_with_empty_linked_records_excluded():
    """Provider whose linked_records is an empty list is not included in result."""
    pd = {
        "pubmed": {"linked_records": []},          # empty → no articles
        "embase": _pd_block([("2", "10.emb/2")]),  # has articles
    }
    result = _articles_from_provider_details_per_source(pd, "Q1")
    # pubmed yields 0 articles → should be absent
    assert "pubmed_Q1" not in result, "Empty-linked_records provider must be excluded"
    assert "embase_Q1" in result


def test_per_source_none_identifiers_not_added():
    """Records where both pmid and doi are None/empty are silently skipped."""
    pd = {
        "pubmed": {
            "linked_records": [
                {"pmid": None, "doi": None},   # invalid
                {"pmid": "10", "doi": "10.x"},  # valid
            ]
        }
    }
    result = _articles_from_provider_details_per_source(pd, "Q_x")
    pool = result.get("pubmed_Q_x", set())
    assert len(pool) == 1
    art = next(iter(pool))
    assert art.pmid == "10"


def test_per_source_key_contains_provider_and_query():
    """Pool keys are '{provider}_{query}', not just '{provider}'."""
    pd = {"scopus": _pd_block([(None, "10.sc/1")])}
    r1 = _articles_from_provider_details_per_source(pd, "Q1 text with spaces")
    r2 = _articles_from_provider_details_per_source(pd, "Q2 different query")
    # Different queries → different keys → pools don't collide
    assert set(r1.keys()) != set(r2.keys())
    assert "scopus_Q1 text with spaces" in r1
    assert "scopus_Q2 different query" in r2


# ════════════════════════════════════════════════════════════════════════════
# Category 3 — load_articles_from_file_split forward/fallback behaviour
# ════════════════════════════════════════════════════════════════════════════

def test_split_non_list_json_delegates_to_standard(tmp_path):
    """
    Non-list JSON schemas (sealed, embase import, old dict-format) fall through
    to load_articles_from_file — the result is the same as the standard loader.
    """
    # Use a simple list that load_articles_from_file can read as one combined pool
    data = [{"query": "q1", "retrieved_pmids": ["1"], "retrieved_dois": [],
             "provider_details": {}}]
    f = tmp_path / "details.json"
    f.write_text(json.dumps(data))

    standard = load_articles_from_file(str(f))
    split = load_articles_from_file_split(str(f))

    # Both should return the same pools when there are no linked_records to split
    assert set(standard.keys()) == set(split.keys()), (
        f"Standard: {list(standard.keys())}  Split (fallback): {list(split.keys())}"
    )


def test_split_entry_without_linked_records_falls_back_to_combined(tmp_path):
    """
    A list entry whose provider_details lacks linked_records (legacy format)
    falls back to the combined-pool path (same as load_articles_from_file).
    """
    # provider_details without linked_records (legacy structure)
    data = _details_list([{
        "query": "legacy_q",
        "provider_details": {
            "pubmed": {"retrieved_ids": ["1", "2"], "results_count": 2},
        },
        "retrieved_pmids": ["1", "2"],
        "retrieved_dois": [],
    }])
    f = tmp_path / "legacy.json"
    f.write_text(json.dumps(data))

    standard = load_articles_from_file(str(f))
    split = load_articles_from_file_split(str(f))

    # Fallback: split yields same combined pool as standard
    assert set(standard.keys()) == set(split.keys())


def test_split_multiple_queries_produces_n_providers_times_n_queries(tmp_path):
    """
    With 2 queries and 2 providers each, split mode returns 2×2 = 4 pools.
    """
    pd = {
        "pubmed": _pd_block([("1", "10.a/1")]),
        "embase": _pd_block([("2", "10.b/2")]),
    }
    data = _details_list([
        {"query": "q1", "provider_details": pd, "providers_included": ["pubmed", "embase"]},
        {"query": "q2", "provider_details": pd, "providers_included": ["pubmed", "embase"]},
    ])
    f = tmp_path / "two_queries.json"
    f.write_text(json.dumps(data))

    split = load_articles_from_file_split(str(f))
    assert len(split) == 4, f"Expected 4 pools (2 queries × 2 providers): {list(split.keys())}"
    assert "pubmed_q1" in split
    assert "embase_q1" in split
    assert "pubmed_q2" in split
    assert "embase_q2" in split


def test_split_and_standard_agree_on_combined_article_set(tmp_path):
    """
    The union of all split pools equals the combined set from load_articles_from_file.
    """
    pd = {
        "pubmed":  _pd_block([("1", "10.pm/1"), ("2", None)]),
        "scopus":  _pd_block([(None, "10.sc/1")]),
        "embase":  _pd_block([("3", "10.emb/3")]),
    }
    data = _details_list([{
        "query": "q",
        "provider_details": pd,
        "providers_included": ["pubmed", "scopus", "embase"],
    }])
    f = tmp_path / "details.json"
    f.write_text(json.dumps(data))

    standard = load_articles_from_file(str(f))
    split = load_articles_from_file_split(str(f))

    combined_split = set().union(*split.values())
    combined_standard = set().union(*standard.values())

    # After ArticleRegistry merging, the union of all split pools == combined pool.
    # (DOI 10.sc/1 appears in scopus only; 10.pm/1 in pubmed only; etc.)
    assert combined_split == combined_standard, (
        f"Union of split pools differs from combined pool.\n"
        f"  Split union: {sorted(str(a) for a in combined_split)}\n"
        f"  Standard:    {sorted(str(a) for a in combined_standard)}"
    )


# ════════════════════════════════════════════════════════════════════════════
# Category 4 — effective_topk correctness
# ════════════════════════════════════════════════════════════════════════════

def test_effective_topk_uses_max_of_pools_and_topk_arg():
    """
    When split mode has more pools than topk, effective_topk = len(pools).
    This ensures all database providers are included in consensus.
    """
    # 4 providers, default topk=3 → effective_topk must be 4
    art_A = Article(pmid="A", doi="10.a/A")   # in 3 of 4 pools
    art_B = Article(pmid="B", doi="10.b/B")   # in exactly 2 pools → meets k=2
    art_C = Article(pmid="C", doi="10.c/C")   # in exactly 1 pool  → fails k=2

    pools = {
        "pubmed_Q1":  {art_A, art_B},
        "scopus_Q1":  {art_A, art_B},
        "wos_Q1":     {art_A},
        "embase_Q1":  {art_C},  # would be skipped with topk=3
    }

    # With topk=3 (first 3 pools from ordered dict):
    #   pubmed(A,B) + scopus(A,B) + wos(A) → A=3, B=2, C=0
    #   → A and B included
    result_topk3 = consensus_k_articles(pools, topk=3, k=2)
    assert art_B in result_topk3  # B survives with topk=3

    # With effective_topk = max(4, 3) = 4 (all providers):
    #   Same as above plus embase(C) → C=1, still fails k=2
    result_effective = consensus_k_articles(pools, topk=4, k=2)
    assert art_A in result_effective
    assert art_B in result_effective
    assert art_C not in result_effective, "C is in only 1 pool, should not pass k=2"


def test_effective_topk_when_fewer_pools_than_topk():
    """
    When split mode has fewer pools than topk, consensus uses all available pools.
    (topk > len(items) means all items are considered.)
    """
    art_A = Article(pmid="1", doi="10.a/1")
    art_B = Article(pmid="2", doi="10.b/2")
    pools = {
        "pubmed_Q1": {art_A, art_B},
        "embase_Q1": {art_A},
    }
    # topk=4 but only 2 pools → items[:4] = both pools
    result = consensus_k_articles(pools, topk=4, k=2)
    assert art_A in result       # in 2 pools → k=2 ✓
    assert art_B not in result   # in 1 pool  → k=1 < 2 ✗


# ════════════════════════════════════════════════════════════════════════════
# Category 5 — Strategy semantics in split mode
# ════════════════════════════════════════════════════════════════════════════

def test_consensus_k2_finds_cross_database_articles():
    """
    consensus_k2 with 4 provider pools = articles retrieved by ≥2 databases.
    Articles in only 1 database are excluded.
    """
    solo_pubmed   = Article(pmid="solo_pm",    doi="10.solo/pm")
    cross_pm_sc   = Article(pmid="cross1",     doi="10.cross/1")  # PubMed + Scopus
    cross_wos_emb = Article(pmid=None,          doi="10.cross/2")  # WOS + Embase
    in_all_four   = Article(pmid="all4",        doi="10.all/4")    # all 4 databases

    pools = {
        "pubmed_Q1":  {solo_pubmed, cross_pm_sc, in_all_four},
        "scopus_Q1":  {cross_pm_sc, in_all_four},
        "wos_Q1":     {cross_wos_emb, in_all_four},
        "embase_Q1":  {cross_wos_emb, in_all_four},
    }

    result = consensus_k_articles(pools, topk=4, k=2)

    assert cross_pm_sc   in result,   "PubMed+Scopus article should be in consensus_k2"
    assert cross_wos_emb in result,   "WOS+Embase article should be in consensus_k2"
    assert in_all_four   in result,   "All-4-databases article should be in consensus_k2"
    assert solo_pubmed   not in result, "PubMed-only article must NOT be in consensus_k2"


def test_precision_gated_union_no_gates_returns_full_union():
    """
    precision_gated_union_articles without gates returns the full union of all
    database pools (same semantic as no filtering).
    """
    art1 = Article(pmid="1", doi="10.a/1")   # only PubMed
    art2 = Article(pmid=None, doi="10.b/2")  # only Scopus
    art3 = Article(pmid="3", doi="10.c/3")   # PubMed + Embase

    pools = {
        "pubmed_Q1":  {art1, art3},
        "scopus_Q1":  {art2},
        "embase_Q1":  {art3},
    }

    result = precision_gated_union_articles(pools, use_titles=False)
    assert result == {art1, art2, art3}


def test_two_stage_screen_no_gates_returns_full_union():
    """
    two_stage_screen_articles without gates returns stage1 = union of first
    effective_topk pools, which in split mode is all providers = full union.
    """
    art_pm = Article(pmid="pm", doi="10.pm/1")
    art_sc = Article(pmid=None, doi="10.sc/1")
    art_em = Article(pmid="em", doi="10.em/1")

    # stage1: set().union(*all 3 pools)
    stage1 = set().union(
        {art_pm},
        {art_sc},
        {art_em},
    )
    result = two_stage_screen_articles(stage1, filters_use_titles=False)
    assert result == {art_pm, art_sc, art_em}


def test_weighted_vote_equal_weights_returns_full_union():
    """
    weighted_vote_articles with equal default weights returns all articles
    (threshold = median weight = 1.0 = minimum score), effectively the union.
    """
    art1 = Article(pmid="1", doi="10.a/1")
    art2 = Article(pmid="2", doi="10.b/2")  # only in 1 pool
    art3 = Article(pmid="3", doi="10.c/3")  # in 2 pools

    pools = {
        "pubmed_Q1": {art1, art3},
        "scopus_Q1": {art2, art3},
    }

    result = weighted_vote_articles(pools, weights=[])   # empty → defaults to equal
    # With equal weights [1.0, 1.0], threshold = sorted[1//2] = 1.0.
    # Art1: 1 vote ≥ 1.0 ✓;  art2: 1 vote ≥ 1.0 ✓;  art3: 2 votes ≥ 1.0 ✓
    assert result == {art1, art2, art3}


def test_time_stratified_hybrid_in_split_mode_returns_full_union():
    """
    time_stratified_hybrid_articles with 4 split pools returns the full union
    (mid=2 → a=first 2 pools, b=last 2 pools; a|b=all).
    """
    art_pm = Article(pmid="pm", doi="10.pm/1")
    art_sc = Article(pmid=None, doi="10.sc/1")
    art_wos = Article(pmid="wos", doi="10.wos/1")
    art_em = Article(pmid="em", doi="10.em/1")

    # Dict order: pubmed, scopus, wos, embase
    pools = {
        "pubmed_Q1":  {art_pm},
        "scopus_Q1":  {art_sc},
        "wos_Q1":     {art_wos},
        "embase_Q1":  {art_em},
    }

    result = time_stratified_hybrid_articles(pools)
    assert result == {art_pm, art_sc, art_wos, art_em}


# ════════════════════════════════════════════════════════════════════════════
# Category 6 — Normal mode (no --split-by-provider) is unchanged
# ════════════════════════════════════════════════════════════════════════════

def test_normal_mode_one_pool_per_query(tmp_path):
    """
    Without --split-by-provider, load_articles_from_file returns one pool per
    query regardless of how many providers are in provider_details.
    """
    pd = {
        "pubmed": _pd_block([("1", "10.pm/1")]),
        "scopus": _pd_block([(None, "10.sc/1")]),
        "wos":    _pd_block([(None, "10.wos/1")]),
    }
    data = _details_list([
        {"query": "q1", "provider_details": pd, "providers_included": ["pubmed", "scopus", "wos"]},
        {"query": "q2", "provider_details": pd, "providers_included": ["pubmed", "scopus", "wos"]},
    ])
    f = tmp_path / "details.json"
    f.write_text(json.dumps(data))

    normal = load_articles_from_file(str(f))
    assert len(normal) == 2, f"Normal mode: expected 2 pools (one per query), got {len(normal)}"
    assert "q1" in normal and "q2" in normal


def test_split_mode_three_pools_per_query(tmp_path):
    """
    With --split-by-provider (via load_articles_from_file_split), the same file
    returns 3 pools per query (one per provider rather than one per query).
    """
    pd = {
        "pubmed": _pd_block([("1", "10.pm/1")]),
        "scopus": _pd_block([(None, "10.sc/1")]),
        "wos":    _pd_block([(None, "10.wos/1")]),
    }
    data = _details_list([
        {"query": "q1", "provider_details": pd, "providers_included": ["pubmed", "scopus", "wos"]},
    ])
    f = tmp_path / "details.json"
    f.write_text(json.dumps(data))

    split = load_articles_from_file_split(str(f))
    assert len(split) == 3, f"Split mode: expected 3 pools (one per provider), got {len(split)}"
    assert any("pubmed" in k for k in split)
    assert any("scopus" in k for k in split)
    assert any("wos" in k for k in split)


# ════════════════════════════════════════════════════════════════════════════
# Category 7 — --split-by-provider without --multi-key emits [WARN]
# ════════════════════════════════════════════════════════════════════════════

def test_split_by_provider_without_multi_key_warns(tmp_path, capsys):
    """
    Running aggregate_queries main() with --split-by-provider but no --multi-key
    should emit a [WARN] to stderr and fall through to the legacy PMID-only path.
    The legacy path has no flat PMIDs (only provider_details), so it exits with 1.
    The important assertion is that the WARN is emitted before that happens.
    """
    from aggregate_queries import main as agg_main

    data = _details_list([{
        "query": "q1",
        "provider_details": {"pubmed": _pd_block([("1", "10.pm/1")])},
        "providers_included": ["pubmed"],
    }])
    f = tmp_path / "details_test.json"
    f.write_text(json.dumps(data))
    outdir = tmp_path / "out"
    outdir.mkdir()

    test_argv = [
        "aggregate_queries.py",
        "--inputs", str(f),
        "--outdir", str(outdir),
        "--split-by-provider",
        # NOTE: intentionally NO --multi-key
    ]
    # Legacy mode exits with code 1 because there are no flat PMIDs (only provider_details)
    with pytest.raises(SystemExit):
        with patch.object(sys, "argv", test_argv):
            agg_main()

    err = capsys.readouterr().err
    assert "WARN" in err, f"Expected [WARN] in stderr for split without multi-key:\n{err}"
    assert "multi-key" in err.lower() or "--multi-key" in err, (
        f"Warning should mention --multi-key:\n{err}"
    )


# ════════════════════════════════════════════════════════════════════════════
# Category 8 — End-to-end aggregate_queries.main() in split mode
# ════════════════════════════════════════════════════════════════════════════

def _run_agg_main(argv: list[str]):
    """Invoke aggregate_queries.main() with patched sys.argv."""
    from aggregate_queries import main as agg_main
    with patch.object(sys, "argv", argv):
        agg_main()


def test_main_split_multi_key_produces_csv_output(tmp_path):
    """
    aggregate_queries.main() with --split-by-provider and --multi-key writes
    CSV output files (not .txt) for all strategies.
    """
    art_cross = Article(pmid="X", doi="10.cross/X")   # in pubmed + scopus → consensus_k2

    pd = {
        "pubmed": _pd_block([("X", "10.cross/X"), ("P", "10.pm/P")]),
        "scopus": _pd_block([(None, "10.cross/X"), (None, "10.sc/S")]),
    }
    data = _details_list([{
        "query": "q1",
        "provider_details": pd,
        "providers_included": ["pubmed", "scopus"],
    }])
    f = tmp_path / "details_main_test.json"
    f.write_text(json.dumps(data))
    outdir = tmp_path / "out"
    outdir.mkdir()

    _run_agg_main([
        "aggregate_queries.py",
        "--inputs", str(f),
        "--outdir", str(outdir),
        "--multi-key",
        "--split-by-provider",
    ])

    csv_files = list(outdir.glob("*.csv"))
    assert len(csv_files) > 0, "No .csv output files produced"
    # Should not produce .txt files in multi-key mode
    txt_files = list(outdir.glob("*.txt"))
    assert len(txt_files) == 0, f"No .txt files should be produced in multi-key mode: {txt_files}"


def test_main_split_consensus_k2_correct(tmp_path):
    """
    End-to-end: with 2 database pools sharing one article, consensus_k2.csv
    contains exactly that article and no others.
    """
    # Article A  → in both PubMed and Scopus → should be in consensus_k2
    # Article B  → only in PubMed            → should NOT be in consensus_k2
    pd = {
        "pubmed": _pd_block([("A", "10.cross/A"), ("B", "10.pm/B")]),
        "scopus": _pd_block([(None, "10.cross/A")]),
    }
    data = _details_list([{
        "query": "q1",
        "provider_details": pd,
        "providers_included": ["pubmed", "scopus"],
    }])
    f = tmp_path / "details_ck2.json"
    f.write_text(json.dumps(data))
    outdir = tmp_path / "ck2_out"
    outdir.mkdir()

    _run_agg_main([
        "aggregate_queries.py",
        "--inputs", str(f),
        "--outdir", str(outdir),
        "--multi-key",
        "--split-by-provider",
    ])

    ck2_files = list(outdir.glob("consensus_k2*"))
    assert ck2_files, "consensus_k2 output file not found"

    import csv
    with open(ck2_files[0], newline="") as fh:
        rows = list(csv.DictReader(fh))

    dois_in_ck2 = {r.get("doi", "").lower() for r in rows}
    pmids_in_ck2 = {r.get("pmid", "") for r in rows}

    assert "10.cross/a" in dois_in_ck2, f"Article A (cross-db) missing from ck2: {dois_in_ck2}"
    assert "10.pm/b" not in dois_in_ck2, f"Article B (PubMed-only) must NOT be in ck2: {dois_in_ck2}"


def test_main_normal_mode_produces_same_union(tmp_path):
    """
    Without --split-by-provider, main() uses the combined pool and consensus_k2
    means 'appears in ≥2 query strategies' — for a single query, always empty.
    """
    pd = {
        "pubmed": _pd_block([("1", "10.pm/1")]),
        "scopus": _pd_block([(None, "10.sc/1")]),
    }
    data = _details_list([{
        "query": "q1",
        "provider_details": pd,
        "providers_included": ["pubmed", "scopus"],
    }])
    f = tmp_path / "details_normal.json"
    f.write_text(json.dumps(data))
    outdir = tmp_path / "normal_out"
    outdir.mkdir()

    _run_agg_main([
        "aggregate_queries.py",
        "--inputs", str(f),
        "--outdir", str(outdir),
        "--multi-key",
        # NO --split-by-provider
    ])

    ck2_files = list(outdir.glob("consensus_k2*"))
    assert ck2_files, "consensus_k2 output file not found"

    import csv
    with open(ck2_files[0], newline="") as fh:
        rows = list(csv.DictReader(fh))

    # Only 1 query pool → no article can appear in ≥2 pools → consensus_k2 is empty
    assert len(rows) == 0, (
        f"With 1 query pool (no split), consensus_k2 should be empty; got {rows}"
    )


def test_main_split_effective_topk_in_info_log(tmp_path, capsys):
    """
    In split mode, the [INFO] log reports the number of per-provider pools
    and the effective_topk used.
    """
    pd = {
        "pubmed":  _pd_block([("1", "10.pm/1")]),
        "scopus":  _pd_block([(None, "10.sc/1")]),
        "wos":     _pd_block([(None, "10.wos/1")]),
        "embase":  _pd_block([("4", "10.emb/4")]),
    }
    data = _details_list([{
        "query": "q1",
        "provider_details": pd,
        "providers_included": ["pubmed", "scopus", "wos", "embase"],
    }])
    f = tmp_path / "details_4prov.json"
    f.write_text(json.dumps(data))
    outdir = tmp_path / "4prov_out"
    outdir.mkdir()

    _run_agg_main([
        "aggregate_queries.py",
        "--inputs", str(f),
        "--outdir", str(outdir),
        "--multi-key",
        "--split-by-provider",
        "--topk", "3",   # default topk=3 but 4 providers → effective_topk=4
    ])

    out = capsys.readouterr().out
    # Info log should mention the 4 pools and effective_topk
    assert "4 provider pool" in out or "topk=4" in out, (
        f"Expected INFO about 4 pools and effective_topk in stdout:\n{out}"
    )


# ════════════════════════════════════════════════════════════════════════════
# Category 9 — Known limitation: PMID-only vs PMID+DOI cross-provider (W4.4)
# ════════════════════════════════════════════════════════════════════════════

def test_known_limitation_pmid_only_vs_pmid_doi_not_in_consensus():
    """
    DOCUMENTED LIMITATION (W4.4 scope):
    If PubMed returns Article(pmid=P, doi=None) for an article (truly DOI-less or
    CrossRef resolution failed) and Embase returns the same article as
    Article(pmid=P, doi=D), the two Article objects have different hashes:
      PubMed:  hash(('pmid', P))
      Embase:  hash(('doi', D))
    They do not compare equal → consensus_k2 does not find them as cross-database
    agreement.

    This test pins the CURRENT behaviour so that any future W4.4 fix is immediately
    visible (the assertion will change from 'not in' to 'in').
    """
    pmid_only_pubmed = Article(pmid="orphan_P", doi=None)
    pmid_doi_embase  = Article(pmid="orphan_P", doi="10.emb/orphan")  # same paper, Embase has DOI

    pools = {
        "pubmed_Q1": {pmid_only_pubmed},
        "embase_Q1": {pmid_doi_embase},
    }

    result = consensus_k_articles(pools, topk=2, k=2)

    # Current behavior: not unified → neither appears in consensus_k2
    assert pmid_only_pubmed not in result, (
        "W4.4 not yet implemented: PMID-only PubMed record should NOT match PMID+DOI Embase record"
    )
    assert pmid_doi_embase not in result, (
        "W4.4 not yet implemented: PMID+DOI Embase record should NOT match PMID-only PubMed record"
    )


def test_known_limitation_same_doi_resolves_correctly():
    """
    POSITIVE CASE: When W2.1b CrossRef enrichment succeeds, PubMed also gets the
    DOI and both provider records share the same DOI → correct consensus_k2.
    (This is the Class A case; ~18 of ~22 PMID-only articles get resolved by W2.1b.)
    """
    pubmed_enriched = Article(pmid="enriched_P", doi="10.cr/enriched")   # W2.1b filled in
    embase_record   = Article(pmid="enriched_P", doi="10.cr/enriched")   # same DOI

    assert pubmed_enriched == embase_record, (
        "After W2.1b, PubMed and Embase records share the same DOI → must be equal"
    )

    pools = {
        "pubmed_Q1": {pubmed_enriched},
        "embase_Q1": {embase_record},
    }
    result = consensus_k_articles(pools, topk=2, k=2)
    assert pubmed_enriched in result, (
        "W2.1b resolved article must appear in consensus_k2 when both providers have the DOI"
    )
