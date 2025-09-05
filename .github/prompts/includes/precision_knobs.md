## Precision-lean variants framework (abstract)

Goal: tighten precision while preserving recall. The model must keep a Recall_Lock clause invariant and explore small precision toggles ("knobs").

### Recall_Lock (contract)
- A minimal, invariant Boolean clause that preserves coverage of the core information need across databases.
- Template (adapt per topic and DB syntax):
  - Disease/Condition block (controlled vocab + key free-text)
  - Phenotype/Outcome/Domain block (controlled vocab + curated free-text)
  - Study design block (e.g., RCT signals via publication types and/or title/abstract markers)
- Constraint: Do not remove core synonyms or the study design requirement from Recall_Lock when generating variants.

### Precision_Knobs (atomic toggles)
- Humans + Language: PubMed → NOT (animals[mh] NOT humans[mh]) AND English[lang]; platform equivalents elsewhere.
- Title emphasis: require at least one core term in the title field (e.g., disease[ti] OR trial[ti]). Use sparingly.
- Mesh/Emtree No Explode: apply NoExp to very broad headings to reduce explosion.
- Exclude publication types: NOT (case reports[pt] OR editorial[pt] OR letter[pt] OR comment[pt]). Adjust per platform.
- Narrower concept subset: replace broad wildcard with a curated subset of specific terms (e.g., replace concept* with a short list of narrower phrases).
- RCT signals in [tiab]: require randomi[sz]ed|trial|placebo in title/abstract, in addition to publication types.
- Adult population filter (optional): PubMed → NOT (child[mh] NOT adult[mh]) when appropriate.
- Field scoping (optional): [majr] for highly central concepts; use cautiously.

### Micro-variants generation
- Produce N single-line, paste-ready variants per DB (default: PubMed N=6).
- Each variant toggles ≤2 precision knobs relative to Recall_Lock.
- For each variant: label, list knobs_on, provide 1-sentence rationale, and annotate expected_recall_delta as none|minimal.

Suggested PubMed micro-variant grid (adjust labels per topic):
- V1: Humans + English filters.
- V2: Require RCT signals in [tiab].
- V3: Narrower concept block for the broadest concept.
- V4: Use [Mesh:NoExp] on very broad headings.
- V5: Title emphasis for disease or trial.
- V6: Exclude case reports/editorials/letters/comments.

### Diversity between runs
- When re-run without changes, produce different variants by toggling different knob combinations (avoid exact duplicates; ensure ≥30% token difference).
- Include a run_id/nonce (e.g., timestamp) in the prompt header to encourage alternative paths while honoring constraints.

### Output contract additions (to request from the model)
- Recall_Lock: the invariant clause (paste-ready for each DB).
- Precision_Knobs: list of available toggles for the topic with DB-specific syntax.
- Micro-variants: N labeled variants (≤2 knobs each) with rationale and expected_recall_delta.
- PRESS: select the top-3 precision-lean variants that preserve recall and append those PubMed variants to queries.txt.
