#!/usr/bin/env python3
"""
PubMed E-utilities lookup for DOI and PMID extraction.

This module provides functions to search PubMed using title, author, and year,
and retrieve both PMID and DOI for included studies.

Key features:
- Search PubMed using Entrez E-utilities
- Fuzzy title matching for disambiguation
- Confidence scoring for matches
- Rate limiting (3 req/sec without API key, 10 req/sec with key)
- Extraction of both PMID and DOI

Usage:
    from scripts.lookup_pmid import search_pubmed, fetch_pubmed_metadata
    
    results = search_pubmed(
        title="Childhood OSA and blood pressure",
        first_author="Chan",
        year=2020,
        email="your@email.com"
    )
"""

import time
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import xml.etree.ElementTree as ET

try:
    from Bio import Entrez
except ImportError:
    raise ImportError("Biopython not installed. Run: pip install biopython")

try:
    from rapidfuzz import fuzz
except ImportError:
    raise ImportError("rapidfuzz not installed. Run: pip install rapidfuzz")


@dataclass
class PubMedMatch:
    """Represents a PubMed search result match."""
    pmid: str
    doi: Optional[str]
    title: str
    authors: List[str]
    journal: str
    year: int
    similarity_score: float
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class PubMedLookup:
    """
    PubMed E-utilities lookup client with rate limiting and fuzzy matching.
    """
    
    def __init__(
        self,
        email: str,
        api_key: Optional[str] = None,
        rate_limit: Optional[float] = None
    ):
        """
        Initialize PubMed lookup client.
        
        Args:
            email: Required by NCBI for API usage tracking
            api_key: Optional API key (increases rate limit to 10 req/sec)
            rate_limit: Custom rate limit in requests per second
                       (default: 3 without key, 10 with key)
        """
        self.email = email
        self.api_key = api_key
        
        # Configure Entrez
        Entrez.email = email
        if api_key:
            Entrez.api_key = api_key
        
        # Set rate limit
        if rate_limit:
            self.rate_limit = rate_limit
        elif api_key:
            self.rate_limit = 10.0  # 10 req/sec with API key
        else:
            self.rate_limit = 3.0   # 3 req/sec without API key
        
        self.min_delay = 1.0 / self.rate_limit
        self.last_request_time = 0
    
    def _rate_limit_wait(self):
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _normalize_title(self, title: str) -> str:
        """
        Normalize title to handle PDF extraction errors and variations.
        
        Fixes:
        - Unicode ligatures (uniFB01 -> fi, uniFB02 -> fl)
        - Missing hyphens in compounds (fourhour -> four-hour, Baroreflex)
        - Extra spaces and special characters
        """
        # Fix common Unicode ligatures from PDF extraction
        title = title.replace('/uniFB01', 'fi')
        title = title.replace('/uniFB02', 'fl')
        title = title.replace('uniFB01', 'fi')
        title = title.replace('uniFB02', 'fl')
        
        # Fix "Barore flex" or "Barore fl ex" -> "Baroreflex" (common medical term)
        title = re.sub(r'Barore\s+fl?\s*ex', 'Baroreflex', title, flags=re.IGNORECASE)
        
        # Fix common compound words that lost hyphens
        # Pattern: number-words like "twenty-four" (twenty + fourhour -> twenty-four-hour)
        title = re.sub(r'(Twenty|Thirty|Forty|Fifty)-(four|five|six|seven|eight|nine)hour', 
                      r'\1-\2-hour', title, flags=re.IGNORECASE)
        
        # Pattern: number + hour/day/etc should have hyphen
        title = re.sub(r'(\d+)(hour|day|week|month|year)(?!\-)', r'\1-\2', title, flags=re.IGNORECASE)
        
        # Normalize whitespace
        title = ' '.join(title.split())
        
        return title
    
    def _clean_title(self, title: str) -> str:
        """
        Clean title for search query.
        
        Removes special characters, normalizes whitespace.
        """
        # First normalize (fix PDF errors)
        title = self._normalize_title(title)
        
        # Remove special characters except spaces and hyphens
        cleaned = re.sub(r'[^\w\s\-]', ' ', title)
        # Normalize whitespace
        cleaned = ' '.join(cleaned.split())
        return cleaned
    
    def _extract_last_name(self, author: str) -> str:
        """
        Extract last name from author string.
        
        Handles formats like:
        - "Smith J"
        - "Smith"
        - "von Smith J"
        """
        parts = author.strip().split()
        if not parts:
            return author
        
        # If last part is single letter (initial), take second-to-last
        if len(parts[-1]) == 1:
            return parts[-2] if len(parts) > 1 else parts[0]
        
        # Otherwise, first part is last name
        return parts[0]
    
    def search_pubmed(
        self,
        title: str,
        first_author: str,
        year: int,
        max_results: int = 10
    ) -> List[str]:
        """
        Search PubMed for studies matching title, author, and year.
        
        Args:
            title: Study title
            first_author: First author name (e.g., "Smith J" or "Smith")
            year: Publication year
            max_results: Maximum number of PMIDs to return
        
        Returns:
            List of PMIDs matching the search criteria
        """
        self._rate_limit_wait()
        
        # Build search query
        cleaned_title = self._clean_title(title)
        last_name = self._extract_last_name(first_author)
        
        # Try two search strategies:
        # 1. Exact title match (if available)
        # 2. Title words + author + year (more lenient)
        
        queries = []
        
        # Strategy 1: Exact title (quoted)
        queries.append(f'"{cleaned_title}"[Title] AND {last_name}[Author] AND {year}[PDAT]')
        
        # Strategy 2: Title words (unquoted for fuzzy matching)
        queries.append(f'{cleaned_title}[Title] AND {last_name}[Author] AND {year}[PDAT]')
        
        # Strategy 3: Key terms only (first 5 significant words)
        title_words = [w for w in cleaned_title.split() if len(w) > 3][:5]
        if title_words:
            key_terms = ' '.join(title_words)
            queries.append(f'{key_terms}[Title] AND {last_name}[Author] AND {year}[PDAT]')
        
        for i, query in enumerate(queries, 1):
            try:
                # Execute search
                handle = Entrez.esearch(
                    db="pubmed",
                    term=query,
                    retmax=max_results,
                    sort="relevance"
                )
                
                result = Entrez.read(handle)
                handle.close()
                
                pmids = result.get("IdList", [])
                count = result.get("Count", 0)
                
                # Debug: print query and result count
                print(f"   Strategy {i}: Found {count} results")
                if i == 1:
                    print(f"   Query: {query[:100]}...")
                
                if pmids:
                    return pmids
                    
            except Exception as e:
                print(f"⚠️  PubMed search error (strategy {i}): {e}")
                continue
        
        return []
    
    def fetch_pubmed_metadata(self, pmid: str) -> Optional[Dict[str, Any]]:
        """
        Fetch full metadata for a PMID using efetch.
        
        Args:
            pmid: PubMed ID
        
        Returns:
            Dictionary with metadata or None if fetch fails
        """
        self._rate_limit_wait()
        
        try:
            # Fetch detailed record
            handle = Entrez.efetch(
                db="pubmed",
                id=pmid,
                rettype="medline",
                retmode="xml"
            )
            
            records = Entrez.read(handle)
            handle.close()
            
            if not records or 'PubmedArticle' not in records:
                return None
            
            article = records['PubmedArticle'][0]
            medline = article.get('MedlineCitation', {})
            article_data = medline.get('Article', {})
            
            # Extract DOI from ArticleIdList
            doi = None
            article_ids = article.get('PubmedData', {}).get('ArticleIdList', [])
            for article_id in article_ids:
                if article_id.attributes.get('IdType') == 'doi':
                    doi = str(article_id)
                    break
            
            # Extract title
            title = article_data.get('ArticleTitle', '')
            
            # Extract authors
            authors = []
            author_list = article_data.get('AuthorList', [])
            for author in author_list:
                last_name = author.get('LastName', '')
                initials = author.get('Initials', '')
                if last_name:
                    authors.append(f"{last_name} {initials}".strip())
            
            # Extract journal
            journal_info = article_data.get('Journal', {})
            journal = journal_info.get('Title', '')
            
            # Extract year
            year = None
            pub_date = article_data.get('ArticleDate')
            if pub_date and len(pub_date) > 0:
                year = int(pub_date[0].get('Year', 0))
            else:
                # Try journal issue date
                journal_issue = journal_info.get('JournalIssue', {})
                pub_date_obj = journal_issue.get('PubDate', {})
                year_str = pub_date_obj.get('Year', '')
                if year_str:
                    year = int(year_str)
            
            return {
                'pmid': pmid,
                'doi': doi,
                'title': title,
                'authors': authors,
                'journal': journal,
                'year': year
            }
            
        except Exception as e:
            print(f"⚠️  Error fetching PMID {pmid}: {e}")
            return None
    
    def calculate_similarity(
        self,
        extracted_title: str,
        pubmed_title: str
    ) -> float:
        """
        Calculate similarity between two titles using fuzzy matching.
        
        Uses token sort ratio which is robust to word order differences.
        
        Args:
            extracted_title: Title from extracted study
            pubmed_title: Title from PubMed result
        
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Normalize titles
        title1 = extracted_title.lower().strip()
        title2 = pubmed_title.lower().strip()
        
        # Calculate token sort ratio (handles word order differences)
        ratio = fuzz.token_sort_ratio(title1, title2)
        
        # Convert from 0-100 to 0.0-1.0
        return ratio / 100.0
    
    def calculate_confidence(
        self,
        similarity_score: float,
        num_results: int,
        author_match: bool
    ) -> float:
        """
        Calculate confidence score for a match.
        
        Args:
            similarity_score: Title similarity (0.0-1.0)
            num_results: Number of PubMed results found
            author_match: Whether first author matches
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence from similarity
        confidence = similarity_score
        
        # Boost for exact match with single result
        if num_results == 1 and similarity_score > 0.95:
            confidence = 0.95
        
        # Boost for strong similarity
        elif similarity_score >= 0.90:
            confidence = 0.90 if num_results <= 3 else 0.85
        
        # Medium confidence for good match
        elif similarity_score >= 0.80:
            confidence = 0.80 if num_results <= 3 else 0.70
        
        # Low confidence for weak match
        elif similarity_score >= 0.70:
            confidence = 0.60
        
        # Very low confidence
        else:
            confidence = similarity_score * 0.5
        
        # Reduce confidence if author doesn't match
        if not author_match:
            confidence *= 0.90
        
        return round(confidence, 3)
    
    def find_best_match(
        self,
        extracted_study: Dict[str, Any],
        max_results: int = 10,
        min_confidence: float = 0.70
    ) -> Optional[PubMedMatch]:
        """
        Find best PubMed match for an extracted study.
        
        Args:
            extracted_study: Study data with keys: title, first_author, year
            max_results: Maximum PubMed results to consider
            min_confidence: Minimum confidence threshold
        
        Returns:
            PubMedMatch object or None if no good match found
        """
        title = extracted_study.get('title', '')
        first_author = extracted_study.get('first_author', '')
        year = extracted_study.get('year', 2000)
        
        if not title or not first_author:
            return None
        
        # Search PubMed
        pmids = self.search_pubmed(title, first_author, year, max_results)
        
        if not pmids:
            return None
        
        # Fetch metadata for each result and calculate similarity
        candidates = []
        
        for pmid in pmids:
            metadata = self.fetch_pubmed_metadata(pmid)
            
            if not metadata:
                continue
            
            # Calculate title similarity
            pm_title = metadata.get('title', '')
            similarity = self.calculate_similarity(title, pm_title)
            
            # Check author match
            pm_authors = metadata.get('authors', [])
            extracted_last_name = self._extract_last_name(first_author).lower()
            author_match = any(
                extracted_last_name in author.lower()
                for author in pm_authors[:3]  # Check first 3 authors
            )
            
            # Calculate confidence
            confidence = self.calculate_confidence(
                similarity,
                len(pmids),
                author_match
            )
            
            if confidence >= min_confidence:
                match = PubMedMatch(
                    pmid=pmid,
                    doi=metadata.get('doi'),
                    title=pm_title,
                    authors=pm_authors,
                    journal=metadata.get('journal', ''),
                    year=metadata.get('year', 0),
                    similarity_score=similarity,
                    confidence=confidence
                )
                candidates.append(match)
        
        if not candidates:
            return None
        
        # Return best match (highest confidence)
        best_match = max(candidates, key=lambda x: x.confidence)
        return best_match
    
    def lookup_batch(
        self,
        studies: List[Dict[str, Any]],
        min_confidence: float = 0.70,
        verbose: bool = True
    ) -> List[Optional[PubMedMatch]]:
        """
        Lookup multiple studies in batch.
        
        Args:
            studies: List of study dicts with title, first_author, year
            min_confidence: Minimum confidence threshold
            verbose: Print progress
        
        Returns:
            List of PubMedMatch objects (or None for no match)
        """
        results = []
        
        for i, study in enumerate(studies, 1):
            if verbose:
                title = study.get('title', 'Unknown')[:50]
                print(f"  [{i}/{len(studies)}] Looking up: {title}...")
            
            match = self.find_best_match(study, min_confidence=min_confidence)
            results.append(match)
            
            if verbose and match:
                print(f"      → PMID: {match.pmid}, DOI: {match.doi or 'N/A'}, "
                      f"Confidence: {match.confidence:.2f} ✓")
            elif verbose:
                print(f"      → No match found")
        
        return results


# Convenience functions
def search_pubmed(
    title: str,
    first_author: str,
    year: int,
    email: str,
    api_key: Optional[str] = None,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Convenience function to search PubMed and get full metadata.
    
    Args:
        title: Study title
        first_author: First author name
        year: Publication year
        email: Your email (required by NCBI)
        api_key: Optional API key
        max_results: Maximum results
    
    Returns:
        List of study metadata dictionaries
    """
    client = PubMedLookup(email, api_key)
    
    pmids = client.search_pubmed(title, first_author, year, max_results)
    
    results = []
    for pmid in pmids:
        metadata = client.fetch_pubmed_metadata(pmid)
        if metadata:
            results.append(metadata)
    
    return results


def find_best_pmid_doi(
    title: str,
    first_author: str,
    year: int,
    email: str,
    api_key: Optional[str] = None,
    min_confidence: float = 0.70
) -> Optional[Dict[str, Any]]:
    """
    Convenience function to find best PMID and DOI for a study.
    
    Args:
        title: Study title
        first_author: First author name
        year: Publication year
        email: Your email (required by NCBI)
        api_key: Optional API key
        min_confidence: Minimum confidence threshold
    
    Returns:
        Dict with pmid, doi, confidence or None
    """
    client = PubMedLookup(email, api_key)
    
    study = {
        'title': title,
        'first_author': first_author,
        'year': year
    }
    
    match = client.find_best_match(study, min_confidence=min_confidence)
    
    if match:
        return {
            'pmid': match.pmid,
            'doi': match.doi,
            'confidence': match.confidence,
            'similarity': match.similarity_score
        }
    
    return None


if __name__ == "__main__":
    # Test with example study
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python lookup_pmid.py <your_email@domain.com>")
        print("\nExample test:")
        print('  python lookup_pmid.py your@email.com')
        sys.exit(1)
    
    email = sys.argv[1]
    
    # Test case from ai_2022
    test_study = {
        'title': 'Childhood OSA is an independent determinant of blood pressure in adulthood',
        'first_author': 'Chan KC',
        'year': 2020
    }
    
    print(f"🔍 Testing PubMed Lookup")
    print(f"   Email: {email}")
    print(f"   Study: {test_study['title'][:50]}...")
    print()
    
    client = PubMedLookup(email)
    match = client.find_best_match(test_study)
    
    if match:
        print(f"✅ Match Found:")
        print(f"   PMID: {match.pmid}")
        print(f"   DOI: {match.doi}")
        print(f"   Title: {match.title}")
        print(f"   Authors: {', '.join(match.authors[:3])}")
        print(f"   Journal: {match.journal}")
        print(f"   Year: {match.year}")
        print(f"   Similarity: {match.similarity_score:.3f}")
        print(f"   Confidence: {match.confidence:.3f}")
    else:
        print(f"❌ No match found")
