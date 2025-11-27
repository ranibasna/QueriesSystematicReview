import os
import time
from typing import Protocol, Set, Tuple, List, Iterable, Optional, Dict

import requests
from Bio import Entrez
from tenacity import retry, wait_exponential, stop_after_attempt

# Set a default rate limit for API calls
RATE_LIMIT_SECONDS = 0.34
EFETCH_BATCH_SIZE = 200
SCOPUS_PAGE_SIZE = 25
SCOPUS_RATE_LIMIT_SECONDS = 0.5
WOS_PAGE_SIZE = 50  # Maximum per WoS API docs
WOS_RATE_LIMIT_SECONDS = 0.5  # Conservative rate limit


def _chunk_list(values: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(values), size):
        yield values[i : i + size]


class SearchProvider(Protocol):
    """
    Defines the standard interface for a database search provider.
    """

    def search(self, query: str, mindate: str, maxdate: str, retmax: int = 100000) -> Tuple[Set[str], Set[str], int]:
        """
        Executes a search and returns a tuple of:
        (set of DOIs, set of original provider IDs, total count)
        """
        ...


class PubMedProvider:
    """
    Search provider for PubMed.
    Uses Bio.Entrez to query PubMed and convert PMIDs to DOIs.
    """

    name = "pubmed"
    id_type = "pmid"

    def __init__(self, email: str = None, api_key: str = None):
        Entrez.email = email or os.getenv("NCBI_EMAIL", "default@example.com")
        Entrez.api_key = api_key or os.getenv("NCBI_API_KEY", None)

    @retry(wait=wait_exponential(multiplier=1, min=1, max=30), stop=stop_after_attempt(5))
    def _extract_doi(self, article: dict) -> Optional[str]:
        """Pull a DOI from a PubMed XML article record, if present."""
        article_ids = (
            article.get("PubmedData", {})
            .get("ArticleIdList", [])
        )
        for article_id in article_ids:
            attrs = getattr(article_id, "attributes", {})
            if attrs.get("IdType") == "doi":
                return str(article_id).strip()

        e_locations = (
            article.get("MedlineCitation", {})
            .get("Article", {})
            .get("ELocationID", [])
        )
        for eloc in e_locations:
            attrs = getattr(eloc, "attributes", {})
            if attrs.get("EIdType") == "doi":
                return str(eloc).strip()
        return None

    @retry(wait=wait_exponential(multiplier=1, min=1, max=30), stop=stop_after_attempt(5))
    def _get_dois_from_pmids(self, pmids: List[str]) -> Set[str]:
        """
        Fetch article details from PubMed and extract DOIs.
        Handles cases where articles may not have a DOI.
        """
        if not pmids:
            return set()

        dois = set()
        for batch in _chunk_list(pmids, EFETCH_BATCH_SIZE):
            handle = Entrez.efetch(
                db="pubmed",
                id=batch,
                rettype="medline",
                retmode="xml",
            )
            records = Entrez.read(handle)
            handle.close()
            time.sleep(RATE_LIMIT_SECONDS)

            for article in records.get("PubmedArticle", []):
                doi = self._extract_doi(article)
                if doi:
                    dois.add(doi.lower())
        return dois

    @retry(wait=wait_exponential(multiplier=1, min=1, max=30), stop=stop_after_attempt(5))
    def search(self, query: str, mindate: str, maxdate: str, retmax: int = 100000) -> Tuple[Set[str], Set[str], int]:
        """
        Search PubMed for a query, retrieve PMIDs, and convert them to DOIs.
        Returns (dois, pmids, total_count)
        """
        handle = Entrez.esearch(
            db="pubmed",
            term=query,
            datetype="pdat",
            mindate=mindate,
            maxdate=maxdate,
            retmax=retmax,
            retstart=0,
            retmode="xml",
        )
        record = Entrez.read(handle)
        handle.close()
        time.sleep(RATE_LIMIT_SECONDS)

        total_count = int(record["Count"])
        pmids = set(record.get("IdList", []))

        # Page through results if necessary
        retstart = retmax
        while retstart < total_count:
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                datetype="pdat",
                mindate=mindate,
                maxdate=maxdate,
                retmax=retmax,
                retstart=retstart,
                retmode="xml",
            )
            record = Entrez.read(handle)
            handle.close()
            time.sleep(RATE_LIMIT_SECONDS)
            pmids.update(record.get("IdList", []))
            retstart += retmax

        dois = self._get_dois_from_pmids(list(pmids))
        
        return dois, pmids, total_count


class ScopusProvider:
    """
    Search provider for Scopus Search API (Elsevier).
    """

    BASE_URL = "https://api.elsevier.com/content/search/scopus"
    name = "scopus"
    id_type = "scopus_id"

    def __init__(self, api_key: str | None = None, insttoken: str | None = None, view: str = "STANDARD", apply_year_filter: bool = True):
        self.api_key = api_key or os.getenv("SCOPUS_API_KEY")
        if not self.api_key:
            raise ValueError("Scopus API key is required (set SCOPUS_API_KEY or pass via config).")
        self.insttoken = insttoken or os.getenv("SCOPUS_INSTTOKEN")
        self.view = view
        self.apply_year_filter = apply_year_filter
        self.session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        headers = {
            "X-ELS-APIKey": self.api_key,
            "Accept": "application/json",
        }
        if self.insttoken:
            headers["X-ELS-Insttoken"] = self.insttoken
        return headers

    def _apply_year_filter(self, query: str, mindate: str, maxdate: str) -> str:
        def _year_from(val: str, default: str) -> str:
            if not val:
                return default
            parts = val.split('/')
            return parts[0] if parts else default
        if not self.apply_year_filter:
            return query
        min_year = _year_from(mindate, "1900")
        max_year = _year_from(maxdate, "2100")
        # Scopus requires > and < operators (not >= and <=) or AFT/BEF keywords
        # Using > (year-1) and < (year+1) to achieve inclusive behavior
        min_year_int = int(min_year) - 1
        max_year_int = int(max_year) + 1
        year_clause = f"PUBYEAR > {min_year_int} AND PUBYEAR < {max_year_int}"
        # Check if any year filter already exists to avoid duplication
        if "pubyear" in query.lower():
            return query
        return f"({query}) AND {year_clause}"

    def search(self, query: str, mindate: str, maxdate: str, retmax: int = 100000) -> Tuple[Set[str], Set[str], int]:
        dois: Set[str] = set()
        scopus_ids: Set[str] = set()
        total_results = 0
        retrieved = 0
        start = 0
        query_with_dates = self._apply_year_filter(query, mindate, maxdate)
        headers = self._headers()
        while start < retmax:
            count = min(SCOPUS_PAGE_SIZE, retmax - start)
            params = {
                "query": query_with_dates,
                "start": start,
                "count": count,
                "view": self.view,
            }
            try:
                resp = self.session.get(self.BASE_URL, headers=headers, params=params, timeout=60)
            except requests.RequestException as exc:
                raise RuntimeError(f"Scopus API request failed: {exc}") from exc
            if resp.status_code == 401:
                body = resp.text.strip()
                snippet = (body[:500] + ('…' if len(body) > 500 else '')) if body else 'No response body.'
                key_hint = f"{self.api_key[:4]}…{self.api_key[-4:]}" if len(str(self.api_key)) >= 8 else 'n/a'
                raise RuntimeError(f"Scopus API returned 401 Unauthorized (key hint {key_hint}). "
                                   f"This usually means the API key lacks Scopus Search entitlements or requires an Insttoken. "
                                   f"Server response: {snippet}")
            if resp.status_code == 429:
                raise RuntimeError("Scopus API rate limit reached. Try again later or reduce requests.")
            resp.raise_for_status()
            data = resp.json()
            meta = data.get("search-results", {})
            if not total_results:
                try:
                    total_results = int(meta.get("opensearch:totalResults", 0))
                except (TypeError, ValueError):
                    total_results = 0
            entries = meta.get("entry") or []
            if not entries:
                break
            for entry in entries:
                identifier = entry.get("dc:identifier") or ""
                if identifier:
                    scopus_ids.add(identifier.replace("SCOPUS_ID:", "").strip())
                doi_val = entry.get("prism:doi")
                if doi_val:
                    dois.add(str(doi_val).lower().strip())
            batch_size = len(entries)
            retrieved += batch_size
            start += batch_size
            if batch_size < count or retrieved >= retmax:
                break
            time.sleep(SCOPUS_RATE_LIMIT_SECONDS)
        return dois, scopus_ids, total_results


class WebOfScienceProvider:
    """
    Search provider for Web of Science Starter API.
    Uses Clarivate's WoS Starter API to query documents and retrieve DOIs and UIDs.
    """

    BASE_URL = "https://api.clarivate.com/apis/wos-starter/v1/documents"
    name = "web_of_science"
    id_type = "wos_uid"

    def __init__(self, api_key: str | None = None, db: str = "WOS"):
        """
        Initialize Web of Science provider.
        
        Args:
            api_key: WoS API key (or set WOS_API_KEY env var)
            db: Database abbreviation (default: "WOS" = Web of Science Core Collection)
        """
        self.api_key = api_key or os.getenv("WOS_API_KEY")
        if not self.api_key:
            raise ValueError("Web of Science API key is required (set WOS_API_KEY or pass via config).")
        self.db = db
        self.session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        """Build request headers with API key authentication."""
        return {
            "X-ApiKey": self.api_key,
            "Accept": "application/json",
        }

    def _apply_year_filter(self, query: str, mindate: str, maxdate: str) -> str:
        """
        Apply year filters using WoS PY= syntax.
        
        WoS uses PY=YYYY-YYYY format for year ranges.
        Example: PY=2015-2024
        """
        def _year_from(val: str, default: str) -> str:
            if not val:
                return default
            parts = val.split('/')
            return parts[0] if parts else default
        
        min_year = _year_from(mindate, "1900")
        max_year = _year_from(maxdate, "2100")
        
        # Check if year filter already exists
        if "py=" in query.lower():
            return query
        
        # WoS uses PY=YYYY-YYYY syntax for ranges
        year_clause = f"PY={min_year}-{max_year}"
        return f"({query}) AND {year_clause}"

    @retry(wait=wait_exponential(multiplier=1, min=1, max=30), stop=stop_after_attempt(5))
    def search(self, query: str, mindate: str, maxdate: str, retmax: int = 100000) -> Tuple[Set[str], Set[str], int]:
        """
        Search Web of Science and return (dois, wos_uids, total_count).
        
        Args:
            query: WoS advanced search query (e.g., "TS=(sleep apnea)")
            mindate: Start date (YYYY/MM/DD format)
            maxdate: End date (YYYY/MM/DD format)
            retmax: Maximum results to retrieve
            
        Returns:
            Tuple of (set of DOIs, set of WoS UIDs, total count)
        """
        dois: Set[str] = set()
        wos_uids: Set[str] = set()
        total_results = 0
        retrieved = 0
        page = 1
        
        query_with_dates = self._apply_year_filter(query, mindate, maxdate)
        headers = self._headers()
        
        while retrieved < retmax:
            limit = min(WOS_PAGE_SIZE, retmax - retrieved)
            params = {
                "q": query_with_dates,
                "db": self.db,
                "limit": limit,
                "page": page,
            }
            
            try:
                resp = self.session.get(self.BASE_URL, headers=headers, params=params, timeout=60)
            except requests.RequestException as exc:
                raise RuntimeError(f"Web of Science API request failed: {exc}") from exc
            
            # Handle authentication errors
            if resp.status_code == 401:
                body = resp.text.strip()
                snippet = (body[:500] + ('…' if len(body) > 500 else '')) if body else 'No response body.'
                key_hint = f"{self.api_key[:4]}…{self.api_key[-4:]}" if len(str(self.api_key)) >= 8 else 'n/a'
                raise RuntimeError(
                    f"Web of Science API returned 401 Unauthorized (key hint {key_hint}). "
                    f"Please verify your API key has access to WoS Starter API. "
                    f"Server response: {snippet}"
                )
            
            # Handle rate limiting
            if resp.status_code == 429:
                raise RuntimeError("Web of Science API rate limit reached. Try again later or reduce requests.")
            
            resp.raise_for_status()
            data = resp.json()
            
            # Parse metadata for total count
            metadata = data.get("metadata", {})
            if not total_results:
                try:
                    total_results = int(metadata.get("total", 0))
                except (TypeError, ValueError):
                    total_results = 0
            
            # Parse documents
            documents = data.get("hits") or []
            if not documents:
                break
            
            for doc in documents:
                # Extract UID (Accession Number)
                uid = doc.get("uid")
                if uid:
                    wos_uids.add(str(uid).strip())
                
                # Extract DOI from identifiers
                identifiers = doc.get("identifiers", {})
                doi_val = identifiers.get("doi")
                if doi_val:
                    dois.add(str(doi_val).lower().strip())
            
            batch_size = len(documents)
            retrieved += batch_size
            
            # Check if we've retrieved everything
            if batch_size < limit or retrieved >= total_results or retrieved >= retmax:
                break
            
            page += 1
            time.sleep(WOS_RATE_LIMIT_SECONDS)
        
        return dois, wos_uids, total_results


PROVIDER_REGISTRY = {
    "pubmed": PubMedProvider,
    "scopus": ScopusProvider,
    "web_of_science": WebOfScienceProvider,
    "wos": WebOfScienceProvider,
}
