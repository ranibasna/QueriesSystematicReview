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


def _provider_name(provider) -> str:
    return getattr(provider, 'name', provider.__class__.__name__.lower())


def _provider_query_path(base_path: Path, provider_name: str) -> Path | None:
    if provider_name == 'pubmed':
        return base_path
    stem = base_path.stem
    suffix = base_path.suffix or '.txt'
    candidates = [
        base_path.with_name(f"{stem}_{provider_name}{suffix}"),
        base_path.with_name(f"{stem}.{provider_name}{suffix}"),
        base_path.with_name(f"{stem}-{provider_name}{suffix}"),
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
        
        # Track raw results before deduplication
        total_raw_results += total
        
        # Deduplicate by DOI (Option A: Simple DOI-based deduplication)
        # Articles with DOIs are deduplicated automatically by using a set
        # Articles without DOIs may appear as duplicates (acceptable ~0.5% edge case)
        # See multi_database_edge_cases_analysis.md for rationale and Option B (future)
        combined_dois.update(dois)
        
        if getattr(provider, 'id_type', '') == 'pmid':
            combined_pmids.update(ids)
        
        provider_details[pname] = {
            'query': query,
            'results_count': total,
            'retrieved_ids': sorted(ids),
            'retrieved_dois': sorted(dois),
            'id_type': getattr(provider, 'id_type', 'id'),
        }
        total_results += total
    
    # Calculate deduplication statistics
    unique_articles = len(combined_dois)
    duplicates_removed = total_raw_results - unique_articles
    
    if duplicates_removed > 0:
        dedup_rate = (duplicates_removed / total_raw_results * 100) if total_raw_results > 0 else 0
        print(f"[INFO] Deduplication (DOI-based): {total_raw_results} raw results → {unique_articles} unique articles ({duplicates_removed} duplicates removed, {dedup_rate:.1f}%)")
    
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
        cov = concept_coverage(canonical_query, cdict)
        lint = lint_query(canonical_query)
        feats = selector_features(canonical_query, total, cov, lint, max_year, min_results, target_results)
        rec = {'query': canonical_query, 'query_sha256': hashlib.sha256(canonical_query.encode()).hexdigest(), 'results_count': total,
               **{k:v for k,v in feats.items() if k != 'vocab_info'}, 'retrieved_pmids': sorted(pmids), 'retrieved_dois': sorted(dois),
               'vocab_info': feats['vocab_info'], 'provider_details': provider_details}
        records.append(rec)
        print(f"Candidate: {rec['query_sha256'][:8]}  Results={total}  Coverage={cov:.2f}  Score={rec['score']:.3f}")
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
       (created by scripts/enhance_gold_standard.py)
    
    Note: DOI column is currently informational. For Scopus-only articles in gold,
    future enhancement could enable DOI-based matching (see tasks_multi_database.md #8.1)
    
    The enhanced format can be generated once during study setup:
        python scripts/enhance_gold_standard.py \
            studies/<study>/gold_pmids.csv \
            studies/<study>/gold_pmids_with_doi.csv
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

def finalize_with_gold(sealed_glob: str, gold_csv: str, outdir: str = None):
    sealed_files = sorted(glob.glob(sealed_glob))
    if not sealed_files:
        raise SystemError(f'No sealed files found for {sealed_glob}')
    sealed_file = sealed_files[-1]
    with open(sealed_file, 'r', encoding='utf-8') as f:
        sealed = json.load(f)
    gold = load_gold_pmids(gold_csv)
    retrieved = set(sealed['retrieved_pmids'])
    metrics = set_metrics(retrieved, gold)
    sealed.update({'finalized_utc': datetime.utcnow().isoformat(), 'gold_size': len(gold), **metrics})
    out = sealed_file.replace('sealed_', 'final_').replace('sealed_outputs', 'final_outputs')
    os.makedirs(Path(out).parent, exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(sealed, f, ensure_ascii=False, indent=2)
    print('Final metrics:', json.dumps(metrics, indent=2))
    print('Wrote:', out)
    return out

def score_queries(providers, query_bundles: List[Dict], mindate: str, maxdate: str, gold_csv: str, outdir: str):
    """Run scoring pipeline and write a summary CSV and details JSON."""
    os.makedirs(outdir, exist_ok=True)
    gold = load_gold_pmids(gold_csv)
    rows = []
    details = []
    for bundle in query_bundles:
        canonical_query = bundle['canonical']
        pmids, dois, total, provider_details = _execute_query_bundle(providers, bundle['per_provider'], mindate, maxdate)
        tp = len(pmids & gold)
        recall = tp / max(len(gold), 1)
        nnr_proxy = total / max(tp, 1)
        rec = {'query': canonical_query, 'results_count': total, 'TP': tp, 'gold_size': len(gold), 'recall': recall, 'NNR_proxy': nnr_proxy}
        rows.append(rec)
        details.append({**rec, 'retrieved_pmids': sorted(pmids), 'retrieved_dois': sorted(dois), 'tp_pmids': sorted(pmids & gold), 'provider_details': provider_details})
        print(f"Query[{hashlib.sha256(canonical_query.encode()).hexdigest()[:8]}]: results={total}  TP={tp}  recall={recall:.3f}  NNR_proxy={nnr_proxy:.2f}")
    df = pd.DataFrame(rows)
    run_id = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    summary = os.path.join(outdir, f'summary_{run_id}.csv')
    details_path = os.path.join(outdir, f'details_{run_id}.json')
    df.to_csv(summary, index=False)
    with open(details_path, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    print('Saved:', summary)
    print('Saved:', details_path)
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
    p_fin.add_argument('--ncbi-email', default=None)
    p_fin.add_argument('--ncbi-api-key', default=None)

    p_score = sub.add_parser('score', help='Direct scoring of queries vs gold')
    p_score.add_argument('--mindate')
    p_score.add_argument('--maxdate')
    p_score.add_argument('--queries-txt')
    p_score.add_argument('--gold-csv')
    p_score.add_argument('--outdir')
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

    # New: score precomputed PMID sets (e.g., aggregates/*.txt) vs gold
    p_sets = sub.add_parser('score-sets', help='Score PMID list files against a gold list (no querying)')
    p_sets.add_argument('--sets', nargs='+', required=True, help='One or more file paths or globs to .txt files containing PMIDs (one per line)')
    p_sets.add_argument('--gold-csv', required=True, help='CSV or TXT with a pmid column or single-column list')
    p_sets.add_argument('--outdir', required=True, help='Directory to write summary CSV and details JSON')

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

    requested_databases = _resolve_database_selection(getattr(args, 'databases', None), cfg)
    providers = _instantiate_providers(requested_databases, cfg, {'ncbi_email': ncbi_email, 'ncbi_api': ncbi_api,
                                                                  'scopus_api_key': scopus_api, 'scopus_insttoken': scopus_inst,
                                                                  'scopus_skip_date_filter': scopus_skip_dates})

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

        finalize_with_gold(sealed_glob=sealed_glob, gold_csv=gold_csv)
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
        score_queries(providers=providers, query_bundles=query_bundles, mindate=mindate, maxdate=maxdate, gold_csv=gold_csv, outdir=study_outdir)
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
        # Expand globs for set files
        set_paths: List[str] = []
        for pat in getattr(args, 'sets', []) or []:
            # The shell script now provides the correct glob pattern directly
            set_paths.extend(glob.glob(pat))
        set_paths = sorted(set(set_paths))
        if not set_paths:
            print('No set files found for provided patterns.', file=sys.stderr); sys.exit(2)
        
        outdir = Path(_resolve(args.outdir, 'SCORE_SETS_OUTDIR', cfg, ['outdir', 'score_sets_outdir'])) / args.study_name
        os.makedirs(outdir, exist_ok=True)
        
        gold_csv_path = resolve_input_path(_resolve(args.gold_csv, 'SCORE_SETS_GOLD_CSV', cfg, ['gold_csv', 'score_sets_gold_csv']))
        gold = load_gold_pmids(gold_csv_path)
        rows = []
        details = []
        for pth in set_paths:
            name = Path(pth).stem
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
