#!/usr/bin/env python3
"""
rescore_comparison.py — Rescore existing details JSONs with OLD vs NEW algorithm.

Reads cached details_{timestamp}.json files (no API calls) and applies:
  OLD: set_metrics_multi_key() — flat-set matching, PMID fallback gated on
       gold_articles_pmid_only > 0 (always 0 when all gold have DOIs)
  NEW: set_metrics_row_level() — per-article row matching, always tries PMID
       fallback after DOI miss

Purpose: isolate the algorithmic impact of W2.3 (Issue 1 fix) from query
differences, by rescoring the SAME API results with both algorithms.

Usage:
    python scripts/rescore_comparison.py \
        --details  benchmark_outputs/Lehner_2022/details_20260206-135814.json \
        --gold     OldResults/V1/studies/Lehner_2022/gold_pmids_Lehner_2022_detailed.csv \
        --study    Lehner_2022

    python scripts/rescore_comparison.py \
        --details  benchmark_outputs/ai_2022/query_01/details_20260218-120658.json \
                   benchmark_outputs/ai_2022/query_02/details_20260218-121008.json \
                   ... \
        --gold     studies/ai_2022/gold_pmids_ai_2022_detailed.csv \
        --study    ai_2022
"""
import argparse
import csv
import json
import sys
import os
from pathlib import Path

# Allow import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_sr_select_and_score import (
    set_metrics_multi_key,
    set_metrics_row_level,
    load_gold_multi_key,
    load_gold_rows,
)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _norm_doi(d: str) -> str:
    return d.strip().lower() if d else ''


def _extract_provider_sets(pdata: dict) -> tuple[set, set]:
    """Return (pmids, dois) from a provider detail block.

    Handles both old format (retrieved_ids + retrieved_dois) and
    future linked_records format.
    """
    if 'linked_records' in pdata:
        pmids, dois = set(), set()
        for rec in pdata['linked_records']:
            if rec.get('pmid'):
                pmids.add(str(rec['pmid']))
            if rec.get('doi'):
                dois.add(_norm_doi(rec['doi']))
        return pmids, dois

    id_type = pdata.get('id_type', 'id')
    raw_ids = set(str(x) for x in pdata.get('retrieved_ids', []) if x)
    raw_dois = {_norm_doi(d) for d in pdata.get('retrieved_dois', []) if d}

    if id_type == 'pmid':
        return raw_ids, raw_dois
    else:
        # scopus_ids / wos_uids: pass empty PMID set to avoid false matches
        return set(), raw_dois


def _load_details(paths: list[str]) -> list[dict]:
    """Load and concatenate all query bundles from one or more details JSON files."""
    bundles = []
    for p in paths:
        with open(p) as f:
            data = json.load(f)
        if isinstance(data, list):
            bundles.extend(data)
        elif isinstance(data, dict):
            bundles.append(data)
    return bundles


# ──────────────────────────────────────────────────────────────────────────────
# Per-bundle scoring
# ──────────────────────────────────────────────────────────────────────────────

def score_bundle(bundle: dict,
                 gold_rows,
                 gold_pmids: set, gold_dois: set,
                 query_num: int) -> list[dict]:
    """
    Score one query bundle using BOTH old and new algorithms.

    Returns a list of row dicts (one per database + one COMBINED per algorithm).
    """
    rows = []
    provider_details = bundle.get('provider_details', {})

    # Compute COMBINED pmids/dois across all providers
    combined_pmids: set = set()
    combined_dois: set = set()
    per_db: dict[str, tuple[set, set]] = {}           # provider → (pmids, dois)

    for pname, pdata in provider_details.items():
        if not isinstance(pdata, dict) or 'error' in pdata:
            continue
        pmids, dois = _extract_provider_sets(pdata)
        per_db[pname] = (pmids, dois)
        combined_pmids |= pmids
        combined_dois |= dois

    # ── Score each row (per-db + COMBINED) ──────────────────────────────────
    targets: dict[str, tuple[set, set]] = {**per_db, 'COMBINED': (combined_pmids, combined_dois)}

    for db_name, (pmids, dois) in targets.items():
        # results_count: use the stored value for COMBINED, else DB-level count
        if db_name == 'COMBINED':
            results_count = bundle.get('results_count', max(len(pmids), len(dois)))
        else:
            pdata = provider_details.get(db_name, {})
            results_count = pdata.get('results_count', max(len(pmids), len(dois)))

        # ── OLD algorithm ───────────────────────────────────────────────────
        old_m = set_metrics_multi_key(pmids, dois, gold_pmids, gold_dois)

        # ── NEW algorithm ───────────────────────────────────────────────────
        new_m = set_metrics_row_level(pmids, dois, gold_rows)

        base = {
            'query_num': query_num,
            'database': db_name,
            'results_count': results_count,
            'gold_size_old': old_m['Gold'],
            'gold_size_new': new_m['Gold'],
        }
        rows.append({
            **base,
            'algorithm': 'OLD',
            'TP': old_m['TP'],
            'Recall': old_m['Recall'],
            'Precision': old_m['Precision'],
            'NNR': results_count / max(old_m['TP'], 1),
            'matches_by_doi': old_m.get('matches_by_doi', 0),
            'matches_by_pmid_fallback': old_m.get('matches_by_pmid_fallback', 0),
        })
        rows.append({
            **base,
            'algorithm': 'NEW',
            'TP': new_m['TP'],
            'Recall': new_m['Recall'],
            'Precision': new_m['Precision'],
            'NNR': results_count / max(new_m['TP'], 1),
            'matches_by_doi': new_m.get('matches_by_doi', 0),
            'matches_by_pmid_fallback': new_m.get('matches_by_pmid_fallback', 0),
        })

    return rows


# ──────────────────────────────────────────────────────────────────────────────
# Report
# ──────────────────────────────────────────────────────────────────────────────

def _pct(v) -> str:
    return f"{v*100:.1f}%"


def print_report(all_rows: list[dict], study: str, gold_rows, gold_pmids, gold_dois):
    """Print a structured comparison report to stdout."""
    print()
    print("=" * 80)
    print(f"  RESCORE COMPARISON  —  {study}")
    print("=" * 80)
    print(f"  Gold standard : {len(gold_rows)} articles  |  "
          f"{len(gold_pmids)} with PMID  |  {len(gold_dois)} with DOI")
    pmid_only_count = sum(1 for g in gold_rows if g.pmid and not g.doi)
    doi_only_count  = sum(1 for g in gold_rows if g.doi and not g.pmid)
    both_count      = sum(1 for g in gold_rows if g.pmid and g.doi)
    neither_count   = sum(1 for g in gold_rows if not g.pmid and not g.doi)
    print(f"    PMID+DOI: {both_count}  |  DOI-only: {doi_only_count}  |  "
          f"PMID-only: {pmid_only_count}  |  neither: {neither_count}")
    print()

    # Separate old/new rows
    old_rows = {(r['query_num'], r['database']): r for r in all_rows if r['algorithm'] == 'OLD'}
    new_rows = {(r['query_num'], r['database']): r for r in all_rows if r['algorithm'] == 'NEW'}

    # Get unique query_nums
    query_nums = sorted(set(r['query_num'] for r in all_rows))

    # Collect all databases seen
    all_dbs = list(dict.fromkeys(
        r['database']
        for r in all_rows
        if r['algorithm'] == 'OLD'
    ))
    # Put COMBINED first, then alphabetical
    all_dbs = ['COMBINED'] + sorted(d for d in all_dbs if d != 'COMBINED')

    changed_cases = []

    for qnum in query_nums:
        print(f"  ─── Query {qnum} ───────────────────────────────────────────────────────")
        print(f"  {'Database':<18} {'Results':>8}  {'OLD TP':>6} {'Rec':>7}  "
              f"{'NEW TP':>6} {'Rec':>7}  {'ΔTP':>5} {'ΔRec':>8}  {'NNR_old':>8} {'NNR_new':>8}")
        print(f"  {'-'*18} {'-'*8}  {'-'*6} {'-'*7}  {'-'*6} {'-'*7}  {'-'*5} {'-'*8}  {'-'*8} {'-'*8}")

        for db in all_dbs:
            key = (qnum, db)
            if key not in old_rows:
                continue
            o = old_rows[key]
            n = new_rows.get(key, o)

            delta_tp = n['TP'] - o['TP']
            delta_rec = n['Recall'] - o['Recall']
            flag = " ◄ CHANGE" if delta_tp != 0 else ""

            delta_rec_str = f"{delta_rec*100:+.1f}%"
            print(f"  {db:<18} {o['results_count']:>8}  "
                  f"{o['TP']:>6} {_pct(o['Recall']):>7}  "
                  f"{n['TP']:>6} {_pct(n['Recall']):>7}  "
                  f"{delta_tp:>+5} {delta_rec_str:>8}  "
                  f"{o['NNR']:>8.1f} {n['NNR']:>8.1f}"
                  f"{flag}")

            if delta_tp != 0:
                changed_cases.append({
                    'study': study, 'query': qnum, 'db': db,
                    'delta_tp': delta_tp, 'delta_recall': delta_rec,
                    'old_tp': o['TP'], 'new_tp': n['TP'],
                    'old_recall': o['Recall'], 'new_recall': n['Recall'],
                    'gold': o['gold_size_new'],
                })

        print()

    # Summary table
    print("=" * 80)
    print("  SUMMARY — Cases where OLD ≠ NEW (W2.3 impact)")
    print("=" * 80)
    if not changed_cases:
        print("  No difference found between OLD and NEW algorithms on this data.")
        print("  (All gold articles were retrievable by DOI alone in every query)")
    else:
        print(f"  {'Study':<20} {'Q':>3} {'DB':<18} {'OLD_TP':>6} → {'NEW_TP':>6}  {'ΔTP':>4}  OLD_Rec → NEW_Rec")
        print(f"  {'-'*20} {'-'*3} {'-'*18} {'-'*6}   {'-'*6}  {'-'*4}  {'-'*19}")
        for c in changed_cases:
            print(f"  {c['study']:<20} {c['query']:>3} {c['db']:<18} "
                  f"{c['old_tp']:>6}   {c['new_tp']:>6}  "
                  f"{c['delta_tp']:>+4}  "
                  f"{_pct(c['old_recall'])} → {_pct(c['new_recall'])}")

    # Gold article breakdown for COMBINED across queries
    print()
    print("=" * 80)
    print("  COMBINED per-query at a glance")
    print("=" * 80)
    print(f"  {'Q':>3}  {'Results':>8}  {'OLD_TP':>6} {'OLD_Rec':>8}  {'NEW_TP':>6} {'NEW_Rec':>8}  "
          f"{'PMID_fallback_gains':>20}")
    print(f"  {'-'*3}  {'-'*8}  {'-'*6} {'-'*8}  {'-'*6} {'-'*8}  {'-'*20}")
    for qnum in query_nums:
        key = (qnum, 'COMBINED')
        if key not in old_rows:
            continue
        o = old_rows[key]
        n = new_rows.get(key, o)
        pmid_gains = n.get('matches_by_pmid_fallback', 0)
        print(f"  {qnum:>3}  {o['results_count']:>8}  "
              f"{o['TP']:>6} {_pct(o['Recall']):>8}  "
              f"{n['TP']:>6} {_pct(n['Recall']):>8}  "
              f"{pmid_gains:>20}")

    print()
    print("  Notes:")
    print("  - OLD = set_metrics_multi_key() with PMID fallback gated on gold_articles_pmid_only>0")
    print("  - NEW = set_metrics_row_level() with per-article PMID fallback always active")
    print("  - gold_size_old: denominator used by old algorithm (may double-count identifiers)")
    print(f"  - gold_size_new: {len(gold_rows)} (number of unique gold articles)")
    print()


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--details', nargs='+', required=True,
                    help='Path(s) to details_*.json files to rescore')
    ap.add_argument('--gold', required=True,
                    help='Path to gold CSV (detailed format with pmid + doi columns)')
    ap.add_argument('--study', default='unknown',
                    help='Study name for display')
    ap.add_argument('--outcsv', default=None,
                    help='Optional: save comparison rows to CSV')
    args = ap.parse_args()

    # ── Load gold standard (both old-format flat sets and new row list) ──────
    gold_pmids, gold_dois = load_gold_multi_key(args.gold)
    gold_rows = load_gold_rows(args.gold)

    # ── Load all query bundles ───────────────────────────────────────────────
    bundles = _load_details(args.details)

    all_rows = []
    for idx, bundle in enumerate(bundles, start=1):
        rows = score_bundle(bundle, gold_rows, gold_pmids, gold_dois, query_num=idx)
        all_rows.extend(rows)

    # ── Print report ─────────────────────────────────────────────────────────
    print_report(all_rows, args.study, gold_rows, gold_pmids, gold_dois)

    # ── Optional CSV output ──────────────────────────────────────────────────
    if args.outcsv:
        with open(args.outcsv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"  Saved comparison CSV → {args.outcsv}")


if __name__ == '__main__':
    main()
