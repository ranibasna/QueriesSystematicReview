#!/usr/bin/env python3
"""
Reference extraction script for systematic review papers.

This script extracts bibliographic references from markdown-formatted
systematic review papers using LLM-based parsing. It identifies the
references section and structures each citation according to the
Reference data model.

Usage:
    python scripts/extract_references.py <study_name> [options]

Example:
    python scripts/extract_references.py Godos_2024 --llm-model claude-3-5-sonnet
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Reference, ReferenceList


def read_markdown_file(filepath: str) -> str:
    """
    Read markdown file with proper encoding handling.
    
    Args:
        filepath: Path to markdown file
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file encoding is incompatible
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except UnicodeDecodeError:
        # Try alternative encoding
        with open(filepath, 'r', encoding='latin-1') as f:
            content = f.read()
        print(f"⚠️  Warning: File encoding was latin-1, not UTF-8")
        return content


def identify_references_section(content: str) -> Optional[Tuple[str, int, int]]:
    """
    Identify the references section in the markdown content.
    
    Uses pattern matching to find section headings like "References",
    "Included Studies", "Bibliography", etc.
    
    Args:
        content: Full markdown content
        
    Returns:
        Tuple of (section_text, start_pos, end_pos) or None if not found
    """
    # Patterns for reference section headings (case-insensitive)
    patterns = [
        r'(?i)^#{1,6}\s*(References?)\s*$',
        r'(?i)^#{1,6}\s*(Included Studies?)\s*$',
        r'(?i)^#{1,6}\s*(Bibliography)\s*$',
        r'(?i)^#{1,6}\s*(Studies Included.*)\s*$',
        r'(?i)^#{1,6}\s*(Characteristics of Included Studies?)\s*$',
        r'(?i)^\*\*(References?)\*\*\s*$',
        r'(?i)^\*\*(Included Studies?)\*\*\s*$',
    ]
    
    lines = content.split('\n')
    start_line = None
    
    # Find start of references section
    for i, line in enumerate(lines):
        for pattern in patterns:
            if re.match(pattern, line.strip()):
                start_line = i
                break
        if start_line is not None:
            break
    
    if start_line is None:
        return None
    
    # Find end of section (next major heading or end of document)
    end_line = len(lines)
    for i in range(start_line + 1, len(lines)):
        line = lines[i].strip()
        # Check for next major heading (# or ##)
        if re.match(r'^#{1,2}\s+\w', line):
            end_line = i
            break
    
    # Extract section content
    section_lines = lines[start_line:end_line]
    section_text = '\n'.join(section_lines)
    
    # Calculate character positions
    start_pos = sum(len(line) + 1 for line in lines[:start_line])
    end_pos = start_pos + len(section_text)
    
    return (section_text, start_pos, end_pos)


def load_extraction_prompt() -> str:
    """
    Load the reference extraction prompt template.
    
    Returns:
        Prompt template as string
    """
    prompt_path = Path(__file__).parent.parent / "prompts" / "extract_references_prompt.md"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def call_llm_api(prompt: str, model: str = "claude-3-5-sonnet-20241022") -> str:
    """
    Call LLM API to extract references.
    
    This function supports multiple LLM providers through environment variables.
    Currently implements Anthropic Claude API.
    
    Args:
        prompt: Full prompt with paper content
        model: LLM model identifier
        
    Returns:
        LLM response (JSON string)
        
    Raises:
        ImportError: If required API client not installed
        Exception: If API call fails
    """
    # Determine API based on model name
    if "claude" in model.lower():
        return _call_anthropic(prompt, model)
    elif "gpt" in model.lower():
        return _call_openai(prompt, model)
    elif "gemini" in model.lower():
        return _call_gemini(prompt, model)
    else:
        raise ValueError(f"Unsupported model: {model}")


def _call_anthropic(prompt: str, model: str, max_retries: int = 3) -> str:
    """
    Call Anthropic Claude API.
    
    Requires ANTHROPIC_API_KEY environment variable.
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    for attempt in range(max_retries):
        try:
            message = client.messages.create(
                model=model,
                max_tokens=8192,
                temperature=0.1,  # Low temperature for consistent extraction
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract text from response
            response_text = message.content[0].text
            return response_text
            
        except anthropic.APIError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"⚠️  API error, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise Exception(f"API call failed after {max_retries} attempts: {e}")


def _call_openai(prompt: str, model: str, max_retries: int = 3) -> str:
    """
    Call OpenAI GPT API.
    
    Requires OPENAI_API_KEY environment variable.
    """
    try:
        import openai
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = openai.OpenAI(api_key=api_key)
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert research librarian."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=8192
            )
            
            return response.choices[0].message.content
            
        except openai.APIError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"⚠️  API error, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise Exception(f"API call failed after {max_retries} attempts: {e}")


def _call_gemini(prompt: str, model: str, max_retries: int = 3) -> str:
    """
    Call Google Gemini API.
    
    Requires GOOGLE_API_KEY environment variable.
    """
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)
    model_instance = genai.GenerativeModel(model)
    
    for attempt in range(max_retries):
        try:
            response = model_instance.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=8192
                )
            )
            
            return response.text
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"⚠️  API error, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise Exception(f"API call failed after {max_retries} attempts: {e}")


def parse_json_response(response: str) -> List[Dict[str, Any]]:
    """
    Parse JSON response from LLM, handling common formatting issues.
    
    Args:
        response: LLM response text
        
    Returns:
        Parsed JSON data as list of dictionaries
        
    Raises:
        json.JSONDecodeError: If JSON cannot be parsed
    """
    # Remove markdown code blocks if present
    response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
    response = re.sub(r'^```\s*$', '', response, flags=re.MULTILINE)
    response = response.strip()
    
    # Try to find JSON array in response
    # Look for outermost [ ... ]
    start = response.find('[')
    end = response.rfind(']')
    
    if start != -1 and end != -1:
        json_str = response[start:end+1]
    else:
        json_str = response
    
    try:
        data = json.loads(json_str)
        if not isinstance(data, list):
            raise ValueError("Response is not a JSON array")
        return data
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"Response preview: {response[:500]}...")
        raise


def validate_and_create_references(data: List[Dict[str, Any]]) -> List[Reference]:
    """
    Validate extracted data and create Reference objects.
    
    Args:
        data: List of reference dictionaries from LLM
        
    Returns:
        List of validated Reference objects
    """
    references = []
    errors = []
    
    for i, ref_data in enumerate(data, 1):
        try:
            # Ensure required fields exist
            if 'reference_id' not in ref_data:
                ref_data['reference_id'] = i
            
            # Create Reference object (validation happens in __post_init__)
            ref = Reference.from_dict(ref_data)
            references.append(ref)
            
        except (ValueError, TypeError, KeyError) as e:
            error_msg = f"Reference {i}: {e}"
            errors.append(error_msg)
            print(f"⚠️  {error_msg}")
            # Continue with next reference
    
    if errors:
        print(f"\n⚠️  {len(errors)} reference(s) had validation errors")
    
    return references


def extract_references(
    study_name: str,
    markdown_file: Optional[str] = None,
    llm_model: str = "claude-3-5-sonnet-20241022",
    output_path: Optional[str] = None,
    debug: bool = False
) -> ReferenceList:
    """
    Main extraction pipeline.
    
    Args:
        study_name: Name of the study (e.g., "Godos_2024")
        markdown_file: Path to markdown file (default: studies/{study_name}/paper_{study_name}.md)
        llm_model: LLM model to use
        output_path: Output file path (default: studies/{study_name}/extracted_references.json)
        debug: Enable debug output
        
    Returns:
        ReferenceList object with extracted references
    """
    # Determine paths
    if markdown_file is None:
        markdown_file = f"studies/{study_name}/paper_{study_name}.md"
    
    if output_path is None:
        output_path = f"studies/{study_name}/extracted_references.json"
    
    print(f"📄 Reference Extraction: {study_name}")
    print(f"   Source: {markdown_file}")
    print(f"   Model: {llm_model}")
    print()
    
    # Step 1: Read markdown file
    print("Step 1: Reading markdown file...")
    try:
        content = read_markdown_file(markdown_file)
        print(f"✓ Read {len(content):,} characters")
    except FileNotFoundError:
        print(f"❌ Error: File not found: {markdown_file}")
        sys.exit(1)
    
    # Step 2: Identify references section
    print("\nStep 2: Identifying references section...")
    section_result = identify_references_section(content)
    
    if section_result is None:
        print("❌ Error: Could not find references section in document")
        print("   Looked for headings like: References, Included Studies, Bibliography")
        sys.exit(1)
    
    section_text, start_pos, end_pos = section_result
    print(f"✓ Found references section ({len(section_text):,} characters)")
    
    if debug:
        print(f"\n--- Section Preview (first 500 chars) ---")
        print(section_text[:500])
        print(f"---\n")
    
    # Step 3: Load prompt template
    print("\nStep 3: Loading extraction prompt...")
    prompt_template = load_extraction_prompt()
    
    # Insert paper content into prompt
    full_prompt = prompt_template.replace("{PAPER_CONTENT}", section_text)
    print(f"✓ Prompt ready ({len(full_prompt):,} characters)")
    
    # Step 4: Call LLM API
    print(f"\nStep 4: Calling LLM API ({llm_model})...")
    print("   This may take 30-90 seconds...")
    
    try:
        response = call_llm_api(full_prompt, model=llm_model)
        print(f"✓ Received response ({len(response):,} characters)")
    except Exception as e:
        print(f"❌ Error calling LLM API: {e}")
        sys.exit(1)
    
    if debug:
        print(f"\n--- Response Preview (first 500 chars) ---")
        print(response[:500])
        print(f"---\n")
    
    # Step 5: Parse JSON response
    print("\nStep 5: Parsing JSON response...")
    try:
        ref_data = parse_json_response(response)
        print(f"✓ Parsed {len(ref_data)} reference(s)")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"❌ Error parsing response: {e}")
        sys.exit(1)
    
    # Step 6: Validate and create Reference objects
    print("\nStep 6: Validating references...")
    references = validate_and_create_references(ref_data)
    print(f"✓ Validated {len(references)} reference(s)")
    
    # Step 7: Create ReferenceList
    ref_list = ReferenceList(
        study_name=study_name,
        references=references,
        source_file=markdown_file,
        metadata={
            'llm_model': llm_model,
            'section_start': start_pos,
            'section_end': end_pos
        }
    )
    
    # Step 8: Save to file
    print(f"\nStep 7: Saving results...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ref_list.save_to_file(output_path)
    print(f"✓ Saved to: {output_path}")
    
    # Print statistics
    stats = ref_list.get_statistics()
    print(f"\n📊 Extraction Statistics:")
    print(f"   Total references: {stats['total_references']}")
    print(f"   With DOI: {stats['with_doi']} ({stats['with_doi']/stats['total_references']*100:.1f}%)")
    print(f"   With PMID: {stats['with_pmid']} ({stats['with_pmid']/stats['total_references']*100:.1f}%)")
    print(f"   With identifiers: {stats['with_identifiers']} ({stats['with_identifiers']/stats['total_references']*100:.1f}%)")
    print(f"   Likely biomedical: {stats['biomedical_likely']} ({stats['biomedical_likely']/stats['total_references']*100:.1f}%)")
    print(f"   Average confidence: {stats['average_confidence']:.3f}")
    print(f"   Year range: {stats['year_range'][0]}-{stats['year_range'][1]}")
    
    print(f"\n✅ Extraction complete!")
    return ref_list


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Extract references from systematic review papers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/extract_references.py Godos_2024
  python scripts/extract_references.py sleep_apnea --llm-model gpt-4-turbo
  python scripts/extract_references.py ai_2022 --debug
        """
    )
    
    parser.add_argument(
        'study_name',
        help='Name of the study (e.g., Godos_2024, ai_2022)'
    )
    
    parser.add_argument(
        '--markdown-file',
        help='Path to markdown file (default: studies/{study_name}/paper_{study_name}.md)'
    )
    
    parser.add_argument(
        '--llm-model',
        default='claude-3-5-sonnet-20241022',
        help='LLM model to use (default: claude-3-5-sonnet-20241022)'
    )
    
    parser.add_argument(
        '--output-path',
        help='Output file path (default: studies/{study_name}/extracted_references.json)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    
    args = parser.parse_args()
    
    # Run extraction
    extract_references(
        study_name=args.study_name,
        markdown_file=args.markdown_file,
        llm_model=args.llm_model,
        output_path=args.output_path,
        debug=args.debug
    )


if __name__ == "__main__":
    main()
