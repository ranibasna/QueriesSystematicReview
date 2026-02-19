"""W2.3 unit tests: load_gold_rows + set_metrics_row_level.

Core purpose of W2.3: replace flat-set matching with per-article (row-level) matching
so the PMID fallback fires on a per-article basis rather than only when gold contains
articles that entirely lack a DOI.

Old behaviour (set_metrics_multi_key):
  - PMID fallback disabled when `len(gold_pmids) == len(gold_dois)` (all gold have DOIs)
  - A gold article whose DOI was NOT retrieved but whose PMID WAS retrieved → MISS

New behaviour (set_metrics_row_level):
  - For each gold article independently: TP if DOI in retrieved_dois OR PMID in retrieved_pmids
  - Above scenario → TP via PMID fallback

Tests also confirm: same return-key names as set_metrics_multi_key (drop-in compat),
correct precision/recall formulae, DOI case-insensitivity, and load_gold_rows parsing.
"""
import csv
import io
import os
import sys
import tempfile

sys.path.insert(0, "/Users/ra1077ba/Documents/DataScience/GU/Daniil/LLM/QueriesSystematicReview")
from llm_sr_select_and_score import GoldArticle, load_gold_rows, set_metrics_row_level, set_metrics_multi_key


# ── Helpers ───────────────────────────────────────────────────────────────────

def gold(*rows):
    """Shorthand: gold(('P1','10.a/1'), ('P2','10.a/2'), ('P3', None))."""
    return [GoldArticle(pmid=p, doi=d) for p, d in rows]


def write_gold_csv(rows, include_doi=True):
    """Write a temp gold CSV and return its path."""
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                      delete=False, newline='', encoding='utf-8')
    w = csv.writer(tmp)
    if include_doi:
        w.writerow(['pmid', 'doi', 'title'])
        for pmid, doi in rows:
            w.writerow([pmid, doi or '', f'Title for {pmid}'])
    else:
        # Simple format: no header, just PMIDs
        for pmid, _ in rows:
            w.writerow([pmid])
    tmp.close()
    return tmp.name


# ── Section 1: set_metrics_row_level correctness ─────────────────────────────

def test_all_matched_by_doi():
    """All gold articles retrieved via DOI → TP = 3, Recall = 1.0."""
    gold_rows = gold(('P1', '10.a/1'), ('P2', '10.a/2'), ('P3', '10.a/3'))
    m = set_metrics_row_level({'P1', 'P2', 'P3'}, {'10.a/1', '10.a/2', '10.a/3'}, gold_rows)
    assert m['TP'] == 3, m['TP']
    assert abs(m['Recall'] - 1.0) < 1e-9, m['Recall']
    assert m['matches_by_doi'] == 3
    assert m['matches_by_pmid_fallback'] == 0
    print("PASS test_all_matched_by_doi")


def test_pmid_fallback_fires_per_article():
    """
    THE KEY W2.3 TEST.

    Gold: 3 articles, all have DOIs.
    Retrieved: all 3 PMIDs, but only 2 DOIs. Article P3 DOI not retrieved, PMID retrieved.

    Old set_metrics_multi_key: gold_articles_pmid_only = max(0, 3-3) = 0
      → fallback disabled → TP = 2  (miss on P3)

    New set_metrics_row_level: tests P3 individually:
      doi_matched = '10.a/3' in {'10.a/1','10.a/2'} → False
      pmid_matched = 'P3' in {'P1','P2','P3'} → True
      → TP via PMID fallback → TP = 3
    """
    gold_rows = gold(('P1', '10.a/1'), ('P2', '10.a/2'), ('P3', '10.a/3'))

    # Retrieved: all PMIDs, only 2 DOIs (P3's DOI absent, e.g. not in PubMed XML)
    retrieved_pmids = {'P1', 'P2', 'P3'}
    retrieved_dois  = {'10.a/1', '10.a/2'}          # P3 DOI missing

    new_m = set_metrics_row_level(retrieved_pmids, retrieved_dois, gold_rows)
    old_m = set_metrics_multi_key(
        retrieved_pmids, retrieved_dois,
        {'P1', 'P2', 'P3'}, {'10.a/1', '10.a/2', '10.a/3'}
    )

    # New: TP=3
    assert new_m['TP'] == 3, f"W2.3 should give TP=3, got {new_m['TP']}"
    assert new_m['matches_by_pmid_fallback'] == 1
    assert abs(new_m['Recall'] - 1.0) < 1e-9

    # Old: TP=2 (demonstrates the bug being fixed)
    assert old_m['TP'] == 2, f"Old approach should give TP=2 (the bug), got {old_m['TP']}"
    assert old_m['matches_by_pmid_fallback'] == 0

    print("PASS test_pmid_fallback_fires_per_article")
    print(f"  W2.3 TP={new_m['TP']} (correct), old TP={old_m['TP']} (bug fixed)")


def test_missed_completely():
    """Article retrieved by neither DOI nor PMID → miss."""
    gold_rows = gold(('P1', '10.a/1'), ('P_miss', '10.miss/x'))
    m = set_metrics_row_level({'P1'}, {'10.a/1'}, gold_rows)
    assert m['TP'] == 1, m['TP']
    assert abs(m['Recall'] - 0.5) < 1e-9, m['Recall']
    print("PASS test_missed_completely")


def test_doi_case_insensitive():
    """DOI matching is case-insensitive."""
    gold_rows = gold(('P1', '10.ABC/XYZ'))  # uppercase in gold
    m = set_metrics_row_level(set(), {'10.abc/xyz'}, gold_rows)  # lowercase retrieved
    assert m['TP'] == 1, m['TP']
    assert m['matches_by_doi'] == 1
    print("PASS test_doi_case_insensitive")


def test_pmid_only_gold_article():
    """Gold article with PMID but no DOI: PMID match still works."""
    gold_rows = gold(('P1', None))
    m = set_metrics_row_level({'P1'}, {'10.irrelevant/x'}, gold_rows)
    assert m['TP'] == 1
    assert m['matches_by_pmid_fallback'] == 1
    print("PASS test_pmid_only_gold_article")


def test_doi_takes_priority_over_pmid():
    """If both DOI and PMID match, it counts as a DOI match (not double-counted)."""
    gold_rows = gold(('P1', '10.a/1'))
    m = set_metrics_row_level({'P1'}, {'10.a/1'}, gold_rows)
    assert m['TP'] == 1
    assert m['matches_by_doi'] == 1
    assert m['matches_by_pmid_fallback'] == 0
    print("PASS test_doi_takes_priority_over_pmid")


def test_empty_gold():
    """Empty gold → TP=0, Recall=0, no division by zero."""
    m = set_metrics_row_level({'P1'}, {'10.a/1'}, [])
    assert m['TP'] == 0
    assert m['Gold'] == 0
    assert m['Recall'] == 0.0
    print("PASS test_empty_gold")


def test_empty_retrieved():
    """Nothing retrieved → TP=0, Recall=0."""
    gold_rows = gold(('P1', '10.a/1'))
    m = set_metrics_row_level(set(), set(), gold_rows)
    assert m['TP'] == 0
    assert m['Recall'] == 0.0
    print("PASS test_empty_retrieved")


def test_precision_with_extra_retrieved():
    """1 gold article; retrieve 1 correct + 9 extra DOIs → Precision = 1/10."""
    gold_rows = gold(('P1', '10.g/1'))
    extra_dois = {f'10.x/{i}' for i in range(9)} | {'10.g/1'}
    m = set_metrics_row_level(set(), extra_dois, gold_rows)
    assert m['TP'] == 1
    assert abs(m['Precision'] - 1/10) < 1e-9
    print("PASS test_precision_with_extra_retrieved")


def test_return_keys_match_set_metrics_multi_key():
    """set_metrics_row_level returns all keys that set_metrics_multi_key returns."""
    old_required_keys = {
        'TP', 'Retrieved', 'Gold', 'Precision', 'Recall', 'F1', 'Jaccard', 'OverlapCoeff',
        'matches_by_doi', 'matches_by_pmid_fallback',
        'matched_dois', 'matched_pmids_fallback',
        'gold_articles_with_doi', 'gold_articles_pmid_only', 'pmid_only_warning',
        'retrieved_pmids_count', 'retrieved_dois_count',
    }
    gold_rows = gold(('P1', '10.a/1'), ('P2', '10.a/2'))
    m = set_metrics_row_level({'P1'}, {'10.a/1'}, gold_rows)
    missing = old_required_keys - set(m.keys())
    assert not missing, f"Missing keys: {missing}"
    print("PASS test_return_keys_match_set_metrics_multi_key:", sorted(m.keys()))


def test_matched_dois_set_contents():
    """`matched_dois` contains exactly the DOIs of gold articles matched by DOI."""
    gold_rows = gold(('P1', '10.a/1'), ('P2', '10.a/2'), ('P3', '10.a/3'))
    m = set_metrics_row_level({'P1', 'P2', 'P3'}, {'10.a/1', '10.a/3'}, gold_rows)
    # P1 and P3 matched by DOI; P2 matched by PMID fallback
    assert m['matched_dois'] == {'10.a/1', '10.a/3'}, m['matched_dois']
    assert m['matched_pmids_fallback'] == {'P2'}, m['matched_pmids_fallback']
    assert m['matches_by_doi'] == 2
    assert m['matches_by_pmid_fallback'] == 1
    print("PASS test_matched_dois_set_contents")


def test_no_double_count_when_both_match():
    """When both DOI and PMID are in retrieved sets, article counted once (DOI priority)."""
    gold_rows = gold(('P1', '10.a/1'))
    m = set_metrics_row_level({'P1'}, {'10.a/1'}, gold_rows)
    assert m['TP'] == 1, f"Should be 1, not {m['TP']}"
    assert m['matches_by_doi'] == 1
    assert m['matches_by_pmid_fallback'] == 0
    print("PASS test_no_double_count_when_both_match")


def test_all_missed():
    """No gold article matches → TP=0, Recall=0."""
    gold_rows = gold(('P1', '10.a/1'), ('P2', '10.a/2'))
    m = set_metrics_row_level({'P_other'}, {'10.other/x'}, gold_rows)
    assert m['TP'] == 0
    assert m['Recall'] == 0.0
    assert m['matches_by_doi'] == 0
    assert m['matches_by_pmid_fallback'] == 0
    print("PASS test_all_missed")


def test_f1_and_jaccard_values():
    """Verify F1 and Jaccard with known values (4 gold, 2 TP, 4 retrieved)."""
    # 2 TP, 2 miss, 2 FP
    # Precision = 2/4 = 0.5, Recall = 2/4 = 0.5, F1 = 0.5
    gold_rows = gold(('P1','10.a/1'),('P2','10.a/2'),('P3','10.a/3'),('P4','10.a/4'))
    m = set_metrics_row_level(
        {'P1','P2','Px','Py'},
        {'10.a/1','10.a/2','10.x/1','10.x/2'},
        gold_rows
    )
    assert m['TP'] == 2, m['TP']
    assert abs(m['Precision'] - 0.5) < 1e-6, m['Precision']
    assert abs(m['Recall'] - 0.5) < 1e-6, m['Recall']
    assert abs(m['F1'] - 0.5) < 1e-6, m['F1']
    print("PASS test_f1_and_jaccard_values", {k: round(v, 4) for k, v in m.items()
                                              if k in ('TP','Precision','Recall','F1','Jaccard')})


# ── Section 2: load_gold_rows parsing ─────────────────────────────────────────

def test_load_gold_rows_enhanced_format():
    """Enhanced CSV (pmid+doi columns) → correct GoldArticle rows."""
    data = [('111', '10.x/1'), ('222', '10.x/2'), ('333', None)]
    path = write_gold_csv(data, include_doi=True)
    try:
        rows = load_gold_rows(path)
        assert len(rows) == 3, len(rows)
        by_pmid = {r.pmid: r for r in rows}
        assert by_pmid['111'].doi == '10.x/1'
        assert by_pmid['222'].doi == '10.x/2'
        assert by_pmid['333'].doi is None  # empty DOI → None
        print("PASS test_load_gold_rows_enhanced_format:", rows)
    finally:
        os.unlink(path)


def test_load_gold_rows_simple_format():
    """Simple CSV (PMID only, no header) → GoldArticle(pmid=..., doi=None)."""
    data = [('111', None), ('222', None)]
    path = write_gold_csv(data, include_doi=False)
    try:
        rows = load_gold_rows(path)
        assert len(rows) == 2, len(rows)
        assert all(r.doi is None for r in rows)
        pmids = {r.pmid for r in rows}
        assert pmids == {'111', '222'}
        print("PASS test_load_gold_rows_simple_format:", rows)
    finally:
        os.unlink(path)


def test_load_gold_rows_doi_lowercased():
    """DOIs in load_gold_rows are lowercased."""
    data = [('111', '10.ABC/XYZ')]
    path = write_gold_csv(data, include_doi=True)
    try:
        rows = load_gold_rows(path)
        assert rows[0].doi == '10.abc/xyz', rows[0].doi
        print("PASS test_load_gold_rows_doi_lowercased:", rows)
    finally:
        os.unlink(path)


def test_load_gold_rows_empty_file():
    """Empty CSV → empty list, no exception."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                     delete=False, encoding='utf-8') as f:
        path = f.name
    try:
        rows = load_gold_rows(path)
        assert rows == [], rows
        print("PASS test_load_gold_rows_empty_file")
    finally:
        os.unlink(path)


# ── Section 3: Integration — load_gold_rows feeds set_metrics_row_level ──────

def test_integration_load_and_score():
    """Full round-trip: write CSV, load_gold_rows, set_metrics_row_level."""
    data = [('P1', '10.a/1'), ('P2', '10.a/2'), ('P3', '10.a/3')]
    path = write_gold_csv(data, include_doi=True)
    try:
        rows = load_gold_rows(path)
        # Retrieve P1+P2 by DOI; P3's DOI missing but PMID retrieved
        m = set_metrics_row_level({'P1', 'P2', 'P3'}, {'10.a/1', '10.a/2'}, rows)
        assert m['TP'] == 3, m['TP']
        assert m['matches_by_doi'] == 2
        assert m['matches_by_pmid_fallback'] == 1
        assert abs(m['Recall'] - 1.0) < 1e-9
        print("PASS test_integration_load_and_score")
    finally:
        os.unlink(path)


def test_integration_vs_old_on_ai2022_scenario():
    """
    Reproduce the ai_2022 scenario described in Issue 1.

    Gold: 12 articles, all with PMID+DOI.
    Retrieved (combined): 10 DOIs from gold + 4 PMIDs from gold.
    The 4 PMID-retrieved articles also have their DOIs retrieved → 0 new TPs from PMID.

    Then a second scenario: 2 of the 4 PMID articles have DOIs NOT retrieved
    → W2.3 adds 2 new TPs (PMID fallback); old approach misses them.
    """
    # Scenario 1: all 4 PubMed PMIDs also have DOIs retrieved (no net improvement)
    gold_rows = [GoldArticle(pmid=f'P{i}', doi=f'10.g/{i}') for i in range(12)]
    pubmed_dois   = {f'10.g/{i}' for i in range(4)}     # PubMed gets DOIs for 0-3
    scopus_dois   = {f'10.g/{i}' for i in range(10)}    # Scopus gets DOIs for 0-9
    combined_dois = pubmed_dois | scopus_dois             # 10 unique gold DOIs
    combined_pmids = {f'P{i}' for i in range(4)}          # all 4 PubMed PMIDs

    old_m = set_metrics_multi_key(combined_pmids, combined_dois,
                                   {g.pmid for g in gold_rows},
                                   {g.doi for g in gold_rows})
    new_m = set_metrics_row_level(combined_pmids, combined_dois, gold_rows)
    assert old_m['TP'] == new_m['TP'] == 10, f"Both should be 10: old={old_m['TP']}, new={new_m['TP']}"
    print("PASS test_integration_vs_old_on_ai2022_scenario (scenario 1: tied at 10 TP)")

    # Scenario 2: PubMed gets PMIDs for articles 10 and 11 whose DOIs are NOT retrieved
    combined_pmids_2 = {f'P{i}' for i in range(4)} | {'P10', 'P11'}
    old_m2 = set_metrics_multi_key(combined_pmids_2, combined_dois,
                                    {g.pmid for g in gold_rows},
                                    {g.doi for g in gold_rows})
    new_m2 = set_metrics_row_level(combined_pmids_2, combined_dois, gold_rows)
    assert old_m2['TP'] == 10, f"Old: should still be 10 (fallback disabled), got {old_m2['TP']}"
    assert new_m2['TP'] == 12, f"W2.3: should be 12 (P10+P11 via PMID fallback), got {new_m2['TP']}"
    assert new_m2['matches_by_pmid_fallback'] == 2
    print("PASS test_integration_vs_old_on_ai2022_scenario (scenario 2: W2.3=12, old=10)")
    print(f"  Old TP={old_m2['TP']}, W2.3 TP={new_m2['TP']} (+2 via PMID fallback)")


if __name__ == "__main__":
    # Section 1: set_metrics_row_level
    test_all_matched_by_doi()
    test_pmid_fallback_fires_per_article()
    test_missed_completely()
    test_doi_case_insensitive()
    test_pmid_only_gold_article()
    test_doi_takes_priority_over_pmid()
    test_empty_gold()
    test_empty_retrieved()
    test_precision_with_extra_retrieved()
    test_return_keys_match_set_metrics_multi_key()
    test_matched_dois_set_contents()
    test_no_double_count_when_both_match()
    test_all_missed()
    test_f1_and_jaccard_values()

    # Section 2: load_gold_rows
    test_load_gold_rows_enhanced_format()
    test_load_gold_rows_simple_format()
    test_load_gold_rows_doi_lowercased()
    test_load_gold_rows_empty_file()

    # Section 3: integration
    test_integration_load_and_score()
    test_integration_vs_old_on_ai2022_scenario()

    print()
    print("All W2.3 tests passed.")
