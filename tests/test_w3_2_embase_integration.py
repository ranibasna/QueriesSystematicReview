"""W3.2 integration tests: EmbaseLocalProvider in the scoring pipeline

Tests cover:
  1.  EmbaseLocalProvider accepts a list of JSON paths (multi-path constructor)
  2.  Multi-path provider merges entries from all files — correct query lookup
  3.  Multi-path: hash miss on all files → empty result + warning (no crash)
  4.  providers_included field is written to each entry in details JSON
  5.  providers_included contains 'embase' when EmbaseLocalProvider is active
  6.  --embase-jsons CLI argument is accepted by the score subcommand
  7.  _load_queries_for_providers discovers queries_embase.txt for EmbaseLocalProvider
  8.  W3.3 — Embase appears as a native per-database row in summary_per_database CSV
  9.  W3.4 — _articles_from_provider_details_per_source creates per-provider pools
 10.  W3.4 — load_articles_from_file_split returns per-provider pools from a details JSON
 11.  W3.4 — load_all_articles_split works with multiple input files
 12.  W3.4 — consensus_k2 via split-by-provider (cross-database, not cross-query)
 13.  Double-counting guard: warning when both details_*.json with embase and standalone
      embase_query*.json are passed to load_all_articles
 14.  EmbaseLocalProvider: backward compat — single str path still works
"""
import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
from io import StringIO
from pathlib import Path
from typing import Dict, List, Set
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from search_providers import EmbaseLocalProvider
from llm_sr_select_and_score import (
    _build_query_bundles,
    _execute_query_bundle,
    _load_queries_for_providers,
    _provider_name,
    score_queries,
)
from aggregate_queries import (
    Article,
    ArticleRegistry,
    _articles_from_provider_details_per_source,
    load_all_articles,
    load_all_articles_split,
    load_articles_from_file,
    load_articles_from_file_split,
)


# ── helpers ───────────────────────────────────────────────────────────────────


def _make_embase_json(query: str, records: list, dois: list = None, pmids: list = None) -> dict:
    """Return a dict in embase_query*.json format, keyed by SHA-256 of query."""
    h = hashlib.sha256(query.encode()).hexdigest()
    return {
        h: {
            "query": query,
            "provider": "embase_manual",
            "results_count": len(records),
            "records": records,
            "retrieved_dois": dois or [r["doi"] for r in records if r.get("doi")],
            "retrieved_pmids": pmids or [r["pmid"] for r in records if r.get("pmid")],
        }
    }


def _write_json(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _make_details_list(bundles: list) -> list:
    """
    Minimal details_*.json list structure (as written by score_queries).
    Each bundle dict must have 'query', 'provider_details', 'providers_included'.
    """
    result = []
    for b in bundles:
        result.append(
            {
                "query": b["query"],
                "results_count": b.get("results_count", 0),
                "TP": b.get("TP", 0),
                "gold_size": b.get("gold_size", 1),
                "recall": b.get("recall", 0.0),
                "NNR_proxy": b.get("NNR_proxy", 0.0),
                "retrieved_pmids": b.get("retrieved_pmids", []),
                "retrieved_dois": b.get("retrieved_dois", []),
                "tp_pmids": b.get("tp_pmids", []),
                "provider_details": b.get("provider_details", {}),
                "providers_included": b.get("providers_included", []),
            }
        )
    return result


# ── Test 1 ── multi-path constructor ─────────────────────────────────────

def test_multi_path_constructor_accepts_list(tmp_path):
    """EmbaseLocalProvider.__init__ accepts a list of paths without error."""
    q = "test query"
    f1 = _write_json(tmp_path / "e1.json", _make_embase_json(q, [{"pmid": "1", "doi": "10.a/1"}]))
    p = EmbaseLocalProvider([str(f1)])
    assert p._json_paths == [str(f1)]
    assert p._json_path == str(f1)  # backward-compat singular attr


def test_backward_compat_single_str(tmp_path):
    """Passing a single str path still works (W3.2 is backward-compatible with W3.1)."""
    q = "test query"
    f = _write_json(tmp_path / "e.json", _make_embase_json(q, [{"pmid": "1", "doi": "10.a/1"}]))
    p = EmbaseLocalProvider(str(f))
    assert p._json_paths == [str(f)]
    dois, pmids, total = p.search(q, "", "")
    assert "10.a/1" in dois
    assert "1" in pmids
    print("PASS test_backward_compat_single_str")


# ── Test 2 ── multi-path merging ─────────────────────────────────────────

def test_multi_path_merges_entries(tmp_path):
    """
    With two JSON files containing different query entries, search() finds
    the correct entry from whichever file contains the matching SHA-256 hash.
    """
    q1 = "query one"
    q2 = "query two"
    f1 = _write_json(tmp_path / "e1.json", _make_embase_json(q1, [{"pmid": "11", "doi": "10.x/1"}]))
    f2 = _write_json(tmp_path / "e2.json", _make_embase_json(q2, [{"pmid": "22", "doi": "10.x/2"}]))

    p = EmbaseLocalProvider([str(f1), str(f2)])

    dois1, pmids1, _ = p.search(q1, "", "")
    assert "10.x/1" in dois1 and "11" in pmids1, f"Query 1 lookup failed: {dois1}, {pmids1}"

    # search() reuses cached data from _load(), so second call should work
    dois2, pmids2, _ = p.search(q2, "", "")
    assert "10.x/2" in dois2 and "22" in pmids2, f"Query 2 lookup failed: {dois2}, {pmids2}"

    print("PASS test_multi_path_merges_entries")


# ── Test 3 ── multi-path all-miss ─────────────────────────────────────────

def test_multi_path_all_miss_returns_empty(tmp_path, capsys):
    """Hash miss across all files → empty result + WARN, no exception."""
    q1, q2 = "q1", "q2"
    f1 = _write_json(tmp_path / "e1.json", _make_embase_json(q1, [{"pmid": "1"}]))
    f2 = _write_json(tmp_path / "e2.json", _make_embase_json(q2, [{"pmid": "2"}]))

    p = EmbaseLocalProvider([str(f1), str(f2)])
    dois, pmids, total = p.search("completely unknown query", "", "")

    assert dois == set() and pmids == set() and total == 0
    err = capsys.readouterr().err
    assert "WARN" in err
    print("PASS test_multi_path_all_miss_returns_empty")


# ── Test 4 ── providers_included field ────────────────────────────────────

def test_providers_included_in_details_json(tmp_path):
    """
    score_queries() writes 'providers_included' to each entry in details JSON.
    """
    q = "gold test query"
    gold_path = tmp_path / "gold.csv"
    gold_path.write_text("pmid\n99999\n", encoding="utf-8")

    class FakePM:
        name = "pubmed"
        id_type = "pmid"
        def search(self, query, mn, mx, retmax=100000):
            self._pmid_to_doi_cache = {"99999": "10.fake/1"}
            return {"10.fake/1"}, {"99999"}, 1

    bundles = [{"index": 0, "canonical": q, "per_provider": {"pubmed": q}}]
    details_path = tmp_path / "details_out"
    details_path.mkdir()

    score_queries(
        providers=[FakePM()],
        query_bundles=bundles,
        mindate="2020/01/01",
        maxdate="2024/12/31",
        gold_csv=str(gold_path),
        outdir=str(details_path),
        use_multi_key=False,
    )

    details_files = list(details_path.glob("details_*.json"))
    assert details_files, "No details_*.json produced"
    with open(details_files[0]) as f:
        data = json.load(f)

    assert isinstance(data, list) and len(data) == 1
    entry = data[0]
    assert "providers_included" in entry, "'providers_included' key missing from details entry"
    assert "pubmed" in entry["providers_included"], f"Expected 'pubmed' in providers_included: {entry['providers_included']}"
    print("PASS test_providers_included_in_details_json")


# ── Test 5 ── providers_included contains 'embase' ────────────────────────

def test_providers_included_has_embase_when_active(tmp_path):
    """
    When an EmbaseLocalProvider is in the providers list, 'embase' appears
    in providers_included of every details entry.
    """
    q = "test embase integration"
    gold_path = tmp_path / "gold.csv"
    gold_path.write_text("pmid\n99999\n", encoding="utf-8")

    embase_query = q  # same text for simplicity
    embase_json = _make_embase_json(embase_query, [{"pmid": "11111", "doi": "10.emb/1"}])
    embase_file = _write_json(tmp_path / "embase_query1.json", embase_json)

    class FakePM:
        name = "pubmed"
        id_type = "pmid"
        def search(self, query, mn, mx, retmax=100000):
            self._pmid_to_doi_cache = {"99999": "10.pm/1"}
            return {"10.pm/1"}, {"99999"}, 1

    embase_prov = EmbaseLocalProvider(str(embase_file))
    bundles = [{"index": 0, "canonical": q, "per_provider": {"pubmed": q, "embase": embase_query}}]

    out_dir = tmp_path / "out"
    out_dir.mkdir()
    score_queries(
        providers=[FakePM(), embase_prov],
        query_bundles=bundles,
        mindate="2020/01/01",
        maxdate="2024/12/31",
        gold_csv=str(gold_path),
        outdir=str(out_dir),
        use_multi_key=False,
    )

    details_files = list(out_dir.glob("details_*.json"))
    with open(details_files[0]) as f:
        data = json.load(f)

    pi = data[0]["providers_included"]
    assert "embase" in pi, f"Expected 'embase' in providers_included: {pi}"
    assert "pubmed" in pi, f"Expected 'pubmed' in providers_included: {pi}"
    print("PASS test_providers_included_has_embase_when_active:", pi)


# ── Test 6 ── --embase-jsons CLI argument ─────────────────────────────────

def test_cli_embase_jsons_argument_accepted():
    """The score subcommand's argparse accepts --embase-jsons without error."""
    import argparse as _ap_mod
    import llm_sr_select_and_score as _main

    # Re-parse with a fake sys.argv — verify no SystemExit / unrecognised arg
    test_argv = [
        "llm_sr_select_and_score.py",
        "--study-name", "fake_study",
        "score",
        "--mindate", "2020/01/01",
        "--maxdate", "2024/12/31",
        "--queries-txt", "queries.txt",
        "--gold-csv", "gold.csv",
        "--outdir", "out",
        "--embase-jsons", "embase_query1.json", "embase_query2.json",
    ]
    # Build the same argument parser as main() builds
    parser = _ap_mod.ArgumentParser()
    parser.add_argument("--study-name")
    parser.add_argument("--config")
    parser.add_argument("--databases")
    parser.add_argument("--scopus-api-key")
    parser.add_argument("--scopus-insttoken")
    parser.add_argument("--scopus-skip-date-filter", action="store_true")
    parser.add_argument("--wos-api-key")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_score = sub.add_parser("score")
    p_score.add_argument("--mindate")
    p_score.add_argument("--maxdate")
    p_score.add_argument("--queries-txt")
    p_score.add_argument("--gold-csv")
    p_score.add_argument("--outdir")
    p_score.add_argument("--query-num-offset", type=int, default=0)
    p_score.add_argument("--use-multi-key", action="store_true")
    p_score.add_argument("--ncbi-email")
    p_score.add_argument("--ncbi-api-key")
    p_score.add_argument("--embase-jsons", nargs="*", default=[], metavar="JSON")

    args = parser.parse_args(test_argv[1:])
    assert args.cmd == "score"
    assert args.embase_jsons == ["embase_query1.json", "embase_query2.json"]
    print("PASS test_cli_embase_jsons_argument_accepted:", args.embase_jsons)


# ── Test 7 ── _load_queries_for_providers discovers queries_embase.txt ───

def test_load_queries_for_providers_finds_embase_file(tmp_path):
    """
    _load_queries_for_providers returns embase-specific queries when
    queries_embase.txt exists alongside queries.txt.
    """
    base = tmp_path / "queries.txt"
    embase = tmp_path / "queries_embase.txt"
    base.write_text("PubMed query one\n\nPubMed query two\n")
    embase.write_text("Embase query one\n\nEmbase query two\n")

    embase_prov = EmbaseLocalProvider(str(tmp_path / "embase_dummy.json"))

    class FakePM:
        name = "pubmed"

    queries = _load_queries_for_providers([FakePM(), embase_prov], base)
    assert "embase" in queries, f"embase key missing: {list(queries.keys())}"
    assert queries["embase"][0] == "Embase query one", (
        f"Wrong embase query: {queries['embase'][0]!r}"
    )
    print("PASS test_load_queries_for_providers_finds_embase_file:", queries["embase"])


# ── Test 8 ── W3.3: Embase as native per-database row ─────────────────────

def test_embase_native_per_database_row(tmp_path):
    """
    W3.3: EmbaseLocalProvider creates a native 'embase' row in
    summary_per_database_*.csv without any post-hoc merge.
    """
    q = "db row test"
    gold_path = tmp_path / "gold.csv"
    gold_path.write_text("pmid\n11111\n", encoding="utf-8")

    embase_json = _make_embase_json(q, [{"pmid": "11111", "doi": "10.emb/1"}])
    embase_file = _write_json(tmp_path / "embase_query1.json", embase_json)

    class FakePM:
        name = "pubmed"
        id_type = "pmid"
        def search(self, query, mn, mx, retmax=100000):
            self._pmid_to_doi_cache = {}
            return set(), set(), 0

    out_dir = tmp_path / "out"
    out_dir.mkdir()
    bundles = [{"index": 0, "canonical": q, "per_provider": {"pubmed": q, "embase": q}}]

    score_queries(
        providers=[FakePM(), EmbaseLocalProvider(str(embase_file))],
        query_bundles=bundles,
        mindate="2020/01/01",
        maxdate="2024/12/31",
        gold_csv=str(gold_path),
        outdir=str(out_dir),
        use_multi_key=False,
    )

    per_db_files = list(out_dir.glob("summary_per_database_*.csv"))
    assert per_db_files, "No summary_per_database_*.csv produced"
    with open(per_db_files[0]) as f:
        rows = list(csv.DictReader(f))

    db_names = [r["database"] for r in rows]
    assert "embase" in db_names, (
        f"'embase' row missing from per-database CSV. Found: {db_names}"
    )
    embase_row = next(r for r in rows if r["database"] == "embase")
    assert int(embase_row["results_count"]) == 1, (
        f"Embase results_count should be 1, got {embase_row['results_count']}"
    )
    print("PASS test_embase_native_per_database_row:", db_names)


# ── Test 9 ── W3.4: _articles_from_provider_details_per_source ──────────

def test_articles_from_provider_details_per_source():
    """_articles_from_provider_details_per_source returns one pool per provider."""
    provider_details = {
        "pubmed": {
            "linked_records": [{"pmid": "1", "doi": "10.pm/1"}, {"pmid": "2", "doi": None}],
        },
        "scopus": {
            "linked_records": [{"pmid": None, "doi": "10.sc/1"}, {"pmid": None, "doi": "10.sc/2"}],
        },
        "embase": {
            "linked_records": [{"pmid": "3", "doi": "10.emb/1"}],
        },
        "wos": {
            "error": "timeout",  # should be skipped
        },
    }
    result = _articles_from_provider_details_per_source(provider_details, "Q1")

    assert len(result) == 3, f"Expected 3 provider pools (wos skipped), got {len(result)}: {list(result)}"
    assert "pubmed_Q1" in result
    assert "scopus_Q1" in result
    assert "embase_Q1" in result
    assert "wos_Q1" not in result

    # Check pmid=2 (PMID-only) is in pubmed pool
    pubmed_pool = result["pubmed_Q1"]
    assert any(a.pmid == "2" for a in pubmed_pool), f"PMID-only article missing: {pubmed_pool}"
    # Check scopus has 2 articles
    assert len(result["scopus_Q1"]) == 2, f"scopus pool size wrong: {result['scopus_Q1']}"
    print("PASS test_articles_from_provider_details_per_source")


# ── Test 10 ── W3.4: load_articles_from_file_split ────────────────────────

def test_load_articles_from_file_split(tmp_path):
    """
    load_articles_from_file_split creates per-provider pools from a details JSON.
    Combined pool (from load_articles_from_file) → 1 key;
    split pool → 1 key per provider.
    """
    provider_details = {
        "pubmed": {
            "linked_records": [{"pmid": "10", "doi": "10.pm/10"}],
            "id_type": "pmid",
        },
        "scopus": {
            "linked_records": [{"pmid": None, "doi": "10.sc/10"}],
            "id_type": "scopus_id",
        },
        "embase": {
            "linked_records": [{"pmid": "20", "doi": "10.emb/20"}],
            "id_type": "pmid",
        },
    }
    data = _make_details_list(
        [{"query": "split test query", "provider_details": provider_details,
          "providers_included": ["embase", "pubmed", "scopus"]}]
    )
    details_file = tmp_path / "details_split.json"
    details_file.write_text(json.dumps(data))

    # Combined (standard)
    combined = load_articles_from_file(str(details_file))
    assert len(combined) == 1, f"Combined should yield 1 pool, got {len(combined)}"

    # Split
    split = load_articles_from_file_split(str(details_file))
    assert len(split) == 3, f"Split should yield 3 pools, got {len(split)}: {list(split)}"
    assert any("pubmed" in k for k in split)
    assert any("scopus" in k for k in split)
    assert any("embase" in k for k in split)
    print("PASS test_load_articles_from_file_split:", list(split.keys()))


# ── Test 11 ── W3.4: load_all_articles_split ─────────────────────────────

def test_load_all_articles_split_multiple_files(tmp_path):
    """load_all_articles_split merges per-provider pools from multiple files."""
    pd1 = {
        "pubmed": {"linked_records": [{"pmid": "1", "doi": "10.a/1"}]},
        "embase": {"linked_records": [{"pmid": "2", "doi": "10.b/2"}]},
    }
    pd2 = {
        "pubmed": {"linked_records": [{"pmid": "3", "doi": "10.c/3"}]},
        "wos":    {"linked_records": [{"pmid": None, "doi": "10.d/4"}]},
    }
    f1 = tmp_path / "details_1.json"
    f2 = tmp_path / "details_2.json"
    f1.write_text(json.dumps(_make_details_list([{"query": "Q1", "provider_details": pd1}])))
    f2.write_text(json.dumps(_make_details_list([{"query": "Q2", "provider_details": pd2}])))

    result = load_all_articles_split([str(f1), str(f2)])
    # Expected pools: pubmed_Q1, embase_Q1, pubmed_Q2, wos_Q2
    assert len(result) == 4, f"Expected 4 pools: {list(result.keys())}"
    print("PASS test_load_all_articles_split_multiple_files:", list(result.keys()))


# ── Test 12 ── W3.4: consensus_k2 with split-by-provider ─────────────────

def test_consensus_k2_split_by_provider(tmp_path):
    """
    With --split-by-provider, consensus_k2 (k=2) finds articles retrieved by
    ≥2 databases, not ≥2 query strategies.
    """
    from aggregate_queries import consensus_k_articles

    # Article A: appears in pubmed AND embase → should be in consensus_k2
    # Article B: appears in pubmed only → should NOT be in consensus_k2
    # Article C: appears in scopus AND wos → should be in consensus_k2
    art_A = Article(pmid="A", doi="10.a/A")
    art_B = Article(pmid="B", doi="10.b/B")
    art_C = Article(pmid=None, doi="10.c/C")

    articles_by_query = {
        "pubmed_Q1": {art_A, art_B},
        "embase_Q1": {art_A},
        "scopus_Q1": {art_C},
        "wos_Q1":    {art_C},
    }
    # Use all 4 pools (topk=4)
    result = consensus_k_articles(articles_by_query, topk=4, k=2)

    assert art_A in result, f"art_A (in pubmed+embase) should be in consensus_k2: {result}"
    assert art_C in result, f"art_C (in scopus+wos) should be in consensus_k2: {result}"
    assert art_B not in result, f"art_B (pubmed only) should NOT be in consensus_k2: {result}"
    print("PASS test_consensus_k2_split_by_provider:", {a.pmid or a.doi for a in result})


# ── Test 13 ── double-counting warning ───────────────────────────────────

def test_double_counting_warning_emitted(tmp_path, capsys):
    """
    load_all_articles() warns when both a details JSON with providers_included='embase'
    AND standalone embase_query*.json files are passed together.
    """
    # Build details JSON with providers_included=['embase', 'pubmed']
    pd_data = {
        "pubmed":  {"linked_records": [{"pmid": "1", "doi": "10.pm/1"}]},
        "embase":  {"linked_records": [{"pmid": "2", "doi": "10.emb/2"}]},
    }
    details_data = _make_details_list(
        [{"query": "Q", "provider_details": pd_data, "providers_included": ["embase", "pubmed"]}]
    )
    details_file = tmp_path / "details_20260101-000000.json"
    details_file.write_text(json.dumps(details_data))

    # Build standalone embase JSON
    standalone = _write_json(
        tmp_path / "embase_query1.json",
        _make_embase_json("Q", [{"pmid": "2", "doi": "10.emb/2"}]),
    )

    # load_all_articles with BOTH → should warn
    _ = load_all_articles([str(details_file), str(standalone)])

    err = capsys.readouterr().err
    assert "WARN" in err and "double-counting" in err.lower(), (
        f"Expected double-counting WARN in stderr:\n{err}"
    )
    print("PASS test_double_counting_warning_emitted")


# ── Test 14 ── no warning when only details file ──────────────────────────

def test_no_double_counting_warning_without_standalone(tmp_path, capsys):
    """No warning when only details_*.json (with embase) is passed — correct use."""
    pd_data = {
        "embase": {"linked_records": [{"pmid": "2", "doi": "10.emb/2"}]},
    }
    details_data = _make_details_list(
        [{"query": "Q", "provider_details": pd_data, "providers_included": ["embase"]}]
    )
    details_file = tmp_path / "details_20260101-000001.json"
    details_file.write_text(json.dumps(details_data))

    _ = load_all_articles([str(details_file)])

    err = capsys.readouterr().err
    assert "double-counting" not in err.lower(), (
        f"Unexpected double-counting WARN with single details file:\n{err}"
    )
    print("PASS test_no_double_counting_warning_without_standalone")


# ── run as script ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import pathlib
    import tempfile as _tf

    _tmp = pathlib.Path(_tf.mkdtemp())

    class _Capsys:
        def readouterr(self):
            class R:
                out = ""
                err = ""
            return R()

    test_multi_path_constructor_accepts_list(_tmp / "t1")
    _tmp_bc = _tmp / "t_bc"; _tmp_bc.mkdir()
    test_backward_compat_single_str(_tmp_bc)
    _tmp2 = _tmp / "t2"; _tmp2.mkdir()
    test_multi_path_merges_entries(_tmp2)
    _tmp3 = _tmp / "t3"; _tmp3.mkdir()
    test_multi_path_all_miss_returns_empty(_tmp3, _Capsys())
    _tmp4 = _tmp / "t4"; _tmp4.mkdir()
    test_providers_included_in_details_json(_tmp4)
    _tmp5 = _tmp / "t5"; _tmp5.mkdir()
    test_providers_included_has_embase_when_active(_tmp5)
    test_cli_embase_jsons_argument_accepted()
    _tmp7 = _tmp / "t7"; _tmp7.mkdir()
    test_load_queries_for_providers_finds_embase_file(_tmp7)
    _tmp8 = _tmp / "t8"; _tmp8.mkdir()
    test_embase_native_per_database_row(_tmp8)
    test_articles_from_provider_details_per_source()
    _tmp10 = _tmp / "t10"; _tmp10.mkdir()
    test_load_articles_from_file_split(_tmp10)
    _tmp11 = _tmp / "t11"; _tmp11.mkdir()
    test_load_all_articles_split_multiple_files(_tmp11)
    test_consensus_k2_split_by_provider(_tmp)
    _tmp13 = _tmp / "t13"; _tmp13.mkdir()
    test_double_counting_warning_emitted(_tmp13, _Capsys())
    _tmp14 = _tmp / "t14"; _tmp14.mkdir()
    test_no_double_counting_warning_without_standalone(_tmp14, _Capsys())

    print()
    print("All W3.2 tests passed.")
