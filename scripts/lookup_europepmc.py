#!/usr/bin/env python3
"""
Europe PMC lookup for DOI/PMID extraction with fuzzy matching.

Serves as an intermediate fallback between PubMed (structured) and CrossRef
(DOI-focused) to recover identifiers when PubMed misses a match.
"""

import time
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import requests

try:
    from rapidfuzz import fuzz
except ImportError:
    raise ImportError("rapidfuzz not installed. Run: pip install rapidfuzz")


@dataclass
class EuropePMCMatch:
    """Represents a Europe PMC search result match."""
    pmid: Optional[str]
    doi: Optional[str]
    title: str
    authors: List[str]
    journal: str
    year: int
    pub_types: List[str]
    similarity_score: float
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EuropePMCLookup:
    """Europe PMC client with rate limiting and multi-query search."""

    def __init__(self, email: Optional[str] = None, rate_limit: float = 10.0):
        self.email = email
        self.rate_limit = rate_limit
        self.min_delay = 1.0 / rate_limit
        self.last_request_time = 0
        self.base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

        # Request headers (Europe PMC respects user agent/email when present)
        self.headers = {
            "User-Agent": f"DOI-PMID-Extractor/1.0 (mailto:{email})" if email else "DOI-PMID-Extractor/1.0"
        }

    def _rate_limit_wait(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_delay:
            time.sleep(self.min_delay - time_since_last)
        self.last_request_time = time.time()

    def _extract_last_name(self, author: str) -> str:
        parts = author.strip().split()
        if not parts:
            return author
        if len(parts[-1]) == 1:
            return parts[-2] if len(parts) > 1 else parts[0]
        return parts[0]

    def _clean_title(self, title: str) -> str:
        cleaned = re.sub(r"[^\w\s-]", " ", title)
        return " ".join(cleaned.split())

    def _build_queries(self, title: str, first_author: str, year: Optional[int]) -> List[str]:
        cleaned_title = self._clean_title(title)
        last_name = self._extract_last_name(first_author)
        queries = []

        # Structured queries first
        if last_name and year:
            queries.append(f'(TITLE:"{cleaned_title}" AND FIRST_AUTHOR:{last_name} AND PUB_YEAR:{year})')
        if year:
            queries.append(f'(TITLE:"{cleaned_title}" AND PUB_YEAR:{year})')
        if last_name:
            queries.append(f'(TITLE:"{cleaned_title}" AND FIRST_AUTHOR:{last_name})')

        # Relaxed fallbacks
        truncated = " ".join(cleaned_title.split()[:12])
        if truncated:
            queries.append(f'(TITLE:"{truncated}")')

        queries.append(f'(TITLE:"{cleaned_title}")')
        return queries

    def search(self, title: str, first_author: str, year: Optional[int], max_results: int = 20) -> List[Dict[str, Any]]:
        queries = self._build_queries(title, first_author, year)

        for q in queries:
            self._rate_limit_wait()
            params = {
                "query": q,
                "pageSize": max_results,
                "format": "json",
            }
            try:
                resp = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                items = data.get("resultList", {}).get("result", [])
                if items:
                    return items
            except requests.RequestException as exc:
                print(f"⚠️  Europe PMC search error: {exc}")
                continue
        return []

    def parse_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            title = item.get("title", "")
            doi = item.get("doi")
            pmid = item.get("pmid") or item.get("pmcid")
            journal = item.get("journalTitle", "")
            year = int(item.get("pubYear")) if item.get("pubYear") else None
            authors = []
            author_string = item.get("authorString") or ""
            if author_string:
                authors = [a.strip() for a in author_string.split(',') if a.strip()]
            pub_types = item.get("pubTypeList", {}).get("pubType", []) if item.get("pubTypeList") else []

            return {
                "title": title,
                "doi": doi,
                "pmid": pmid,
                "journal": journal,
                "year": year,
                "authors": authors,
                "pub_types": pub_types,
            }
        except Exception as exc:
            print(f"⚠️  Error parsing Europe PMC item: {exc}")
            return None

    def calculate_similarity(self, extracted_title: str, candidate_title: str) -> float:
        ratio = fuzz.token_sort_ratio(extracted_title.lower().strip(), candidate_title.lower().strip())
        return ratio / 100.0

    def _type_penalty(self, pub_types: List[str]) -> float:
        lower_types = {t.lower() for t in pub_types}
        if any("preprint" in t for t in lower_types):
            return 0.85
        return 1.0

    def _validate_metadata(
        self,
        extracted_study: Dict[str, Any],
        metadata: Dict[str, Any],
        max_year_diff: int
    ) -> bool:
        extracted_year = extracted_study.get("year")
        candidate_year = metadata.get("year")
        if extracted_year and candidate_year:
            if abs(candidate_year - extracted_year) > max_year_diff:
                return False

        extracted_last = self._extract_last_name(extracted_study.get("first_author", "")).lower()
        authors = metadata.get("authors", [])
        if extracted_last:
            if not any(extracted_last in a.lower() for a in authors[:5]):
                return False

        return True

    def calculate_confidence(
        self,
        similarity_score: float,
        num_results: int,
        author_match: bool,
        year_match: bool,
        type_penalty: float = 1.0
    ) -> float:
        confidence = similarity_score

        if similarity_score >= 0.95 and author_match and year_match:
            confidence = 0.95
        elif similarity_score >= 0.90:
            confidence = 0.90 if (author_match and year_match) else 0.85
        elif similarity_score >= 0.80:
            confidence = 0.80 if author_match else 0.70
        elif similarity_score >= 0.70:
            confidence = 0.60
        else:
            confidence = similarity_score * 0.5

        if num_results > 10:
            confidence *= 0.95

        confidence *= type_penalty
        return round(confidence, 3)

    def find_best_match(
        self,
        extracted_study: Dict[str, Any],
        max_results: int = 20,
        min_confidence: float = 0.80,
        max_year_diff: int = 1
    ) -> Optional[EuropePMCMatch]:
        title = extracted_study.get("title", "")
        first_author = extracted_study.get("first_author", "")
        year = extracted_study.get("year")

        if not title:
            return None

        items = self.search(title, first_author, year, max_results)
        if not items:
            return None

        candidates: List[EuropePMCMatch] = []
        for item in items:
            metadata = self.parse_item(item)
            if not metadata:
                continue

            if not self._validate_metadata(extracted_study, metadata, max_year_diff):
                continue

            sim = self.calculate_similarity(title, metadata.get("title", ""))
            authors = metadata.get("authors", [])
            extracted_last = self._extract_last_name(first_author).lower()
            author_match = any(extracted_last in a.lower() for a in authors[:5]) if extracted_last else False
            year_match = (year == metadata.get("year")) if year and metadata.get("year") else False

            confidence = self.calculate_confidence(
                sim,
                len(items),
                author_match,
                year_match,
                type_penalty=self._type_penalty(metadata.get("pub_types", []))
            )

            if confidence >= min_confidence:
                candidates.append(
                    EuropePMCMatch(
                        pmid=metadata.get("pmid"),
                        doi=metadata.get("doi"),
                        title=metadata.get("title", ""),
                        authors=authors,
                        journal=metadata.get("journal", ""),
                        year=metadata.get("year") or 0,
                        pub_types=metadata.get("pub_types", []),
                        similarity_score=sim,
                        confidence=confidence,
                    )
                )

        if not candidates:
            return None

        return max(candidates, key=lambda c: c.confidence)


# Convenience wrapper

def find_best_epmc(
    title: str,
    first_author: str,
    year: int,
    email: Optional[str] = None,
    min_confidence: float = 0.80
) -> Optional[Dict[str, Any]]:
    client = EuropePMCLookup(email)
    study = {
        "title": title,
        "first_author": first_author,
        "year": year,
    }
    match = client.find_best_match(study, min_confidence=min_confidence)
    if not match:
        return None
    return {
        "pmid": match.pmid,
        "doi": match.doi,
        "confidence": match.confidence,
        "similarity": match.similarity_score,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python lookup_europepmc.py <your_email@domain.com>")
        sys.exit(1)

    email = sys.argv[1]
    test_study = {
        "title": "Twenty-four-hour ambulatory blood pressure in children with sleep-disordered breathing",
        "first_author": "Amin RS",
        "year": 2004,
    }

    print("🔍 Testing Europe PMC Lookup")
    client = EuropePMCLookup(email)
    match = client.find_best_match(test_study)
    if match:
        print(f"✅ PMID: {match.pmid} DOI: {match.doi} Conf: {match.confidence:.2f}")
    else:
        print("❌ No match found")
