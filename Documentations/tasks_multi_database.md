# Multi-Database Feature Tasks

This checklist breaks the roadmap into actionable work items. Each task should leave the workflow in a runnable state for the existing PubMed-only studies while incrementally enabling Scopus support and the shared multi-provider pipeline.

## 1. Query Specification & Prompt Workflow

1.1 Document the new multi-database query format (e.g., Markdown sections with fenced code for PubMed / Scopus) and update the README + study template instructions.  
1.2 Update the `/generate_prompt` tooling so the LLM prompt explicitly requests per-database query blocks and emits the documented structure.  
1.3 Extend the parser that ingests `studies/<name>/queries.txt` (or `.md`) to extract each provider block, validate required sections, and surface actionable lint messages when sections are missing or malformed.  
1.4 Add provider-specific query validators (at least for PubMed + Scopus) that flag unsupported syntax before any API call.

## 2. Provider Registry & Configuration Layer

2.1 Define a provider registry (`REGISTRY = {"pubmed": PubMedProvider, "scopus": ScopusProvider}`) plus helper logic that instantiates providers based on CLI/env/config selections.  
2.2 Extend `sr_config.toml` schema (and README docs) with `[databases]` configuration, including defaults, provider-specific credential blocks, and environment-variable interpolation.  
2.3 Add CLI flags (`--databases`, `--scopus-api-key`, etc.) and merge rules so CLI > env > config precedence continues to hold, with clear messages when a requested provider is disabled or missing credentials.  
2.4 Update workflow scripts (e.g., `run_workflow_sleep_apnea.sh`) to optionally accept a `DATABASES` override while keeping current behavior unchanged if the variable is unset.

## 3. Scopus Provider Implementation

3.1 Research and choose the Python client/library (e.g., `pybliometrics`/`scopus`) that fits licensing constraints; document installation steps in `environment.yml`.  
3.2 Implement `ScopusProvider` with authentication, pagination, and rate-limiting that mirror the PubMed provider contract, returning DOIs + native IDs per query.  
3.3 Provide a mock/fallback mode (environment toggle) that returns deterministic sample data for CI/testing when real credentials are unavailable.  
3.4 Write unit tests covering happy path, pagination, and auth failure handling using mocked responses.

## 4. Result Normalization & Deduplication

4.1 Build a normalization module that accepts multiple provider outputs and produces a unified record list containing `{doi, provider_ids, metadata}` plus provenance details.  
4.2 Implement DOI fallback logic: PMID→DOI lookups (Entrez), title/year heuristics, and hooks for Crossref/Unpaywall lookups, ensuring retries/rate limits are respected.  
4.3 Add deduplication routines that merge records sharing a DOI or matching fallback heuristics, preserving the list of contributing providers for reporting.  
4.4 Integrate the normalization pipeline into `select_without_gold` and `score_queries`, ensuring downstream code still receives the PMIDs it expects while gaining DOI awareness.  
4.5 Emit debugging artifacts (e.g., `dedup_details.json`) so study leads can inspect how duplicates were resolved.

## 5. Workflow & UX Updates

5.1 Update CLI output and logs to show per-provider counts, elapsed time, and any skipped queries, so users can verify both PubMed and Scopus ran.  
5.2 Adjust `details_*.json`/`sealed_*.json` schemas to include provider provenance and normalized identifiers; add a migration note for older scripts that parse these files.  
5.3 Refresh README snippets, `run_workflow_*.sh`, and sample study folders to demonstrate a mixed `pubmed,scopus` run while clearly documenting how to stay PubMed-only.

## 6. Testing & Validation

6.1 Add automated tests for the query parser/validator, provider registry, and normalization/dedup modules.  
6.2 Record integration fixtures (where licensing allows) for PubMed + Scopus queries to run in CI without live API calls; otherwise, wire up injectable stubs.  
6.3 Manually verify at least one study end-to-end with `--databases pubmed,scopus`, logging findings and any manual steps that still need automation.  
6.4 Create troubleshooting docs covering common failure modes (missing credentials, invalid queries, rate limiting) and recommended resolutions.

## 7. Future Database Hooks

7.1 Define the checklist for onboarding the next provider (Web of Science, Embase) so future contributions follow the same process: query format requirements, credential setup, provider implementation, and tests.  
7.2 Track open questions (licensing, API quotas, normalization quirks) for each upcoming provider in a separate section so they can be resolved before implementation begins.

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
