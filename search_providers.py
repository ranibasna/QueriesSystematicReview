import hashlib
import json
import logging
import os
import sys
import time
from typing import Protocol, Set, Tuple, List, Iterable, Optional, Dict, Union

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

    def _extract_article_metadata(self, article: dict) -> dict:
        """
        Extract article-level metadata (title, first_author, year, journal) from a
        PubMed XML record returned by Entrez.efetch.

        Returns a dict with only the keys whose values are non-None/non-empty.
        Silently returns {} on any extraction error so that a malformed record never
        interrupts the main search loop.

        Used by W4.1 to populate ``_metadata_cache`` for downstream fuzzy matching.
        """
        meta: dict = {}
        try:
            mc = article.get("MedlineCitation", {})
            art = mc.get("Article", {})

            # Title
            raw_title = art.get("ArticleTitle")
            if raw_title:
                title_str = str(raw_title).strip()
                if title_str:
                    meta["title"] = title_str

            # First author (last name)
            author_list = art.get("AuthorList", [])
            if author_list:
                last_name = str(author_list[0].get("LastName", "") or "").strip()
                if last_name:
                    meta["first_author"] = last_name

            # Year — prefer PubDate Year; fallback to MedlineDate first 4 chars
            journal = art.get("Journal", {})
            pub_date = journal.get("JournalIssue", {}).get("PubDate", {})
            year_str = str(pub_date.get("Year", "") or "").strip()
            if year_str.isdigit():
                meta["year"] = int(year_str)
            else:
                med_date = str(pub_date.get("MedlineDate", "") or "").strip()
                if med_date and med_date[:4].isdigit():
                    meta["year"] = int(med_date[:4])

            # Journal title
            journal_title = str(journal.get("Title", "") or "").strip()
            if journal_title:
                meta["journal"] = journal_title

        except Exception:
            pass  # Never raise — metadata extraction is best-effort

        return meta

    def _crossref_lookup(self, pmid: str) -> Optional[str]:
        """
        Fallback DOI lookup via CrossRef for a single PMID that PubMed XML did not
        carry a DOI for.  Uses the polite-pool endpoint with a mailto parameter.

        Returns the lowercased DOI string on success, or None on any failure
        (HTTP error, timeout, empty result, or PMID round-trip mismatch).

        Class E guard: if CrossRef returns a record whose own PMID field differs
        from the queried PMID (can happen for errata/corrections), the DOI is
        rejected to avoid mis-attribution.
        """
        mailto = Entrez.email or "default@example.com"
        url = "https://api.crossref.org/works"
        params = {
            "filter": f"from-pub-date:1000,pmid:{pmid}",
            "mailto": mailto,
            "rows": 1,
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("message", {}).get("items", [])
            if not items:
                return None
            item = items[0]
            # Class E guard: if CrossRef returns a record carrying a different PMID
            # (e.g. an erratum), reject it to avoid mis-attribution.
            item_pmid = str(item.get("PMID", "")).strip()
            if item_pmid and item_pmid != str(pmid):
                return None
            doi = item.get("DOI", "")
            return doi.lower() if doi else None
        except Exception:
            return None

    @retry(wait=wait_exponential(multiplier=1, min=1, max=30), stop=stop_after_attempt(5))
    def _get_dois_from_pmids(self, pmids: List[str]) -> Dict[str, str]:
        """
        Fetch article details from PubMed and extract DOIs.

        Returns a {pmid: doi} mapping for each article that has both identifiers.
        Articles without a DOI are absent from the mapping; their PMIDs are still
        present in the set returned by search().  The caller should set
        self._pmid_to_doi_cache = result so that _execute_query_bundle can read the
        preserved pairing without altering the search() return signature.

        W4.1 side effect: sets ``self._metadata_cache`` — a DOI-keyed dict of article
        metadata (title, first_author, year, journal) extracted from the same efetch
        XML records.  PMID-only articles (no DOI) are keyed as ``"pmid:{pmid}"``.
        This attribute is reset to {} at the start of every call so that stale data
        from a previous query never leaks into the current one.
        """
        # W4.1: Reset in case this method is never reached in the loop (empty pmids
        # handled below), so the attribute always exists on the instance.
        self._metadata_cache: Dict[str, dict] = {}
        if not pmids:
            return {}

        pmid_to_doi: Dict[str, str] = {}
        # W4.1: temporary PMID-keyed store; converted to DOI keys at the end
        _pmid_meta_tmp: Dict[str, dict] = {}

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
                pmid = str(article.get("MedlineCitation", {}).get("PMID", ""))
                doi = self._extract_doi(article)
                if pmid and doi:
                    pmid_to_doi[pmid] = doi.lower()
                # W4.1: extract metadata for every article, regardless of DOI
                if pmid:
                    meta = self._extract_article_metadata(article)
                    if meta:
                        _pmid_meta_tmp[pmid] = meta

        # W4.1: convert PMID-keyed metadata to DOI-keyed (primary) or pmid:XXXX
        # (fallback for PMID-only articles).  This happens after the full loop so
        # that all pmid→doi mappings are available before the key conversion.
        metadata_cache: Dict[str, dict] = {}
        for pmid, meta in _pmid_meta_tmp.items():
            doi = pmid_to_doi.get(pmid)
            key = doi if doi else f"pmid:{pmid}"
            metadata_cache[key] = meta
        self._metadata_cache = metadata_cache

        # W2.1b: CrossRef fallback for PMIDs that PubMed XML didn't carry a DOI for
        unresolved = [p for p in pmids if p not in pmid_to_doi]
        if unresolved:
            gained = 0
            for pmid in unresolved:
                doi = self._crossref_lookup(pmid)
                if doi:
                    pmid_to_doi[pmid] = doi
                    # Also update metadata cache key if metadata was captured
                    fallback_key = f"pmid:{pmid}"
                    if fallback_key in self._metadata_cache:
                        self._metadata_cache[doi] = self._metadata_cache.pop(fallback_key)
                    gained += 1
                    logging.debug("CrossRef fallback: PMID %s → %s", pmid, doi)
            logging.info(
                "CrossRef fallback: %d/%d unresolved PMIDs gained a DOI",
                gained, len(unresolved),
            )

        return pmid_to_doi

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

        pmid_to_doi = self._get_dois_from_pmids(list(pmids))
        # Cache the PMID↔DOI mapping as an instance attribute so that
        # _execute_query_bundle can read it without changing the search() return
        # signature.  The cache is overwritten on each call (one call per query
        # bundle), so callers must read it immediately after search() returns.
        self._pmid_to_doi_cache: Dict[str, str] = pmid_to_doi
        dois = set(pmid_to_doi.values())

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
        # W4.1: article metadata keyed by DOI (lowercase); populated from each entry
        self._metadata_cache: Dict[str, dict] = {}
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
                doi_key: Optional[str] = None
                if doi_val:
                    doi_key = str(doi_val).lower().strip()
                    dois.add(doi_key)
                # W4.1: extract metadata — only store when DOI is available;
                # Scopus-only records wthout a DOI cannot be linked to gold articles
                # at scoring time, so metadata without a lookup key is useless.
                if doi_key:
                    _title = str(entry.get("dc:title") or "").strip() or None
                    # dc:creator: typically "LastName Initials" or "LastName, First"
                    _creator = str(entry.get("dc:creator") or "").strip()
                    _first_author = _creator.split(",")[0].strip() or None
                    # prism:coverDate: "YYYY-MM-DD" or "YYYY" → extract year
                    _cover = str(entry.get("prism:coverDate") or "").strip()
                    _year = int(_cover[:4]) if _cover and _cover[:4].isdigit() else None
                    _journal = str(entry.get("prism:publicationName") or "").strip() or None
                    _meta = {k: v for k, v in {
                        "title": _title, "first_author": _first_author,
                        "year": _year, "journal": _journal,
                    }.items() if v is not None}
                    if _meta:
                        self._metadata_cache[doi_key] = _meta
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
        # W4.1: article metadata keyed by DOI (lowercase)
        self._metadata_cache: Dict[str, dict] = {}
        
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
                doi_key: Optional[str] = None
                if doi_val:
                    doi_key = str(doi_val).lower().strip()
                    dois.add(doi_key)

                # W4.1: extract metadata — only keyed by DOI (same reasoning as Scopus)
                if doi_key:
                    _title_raw = doc.get("title")
                    _title = str(_title_raw).strip() if _title_raw else None
                    # names.authors[0].displayName → "LastName, FirstName" or "LastName F."
                    _authors = doc.get("names", {}).get("authors", [])
                    _first_author: Optional[str] = None
                    if _authors:
                        _display = str(_authors[0].get("displayName", "") or "").strip()
                        _first_author = _display.split(",")[0].strip() or None
                    _source = doc.get("source", {})
                    _pub_year = _source.get("publishYear")
                    _year: Optional[int] = None
                    if _pub_year is not None:
                        try:
                            _year = int(_pub_year)
                        except (TypeError, ValueError):
                            pass
                    _journal = str(_source.get("sourceTitle", "") or "").strip() or None
                    _meta = {k: v for k, v in {
                        "title": _title, "first_author": _first_author,
                        "year": _year, "journal": _journal,
                    }.items() if v is not None}
                    if _meta:
                        self._metadata_cache[doi_key] = _meta
            
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
    # EmbaseLocalProvider is intentionally absent from PROVIDER_REGISTRY:
    # it requires a json_path constructor argument and is instantiated explicitly
    # by the caller (e.g. via the --embase-jsons CLI flag added in W3.2),
    # not through the generic key-based _instantiate_providers() factory.
}
logger = logging.getLogger(__name__)


class EmbaseLocalProvider:
    """
    Search provider for Embase results that were manually exported from the Embase
    website and pre-imported via ``scripts/import_embase_manual.py``.

    Because Embase has no machine-readable API, results are stored as JSON files on
    disk by the existing import script and loaded at query time.  This provider
    presents the same interface as PubMedProvider / ScopusProvider / WebOfScienceProvider
    so that ``_execute_query_bundle`` can treat Embase identically to any API-backed
    database.

    JSON file format (written by import_embase_manual.py)::

        {
          "<sha256_of_query_text>": {
            "query":          "<the Embase query string>",
            "provider":       "embase_manual",
            "results_count":  <int>,
            "retrieved_dois": ["10.x/y", ...],
            "retrieved_pmids": ["12345", ...],          # articles cross-referenced to PubMed
            "pmids":          ["12345", ...],           # legacy alias — same list
            "records": [
              {"pmid": "12345", "doi": "10.x/y", "title": "..."},
              ...
            ],
            ...
          }
        }

    Key design decisions (aligned with the W3 plan):

    * ``id_type = 'pmid'`` — Embase CSV exports include NCBI-validated PMIDs for indexed
      articles.  Setting id_type to 'pmid' causes ``_execute_query_bundle`` to add
      Embase PMIDs to ``combined_pmids`` and to the PMID fallback count, which is correct
      because these are real PubMed IDs.

    * Query lookup uses SHA-256 of the query string — identical to the hash key written by
      ``import_embase_manual.py``'s ``create_workflow_json()``.

    * Date bounds are informational only.  Embase CSVs are date-filtered at export time
      by the researcher.  A DEBUG log message is emitted when date bounds are received.

    * ``_pmid_to_doi_cache`` is populated from ``records`` (per-record paired data),
      integrating with W2.1's enrichment flow so that Embase PMID↔DOI pairs propagate
      to ``combined_pmid_to_doi`` in ``_execute_query_bundle``.

    * ``linked_records`` is NOT built here; it is constructed by ``_execute_query_bundle``
      from ``_pmid_to_doi_cache`` and the set of PMIDs returned by ``search()``, using
      exactly the same logic as for PubMedProvider.  This avoids duplicating that logic.

    Constraints / known limitations:
    * If no JSON file is found for the query hash, ``search()`` returns an empty result
      rather than raising an error.  This allows the workflow to continue gracefully when
      a query-specific Embase file is missing (e.g. a query that returned no Embase
      results was imported as an empty placeholder).
    * The JSON file must have been produced with the same query text used here; any
      whitespace normalisation or encoding differences will cause a hash mismatch.
    """

    name = "embase"
    id_type = "pmid"  # Embase records carry NCBI-validated PMIDs

    def __init__(self, json_paths: Union[str, List[str]]):
        """
        Args:
            json_paths: Path (str) or list of paths to Embase JSON files produced by
                        import_embase_manual.py (e.g. ``studies/ai_2022/embase_query1.json``).
                        Multiple paths are merged into a single entry lookup keyed by
                        SHA-256 hash — enabling a single provider instance to serve all
                        N query entries in normal mode (one file per query index).

                        Backward-compatible: a single ``str`` path is also accepted.
        """
        if isinstance(json_paths, str):
            self._json_paths: List[str] = [json_paths]
        else:
            self._json_paths = list(json_paths)
        # Keep _json_path (singular) pointing at the first entry for backward compat
        # with code that only needs the primary path (e.g. repr / logging).
        self._json_path: str = self._json_paths[0] if self._json_paths else ""
        self._data: Dict | None = None  # lazy-loaded on first search()

    def _load(self) -> Dict:
        """Load and merge all JSON file contents into a single entry dict."""
        if self._data is None:
            merged: Dict = {}
            for path in self._json_paths:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as fh:
                        try:
                            merged.update(json.load(fh))
                        except json.JSONDecodeError as exc:
                            print(
                                f"[WARN] EmbaseLocalProvider: failed to parse {path}: {exc}",
                                file=sys.stderr,
                            )
            self._data = merged
        return self._data  # type: ignore[return-value]

    def search(
        self,
        query: str,
        mindate: str,
        maxdate: str,
        retmax: int = 100000,
    ) -> Tuple[Set[str], Set[str], int]:
        """
        Load pre-imported Embase results for the given query text.

        Date bounds are informational only — Embase results were date-filtered at
        export time.  A DEBUG message is logged when bounds are provided.

        Returns:
            (dois, pmids, total_count)  — same signature as other providers.

        Side effects:
            Sets ``self._pmid_to_doi_cache: Dict[str, str]`` so that
            ``_execute_query_bundle`` can read the authoritative PMID↔DOI pairing
            without changing the search() return signature (W2.1 pattern).
        """
        if mindate or maxdate:
            logger.debug(
                "[embase] Date bounds received (%s – %s) — Embase results are "
                "pre-filtered at export time; bounds are informational only.",
                mindate,
                maxdate,
            )

        existing = [p for p in self._json_paths if os.path.exists(p)]
        if not existing:
            paths_str = ", ".join(self._json_paths) if len(self._json_paths) <= 3 else \
                f"{', '.join(self._json_paths[:3])} … ({len(self._json_paths)} total)"
            print(
                f"[WARN] EmbaseLocalProvider: no JSON file(s) found at: {paths_str}. "
                "Returning empty results.",
                file=sys.stderr,
            )
            self._pmid_to_doi_cache: Dict[str, str] = {}
            self._metadata_cache: Dict[str, dict] = {}
            return set(), set(), 0

        data = self._load()
        query_hash = hashlib.sha256(query.encode()).hexdigest()

        entry = data.get(query_hash)
        if entry is None:
            # Try a linear search in case there is only one entry and the caller
            # used a slightly different query text (e.g. stripped vs non-stripped).
            # Only fall back when there is exactly one entry; ambiguity is an error.
            entries = list(data.values())
            if len(entries) == 1:
                entry = entries[0]
                logger.debug(
                    "[embase] Exact hash miss for query; falling back to the single "
                    "entry in %s (single-entry file).",
                    self._json_path,
                )
            else:
                print(
                    f"[WARN] EmbaseLocalProvider: no entry found for query hash "
                    f"{query_hash[:8]} in {self._json_path} ({len(data)} entries). "
                    "Returning empty results.",
                    file=sys.stderr,
                )
                self._pmid_to_doi_cache = {}
                self._metadata_cache = {}
                return set(), set(), 0

        # Build the PMID↔DOI cache from the per-record paired data.
        # ``records`` carries the most accurate per-article pairing; fall back to
        # zip(pmids, dois) for legacy files that lack a ``records`` list.
        pmid_to_doi: Dict[str, str] = {}
        records: List[Dict] = entry.get("records", [])
        if records:
            for rec in records:
                if not isinstance(rec, dict):
                    continue
                pmid = rec.get("pmid")
                doi = rec.get("doi")
                if pmid and doi:
                    pmid_to_doi[str(pmid)] = str(doi).lower()
        else:
            # Legacy: pair by the flat lists already in the entry.
            flat_pmids: List[str] = [str(p) for p in (entry.get("retrieved_pmids") or entry.get("pmids") or []) if p]
            flat_dois: List[str] = [str(d).lower() for d in (entry.get("retrieved_dois") or []) if d]
            for p, d in zip(flat_pmids, flat_dois):
                if p and d:
                    pmid_to_doi[p] = d

        self._pmid_to_doi_cache = pmid_to_doi

        # W4.1: Build metadata cache from per-record fields.
        # Key: DOI (lowercase) when available, "pmid:{pmid}" for PMID-only records.
        # Only fields with non-None/non-empty values are stored (no null inflation).
        # When the records list is missing (legacy import), the cache is left empty;
        # W4.3 will simply skip Layer 3 for this provider — graceful degradation.
        meta_cache: Dict[str, dict] = {}
        for rec in records:
            if not isinstance(rec, dict):
                continue
            rec_doi = rec.get("doi")
            rec_pmid = rec.get("pmid")
            doi_lower = str(rec_doi).lower().strip() if rec_doi else None
            key: Optional[str] = doi_lower or (f"pmid:{rec_pmid}" if rec_pmid else None)
            if not key:
                continue
            _meta: dict = {}
            _title = str(rec.get("title", "") or "").strip()
            if _title:
                _meta["title"] = _title
            _fa = str(rec.get("first_author", "") or "").strip()
            if _fa:
                _meta["first_author"] = _fa
            _yr = rec.get("year")
            if _yr is not None:
                try:
                    _meta["year"] = int(_yr)
                except (TypeError, ValueError):
                    pass
            _jn = str(rec.get("journal", "") or "").strip()
            if _jn:
                _meta["journal"] = _jn
            if _meta:
                meta_cache[key] = _meta
        self._metadata_cache: Dict[str, dict] = meta_cache

        # Build return sets from the JSON entry — always use the stored lists as the
        # authoritative source (not re-derived from the cache) so that PMID-only
        # articles (no DOI) are included in the pmids return set.
        pmids: Set[str] = {
            str(p) for p in (entry.get("retrieved_pmids") or entry.get("pmids") or []) if p
        }
        dois: Set[str] = {
            str(d).lower() for d in (entry.get("retrieved_dois") or []) if d
        }
        total_count: int = entry.get("results_count", len(dois))

        return dois, pmids, total_count
