#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aggregate PMIDs from multiple queries using several ensemble strategies and optional
PROSPERO-aligned gates. Inputs are JSON details files (from score/select) or sealed files.

Usage (examples):
  python scripts/aggregate_queries.py \
    --inputs benchmark_outputs/details_*.json sealed_outputs/sealed_*.json \
    --outdir aggregates \
    --prospero-gates

  python scripts/aggregate_queries.py \
    --inputs benchmark_outputs/details_*.json \
    --topk 3 --consensus-k 2 --outdir aggregates

  python aggregate_queries.py \
    --inputs details_20250904-200512.json \
    --outdir aggregates_families \
    --families Population Sleep Intervention Design

  python aggregate_queries.py \
    --inputs details_20250904-200512.json \
    --outdir aggregates_weighted \
    --weights 1.0 0.7 0.5 0.5

    python scripts/aggregate_queries.py \
    --inputs benchmark_outputs/details_20250904-200512.json \
    --outdir aggregates \
    --topk 3 \
    --prospero-gates

    What two_stage_screen (the code just above this) is
        Stage 1: Take the union of the first topk queries (default topk=3).
        Stage 2: Apply PROSPERO-aligned text gates (MS + sleep + RCT + non-pharma) only if you pass --prospero-gates.
        There is no --two_stage_screen flag. The script always writes aggregates/two_stage_screen.txt; adding --prospero-gates decides whether Stage 2 filtering is applied.
        
        This writes: consensus_k2.txt, precision_gated_union.txt, weighted_vote.txt, concept_family_consensus.txt (if families provided), two_stage_screen.txt, time_stratified_hybrid.txt.
        Omit --prospero-gates if you want Stage 1 only (no filtering).
        Brief code walkthrough (relevant lines)
        stage1 = union of the first topk queries:
        stage1 = set().union(*[s for _, s in list(pmids_by_query.items())[:args.topk]])
        tss = two_stage_screen(stage1, args.prospero_gates)
        If filters_use_titles is False → return stage1 unchanged.
        If True → fetch titles/abstracts and keep only records passing passes_prospero_gates().
    
Outputs:
  - aggregates/consensus_k{K}.txt           (PMIDs appearing in >=K of top-K queries)
  - aggregates/precision_gated_union.txt    (Union filtered by protocol gates)
  - aggregates/weighted_vote.txt            (Weighted voting)
  - aggregates/concept_family_consensus.txt (By concept families)
  - aggregates/two_stage_screen.txt         (Stage1 broad -> Stage2 gates)
  - aggregates/time_stratified_hybrid.txt   (Split by year strategy)
  
What you’ll get (in aggregates/)

    consensus_k2.txt
    PMIDs that appear in at least 2 of the first top-3 queries. Good precision bump with small recall loss.
    precision_gated_union.txt
    Union of all PMIDs filtered by PROSPERO-aligned textual gates (MS + sleep + RCT signal + non-pharma keywords). If you omit --prospero-gates, this is just the union.
    weighted_vote.txt
    Union where each query contributes a weight; PMIDs whose total weight reaches the threshold are kept (default threshold ≈ median weight). Use --weights to tune.
    concept_family_consensus.txt
    If you provide --families with one label per query, keeps PMIDs that appear in at least 2 distinct families (e.g., Population and Design). Aligns with the protocol’s concept structure.
    two_stage_screen.txt
    Stage 1 = union of the first topk queries (default 3). Stage 2 = apply the PROSPERO gates (if --prospero-gates). This mimics a recall-first then filter workflow.
    time_stratified_hybrid.txt
    Approximate blend of “first half” vs “second half” queries to mimic MeSH-heavy vs text-heavy mixing when date metadata isn’t available. Useful as a diversity baseline.
"""

from __future__ import annotations
import argparse, glob, json, os, re, sys
from collections import Counter, defaultdict


def load_pmids_from_file(path: str) -> dict[str, set[str]]:
    pmids_by_query: dict[str, set[str]] = {}
    with open(path, 'r') as f:
        data = json.load(f)
    # Handle formats:
    # 1) sealed_*.json: single object with 'retrieved_pmids'
    # 2) details_*.json (dict): {id: {query, pmids}}
    # 3) details_*.json (list): [ {query, retrieved_pmids|pmids, ...}, ... ]
    if isinstance(data, dict) and 'retrieved_pmids' in data:
        q = data.get('query', f"sealed:{os.path.basename(path)}")
        pmids_by_query[q] = set(data.get('retrieved_pmids', []))
    elif isinstance(data, dict):
        for key, item in data.items():
            if isinstance(item, dict):
                pmids = item.get('pmids') or item.get('retrieved_pmids') or []
                if pmids:
                    q = item.get('query', key)
                    pmids_by_query[q] = set(pmids)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                pmids = item.get('pmids') or item.get('retrieved_pmids') or []
                if pmids:
                    q = item.get('query', f"item_{i}")
                    pmids_by_query[q] = set(pmids)
    return pmids_by_query


def load_all(inputs: list[str]) -> dict[str, set[str]]:
    merged: dict[str, set[str]] = {}
    paths: list[str] = []
    for pat in inputs:
        paths.extend(glob.glob(pat))
    for p in paths:
        for q, pmids in load_pmids_from_file(p).items():
            merged.setdefault(q, set()).update(pmids)
    return merged


def prospero_gate_predicates() -> list[re.Pattern]:
    # Protocol-aligned textual signals; keep lightweight and recall-friendly
    pats = [
        re.compile(r"\bmultiple sclerosis\b", re.I),
        re.compile(r"\bsleep\b|insomnia|sleep apnea|restless leg|narcolep|REM sleep behavior", re.I),
        re.compile(r"randomi[sz]ed|trial|placebo|randomly", re.I),
        re.compile(r"non[- ]?pharmacolog|non[- ]?invas|behavior|cognitive|exercise|rehabilitation|psychotherap|mindfulness|meditation", re.I),
    ]
    return pats


def fetch_min_titles(pmids: set[str]) -> dict[str, dict]:
    # Lazy import to avoid hard dependency; reuse existing script if present.
    try:
        from llm_sr_select_and_score import fetch_titles
    except Exception:
        return {}
    titles = {}
    for chunk in [list(pmids)[i:i+200] for i in range(0, len(pmids), 200)]:
        for rec in fetch_titles(chunk):
            pid = rec.get('pmid') or rec.get('PMID') or rec.get('pmid_str')
            if pid:
                titles[str(pid)] = rec
    return titles


def passes_prospero_gates(rec: dict) -> bool:
    text = ' '.join(str(rec.get(k,'')) for k in ('title','Title','abstract','Abstract'))
    if not text.strip():
        return False
    for pat in prospero_gate_predicates():
        if not pat.search(text):
            return False
    return True


def write_list(path: str, ids: set[str]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        for x in sorted(ids, key=lambda s: int(re.sub(r"\D","", s) or 0)):
            f.write(f"{x}\n")


def consensus_k(pmids_by_query: dict[str,set[str]], topk: int, k: int) -> set[str]:
    items = list(pmids_by_query.items())[:topk]
    cnt = Counter()
    for _, s in items:
        cnt.update(s)
    return {pid for pid, c in cnt.items() if c >= k}


def precision_gated_union(pmids_by_query: dict[str,set[str]], use_titles: bool) -> set[str]:
    universe = set().union(*pmids_by_query.values()) if pmids_by_query else set()
    if not use_titles:
        return universe
    meta = fetch_min_titles(universe)
    return {pid for pid in universe if pid in meta and passes_prospero_gates(meta[pid])}


def weighted_vote(pmids_by_query: dict[str,set[str]], weights: list[float]) -> set[str]:
    qs = list(pmids_by_query.items())
    w = weights or [1.0] * len(qs)
    total = defaultdict(float)
    for (i, (_q, s)) in enumerate(qs):
        wi = w[i] if i < len(w) else w[-1]
        for pid in s:
            total[pid] += wi
    # default threshold is median of weights
    thr = sorted(w)[len(w)//2] if w else 1.0
    return {pid for pid, score in total.items() if score >= thr}


def concept_family_consensus(pmids_by_family: dict[str, dict[str,set[str]]], required_families: int = 2) -> set[str]:
    # pmids_by_family: {family: {query: set(pmids)}}
    votes = Counter()
    families = list(pmids_by_family.keys())
    all_pmids = set().union(*[set().union(*pmids_by_family[fam].values()) for fam in families]) if families else set()
    for pid in all_pmids:
        hit_fams = sum(1 for fam in families if any(pid in s for s in pmids_by_family[fam].values()))
        if hit_fams >= required_families:
            votes[pid] += 1
    return set(votes.keys())


def two_stage_screen(high_recall: set[str], filters_use_titles: bool) -> set[str]:
    if not filters_use_titles:
        return high_recall
    meta = fetch_min_titles(high_recall)
    return {pid for pid in high_recall if pid in meta and passes_prospero_gates(meta[pid])}


def time_stratified_hybrid(pmids_by_query: dict[str,set[str]]) -> set[str]:
    # Without metadata dates, approximate by mixing top-half queries (treat as MeSH-heavy) and bottom-half (text-heavy)
    qs = list(pmids_by_query.items())
    mid = len(qs)//2
    a = set().union(*[s for _, s in qs[:mid]]) if mid else set()
    b = set().union(*[s for _, s in qs[mid:]]) if mid else set()
    return a.union(b)


def main():
    ap = argparse.ArgumentParser(description="Aggregate PMIDs from multiple query outputs")
    ap.add_argument('--inputs', nargs='+', required=True, help='details_*.json and/or sealed_*.json globs')
    ap.add_argument('--outdir', default='aggregates')
    ap.add_argument('--topk', type=int, default=3)
    ap.add_argument('--consensus-k', type=int, default=2)
    ap.add_argument('--prospero-gates', action='store_true', help='Filter using PROSPERO-aligned textual gates (requires fetch_titles)')
    ap.add_argument('--weights', nargs='*', type=float, help='Weights for weighted voting (order = as loaded)')
    ap.add_argument('--families', nargs='*', help='Family labels per query, same order as loaded (e.g., Population Sleep Intervention Design ...)')
    args = ap.parse_args()

    pmids_by_query = load_all(args.inputs)
    if not pmids_by_query:
        print('No inputs loaded', file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.outdir, exist_ok=True)

    # 1) consensus ≥K of top-K
    cset = consensus_k(pmids_by_query, args.topk, args.consensus_k)
    write_list(os.path.join(args.outdir, f'consensus_k{args.consensus_k}.txt'), cset)

    # 2) precision-gated union
    pgun = precision_gated_union(pmids_by_query, args.prospero_gates)
    write_list(os.path.join(args.outdir, 'precision_gated_union.txt'), pgun)

    # 3) weighted voting
    wv = weighted_vote(pmids_by_query, args.weights or [])
    write_list(os.path.join(args.outdir, 'weighted_vote.txt'), wv)

    # 4) concept-family consensus
    fams = args.families or []
    pmids_by_family: dict[str, dict[str,set[str]]] = defaultdict(dict)
    if fams and len(fams) == len(pmids_by_query):
        for (fam, (q, s)) in zip(fams, pmids_by_query.items()):
            pmids_by_family[fam][q] = s
    cfc = concept_family_consensus(pmids_by_family, required_families=2) if pmids_by_family else set()
    if cfc:
        write_list(os.path.join(args.outdir, 'concept_family_consensus.txt'), cfc)

    # 5) two-stage screen
    # treat union of first topk queries as stage-1
    stage1 = set().union(*[s for _, s in list(pmids_by_query.items())[:args.topk]])
    tss = two_stage_screen(stage1, args.prospero_gates)
    write_list(os.path.join(args.outdir, 'two_stage_screen.txt'), tss)

    # 6) time-stratified hybrid (approximate)
    tsh = time_stratified_hybrid(pmids_by_query)
    write_list(os.path.join(args.outdir, 'time_stratified_hybrid.txt'), tsh)

    print(f"Wrote aggregates in {args.outdir}")


if __name__ == '__main__':
    main()
