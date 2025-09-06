Make prompts produce more precision‑leaning variants (without hurting recall) Add two small blocks to your prompt (no manual query edits; the model generates them):

Variation grid (micro‑variants)

In the OUTPUT for PubMed, request 6 micro‑variants per strategy (single‑line, paste‑ready):
V1: add humans + English filters.
V2: require RCT signals in [tiab].
V3: narrow sleep block (insomnia|“sleep disturbance”|“sleep quality”, not sleep*).
V4: use [Mesh:NoExp] on very broad headings.
V5: title emphasis for MS or trial (e.g., “multiple sclerosis”[ti] OR trial[ti]).
V6: exclude case reports/editorials.
Require a one‑sentence rationale and “expected recall delta: none|minimal”.
Keep a “Recall Lock” clause (MS + sleep + RCT concept must remain) so recall isn’t broken.
Recall lock + precision knobs

Ask the model to output:
Recall_Lock: the minimal invariant clause that preserves coverage (MS + sleep + RCT).
Precision_Knobs list: humans/lang, title‑emphasis, Mesh:NoExp, exclude case reports, narrower sleep.
Generate 5 PubMed variants by toggling at most 2 knobs each; label knobs_on, rationale, expected_recall_delta.
In PRESS, select the top‑3 precision variants to append to queries.txt.
Diversity across runs (why you see the same results)

If your runner allows, increase sampling diversity (temperature 0.7–0.9, top_p 0.9–0.95) and vary seed per run.
Add a “Diversity” instruction to your prompt:
“When rerun without changes, produce a different set of variants by toggling different precision knobs (avoid exact duplicates; ensure ≥30% token difference).”
Include a run_id/nonce in the prompt header (e.g., current timestamp) so the model explores a different path while keeping constraints.