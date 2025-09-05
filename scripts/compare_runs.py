#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compare two runs (A vs B): PMIDs overlap, summary metrics, and prompt/comment headers.

Usage:
  python scripts/compare_runs.py \
    --runA benchmark_A --runB benchmark_B \
    --gold Gold_list__all_included_studies_.csv

Expects files:
  runX/summary_*.csv and runX/details_*.json
Outputs to stdout and a JSON report in runX_vs_runY/
"""

from __future__ import annotations
import argparse, csv, glob, json, os, re


def load_summary(path_glob: str):
    files = sorted(glob.glob(path_glob))
    rows = []
    for p in files:
        with open(p, newline='') as f:
            for row in csv.DictReader(f):
                rows.append(row)
    return rows


def load_pmids_details(path_glob: str) -> set[str]:
    files = sorted(glob.glob(path_glob))
    pmids = set()
    for p in files:
        with open(p) as f:
            data = json.load(f)
        # details json structure: {hash: {query, pmids, ...}}
        if isinstance(data, dict):
            for _k, item in data.items():
                if isinstance(item, dict) and 'pmids' in item:
                    pmids.update(str(x) for x in item.get('pmids', []))
    return pmids


def load_gold_pmids(gold_csv: str) -> set[str]:
    pmids = set()
    with open(gold_csv, newline='') as f:
        for line in f:
            for tok in re.split(r'[^0-9]+', line.strip()):
                if tok:
                    pmids.add(tok)
    return pmids


def main():
    ap = argparse.ArgumentParser(description='Compare two runs A vs B')
    ap.add_argument('--runA', required=True)
    ap.add_argument('--runB', required=True)
    ap.add_argument('--gold', help='Gold CSV to compute TP/FP/FN deltas')
    args = ap.parse_args()

    sumA = load_summary(os.path.join(args.runA, 'summary_*.csv'))
    sumB = load_summary(os.path.join(args.runB, 'summary_*.csv'))
    pmA = load_pmids_details(os.path.join(args.runA, 'details_*.json'))
    pmB = load_pmids_details(os.path.join(args.runB, 'details_*.json'))

    inter = pmA & pmB
    onlyA = pmA - pmB
    onlyB = pmB - pmA

    report = {
        'counts': {
            'A_total': len(pmA), 'B_total': len(pmB), 'A∩B': len(inter), 'A−B': len(onlyA), 'B−A': len(onlyB)
        },
        'overlap_coefficient': len(inter) / max(1, min(len(pmA), len(pmB))),
        'jaccard': len(inter) / max(1, len(pmA | pmB)),
        'summary_head_A': sumA[:5],
        'summary_head_B': sumB[:5],
    }

    if args.gold:
        gold = load_gold_pmids(args.gold)
        tpA = len(pmA & gold); fpA = len(pmA - gold); fnA = len(gold - pmA)
        tpB = len(pmB & gold); fpB = len(pmB - gold); fnB = len(gold - pmB)
        report['gold'] = {
            'A': {'TP': tpA, 'FP': fpA, 'FN': fnA},
            'B': {'TP': tpB, 'FP': fpB, 'FN': fnB},
        }

    outdir = f"{args.runA}_vs_{args.runB}"
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, 'report.json'), 'w') as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
