#!/usr/bin/env python3
"""
Study Preparation Script for Systematic Review Workflow

This script converts PROSPERO and Paper PDFs to Markdown format using the 
docling library via subprocess (keeps the docling environment separate).

The markdown files can then be used for manual extraction of study information
and gold standard PMID lists (PMID extraction must be done manually).

Usage:
    python scripts/prepare_study.py <study_name> [--docling-env docling]
    
Examples:
    # Convert all PDFs in the study directory
    python scripts/prepare_study.py ai_2022
    
    # Use a different docling environment
    python scripts/prepare_study.py ai_2022 --docling-env my_docling
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent


def get_study_dir(study_name: str) -> Path:
    """Get the study directory path."""
    return PROJECT_ROOT / "studies" / study_name


def find_pdf_files(study_dir: Path) -> dict:
    """
    Find PROSPERO and Paper PDFs in the study directory.
    
    Returns:
        dict with 'prospero' and 'paper' keys pointing to PDF paths
    """
    pdfs = {"prospero": None, "paper": None}
    
    for pdf_file in study_dir.glob("*.pdf"):
        name_lower = pdf_file.name.lower()
        if "prospero" in name_lower:
            pdfs["prospero"] = pdf_file
        elif "paper" in name_lower:
            pdfs["paper"] = pdf_file
    
    return pdfs


def convert_pdf_to_markdown(
    pdf_path: Path,
    output_path: Optional[Path] = None,
    docling_env: str = "docling"
) -> Path:
    """
    Convert a PDF to Markdown using docling via subprocess.
    
    This runs in the docling conda environment to keep environments separate.
    
    Args:
        pdf_path: Path to the input PDF
        output_path: Path for the output markdown (default: same name with .md extension)
        docling_env: Name of the conda environment with docling installed
        
    Returns:
        Path to the generated markdown file
    """
    if output_path is None:
        # Clean up filename - replace spaces with underscores for easier handling
        clean_name = pdf_path.stem.replace(' ', '_').replace('-_', '-')
        output_path = pdf_path.parent / f"{clean_name}.md"
    
    print(f"🔄 Converting {pdf_path.name} to Markdown...")
    
    # Use the existing pdf_to_markdown.py script via conda run
    script_path = PROJECT_ROOT / "scripts" / "pdf_to_markdown.py"
    
    cmd = [
        "conda", "run", "-n", docling_env,
        "python", str(script_path),
        str(pdf_path),
        "--output", str(output_path.parent)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout for large PDFs
        )
        
        # The pdf_to_markdown script creates output with original filename
        # We need to rename it to our desired output path
        original_output = pdf_path.parent / f"{pdf_path.stem}.md"
        if original_output.exists() and original_output != output_path:
            original_output.rename(output_path)
        
        if result.returncode != 0 and not output_path.exists():
            print(f"❌ Docling conversion failed: {result.stderr}")
            # Try alternative: direct Python call with docling
            return _convert_pdf_direct(pdf_path, output_path, docling_env)
        
        print(f"✅ Created: {output_path}")
        return output_path
        
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout converting {pdf_path.name}")
        raise
    except FileNotFoundError:
        print(f"⚠️  Script not found, trying direct conversion...")
        return _convert_pdf_direct(pdf_path, output_path, docling_env)


def _convert_pdf_direct(pdf_path: Path, output_path: Path, docling_env: str) -> Path:
    """Direct conversion using inline Python code via conda run."""
    
    python_code = f'''
import sys
from pathlib import Path
from docling.document_converter import DocumentConverter

pdf_path = Path("{pdf_path}")
output_path = Path("{output_path}")

converter = DocumentConverter()
result = converter.convert(str(pdf_path))
markdown_content = result.document.export_to_markdown()

output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(markdown_content)

print(f"Converted to {{output_path}}")
'''
    
    cmd = ["conda", "run", "-n", docling_env, "python", "-c", python_code]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    
    if result.returncode != 0:
        raise RuntimeError(f"Direct conversion failed: {result.stderr}")
    
    print(f"✅ Created: {output_path}")
    return output_path




def lookup_pmid(
    first_author: str,
    year: str,
    title: Optional[str] = None,
    email: Optional[str] = None
) -> Optional[dict]:
    """
    DEPRECATED: This function has been removed.
    
    PMID extraction must be done manually for each study.
    See documentation for guidance on manual PMID extraction.
    """
    raise NotImplementedError("PMID extraction removed. See documentation for manual PMID extraction guidance.")


def generate_gold_pmids(studies: list, output_path: Path, email: Optional[str] = None, verbose: bool = True) -> int:
    """
    DEPRECATED: This function has been removed.
    
    PMID extraction must be done manually for each study.
    See documentation for guidance on manual PMID extraction.
    """
    raise NotImplementedError("PMID extraction removed. See documentation for manual PMID extraction guidance.")


def interactive_pmid_input(output_path: Path) -> int:
    """
    DEPRECATED: This function has been removed.
    
    PMID extraction must be done manually for each study.
    See documentation for guidance on manual PMID extraction.
    """
    raise NotImplementedError("PMID extraction removed. See documentation for manual PMID extraction guidance.")


def main():
    parser = argparse.ArgumentParser(
        description="Convert PROSPERO and Paper PDFs to Markdown for a study",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all PDFs in the study directory
  python scripts/prepare_study.py ai_2022
  
  # Use different docling environment
  python scripts/prepare_study.py ai_2022 --docling-env my_docling
        """
    )
    
    parser.add_argument(
        "study_name",
        help="Name of the study (directory under studies/)"
    )
    
    parser.add_argument(
        "--docling-env",
        default="docling",
        help="Conda environment with docling installed (default: docling)"
    )
    
    args = parser.parse_args()
    
    # Validate study directory
    study_dir = get_study_dir(args.study_name)
    if not study_dir.exists():
        print(f"❌ Study directory not found: {study_dir}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"📋 Preparing Study: {args.study_name}")
    print(f"📂 Directory: {study_dir}")
    print(f"{'='*60}\n")
    
    # Find PDF files
    pdfs = find_pdf_files(study_dir)
    
    # Convert PDFs to Markdown
    print("📄 Converting PDFs to Markdown")
    print("-" * 40)
    
    conversion_count = 0
    for pdf_type, pdf_path in pdfs.items():
        if pdf_path:
            try:
                # Generate appropriate output name
                if pdf_type == "prospero":
                    output_name = f"prospero_{args.study_name}.md"
                else:
                    output_name = f"paper_{args.study_name}.md"
                output_path = study_dir / output_name
                
                convert_pdf_to_markdown(pdf_path, output_path, args.docling_env)
                conversion_count += 1
            except Exception as e:
                print(f"❌ Failed to convert {pdf_path.name}: {e}")
        else:
            print(f"⚠️  No {pdf_type} PDF found")
    
    print(f"\n{'='*60}")
    print("✅ PDF conversion complete!")
    print(f"{'='*60}\n")
    
    # Print next steps
    print("📋 Next Steps:")
    print(f"   1. Review the markdown files in {study_dir}")
    print(f"   2. Manually extract gold standard PMIDs (see documentation)")
    print(f"   3. Create gold_pmids_{args.study_name}.csv with the PMIDs")
    print(f"   4. Create queries.txt with your search strategies")
    print(f"   5. Run the workflow: ./run_workflow.sh {args.study_name}\n")


if __name__ == "__main__":
    main()
