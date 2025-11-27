#!/usr/bin/env python3
"""
Quick test script for Web of Science API connectivity.
Tests basic authentication and query functionality.

Usage:
    export WOS_API_KEY="your_key_here"
    python test_wos_connection.py
    
    Or add WOS_API_KEY to your .env file
"""

import os
import sys

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, rely on environment variables

from search_providers import WebOfScienceProvider

def test_wos_connection():
    """Test WoS API with a simple query."""
    
    api_key = os.getenv("WOS_API_KEY")
    if not api_key:
        print("ERROR: WOS_API_KEY environment variable not set.")
        print("Please set it with: export WOS_API_KEY='your_key_here'")
        sys.exit(1)
    
    print(f"Testing Web of Science API...")
    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    print()
    
    try:
        # Initialize provider
        provider = WebOfScienceProvider(api_key=api_key)
        print("✓ Provider initialized successfully")
        
        # Simple test query
        test_query = 'TS=("sleep apnea" AND dementia)'
        mindate = "2020/01/01"
        maxdate = "2021/12/31"
        
        print(f"\nRunning test query: {test_query}")
        print(f"Date range: {mindate} to {maxdate}")
        print("(This will only retrieve first page for testing)")
        print()
        
        # Search with limited results
        dois, wos_uids, total = provider.search(
            query=test_query,
            mindate=mindate,
            maxdate=maxdate,
            retmax=50  # Only get first page
        )
        
        print(f"✓ Query successful!")
        print(f"\nResults:")
        print(f"  Total count: {total}")
        print(f"  DOIs retrieved: {len(dois)}")
        print(f"  WoS UIDs retrieved: {len(wos_uids)}")
        
        if dois:
            print(f"\nSample DOIs (first 3):")
            for i, doi in enumerate(list(dois)[:3], 1):
                print(f"  {i}. {doi}")
        
        if wos_uids:
            print(f"\nSample WoS UIDs (first 3):")
            for i, uid in enumerate(list(wos_uids)[:3], 1):
                print(f"  {i}. {uid}")
        
        print("\n" + "="*60)
        print("✓ WEB OF SCIENCE API CONNECTION SUCCESSFUL!")
        print("="*60)
        print("\nYou can now run the full workflow with:")
        print("  python llm_sr_select_and_score.py --databases pubmed,scopus,wos ...")
        
        return True
        
    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
        return False
    except RuntimeError as e:
        print(f"\n✗ API error: {e}")
        if "401" in str(e):
            print("\nTroubleshooting:")
            print("  1. Verify your API key is correct")
            print("  2. Check that you have WoS Starter API subscription")
            print("  3. Ensure the key hasn't expired")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_wos_connection()
    sys.exit(0 if success else 1)
