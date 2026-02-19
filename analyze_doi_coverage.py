import json
import os
import glob

BASE = '/Users/ra1077ba/Documents/DataScience/GU/Daniil/LLM/QueriesSystematicReview'

print('=== DOI COVERAGE ANALYSIS: ai_2022 ===\n')

results = {}

for q in range(1, 7):
    q_label = f'query_{q:02d}'
    results[q_label] = {}

    # --- WoS & Scopus from benchmark_outputs ---
    bm_dir = os.path.join(BASE, 'benchmark_outputs', 'ai_2022', q_label)
    bm_files = glob.glob(os.path.join(bm_dir, 'details_*.json'))
    if bm_files:
        bm_file = sorted(bm_files)[-1]  # most recent
        with open(bm_file) as f:
            data = json.load(f)
        item = data[0] if isinstance(data, list) else data
        provider_details = item.get('provider_details', {})

        for prov_key, prov_label in [('web_of_science', 'WoS'), ('scopus', 'Scopus')]:
            pdata = provider_details.get(prov_key, {})
            total = pdata.get('results_count', 0)
            dois = pdata.get('retrieved_dois', [])
            n_dois = len(dois) if isinstance(dois, list) else dois
            no_doi = total - n_dois
            results[q_label][prov_label] = {'total': total, 'with_doi': n_dois, 'no_doi': no_doi}
    else:
        print(f'  WARNING: No benchmark file found for {q_label}')
        results[q_label]['WoS'] = None
        results[q_label]['Scopus'] = None

    # --- Embase from studies/ai_2022 ---
    emb_file = os.path.join(BASE, 'studies', 'ai_2022', f'embase_query{q}.json')
    if os.path.exists(emb_file):
        with open(emb_file) as f:
            data = json.load(f)
        key = list(data.keys())[0]
        entry = data[key]
        records = entry.get('records', [])
        total = len(records)
        with_doi = sum(
            1 for r in records
            if r.get('doi') and str(r.get('doi', '')).strip() not in ('', 'None', 'nan', 'N/A')
        )
        no_doi = total - with_doi
        results[q_label]['Embase'] = {'total': total, 'with_doi': with_doi, 'no_doi': no_doi}
    else:
        print(f'  WARNING: No Embase file found for query {q}')
        results[q_label]['Embase'] = None

# --- Print table ---
col = 12
print(f"{'Query':<{col}} {'Database':<10} {'Total':>8} {'With DOI':>10} {'No DOI':>8} {'% No DOI':>10}")
print('-' * 62)

totals = {'WoS': [0, 0, 0], 'Scopus': [0, 0, 0], 'Embase': [0, 0, 0]}

for q_label in sorted(results.keys()):
    dbs = results[q_label]
    for db in ['WoS', 'Scopus', 'Embase']:
        info = dbs.get(db)
        if info:
            pct = (info['no_doi'] / info['total'] * 100) if info['total'] > 0 else 0
            print(f"{q_label:<{col}} {db:<10} {info['total']:>8,} {info['with_doi']:>10,} {info['no_doi']:>8,} {pct:>9.1f}%")
            totals[db][0] += info['total']
            totals[db][1] += info['with_doi']
            totals[db][2] += info['no_doi']
        else:
            print(f"{q_label:<{col}} {db:<10} {'N/A':>8}")
    print()

print('=== TOTALS (sum across all 6 queries, not deduplicated) ===')
print('-' * 62)
for db in ['WoS', 'Scopus', 'Embase']:
    t = totals[db]
    pct = (t[2] / t[0] * 100) if t[0] > 0 else 0
    print(f"{'ALL':<{col}} {db:<10} {t[0]:>8,} {t[1]:>10,} {t[2]:>8,} {pct:>9.1f}%")
