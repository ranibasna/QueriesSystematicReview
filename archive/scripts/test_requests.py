import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SCOPUS_API_KEY", "your_api_key_here")

url = "https://api.elsevier.com/content/search/scopus"

# params = {
#     "query": "TITLE(sleep-disordered breathing)",
#     "count": 1
# }

# params = {
#       "query": "(TITLE-ABS-KEY(\"sleep apnea\") AND TITLE-ABS-KEY(\"dementia\"))",
#       "start": 0,
#       "count": 1,
#       "view": "STANDARD",
#   }


QUERY = open("studies/sleep_apnea/queries_scopus.txt").read().split("\n\n")[0]  # first query block

print("Using query:", QUERY)

params = {"query": QUERY, "start": 0, "count": 5, "view": "STANDARD"}
headers = {"X-ELS-APIKey": API_KEY, "Accept": "application/json"}
resp = requests.get("https://api.elsevier.com/content/search/scopus", headers=headers,
params=params)
print(resp.status_code, resp.text[:500])



headers = {
    "X-ELS-APIKey": API_KEY,
    "Accept": "application/json"
}

# r = requests.get(url, headers=headers, params=params)

# print("Response text:", r.text)

# print("Status code:", r.status_code)

# if r.status_code == 200:
#     print("✓ API key i
# s valid.")
#     print("Response snippet:", r.json()["search-results"]["opensearch:totalResults"])
# elif r.status_code == 401:
#     print("✗ Unauthorized — API key is invalid or not recognized.")
# elif r.status_code == 403:
#     print("✗ Forbidden — API key is valid but lacks permissions or entitlements.")
# else:
#     print("Other error:", r.text)
    
    
    
resp = requests.get("https://api.elsevier.com/content/search/scopus", headers=headers, params=params)
resp.raise_for_status()
data = resp.json()["search-results"]["entry"]

for idx, entry in enumerate(data, start=1):
    print(f"\n=== Article {idx} ===")
    print("Title:", entry.get("dc:title"))
    print("EID:", entry.get("eid"))
    print("Scopus ID:", entry.get("dc:identifier"))
    print("DOI:", entry.get("prism:doi"))
    print("Cover Date:", entry.get("prism:coverDate"))
    print("Journal:", entry.get("prism:publicationName"))
    print("Authors:", entry.get("dc:creator"))   
