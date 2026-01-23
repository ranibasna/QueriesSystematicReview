#!/usr/bin/env python3
"""
Unit tests for PubMed lookup module.
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import pytest
from unittest.mock import Mock, patch, MagicMock
from lookup_pmid import PubMedLookup, PubMedMatch


class TestPubMedLookup:
    """Test PubMedLookup class."""
    
    def test_init_without_api_key(self):
        """Test initialization without API key."""
        client = PubMedLookup(email="test@example.com")
        
        assert client.email == "test@example.com"
        assert client.api_key is None
        assert client.rate_limit == 3.0
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        client = PubMedLookup(email="test@example.com", api_key="abc123")
        
        assert client.api_key == "abc123"
        assert client.rate_limit == 10.0
    
    def test_init_custom_rate_limit(self):
        """Test initialization with custom rate limit."""
        client = PubMedLookup(email="test@example.com", rate_limit=5.0)
        
        assert client.rate_limit == 5.0
    
    def test_clean_title(self):
        """Test title cleaning."""
        client = PubMedLookup(email="test@example.com")
        
        # Test special character removal (colon becomes space, normalized to single space)
        title = "Sleep apnea: effects on BP"
        cleaned = client._clean_title(title)
        assert cleaned == "Sleep apnea effects on BP"
        
        # Test whitespace normalization
        title = "Sleep   apnea\n\teffects"
        cleaned = client._clean_title(title)
        assert cleaned == "Sleep apnea effects"
    
    def test_normalize_title_unicode_ligatures(self):
        """Test normalization of Unicode ligatures from PDF extraction."""
        client = PubMedLookup(email="test@example.com")
        
        # Test /uniFB02 -> fl ligature
        title = "Barore /uniFB02 ex gain"
        normalized = client._normalize_title(title)
        assert "Baroreflex" in normalized
        assert "/uniFB02" not in normalized
        
        # Test uniFB01 -> fi ligature
        title = "Study on uniFB01 ndings"
        normalized = client._normalize_title(title)
        assert "fi" in normalized
        assert "uniFB01" not in normalized
    
    def test_normalize_title_compound_words(self):
        """Test normalization of compound words missing hyphens."""
        client = PubMedLookup(email="test@example.com")
        
        # Test "Twenty-fourhour" -> "Twenty-four-hour"
        title = "Twenty-fourhour ambulatory blood pressure"
        normalized = client._normalize_title(title)
        assert "Twenty-four-hour" in normalized or "twenty-four-hour" in normalized.lower()
        
        # Test number + hour pattern
        title = "24hour monitoring study"
        normalized = client._normalize_title(title)
        assert "24-hour" in normalized
    
    def test_extract_last_name(self):
        """Test last name extraction."""
        client = PubMedLookup(email="test@example.com")
        
        # Format: "Smith J"
        assert client._extract_last_name("Smith J") == "Smith"
        
        # Format: "Smith"
        assert client._extract_last_name("Smith") == "Smith"
        
        # Format: "von Smith J"
        assert client._extract_last_name("von Smith J") == "Smith"
        
        # Format: "Smith JA"
        assert client._extract_last_name("Smith JA") == "Smith"
    
    def test_calculate_similarity_exact_match(self):
        """Test similarity calculation for exact match."""
        client = PubMedLookup(email="test@example.com")
        
        title1 = "Sleep apnea and blood pressure"
        title2 = "Sleep apnea and blood pressure"
        
        similarity = client.calculate_similarity(title1, title2)
        assert similarity == 1.0
    
    def test_calculate_similarity_case_insensitive(self):
        """Test similarity calculation is case insensitive."""
        client = PubMedLookup(email="test@example.com")
        
        title1 = "Sleep Apnea and Blood Pressure"
        title2 = "sleep apnea and blood pressure"
        
        similarity = client.calculate_similarity(title1, title2)
        assert similarity == 1.0
    
    def test_calculate_similarity_word_order(self):
        """Test similarity with different word order."""
        client = PubMedLookup(email="test@example.com")
        
        title1 = "Blood pressure and sleep apnea"
        title2 = "Sleep apnea and blood pressure"
        
        similarity = client.calculate_similarity(title1, title2)
        # Token sort ratio handles word order differences
        assert similarity >= 0.9
    
    def test_calculate_similarity_partial_match(self):
        """Test similarity for partial match."""
        client = PubMedLookup(email="test@example.com")
        
        title1 = "Sleep apnea effects on blood pressure"
        title2 = "Sleep apnea and cardiovascular outcomes"
        
        similarity = client.calculate_similarity(title1, title2)
        assert 0.4 < similarity < 0.7
    
    def test_calculate_confidence_exact_match_single_result(self):
        """Test confidence for exact match with single result."""
        client = PubMedLookup(email="test@example.com")
        
        confidence = client.calculate_confidence(
            similarity_score=0.98,
            num_results=1,
            author_match=True
        )
        
        assert confidence == 0.95
    
    def test_calculate_confidence_strong_match(self):
        """Test confidence for strong similarity."""
        client = PubMedLookup(email="test@example.com")
        
        confidence = client.calculate_confidence(
            similarity_score=0.92,
            num_results=2,
            author_match=True
        )
        
        assert confidence == 0.90
    
    def test_calculate_confidence_weak_match(self):
        """Test confidence for weak similarity."""
        client = PubMedLookup(email="test@example.com")
        
        confidence = client.calculate_confidence(
            similarity_score=0.75,
            num_results=5,
            author_match=True
        )
        
        # Confidence is 0.60 for similarity 0.75 (not high enough for 0.70 threshold)
        assert confidence == 0.60
    
    def test_calculate_confidence_no_author_match(self):
        """Test confidence reduction when author doesn't match."""
        client = PubMedLookup(email="test@example.com")
        
        # With author match
        conf_with_author = client.calculate_confidence(
            similarity_score=0.90,
            num_results=1,
            author_match=True
        )
        
        # Without author match
        conf_without_author = client.calculate_confidence(
            similarity_score=0.90,
            num_results=1,
            author_match=False
        )
        
        assert conf_without_author < conf_with_author
        assert conf_without_author == conf_with_author * 0.90


class TestPubMedMatch:
    """Test PubMedMatch dataclass."""
    
    def test_pubmed_match_creation(self):
        """Test creating a PubMedMatch object."""
        match = PubMedMatch(
            pmid="12345678",
            doi="10.1234/test",
            title="Test Study",
            authors=["Smith J", "Jones A"],
            journal="Test Journal",
            year=2020,
            similarity_score=0.95,
            confidence=0.90
        )
        
        assert match.pmid == "12345678"
        assert match.doi == "10.1234/test"
        assert match.confidence == 0.90
    
    def test_pubmed_match_to_dict(self):
        """Test converting PubMedMatch to dictionary."""
        match = PubMedMatch(
            pmid="12345678",
            doi="10.1234/test",
            title="Test Study",
            authors=["Smith J"],
            journal="Test Journal",
            year=2020,
            similarity_score=0.95,
            confidence=0.90
        )
        
        data = match.to_dict()
        
        assert isinstance(data, dict)
        assert data['pmid'] == "12345678"
        assert data['doi'] == "10.1234/test"
        assert data['confidence'] == 0.90


class TestPubMedIntegration:
    """Integration tests for PubMed lookup (require network access)."""
    
    @pytest.mark.integration
    def test_search_pubmed_real(self):
        """Test real PubMed search."""
        client = PubMedLookup(email="test@example.com")
        
        # Well-known study
        pmids = client.search_pubmed(
            title="Childhood OSA independent determinant blood pressure",
            first_author="Chan KC",
            year=2020,
            max_results=5
        )
        
        # Should find at least one result
        assert len(pmids) >= 1
        assert all(isinstance(pmid, str) for pmid in pmids)
    
    @pytest.mark.integration
    def test_fetch_pubmed_metadata_real(self):
        """Test real PubMed metadata fetch."""
        client = PubMedLookup(email="test@example.com")
        
        # Known PMID
        metadata = client.fetch_pubmed_metadata("32209641")
        
        assert metadata is not None
        assert metadata['pmid'] == "32209641"
        assert 'doi' in metadata
        assert 'title' in metadata
        assert 'authors' in metadata
        assert len(metadata['authors']) > 0
    
    @pytest.mark.integration
    def test_find_best_match_real(self):
        """Test finding best match for real study."""
        client = PubMedLookup(email="test@example.com")
        
        study = {
            'title': 'Childhood OSA is an independent determinant of blood pressure in adulthood',
            'first_author': 'Chan KC',
            'year': 2020
        }
        
        match = client.find_best_match(study, min_confidence=0.70)
        
        assert match is not None
        assert match.pmid == "32209641"
        assert match.doi == "10.1136/thoraxjnl-2019-213692"
        assert match.confidence >= 0.90
        assert match.similarity_score >= 0.95


if __name__ == "__main__":
    # Run tests
    import sys
    
    # Run unit tests only (no integration tests)
    sys.exit(pytest.main([__file__, "-v", "-m", "not integration"]))
