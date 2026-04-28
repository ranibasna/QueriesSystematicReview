#!/bin/bash
# Prepare all studies for cross-study validation:
#   Part A – combine per-query summaries into one 6-row CSV
#   Part B – aggregate all queries into 5 combined strategy files
#   Part C – score those strategies against the gold standard
set -e

STUDIES=(
    "Godos_2024"
    "lang_2024"
    "Lehner_2022"
    "Li_2024"
    "Medeiros_2023"
    "Nexha_2024"
    "Riedy_2021"
    "Cid-Verdejo_2024_Paper"
    "Varallo_2022"
)

for STUDY in "${STUDIES[@]}"; do
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Study: $STUDY"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # ── Part A: combine per-query summaries into one file ──────────────
    TS=$(date +%Y%m%d-%H%M%S)
    COMBINED="benchmark_outputs/$STUDY/summary_combined_${TS}.csv"
    first=true
    for qdir in $(ls -d benchmark_outputs/$STUDY/query_*/ | sort); do
        latest=$(ls -t "${qdir}"summary_*.csv 2>/dev/null | grep -v per_database | head -1)
        if [ -n "$latest" ]; then
            if $first; then
                cp "$latest" "$COMBINED"
                first=false
            else
                tail -n +2 "$latest" >> "$COMBINED"
            fi
        fi
    done
    NQUERIES=$(( $(wc -l < "$COMBINED") - 1 ))
    echo "  Part A ✅  Combined summary: $NQUERIES queries → $(basename $COMBINED)"

    # ── Part B: aggregate all queries → 5 combined strategies ──────────
    latest_details=()
    for qdir in $(ls -d benchmark_outputs/$STUDY/query_*/ | sort); do
        latest=$(ls -t "${qdir}"details_*.json 2>/dev/null | head -1)
        if [ -n "$latest" ]; then
            latest_details+=("$latest")
        fi
    done
    echo "  Part B: aggregating ${#latest_details[@]} queries..."
    python scripts/aggregate_queries.py \
        --inputs "${latest_details[@]}" \
        --outdir "aggregates/$STUDY" \
        --multi-key 2>&1 | grep -E "✓|ERROR|Wrote"

    # ── Part C: score combined strategies against gold ──────────────────
    GOLD="gold_pmids_${STUDY}_detailed.csv"
    echo "  Part C: scoring strategies vs gold ($GOLD)..."
    python llm_sr_select_and_score.py \
        --study-name "$STUDY" \
        score-sets \
        --sets "aggregates/$STUDY"/*.csv \
        --gold-csv "$GOLD" \
        --outdir aggregates_eval \
        --use-multi-key 2>&1 | grep -E "Set\[|Saved:|ERROR"

    echo "  Parts B+C ✅"
done

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  All studies processed!"
echo "════════════════════════════════════════════════════════════════"
