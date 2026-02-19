"""W3.3 tests: Unified per-database reporting with Embase as native provider.

Scope
-----
W3.3 states: "EmbaseLocalProvider flows through the same per-DB scoring loop as
PubMed/Scopus/WOS, producing a native Embase row in summary_per_database_*.csv —
no extra code required beyond correct provider wiring from W3.2."

These tests verify:
  1.  4-provider (pubmed + scopus + wos + embase) + COMBINED row structure
  2.  Embase TP via DOI Layer 1 (use_multi_key=True)
  3.  Embase TP via PMID Layer 2 fallback (use_multi_key=True, DOI absent)
  4.  Embase-unique article contribution to COMBINED recall
  5.  NNR_proxy calculation for Embase row
  6.  query_num field correctness across multiple query bundles
  7.  Embase NOT matched when article is absent from its results
  8.  Embase handles multiple gold articles — partial recall
  9.  Embase with only DOI records (no PMIDs) — DOI-only matching
 10.  W3.4 — Article objects produced by Embase linked_records match correctly across
      PubMed+Embase in per-provider split (consensus_k2 succeeds)
 11.  W3.4 — Documented edge case: PMID-only from PubMed does NOT match PMID+DOI
      from Embase in per-provider split (known W4.4 limitation; asserted as expected
      behavior here so we notice if it ever changes)

Design notes
------------
- All tests use fake providers to avoid any real API calls.
- Embase fake is a real EmbaseLocalProvider backed by a tmp JSON file.
- Fake PubMed sets self._pmid_to_doi_cache (as the real provider does) so that
  _execute_query_bundle reads it correctly.
- Fake Scopus / WOS use id_type != 'pmid', so their native IDs never flow into
  db_pmids_for_matching (exactly as in production).
"""

import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import List, Set

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from search_providers import EmbaseLocalProvider
from llm_sr_select_and_score import score_queries
from aggregate_queries import (
    Article,
    _articles_from_provider_details_per_source,
    consensus_k_articles,
)


# ── helpers ──────────────────────────────────────────────────────────────────


def _embase_json(query: str, records: list) -> dict:
    """Build embase_query*.json content for a single query."""
    h = hashlib.sha256(query.encode()).hexdigest()
    dois = [r["doi"] for r in records if r.get("doi")]
    pmids = [r["pmid"] for r in records if r.get("pmid")]
    return {
        h: {
            "query": query,
            "provider": "embase_manual",
            "results_count": len(records),
            "records": records,
            "retrieved_dois": dois,
            "retrieved_pmids": pmids,
        }
    }


def _write_json(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _gold_csv(path: Path, rows: list) -> Path:
    """Write pmid,doi gold CSV. Each row is (pmid, doi); use '' for missing."""
    lines = ["pmid,doi"] + [f"{pmid},{doi}" for pmid, doi in rows]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _read_per_db(out_dir: Path) -> list:
    files = list(out_dir.glob("summary_per_database_*.csv"))
    assert files, f"No summary_per_database_*.csv produced in {out_dir}"
    with open(files[0]) as f:
        return list(csv.DictReader(f))


def _db_row(rows: list, db: str, qnum: int = 1) -> dict:
    """Return the per-DB row for a given database and query_num."""
    matches = [
        r for r in rows
        if r["database"] == db and int(r.get("query_num", qnum)) == qnum
    ]
    assert matches, (
        f"No row for database='{db}' query_num={qnum}. "
        f"Found: {[(r['database'], r.get('query_num')) for r in rows]}"
    )
    return matches[0]


# ── Fake providers ────────────────────────────────────────────────────────────


class _FakePubMed:
    """PubMed fake: id_type='pmid', sets _pmid_to_doi_cache on each search()."""
    name = "pubmed"
    id_type = "pmid"

    def __init__(self, pmid_doi_pairs: list):
        """pairs = [(pmid, doi_or_None), ...]"""
        self._pairs = pmid_doi_pairs

    def search(self, query, mn, mx, retmax=100000):
        # Populate the cache exactly as the real PubMedProvider does (W2.1)
        self._pmid_to_doi_cache = {p: d for p, d in self._pairs if d}
        dois = {d for _, d in self._pairs if d}
        pmids = {p for p, _ in self._pairs if p}
        return dois, pmids, len(pmids)


class _FakeScopus:
    """Scopus fake: id_type='scopus_id' (internal IDs, never PMIDs)."""
    name = "scopus"
    id_type = "scopus_id"

    def __init__(self, dois: set = None):
        self._dois = dois or set()

    def search(self, query, mn, mx, retmax=100000):
        ids = {f"sc_{i}" for i, _ in enumerate(sorted(self._dois))}
        return set(self._dois), ids, len(self._dois)


class _FakeWOS:
    """WOS fake: id_type='wos_id' (internal IDs, never PMIDs)."""
    name = "wos"
    id_type = "wos_id"

    def __init__(self, dois: set = None):
        self._dois = dois or set()

    def search(self, query, mn, mx, retmax=100000):
        ids = {f"wos_{i}" for i, _ in enumerate(sorted(self._dois))}
        return set(self._dois), ids, len(self._dois)


def _run_score_queries(
    tmp_path: Path,
    providers: list,
    provider_queries: dict,
    gold_rows: list,
    use_multi_key: bool = True,
    query_num_offset: int = 0,
) -> list:
    """Run score_queries with a single bundle and return the per-DB CSV rows."""
    from llm_sr_select_and_score import _build_query_bundles

    gold_path = tmp_path / "gold.csv"
    _gold_csv(gold_path, gold_rows)

    out_dir = tmp_path / "out"
    out_dir.mkdir(exist_ok=True)

    # Build bundle: canonical = pubmed query (or first available)
    canonical = provider_queries.get("pubmed") or next(iter(provider_queries.values()))
    bundles = [
        {
            "index": 0,
            "canonical": canonical,
            "per_provider": dict(provider_queries),
        }
    ]

    score_queries(
        providers=providers,
        query_bundles=bundles,
        mindate="2020/01/01",
        maxdate="2024/12/31",
        gold_csv=str(gold_path),
        outdir=str(out_dir),
        use_multi_key=use_multi_key,
        query_num_offset=query_num_offset,
    )
    return _read_per_db(out_dir)


# ══════════════════════════════════════════════════════════════════════════════
# Test 1 — 4-provider full structure
# ══════════════════════════════════════════════════════════════════════════════


def test_four_provider_row_structure(tmp_path):
    """
    Per-DB CSV must contain exactly 5 rows per query:
    pubmed, scopus, wos, embase, COMBINED — in that order (or any order, but all present).
    Each row must have the expected column set.
    """
    Q = "structure test query"
    embase_file = _write_json(
        tmp_path / "embase.json",
        _embase_json(Q, [{"pmid": "999", "doi": "10.em/999"}]),
    )

    rows = _run_score_queries(
        tmp_path=tmp_path,
        providers=[
            _FakePubMed([("111", "10.pm/111")]),
            _FakeScopus({"10.sc/1"}),
            _FakeWOS({"10.wos/1"}),
            EmbaseLocalProvider(str(embase_file)),
        ],
        provider_queries={"pubmed": Q, "scopus": Q, "wos": Q, "embase": Q},
        gold_rows=[("111", "10.pm/111"), ("999", "10.em/999")],
        use_multi_key=True,
    )

    db_names = {r["database"] for r in rows}
    assert "pubmed" in db_names, f"Missing pubmed row: {db_names}"
    assert "scopus" in db_names, f"Missing scopus row: {db_names}"
    assert "wos" in db_names, f"Missing wos row: {db_names}"
    assert "embase" in db_names, f"Missing embase row: {db_names}"
    assert "COMBINED" in db_names, f"Missing COMBINED row: {db_names}"
    assert len(rows) == 5, f"Expected 5 rows, got {len(rows)}: {db_names}"

    # Each row must have the core columns
    required_cols = {"query_num", "database", "results_count", "TP", "gold_size", "recall", "NNR_proxy"}
    for row in rows:
        missing = required_cols - set(row.keys())
        assert not missing, f"Row for '{row['database']}' missing columns: {missing}"

    # multi-key columns present for each row
    mk_cols = {"matches_by_pmid", "matches_by_doi_only"}
    for row in rows:
        for col in mk_cols:
            assert col in row, f"Row for '{row['database']}' missing multi-key column '{col}'"

    print(f"PASS test_four_provider_row_structure: found {db_names}")


# ══════════════════════════════════════════════════════════════════════════════
# Test 2 — Embase TP via DOI Layer 1 (use_multi_key=True)
# ══════════════════════════════════════════════════════════════════════════════


def test_embase_tp_via_doi_layer1(tmp_path):
    """
    When Embase returns an article whose DOI exactly matches a gold article's DOI,
    set_metrics_row_level Layer 1 should count it as a TP.
    PubMed/Scopus/WOS return nothing — only Embase can produce the TP.
    """
    Q = "doi layer1 test"
    gold_doi = "10.em/layer1"
    gold_pmid = "10001"

    embase_file = _write_json(
        tmp_path / "embase.json",
        _embase_json(Q, [{"pmid": gold_pmid, "doi": gold_doi}]),
    )

    rows = _run_score_queries(
        tmp_path=tmp_path,
        providers=[
            _FakePubMed([]),                         # returns nothing
            _FakeScopus(set()),                      # returns nothing
            EmbaseLocalProvider(str(embase_file)),
        ],
        provider_queries={"pubmed": Q, "scopus": Q, "embase": Q},
        gold_rows=[(gold_pmid, gold_doi)],
        use_multi_key=True,
    )

    embase_row = _db_row(rows, "embase")
    assert int(embase_row["TP"]) == 1, f"Embase TP should be 1, got {embase_row['TP']}"
    assert float(embase_row["recall"]) == pytest.approx(1.0), (
        f"Embase recall should be 1.0, got {embase_row['recall']}"
    )
    assert int(embase_row["matches_by_doi_only"]) == 1, (
        f"matches_by_doi_only should be 1 (DOI Layer 1 matched), got {embase_row['matches_by_doi_only']}"
    )
    print(
        f"PASS test_embase_tp_via_doi_layer1: TP={embase_row['TP']}, "
        f"recall={embase_row['recall']}, doi_only={embase_row['matches_by_doi_only']}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# Test 3 — Embase TP via PMID Layer 2 fallback (DOI absent in Embase record)
# ══════════════════════════════════════════════════════════════════════════════


def test_embase_tp_via_pmid_layer2_fallback(tmp_path):
    """
    When Embase returns an article with PMID only (no DOI), but the gold standard
    has a matching PMID, set_metrics_row_level Layer 2 (PMID fallback) should fire.

    Verifies that id_type='pmid' causes db_pmids_for_matching = db_ids (Embase PMIDs),
    enabling the fallback path in the per-DB scoring loop.
    """
    Q = "pmid fallback test"
    gold_pmid = "20002"
    gold_doi = "10.em/layer2"  # gold has DOI, but Embase record does NOT

    embase_file = _write_json(
        tmp_path / "embase.json",
        # Embase record: PMID only, no DOI — simulates incomplete Embase export
        _embase_json(Q, [{"pmid": gold_pmid, "doi": ""}]),
    )

    rows = _run_score_queries(
        tmp_path=tmp_path,
        providers=[
            _FakePubMed([]),                         # returns nothing
            EmbaseLocalProvider(str(embase_file)),
        ],
        provider_queries={"pubmed": Q, "embase": Q},
        gold_rows=[(gold_pmid, gold_doi)],
        use_multi_key=True,
    )

    embase_row = _db_row(rows, "embase")
    assert int(embase_row["TP"]) == 1, (
        f"Embase should have TP=1 via PMID fallback, got {embase_row['TP']}"
    )
    assert float(embase_row["recall"]) == pytest.approx(1.0), (
        f"Embase recall should be 1.0, got {embase_row['recall']}"
    )
    # DOI Layer 1 did NOT fire (Embase DOI was empty)
    assert int(embase_row["matches_by_doi_only"]) == 0, (
        f"matches_by_doi_only should be 0 (DOI absent), got {embase_row['matches_by_doi_only']}"
    )
    # matches_by_pmid = TP = 1 (one PMID-fallback match)
    assert int(embase_row["matches_by_pmid"]) == 1, (
        f"matches_by_pmid should be 1, got {embase_row['matches_by_pmid']}"
    )
    print(
        f"PASS test_embase_tp_via_pmid_layer2_fallback: TP={embase_row['TP']}, "
        f"doi_only={embase_row['matches_by_doi_only']}, by_pmid={embase_row['matches_by_pmid']}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# Test 4 — Embase-unique article contributes to COMBINED recall
# ══════════════════════════════════════════════════════════════════════════════


def test_embase_unique_article_lifts_combined_recall(tmp_path):
    """
    Scenario:
      Gold:   Article A (pmid=1, doi=10.a/1)   — found by PubMed AND Embase
              Article B (pmid=2, doi=10.b/2)   — found ONLY by Embase
      PubMed: returns A only (1 article)
      Embase: returns A and B (2 articles)

    Expected per-DB metrics (use_multi_key=True):
      pubmed   TP=1, recall=0.5  (misses B)
      embase   TP=2, recall=1.0  (finds both A and B)
      COMBINED TP=2, recall=1.0  (union includes Embase's B)

    This confirms that Embase participation in _execute_query_bundle increases
    COMBINED recall beyond what PubMed alone achieves.
    """
    Q = "embase unique contribution"
    gold = [("1", "10.a/1"), ("2", "10.b/2")]

    embase_file = _write_json(
        tmp_path / "embase.json",
        _embase_json(Q, [
            {"pmid": "1", "doi": "10.a/1"},
            {"pmid": "2", "doi": "10.b/2"},
        ]),
    )

    rows = _run_score_queries(
        tmp_path=tmp_path,
        providers=[
            _FakePubMed([("1", "10.a/1")]),          # only article A
            EmbaseLocalProvider(str(embase_file)),   # articles A and B
        ],
        provider_queries={"pubmed": Q, "embase": Q},
        gold_rows=gold,
        use_multi_key=True,
    )

    pubmed_row = _db_row(rows, "pubmed")
    embase_row = _db_row(rows, "embase")
    combined_row = _db_row(rows, "COMBINED")

    assert int(pubmed_row["TP"]) == 1, f"PubMed TP should be 1 (only A), got {pubmed_row['TP']}"
    assert float(pubmed_row["recall"]) == pytest.approx(0.5), f"PubMed recall should be 0.5"

    assert int(embase_row["TP"]) == 2, f"Embase TP should be 2 (A+B), got {embase_row['TP']}"
    assert float(embase_row["recall"]) == pytest.approx(1.0), f"Embase recall should be 1.0"

    assert int(combined_row["TP"]) == 2, (
        f"COMBINED TP should be 2 (Embase lifts recall), got {combined_row['TP']}"
    )
    assert float(combined_row["recall"]) == pytest.approx(1.0), (
        f"COMBINED recall should be 1.0, got {combined_row['recall']}"
    )
    print(
        f"PASS test_embase_unique_article_lifts_combined_recall: "
        f"pubmed_recall={pubmed_row['recall']}, embase_recall={embase_row['recall']}, "
        f"combined_recall={combined_row['recall']}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# Test 5 — NNR_proxy correctness for Embase row
# ══════════════════════════════════════════════════════════════════════════════


def test_embase_nnr_proxy(tmp_path):
    """
    NNR_proxy = results_count / max(TP, 1).
    Embase returns 5 articles; 1 is a gold match → NNR_proxy = 5.0.
    Embase returns 3 articles; 0 gold matches → NNR_proxy = 3/1 = 3.0 (max denom=1).
    """
    Q_match = "nnr match"
    Q_miss = "nnr miss"
    gold_pmid, gold_doi = "50001", "10.nnr/1"

    # 5-article Embase set: 1 match + 4 non-matches
    embase_data = {}
    embase_data.update(_embase_json(Q_match, [
        {"pmid": gold_pmid, "doi": gold_doi},
        {"pmid": "50002", "doi": "10.nnr/2"},
        {"pmid": "50003", "doi": "10.nnr/3"},
        {"pmid": "50004", "doi": "10.nnr/4"},
        {"pmid": "50005", "doi": "10.nnr/5"},
    ]))
    # 3-article Embase set: 0 matches
    embase_data.update(_embase_json(Q_miss, [
        {"pmid": "60001", "doi": "10.miss/1"},
        {"pmid": "60002", "doi": "10.miss/2"},
        {"pmid": "60003", "doi": "10.miss/3"},
    ]))

    embase_file = _write_json(tmp_path / "embase.json", embase_data)
    gold_path = tmp_path / "gold.csv"
    _gold_csv(gold_path, [(gold_pmid, gold_doi)])
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    bundles = [
        {"index": 0, "canonical": Q_match, "per_provider": {"pubmed": Q_match, "embase": Q_match}},
        {"index": 1, "canonical": Q_miss, "per_provider": {"pubmed": Q_miss, "embase": Q_miss}},
    ]
    score_queries(
        providers=[_FakePubMed([]), EmbaseLocalProvider(str(embase_file))],
        query_bundles=bundles,
        mindate="2020/01/01", maxdate="2024/12/31",
        gold_csv=str(gold_path),
        outdir=str(out_dir),
        use_multi_key=True,
    )
    rows = _read_per_db(out_dir)

    embase_match = _db_row(rows, "embase", qnum=1)
    embase_miss  = _db_row(rows, "embase", qnum=2)

    assert int(embase_match["results_count"]) == 5, (
        f"Embase results_count should be 5, got {embase_match['results_count']}"
    )
    assert int(embase_match["TP"]) == 1
    assert float(embase_match["NNR_proxy"]) == pytest.approx(5.0), (
        f"NNR_proxy should be 5.0 (5 results / 1 TP), got {embase_match['NNR_proxy']}"
    )

    assert int(embase_miss["results_count"]) == 3
    assert int(embase_miss["TP"]) == 0
    assert float(embase_miss["NNR_proxy"]) == pytest.approx(3.0), (
        f"NNR_proxy with 0 TP should be 3.0 (3/max(0,1)=3), got {embase_miss['NNR_proxy']}"
    )
    print(
        f"PASS test_embase_nnr_proxy: "
        f"match={embase_match['NNR_proxy']}, miss={embase_miss['NNR_proxy']}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# Test 6 — query_num field correctness across multiple query bundles
# ══════════════════════════════════════════════════════════════════════════════


def test_embase_query_num_multi_bundle(tmp_path):
    """
    With 3 query bundles, each produces an Embase row with the correct query_num
    (1, 2, 3). Tests that bundle_idx + 1 + query_num_offset is correct.
    Also verifies query_num_offset shifts numbering correctly (offset=2 → nums 3,4,5).
    """
    Qs = ["bundle one", "bundle two", "bundle three"]

    embase_data = {}
    for q in Qs:
        embase_data.update(_embase_json(q, [{"pmid": "99", "doi": "10.em/99"}]))
    embase_file = _write_json(tmp_path / "embase.json", embase_data)

    gold_path = tmp_path / "gold.csv"
    _gold_csv(gold_path, [("99", "10.em/99")])
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    bundles = [
        {"index": i, "canonical": q, "per_provider": {"pubmed": q, "embase": q}}
        for i, q in enumerate(Qs)
    ]
    score_queries(
        providers=[_FakePubMed([]), EmbaseLocalProvider(str(embase_file))],
        query_bundles=bundles,
        mindate="2020/01/01", maxdate="2024/12/31",
        gold_csv=str(gold_path),
        outdir=str(out_dir),
        use_multi_key=False,       # simple mode is enough for this test
        query_num_offset=0,
    )
    rows = _read_per_db(out_dir)

    embase_rows = sorted([r for r in rows if r["database"] == "embase"],
                         key=lambda r: int(r["query_num"]))
    qnums = [int(r["query_num"]) for r in embase_rows]
    assert qnums == [1, 2, 3], f"query_num values should be [1, 2, 3], got {qnums}"

    # Re-run with offset=2 → query_nums should be 3, 4, 5
    out_dir2 = tmp_path / "out2"
    out_dir2.mkdir()
    score_queries(
        providers=[_FakePubMed([]), EmbaseLocalProvider(str(embase_file))],
        query_bundles=bundles,
        mindate="2020/01/01", maxdate="2024/12/31",
        gold_csv=str(gold_path),
        outdir=str(out_dir2),
        use_multi_key=False,
        query_num_offset=2,
    )
    rows2 = _read_per_db(out_dir2)
    embase_rows2 = sorted([r for r in rows2 if r["database"] == "embase"],
                          key=lambda r: int(r["query_num"]))
    qnums2 = [int(r["query_num"]) for r in embase_rows2]
    assert qnums2 == [3, 4, 5], f"With offset=2, query_nums should be [3, 4, 5], got {qnums2}"
    print(f"PASS test_embase_query_num_multi_bundle: base={qnums}, offset={qnums2}")


# ══════════════════════════════════════════════════════════════════════════════
# Test 7 — Embase returns no matching article → TP=0, recall=0
# ══════════════════════════════════════════════════════════════════════════════


def test_embase_no_match_tp_zero(tmp_path):
    """
    When Embase results contain no gold article, its per-DB row has TP=0, recall=0.
    COMBINED recall is driven by PubMed only.
    """
    Q = "embase zero tp"
    gold_rows = [("1001", "10.gold/1")]

    embase_file = _write_json(
        tmp_path / "embase.json",
        _embase_json(Q, [{"pmid": "9999", "doi": "10.irrelevant/99"}]),  # no gold match
    )

    rows = _run_score_queries(
        tmp_path=tmp_path,
        providers=[
            _FakePubMed([("1001", "10.gold/1")]),    # PubMed finds the gold article
            EmbaseLocalProvider(str(embase_file)),   # Embase does NOT
        ],
        provider_queries={"pubmed": Q, "embase": Q},
        gold_rows=gold_rows,
        use_multi_key=True,
    )

    embase_row = _db_row(rows, "embase")
    assert int(embase_row["TP"]) == 0, f"Embase TP should be 0, got {embase_row['TP']}"
    assert float(embase_row["recall"]) == pytest.approx(0.0), f"Embase recall should be 0.0"

    combined_row = _db_row(rows, "COMBINED")
    assert int(combined_row["TP"]) == 1, f"COMBINED should still have TP=1 via PubMed"
    print(f"PASS test_embase_no_match_tp_zero: embase_tp=0, combined_tp={combined_row['TP']}")


# ══════════════════════════════════════════════════════════════════════════════
# Test 8 — Partial recall: Embase finds 2 of 4 gold articles
# ══════════════════════════════════════════════════════════════════════════════


def test_embase_partial_recall(tmp_path):
    """
    Gold has 4 articles. Embase finds 2 of them.
    Verifies fractional recall and correct gold_size in Embase row.
    """
    Q = "partial recall test"
    gold = [("1", "10.g/1"), ("2", "10.g/2"), ("3", "10.g/3"), ("4", "10.g/4")]

    embase_file = _write_json(
        tmp_path / "embase.json",
        _embase_json(Q, [
            {"pmid": "1", "doi": "10.g/1"},   # gold match
            {"pmid": "2", "doi": "10.g/2"},   # gold match
            {"pmid": "99", "doi": "10.g/99"}, # not in gold
        ]),
    )

    rows = _run_score_queries(
        tmp_path=tmp_path,
        providers=[_FakePubMed([]), EmbaseLocalProvider(str(embase_file))],
        provider_queries={"pubmed": Q, "embase": Q},
        gold_rows=gold,
        use_multi_key=True,
    )

    embase_row = _db_row(rows, "embase")
    assert int(embase_row["TP"]) == 2, f"Embase TP should be 2, got {embase_row['TP']}"
    assert int(embase_row["gold_size"]) == 4, f"gold_size should be 4, got {embase_row['gold_size']}"
    assert float(embase_row["recall"]) == pytest.approx(0.5), (
        f"Embase recall should be 0.5 (2/4), got {embase_row['recall']}"
    )
    assert int(embase_row["results_count"]) == 3, (
        f"Embase results_count should be 3, got {embase_row['results_count']}"
    )
    print(
        f"PASS test_embase_partial_recall: TP={embase_row['TP']}, "
        f"recall={embase_row['recall']}, gold_size={embase_row['gold_size']}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# Test 9 — Embase DOI-only records (PMID absent): still scores via DOI Layer 1
# ══════════════════════════════════════════════════════════════════════════════


def test_embase_doi_only_records(tmp_path):
    """
    Some Embase exports include only DOI (no PMID). These should still match via
    DOI Layer 1 in set_metrics_row_level. id_type='pmid' does not prevent DOI matching
    — it only controls which id set flows into db_pmids_for_matching.
    """
    Q = "doi only records"
    gold_doi = "10.doi_only/42"
    gold_pmid = "42000"

    embase_file = _write_json(
        tmp_path / "embase.json",
        # Embase record has DOI but NO pmid (empty string → treated as absent)
        _embase_json(Q, [{"pmid": "", "doi": gold_doi}]),
    )

    rows = _run_score_queries(
        tmp_path=tmp_path,
        providers=[_FakePubMed([]), EmbaseLocalProvider(str(embase_file))],
        provider_queries={"pubmed": Q, "embase": Q},
        gold_rows=[(gold_pmid, gold_doi)],
        use_multi_key=True,
    )

    embase_row = _db_row(rows, "embase")
    assert int(embase_row["TP"]) == 1, (
        f"Embase TP should be 1 via DOI-only match, got {embase_row['TP']}"
    )
    assert int(embase_row["matches_by_doi_only"]) == 1, (
        f"matches_by_doi_only should be 1, got {embase_row['matches_by_doi_only']}"
    )
    print(f"PASS test_embase_doi_only_records: TP={embase_row['TP']}")


# ══════════════════════════════════════════════════════════════════════════════
# Test 10 — W3.4 interaction: Article equality across PubMed–Embase in split-by-provider
# ══════════════════════════════════════════════════════════════════════════════


def test_w34_article_equality_pubmed_embase_split(tmp_path):
    """
    W3.4 per-provider pool mode: when PubMed and Embase both return Article(P, D)
    (same PMID and DOI), the two Article objects are equal and hash-equal, so
    consensus_k2 correctly counts the article as appearing in ≥2 provider pools.

    This verifies that _articles_from_provider_details_per_source produces the
    correct Article objects from Embase's linked_records.
    """
    # Simulate provider_details as written by _execute_query_bundle (W2.2 format)
    provider_details = {
        "pubmed": {
            "linked_records": [{"pmid": "100", "doi": "10.shared/100"}],
            "id_type": "pmid",
        },
        "embase": {
            "linked_records": [{"pmid": "100", "doi": "10.shared/100"}],  # same article
            "id_type": "pmid",
        },
        "scopus": {
            "linked_records": [{"pmid": None, "doi": "10.scopus_only/1"}],  # different article
            "id_type": "scopus_id",
        },
    }

    pools = _articles_from_provider_details_per_source(provider_details, "Q1")
    assert "pubmed_Q1" in pools and "embase_Q1" in pools

    shared_article = Article(pmid="100", doi="10.shared/100")

    # The shared article must appear in both pools
    assert shared_article in pools["pubmed_Q1"], (
        f"shared_article missing from pubmed_Q1: {pools['pubmed_Q1']}"
    )
    assert shared_article in pools["embase_Q1"], (
        f"shared_article missing from embase_Q1: {pools['embase_Q1']}"
    )

    # Confirm hash equality: this is why consensus_k2 counts it correctly
    pm_articles = {a for a in pools["pubmed_Q1"] if a.pmid == "100"}
    em_articles = {a for a in pools["embase_Q1"] if a.pmid == "100"}
    assert pm_articles and em_articles
    pm_art = next(iter(pm_articles))
    em_art = next(iter(em_articles))
    assert pm_art == em_art, (
        f"PubMed and Embase Article objects are not equal: {pm_art} vs {em_art}"
    )
    assert hash(pm_art) == hash(em_art), (
        f"Hash mismatch: {hash(pm_art)} vs {hash(em_art)}"
    )

    # consensus_k2 with topk=3 should include the shared article
    result = consensus_k_articles(pools, topk=3, k=2)
    assert shared_article in result, (
        f"shared_article should be in consensus_k2 result: {result}"
    )
    # Scopus-only article should NOT be in consensus (only 1 vote)
    scopus_only = Article(pmid=None, doi="10.scopus_only/1")
    assert scopus_only not in result, (
        f"scopus_only article should NOT be in consensus_k2 (only 1 vote): {result}"
    )
    print(
        f"PASS test_w34_article_equality_pubmed_embase_split: "
        f"shared_in_consensus={shared_article in result}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# Test 11 — W3.4 documented limitation: PMID-only PubMed ≠ PMID+DOI Embase
# ══════════════════════════════════════════════════════════════════════════════


def test_w34_known_limitation_pmid_only_vs_pmid_doi(tmp_path):
    """
    KNOWN LIMITATION (W4.4 scope, not fixed in W3):

    When PubMed has a PMID-only record (DOI absent from PubMed XML, CrossRef
    enrichment W2.1b not yet applied) AND Embase has the same article WITH a DOI,
    Article.__hash__ uses DOI as primary key:

        PubMed:  Article(pmid='P', doi=None)       → hash = hash(('pmid', 'P'))
        Embase:  Article(pmid='P', doi='10.x/y')   → hash = hash(('doi', '10.x/y'))

    Different hashes → NOT equal → consensus_k2 does NOT count them as the same
    article, even though they represent the same real-world paper.

    This test asserts the CURRENT behavior (limitation) so we will notice if
    something inadvertently changes it.  The fix is W4.4 (fuzzy ArticleRegistry
    merge pass) which is out of scope for W3.3.
    """
    # PubMed: PMID-only (no DOI in XML)
    provider_details_pmid_only_pubmed = {
        "pubmed": {
            "linked_records": [{"pmid": "P", "doi": None}],
            "id_type": "pmid",
        },
        "embase": {
            "linked_records": [{"pmid": "P", "doi": "10.has_doi/P"}],
            "id_type": "pmid",
        },
    }

    pools = _articles_from_provider_details_per_source(
        provider_details_pmid_only_pubmed, "Q1"
    )

    pubmed_art = Article(pmid="P", doi=None)
    embase_art = Article(pmid="P", doi="10.has_doi/P")

    # Confirm they are NOT equal (hash uses DOI as primary key when present)
    assert hash(pubmed_art) != hash(embase_art), (
        "Unexpected: PubMed PMID-only and Embase PMID+DOI articles have same hash. "
        "Has the Article hash function changed?"
    )
    assert pubmed_art != embase_art, (
        "Unexpected: PubMed PMID-only == Embase PMID+DOI. "
        "Has Article.__eq__ changed?"
    )

    # Consequence: consensus_k2 does NOT include this article
    result = consensus_k_articles(pools, topk=2, k=2)
    assert pubmed_art not in result, (
        "Unexpected: PMID-only article reached consensus_k2 "
        "(should require W4.4 to fix this)."
    )
    assert embase_art not in result, (
        "Unexpected: Embase PMID+DOI article reached consensus_k2 without PubMed "
        "agreement (should require W4.4 to fix)."
    )

    print(
        "PASS test_w34_known_limitation_pmid_only_vs_pmid_doi: "
        f"pubmed_art={pubmed_art}, embase_art={embase_art}, "
        "correctly NOT in consensus (W4.4 limitation documented)"
    )


# ── run as script ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import pathlib
    import tempfile as _tf

    _tmp = pathlib.Path(_tf.mkdtemp())
    print("Running W3.3 tests...\n")

    _t = _tmp / "t1"; _t.mkdir()
    test_four_provider_row_structure(_t)

    _t = _tmp / "t2"; _t.mkdir()
    test_embase_tp_via_doi_layer1(_t)

    _t = _tmp / "t3"; _t.mkdir()
    test_embase_tp_via_pmid_layer2_fallback(_t)

    _t = _tmp / "t4"; _t.mkdir()
    test_embase_unique_article_lifts_combined_recall(_t)

    _t = _tmp / "t5"; _t.mkdir()
    test_embase_nnr_proxy(_t)

    _t = _tmp / "t6"; _t.mkdir()
    test_embase_query_num_multi_bundle(_t)

    _t = _tmp / "t7"; _t.mkdir()
    test_embase_no_match_tp_zero(_t)

    _t = _tmp / "t8"; _t.mkdir()
    test_embase_partial_recall(_t)

    _t = _tmp / "t9"; _t.mkdir()
    test_embase_doi_only_records(_t)

    test_w34_article_equality_pubmed_embase_split(_tmp / "t10")

    _t = _tmp / "t11"; _t.mkdir()
    test_w34_known_limitation_pmid_only_vs_pmid_doi(_t)

    print("\nAll W3.3 tests passed.")
