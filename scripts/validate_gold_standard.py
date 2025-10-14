import pandas as pd
import argparse
import os
import sys

def validate_and_clean_gold_standard(file_path: str):
    """
    Validates a gold standard CSV file.

    Checks for a 'pmid' column, cleans it by keeping only valid numeric PMIDs,
    and overwrites the file with a clean, single-column version.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'", file=sys.stderr)
        sys.exit(1)

    try:
        df = pd.read_csv(file_path, dtype=str)
    except Exception as e:
        print(f"Error: Could not read CSV file. Reason: {e}", file=sys.stderr)
        sys.exit(1)

    original_rows = len(df)
    
    # Find the pmid column, case-insensitive
    pmid_col = None
    for col in df.columns:
        if col.strip().lower() == 'pmid':
            pmid_col = col
            break
            
    if pmid_col is None:
        print(f"Error: Required 'pmid' column not found in '{file_path}'", file=sys.stderr)
        print(f"Available columns: {list(df.columns)}", file=sys.stderr)
        sys.exit(1)

    # Clean up the PMIDs
    # 1. Convert to string and strip whitespace
    pmids = df[pmid_col].astype(str).str.strip()
    
    # 2. Keep only rows that match a pure digit regex and are not empty
    valid_mask = pmids.str.match(r'^\d+$').fillna(False)
    valid_pmids = pmids[valid_mask]
    
    kept_rows = len(valid_pmids)
    dropped_rows = original_rows - kept_rows

    # Create a new clean DataFrame
    cleaned_df = pd.DataFrame({'pmid': valid_pmids})

    # Overwrite the original file
    try:
        cleaned_df.to_csv(file_path, index=False)
    except Exception as e:
        print(f"Error: Could not write cleaned file. Reason: {e}", file=sys.stderr)
        sys.exit(1)

    print("--- Gold Standard Validation Report ---")
    print(f"File processed: {file_path}")
    print(f"Found {original_rows} total rows.")
    print(f"Kept {kept_rows} valid PMIDs.")
    print(f"Removed {dropped_rows} invalid or empty rows.")
    print("File has been successfully cleaned and overwritten.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate and clean a gold standard PMID CSV file."
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to the gold standard CSV file to validate."
    )
    args = parser.parse_args()
    validate_and_clean_gold_standard(args.file)