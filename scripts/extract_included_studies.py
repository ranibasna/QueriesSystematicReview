#!/usr/bin/env python3
"""
Extract included studies from systematic review papers.

This script is designed to extract the LIST OF INCLUDED STUDIES from systematic
reviews, not all references. It:
1. Identifies tables listing included studies (e.g., "Table 1: Characteristics of included studies")
2. Extracts reference numbers/citations from the table
3. Matches them to the references section for full bibliographic data
4. Outputs structured data about ONLY the studies included in the review

This is critical for systematic reviews where we need to identify which studies
passed the screening process and were included in the analysis.

Usage:
    python scripts/extract_included_studies.py <study_name> [options]

Example:
    python scripts/extract_included_studies.py ai_2022 --debug
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Reference, ReferenceList


@dataclass
class IncludedStudy:
    """Represents a study included in the systematic review."""
    reference_number: int  # Reference number in the paper (e.g., [13])
    first_author: str
    year: int
    title: str
    journal: str
    authors: List[str]
    doi: Optional[str] = None
    pmid: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    raw_citation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


def read_markdown_file(filepath: str) -> str:
    """Read markdown file with proper encoding handling."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='latin-1') as f:
            content = f.read()
        print(f"⚠️  Warning: File encoding was latin-1, not UTF-8")
        return content


def find_included_studies_table(content: str) -> Optional[Tuple[str, List[int]]]:
    """
    Find the table that lists included studies and extract reference numbers.
    
    Returns:
        Tuple of (table_text, list_of_reference_numbers) or None if not found
    """
    # Look for table headings
    table_patterns = [
        r'Table\s+\d+\s+.*[Ii]ncluded\s+[Ss]tudies',
        r'Table\s+\d+\s+.*[Cc]haracteristics\s+of\s+.*[Ss]tudies',
        r'Table\s+\d+\s+.*[Bb]aseline\s+[Cc]haracteristics',
        r'## [Ii]ncluded [Ss]tudies',
        r'## [Cc]haracteristics of [Ii]ncluded [Ss]tudies'
    ]
    
    lines = content.split('\n')
    table_start = None
    
    # Find table start
    for i, line in enumerate(lines):
        for pattern in table_patterns:
            if re.search(pattern, line):
                table_start = i
                print(f"✓ Found table: {line.strip()}")
                break
        if table_start is not None:
            break
    
    if table_start is None:
        return None
    
    # Find table end (next heading or empty section)
    table_end = len(lines)
    empty_line_count = 0
    for i in range(table_start + 1, len(lines)):
        line = lines[i].strip()
        if re.match(r'^##\s+\w', line):  # Next heading
            table_end = i
            break
        if not line:
            empty_line_count += 1
            if empty_line_count > 3:  # Multiple empty lines = end of section
                table_end = i
                break
        else:
            empty_line_count = 0
    
    # Extract table content
    table_text = '\n'.join(lines[table_start:table_end])
    
    # Extract reference numbers from table using multiple patterns
    # Pattern 1: Author et al. [13]
    # Pattern 2: Author et al. [12,13]
    # Pattern 3: [13] at start of line
    
    ref_numbers = set()
    
    # Find all [number] patterns
    for match in re.finditer(r'\[(\d+)\]', table_text):
        ref_num = int(match.group(1))
        ref_numbers.add(ref_num)
    
    # Also look for references in table cells (e.g., "Study (Ref.)" column)
    for match in re.finditer(r'(?:et al\.|Al\.) \[(\d+)\]', table_text):
        ref_num = int(match.group(1))
        ref_numbers.add(ref_num)
    
    if not ref_numbers:
        print(f"⚠️  Warning: Found table but no reference numbers extracted")
        return None
    
    ref_list = sorted(list(ref_numbers))
    print(f"✓ Extracted {len(ref_list)} reference numbers: {ref_list}")
    
    return (table_text, ref_list)


def parse_references_section(content: str) -> Dict[int, str]:
    """
    Parse the references section and return a mapping of reference_number -> citation text.
    
    Returns:
        Dictionary mapping reference numbers to full citation strings
    """
    # Find references section
    lines = content.split('\n')
    ref_start = None
    
    for i, line in enumerate(lines):
        if re.match(r'^##?\s*(References?|Bibliography)\s*$', line.strip()):
            ref_start = i
            print(f"✓ Found references section at line {i}")
            break
    
    if ref_start is None:
        print(f"❌ Error: Could not find references section")
        return {}
    
    # Parse references
    # Pattern: - [1] Citation text...
    # Pattern: [1] Citation text...
    # Pattern: 1. Citation text...
    
    references = {}
    current_ref_num = None
    current_ref_text = []
    
    for line in lines[ref_start + 1:]:
        # Check for new reference
        # Pattern 1: - [1] Text
        match = re.match(r'^\s*-\s*\[(\d+)\]\s+(.*)', line)
        if match:
            # Save previous reference
            if current_ref_num is not None:
                references[current_ref_num] = ' '.join(current_ref_text).strip()
            
            current_ref_num = int(match.group(1))
            current_ref_text = [match.group(2)]
            continue
        
        # Pattern 2: [1] Text (at start of line)
        match = re.match(r'^\s*\[(\d+)\]\s+(.*)', line)
        if match:
            if current_ref_num is not None:
                references[current_ref_num] = ' '.join(current_ref_text).strip()
            
            current_ref_num = int(match.group(1))
            current_ref_text = [match.group(2)]
            continue
        
        # Pattern 3: 1. Text
        match = re.match(r'^\s*(\d+)\.\s+(.*)', line)
        if match:
            if current_ref_num is not None:
                references[current_ref_num] = ' '.join(current_ref_text).strip()
            
            current_ref_num = int(match.group(1))
            current_ref_text = [match.group(2)]
            continue
        
        # Continuation of current reference
        if current_ref_num is not None and line.strip():
            # Skip table separators
            if not re.match(r'^\s*\|', line) and not re.match(r'^\s*[-\|]+\s*$', line):
                current_ref_text.append(line.strip())
    
    # Save last reference
    if current_ref_num is not None:
        references[current_ref_num] = ' '.join(current_ref_text).strip()
    
    print(f"✓ Parsed {len(references)} total references")
    return references


def parse_citation(ref_number: int, citation_text: str) -> Optional[IncludedStudy]:
    """
    Parse a citation string into structured data.
    
    This uses deterministic pattern matching instead of LLM APIs.
    """
    # Clean up citation
    citation = citation_text.strip()
    
    # Remove asterisks (importance markers)
    citation = re.sub(r'^\*\s*', '', citation)
    
    # Extract DOI
    doi = None
    doi_match = re.search(r'(?:doi:|https?://doi\.org/)(10\.\d{4,}[^\s,;]+)', citation, re.IGNORECASE)
    if doi_match:
        doi = doi_match.group(1).rstrip('.')
    
    # Extract PMID
    pmid = None
    pmid_match = re.search(r'PMID:?\s*(\d+)', citation, re.IGNORECASE)
    if pmid_match:
        pmid = pmid_match.group(1)
    
    # Parse authors and title
    # Common pattern: Authors. Title. Journal Year;Volume:Pages.
    # Pattern 1: LastName FirstInitial(s), ... Title. Journal ...
    
    # Extract first author (before first comma or period)
    first_author_match = re.match(r'^([A-Z][a-zA-Z\'-]+\s+[A-Z]+(?:\s+[A-Z]+)?)', citation)
    first_author = first_author_match.group(1) if first_author_match else "Unknown"
    
    # Extract year
    year = None
    year_match = re.search(r'\b(19\d{2}|20[012]\d)\b', citation)
    if year_match:
        year = int(year_match.group(1))
    else:
        year = 2000  # Default fallback
    
    # Extract title (between first period and second period or "Journal")
    title = ""
    # Look for pattern: Authors. Title. Journal
    parts = citation.split('. ')
    if len(parts) >= 2:
        # Title is usually the second part
        title = parts[1].strip()
        # Remove trailing punctuation
        title = re.sub(r'[.,;:]\s*$', '', title)
    
    if not title:
        # Fallback: use first 100 chars
        title = citation[:100] + "..." if len(citation) > 100 else citation
    
    # Extract journal name (tricky - usually after title, before year)
    journal = ""
    # Pattern: Title. Journal Year;Volume:Pages
    journal_match = re.search(r'\.\s+([A-Z][^.]+?)\s+\d{4}', citation)
    if journal_match:
        journal = journal_match.group(1).strip()
    
    if not journal:
        # Fallback
        journal = "Unknown Journal"
    
    # Extract all authors (simplified - just get first author for now)
    authors = [first_author]
    
    # Extract volume/issue/pages
    volume = None
    issue = None
    pages = None
    
    # Pattern: Year;Volume(Issue):Pages
    vol_match = re.search(r'\d{4};(\d+)(?:\((\d+)\))?:(\d+[\s-]+\d+|[\de\s]+)', citation)
    if vol_match:
        volume = vol_match.group(1)
        issue = vol_match.group(2)
        pages = vol_match.group(3).replace(' ', '')
    
    return IncludedStudy(
        reference_number=ref_number,
        first_author=first_author,
        year=year,
        title=title,
        journal=journal,
        authors=authors,
        doi=doi,
        pmid=pmid,
        volume=volume,
        issue=issue,
        pages=pages,
        raw_citation=citation
    )


def extract_included_studies(
    study_name: str,
    markdown_file: Optional[str] = None,
    output_path: Optional[str] = None,
    debug: bool = False
) -> Dict[str, Any]:
    """
    Main extraction pipeline for included studies.
    
    Args:
        study_name: Name of the systematic review study
        markdown_file: Path to markdown file
        output_path: Output file path
        debug: Enable debug output
        
    Returns:
        Dictionary with extracted studies data
    """
    # Determine paths
    if markdown_file is None:
        markdown_file = f"studies/{study_name}/paper_{study_name}.md"
    
    if output_path is None:
        output_path = f"studies/{study_name}/included_studies.json"
    
    print(f"📚 Included Studies Extraction: {study_name}")
    print(f"   Source: {markdown_file}")
    print()
    
    # Step 1: Read markdown file
    print("Step 1: Reading markdown file...")
    try:
        content = read_markdown_file(markdown_file)
        print(f"✓ Read {len(content):,} characters\n")
    except FileNotFoundError:
        print(f"❌ Error: File not found: {markdown_file}")
        sys.exit(1)
    
    # Step 2: Find included studies table
    print("Step 2: Finding included studies table...")
    table_result = find_included_studies_table(content)
    
    if table_result is None:
        print("❌ Error: Could not find included studies table")
        sys.exit(1)
    
    table_text, ref_numbers = table_result
    print(f"✓ Found {len(ref_numbers)} included studies\n")
    
    if debug:
        print(f"--- Table Preview (first 500 chars) ---")
        print(table_text[:500])
        print(f"---\n")
    
    # Step 3: Parse references section
    print("Step 3: Parsing references section...")
    references = parse_references_section(content)
    
    if not references:
        print("❌ Error: Could not parse references section")
        sys.exit(1)
    
    print(f"✓ Parsed {len(references)} total references\n")
    
    # Step 4: Extract included studies
    print("Step 4: Extracting included studies...")
    included_studies = []
    
    for ref_num in ref_numbers:
        if ref_num not in references:
            print(f"⚠️  Warning: Reference [{ref_num}] not found in references section")
            continue
        
        citation_text = references[ref_num]
        
        if debug:
            print(f"\n[{ref_num}] {citation_text[:100]}...")
        
        study = parse_citation(ref_num, citation_text)
        
        if study:
            included_studies.append(study)
            if debug:
                print(f"    → {study.first_author} ({study.year}): {study.title[:60]}...")
    
    print(f"✓ Extracted {len(included_studies)} included studies\n")
    
    # Step 5: Generate output
    output_data = {
        "study_name": study_name,
        "source_file": markdown_file,
        "total_included_studies": len(included_studies),
        "extraction_method": "deterministic_parsing",
        "included_studies": [study.to_dict() for study in included_studies]
    }
    
    # Step 6: Calculate statistics
    with_doi = sum(1 for s in included_studies if s.doi)
    with_pmid = sum(1 for s in included_studies if s.pmid)
    with_identifiers = sum(1 for s in included_studies if s.doi or s.pmid)
    
    output_data["statistics"] = {
        "total_studies": len(included_studies),
        "with_doi": with_doi,
        "with_pmid": with_pmid,
        "with_identifiers": with_identifiers,
        "doi_coverage_percent": round(with_doi / len(included_studies) * 100, 1) if included_studies else 0,
        "pmid_coverage_percent": round(with_pmid / len(included_studies) * 100, 1) if included_studies else 0,
        "identifier_coverage_percent": round(with_identifiers / len(included_studies) * 100, 1) if included_studies else 0
    }
    
    # Step 7: Save to file
    print("Step 5: Saving results...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved to: {output_path}\n")
    
    # Print statistics
    stats = output_data["statistics"]
    print(f"📊 Extraction Statistics:")
    print(f"   Total included studies: {stats['total_studies']}")
    print(f"   With DOI: {stats['with_doi']} ({stats['doi_coverage_percent']}%)")
    print(f"   With PMID: {stats['with_pmid']} ({stats['pmid_coverage_percent']}%)")
    print(f"   With identifiers: {stats['with_identifiers']} ({stats['identifier_coverage_percent']}%)")
    
    print(f"\n✅ Extraction complete!")
    return output_data


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Extract included studies from systematic review papers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/extract_included_studies.py ai_2022
  python scripts/extract_included_studies.py Godos_2024 --debug
        """
    )
    
    parser.add_argument(
        'study_name',
        help='Name of the study (e.g., ai_2022, Godos_2024)'
    )
    
    parser.add_argument(
        '--markdown-file',
        help='Path to markdown file (default: studies/{study_name}/paper_{study_name}.md)'
    )
    
    parser.add_argument(
        '--output-path',
        help='Output file path (default: studies/{study_name}/included_studies.json)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    
    args = parser.parse_args()
    
    # Run extraction
    extract_included_studies(
        study_name=args.study_name,
        markdown_file=args.markdown_file,
        output_path=args.output_path,
        debug=args.debug
    )


if __name__ == "__main__":
    main()
