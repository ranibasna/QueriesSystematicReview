"""
Data models for DOI/PMID extraction automation.

This module defines the data structures used for representing bibliographic
references extracted from systematic review papers.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


@dataclass
class Reference:
    """
    Represents a bibliographic reference extracted from a systematic review paper.
    
    Attributes:
        reference_id: Unique identifier for the reference (1-indexed)
        title: Article title
        authors: List of author names (e.g., ["Smith J", "Jones M"])
        journal: Journal name
        year: Publication year (1900-2026)
        volume: Journal volume (optional)
        issue: Journal issue (optional)
        pages: Page range (e.g., "123-145") (optional)
        doi: Digital Object Identifier (optional)
        pmid: PubMed ID (optional)
        raw_citation: Original citation text for debugging
        confidence: Extraction confidence score (0.0-1.0)
        extraction_timestamp: When the reference was extracted
        metadata: Additional metadata (e.g., abstract, keywords)
    """
    reference_id: int
    title: str
    authors: List[str]
    journal: str
    year: int
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    pmid: Optional[str] = None
    raw_citation: str = ""
    confidence: float = 1.0
    extraction_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate reference data after initialization."""
        # Validate year
        if not (1900 <= self.year <= 2026):
            raise ValueError(f"Year {self.year} must be between 1900 and 2026")
        
        # Validate confidence score
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence {self.confidence} must be between 0.0 and 1.0")
        
        # Validate reference_id
        if self.reference_id < 1:
            raise ValueError(f"Reference ID {self.reference_id} must be >= 1")
        
        # Validate title is not empty
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        
        # Validate authors list is not empty
        if not self.authors or len(self.authors) == 0:
            raise ValueError("Authors list cannot be empty")
        
        # Clean and normalize data
        self.title = self.title.strip()
        self.journal = self.journal.strip()
        self.authors = [author.strip() for author in self.authors if author.strip()]
        
        # Normalize DOI (remove URL prefix if present)
        if self.doi:
            self.doi = self.doi.replace("https://doi.org/", "").replace("http://dx.doi.org/", "").strip()
        
        # Normalize PMID (ensure it's just digits)
        if self.pmid:
            self.pmid = ''.join(filter(str.isdigit, self.pmid))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert reference to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert reference to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reference':
        """Create Reference from dictionary."""
        # Remove any extra fields not in dataclass
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Reference':
        """Create Reference from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def has_identifiers(self) -> bool:
        """Check if reference has DOI or PMID."""
        return bool(self.doi or self.pmid)
    
    def get_primary_identifier(self) -> Optional[str]:
        """Get primary identifier (prefer DOI over PMID)."""
        return self.doi if self.doi else self.pmid
    
    def is_biomedical(self) -> bool:
        """
        Heuristic check if reference is likely biomedical.
        Used for deciding which API to query first.
        """
        biomedical_journals = [
            'plos', 'bmc', 'jama', 'nejm', 'lancet', 'nature', 'science',
            'cell', 'neurology', 'medicine', 'health', 'clinical', 'medical',
            'journal of', 'american journal', 'british journal', 'european journal'
        ]
        journal_lower = self.journal.lower()
        return any(keyword in journal_lower for keyword in biomedical_journals)


@dataclass
class ReferenceList:
    """
    Container for a list of references from a systematic review.
    
    Attributes:
        study_name: Name of the study (e.g., "Godos_2024")
        references: List of Reference objects
        extraction_date: When the references were extracted
        source_file: Path to the source markdown file
        total_count: Total number of references
        metadata: Additional metadata about the extraction
    """
    study_name: str
    references: List[Reference]
    extraction_date: str = field(default_factory=lambda: datetime.now().isoformat())
    source_file: Optional[str] = None
    total_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Update total count after initialization."""
        self.total_count = len(self.references)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'study_name': self.study_name,
            'references': [ref.to_dict() for ref in self.references],
            'extraction_date': self.extraction_date,
            'source_file': self.source_file,
            'total_count': self.total_count,
            'metadata': self.metadata
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReferenceList':
        """Create ReferenceList from dictionary."""
        references = [Reference.from_dict(ref) for ref in data.get('references', [])]
        return cls(
            study_name=data['study_name'],
            references=references,
            extraction_date=data.get('extraction_date', datetime.now().isoformat()),
            source_file=data.get('source_file'),
            total_count=data.get('total_count', len(references)),
            metadata=data.get('metadata', {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ReferenceList':
        """Create ReferenceList from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save_to_file(self, filepath: str) -> None:
        """Save reference list to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'ReferenceList':
        """Load reference list from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            json_str = f.read()
        return cls.from_json(json_str)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the references."""
        return {
            'total_references': self.total_count,
            'with_doi': sum(1 for ref in self.references if ref.doi),
            'with_pmid': sum(1 for ref in self.references if ref.pmid),
            'with_identifiers': sum(1 for ref in self.references if ref.has_identifiers()),
            'without_identifiers': sum(1 for ref in self.references if not ref.has_identifiers()),
            'biomedical_likely': sum(1 for ref in self.references if ref.is_biomedical()),
            'average_confidence': sum(ref.confidence for ref in self.references) / len(self.references) if self.references else 0,
            'year_range': (
                min(ref.year for ref in self.references),
                max(ref.year for ref in self.references)
            ) if self.references else (None, None)
        }


# Example usage and validation
if __name__ == "__main__":
    # Example reference
    ref = Reference(
        reference_id=1,
        title="Mediterranean diet and cognitive function in older adults",
        authors=["Smith J", "Johnson M", "Williams K"],
        journal="American Journal of Clinical Nutrition",
        year=2020,
        volume="112",
        issue="3",
        pages="580-589",
        doi="10.1093/ajcn/nqaa123",
        pmid="32648899",
        raw_citation="Smith J, et al. Mediterranean diet and cognitive function. Am J Clin Nutr. 2020;112(3):580-589.",
        confidence=0.95
    )
    
    print("Reference created successfully:")
    print(ref.to_json())
    print(f"\nHas identifiers: {ref.has_identifiers()}")
    print(f"Primary identifier: {ref.get_primary_identifier()}")
    print(f"Is biomedical: {ref.is_biomedical()}")
