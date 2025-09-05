
from Bio import Entrez
import os

# Use environment variables for email and API key, with a default email.
Entrez.email = os.getenv("NCBI_EMAIL", "default@example.com")
Entrez.api_key = os.getenv("NCBI_API_KEY", None)

print(f"Attempting to connect to NCBI with email: {Entrez.email}")

# The MeSH term to validate
term_to_validate = '"Adult"[mh]'

print(f"Attempting to validate MeSH term: {term_to_validate}")

try:
    # Perform the search in the MeSH database
    handle = Entrez.esearch(db="mesh", term=term_to_validate)
    record = Entrez.read(handle)
    handle.close()
    
    # Check if the search returned any results
    if int(record.get('Count', 0)) > 0:
        print("SUCCESS: Successfully connected to NCBI and validated the term.")
        print(f"Result: {record}")
    else:
        print("FAILURE: Connected to NCBI, but the term was not found or is invalid.")
        print(f"Result: {record}")

except Exception as e:
    print("FAILURE: An error occurred during the connection or validation process.")
    print(f"Error: {e}")
