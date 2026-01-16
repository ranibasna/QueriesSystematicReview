import requests

API_KEY = "2e4786f1a46af8fd1a7d8568106f36c7"  # <-- put your key here

BASE_URL = "https://api.elsevier.com/content/search/scopus"

# ---- Scopus Queries --------------------------------------------------------

query_variant_a = r"""(TITLE-ABS-KEY("sleep apnea syndrome" OR "sleep apnea syndromes" OR "sleep apnea, obstructive" OR "sleep apnea, central" OR "obstructive sleep apnea" OR "sleep-disordered breathing") AND TITLE-ABS-KEY("dementia" OR "dementias" OR "alzheimer disease" OR "alzheimer's disease" OR "lewy body" OR "vascular dementia" OR "frontotemporal dementia" OR "parkinson disease" OR "cognitive dysfunction" OR "cognitive disorder"))"""

query_variant_b = r"""(TITLE-ABS-KEY("sleep apnea" OR "sleep apnoea" OR "sleep-disordered breathing" OR "sleep disordered breathing" OR "obstructive sleep apnea" OR "OSA" OR "hypopnea" OR "hypopnoea" OR "apnea-hypopnea index" OR "AHI") AND TITLE-ABS-KEY("dementia*" OR "alzheimer's disease" OR "alzheimer disease" OR "AD" OR "lewy body" OR "vascular dementia" OR "frontotemporal dementia" OR "FTD" OR "cognitive decline" OR "cognitive impairment" OR "neurocognitive disorder*"))"""

query_variant_c = r"""(TITLE-ABS-KEY("sleep apnea syndrome" OR "sleep apnea" OR "sleep apnoea" OR "sleep-disordered breathing" OR "obstructive sleep apnea") AND TITLE-ABS-KEY("dementia" OR "dementia*" OR "alzheimer disease" OR "alzheimer's disease" OR "cognitive decline" OR "cognitive impairment"))"""

query_press_rev1 = r"""(TITLE-ABS-KEY("sleep apnea" OR "sleep apnoea" OR "sleep-disordered breathing" OR "obstructive sleep apnea" OR "hypopnea" OR "hypopnoea" OR "apnea-hypopnea index") AND (TITLE-ABS-KEY("dementia*" OR "alzheimer's disease" OR "alzheimer disease" OR "vascular dementia" OR "frontotemporal dementia" OR "cognitive decline" OR "cognitive impairment" OR "neurocognitive disorder*") OR (TITLE-ABS-KEY("lewy body") AND TITLE-ABS-KEY("dementia"))))"""

query_press_rev2 = r"""(TITLE-ABS-KEY("sleep apnea" OR "sleep apnoea" OR "sleep-disordered breathing" OR "obstructive sleep apnea") AND TITLE-ABS-KEY("dementia" OR "dementia*" OR "alzheimer disease" OR "alzheimer's disease" OR "lewy body disease" OR "vascular dementia" OR "cognitive decline"))"""

queries = {
    "variant_a_high_recall": query_variant_a,
    "variant_b_balanced": query_variant_b,
    "variant_c_high_precision": query_variant_c,
    "press_revised_1": query_press_rev1,
    "press_revised_2": query_press_rev2,
}

# ---- Helper to run one query ----------------------------------------------

def run_scopus_query(name, query, count=25, start=0, view="STANDARD"):
    """
    Run a single Scopus search query and return the JSON response.
    """
    headers = {
        "Accept": "application/json",
        "X-ELS-APIKey": API_KEY,
    }
    params = {
        "query": query,
        "count": count,   # max 200 for STANDARD, usually OK
        "start": start,   # for pagination
        "view": view,     # "STANDARD" or "COMPLETE"
    }

    resp = requests.get(BASE_URL, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()

    total = data.get("search-results", {}).get("opensearch:totalResults")
    print(f"[{name}] HTTP {resp.status_code}, totalResults={total}")
    return data

# ---- Example: run all variants and print first few titles ------------------

if __name__ == "__main__":
    for name, q in queries.items():
        data = run_scopus_query(name, q, count=5, view="STANDARD")
        entries = data.get("search-results", {}).get("entry", [])
        print(f"\n=== {name} (showing up to {len(entries)} hits) ===")
        for e in entries:
            title = e.get("dc:title")
            eid = e.get("eid")
            print(f"- {title}  [EID: {eid}]")
