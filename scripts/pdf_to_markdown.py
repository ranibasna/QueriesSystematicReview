#!/usr/bin/env python3
"""
PDF to Markdown Converter using Docling

This script converts PDF files to Markdown format using the Docling library.
It supports single file conversion or batch processing of multiple PDFs.

Usage:
    python pdf_to_markdown.py <input_pdf_path> [--output <output_dir>]
    python pdf_to_markdown.py <input_directory> [--output <output_dir>] [--batch]
    
Examples:
    # Convert single PDF
    python pdf_to_markdown.py document.pdf
    
    # Convert single PDF with custom output directory
    python pdf_to_markdown.py document.pdf --output ./markdown_files
    
    # Convert all PDFs in a directory
    python pdf_to_markdown.py ./pdfs --batch --output ./markdown_files
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
from docling.document_converter import DocumentConverter


def setup_converter() -> DocumentConverter:
    """
    Set up and configure the Docling DocumentConverter with optimized settings.
    
    Returns:
        DocumentConverter: Configured document converter instance
    """
    # Initialize converter with default settings
    # Docling automatically handles OCR, table extraction, and format detection
    converter = DocumentConverter()
    
    return converter


def convert_pdf_to_markdown(
    pdf_path: Path,
    output_dir: Optional[Path] = None,
    verbose: bool = True
) -> Path:
    """
    Convert a single PDF file to Markdown format.
    
    Args:
        pdf_path: Path to the input PDF file
        output_dir: Directory where the markdown file will be saved (default: same as input)
        verbose: Print conversion progress messages
        
    Returns:
        Path: Path to the generated markdown file
        
    Raises:
        FileNotFoundError: If the input PDF file doesn't exist
        Exception: If conversion fails
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    if verbose:
        print(f"🔄 Converting: {pdf_path.name}")
    
    # Set up output directory
    if output_dir is None:
        output_dir = pdf_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate output filename
    output_filename = pdf_path.stem + ".md"
    output_path = output_dir / output_filename
    
    try:
        # Initialize converter
        converter = setup_converter()
        
        # Convert the document
        if verbose:
            print(f"   Processing PDF...")
        result = converter.convert(str(pdf_path))
        
        # Export to markdown
        markdown_content = result.document.export_to_markdown()
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        if verbose:
            print(f"✅ Successfully converted to: {output_path}")
            print(f"   Output size: {len(markdown_content)} characters")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error converting {pdf_path.name}: {str(e)}", file=sys.stderr)
        raise


def batch_convert_pdfs(
    input_dir: Path,
    output_dir: Optional[Path] = None,
    verbose: bool = True
) -> list[Path]:
    """
    Convert all PDF files in a directory to Markdown format.
    
    Args:
        input_dir: Directory containing PDF files
        output_dir: Directory where markdown files will be saved (default: same as input)
        verbose: Print conversion progress messages
        
    Returns:
        list[Path]: List of paths to generated markdown files
        
    Raises:
        NotADirectoryError: If input_dir is not a directory
    """
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {input_dir}")
    
    # Find all PDF files
    pdf_files = list(input_dir.glob("*.pdf")) + list(input_dir.glob("*.PDF"))
    
    if not pdf_files:
        print(f"⚠️  No PDF files found in: {input_dir}")
        return []
    
    if verbose:
        print(f"📁 Found {len(pdf_files)} PDF file(s) in {input_dir}")
        print("=" * 70)
    
    # Convert each PDF
    output_paths = []
    success_count = 0
    fail_count = 0
    
    for i, pdf_path in enumerate(pdf_files, 1):
        if verbose:
            print(f"\n[{i}/{len(pdf_files)}]")
        
        try:
            output_path = convert_pdf_to_markdown(pdf_path, output_dir, verbose)
            output_paths.append(output_path)
            success_count += 1
        except Exception as e:
            fail_count += 1
            if verbose:
                print(f"   Skipping due to error: {e}")
    
    # Summary
    if verbose:
        print("\n" + "=" * 70)
        print(f"📊 Conversion Summary:")
        print(f"   ✅ Successful: {success_count}")
        print(f"   ❌ Failed: {fail_count}")
        print(f"   📝 Total: {len(pdf_files)}")
    
    return output_paths


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Convert PDF files to Markdown format using Docling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single PDF
  %(prog)s document.pdf
  
  # Convert single PDF with custom output directory
  %(prog)s document.pdf --output ./markdown_files
  
  # Convert all PDFs in a directory
  %(prog)s ./pdfs --batch --output ./markdown_files
  
  # Quiet mode (minimal output)
  %(prog)s document.pdf --quiet
        """
    )
    
    parser.add_argument(
        "input",
        type=str,
        help="Path to input PDF file or directory"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output directory for markdown files (default: same as input)"
    )
    
    parser.add_argument(
        "-b", "--batch",
        action="store_true",
        help="Batch mode: convert all PDFs in the input directory"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet mode: minimal output"
    )
    
    args = parser.parse_args()
    
    # Convert paths
    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve() if args.output else None
    verbose = not args.quiet
    
    # Validate input
    if not input_path.exists():
        print(f"❌ Error: Input path does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        if args.batch or input_path.is_dir():
            # Batch conversion mode
            batch_convert_pdfs(input_path, output_dir, verbose)
        else:
            # Single file conversion mode
            if not input_path.suffix.lower() == '.pdf':
                print(f"❌ Error: Input file must be a PDF: {input_path}", file=sys.stderr)
                sys.exit(1)
            convert_pdf_to_markdown(input_path, output_dir, verbose)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Conversion interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
