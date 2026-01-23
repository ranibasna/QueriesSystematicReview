"""
Unit tests for extract_included_studies.py
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.extract_included_studies import (
    find_included_studies_table,
    parse_references_section,
    parse_citation,
    extract_included_studies
)


class TestTableFinding(unittest.TestCase):
    """Test finding included studies tables."""
    
    def test_find_table_with_standard_heading(self):
        """Test finding table with 'Table 1 Baseline characteristics of included studies'."""
        content = """
# Introduction
Some text.

Table 1 Baseline characteristics of included studies.

| Study (Ref.) | Year | Country |
|--------------|------|---------|
| Smith et al. [12] | 2020 | USA |
| Jones et al. [13] | 2021 | UK |

## Discussion
More text.
"""
        result = find_included_studies_table(content)
        self.assertIsNotNone(result)
        table_text, ref_numbers = result
        self.assertEqual(sorted(ref_numbers), [12, 13])
    
    def test_find_table_with_included_studies_heading(self):
        """Test finding table with 'Included Studies' heading."""
        content = """
## Included Studies

The following studies were included [15, 16, 17]:

| Author | Year |
|--------|------|
| [15] Author A | 2020 |
"""
        result = find_included_studies_table(content)
        self.assertIsNotNone(result)
        _, ref_numbers = result
        self.assertIn(15, ref_numbers)
    
    def test_no_table_found(self):
        """Test when no table exists."""
        content = """
# Introduction
No tables here.

## Methods
Still no tables.
"""
        result = find_included_studies_table(content)
        self.assertIsNone(result)


class TestReferenceParsing(unittest.TestCase):
    """Test parsing references section."""
    
    def test_parse_references_with_brackets(self):
        """Test parsing references with bracket numbers."""
        content = """
## References

- [1] Smith J, Jones M. Title of paper. Journal. 2020;10:123-456.
- [2] Brown K. Another paper. Different Journal. 2021;15:789-012.
"""
        refs = parse_references_section(content)
        self.assertEqual(len(refs), 2)
        self.assertIn(1, refs)
        self.assertIn(2, refs)
        self.assertIn("Smith J", refs[1])
        self.assertIn("Brown K", refs[2])
    
    def test_parse_references_without_dash(self):
        """Test parsing references without leading dash."""
        content = """
## References

[1] Author A. Paper title. Journal. 2020;5:1-10.
[2] Author B. Second paper. Journal. 2021;6:11-20.
"""
        refs = parse_references_section(content)
        self.assertEqual(len(refs), 2)
    
    def test_parse_multi_line_references(self):
        """Test parsing references spanning multiple lines."""
        content = """
## References

- [1] Smith J, Jones M, Williams K, Brown P. Very long title that spans 
multiple lines in the document. Journal Name. 2020;10:123-456.
- [2] Single line reference. Journal. 2021;5:1-10.
"""
        refs = parse_references_section(content)
        self.assertEqual(len(refs), 2)
        self.assertIn("multiple lines", refs[1])


class TestCitationParsing(unittest.TestCase):
    """Test parsing individual citations."""
    
    def test_parse_complete_citation(self):
        """Test parsing citation with all fields."""
        citation = "Li AM, Au CT, Sung RY, Ho C, Ng PC, Fok TF, et al. Ambulatory blood pressure in children with obstructive sleep apnoea: a community based study. Thorax 2008;63:803-809. doi:10.1136/thx.2007.091132"
        
        study = parse_citation(12, citation)
        
        self.assertIsNotNone(study)
        self.assertEqual(study.reference_number, 12)
        self.assertEqual(study.first_author, "Li AM")
        self.assertEqual(study.year, 2008)
        self.assertIn("Ambulatory blood pressure", study.title)
        self.assertEqual(study.journal, "Thorax")
        self.assertEqual(study.doi, "10.1136/thx.2007.091132")
        self.assertEqual(study.volume, "63")
        self.assertEqual(study.pages, "803-809")
    
    def test_parse_citation_with_pmid(self):
        """Test parsing citation with PMID."""
        citation = "Amin RS, Carroll JL, Jeffries JL, Grone C, Bean JA, Chini B, et al. Twenty-four-hour ambulatory blood pressure in children with sleep-disordered breathing. Am J Respir Crit Care Med 2004;169:950-956. PMID: 14764433"
        
        study = parse_citation(13, citation)
        
        self.assertIsNotNone(study)
        self.assertEqual(study.pmid, "14764433")
        self.assertEqual(study.year, 2004)
    
    def test_parse_citation_minimal(self):
        """Test parsing citation with minimal information."""
        citation = "Author A. Simple title. Journal 2020;5:1-10."
        
        study = parse_citation(1, citation)
        
        self.assertIsNotNone(study)
        self.assertEqual(study.first_author, "Author A")
        self.assertEqual(study.year, 2020)
        self.assertEqual(study.volume, "5")
    
    def test_parse_citation_with_asterisk(self):
        """Test parsing citation with importance marker (asterisk)."""
        citation = "* Important Study, Author B. Critical findings. Top Journal 2021;10:100-200."
        
        study = parse_citation(5, citation)
        
        self.assertIsNotNone(study)
        # Asterisk should be removed, first author extracted
        self.assertIn("Important S", study.first_author)  # Extracts first name with initial


class TestIntegration(unittest.TestCase):
    """Integration tests with real ai_2022 data."""
    
    def test_ai_2022_extraction(self):
        """Test extraction on actual ai_2022 study."""
        ai_2022_md = "studies/ai_2022/paper_ai_2022.md"
        
        if not os.path.exists(ai_2022_md):
            self.skipTest("ai_2022 markdown file not found")
        
        # Run extraction
        result = extract_included_studies(
            study_name="ai_2022_test",
            markdown_file=ai_2022_md,
            output_path="/tmp/test_ai_2022_included.json",
            debug=False
        )
        
        # Verify results
        self.assertEqual(result["total_included_studies"], 14)
        self.assertEqual(len(result["included_studies"]), 14)
        
        # Check that we extracted the expected reference numbers
        ref_numbers = [s["reference_number"] for s in result["included_studies"]]
        expected_refs = [12, 13, 17, 18, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]
        self.assertEqual(sorted(ref_numbers), expected_refs)
        
        # Verify key studies
        first_study = result["included_studies"][0]
        self.assertIn("first_author", first_study)
        self.assertIn("year", first_study)
        self.assertIn("title", first_study)
        self.assertIn("journal", first_study)
        
        # Clean up
        if os.path.exists("/tmp/test_ai_2022_included.json"):
            os.remove("/tmp/test_ai_2022_included.json")
    
    def test_comparison_with_gold_standard(self):
        """Compare extraction with gold standard PMIDs."""
        ai_2022_md = "studies/ai_2022/paper_ai_2022.md"
        gold_standard = "studies/ai_2022/gold_pmids_ai_2022_detailed.csv"
        
        if not os.path.exists(ai_2022_md) or not os.path.exists(gold_standard):
            self.skipTest("Required files not found")
        
        # Run extraction
        result = extract_included_studies(
            study_name="ai_2022_test",
            markdown_file=ai_2022_md,
            output_path="/tmp/test_ai_2022_gold.json",
            debug=False
        )
        
        # Load gold standard
        import csv
        gold_pmids = set()
        with open(gold_standard, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                gold_pmids.add(row['pmid'])
        
        # We should have found 14 studies (same as gold standard)
        self.assertEqual(result["total_included_studies"], len(gold_pmids))
        
        # Clean up
        if os.path.exists("/tmp/test_ai_2022_gold.json"):
            os.remove("/tmp/test_ai_2022_gold.json")


if __name__ == '__main__':
    unittest.main()
