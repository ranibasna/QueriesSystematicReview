#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-assisted SR pipeline — single-file CLI

What this tool does:
- Select WITHOUT gold (sealed) using: concept coverage + screening burden + lint checks + MeSH sanity + simplicity.
- Finalize WITH gold: compute recall/TP/NNR and similarity metrics for a sealed selection.
- Direct scoring (benchmark): compute metrics for queries against a gold list.
- Utilities: fetch titles for PMIDs; (optional) extract gold list from a PDF references section.

Inputs can be provided via (priority order):
1) CLI options (e.g., --mindate, --maxdate, ...)
2) Environment variables (e.g., SELECT_MINDATE, NCBI_EMAIL)
3) Config file via --config (TOML or JSON)

Environment variables (common):
- NCBI_EMAIL, NCBI_API_KEY
- SELECT_MINDATE, SELECT_MAXDATE, SELECT_CONCEPT_TERMS, SELECT_QUERIES_TXT, SELECT_OUTDIR, SELECT_TARGET_RESULTS, SELECT_MIN_RESULTS
- FINALIZE_SEALED_GLOB, FINALIZE_GOLD_CSV
- SCORE_MINDATE, SCORE_MAXDATE, SCORE_QUERIES_TXT, SCORE_GOLD_CSV, SCORE_OUTDIR

Tip: place them in a .env file and this script will load them automatically (requires python-dotenv).

Requirements (conda env recommended):
- biopython, pandas, tenacity, python-dotenv  (optional: pdfminer.six if using PDF extraction)

NCBI settings (can be in environment or .env):
    export NCBI_EMAIL="you@example.com"
    export NCBI_API_KEY="..."   # optional
"""
import os, sys, csv, re, time, json, argparse, glob, hashlib
from datetime import datetime
from typing import List, Dict, Set, Tuple
from pathlib import Path

# Load .env if present (non-fatal if missing)
def _load_env_fallback(dotenv_path: str = '.env'):
    try:
        env_path = Path(dotenv_path)
        if not env_path.exists():
            return
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, val = line.split('=', 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and val and key not in os.environ:
                os.environ[key] = val
    except Exception:
        pass

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    _load_env_fallback()

# Optional: TOML support for --config
try:
    import tomllib  # Python 3.11+
except Exception:
    tomllib = None

def _ensure_imports():
    missing = []
    try:
        import pandas as pd
    except Exception:
        missing.append('pandas')
    try:
        from Bio import Entrez
    except Exception:
        missing.append('biopython')
    try:
        from tenacity import retry, wait_exponential, stop_after_attempt
    except Exception:
        missing.append('tenacity')
    # try:
    #     import pdfminer
    # except Exception:
    #     missing.append('pdfminer.six')
    if missing:
        print('NOTE: You may need to install:', ', '.join(missing), file=sys.stderr)

_ensure_imports()
import pandas as pd
from Bio import Entrez
from tenacity import retry, wait_exponential, stop_after_attempt
from search_providers import PROVIDER_REGISTRY
from collections import namedtuple

# W2.3: row-level gold article representation, one entry per CSV row.
# pmid and doi may both be present, one, or (rarely) neither.
# DOIs are expected to be pre-normalised to lowercase.
GoldArticle = namedtuple('GoldArticle', ['pmid', 'doi'])

def set_ncbi_identity(email: str = None, api_key: str = None):
    Entrez.email = email or os.getenv('NCBI_EMAIL', 'you@example.com')
    Entrez.api_key = api_key or os.getenv('NCBI_API_KEY', None)

RATE_LIMIT_SECONDS = 0.34

def lint_query(q: str) -> int:
    """Lightweight checks for common Boolean query issues.

    Examples: unbalanced parentheses/quotes; accidental duplicates; proximity operators (not in PubMed).
    Returns a small integer penalty count.
    """
    issues = 0
    if q.count('(') != q.count(')'): issues += 1
    if q.count('"') % 2 != 0: issues += 1
    if '()' in q: issues += 1
    if 'OR OR' in q or 'AND AND' in q: issues += 1
    if re.search(r'\b(NEAR|ADJ|adj|near)\b', q): issues += 1
    return issues

def load_concept_terms(path: str) -> Dict[str, List[re.Pattern]]:
    """Load a CSV of concept,term_regex → compile regex patterns per concept."""
    if not path or not os.path.exists(path):
        return {}
    df = pd.read_csv(path)
    out: Dict[str, List[re.Pattern]] = {}
    for _, r in df.iterrows():
        c = str(r['concept']).strip()
        rx = str(r['term_regex']).strip()
        if c and rx:
            try:
                out.setdefault(c, []).append(re.compile(rx, flags=re.IGNORECASE))
            except re.error as e:
                print(f"[WARN] Bad regex for concept {c}: {rx} ({e})", file=sys.stderr)
    return out

def concept_coverage(q: str, cdict: Dict[str, List[re.Pattern]]) -> float:
    """Fraction of concepts for which at least one pattern matches the query string."""
    if not cdict: return 0.0
    covered = 0
    for concept, pats in cdict.items():
        if any(p.search(q) for p in pats):
            covered += 1
    return covered / max(len(cdict), 1)

_MESH_PATTERNS = [r'"([^"]+)"\[(?:mh|MeSH Terms)(?::noexp)?\]', r'"([^"]+)"\[majr\]']

def extract_mesh_headings(query: str):
    """Extract MeSH headings from a Boolean query (mh/MeSH Terms/majr)."""
    heads = []
    for pat in _MESH_PATTERNS:
        for m in re.finditer(pat, query, flags=re.IGNORECASE):
            heads.append(m.group(1))
    return sorted(set(heads))

def _fetch_mesh_record(heading: str):
    """Fetch MeSH record metadata for a heading (used for intro-year sanity checks)."""
    srch = Entrez.esearch(db='mesh', term=f'"{heading}"[mh]')
    rid = Entrez.read(srch); srch.close()
    if int(rid.get('Count', 0)) == 0:
        return None, None
    uid = rid['IdList'][0]
    ef = Entrez.efetch(db='mesh', id=uid, rettype='full', retmode='xml')
    rec = Entrez.read(ef); ef.close()
    return uid, rec

def mesh_intro_year(rec_xml):
    try:
        dc = rec_xml[0]['DescriptorRecord']['DateCreated']
        return int(dc['Year'])
    except Exception:
        try:
            de = rec_xml[0]['DescriptorRecord']['DateEstablished']
            return int(de['Year'])
        except Exception:
            return 0

def mesh_sanity(query: str, max_year: int):
    """Validate MeSH usage: flag unknown headings and headings introduced after max_year."""
    heads = extract_mesh_headings(query)
    invalid = []; post_date = []; meta = {}
    for h in heads:
        try:
            uid, rec = _fetch_mesh_record(h)
            if rec is None:
                invalid.append(h); continue
            y = mesh_intro_year(rec); meta[h] = {'uid': uid, 'intro_year': y}
            if y and y > max_year:
                post_date.append((h, y))
        except Exception:
            invalid.append(h)
    return {'mesh_headings': heads, 'invalid': invalid, 'post_date': post_date, 'meta': meta}

def vocabulary_penalty(query: str, max_year: int):
    info = mesh_sanity(query, max_year)
    pen = 0.0; notes = []
    if info['invalid']:
        pen += 0.5 * len(info['invalid']); notes.append(f"Invalid MeSH: {info['invalid']}")
    if info['post_date']:
        pen += 0.25 * len(info['post_date']); notes.append(f"Post-date MeSH (after {max_year}): {info['post_date']}")
    return pen, '; '.join(notes), info

def query_stats(q: str):
    """Return lightweight size/complexity stats for a Boolean string."""
    chars = len(q); tokens = len(q.split()); depth = 0; max_depth = 0
    for ch in q:
        if ch == '(':
            depth += 1; max_depth = max(max_depth, depth)
        elif ch == ')':
            depth = max(0, depth-1)
    return {'chars': chars, 'tokens': tokens, 'max_depth': max_depth}

CHAR_T = 2000; TOK_T = 250; DEP_T = 6
def simplicity_penalty(q: str):
    s = query_stats(q); pen = 0.0
    if s['chars'] > CHAR_T: pen += (s['chars'] - CHAR_T) / CHAR_T
    if s['tokens'] > TOK_T: pen += 0.5 * (s['tokens'] - TOK_T) / TOK_T
    if s['max_depth'] > DEP_T: pen += 0.5 * (s['max_depth'] - DEP_T)
    return pen, s

def burden_score(results: int, min_results: int, target_results: int) -> float:
    if results < min_results: return -1.0
    b = 1.0 - abs(results - target_results) / max(target_results, 1)
    return max(-1.0, b)

def selector_features(query: str, results: int, coverage: float, lint_issues: int, max_year: int, min_results: int, target_results: int):
    b = burden_score(results, min_results, target_results)
    v_pen, v_notes, v_info = vocabulary_penalty(query, max_year)
    s_pen, s_stats = simplicity_penalty(query)
    score = 2.0*coverage + b - 0.5*lint_issues - v_pen - s_pen
    return {'score': score, 'burden': b, 'vocab_penalty': v_pen, 'simplicity_penalty': s_pen,
            'lint_issues': lint_issues, 'coverage': coverage, 'vocab_notes': v_notes,
            'simplicity_stats': s_stats, 'vocab_info': v_info}

def fetch_titles(pmids: List[str]):
    """Return a list of dicts with minimal metadata for each PMID (Title/Journal/Date)."""
    if not pmids: return []
    h = Entrez.efetch(db='pubmed', id=','.join(pmids), rettype='medline', retmode='text')
    txt = h.read(); h.close()
    titles = []; rec = {}
    for line in txt.splitlines():
        if line.startswith('PMID- '):
            if rec: titles.append(rec)
            rec = {'PMID': line.split('- ')[1].strip()}
        elif line.startswith('TI  - '):
            rec['Title'] = line.split('- ',1)[1].strip()
        elif line.startswith('JT  - '):
            rec['Journal'] = line.split('- ',1)[1].strip()
        elif line.startswith('DP  - '):
            rec['Date'] = line.split('- ',1)[1].strip()
    if rec: titles.append(rec)
    return titles

# def extract_gold_from_pdf(pdf_path: str, out_csv: str = None):
#     from pdfminer.high_level import extract_text
#     full_text = extract_text(pdf_path)
#     m = re.search(r'\bReferences\b', full_text, flags=re.IGNORECASE)
#     refs_text = full_text[m.start():] if m else full_text
#     cands = [l.strip() for l in re.split(r'\n+', refs_text) if l.strip()]
#     doi_rx = re.compile(r'(10\.\d{4,9}/\S+)', re.IGNORECASE)
#     year_rx = re.compile(r'\((20\d{2}|19\d{2})\)')
#     fa_rx = re.compile(r'^([A-Z][A-Za-z\-\s]+?),')
#     def try_pubmed_by_title(title: str):
#         q = f'"{title}"[Title]'
#         try:
#             srch = Entrez.esearch(db='pubmed', term=q, retmax=3)
#             rid = Entrez.read(srch); srch.close()
#             if int(rid.get('Count',0))>0: return rid['IdList'][0]
#         except Exception:
#             return None
#         return None
#     rows = []
#     for line in cands:
#         m_doi = doi_rx.search(line); doi = m_doi.group(1).rstrip('.;,') if m_doi else None
#         m_year = year_rx.search(line); year = int(m_year.group(1)) if m_year else None
#         title = None
#         if m_year:
#             after = line[m_year.end():]
#             after = re.sub(r'^[\).\s:;-]+','', after)
#             parts = re.split(r'\.\s', after, maxsplit=1)
#             if parts: title = parts[0].strip('“”" ')
#         if not title:
#             q = re.search(r'“([^”]+)”', line) or re.search(r'"([^"]+)"', line)
#             if q: title = q.group(1)
#         fa = None; m_fa = fa_rx.search(line)
#         if m_fa: fa = m_fa.group(1).strip()
#         pmid = None
#         if doi:
#             try:
#                 srch = Entrez.esearch(db='pubmed', term=f'{doi}[DOI]', retmax=1)
#                 rid = Entrez.read(srch); srch.close()
#                 if int(rid.get('Count',0))>0: pmid = rid['IdList'][0]
#             except Exception:
#                 pmid = None
#         if not pmid and title:
#             pmid = try_pubmed_by_title(title)
#         rows.append({'title': title, 'first_author': fa, 'year': year, 'doi': doi, 'pmid': pmid, 'raw': line[:300]})
#         time.sleep(RATE_LIMIT_SECONDS)
#     df = pd.DataFrame(rows)
#     df = df[(df['title'].notna()) | (df['doi'].notna())].reset_index(drop=True)
#     if out_csv: df.to_csv(out_csv, index=False)
#     return df

def set_metrics(retrieved: Set[str], gold: Set[str]):
    tp = len(retrieved & gold) # True Positives
    prec = tp / max(len(retrieved), 1) # Precision
    rec = tp / max(len(gold), 1) # Recall
    jacc = tp / max(len(retrieved | gold), 1) # Jaccard
    overlap = tp / max(min(len(retrieved), len(gold)), 1) # Overlap Coefficient
    f1 = 2*prec*rec / max(prec+rec, 1e-12) # F1 Score
    return {'TP': tp, 'Retrieved': len(retrieved), 'Gold': len(gold), 'Precision': prec, 'Recall': rec, 'F1': f1, 'Jaccard': jacc, 'OverlapCoeff': overlap}

def set_metrics_multi_key(
    retrieved_pmids: Set[str], 
    retrieved_dois: Set[str], 
    gold_pmids: Set[str], 
    gold_dois: Set[str]
):
    """
    Calculate metrics using DOI-primary matching with PMID fallback.
    
    Matching Strategy (DOI-primary):
    - DOI is the primary identifier (universal across databases)
    - PMID is used as fallback ONLY for gold articles without DOI
    - This reflects real-world scenarios where Scopus/WoS return DOIs without PMIDs
    
    Args:
        retrieved_pmids: Set of PMIDs from query results
        retrieved_dois: Set of DOIs from query results
        gold_pmids: Set of PMIDs from gold standard
        gold_dois: Set of DOIs from gold standard
    
    Returns:
        Dict with metrics and detailed breakdown
    
    Note:
        - DOIs are matched case-insensitively (normalized to lowercase)
        - Gold articles without DOI trigger a warning and use PMID fallback
        - Recall denominator = unique gold articles, not identifier count
    """
    # Normalize DOIs to lowercase for matching
    retrieved_dois_norm = {doi.lower() for doi in retrieved_dois if doi}
    gold_dois_norm = {doi.lower() for doi in gold_dois if doi}
    
    # Count unique gold articles:
    # - Primary: articles with DOI (count via DOI)
    # - Fallback: articles with PMID but no DOI (edge cases)
    gold_articles_with_doi = len(gold_dois_norm)
    
    # For PMID-only gold articles: we need to identify PMIDs that don't have corresponding DOI
    # Since we don't have explicit PMID<->DOI mapping in gold, assume each row is unique article
    # If gold has 12 PMIDs and 12 DOIs, these are likely the same 12 articles
    # If gold has 12 PMIDs and 10 DOIs, 2 articles have PMID-only
    gold_articles_pmid_only = max(0, len(gold_pmids) - len(gold_dois_norm))
    gold_unique_articles = max(len(gold_pmids), len(gold_dois_norm))
    
    # Flag warning if any gold articles lack DOI
    pmid_only_warning = gold_articles_pmid_only > 0
    
    # Match by DOI (primary) - this is the main matching mechanism
    matches_by_doi = retrieved_dois_norm & gold_dois_norm
    
    # Match by PMID (fallback) - only for gold articles WITHOUT DOI
    # If gold has PMID but no DOI for an article, match by PMID
    # Assumption: if gold_pmids > gold_dois, the extra PMIDs are PMID-only articles
    if gold_articles_pmid_only > 0:
        # There are some gold articles with PMID but no DOI
        # We can't identify which specific PMIDs lack DOI without row-level data
        # Conservative approach: count PMID matches not already matched by DOI
        matches_by_pmid = retrieved_pmids & gold_pmids
        # Subtract matches that were already counted via DOI
        # This is an approximation since we don't have explicit mapping
        matches_by_pmid_fallback = matches_by_pmid - matches_by_doi
    else:
        # All gold articles have DOI, so no PMID fallback needed
        matches_by_pmid_fallback = set()
    
    # Total true positives (unique articles matched)
    tp = len(matches_by_doi) + len(matches_by_pmid_fallback)
    
    # Count unique retrieved articles
    # Use max of PMID or DOI counts as approximation of unique articles
    retrieved_unique_articles = max(len(retrieved_pmids), len(retrieved_dois_norm))
    
    # Calculate metrics
    prec = tp / max(retrieved_unique_articles, 1)
    rec = tp / max(gold_unique_articles, 1)
    f1 = 2 * prec * rec / max(prec + rec, 1e-12)
    
    # Jaccard: intersection over union
    union_size = retrieved_unique_articles + gold_unique_articles - tp
    jacc = tp / max(union_size, 1)
    
    # Overlap coefficient: intersection over minimum
    overlap = tp / max(min(retrieved_unique_articles, gold_unique_articles), 1)
    
    return {
        'TP': tp,
        'Retrieved': retrieved_unique_articles,
        'Gold': gold_unique_articles,
        'Precision': prec,
        'Recall': rec,
        'F1': f1,
        'Jaccard': jacc,
        'OverlapCoeff': overlap,
        # Detailed breakdown for analysis
        'matches_by_doi': len(matches_by_doi),
        'matches_by_pmid_fallback': len(matches_by_pmid_fallback),
        'matched_dois': matches_by_doi,  # Actual DOIs matched (for details)
        'matched_pmids_fallback': matches_by_pmid_fallback,  # Actual PMIDs matched via fallback
        'gold_articles_with_doi': gold_articles_with_doi,
        'gold_articles_pmid_only': gold_articles_pmid_only,
        'pmid_only_warning': pmid_only_warning,
        'retrieved_pmids_count': len(retrieved_pmids),
        'retrieved_dois_count': len(retrieved_dois_norm),
    }

def set_metrics_row_level(
    retrieved_pmids: Set[str],
    retrieved_dois: Set[str],
    gold_rows: List[GoldArticle],
) -> dict:
    """
    Row-level (per-article) metrics: each gold article is a TP if DOI OR PMID was retrieved.

    Fixes Issue 1: the flat-set approach in set_metrics_multi_key() disables the PMID
    fallback whenever all gold articles have DOIs (because it gates the fallback on
    `gold_articles_pmid_only > 0`).  Here each gold article is tested independently:

      1. DOI match  : gold.doi != None  and  gold.doi in retrieved_dois → TP
      2. PMID fallback: gold.pmid != None and gold.pmid in retrieved_pmids
                        (only fires when DOI did NOT match)  → TP
      3. Miss otherwise.

    This correctly handles the scenario where PubMed retrieved an article's PMID but
    the DOI was absent from the PubMed XML, and no other database retrieved the DOI.
    Old code: miss (fallback disabled).  This function: TP via PMID.

    Returns the same keys as set_metrics_multi_key() for drop-in compatibility.
    """
    retrieved_dois_norm = {d.lower() for d in retrieved_dois if d}

    matches_by_doi_count = 0
    matches_by_pmid_only_count = 0  # matched by PMID; DOI was NOT in retrieved set
    matched_dois_set: Set[str] = set()
    matched_pmids_fallback_set: Set[str] = set()

    for g in gold_rows:
        doi_matched = bool(g.doi) and g.doi.lower() in retrieved_dois_norm
        pmid_matched = bool(g.pmid) and g.pmid in retrieved_pmids

        if doi_matched:
            matches_by_doi_count += 1
            matched_dois_set.add(g.doi.lower())  # g.doi is non-None here
        elif pmid_matched:
            # PMID fallback: article was not matched by DOI, but PMID was retrieved
            matches_by_pmid_only_count += 1
            matched_pmids_fallback_set.add(g.pmid)  # g.pmid is non-None here

    tp = matches_by_doi_count + matches_by_pmid_only_count
    gold = len(gold_rows)
    retrieved_unique = max(len(retrieved_pmids), len(retrieved_dois_norm))

    prec = tp / max(retrieved_unique, 1)
    rec = tp / max(gold, 1)
    f1 = 2 * prec * rec / max(prec + rec, 1e-12)
    union_size = retrieved_unique + gold - tp
    jacc = tp / max(union_size, 1)
    overlap = tp / max(min(retrieved_unique, gold), 1)

    return {
        'TP': tp,
        'Retrieved': retrieved_unique,
        'Gold': gold,
        'Precision': prec,
        'Recall': rec,
        'F1': f1,
        'Jaccard': jacc,
        'OverlapCoeff': overlap,
        # Detailed breakdown (same key names as set_metrics_multi_key for compat)
        'matches_by_doi': matches_by_doi_count,
        'matches_by_pmid_fallback': matches_by_pmid_only_count,
        'matched_dois': matched_dois_set,
        'matched_pmids_fallback': matched_pmids_fallback_set,
        'gold_articles_with_doi': sum(1 for g in gold_rows if g.doi),
        'gold_articles_pmid_only': sum(1 for g in gold_rows if not g.doi),
        'pmid_only_warning': any(not g.doi for g in gold_rows),
        'retrieved_pmids_count': len(retrieved_pmids),
        'retrieved_dois_count': len(retrieved_dois_norm),
    }

def read_queries_from_txt(path: str) -> List[str]:
    """Read one or more Boolean queries from a .txt file.

    - Blank lines separate queries; lines starting with # are ignored.
    - Returns a list of non-empty query strings.
    """
    with open(path, 'r', encoding='utf-8') as f:
        lines = [ln.strip() for ln in f.readlines()]
    buf = []; queries = []
    for ln in lines:
        if not ln:
            if buf:
                queries.append(' '.join(buf).strip()); buf = []
        else:
            if ln.startswith('#'): continue
            buf.append(ln)
    if buf: queries.append(' '.join(buf).strip())
    return [q for q in queries if q]

def read_pmids_from_txt(path: str) -> Set[str]:
    """Read newline-separated PMIDs from a text file into a set of strings.

    Empty lines and comments starting with # are ignored. Whitespace is stripped.
    """
    pmids: Set[str] = set()
    with open(path, 'r', encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            pmids.add(ln)
    return pmids


def read_articles_from_csv(path: str) -> dict:
    """
    Read aggregated results from CSV file with pmid,doi columns.
    
    This function reads the multi-key output format from aggregate_queries.py --multi-key.
    
    Args:
        path: Path to CSV file with pmid,doi columns
    
    Returns:
        Dict with:
        - 'pmids': Set of PMID strings (empty strings filtered out)
        - 'dois': Set of DOI strings (normalized to lowercase, empty filtered)
        - 'count': Total number of articles
    
    Note:
        DOIs are normalized to lowercase for case-insensitive matching.
    """
    pmids: Set[str] = set()
    dois: Set[str] = set()
    
    with open(path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pmid = row.get('pmid', '').strip()
            doi = row.get('doi', '').strip()
            
            if pmid and pmid.lower() not in ('', 'nan', 'none'):
                pmids.add(pmid)
            if doi and doi.lower() not in ('', 'nan', 'none'):
                dois.add(doi.lower())
    
    return {
        'pmids': pmids,
        'dois': dois,
        'count': max(len(pmids), len(dois)),  # Unique articles approximation
    }


def _provider_name(provider) -> str:
    return getattr(provider, 'name', provider.__class__.__name__.lower())


def _provider_query_path(base_path: Path, provider_name: str) -> Path | None:
    if provider_name == 'pubmed':
        return base_path
    
    # Map provider names to aliases for file naming
    # web_of_science can be abbreviated as 'wos'
    provider_aliases = {
        'web_of_science': ['web_of_science', 'wos'],
        'scopus': ['scopus'],
        'pubmed': ['pubmed'],
    }
    
    # Get all possible names for this provider (including aliases)
    possible_names = provider_aliases.get(provider_name, [provider_name])
    
    stem = base_path.stem
    suffix = base_path.suffix or '.txt'
    
    # Try all combinations of aliases and patterns
    for name in possible_names:
        candidates = [
            base_path.with_name(f"{stem}_{name}{suffix}"),
            base_path.with_name(f"{stem}.{name}{suffix}"),
            base_path.with_name(f"{stem}-{name}{suffix}"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
    
    return None


def _load_queries_for_providers(providers, base_path: Path) -> Dict[str, List[str]]:
    if not base_path.exists():
        raise SystemExit(f"Queries file not found: {base_path}")
    base_queries = read_queries_from_txt(str(base_path))
    provider_queries: Dict[str, List[str]] = {}
    for provider in providers:
        pname = _provider_name(provider)
        specific_path = _provider_query_path(base_path, pname)
        if specific_path and specific_path != base_path:
            queries = read_queries_from_txt(str(specific_path))
            print(f"[INFO] Using queries from {specific_path} for provider '{pname}'.")
        else:
            queries = base_queries
            if pname != 'pubmed':
                print(f"[WARN] No provider-specific queries found for '{pname}'. Using {base_path}.", file=sys.stderr)
        provider_queries[pname] = queries
    lengths = {name: len(qs) for name, qs in provider_queries.items()}
    if len(set(lengths.values())) > 1:
        raise SystemExit(f"Provider query counts differ: {lengths}. Ensure each provider file lists the same number of queries (aligned by order).")
    return provider_queries


def _build_query_bundles(provider_queries: Dict[str, List[str]]) -> List[Dict]:
    if not provider_queries:
        return []
    provider_names = list(provider_queries.keys())
    bundle_count = len(provider_queries[provider_names[0]])
    bundles: List[Dict] = []
    for idx in range(bundle_count):
        qmap = {name: provider_queries[name][idx] for name in provider_names}
        canonical = qmap.get('pubmed') or next(iter(qmap.values()))
        bundles.append({'index': idx, 'canonical': canonical, 'per_provider': qmap})
    return bundles


def _execute_query_bundle(providers, qmap: Dict[str, str], mindate: str, maxdate: str):
    combined_pmids: Set[str] = set()
    combined_dois: Set[str] = set()
    # W2.1: accumulate PMID↔DOI pairs from PubMed so downstream code (W2.2
    # linked_records serialisation, W2.3 row-level gold matching, W2.4
    # total_results dedup fix) can use the authoritative pairing without
    # changing any function return signatures.
    combined_pmid_to_doi: Dict[str, str] = {}
    provider_details: Dict[str, Dict] = {}
    total_results = 0
    total_raw_results = 0
    
    for provider in providers:
        pname = _provider_name(provider)
        query = qmap.get(pname)
        if not query:
            continue
        if pname == 'scopus' and getattr(provider, 'apply_year_filter', True) is False:
            print("[INFO] Scopus date filter disabled (SCOPUS_SKIP_DATE_FILTER=true or flag). Running query without PUBYEAR bounds.")
        try:
            dois, ids, total = provider.search(query, mindate, maxdate)
        except Exception as exc:
            print(f"[WARN] Provider '{pname}' failed: {exc}. Skipping its contribution for this query.", file=sys.stderr)
            provider_details[pname] = {
                'query': query,
                'results_count': 0,
                'retrieved_ids': [],
                'retrieved_dois': [],
                'error': str(exc),
            }
            continue
        
        # W2.1: read the PMID↔DOI cache set by PubMedProvider.search() on this
        # provider instance immediately after the call (before the next iteration
        # overwrites it on a different provider).  Non-PubMed providers do not set
        # this attribute, so getattr returns {} safely.
        pmid_to_doi = getattr(provider, '_pmid_to_doi_cache', {})
        combined_pmid_to_doi.update(pmid_to_doi)

        # Track raw results before deduplication
        total_raw_results += total
        
        # Deduplicate by DOI (Option A: Simple DOI-based deduplication)
        # Articles with DOIs are deduplicated automatically by using a set
        # Articles without DOIs may appear as duplicates (acceptable ~0.5% edge case)
        # See multi_database_edge_cases_analysis.md for rationale and Option B (future)
        combined_dois.update(dois)
        
        id_type = getattr(provider, 'id_type', 'id')
        if id_type == 'pmid':
            combined_pmids.update(ids)

        # W2.2: build linked_records that preserve the authoritative PMID↔DOI
        # pairing so downstream code (W2.5 ArticleRegistry, W2.3 row-level gold
        # matching) can construct correctly-linked Article objects rather than
        # relying on the broken index-based pairing in _merge_pmids_dois.
        #
        # PubMed  (id_type='pmid'):  paired records from _pmid_to_doi_cache, then
        #   PMID-only records for PMIDs whose DOI was absent from the PubMed XML.
        # Scopus/WOS               :  DOI-only records (native IDs are not PMIDs).
        if id_type == 'pmid':
            _linked: list = [{'pmid': p, 'doi': d} for p, d in pmid_to_doi.items()]
            _pmids_no_doi = sorted(set(ids) - set(pmid_to_doi.keys()))
            _linked += [{'pmid': p, 'doi': None} for p in _pmids_no_doi]
        else:
            _linked = [{'pmid': None, 'doi': d} for d in sorted(dois)]

        provider_details[pname] = {
            'query': query,
            'results_count': total,
            'retrieved_ids': sorted(ids),
            'retrieved_dois': sorted(dois),
            'id_type': id_type,
            'linked_records': _linked,  # W2.2: authoritative PMID↔DOI pairs
        }
        # W2.4: per-DB counts are stored in provider_details[*]['results_count'].
        # total_results is NOT accumulated here; it is set to the deduplicated
        # unique-article count after the provider loop ends (see below).
    
    # Calculate deduplication statistics
    # Count PubMed PMIDs that have no corresponding DOI (truly PMID-only articles).
    # W2.1: use the exact pairing from combined_pmid_to_doi when available, so
    # the count is derived from the authoritative PMID↔DOI map rather than an
    # index-length approximation.
    if combined_pmid_to_doi:
        # Exact: PMIDs not present as keys in the PMID→DOI map have no DOI.
        _pmid_only_count = len(combined_pmids - set(combined_pmid_to_doi.keys()))
    else:
        # Fallback for when PubMed was not queried or cache is unavailable.
        _pm_detail = provider_details.get('pubmed', {})
        _pmid_only_count = max(
            0,
            len(_pm_detail.get('retrieved_ids', [])) - len(_pm_detail.get('retrieved_dois', [])),
        )
    unique_articles = len(combined_dois) + _pmid_only_count
    # W2.4: total_results is now the deduplicated unique-article count, NOT the
    # raw sum of per-database API-reported counts. The raw sum is preserved in
    # total_raw_results (used for the log below) and is recoverable by callers
    # as sum(provider_details[*]['results_count']).
    total_results = unique_articles
    duplicates_removed = total_raw_results - total_results

    if duplicates_removed > 0:
        dedup_rate = (duplicates_removed / total_raw_results * 100) if total_raw_results > 0 else 0
        pmid_only_note = f", {_pmid_only_count} PubMed PMID-only" if _pmid_only_count else ""
        print(f"[INFO] Deduplication (DOI-based): {total_raw_results} raw results → {total_results} unique articles ({len(combined_dois)} with DOI{pmid_only_note}, {duplicates_removed} duplicates removed, {dedup_rate:.1f}%)")
    
    return combined_pmids, combined_dois, total_results, provider_details

def select_without_gold(providers, query_bundles: List[Dict], mindate: str, maxdate: str, concept_terms_path: str, outdir: str, target_results: int = 5000, min_results: int = 50):
    """Run selection pipeline without gold and write a sealed JSON plus CSV summary."""
    os.makedirs(outdir, exist_ok=True)
    cdict = load_concept_terms(concept_terms_path)
    max_year = int(maxdate.split('/')[0]) if '/' in maxdate else int(maxdate[:4])
    records = []
    for bundle in query_bundles:
        canonical_query = bundle['canonical']
        pmids, dois, total, provider_details = _execute_query_bundle(providers, bundle['per_provider'], mindate, maxdate)
        # W2.4: total is now the deduplicated unique count; compute raw sum for reference.
        total_raw = sum(
            v.get('results_count', 0)
            for v in provider_details.values()
            if 'error' not in v
        )
        cov = concept_coverage(canonical_query, cdict)
        lint = lint_query(canonical_query)
        feats = selector_features(canonical_query, total, cov, lint, max_year, min_results, target_results)
        rec = {'query': canonical_query, 'query_sha256': hashlib.sha256(canonical_query.encode()).hexdigest(),
               'results_count': total,          # W2.4: deduplicated unique article count
               'results_count_raw': total_raw,  # W2.4: raw sum of per-DB API counts
               **{k:v for k,v in feats.items() if k != 'vocab_info'}, 'retrieved_pmids': sorted(pmids), 'retrieved_dois': sorted(dois),
               'vocab_info': feats['vocab_info'], 'provider_details': provider_details}
        records.append(rec)
        _raw_note = f" (raw={total_raw})" if total_raw != total else ""
        print(f"Candidate: {rec['query_sha256'][:8]}  Results={total}{_raw_note}  Coverage={cov:.2f}  Score={rec['score']:.3f}")
    df = pd.DataFrame([{k:(v if k not in ('simplicity_stats','vocab_info') else str(v)) for k,v in r.items() if k not in ('retrieved_pmids', 'retrieved_dois', 'provider_details')} for r in records]).sort_values(['score','coverage','results_count'], ascending=[False,False,True])
    run_id = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    df_path = os.path.join(outdir, f'selection_summary_{run_id}.csv'); df.to_csv(df_path, index=False)
    best = df.iloc[0].to_dict()
    pick = next(r for r in records if r['query_sha256'] == best['query_sha256'])
    sealed = {**pick, 'mindate': mindate, 'maxdate': maxdate, 'created_utc': datetime.utcnow().isoformat()}
    sealed_path = os.path.join(outdir, f'sealed_{run_id}.json')
    with open(sealed_path, 'w', encoding='utf-8') as f: json.dump(sealed, f, ensure_ascii=False, indent=2)
    print(f"\nBest query: {best['query_sha256'][:8]}  Score={best['score']:.3f}  Results={best['results_count']}  Coverage={best['coverage']}")
    print('Wrote:', sealed_path); print('Summary:', df_path)
    return sealed_path, df_path

def load_gold_pmids(path: str) -> Set[str]:
    """
    Load gold standard PMIDs from a CSV file.
    
    Supports two formats:
    1. Simple format: Single column with PMIDs (no header or 'pmid' header)
    2. Enhanced format: Multiple columns including 'pmid' and optionally 'doi'
       (created by scripts/enhance_gold_standard.py or scripts/generate_gold_standard.py)
    
    Note: DOI column is currently informational for this function. 
    Use load_gold_multi_key() to get both PMIDs and DOIs for multi-key matching.
    
    The enhanced format can be generated once during study setup:
        python scripts/generate_gold_standard.py <study_name>
        # Creates both gold_pmids_<study>.csv and gold_pmids_<study>_detailed.csv
    """
    pmids = set()
    with open(path, newline='', encoding='utf-8') as f:
        rows = list(csv.reader(f))
    if not rows: return pmids
    header = [h.strip().lower() for h in rows[0]]
    if 'pmid' in header:
        df = pd.read_csv(path, dtype=str)
        pmids = set(df['pmid'].dropna().astype(str).str.strip())
    else:
        for r in rows:
            if r: pmids.add(str(r[0]).strip())
    return pmids

def load_gold_multi_key(path: str) -> tuple:
    """
    Load gold standard with both PMIDs and DOIs for multi-key matching.
    
    Supports same formats as load_gold_pmids():
    1. Simple format: Returns (pmids, empty set) - backward compatible
    2. Enhanced format with DOI column: Returns (pmids, dois)
    
    Args:
        path: Path to gold standard CSV file
    
    Returns:
        Tuple of (pmid_set, doi_set)
        - pmid_set: Set of PMID strings
        - doi_set: Set of DOI strings (normalized to lowercase)
    
    Usage:
        gold_pmids, gold_dois = load_gold_multi_key('studies/ai_2022/gold_pmids_ai_2022_detailed.csv')
        metrics = set_metrics_multi_key(retrieved_pmids, retrieved_dois, gold_pmids, gold_dois)
    
    Note:
        - DOIs are normalized to lowercase for case-insensitive matching
        - Empty/missing DOIs are filtered out
        - Maintains backward compatibility with simple PMID-only format
    """
    pmids = set()
    dois = set()
    
    with open(path, newline='', encoding='utf-8') as f:
        rows = list(csv.reader(f))
    
    if not rows:
        return pmids, dois
    
    header = [h.strip().lower() for h in rows[0]]
    
    if 'pmid' in header:
        # Enhanced format with column headers
        df = pd.read_csv(path, dtype=str)
        pmids = set(df['pmid'].dropna().astype(str).str.strip())
        
        # Extract DOIs if column exists
        if 'doi' in df.columns:
            # Normalize DOIs to lowercase and filter out empty values
            dois = {doi.lower().strip() for doi in df['doi'].dropna().astype(str) 
                    if doi and doi.lower() not in ('', 'nan', 'none')}
    else:
        # Simple format (PMID only, no header)
        for r in rows:
            if r: 
                pmids.add(str(r[0]).strip())
        # dois remains empty set
    
    return pmids, dois

def load_gold_rows(path: str) -> List[GoldArticle]:
    """
    Load gold standard as an ordered list of GoldArticle(pmid, doi) rows.

    Each row represents one article from the gold standard CSV.  Both identifiers
    may be present, one, or neither (though the latter is unusual).
    DOIs are normalised to lowercase.

    Supports the same CSV formats as load_gold_multi_key():
      - Enhanced format: column headers 'pmid' (required) and 'doi' (optional)
      - Simple format  : no header row; first column treated as PMID, doi=None

    Used by W2.3 set_metrics_row_level() for per-article matching.
    """
    rows: List[GoldArticle] = []

    with open(path, newline='', encoding='utf-8') as f:
        csv_rows = list(csv.reader(f))

    if not csv_rows:
        return rows

    header = [h.strip().lower() for h in csv_rows[0]]

    if 'pmid' in header:
        df = pd.read_csv(path, dtype=str)
        doi_col = df['doi'] if 'doi' in df.columns else pd.Series([None] * len(df))
        for pmid_val, doi_val in zip(df['pmid'], doi_col):
            pmid_str = str(pmid_val).strip() if pmid_val is not None else ''
            pmid = pmid_str if pmid_str and pmid_str.lower() not in ('nan', 'none', '') else None
            doi_raw = str(doi_val).strip().lower() if doi_val is not None else ''
            doi = doi_raw if doi_raw and doi_raw not in ('nan', 'none', '') else None
            rows.append(GoldArticle(pmid=pmid, doi=doi))
    else:
        # Simple format: each row is just a PMID, no DOI available
        for r in csv_rows:
            if r:
                pmid = str(r[0]).strip()
                if pmid:
                    rows.append(GoldArticle(pmid=pmid, doi=None))

    return rows

def finalize_with_gold(sealed_glob: str, gold_csv: str, outdir: str = None, use_multi_key: bool = False):
    """
    Finalize sealed query results with gold standard evaluation.
    
    Args:
        sealed_glob: Glob pattern for sealed JSON files
        gold_csv: Path to gold standard CSV file
        outdir: Output directory (optional)
        use_multi_key: If True, use multi-key matching (PMID OR DOI)
                      Requires gold_csv to have DOI column (e.g., *_detailed.csv)
    
    Returns:
        Path to finalized output file
    """
    sealed_files = sorted(glob.glob(sealed_glob))
    if not sealed_files:
        raise SystemError(f'No sealed files found for {sealed_glob}')
    sealed_file = sealed_files[-1]
    with open(sealed_file, 'r', encoding='utf-8') as f:
        sealed = json.load(f)
    
    if use_multi_key:
        # W2.3: row-level matching (PMID OR DOI per article)
        gold_rows = load_gold_rows(gold_csv)
        retrieved_pmids = set(sealed.get('retrieved_pmids', []))
        retrieved_dois = set(sealed.get('retrieved_dois', []))

        metrics = set_metrics_row_level(retrieved_pmids, retrieved_dois, gold_rows)

        sealed.update({
            'finalized_utc': datetime.utcnow().isoformat(),
            'gold_pmids_count': sum(1 for g in gold_rows if g.pmid),
            'gold_dois_count': sum(1 for g in gold_rows if g.doi),
            'matching_mode': 'row_level',
            **metrics
        })

        print(f'Row-level matching (per-article DOI-then-PMID):')
        print(f'  Matches by DOI: {metrics["matches_by_doi"]}')
        print(f'  Matches by PMID fallback (no DOI match): {metrics["matches_by_pmid_fallback"]}')
        print(f'  Total TP: {metrics["TP"]}')
    else:
        # Legacy PMID-only matching
        gold = load_gold_pmids(gold_csv)
        retrieved = set(sealed['retrieved_pmids'])
        metrics = set_metrics(retrieved, gold)
        
        sealed.update({
            'finalized_utc': datetime.utcnow().isoformat(), 
            'gold_size': len(gold),
            'matching_mode': 'pmid_only',
            **metrics
        })
    
    out = sealed_file.replace('sealed_', 'final_').replace('sealed_outputs', 'final_outputs')
    os.makedirs(Path(out).parent, exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(sealed, f, ensure_ascii=False, indent=2)
    print('Final metrics:', json.dumps({k: v for k, v in metrics.items() 
                                        if k in ['TP', 'Precision', 'Recall', 'F1']}, indent=2))
    print('Wrote:', out)
    return out

def score_queries(providers, query_bundles: List[Dict], mindate: str, maxdate: str, gold_csv: str, outdir: str, use_multi_key: bool = False, query_num_offset: int = 0):
    """
    Run scoring pipeline and write a summary CSV, per-database summary CSV, and details JSON.
    
    Args:
        providers: List of search provider instances
        query_bundles: List of query bundle dictionaries
        mindate: Start date for queries
        maxdate: End date for queries
        gold_csv: Path to gold standard CSV
        outdir: Output directory
        use_multi_key: If True, use multi-key matching (PMID OR DOI)
    
    Output Files:
        summary_{timestamp}.csv: Combined query performance (one row per query)
        summary_per_database_{timestamp}.csv: Per-database query performance (one row per query per database)
        details_{timestamp}.json: Full details including retrieved IDs
    """
    os.makedirs(outdir, exist_ok=True)
    
    if use_multi_key:
        gold_pmids, gold_dois = load_gold_multi_key(gold_csv)
        gold_rows = load_gold_rows(gold_csv)  # W2.3: row-level matching
    else:
        gold = load_gold_pmids(gold_csv)
        gold_pmids = gold
        gold_dois = set()

    rows = []
    details = []
    per_db_rows = []  # New: per-database metrics

    for bundle_idx, bundle in enumerate(query_bundles):
        canonical_query = bundle['canonical']
        pmids, dois, total, provider_details = _execute_query_bundle(providers, bundle['per_provider'], mindate, maxdate)
        # W2.4: total is now the deduplicated unique count. Compute raw sum for
        # reference (= what the old code returned; now stored as results_count_raw).
        total_raw = sum(
            v.get('results_count', 0)
            for v in provider_details.values()
            if 'error' not in v
        )

        if use_multi_key:
            # W2.3: row-level matching (per-article DOI-then-PMID)
            metrics = set_metrics_row_level(pmids, dois, gold_rows)
            tp = metrics['TP']
            recall = metrics['Recall']
            gold_size = metrics['Gold']
        else:
            # Legacy PMID-only matching
            tp = len(pmids & gold)
            recall = tp / max(len(gold), 1)
            gold_size = len(gold)
        
        nnr_proxy = total / max(tp, 1)
        rec = {
            'query': canonical_query,
            'results_count': total,          # W2.4: deduplicated unique article count
            'results_count_raw': total_raw,  # W2.4: raw sum of per-DB API counts
            'TP': tp,
            'gold_size': gold_size,
            'recall': recall,
            'NNR_proxy': nnr_proxy
        }
        
        if use_multi_key:
            rec.update({
                'matches_by_pmid': metrics['matches_by_doi'] + metrics['matches_by_pmid_fallback'],
                'matches_by_doi_only': metrics['matches_by_doi'],
            })
        
        rows.append(rec)
        # Store TP PMIDs for details - use appropriate gold standard
        tp_pmids_for_details = (pmids & gold_pmids) if use_multi_key else (pmids & gold)
        details.append({**rec, 'retrieved_pmids': sorted(pmids), 'retrieved_dois': sorted(dois), 'tp_pmids': sorted(tp_pmids_for_details), 'provider_details': provider_details})
        _raw_note = f" (raw={total_raw})" if total_raw != total else ""
        print(f"Query[{hashlib.sha256(canonical_query.encode()).hexdigest()[:8]}]: results={total}{_raw_note}  TP={tp}  recall={recall:.3f}  NNR_proxy={nnr_proxy:.2f}")
        
        # Generate per-database metrics
        for db_name, db_details in provider_details.items():
            if 'error' in db_details:
                # Skip databases that failed
                continue
            
            db_id_type = db_details.get('id_type', 'id')
            db_ids = set(db_details.get('retrieved_ids', []))
            db_dois = set(db_details.get('retrieved_dois', []))
            db_results = db_details.get('results_count', 0)
            db_query = db_details.get('query', '')
            
            # Only PubMed returns real PMIDs; Scopus/WOS native IDs are internal
            # identifiers that will never match gold PMIDs — pass empty set instead.
            db_pmids_for_matching = db_ids if db_id_type == 'pmid' else set()

            if use_multi_key:
                # W2.3: row-level matching for this database
                db_metrics = set_metrics_row_level(db_pmids_for_matching, db_dois, gold_rows)
                db_tp = db_metrics['TP']
                db_recall = db_metrics['Recall']
            else:
                # Legacy PMID-only matching
                db_tp = len(db_pmids_for_matching & gold)
                db_recall = db_tp / max(len(gold), 1)
            
            db_nnr_proxy = db_results / max(db_tp, 1)
            
            db_rec = {
                'query_num': bundle_idx + 1 + query_num_offset,
                'database': db_name,
                'query': db_query[:200] + '...' if len(db_query) > 200 else db_query,  # Truncate long queries
                'results_count': db_results,
                'TP': db_tp,
                'gold_size': gold_size,
                'recall': db_recall,
                'NNR_proxy': db_nnr_proxy
            }
            
            if use_multi_key:
                db_rec.update({
                    'matches_by_pmid': db_metrics.get('matches_by_doi', 0) + db_metrics.get('matches_by_pmid_fallback', 0),
                    'matches_by_doi_only': db_metrics.get('matches_by_doi', 0),
                })
            
            per_db_rows.append(db_rec)
        
        # Also add combined row to per-database CSV for reference
        combined_rec = {
            'query_num': bundle_idx + 1 + query_num_offset,
            'database': 'COMBINED',
            'query': canonical_query[:200] + '...' if len(canonical_query) > 200 else canonical_query,
            'results_count': total,          # W2.4: deduplicated unique article count
            'results_count_raw': total_raw,  # W2.4: raw sum of per-DB API counts
            'TP': tp,
            'gold_size': gold_size,
            'recall': recall,
            'NNR_proxy': nnr_proxy
        }
        if use_multi_key:
            combined_rec.update({
                'matches_by_pmid': metrics['matches_by_doi'] + metrics['matches_by_pmid_fallback'],
                'matches_by_doi_only': metrics['matches_by_doi'],
            })
        per_db_rows.append(combined_rec)
    
    df = pd.DataFrame(rows)
    df_per_db = pd.DataFrame(per_db_rows)
    
    run_id = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    summary = os.path.join(outdir, f'summary_{run_id}.csv')
    summary_per_db = os.path.join(outdir, f'summary_per_database_{run_id}.csv')
    details_path = os.path.join(outdir, f'details_{run_id}.json')
    
    df.to_csv(summary, index=False)
    df_per_db.to_csv(summary_per_db, index=False)
    with open(details_path, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    
    print('Saved:', summary)
    print('Saved:', summary_per_db)
    print('Saved:', details_path)
    
    # Print per-database summary
    if len(per_db_rows) > 0:
        print('\n📊 Per-Database Query Performance:')
        print('─' * 70)
        # Group by database for summary
        db_summary = {}
        for row in per_db_rows:
            db = row['database']
            if db == 'COMBINED':
                continue
            if db not in db_summary:
                db_summary[db] = {'total_results': 0, 'best_recall': 0, 'queries': 0}
            db_summary[db]['total_results'] += row['results_count']
            db_summary[db]['best_recall'] = max(db_summary[db]['best_recall'], row['recall'])
            db_summary[db]['queries'] += 1
        
        for db, stats in sorted(db_summary.items()):
            print(f"  {db:12s}: {stats['queries']} queries, {stats['total_results']:,} results, best recall={stats['best_recall']:.3f}")
        print('─' * 70)
    
    return summary, details_path

def _load_config(config_path: str | None) -> dict:
    """Load a config file (TOML or JSON). Returns {} if missing or on parse error."""
    if not config_path:
        return {}
    p = Path(config_path)
    if not p.exists():
        return {}
    try:
        if p.suffix.lower() == '.json':
            return json.loads(p.read_text(encoding='utf-8'))
        if p.suffix.lower() == '.toml' and tomllib is not None:
            return tomllib.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return {}
    return {}

def _resolve(val, env_key: str | None, cfg: dict, cfg_keys: list[str], cast=lambda x: x):
    """Resolve a value from CLI (val), ENV (env_key), or CONFIG (first found in cfg_keys)."""
    if val is not None:
        return cast(val)
    if env_key:
        ev = os.getenv(env_key)
        if ev is not None:
            return cast(ev)
    for k in cfg_keys:
        if k in cfg and cfg[k] is not None:
            return cast(cfg[k])
    return None

def _parse_bool(val):
    if isinstance(val, bool):
        return val
    if val is None:
        return False
    s = str(val).strip().lower()
    return s in ('1','true','yes','on')

DATABASE_ENV_KEY = 'SR_DATABASES'
DEFAULT_DATABASES = ['pubmed']
_PROVIDER_ALIASES = {
    'ncbi': 'pubmed',
    'pubmed': 'pubmed',
    'scopus': 'scopus',
    'wos': 'web_of_science',
    'web_of_science': 'web_of_science',
    'webofscience': 'web_of_science',
}


def _dedupe_preserve(seq: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _parse_database_list(val) -> List[str]:
    if val is None:
        return []
    items: List[str] = []
    if isinstance(val, str):
        raw = val.replace(';', ',')
        for piece in raw.split(','):
            piece = piece.strip()
            if not piece:
                continue
            norm = _PROVIDER_ALIASES.get(piece.lower().replace('-', '_').strip(), piece.lower().strip())
            if norm:
                items.append(norm)
        return items
    if isinstance(val, (list, tuple, set)):
        for entry in val:
            items.extend(_parse_database_list(entry))
    return items


def _resolve_database_selection(cli_value, cfg: dict) -> List[str]:
    cli = _dedupe_preserve(_parse_database_list(cli_value))
    if cli:
        return cli
    env = _dedupe_preserve(_parse_database_list(os.getenv(DATABASE_ENV_KEY)))
    if env:
        return env
    cfg_databases = cfg.get('databases')
    defaults: List[str] = []
    if isinstance(cfg_databases, dict):
        defaults = _dedupe_preserve(_parse_database_list(cfg_databases.get('default')))
    elif cfg_databases:
        defaults = _dedupe_preserve(_parse_database_list(cfg_databases))
    if defaults:
        return defaults
    return DEFAULT_DATABASES.copy()


def _provider_config_for(name: str, cfg_section) -> dict:
    if isinstance(cfg_section, dict):
        val = cfg_section.get(name)
        if isinstance(val, dict):
            return val
        if isinstance(val, bool):
            return {'enabled': bool(val)}
    return {}


def _clean_secret(value):
    if isinstance(value, str):
        cleaned = value.strip().strip('"').strip("'")
        expanded = os.path.expandvars(cleaned)
        return expanded
    return value


def _instantiate_providers(names: List[str], cfg: dict, overrides: dict):
    providers = []
    cfg_section = cfg.get('databases') if isinstance(cfg.get('databases'), dict) else {}
    for name in names:
        provider_cls = PROVIDER_REGISTRY.get(name)
        if not provider_cls:
            raise SystemExit(f"Unknown database provider '{name}'. Available: {', '.join(sorted(set(PROVIDER_REGISTRY)))}")
        p_cfg = _provider_config_for(name, cfg_section or {})
        if p_cfg.get('enabled', True) is False:
            raise SystemExit(f"Database provider '{name}' is disabled via configuration.")
        kwargs = {}
        if name == 'pubmed':
            kwargs = {'email': overrides.get('ncbi_email'), 'api_key': overrides.get('ncbi_api')}
        elif name == 'scopus':
            kwargs = {
                'api_key': _clean_secret(overrides.get('scopus_api_key') or p_cfg.get('api_key')),
                'insttoken': _clean_secret(overrides.get('scopus_insttoken') or p_cfg.get('insttoken')),
                'view': p_cfg.get('view', 'STANDARD'),
                'apply_year_filter': not overrides.get('scopus_skip_date_filter', False),
            }
        elif name == 'web_of_science' or name == 'wos':
            kwargs = {
                'api_key': _clean_secret(overrides.get('wos_api_key') or p_cfg.get('api_key')),
                'db': p_cfg.get('db', 'WOS'),
            }
        providers.append(provider_cls(**kwargs))
    if not providers:
        raise SystemExit("No active database providers were instantiated. Check --databases or configuration.")
    return providers

def main():
    parser = argparse.ArgumentParser(description='LLM-assisted SR selection & scoring')
    # Note: --study-name is not globally required because `scaffold` doesn't need it
    parser.add_argument('--study-name', help='The name of the study directory under studies/')
    parser.add_argument('--config', help='Path to a TOML or JSON config file (values overridden by CLI/env).')
    parser.add_argument('--databases', help='Comma-separated list of database providers to use (e.g., pubmed,scopus).')
    parser.add_argument('--scopus-api-key', help='API key for Scopus (else set SCOPUS_API_KEY env).')
    parser.add_argument('--scopus-insttoken', help='Institution token for Scopus, if required.')
    parser.add_argument('--scopus-skip-date-filter', action='store_true', help='Disable Scopus PUBYEAR filter (useful when Insttoken is unavailable).')
    parser.add_argument('--wos-api-key', help='API key for Web of Science (else set WOS_API_KEY env).')
    sub = parser.add_subparsers(dest='cmd', required=True)

    # --- Scaffold Command ---
    p_scaffold = sub.add_parser('scaffold', help='Create a new study directory with boilerplate files.')
    p_scaffold.add_argument('name', help='The name for the new study.')

    p_sel = sub.add_parser('select', help='Select best query without gold (sealed)')
    p_sel.add_argument('--mindate')
    p_sel.add_argument('--maxdate')
    p_sel.add_argument('--concept-terms', help='CSV with concept,term_regex')
    p_sel.add_argument('--queries-txt', help='TXT with one or more queries (blank lines separate)')
    p_sel.add_argument('--outdir')
    p_sel.add_argument('--target-results', type=int, default=5000)
    p_sel.add_argument('--min-results', type=int, default=50)
    p_sel.add_argument('--ncbi-email', default=None)
    p_sel.add_argument('--ncbi-api-key', default=None)

    p_fin = sub.add_parser('finalize', help='Finalize with gold (compute recall/TP/NNR & similarity)')
    p_fin.add_argument('--sealed', help='Path or glob to sealed_*.json')
    p_fin.add_argument('--gold-csv')
    p_fin.add_argument('--use-multi-key', action='store_true', 
                       help='Enable multi-key matching (PMID OR DOI). Requires gold CSV with DOI column (e.g., *_detailed.csv)')
    p_fin.add_argument('--ncbi-email', default=None)
    p_fin.add_argument('--ncbi-api-key', default=None)

    p_score = sub.add_parser('score', help='Direct scoring of queries vs gold')
    p_score.add_argument('--mindate')
    p_score.add_argument('--maxdate')
    p_score.add_argument('--queries-txt')
    p_score.add_argument('--gold-csv')
    p_score.add_argument('--outdir')
    p_score.add_argument('--query-num-offset', type=int, default=0,
                          help='Add this offset to query_num in per-database CSV output. '
                               'Use in query-by-query mode: pass QUERY_NUM-1 so the CSV '
                               'reflects the actual query number instead of always showing 1.')
    p_score.add_argument('--use-multi-key', action='store_true',
                         help='Enable multi-key matching (PMID OR DOI). Requires gold CSV with DOI column (e.g., *_detailed.csv)')
    p_score.add_argument('--ncbi-email', default=None)
    p_score.add_argument('--ncbi-api-key', default=None)

    p_titles = sub.add_parser('print-titles', help='Fetch and print titles for PMIDs')
    p_titles.add_argument('--pmids', help='Comma-separated PMIDs')
    p_titles.add_argument('--sealed', help='Read PMIDs from a sealed_*.json')
    p_titles.add_argument('--ncbi-email', default=None)
    p_titles.add_argument('--ncbi-api-key', default=None)

    p_pdf = sub.add_parser('extract-gold', help='Extract gold list from a PDF references section')
    p_pdf.add_argument('--pdf', required=True)
    p_pdf.add_argument('--out', required=True)
    p_pdf.add_argument('--ncbi-email', default=None)
    p_pdf.add_argument('--ncbi-api-key', default=None)

    # New: score precomputed PMID sets (e.g., aggregates/*.txt or aggregates/*.csv) vs gold
    p_sets = sub.add_parser('score-sets', help='Score PMID list files against a gold list (no querying)')
    p_sets.add_argument('--sets', nargs='+', required=True, 
                        help='One or more file paths or globs to .txt (PMIDs) or .csv (pmid,doi columns) files')
    p_sets.add_argument('--gold-csv', required=True, help='CSV or TXT with a pmid column or single-column list')
    p_sets.add_argument('--outdir', required=True, help='Directory to write summary CSV and details JSON')
    p_sets.add_argument('--use-multi-key', action='store_true',
                        help='Enable multi-key matching (PMID OR DOI). Requires CSV aggregate files with pmid,doi columns '
                             'and a detailed gold standard with DOI column. Improves recall by 5-15%% for multi-database queries.')

    args = parser.parse_args()

    if args.cmd == 'scaffold':
        study_name = args.name
        study_dir = Path("studies") / study_name
        if study_dir.exists():
            print(f"Error: Study directory already exists at: {study_dir}", file=sys.stderr)
            sys.exit(1)
        
        # Create directory and boilerplate files
        study_dir.mkdir(parents=True)
        (study_dir / 'queries.txt').touch()
        (study_dir / 'concept_terms.csv').touch()
        (study_dir / 'sr_config.toml').touch()

        # Copy prompt template
        template_path = Path("Documentations/prompt_template_for_query_generation.md")
        if template_path.exists():
            (study_dir / 'prompt.md').write_text(template_path.read_text())
        
        print(f"Successfully created new study: {study_name}")
        print(f"Directory: {study_dir}")
        print("Created files:")
        print(f"- {study_dir / 'queries.txt'}")
        print(f"- {study_dir / 'concept_terms.csv'}")
        print(f"- {study_dir / 'sr_config.toml'}")
        if template_path.exists():
            print(f"- {study_dir / 'prompt.md'}")
        sys.exit(0)

    # --- Multi-study path and config logic (for all other commands) ---
    if not args.study_name:
        print("Error: --study-name is required for this command.", file=sys.stderr)
        sys.exit(1)

    study_dir = Path("studies") / args.study_name
    if not study_dir.is_dir():
        print(f"Error: Study directory not found at: {study_dir}", file=sys.stderr)
        sys.exit(1)

    # Layered config: study-specific overrides global
    global_config_path = getattr(args, 'config', None) or 'sr_config.toml'
    study_config_path = study_dir / 'sr_config.toml'

    cfg = _load_config(global_config_path)
    study_cfg = _load_config(study_config_path)
    cfg.update(study_cfg) # study values overwrite global

    # Set NCBI identity via CLI/ENV/CONFIG
    ncbi_email = _resolve(getattr(args, 'ncbi_email', None), 'NCBI_EMAIL', cfg, ['ncbi_email'])
    ncbi_api = _resolve(getattr(args, 'ncbi_api_key', None), 'NCBI_API_KEY', cfg, ['ncbi_api_key'])
    set_ncbi_identity(ncbi_email, ncbi_api)

    scopus_api = _resolve(getattr(args, 'scopus_api_key', None), 'SCOPUS_API_KEY', cfg, ['scopus_api_key'])
    scopus_inst = _resolve(getattr(args, 'scopus_insttoken', None), 'SCOPUS_INSTTOKEN', cfg, ['scopus_insttoken'])
    scopus_skip_dates = _resolve(getattr(args, 'scopus_skip_date_filter', None), 'SCOPUS_SKIP_DATE_FILTER', cfg, ['scopus_skip_date_filter'], _parse_bool) or False

    wos_api = _resolve(getattr(args, 'wos_api_key', None), 'WOS_API_KEY', cfg, ['wos_api_key'])

    requested_databases = _resolve_database_selection(getattr(args, 'databases', None), cfg)
    providers = _instantiate_providers(requested_databases, cfg, {'ncbi_email': ncbi_email, 'ncbi_api': ncbi_api,
                                                                  'scopus_api_key': scopus_api, 'scopus_insttoken': scopus_inst,
                                                                  'scopus_skip_date_filter': scopus_skip_dates,
                                                                  'wos_api_key': wos_api})

    def resolve_input_path(path_val: str) -> Path | None:
        if not path_val: return None
        p = Path(path_val)
        return p if p.is_absolute() else study_dir / p

    if args.cmd == 'select':
        # Resolve inputs for selection (CLI > ENV > CONFIG)
        mindate = _resolve(args.mindate, 'SELECT_MINDATE', cfg, ['select_mindate','mindate','SELECT_MINDATE'])
        maxdate = _resolve(args.maxdate, 'SELECT_MAXDATE', cfg, ['select_maxdate','maxdate','SELECT_MAXDATE'])
        concept_terms = resolve_input_path(_resolve(args.concept_terms, 'SELECT_CONCEPT_TERMS', cfg, ['concept_terms','SELECT_CONCEPT_TERMS']))
        queries_txt = resolve_input_path(_resolve(args.queries_txt, 'SELECT_QUERIES_TXT', cfg, ['queries_txt','SELECT_QUERIES_TXT']))
        outdir = _resolve(args.outdir, 'SELECT_OUTDIR', cfg, ['outdir','SELECT_OUTDIR'])
        target_results = _resolve(args.target_results, 'SELECT_TARGET_RESULTS', cfg, ['target_results','SELECT_TARGET_RESULTS'], int) or args.target_results
        min_results = _resolve(args.min_results, 'SELECT_MIN_RESULTS', cfg, ['min_results','SELECT_MIN_RESULTS'], int) or args.min_results
        
        missing = [k for k,v in {'mindate':mindate,'maxdate':maxdate,'concept_terms':concept_terms,'queries_txt':queries_txt,'outdir':outdir}.items() if not v]
        if missing:
            print(f"Missing required values for select: {', '.join(missing)}", file=sys.stderr); sys.exit(2)

        # Adjust outdir for study
        study_outdir = Path(outdir) / args.study_name

        queries_path = queries_txt if isinstance(queries_txt, Path) else Path(str(queries_txt))
        provider_queries = _load_queries_for_providers(providers, queries_path)
        query_bundles = _build_query_bundles(provider_queries)
        select_without_gold(providers=providers, query_bundles=query_bundles, mindate=mindate, maxdate=maxdate, concept_terms_path=concept_terms,
                            outdir=study_outdir, target_results=target_results, min_results=min_results)
    elif args.cmd == 'finalize':
        sealed_glob = _resolve(args.sealed, 'FINALIZE_SEALED_GLOB', cfg, ['sealed','FINALIZE_SEALED_GLOB'])
        gold_csv = resolve_input_path(_resolve(args.gold_csv, 'FINALIZE_GOLD_CSV', cfg, ['gold_csv','FINALIZE_GOLD_CSV']))
        missing = [k for k,v in {'sealed':sealed_glob,'gold_csv':gold_csv}.items() if not v]
        if missing:
            print(f"Missing required values for finalize: {', '.join(missing)}", file=sys.stderr); sys.exit(2)

        # Adjust sealed glob if it's not pointing inside a specific study output dir
        if args.study_name not in sealed_glob and 'outputs' in sealed_glob:
             # A bit of a heuristic: if the glob looks generic, scope it to the study
            sealed_glob = str(Path(sealed_glob).parent / args.study_name / Path(sealed_glob).name)

        finalize_with_gold(sealed_glob=sealed_glob, gold_csv=gold_csv, use_multi_key=getattr(args, 'use_multi_key', False))
    elif args.cmd == 'score':
        mindate = _resolve(args.mindate, 'SCORE_MINDATE', cfg, ['score_mindate','mindate','SCORE_MINDATE'])
        maxdate = _resolve(args.maxdate, 'SCORE_MAXDATE', cfg, ['score_maxdate','maxdate','SCORE_MAXDATE'])
        queries_txt = resolve_input_path(_resolve(args.queries_txt, 'SCORE_QUERIES_TXT', cfg, ['queries_txt','SCORE_QUERIES_TXT']))
        gold_csv = resolve_input_path(_resolve(args.gold_csv, 'SCORE_GOLD_CSV', cfg, ['gold_csv','SCORE_GOLD_CSV']))
        outdir = _resolve(args.outdir, 'SCORE_OUTDIR', cfg, ['outdir','SCORE_OUTDIR'])
        missing = [k for k,v in {'mindate':mindate,'maxdate':maxdate,'queries_txt':queries_txt,'gold_csv':gold_csv,'outdir':outdir}.items() if not v]
        if missing:
            print(f"Missing required values for score: {', '.join(missing)}", file=sys.stderr); sys.exit(2)

        # Adjust outdir for study
        study_outdir = Path(outdir) / args.study_name

        queries_path = queries_txt if isinstance(queries_txt, Path) else Path(str(queries_txt))
        provider_queries = _load_queries_for_providers(providers, queries_path)
        query_bundles = _build_query_bundles(provider_queries)
        score_queries(providers=providers, query_bundles=query_bundles, mindate=mindate, maxdate=maxdate, gold_csv=gold_csv, outdir=study_outdir, use_multi_key=getattr(args, 'use_multi_key', False), query_num_offset=getattr(args, 'query_num_offset', 0))
    elif args.cmd == 'print-titles':
        pmids = []
        if args.pmids:
            pmids = [p.strip() for p in args.pmids.split(',') if p.strip()]
        elif args.sealed:
            with open(args.sealed, 'r', encoding='utf-8') as f:
                sealed = json.load(f)
            pmids = sealed.get('retrieved_pmids', [])
        else:
            print('Provide --pmids or --sealed', file=sys.stderr); sys.exit(2)
        for r in fetch_titles(pmids):
            print(f"{r.get('PMID')}: {r.get('Title')}  [{r.get('Journal')}] {r.get('Date','').strip()})")
    elif args.cmd == 'score-sets':
        # Expand globs for set files (supports both .txt and .csv)
        set_paths: List[str] = []
        for pat in getattr(args, 'sets', []) or []:
            set_paths.extend(glob.glob(pat))
        set_paths = sorted(set(set_paths))
        if not set_paths:
            print('No set files found for provided patterns.', file=sys.stderr); sys.exit(2)
        
        outdir = Path(_resolve(args.outdir, 'SCORE_SETS_OUTDIR', cfg, ['outdir', 'score_sets_outdir'])) / args.study_name
        os.makedirs(outdir, exist_ok=True)
        
        gold_csv_path = resolve_input_path(_resolve(args.gold_csv, 'SCORE_SETS_GOLD_CSV', cfg, ['gold_csv', 'score_sets_gold_csv']))
        
        use_multi_key = getattr(args, 'use_multi_key', False)
        
        if use_multi_key:
            # Multi-key mode: load gold with DOIs and use set_metrics_multi_key
            gold_pmids, gold_dois = load_gold_multi_key(gold_csv_path)
            print(f"[INFO] Multi-key mode: Gold standard has {len(gold_pmids)} PMIDs and {len(gold_dois)} DOIs")
            
            rows = []
            details = []
            for pth in set_paths:
                name = Path(pth).stem
                ext = Path(pth).suffix.lower()
                
                if ext == '.json':
                    # JSON format (from Embase import or query results)
                    with open(pth, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    # Extract PMIDs and DOIs from all queries in the JSON
                    pmids = set()
                    dois = set()
                    for query_hash, query_data in data.items():
                        if isinstance(query_data, dict):
                            if 'retrieved_dois' in query_data:
                                dois.update(query_data['retrieved_dois'])
                            if 'retrieved_pmids' in query_data:
                                pmids.update(map(str, query_data['retrieved_pmids']))
                    m = set_metrics_multi_key(pmids, dois, gold_pmids, gold_dois)
                elif ext == '.csv':
                    # Multi-key CSV format (from aggregate_queries.py --multi-key)
                    articles = read_articles_from_csv(pth)
                    pmids = articles['pmids']
                    dois = articles['dois']
                    m = set_metrics_multi_key(pmids, dois, gold_pmids, gold_dois)
                else:
                    # Legacy .txt format (PMIDs only)
                    pmids = read_pmids_from_txt(pth)
                    dois = set()
                    m = set_metrics_multi_key(pmids, dois, gold_pmids, gold_dois)
                
                # Filter out set objects for CSV/JSON serialization
                m_for_export = {k: v for k, v in m.items() if not isinstance(v, set)}
                
                rows.append({'name': name, 'path': str(pth), **m_for_export})
                details.append({
                    'name': name, 'path': str(pth), 
                    'pmids': sorted(pmids), 
                    'dois': sorted(dois),
                    'tp_by_doi': sorted(m.get('matched_dois', set())),
                    'tp_by_pmid_fallback': sorted(m.get('matched_pmids_fallback', set())),
                    **m_for_export
                })
                
                # Enhanced output showing DOI-primary breakdown
                doi_matches = m.get('matches_by_doi', 0)
                pmid_fallback = m.get('matches_by_pmid_fallback', 0)
                warning = " ⚠️ PMID-only gold" if m.get('pmid_only_warning', False) else ""
                print(f"Set[{name}]: n={m['Retrieved']} TP={m['TP']} (DOI:{doi_matches}, PMID-fallback:{pmid_fallback}) "
                      f"Precision={m['Precision']:.3f} Recall={m['Recall']:.3f} F1={m['F1']:.3f}{warning}")
        else:
            # Legacy mode: PMID-only matching
            gold = load_gold_pmids(gold_csv_path)
            rows = []
            details = []
            for pth in set_paths:
                name = Path(pth).stem
                ext = Path(pth).suffix.lower()
                
                if ext == '.csv':
                    # Read PMIDs from CSV (ignore DOIs in legacy mode)
                    articles = read_articles_from_csv(pth)
                    pmids = articles['pmids']
                else:
                    pmids = read_pmids_from_txt(pth)
                
                m = set_metrics(pmids, gold)
                rows.append({'name': name, 'path': str(pth), **m})
                details.append({'name': name, 'path': str(pth), 'pmids': sorted(pmids), 'tp_pmids': sorted(pmids & gold), **m})
                print(f"Set[{name}]: n={len(pmids)} TP={m['TP']} Precision={m['Precision']:.3f} Recall={m['Recall']:.3f} F1={m['F1']:.3f}")
        df = pd.DataFrame(rows).sort_values(['F1','Recall','Precision'], ascending=[False, False, False])
        run_id = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        summary = os.path.join(outdir, f'sets_summary_{run_id}.csv')
        details_path = os.path.join(outdir, f'sets_details_{run_id}.json')
        df.to_csv(summary, index=False)
        with open(details_path, 'w', encoding='utf-8') as f:
            json.dump(details, f, ensure_ascii=False, indent=2)
        print('Saved:', summary)
        print('Saved:', details_path)
        return
    # elif args.cmd == 'extract-gold':
    #     df = extract_gold_from_pdf(args.pdf, out_csv=args.out)
    #     print(f'Wrote: {args.out}  (rows={len(df)})')

if __name__ == '__main__':
    main()
