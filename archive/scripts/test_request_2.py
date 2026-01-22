import requests
import os
from dotenv import load_dotenv

load_dotenv()
# Replace 'YOUR_API_KEY' with your Elsevier/Scopus API key
API_KEY = os.getenv("SCOPUS_API_KEY", "your_api_key_here")

# The Scopus search query – note: this uses the Scopus search language
# query = (
#     '(TITLE-ABS-KEY("sleep apnea syndrome" OR "sleep apnea syndromes" '
#     'OR "sleep apnea, obstructive" OR "sleep apnea, central" '
#     'OR "obstructive sleep apnea" OR "sleep-disordered breathing") '
#     'AND TITLE-ABS-KEY("dementia" OR "dementias" OR "alzheimer disease" '
#     'OR "alzheimer\'s disease" OR "lewy body" OR "vascular dementia" '
#     'OR "frontotemporal dementia" OR "parkinson disease" '
#     'OR "cognitive dysfunction" OR "cognitive disorder"))'
# )

query = open("studies/sleep_apnea/queries_scopus.txt").read().split("\n\n")[0]  # first query block

# Base URL for the Scopus Search API:contentReference[oaicite:2]{index=2}
base_url = 'https://api.elsevier.com/content/search/scopus'

# Request parameters – you can adjust count (max 200) and view if needed
params = {
    'query': query,
    'count': 25,        # number of results to return (default 25, max 200)
    'view': 'COMPLETE'  # 'COMPLETE' includes more metadata than 'STANDARD'
}

# HTTP headers: include your API key and ask for JSON
headers = {
    'Accept': 'application/json',
    'X-ELS-APIKey': API_KEY
}

# Send GET request
response = requests.get(base_url, params=params, headers=headers)

# If the request fails, this will raise an HTTPError
response.raise_for_status()

# Parse JSON response
results = response.json()

# Access the list of returned documents (entries)
entries = results.get('search-results', {}).get('entry', [])
for entry in entries:
    title = entry.get('dc:title')
    eid = entry.get('eid')  # Scopus EID (document identifier)
    cover_date = entry.get('prism:coverDate')
    print(f'{title} (EID: {eid}) – {cover_date}')
