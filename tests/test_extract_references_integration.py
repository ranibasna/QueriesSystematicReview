"""
Integration test for extract_references.py (without API calls)

This test validates the extraction pipeline end-to-end using
mock LLM responses instead of real API calls.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.extract_references import extract_references


class TestExtractionPipelineMocked(unittest.TestCase):
    """Test full extraction pipeline with mocked API calls."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test markdown file with references section
        self.test_study = "test_study"
        self.test_md_content = """
# Test Systematic Review Paper

## Introduction
This is a test paper for validating reference extraction.

## References

1. Smith J, Johnson M. The effects of Mediterranean diet on cognitive function. American Journal of Clinical Nutrition. 2020;112(3):456-465. doi:10.1093/ajcn/nqaa123. PMID: 32648899.

2. Williams K, Brown P, Davis R. Systematic review methodology best practices. Journal of Medical Research. 2019;45(2):123-134. doi:10.1234/jmr.2019.123.

3. Garcia M, Rodriguez A. Meta-analysis techniques in nutritional epidemiology. Nutrition Reviews. 2021;78(4):234-245. PMID: 33445566.

## Supplementary Material
Additional content that should not be included.
"""
        
        # Create test file structure
        study_dir = os.path.join(self.temp_dir, "studies", self.test_study)
        os.makedirs(study_dir, exist_ok=True)
        
        self.test_md_file = os.path.join(study_dir, f"paper_{self.test_study}.md")
        with open(self.test_md_file, 'w', encoding='utf-8') as f:
            f.write(self.test_md_content)
        
        # Mock LLM response (simulating what Claude would return)
        self.mock_llm_response = """```json
[
  {
    "reference_id": 1,
    "title": "The effects of Mediterranean diet on cognitive function",
    "authors": ["Smith J", "Johnson M"],
    "journal": "American Journal of Clinical Nutrition",
    "year": 2020,
    "volume": "112",
    "issue": "3",
    "pages": "456-465",
    "doi": "10.1093/ajcn/nqaa123",
    "pmid": "32648899",
    "raw_citation": "Smith J, Johnson M. The effects of Mediterranean diet on cognitive function. American Journal of Clinical Nutrition. 2020;112(3):456-465. doi:10.1093/ajcn/nqaa123. PMID: 32648899.",
    "confidence": 0.95
  },
  {
    "reference_id": 2,
    "title": "Systematic review methodology best practices",
    "authors": ["Williams K", "Brown P", "Davis R"],
    "journal": "Journal of Medical Research",
    "year": 2019,
    "volume": "45",
    "issue": "2",
    "pages": "123-134",
    "doi": "10.1234/jmr.2019.123",
    "raw_citation": "Williams K, Brown P, Davis R. Systematic review methodology best practices. Journal of Medical Research. 2019;45(2):123-134. doi:10.1234/jmr.2019.123.",
    "confidence": 0.92
  },
  {
    "reference_id": 3,
    "title": "Meta-analysis techniques in nutritional epidemiology",
    "authors": ["Garcia M", "Rodriguez A"],
    "journal": "Nutrition Reviews",
    "year": 2021,
    "volume": "78",
    "issue": "4",
    "pages": "234-245",
    "pmid": "33445566",
    "raw_citation": "Garcia M, Rodriguez A. Meta-analysis techniques in nutritional epidemiology. Nutrition Reviews. 2021;78(4):234-245. PMID: 33445566.",
    "confidence": 0.90
  }
]
```"""
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('scripts.extract_references._call_anthropic')
    def test_full_extraction_pipeline_claude(self, mock_api):
        """Test complete extraction pipeline with mocked Claude API."""
        # Mock the API call
        mock_api.return_value = self.mock_llm_response
        
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        try:
            # Run extraction
            output_path = f"studies/{self.test_study}/extracted_references.json"
            ref_list = extract_references(
                study_name=self.test_study,
                markdown_file=self.test_md_file,
                llm_model="claude-3-5-sonnet-20241022",
                output_path=output_path,
                debug=False
            )
            
            # Verify API was called
            mock_api.assert_called_once()
            
            # Verify ReferenceList
            self.assertEqual(ref_list.study_name, self.test_study)
            self.assertEqual(len(ref_list.references), 3)
            
            # Verify first reference
            ref1 = ref_list.references[0]
            self.assertEqual(ref1.reference_id, 1)
            self.assertEqual(ref1.title, "The effects of Mediterranean diet on cognitive function")
            self.assertEqual(ref1.authors, ["Smith J", "Johnson M"])
            self.assertEqual(ref1.journal, "American Journal of Clinical Nutrition")
            self.assertEqual(ref1.year, 2020)
            self.assertEqual(ref1.doi, "10.1093/ajcn/nqaa123")
            self.assertEqual(ref1.pmid, "32648899")
            self.assertEqual(ref1.confidence, 0.95)
            
            # Verify output file was created
            self.assertTrue(os.path.exists(output_path))
            
            # Verify output file content
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.assertEqual(data['study_name'], self.test_study)
            self.assertEqual(len(data['references']), 3)
            
            # Verify statistics
            stats = ref_list.get_statistics()
            self.assertEqual(stats['total_references'], 3)
            self.assertEqual(stats['with_doi'], 2)
            self.assertEqual(stats['with_pmid'], 2)
            self.assertEqual(stats['with_identifiers'], 3)
            
        finally:
            os.chdir(original_cwd)
    
    @patch('scripts.extract_references._call_openai')
    def test_full_extraction_pipeline_gpt(self, mock_api):
        """Test complete extraction pipeline with mocked GPT API."""
        # Mock the API call
        mock_api.return_value = self.mock_llm_response
        
        original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        try:
            output_path = f"studies/{self.test_study}/extracted_references.json"
            ref_list = extract_references(
                study_name=self.test_study,
                markdown_file=self.test_md_file,
                llm_model="gpt-4-turbo",
                output_path=output_path,
                debug=False
            )
            
            mock_api.assert_called_once()
            self.assertEqual(len(ref_list.references), 3)
            
        finally:
            os.chdir(original_cwd)
    
    @patch('scripts.extract_references._call_anthropic')
    def test_extraction_with_invalid_reference(self, mock_api):
        """Test extraction handles invalid reference gracefully."""
        # Mock response with one invalid reference
        invalid_response = """[
  {
    "reference_id": 1,
    "title": "Valid Reference",
    "authors": ["Author A"],
    "journal": "Journal",
    "year": 2020,
    "raw_citation": "Citation"
  },
  {
    "reference_id": 2,
    "title": "Invalid Reference",
    "authors": ["Author B"],
    "journal": "Journal",
    "year": 1800,
    "raw_citation": "Citation"
  }
]"""
        mock_api.return_value = invalid_response
        
        original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        try:
            ref_list = extract_references(
                study_name=self.test_study,
                markdown_file=self.test_md_file,
                llm_model="claude-3-5-sonnet-20241022",
                debug=False
            )
            
            # Should only have 1 valid reference
            self.assertEqual(len(ref_list.references), 1)
            self.assertEqual(ref_list.references[0].title, "Valid Reference")
            
        finally:
            os.chdir(original_cwd)
    
    @patch('scripts.extract_references._call_anthropic')
    def test_extraction_statistics_calculation(self, mock_api):
        """Test that statistics are calculated correctly."""
        mock_api.return_value = self.mock_llm_response
        
        original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        try:
            ref_list = extract_references(
                study_name=self.test_study,
                markdown_file=self.test_md_file,
                llm_model="claude-3-5-sonnet-20241022",
                debug=False
            )
            
            stats = ref_list.get_statistics()
            
            # Verify all statistics fields
            self.assertEqual(stats['total_references'], 3)
            self.assertEqual(stats['with_doi'], 2)
            self.assertEqual(stats['with_pmid'], 2)
            self.assertEqual(stats['with_identifiers'], 3)
            self.assertEqual(stats['biomedical_likely'], 2)  # Only refs with PMID or biomedical journal
            self.assertAlmostEqual(stats['average_confidence'], 0.923, places=2)
            self.assertEqual(stats['year_range'], (2019, 2021))
            
        finally:
            os.chdir(original_cwd)


class TestExtractionErrors(unittest.TestCase):
    """Test error handling in extraction pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_file_not_found_error(self):
        """Test handling of missing markdown file."""
        with self.assertRaises(SystemExit):
            extract_references(
                study_name="nonexistent",
                markdown_file="/nonexistent/file.md"
            )
    
    def test_no_references_section_error(self):
        """Test handling when no references section found."""
        # Create file without references section
        study_dir = os.path.join(self.temp_dir, "studies", "test")
        os.makedirs(study_dir, exist_ok=True)
        
        md_file = os.path.join(study_dir, "paper_test.md")
        with open(md_file, 'w') as f:
            f.write("# Paper\n\nNo references here.")
        
        original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        try:
            with self.assertRaises(SystemExit):
                extract_references(
                    study_name="test",
                    markdown_file=md_file
                )
        finally:
            os.chdir(original_cwd)


if __name__ == '__main__':
    unittest.main()
