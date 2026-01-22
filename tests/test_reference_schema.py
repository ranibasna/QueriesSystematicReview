"""
Unit tests for Reference and ReferenceList data models.

Tests cover:
- Valid reference creation
- Invalid data rejection
- JSON serialization/deserialization
- Helper methods
- Edge cases
"""

import sys
from pathlib import Path

# Add parent directory to path to import models
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import json
from datetime import datetime
from models import Reference, ReferenceList


class TestReference:
    """Test cases for Reference dataclass."""
    
    def test_valid_reference_creation(self):
        """Test creating a valid reference."""
        ref = Reference(
            reference_id=1,
            title="Test Article",
            authors=["Smith J", "Jones M"],
            journal="Test Journal",
            year=2020,
            volume="10",
            issue="2",
            pages="100-110",
            doi="10.1234/test.2020.001",
            pmid="12345678",
            raw_citation="Smith J, Jones M. Test Article. Test Journal. 2020;10(2):100-110.",
            confidence=0.95
        )
        
        assert ref.reference_id == 1
        assert ref.title == "Test Article"
        assert len(ref.authors) == 2
        assert ref.year == 2020
        assert ref.confidence == 0.95
    
    def test_minimal_valid_reference(self):
        """Test creating reference with only required fields."""
        ref = Reference(
            reference_id=1,
            title="Minimal Article",
            authors=["Author A"],
            journal="Journal X",
            year=2015
        )
        
        assert ref.reference_id == 1
        assert ref.volume is None
        assert ref.doi is None
        assert ref.confidence == 1.0  # Default value
    
    def test_invalid_year_too_early(self):
        """Test that year < 1900 raises ValueError."""
        with pytest.raises(ValueError, match="Year .* must be between 1900 and 2026"):
            Reference(
                reference_id=1,
                title="Old Article",
                authors=["Smith J"],
                journal="Journal",
                year=1899
            )
    
    def test_invalid_year_too_late(self):
        """Test that year > 2026 raises ValueError."""
        with pytest.raises(ValueError, match="Year .* must be between 1900 and 2026"):
            Reference(
                reference_id=1,
                title="Future Article",
                authors=["Smith J"],
                journal="Journal",
                year=2027
            )
    
    def test_invalid_confidence_negative(self):
        """Test that confidence < 0 raises ValueError."""
        with pytest.raises(ValueError, match="Confidence .* must be between 0.0 and 1.0"):
            Reference(
                reference_id=1,
                title="Article",
                authors=["Smith J"],
                journal="Journal",
                year=2020,
                confidence=-0.1
            )
    
    def test_invalid_confidence_too_high(self):
        """Test that confidence > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="Confidence .* must be between 0.0 and 1.0"):
            Reference(
                reference_id=1,
                title="Article",
                authors=["Smith J"],
                journal="Journal",
                year=2020,
                confidence=1.5
            )
    
    def test_invalid_reference_id(self):
        """Test that reference_id < 1 raises ValueError."""
        with pytest.raises(ValueError, match="Reference ID .* must be >= 1"):
            Reference(
                reference_id=0,
                title="Article",
                authors=["Smith J"],
                journal="Journal",
                year=2020
            )
    
    def test_empty_title(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Reference(
                reference_id=1,
                title="",
                authors=["Smith J"],
                journal="Journal",
                year=2020
            )
    
    def test_empty_authors_list(self):
        """Test that empty authors list raises ValueError."""
        with pytest.raises(ValueError, match="Authors list cannot be empty"):
            Reference(
                reference_id=1,
                title="Article",
                authors=[],
                journal="Journal",
                year=2020
            )
    
    def test_whitespace_cleaning(self):
        """Test that whitespace is properly cleaned."""
        ref = Reference(
            reference_id=1,
            title="  Title with spaces  ",
            authors=["  Smith J  ", "  Jones M  "],
            journal="  Journal Name  ",
            year=2020
        )
        
        assert ref.title == "Title with spaces"
        assert ref.journal == "Journal Name"
        assert ref.authors == ["Smith J", "Jones M"]
    
    def test_doi_normalization(self):
        """Test that DOI URLs are normalized."""
        ref = Reference(
            reference_id=1,
            title="Article",
            authors=["Smith J"],
            journal="Journal",
            year=2020,
            doi="https://doi.org/10.1234/test"
        )
        
        assert ref.doi == "10.1234/test"
    
    def test_pmid_normalization(self):
        """Test that PMID is normalized to digits only."""
        ref = Reference(
            reference_id=1,
            title="Article",
            authors=["Smith J"],
            journal="Journal",
            year=2020,
            pmid="PMID: 12345678"
        )
        
        assert ref.pmid == "12345678"
    
    def test_to_dict(self):
        """Test converting reference to dictionary."""
        ref = Reference(
            reference_id=1,
            title="Test",
            authors=["Smith J"],
            journal="Journal",
            year=2020
        )
        
        data = ref.to_dict()
        assert isinstance(data, dict)
        assert data['reference_id'] == 1
        assert data['title'] == "Test"
    
    def test_to_json(self):
        """Test converting reference to JSON string."""
        ref = Reference(
            reference_id=1,
            title="Test",
            authors=["Smith J"],
            journal="Journal",
            year=2020
        )
        
        json_str = ref.to_json()
        assert isinstance(json_str, str)
        
        # Verify it's valid JSON
        data = json.loads(json_str)
        assert data['reference_id'] == 1
    
    def test_from_dict(self):
        """Test creating reference from dictionary."""
        data = {
            'reference_id': 1,
            'title': "Test Article",
            'authors': ["Smith J"],
            'journal': "Journal",
            'year': 2020
        }
        
        ref = Reference.from_dict(data)
        assert ref.reference_id == 1
        assert ref.title == "Test Article"
    
    def test_from_json(self):
        """Test creating reference from JSON string."""
        json_str = json.dumps({
            'reference_id': 1,
            'title': "Test Article",
            'authors': ["Smith J"],
            'journal': "Journal",
            'year': 2020
        })
        
        ref = Reference.from_json(json_str)
        assert ref.reference_id == 1
        assert ref.title == "Test Article"
    
    def test_json_roundtrip(self):
        """Test that JSON serialization/deserialization is lossless."""
        ref1 = Reference(
            reference_id=1,
            title="Test",
            authors=["Smith J", "Jones M"],
            journal="Journal",
            year=2020,
            doi="10.1234/test",
            confidence=0.92
        )
        
        # Convert to JSON and back
        json_str = ref1.to_json()
        ref2 = Reference.from_json(json_str)
        
        # Compare (excluding timestamp which will differ)
        assert ref1.reference_id == ref2.reference_id
        assert ref1.title == ref2.title
        assert ref1.authors == ref2.authors
        assert ref1.doi == ref2.doi
        assert ref1.confidence == ref2.confidence
    
    def test_has_identifiers(self):
        """Test has_identifiers method."""
        ref_with_doi = Reference(
            reference_id=1, title="Test", authors=["A"], journal="J", year=2020,
            doi="10.1234/test"
        )
        ref_with_pmid = Reference(
            reference_id=2, title="Test", authors=["A"], journal="J", year=2020,
            pmid="12345678"
        )
        ref_with_both = Reference(
            reference_id=3, title="Test", authors=["A"], journal="J", year=2020,
            doi="10.1234/test", pmid="12345678"
        )
        ref_without = Reference(
            reference_id=4, title="Test", authors=["A"], journal="J", year=2020
        )
        
        assert ref_with_doi.has_identifiers() is True
        assert ref_with_pmid.has_identifiers() is True
        assert ref_with_both.has_identifiers() is True
        assert ref_without.has_identifiers() is False
    
    def test_get_primary_identifier(self):
        """Test get_primary_identifier method (prefers DOI)."""
        ref_with_doi = Reference(
            reference_id=1, title="Test", authors=["A"], journal="J", year=2020,
            doi="10.1234/test"
        )
        ref_with_pmid = Reference(
            reference_id=2, title="Test", authors=["A"], journal="J", year=2020,
            pmid="12345678"
        )
        ref_with_both = Reference(
            reference_id=3, title="Test", authors=["A"], journal="J", year=2020,
            doi="10.1234/test", pmid="12345678"
        )
        ref_without = Reference(
            reference_id=4, title="Test", authors=["A"], journal="J", year=2020
        )
        
        assert ref_with_doi.get_primary_identifier() == "10.1234/test"
        assert ref_with_pmid.get_primary_identifier() == "12345678"
        assert ref_with_both.get_primary_identifier() == "10.1234/test"  # Prefers DOI
        assert ref_without.get_primary_identifier() is None
    
    def test_is_biomedical(self):
        """Test is_biomedical heuristic."""
        biomedical_ref = Reference(
            reference_id=1, title="Test", authors=["A"],
            journal="Journal of Clinical Medicine", year=2020
        )
        non_biomedical_ref = Reference(
            reference_id=2, title="Test", authors=["A"],
            journal="Physics Letters", year=2020
        )
        
        assert biomedical_ref.is_biomedical() is True
        assert non_biomedical_ref.is_biomedical() is False


class TestReferenceList:
    """Test cases for ReferenceList container."""
    
    def test_reference_list_creation(self):
        """Test creating a ReferenceList."""
        refs = [
            Reference(1, "Title 1", ["Author A"], "Journal X", 2020),
            Reference(2, "Title 2", ["Author B"], "Journal Y", 2021)
        ]
        
        ref_list = ReferenceList(
            study_name="test_study",
            references=refs,
            source_file="test.md"
        )
        
        assert ref_list.study_name == "test_study"
        assert len(ref_list.references) == 2
        assert ref_list.total_count == 2
    
    def test_to_dict(self):
        """Test converting ReferenceList to dictionary."""
        refs = [
            Reference(1, "Title 1", ["Author A"], "Journal X", 2020)
        ]
        ref_list = ReferenceList(study_name="test", references=refs)
        
        data = ref_list.to_dict()
        assert isinstance(data, dict)
        assert data['study_name'] == "test"
        assert len(data['references']) == 1
    
    def test_to_json(self):
        """Test converting ReferenceList to JSON."""
        refs = [
            Reference(1, "Title 1", ["Author A"], "Journal X", 2020)
        ]
        ref_list = ReferenceList(study_name="test", references=refs)
        
        json_str = ref_list.to_json()
        data = json.loads(json_str)
        assert data['study_name'] == "test"
    
    def test_from_dict(self):
        """Test creating ReferenceList from dictionary."""
        data = {
            'study_name': 'test_study',
            'references': [
                {
                    'reference_id': 1,
                    'title': 'Test',
                    'authors': ['Author A'],
                    'journal': 'Journal',
                    'year': 2020
                }
            ]
        }
        
        ref_list = ReferenceList.from_dict(data)
        assert ref_list.study_name == 'test_study'
        assert len(ref_list.references) == 1
    
    def test_get_statistics(self):
        """Test getting statistics about references."""
        refs = [
            Reference(1, "Title 1", ["A"], "Journal", 2020, doi="10.1234/test1"),
            Reference(2, "Title 2", ["B"], "Journal", 2021, pmid="12345678"),
            Reference(3, "Title 3", ["C"], "Journal", 2019),  # No identifiers
            Reference(4, "Title 4", ["D"], "Journal of Medicine", 2022, doi="10.1234/test2", pmid="87654321")
        ]
        ref_list = ReferenceList(study_name="test", references=refs)
        
        stats = ref_list.get_statistics()
        assert stats['total_references'] == 4
        assert stats['with_doi'] == 2
        assert stats['with_pmid'] == 2
        assert stats['with_identifiers'] == 3  # 3 have at least one identifier
        assert stats['without_identifiers'] == 1
        assert stats['year_range'] == (2019, 2022)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
