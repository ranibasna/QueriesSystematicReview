import requests
import os
from dotenv import load_dotenv

load_dotenv()
# Replace with your Embase-enabled API key and institutional token
API_KEY = os.getenv("SCOPUS_API_KEY", "your_api_key_here")
INST_TOKEN = os.getenv("SCOPUS_INSTTOKEN", "your_inst_token_here")

# Build the advanced query – Embase accepts a similar Boolean syntax to Scopus
query = (
    '(TITLE-ABS-KEY("sleep apnea syndrome" OR "sleep apnea syndromes" OR '
    '"sleep apnea, obstructive" OR "sleep apnea, central" OR '
    '"obstructive sleep apnea" OR "sleep-disordered breathing") '
    'AND TITLE-ABS-KEY("dementia" OR "dementias" OR "alzheimer disease" '
    'OR "alzheimer\'s disease" OR "lewy body" OR "vascular dementia" OR '
    '"frontotemporal dementia" OR "parkinson disease" OR '
    '"cognitive dysfunction" OR "cognitive disorder"))'
)

# Base URL for Embase article search:contentReference[oaicite:1]{index=1}
base_url = 'https://api.elsevier.com/content/embase/article/'

# Request parameters; adjust 'count' (page size) and 'start' for pagination
params = {
    'query': query,
    'count': 25,   # number of records to return per call
    'start': 0     # offset for pagination
}

# Set headers – note the need for the institutional token:contentReference[oaicite:2]{index=2}
headers = {
    'Accept': 'application/json',
    'X-ELS-APIKey': API_KEY
    # 'X-ELS-Insttoken': INST_TOKEN
}

# The Embase API expects a POST request when sending the query
response = requests.post(base_url, data=params, headers=headers)
response.raise_for_status()  # raise exception if request failed

data = response.json()

# Process results
hits = data.get('header', {}).get('hits')
print(f"Total hits: {hits}")
for record in data.get('results', []):
    info = record.get('head', {})
    title = info.get('title')
    authors = [au['familyName'] for au in info.get('authors', [])]
    pub_date = info.get('pubDate')
    doi = record.get('itemInfo', {}).get('itemIdList', {}).get('doi')
    print(f"{title} – {pub_date}, DOI: {doi}")
