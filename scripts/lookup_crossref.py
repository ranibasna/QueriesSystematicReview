#!/usr/bin/env python3
"""
CrossRef API lookup for DOI extraction.

CrossRef is the official DOI registration agency and provides a REST API
for searching and retrieving DOI metadata. This is particularly useful as
a fallback when PubMed fails, since:
- CrossRef has more lenient title matching
- CrossRef is DOI-focused (not limited to biomedical)
- CrossRef doesn't require exact title matches

Rate limits: 50 req/sec with polite pool (recommended)
API docs: https://api.crossref.org/swagger-ui/index.html
"""

import time
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import requests
from urllib.parse import quote

try:
    from rapidfuzz import fuzz
except ImportError:
    raise ImportError("rapidfuzz not installed. Run: pip install rapidfuzz")


@dataclass
class CrossRefMatch:
    """Represents a CrossRef search result match."""
    doi: str
    title: str
    authors: List[str]
    journal: str
    year: int
    work_type: Optional[str]
    similarity_score: float
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class CrossRefLookup:
    """
    CrossRef API client for DOI lookup with fuzzy title matching.
    """
    
    def __init__(
        self,
        email: Optional[str] = None,
        rate_limit: float = 20.0  # Conservative: 20 req/sec
    ):
        """
        Initialize CrossRef lookup client.
        
        Args:
            email: Your email (for polite pool access, increases rate limit)
            rate_limit: Requests per second (default: 20, max: 50 with email)
        """
        self.email = email
        self.rate_limit = rate_limit
        self.min_delay = 1.0 / rate_limit
        self.last_request_time = 0
        
        # Base URL for CrossRef API
        self.base_url = "https://api.crossref.org/works"
        
        # Setup headers
        self.headers = {
            'User-Agent': f'DOI-PMID-Extractor/1.0 (mailto:{email})' if email else 'DOI-PMID-Extractor/1.0'
        }
    
    def _rate_limit_wait(self):
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _extract_last_name(self, author: str) -> str:
        """
        Extract last name from author string.
        
        Handles formats like:
        - "Smith J"
        - "Smith"
        """
        parts = author.strip().split()
        if not parts:
            return author
        
        # If last part is single letter (initial), take second-to-last
        if len(parts[-1]) == 1:
            return parts[-2] if len(parts) > 1 else parts[0]
        
        # Otherwise, first part is last name
        return parts[0]
    
    def search_by_title(
        self,
        title: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search CrossRef by title.
        
        Args:
            title: Article title
            max_results: Maximum number of results
        
        Returns:
            List of CrossRef work items
        """
        self._rate_limit_wait()
        
        # Build query
        params = {
            'query.title': title,
            'rows': max_results,
            'sort': 'relevance'
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            items = data.get('message', {}).get('items', [])
            
            return items
            
        except requests.RequestException as e:
            print(f"⚠️  CrossRef search error: {e}")
            return []

    def search_title_variations(
        self,
        title: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Try multiple title variants to improve recall."""
        # Full title
        items = self.search_by_title(title, max_results)
        if items:
            return items

        # Truncate to first 12 words to dampen noisy tails
        truncated = ' '.join(title.split()[:12])
        if truncated and truncated != title:
            items = self.search_by_title(truncated, max_results)
            if items:
                return items

        # Remove punctuation and retry
        cleaned = re.sub(r'[^\w\s-]', ' ', title)
        cleaned = ' '.join(cleaned.split())
        if cleaned and cleaned != title:
            items = self.search_by_title(cleaned, max_results)

        return items
    
    def search_by_bibliographic(
        self,
        title: str,
        author: Optional[str] = None,
        year: Optional[int] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search CrossRef using bibliographic query (more accurate).
        
        Args:
            title: Article title
            author: First author (optional)
            year: Publication year (optional)
            max_results: Maximum results
        
        Returns:
            List of CrossRef work items
        """
        self._rate_limit_wait()
        
        # Build bibliographic string
        # Format: "Author Title year"
        bib_parts = []
        
        if author:
            last_name = self._extract_last_name(author)
            bib_parts.append(last_name)
        
        bib_parts.append(title)
        
        if year:
            bib_parts.append(str(year))
        
        query = ' '.join(bib_parts)
        
        params = {
            'query.bibliographic': query,
            'rows': max_results,
            'sort': 'relevance'
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            items = data.get('message', {}).get('items', [])
            
            return items
            
        except requests.RequestException as e:
            print(f"⚠️  CrossRef bibliographic search error: {e}")
            return []
    
    def parse_crossref_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse CrossRef work item into standardized format.
        
        Args:
            item: CrossRef work item
        
        Returns:
            Standardized metadata dict or None
        """
        try:
            # Extract DOI
            doi = item.get('DOI')
            if not doi:
                return None
            
            # Extract title
            titles = item.get('title', [])
            title = titles[0] if titles else ''
            
            # Extract authors
            authors = []
            author_list = item.get('author', [])
            for author in author_list:
                family = author.get('family', '')
                given = author.get('given', '')
                if family:
                    authors.append(f"{family} {given}".strip())
            
            # Extract journal
            container_titles = item.get('container-title', [])
            journal = container_titles[0] if container_titles else ''
            
            # Extract year
            year = None
            published = item.get('published-print') or item.get('published-online')
            if published:
                date_parts = published.get('date-parts', [[]])
                if date_parts and date_parts[0]:
                    year = date_parts[0][0]

            work_type = item.get('type')
            
            return {
                'doi': doi,
                'title': title,
                'authors': authors,
                'journal': journal,
                'year': year,
                'type': work_type
            }
            
        except Exception as e:
            print(f"⚠️  Error parsing CrossRef item: {e}")
            return None
    
    def calculate_similarity(
        self,
        extracted_title: str,
        crossref_title: str
    ) -> float:
        """
        Calculate similarity between two titles using fuzzy matching.
        
        Args:
            extracted_title: Title from extracted study
            crossref_title: Title from CrossRef result
        
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Normalize titles
        title1 = extracted_title.lower().strip()
        title2 = crossref_title.lower().strip()
        
        # Calculate token sort ratio (handles word order differences)
        ratio = fuzz.token_sort_ratio(title1, title2)
        
        # Convert from 0-100 to 0.0-1.0
        return ratio / 100.0
    
    def calculate_confidence(
        self,
        similarity_score: float,
        num_results: int,
        author_match: bool,
        year_match: bool,
        type_penalty: float = 1.0
    ) -> float:
        """
        Calculate confidence score for a match.
        
        Args:
            similarity_score: Title similarity (0.0-1.0)
            num_results: Number of CrossRef results found
            author_match: Whether first author matches
            year_match: Whether year matches
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence from similarity
        confidence = similarity_score
        
        # Boost for excellent match
        if similarity_score >= 0.95 and author_match and year_match:
            confidence = 0.95
        
        # Strong match
        elif similarity_score >= 0.90:
            confidence = 0.90 if (author_match and year_match) else 0.85
        
        # Good match
        elif similarity_score >= 0.80:
            confidence = 0.80 if author_match else 0.70
        
        # Weak match
        elif similarity_score >= 0.70:
            confidence = 0.60
        
        # Very weak
        else:
            confidence = similarity_score * 0.5
        
        # Reduce if many results (ambiguous)
        if num_results > 5:
            confidence *= 0.95

        # Apply type-based penalty
        confidence *= type_penalty
        
        return round(confidence, 3)

    def _type_penalty(self, work_type: Optional[str]) -> float:
        """Apply a light penalty for non-article types."""
        if not work_type:
            return 1.0
        # Lower confidence for preprints or posted content
        if work_type in {"posted-content", "preprint"}:
            return 0.85
        # Light penalty for proceedings
        if work_type in {"proceedings-article", "book-chapter"}:
            return 0.95
        return 1.0

    def _validate_metadata(
        self,
        extracted_study: Dict[str, Any],
        metadata: Dict[str, Any],
        max_year_diff: int,
        allowed_types: Optional[List[str]]
    ) -> bool:
        """Validate CrossRef metadata against extracted study fields."""
        extracted_year = extracted_study.get('year')
        candidate_year = metadata.get('year')

        if extracted_year and candidate_year:
            if abs(candidate_year - extracted_year) > max_year_diff:
                return False

        # Author last-name match required when available
        extracted_last = self._extract_last_name(extracted_study.get('first_author', '')).lower()
        authors = metadata.get('authors', [])
        if extracted_last:
            if not any(extracted_last in a.lower() for a in authors[:5]):
                return False

        # Type validation if provided
        if allowed_types:
            candidate_type = metadata.get('type')
            if candidate_type and candidate_type not in allowed_types:
                return False

        return True
    
    def find_best_match(
        self,
        extracted_study: Dict[str, Any],
        max_results: int = 10,
        min_confidence: float = 0.80,
        max_year_diff: int = 1,
        allowed_types: Optional[List[str]] = None
    ) -> Optional[CrossRefMatch]:
        """
        Find best CrossRef match for an extracted study.
        
        Args:
            extracted_study: Study data with keys: title, first_author, year
            max_results: Maximum CrossRef results to consider
            min_confidence: Minimum confidence threshold
        
        Returns:
            CrossRefMatch object or None if no good match found
        """
        title = extracted_study.get('title', '')
        first_author = extracted_study.get('first_author', '')
        year = extracted_study.get('year')
        
        if not title:
            return None

        if allowed_types is None:
            allowed_types = [
                "journal-article",
                "article",
                "review-article",
                "proceedings-article"
            ]
        
        # Try multiple strategies to improve recall
        search_strategies = [
            lambda: self.search_by_bibliographic(title, first_author, year, max_results),
            lambda: self.search_title_variations(title, max_results),
        ]

        items: List[Dict[str, Any]] = []
        for search_fn in search_strategies:
            items = search_fn()
            if items:
                break
        
        if not items:
            return None
        
        # Parse and score each result
        candidates = []
        
        for item in items:
            metadata = self.parse_crossref_item(item)
            
            if not metadata:
                continue

            if not self._validate_metadata(extracted_study, metadata, max_year_diff, allowed_types):
                continue
            
            # Calculate title similarity
            cr_title = metadata.get('title', '')
            similarity = self.calculate_similarity(title, cr_title)
            
            # Check author match
            cr_authors = metadata.get('authors', [])
            extracted_last_name = self._extract_last_name(first_author).lower()
            author_match = any(
                extracted_last_name in author.lower()
                for author in cr_authors[:3]  # Check first 3 authors
            )
            
            # Check year match
            cr_year = metadata.get('year')
            year_match = (year == cr_year) if year and cr_year else False
            
            # Calculate confidence
            confidence = self.calculate_confidence(
                similarity,
                len(items),
                author_match,
                year_match,
                type_penalty=self._type_penalty(metadata.get('type'))
            )
            
            if confidence >= min_confidence:
                match = CrossRefMatch(
                    doi=metadata['doi'],
                    title=cr_title,
                    authors=cr_authors,
                    journal=metadata.get('journal', ''),
                    year=cr_year or 0,
                    work_type=metadata.get('type'),
                    similarity_score=similarity,
                    confidence=confidence
                )
                candidates.append(match)
        
        if not candidates:
            return None
        
        # Return best match (highest confidence)
        best_match = max(candidates, key=lambda x: x.confidence)
        return best_match


# Convenience function
def find_doi(
    title: str,
    first_author: str,
    year: int,
    email: Optional[str] = None,
    min_confidence: float = 0.80
) -> Optional[Dict[str, Any]]:
    """
    Convenience function to find DOI for a study.
    
    Args:
        title: Study title
        first_author: First author name
        year: Publication year
        email: Your email (optional, for polite pool)
        min_confidence: Minimum confidence threshold
    
    Returns:
        Dict with doi, confidence, similarity or None
    """
    client = CrossRefLookup(email)
    
    study = {
        'title': title,
        'first_author': first_author,
        'year': year
    }
    
    match = client.find_best_match(study, min_confidence=min_confidence)
    
    if match:
        return {
            'doi': match.doi,
            'confidence': match.confidence,
            'similarity': match.similarity_score
        }
    
    return None


if __name__ == "__main__":
    # Test with example study
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python lookup_crossref.py <your_email@domain.com>")
        print("\nExample test:")
        print('  python lookup_crossref.py your@email.com')
        sys.exit(1)
    
    email = sys.argv[1]
    
    # Test case - one of the failed PubMed studies
    test_study = {
        'title': 'Twenty-four-hour ambulatory blood pressure in children with sleep-disordered breathing',
        'first_author': 'Amin RS',
        'year': 2004
    }
    
    print(f"🔍 Testing CrossRef Lookup")
    print(f"   Email: {email}")
    print(f"   Study: {test_study['title'][:50]}...")
    print()
    
    client = CrossRefLookup(email)
    match = client.find_best_match(test_study)
    
    if match:
        print(f"✅ Match Found:")
        print(f"   DOI: {match.doi}")
        print(f"   Title: {match.title}")
        print(f"   Authors: {', '.join(match.authors[:3])}")
        print(f"   Journal: {match.journal}")
        print(f"   Year: {match.year}")
        print(f"   Similarity: {match.similarity_score:.3f}")
        print(f"   Confidence: {match.confidence:.3f}")
    else:
        print(f"❌ No match found")
