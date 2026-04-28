#!/usr/bin/env python3
"""
Generate retrieval comparison table and figure.

Compares the number of articles retrieved in the original systematic review paper
versus the number retrieved by the LLM-generated queries (combined 4 databases,
AFTER deduplication across all 6 queries).

Deduplication counts come from the aggregation strategy 'precision_gated_union'
(= union of all 6 queries, deduplicated by DOI/PMID), and 'consensus_k2'
(= articles found by at least 2 of the 6 queries).

Also shows per-query raw counts (each query's individual result set, already
deduped across the 4 databases for that single query but NOT cross-query deduped).

Outputs (all in cross_study_validation/reports/):
  - retrieval_comparison.csv
  - retrieval_comparison.md
  - figures/retrieval_comparison_bars.png
  - figures/retrieval_comparison_heatmap.png
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

# ── Hard-coded original paper retrieval counts (from paper markdown/text) ──────
# These are the counts reported in the published paper (typically pre-dedup total
# across all databases used in the original search).
PAPER_COUNTS = {
    "ai_2022":                 4902,   # "Of the 4902 identified articles..."
    "Godos_2024":              2255,   # "Out of the initial 2255 potential articles..."
    "lang_2024":               4582,   # "A total of 4582 articles were retrieved..."
    "Lehner_2022":             2204,   # Original paper retrieval count from the extracted paper text
    "Li_2024":                 1179,   # "A total of 1,179 articles were initially identified..."
    "Medeiros_2023":           2724,   # "We obtained 2,724 results..."
    "Nexha_2024":               575,   # "This search yielded a total of 575 articles..."
    "Riedy_2021":               564,   # "A total of 564 articles were identified..."
    "Cid-Verdejo_2024_Paper":  3233,   # "Overall, 3233 papers were identified..."
    "Varallo_2022":            6262,   # post-dedup count reported: "composed of 6262 records"
}

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR  = BASE_DIR / "cross_study_validation" / "data"
OUT_DIR   = BASE_DIR / "cross_study_validation" / "reports"
FIG_DIR   = OUT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

NUM_QUERIES = 6
QUERY_LABELS = [f"Q{i+1}" for i in range(NUM_QUERIES)]


def fmt(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "N/A"
    return f"{int(v):,}"


# ── Load data from JSON files ──────────────────────────────────────────────────
rows = []
for study_id, paper_count in PAPER_COUNTS.items():
    json_path = DATA_DIR / f"{study_id}.json"
    if not json_path.exists():
        print(f"  WARNING: {json_path} not found, skipping.")
        continue
    data = json.loads(json_path.read_text())

    # Per-query raw counts (each query, 4 DBs combined, intra-query deduped only)
    qp = data.get("query_performance", [])
    query_counts = [q["results_count"] for q in qp]
    while len(query_counts) < NUM_QUERIES:
        query_counts.append(None)

    # Post-dedup totals from aggregation strategies
    strats = {s["name"]: s for s in data.get("aggregation_strategies", [])}
    union_count = strats["precision_gated_union"]["retrieved_count"] \
        if "precision_gated_union" in strats else None
    consensus_count = strats["consensus_k2"]["retrieved_count"] \
        if "consensus_k2" in strats else None

    row = {
        "study":          study_id,
        "paper_original": paper_count,
        "union_deduped":  union_count,    # all unique articles across all 6 queries
        "consensus_k2":   consensus_count, # articles in ≥2 queries
    }
    for i, cnt in enumerate(query_counts[:NUM_QUERIES]):
        row[QUERY_LABELS[i]] = cnt
    rows.append(row)

df = pd.DataFrame(rows).set_index("study")

# ── 1. Save CSV ────────────────────────────────────────────────────────────────
csv_path = OUT_DIR / "retrieval_comparison.csv"
df.to_csv(csv_path)
print(f"Saved CSV: {csv_path}")

# ── 2. Save Markdown table ─────────────────────────────────────────────────────
md_lines = [
    "# Retrieval Comparison: Original Paper vs LLM-Generated Queries",
    "",
    "## Column definitions",
    "",
    "- **paper_original** — articles retrieved in the published systematic review (pre-dedup",
    "  total across all databases as reported in the paper).",
    "- **union_deduped** — unique articles retrieved by all 6 LLM queries combined, after",
    "  deduplication across queries and databases (`precision_gated_union` strategy).",
    "- **consensus_k2** — articles found by ≥2 of the 6 LLM queries (higher precision subset).",
    "- **Q1–Q6** — raw per-query counts: each individual query result across 4 databases",
    "  (PubMed, Scopus, Web of Science, Embase), deduped within that query only.",
    "  Articles can appear in multiple queries — do NOT sum these.",
    "",
    "| Study | Paper Original | Union (deduped) | Consensus k≥2 | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 |",
    "|-------|---------------:|----------------:|--------------:|---:|---:|---:|---:|---:|---:|",
]
for study, row in df.iterrows():
    cols = [
        fmt(row["paper_original"]),
        fmt(row["union_deduped"]),
        fmt(row["consensus_k2"]),
    ] + [fmt(row[q]) for q in QUERY_LABELS]
    md_lines.append(f"| {study} | " + " | ".join(cols) + " |")

md_lines += [
    "",
    "> **Lehner_2022**: original paper retrieval count is 2,204.",
    "> **Varallo_2022**: original count (6,262) is post-dedup as reported; pre-dedup total not stated.",
    "> **Note on Q1–Q6**: these are per-query raw counts and overlap significantly across queries.",
    ">  Use `union_deduped` for the true total unique retrieval across all 6 queries.",
]
md_path = OUT_DIR / "retrieval_comparison.md"
md_path.write_text("\n".join(md_lines))
print(f"Saved Markdown: {md_path}")

# ── 3. Bar chart: original vs union (deduped) vs consensus ─────────────────────
studies = df.index.tolist()
n = len(studies)
x = np.arange(n)
width = 0.25

fig, ax = plt.subplots(figsize=(16, 7))

# Three bars per study
orig_vals  = [df.loc[s, "paper_original"]  if pd.notna(df.loc[s, "paper_original"])  else 0 for s in studies]
union_vals = [df.loc[s, "union_deduped"]   if pd.notna(df.loc[s, "union_deduped"])   else 0 for s in studies]
cons_vals  = [df.loc[s, "consensus_k2"]    if pd.notna(df.loc[s, "consensus_k2"])    else 0 for s in studies]

bars_orig  = ax.bar(x - width, orig_vals,  width, label="Original Paper",      color="#4472C4", alpha=0.85, edgecolor="white")
bars_union = ax.bar(x,          union_vals, width, label="LLM Union (deduped)", color="#ED7D31", alpha=0.85, edgecolor="white")
bars_cons  = ax.bar(x + width,  cons_vals,  width, label="LLM Consensus k≥2",  color="#A9D18E", alpha=0.85, edgecolor="white")

# Mark studies where paper_original is N/A
for xi, s in zip(x, studies):
    if pd.isna(df.loc[s, "paper_original"]):
        ax.text(xi - width, 200, "N/A", ha="center", va="bottom", fontsize=7,
                color="gray", style="italic")

ax.set_xticks(x)
ax.set_xticklabels([s.replace("_", "\n") for s in studies], fontsize=9)
ax.set_ylabel("Retrieved Articles (unique, after deduplication)", fontweight="bold")
ax.set_title(
    "Retrieved Articles: Original Paper  vs  LLM Queries (all 6 queries, 4 databases, deduplicated)",
    fontweight="bold", pad=15
)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.grid(axis="y", alpha=0.3, linestyle="--")
ax.set_axisbelow(True)
ax.legend(loc="upper right", framealpha=0.9, fontsize=10)

plt.tight_layout()
bar_path = FIG_DIR / "retrieval_comparison_bars.png"
plt.savefig(bar_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"Saved figure: {bar_path}")

# ── 4. Heatmap: ratio = union_deduped / paper_original ────────────────────────
ratio_vals = []
for s in studies:
    orig  = df.loc[s, "paper_original"]
    union = df.loc[s, "union_deduped"]
    if pd.notna(orig) and orig > 0 and pd.notna(union):
        ratio_vals.append(union / orig)
    else:
        ratio_vals.append(np.nan)

ratio_series = pd.Series(ratio_vals, index=studies)

fig2, axes = plt.subplots(1, 2, figsize=(16, 6),
                           gridspec_kw={"width_ratios": [1, 1.4]})

# Left: ratio bar chart
colors_ratio = ["#ED7D31" if pd.notna(v) else "#CCCCCC" for v in ratio_vals]
mask_nan = [pd.isna(v) for v in ratio_vals]
plot_vals = [v if not np.isnan(v) else 0 for v in ratio_vals]
axes[0].barh(range(n), plot_vals, color=colors_ratio, alpha=0.85, edgecolor="white")
axes[0].axvline(x=1.0, color="black", linewidth=1.5, linestyle="--", label="1:1 reference")
for yi, (v, s) in enumerate(zip(ratio_vals, studies)):
    if pd.notna(v):
        axes[0].text(v + 0.02, yi, f"{v:.2f}×", va="center", fontsize=8)
    else:
        axes[0].text(0.05, yi, "N/A", va="center", fontsize=8, color="gray", style="italic")
axes[0].set_yticks(range(n))
axes[0].set_yticklabels([s.replace("_", "\n") for s in studies], fontsize=8)
axes[0].set_xlabel("LLM Union (deduped) / Original Paper", fontweight="bold")
axes[0].set_title("Retrieval Ratio\n(>1 = LLM retrieved more; <1 = fewer)", fontweight="bold")
axes[0].legend(fontsize=9)
axes[0].grid(axis="x", alpha=0.3, linestyle="--")

# Right: absolute counts table
col_labels = ["Paper\nOriginal", "Union\n(deduped)", "Consensus\nk≥2"] + QUERY_LABELS
table_data = []
for s in studies:
    r = [
        fmt(df.loc[s, "paper_original"]),
        fmt(df.loc[s, "union_deduped"]),
        fmt(df.loc[s, "consensus_k2"]),
    ] + [fmt(df.loc[s, q]) for q in QUERY_LABELS]
    table_data.append(r)

axes[1].axis("off")
tbl = axes[1].table(
    cellText=table_data,
    rowLabels=[s.replace("_2", "\n_2").replace("_Paper", "\nPaper") for s in studies],
    colLabels=col_labels,
    cellLoc="right",
    loc="center",
    bbox=[0, 0, 1, 1]
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(7.5)
for (r, c), cell in tbl.get_celld().items():
    if r == 0 or c == -1:
        cell.set_text_props(fontweight="bold")
    if r > 0 and c in (0, 1, 2):   # highlight main comparison columns
        cell.set_facecolor("#F2F2F2")
    cell.set_edgecolor("lightgray")
axes[1].set_title("Absolute Counts\n(Q1–Q6 are per-query, overlap — do not sum)", fontweight="bold", pad=10)

plt.suptitle("Retrieval Coverage: Original Paper vs LLM-Generated Queries (deduplicated)",
             fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
heat_path = FIG_DIR / "retrieval_comparison_heatmap.png"
plt.savefig(heat_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"Saved figure: {heat_path}")

# ── 5. Faceted per-query comparison ───────────────────────────────────────────
# One panel per study: Q1–Q6 bars + reference lines for paper_original & union
# Makes it clear how each individual LLM query compares to the paper's total.
#
# Color coding:
#   Bars   Q1–Q6     : blue gradient (distinct per query, consistent across panels)
#   Line   Paper     : solid dark-blue  (the target to match)
#   Line   Union     : dashed orange    (what all 6 queries achieve together)

QUERY_COLORS = ["#4E79A7", "#59A14F", "#F28E2B", "#E15759", "#76B7B2", "#B07AA1"]

ncols = 5
nrows = int(np.ceil(n / ncols))

fig3, axes3 = plt.subplots(nrows, ncols, figsize=(ncols * 3.8, nrows * 4.2),
                            sharey=False)
axes3 = axes3.flatten()

for idx, study in enumerate(studies):
    ax = axes3[idx]
    q_vals    = [df.loc[study, q] if pd.notna(df.loc[study, q]) else 0 for q in QUERY_LABELS]
    paper_val = df.loc[study, "paper_original"] if pd.notna(df.loc[study, "paper_original"]) else None
    union_val = df.loc[study, "union_deduped"]  if pd.notna(df.loc[study, "union_deduped"])  else None

    ax.bar(QUERY_LABELS, q_vals, color=QUERY_COLORS, alpha=0.88, edgecolor="white", width=0.6)

    legend_handles = []
    if paper_val is not None:
        line_p = ax.axhline(paper_val, color="#1F3864", linewidth=2.0, linestyle="-",
                            label=f"Paper ({fmt(paper_val)})")
        legend_handles.append(line_p)
    if union_val is not None:
        line_u = ax.axhline(union_val, color="#ED7D31", linewidth=2.0, linestyle="--",
                            label=f"Union Q1–Q6 ({fmt(union_val)})")
        legend_handles.append(line_u)

    ceiling = max(q_vals + [paper_val or 0, union_val or 0, 1])
    ax.set_ylim(0, ceiling * 1.24)

    # Value labels on bars
    label_offset = max(ceiling * 0.015, 18)
    for bar_idx, (bar_x, bar_y) in enumerate(zip(QUERY_LABELS, q_vals)):
        if bar_y > 0:
            ax.text(
                bar_idx,
                bar_y + label_offset,
                f"{int(bar_y):,}",
                ha="center",
                va="bottom",
                fontsize=7.5,
                fontweight="semibold",
                color="black",
                clip_on=False,
                bbox={
                    "boxstyle": "round,pad=0.18",
                    "facecolor": "white",
                    "edgecolor": "none",
                    "alpha": 0.9,
                },
            )

    ax.set_title(study.replace("_Paper", "").replace("_", "\n"), fontsize=8.5, fontweight="bold")
    ax.set_ylabel("Articles" if idx % ncols == 0 else "", fontsize=8)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(
        lambda v, _: f"{int(v/1000)}k" if v >= 1000 else f"{int(v)}"))
    ax.tick_params(axis="both", labelsize=7.5)
    ax.grid(axis="y", alpha=0.3, linestyle=":")
    ax.set_axisbelow(True)
    if legend_handles:
        ax.legend(handles=legend_handles, fontsize=6.0, loc="upper right",
                  framealpha=0.85, handlelength=1.5)

# Hide unused subplot panels
for idx in range(n, len(axes3)):
    axes3[idx].set_visible(False)

# Shared legend explanation at the bottom
legend_patches = [
    Patch(facecolor=QUERY_COLORS[i], alpha=0.88, label=f"Q{i+1} (benchmark, title+PMID+DOI deduped)")
    for i in range(NUM_QUERIES)
]
legend_patches += [
    Line2D([0], [0], color="#1F3864", linewidth=2.0, linestyle="-",  label="Paper Original (reported total)"),
    Line2D([0], [0], color="#ED7D31", linewidth=2.0, linestyle="--", label="LLM Union Q1–Q6 (aggregates pipeline, PMID/DOI only)"),
]
fig3.legend(handles=legend_patches, loc="lower center", ncol=4, fontsize=8,
            bbox_to_anchor=(0.5, -0.04), framealpha=0.9,
            title="Each bar = one individual LLM query across 4 databases  |  Lines = reference counts",
            title_fontsize=8)

fig3.suptitle(
    "Per-Query Retrieval vs Paper Original  (Q1–Q6 individual queries)\n"
    "Bars: benchmark pipeline (title + PMID + DOI)  |  Lines: paper total and union of all 6 queries",
    fontsize=11, fontweight="bold", y=1.01
)
plt.tight_layout(rect=[0, 0.04, 1, 1])
query_path = FIG_DIR / "retrieval_comparison_queries.png"
fig3.savefig(query_path, dpi=300, bbox_inches="tight")
plt.close(fig3)
print(f"Saved figure: {query_path}")

print("\nDone.")
