# Multi-Database Feature Tasks                                                                                                   
                                                                                                                                 
This checklist breaks the roadmap into actionable work items. Each task should leave the workflow in a runnable state for the exi
sting PubMed-only studies while incrementally enabling Scopus support and the shared multi-provider pipeline.                    
                                                                                                                                 
**Progress Summary**:                                                                                                            
- ✅ Core multi-database infrastructure complete (Sections 2, 3, 4 - partially, 5)                                                
- 🚧 Query generation workflow needs LLM integration (Section 1)                                                                  
- 📋 Testing & validation in progress (Section 6)                                                                                 
                                                                                                                                 
## 1. Query Specification & Prompt Workflow                                                                                      
                                                                                                                                 
- [ ] 1.1 Document the new multi-database query format (e.g., Markdown sections with fenced code for PubMed / Scopus) and update 
the README + study template instructions.                                                                                        
- [ ] 1.2 Update the `/generate_prompt` tooling so the LLM prompt explicitly requests per-database query blocks and emits the doc
umented structure.                                                                                                               
- [ ] 1.3 Extend the parser that ingests `studies/<name>/queries.txt` (or `.md`) to extract each provider block, validate require
d sections, and surface actionable lint messages when sections are missing or malformed.                                         
- [ ] 1.4 Add provider-specific query validators (at least for PubMed + Scopus) that flag unsupported syntax before any API call.
                                                                                                                                 
**Note**: Currently using manual provider-specific query files (e.g., `queries_scopus.txt`). Automated LLM generation is pending.
                                                                                                                                 
## 2. Provider Registry & Configuration Layer ✅                                                                                  
                                                                                                                                 
- [x] 2.1 Define a provider registry (`REGISTRY = {"pubmed": PubMedProvider, "scopus": ScopusProvider}`) plus helper logic that i
nstantiates providers based on CLI/env/config selections.                                                                        
- [x] 2.2 Extend `sr_config.toml` schema (and README docs) with `[databases]` configuration, including defaults, provider-specifi
c credential blocks, and environment-variable interpolation.                                                                     
- [x] 2.3 Add CLI flags (`--databases`, `--scopus-api-key`, etc.) and merge rules so CLI > env > config precedence continues to h
old, with clear messages when a requested provider is disabled or missing credentials.                                           
- [x] 2.4 Update workflow scripts (e.g., `run_workflow_sleep_apnea.sh`) to optionally accept a `DATABASES` override while keeping
 current behavior unchanged if the variable is unset.                                                                            
                                                                                                                                 
**Status**: Complete. `PROVIDER_REGISTRY` in `search_providers.py`, full config support in `sr_config.toml`, CLI precedence worki
ng.                                                                                                                              
                                                                                                                                 
## 3. Scopus Provider Implementation ✅                                                                                           
                                                                                                                                 
- [x] 3.1 Research and choose the Python client/library (e.g., `pybliometrics`/`scopus`) that fits licensing constraints; documen
t installation steps in `environment.yml`.                                                                                       
- [x] 3.2 Implement `ScopusProvider` with authentication, pagination, and rate-limiting that mirror the PubMed provider contract,
 returning DOIs + native IDs per query.                                                                                          
- [x] 3.3 Provide a mock/fallback mode (environment toggle) that returns deterministic sample data for CI/testing when real crede
ntials are unavailable.                                                                                                          
- [ ] 3.4 Write unit tests covering happy path, pagination, and auth failure handling using mocked responses.                    
                                                                                                                                 
**Status**: Core implementation complete. Uses `requests` directly with Scopus Search API. Date filter fix implemented (PUBYEAR >
 X AND < Y). Unit tests pending.                                                                                                 
                                                                                                                                 
## 4. Result Normalization & Deduplication 🚧                                                                                     
                                                                                                                                 
- [x] 4.1 Build a normalization module that accepts multiple provider outputs and produces a unified record list containing `{doi
, provider_ids, metadata}` plus provenance details.                                                                              
- [x] 4.2 Implement DOI fallback logic: PMID→DOI lookups (Entrez), title/year heuristics, and hooks for Crossref/Unpaywall lookup
s, ensuring retries/rate limits are respected.                                                                                   
- [x] 4.3 Add deduplication routines that merge records sharing a DOI or matching fallback heuristics, preserving the list of con
tributing providers for reporting.                                                                                               
- [x] 4.4 Integrate the normalization pipeline into `select_without_gold` and `score_queries`, ensuring downstream code still rec
eives the PMIDs it expects while gaining DOI awareness.                                                                          
- [x] 4.5 Emit debugging artifacts (e.g., `dedup_details.json`) so study leads can inspect how duplicates were resolved.         
                                                                                                                                 
**Status**: Option A (DOI-based deduplication) implemented in `_execute_query_bundle()`. Full Article dataclass + Option B (title
/year fuzzy matching) documented for future. Gold standard enhancement script (`enhance_gold_standard.py`) created and tested. Se
e `Documentations/multi_database_deduplication_complete.md` for details.                                                         
                                                                                                                                 
## 5. Workflow & UX Updates ✅                                                                                                    
                                                                                                                                 
- [x] 5.1 Update CLI output and logs to show per-provider counts, elapsed time, and any skipped queries, so users can verify both
 PubMed and Scopus ran.                                                                                                          
- [x] 5.2 Adjust `details_*.json`/`sealed_*.json` schemas to include provider provenance and normalized identifiers; add a migrat
ion note for older scripts that parse these files.                                                                               
- [x] 5.3 Refresh README snippets, `run_workflow_*.sh`, and sample study folders to demonstrate a mixed `pubmed,scopus` run while
 clearly documenting how to stay PubMed-only.                                                                                    
                                                                                                                                 
**Status**: Complete. Logs show deduplication stats with percentages. JSON schemas include `provider_details` with per-provider q
ueries, counts, and IDs. README has multi-database workflow section.                                                             
                                                                                                                                 
## 6. Testing & Validation 🚧                                                                                                     
                                                                                                                                 
- [ ] 6.1 Add automated tests for the query parser/validator, provider registry, and normalization/dedup modules.                
- [ ] 6.2 Record integration fixtures (where licensing allows) for PubMed + Scopus queries to run in CI without live API calls; o
therwise, wire up injectable stubs.                                                                                              
- [x] 6.3 Manually verify at least one study end-to-end with `--databases pubmed,scopus`, logging findings and any manual steps t
hat still need automation.                                                                                                       
- [x] 6.4 Create troubleshooting docs covering common failure modes (missing credentials, invalid queries, rate limiting) and rec
ommended resolutions.                                                                                                            
                                                                                                                                 
**Status**: Manual validation complete (sleep apnea study with PubMed + Scopus). Troubleshooting documented in README. Automated 
tests pending.                                                                                                                   
                                                                                                                                 
## 7. Future Database Hooks ✅                                                                                                    
                                                                                                                                 
- [x] 7.1 Define the checklist for onboarding the next provider (Web of Science, Embase) so future contributions follow the same 
process: query format requirements, credential setup, provider implementation, and tests.                                        
- [x] 7.2 Track open questions (licensing, API quotas, normalization quirks) for each upcoming provider in a separate section so 
they can be resolved before implementation begins.                                                                               
                                                                                                                                 
**Status**: Complete. Architecture is database-agnostic. `multi_database_deduplication_complete.md` includes "Adding New Database
s" section with step-by-step instructions.                                                                                       
                                                                                                                                 
## 8. Future Enhancements                                                                                                        
                                                                                                                                 
8.1 **Gold Standard Enhancement Integration** - Integrate `enhance_gold_standard.py` into study setup workflow:                  
    - Script location: `scripts/enhance_gold_standard.py` (completed)                                                            
    - Usage: Run once during study setup after creating gold PMID list                                                           
    - Command: `python scripts/enhance_gold_standard.py studies/<study>/gold_pmids.csv studies/<study>/gold_pmids_with_doi.csv`  
    - Add optional step to `scaffold` command to prompt for DOI enhancement                                                      
    - Update `load_gold_pmids()` to prefer DOI-enhanced version if available (currently reads both formats)                      
    - Document usage in README for study initialization                                                                          
    - Enable DOI-based matching for Scopus-only articles in gold standard                                                        
                                                                                                                                 
8.2 **Hybrid Deduplication (Option B)** - Implement comprehensive deduplication for articles without DOIs:                       
    - Current status: Using DOI-only deduplication (Option A implemented) - handles 96% perfectly                                
    - Add title/year fuzzy matching for the ~6% of articles lacking DOIs                                                         
    - Use difflib.SequenceMatcher with 90% similarity threshold                                                                  
    - Require year match in addition to title similarity                                                                         
    - Expected impact: Eliminate ~1-2 potential duplicates in typical studies                                                    
    - Priority: Low - edge case affects <0.5% of results in practice                                                             
    - Reference: See `multi_database_edge_cases_analysis.md` for complete algorithm specification                                
    - Decision: Deferred based on cost/benefit analysis showing minimal real-world impact

## 9. Dynamic Multi-Database Query Generation

This section details the implementation of a unified, "run-once" workflow for generating balanced and tailored search queries across multiple databases.

- [ ] **9.1 Create Centralized Database Guidelines File**
  - **Description:** Create a new file `prompts/database_guidelines.md`. This file will act as a centralized, machine-readable repository for database-specific querying syntax, controlled vocabularies, and precision-tuning "knobs". This modular approach allows for easy maintenance and expansion of database-specific rules without altering the core prompt logic.
  - **Acceptance Criteria:** The file exists and contains well-structured Markdown sections for at least PubMed, Scopus, and Embase, with subsections for `Syntax`, `Controlled Vocabulary`, and `Precision_Knobs`.

- [ ] **9.2 Develop a New Multi-Database Prompt Template**
  - **Description:** Create a new prompt template, `prompts/prompt_template_multidb.md`. This template will instruct the LLM to perform a multi-database query generation. It will be designed to accept dynamically injected guidelines and will mandate a structured JSON output for all queries, ensuring a balanced number of strategies (including micro-variants) across all specified databases.
  - **Acceptance Criteria:** The new template exists. It includes a `[DATABASE_SPECIFIC_GUIDELINES]` placeholder. Its `OUTPUT` section demands a single JSON object. Its `FINAL TASK` section instructs the agent to parse the JSON and write to multiple `queries_{db}.txt` files. The "PubMed focus" on micro-variants is removed and generalized.

- [ ] **9.3 Create a Dynamic Prompt Generation Command**
  - **Description:** Create a new Gemini command, `/generate_multidb_prompt`, defined in `.gemini/commands/generate_multidb_prompt.toml`. This command will orchestrate the entire prompt generation process. It will accept a list of target databases, read the corresponding guidelines from `prompts/database_guidelines.md`, and inject them into the `prompts/prompt_template_multidb.md` template before creating the final, runnable query-generation command.
  - **Acceptance Criteria:** The new command `/generate_multidb_prompt` is available. It accepts a `--databases` argument. Its implementation correctly reads from the guidelines file and injects the content into the new multi-database template to create a final, runnable TOML command.