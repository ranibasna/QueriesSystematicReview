"""
Unit tests for extract_references.py

Tests cover:
- Markdown file reading
- References section identification
- JSON parsing
- Reference validation
- Error handling
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

from scripts.extract_references import (
    read_markdown_file,
    identify_references_section,
    parse_json_response,
    validate_and_create_references,
    load_extraction_prompt
)
from models import Reference


class TestMarkdownReading(unittest.TestCase):
    """Test markdown file reading functionality."""
    
    def test_read_utf8_file(self):
        """Test reading UTF-8 encoded file."""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.md') as f:
            f.write("# Test Document\n\nSome content with émojis: 🚀")
            temp_path = f.name
        
        try:
            content = read_markdown_file(temp_path)
            self.assertIn("Test Document", content)
            self.assertIn("🚀", content)
        finally:
            os.unlink(temp_path)
    
    def test_read_latin1_file(self):
        """Test reading latin-1 encoded file (with fallback)."""
        with tempfile.NamedTemporaryFile(mode='w', encoding='latin-1', delete=False, suffix='.md') as f:
            f.write("# Test Document\n\nSome content")
            temp_path = f.name
        
        try:
            content = read_markdown_file(temp_path)
            self.assertIn("Test Document", content)
        finally:
            os.unlink(temp_path)
    
    def test_file_not_found(self):
        """Test handling of missing file."""
        with self.assertRaises(FileNotFoundError):
            read_markdown_file("/nonexistent/file.md")


class TestReferenceSectionIdentification(unittest.TestCase):
    """Test references section identification."""
    
    def test_identify_references_heading(self):
        """Test identification with standard 'References' heading."""
        content = """
# Introduction
Some intro text.

## References
1. Smith J. Title. Journal. 2020.
2. Jones M. Another title. Journal. 2021.

## Appendix
Extra content.
"""
        result = identify_references_section(content)
        self.assertIsNotNone(result)
        section_text, start_pos, end_pos = result
        self.assertIn("References", section_text)
        self.assertIn("Smith J", section_text)
        self.assertNotIn("Appendix", section_text)
    
    def test_identify_included_studies_heading(self):
        """Test identification with 'Included Studies' heading."""
        content = """
# Methods

## Included Studies
1. Author A. Study 1. 2020.
2. Author B. Study 2. 2021.

## Discussion
"""
        result = identify_references_section(content)
        self.assertIsNotNone(result)
        section_text, _, _ = result
        self.assertIn("Included Studies", section_text)
        self.assertIn("Author A", section_text)
    
    def test_identify_bibliography_heading(self):
        """Test identification with 'Bibliography' heading."""
        content = """
# Abstract

### Bibliography
- Item 1
- Item 2

## Supplementary
"""
        result = identify_references_section(content)
        self.assertIsNotNone(result)
        section_text, _, _ = result
        self.assertIn("Bibliography", section_text)
    
    def test_bold_references_heading(self):
        """Test identification with bold references heading."""
        content = """
# Main Content

**References**

1. Citation 1
2. Citation 2
"""
        result = identify_references_section(content)
        self.assertIsNotNone(result)
        section_text, _, _ = result
        self.assertIn("References", section_text)
        self.assertIn("Citation 1", section_text)
    
    def test_case_insensitive_matching(self):
        """Test case-insensitive heading matching."""
        content = "## REFERENCES\n1. Citation"
        result = identify_references_section(content)
        self.assertIsNotNone(result)
        
        content = "## references\n1. Citation"
        result = identify_references_section(content)
        self.assertIsNotNone(result)
    
    def test_no_references_section(self):
        """Test handling when no references section exists."""
        content = """
# Introduction
Some content.

## Methods
More content.

## Results
Even more content.
"""
        result = identify_references_section(content)
        self.assertIsNone(result)
    
    def test_section_ends_at_next_heading(self):
        """Test that section correctly ends at next heading."""
        content = """
## References
1. Citation 1
2. Citation 2

## Supplementary Material
Should not be included.
"""
        result = identify_references_section(content)
        self.assertIsNotNone(result)
        section_text, _, _ = result
        self.assertIn("Citation 2", section_text)
        self.assertNotIn("Supplementary", section_text)
    
    def test_section_extends_to_end_of_document(self):
        """Test that section extends to end if no next heading."""
        content = """
## References
1. Citation 1
2. Citation 2
Last line.
"""
        result = identify_references_section(content)
        self.assertIsNotNone(result)
        section_text, _, _ = result
        self.assertIn("Last line", section_text)


class TestJSONParsing(unittest.TestCase):
    """Test JSON response parsing."""
    
    def test_parse_clean_json_array(self):
        """Test parsing clean JSON array."""
        response = '[{"reference_id": 1, "title": "Test"}]'
        result = parse_json_response(response)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Test")
    
    def test_parse_json_with_markdown_code_block(self):
        """Test parsing JSON wrapped in markdown code block."""
        response = """```json
[{"reference_id": 1, "title": "Test"}]
```"""
        result = parse_json_response(response)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
    
    def test_parse_json_with_surrounding_text(self):
        """Test parsing JSON with surrounding text."""
        response = """Here are the references:

[{"reference_id": 1, "title": "Test"}]

Hope this helps!"""
        result = parse_json_response(response)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
    
    def test_parse_json_with_whitespace(self):
        """Test parsing JSON with extra whitespace."""
        response = """
        
        [
            {"reference_id": 1, "title": "Test"}
        ]
        
        """
        result = parse_json_response(response)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
    
    def test_invalid_json_raises_error(self):
        """Test that invalid JSON raises error."""
        response = "This is not JSON at all"
        with self.assertRaises(json.JSONDecodeError):
            parse_json_response(response)
    
    def test_non_array_json_raises_error(self):
        """Test that non-array JSON raises error."""
        response = '{"reference_id": 1, "title": "Test"}'
        with self.assertRaises(ValueError):
            parse_json_response(response)


class TestReferenceValidation(unittest.TestCase):
    """Test reference validation and creation."""
    
    def test_validate_valid_reference(self):
        """Test validation of valid reference data."""
        data = [{
            "reference_id": 1,
            "title": "Test Article",
            "authors": ["Smith J", "Jones M"],
            "journal": "Test Journal",
            "year": 2020,
            "doi": "10.1234/test",
            "confidence": 0.95,
            "raw_citation": "Smith J, Jones M. Test Article. Test Journal. 2020."
        }]
        
        refs = validate_and_create_references(data)
        self.assertEqual(len(refs), 1)
        self.assertIsInstance(refs[0], Reference)
        self.assertEqual(refs[0].title, "Test Article")
    
    def test_validate_minimal_reference(self):
        """Test validation of minimal valid reference."""
        data = [{
            "reference_id": 1,
            "title": "Title",
            "authors": ["Author"],
            "journal": "Journal",
            "year": 2020,
            "raw_citation": "Citation"
        }]
        
        refs = validate_and_create_references(data)
        self.assertEqual(len(refs), 1)
    
    def test_validate_adds_missing_reference_id(self):
        """Test that missing reference_id is added automatically."""
        data = [{
            "title": "Title",
            "authors": ["Author"],
            "journal": "Journal",
            "year": 2020,
            "raw_citation": "Citation"
        }]
        
        refs = validate_and_create_references(data)
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].reference_id, 1)
    
    def test_validate_invalid_year_skips_reference(self):
        """Test that reference with invalid year is skipped."""
        data = [
            {
                "reference_id": 1,
                "title": "Good",
                "authors": ["A"],
                "journal": "J",
                "year": 2020,
                "raw_citation": "C"
            },
            {
                "reference_id": 2,
                "title": "Bad",
                "authors": ["B"],
                "journal": "J",
                "year": 1800,  # Invalid
                "raw_citation": "C"
            }
        ]
        
        refs = validate_and_create_references(data)
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].title, "Good")
    
    def test_validate_missing_required_field_skips_reference(self):
        """Test that reference missing required field is skipped."""
        data = [
            {
                "reference_id": 1,
                "title": "Good",
                "authors": ["A"],
                "journal": "J",
                "year": 2020,
                "raw_citation": "C"
            },
            {
                "reference_id": 2,
                # Missing title
                "authors": ["B"],
                "journal": "J",
                "year": 2020,
                "raw_citation": "C"
            }
        ]
        
        refs = validate_and_create_references(data)
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].title, "Good")
    
    def test_validate_multiple_valid_references(self):
        """Test validation of multiple valid references."""
        data = [
            {
                "reference_id": i,
                "title": f"Title {i}",
                "authors": [f"Author {i}"],
                "journal": "Journal",
                "year": 2020,
                "raw_citation": f"Citation {i}"
            }
            for i in range(1, 6)
        ]
        
        refs = validate_and_create_references(data)
        self.assertEqual(len(refs), 5)


class TestPromptLoading(unittest.TestCase):
    """Test prompt template loading."""
    
    def test_load_extraction_prompt(self):
        """Test loading the extraction prompt template."""
        prompt = load_extraction_prompt()
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 100)
        self.assertIn("{PAPER_CONTENT}", prompt)
        # Check for key instructions
        self.assertIn("reference", prompt.lower())
        self.assertIn("json", prompt.lower())


if __name__ == '__main__':
    unittest.main()
