#!/bin/bash
################################################################################
# Complete Systematic Review Workflow - Universal Script
#
# Description:
#   A unified, study-agnostic workflow script that automates the complete 
#   systematic review pipeline from query execution to aggregation scoring.
#
# Usage:
#   bash scripts/run_complete_workflow.sh <STUDY_NAME> [OPTIONS]
#
# Example:
#   bash scripts/run_complete_workflow.sh ai_2022 --databases pubmed,scopus,wos
#   bash scripts/run_complete_workflow.sh sleep_apnea --skip-embase
#
# Options:
#   --databases DB1,DB2     Databases to query (default: pubmed,scopus,wos)
#   --skip-embase           Skip Embase import even if CSV files exist
#   --embase-only           Only import Embase and re-aggregate (Method 2)
#   --skip-aggregation      Skip aggregation and scoring steps
#   --multi-key             Use multi-key matching (PMID OR DOI) for improved recall
#   --query-by-query        Run full scoring+aggregation per query (1..N), sequentially
#   --query-index N         Run full scoring+aggregation for a single query index only
#   --help                  Show this help message
#
# Prerequisites:
#   studies/<STUDY_NAME>/
#     ├── queries.txt              # PubMed queries (required)
#     ├── queries_scopus.txt       # Scopus queries (if using Scopus)
#     ├── queries_wos.txt          # WOS queries (if using WOS)
#     ├── queries_embase.txt       # Embase queries (if using Embase)
#     ├── gold_pmids_<STUDY>.csv   # Gold standard (required)
#     └── embase_manual_queries/   # Embase CSV exports (optional)
#         ├── embase_query1.csv
#         ├── embase_query2.csv
#         └── ...
#
################################################################################

set -e  # Exit on any error

# ============================================================================
# CONFIGURATION & ARGUMENT PARSING
# ============================================================================

STUDY_NAME="${1:-}"
DATABASES="pubmed,scopus,wos"
SKIP_EMBASE=false
EMBASE_ONLY=false
SKIP_AGGREGATION=false
USE_MULTI_KEY=false
QUERY_BY_QUERY=false
QUERY_INDEX=""

# Parse command line arguments
shift 1 2>/dev/null || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --databases)
            DATABASES="$2"
            shift 2
            ;;
        --skip-embase)
            SKIP_EMBASE=true
            shift
            ;;
        --embase-only)
            EMBASE_ONLY=true
            shift
            ;;
        --skip-aggregation)
            SKIP_AGGREGATION=true
            shift
            ;;
        --multi-key)
            USE_MULTI_KEY=true
            shift
            ;;
        --query-by-query)
            QUERY_BY_QUERY=true
            shift
            ;;
        --query-index)
            if [ -z "${2:-}" ]; then
                echo "❌ Error: --query-index requires an integer argument"
                exit 1
            fi
            QUERY_INDEX="$2"
            shift 2
            ;;
        --help)
            head -n 38 "$0" | tail -n +3 | sed 's/^# //' | sed 's/^#//'
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate study name
if [ -z "$STUDY_NAME" ]; then
    echo "❌ Error: STUDY_NAME is required"
    echo ""
    echo "Usage: bash scripts/run_complete_workflow.sh <STUDY_NAME> [OPTIONS]"
    echo "Example: bash scripts/run_complete_workflow.sh ai_2022 --databases pubmed,scopus"
    echo ""
    echo "Use --help for full documentation"
    exit 1
fi

# ============================================================================
# QUERY HELPERS
# ============================================================================

# Count queries using same semantics as read_queries_from_txt():
# - blank lines separate queries
# - comment lines starting with # are ignored
count_queries_in_file() {
    local file="$1"
    awk '
    BEGIN { count=0; in_query=0 }
    {
        line=$0
        sub(/\r$/, "", line)
        if (line ~ /^[[:space:]]*$/) {
            in_query=0
            next
        }
        if (line ~ /^[[:space:]]*#/) {
            next
        }
        if (in_query == 0) {
            count++
            in_query=1
        }
    }
    END { print count }
    ' "$file"
}

# Extract a single query (1-based index) to output file.
extract_query_to_file() {
    local file="$1"
    local query_index="$2"
    local output_file="$3"
    awk -v target="$query_index" '
    BEGIN { current=0; in_query=0 }
    {
        line=$0
        sub(/\r$/, "", line)
        if (line ~ /^[[:space:]]*$/) {
            in_query=0
            next
        }
        if (line ~ /^[[:space:]]*#/) {
            next
        }
        if (in_query == 0) {
            current++
            in_query=1
        }
        if (current == target) {
            print line
        }
    }
    ' "$file" > "$output_file"

    [ -s "$output_file" ]
}

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

# Load environment variables from .env file (API keys, credentials, etc.)
if [ -f .env ]; then
    source .env
fi

# Activate conda environment
if command -v conda &> /dev/null; then
    source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || true
    conda activate systematic_review_queries 2>/dev/null || echo "⚠️  Warning: Could not activate conda environment"
fi

# ============================================================================
# PATH VALIDATION
# ============================================================================

STUDY_DIR="studies/$STUDY_NAME"
QUERIES_TXT="queries.txt"
QUERIES_SCOPUS="queries_scopus.txt"
QUERIES_WOS="queries_wos.txt"
QUERIES_EMBASE="queries_embase.txt"
GOLD_CSV="gold_pmids_${STUDY_NAME}.csv"

# Output directories
SEALED_OUTDIR="sealed_outputs"
BENCHMARK_OUTDIR="benchmark_outputs"
AGGREGATES_OUTDIR="aggregates"
AGGREGATES_EVAL_OUTDIR="aggregates_eval"

echo "════════════════════════════════════════════════════════════════"
echo "  Complete Systematic Review Workflow"
echo "  Study: $STUDY_NAME"
echo "  Databases: $DATABASES"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if study directory exists
if [ ! -d "$STUDY_DIR" ]; then
    echo "❌ Error: Study directory not found: $STUDY_DIR"
    echo ""
    echo "Please create the study directory and required files:"
    echo "  mkdir -p $STUDY_DIR"
    echo "  # Then add queries.txt and gold_pmids_${STUDY_NAME}.csv"
    exit 1
fi

# Check for required files
echo "📋 Validating study files..."
if [ ! -f "$STUDY_DIR/$QUERIES_TXT" ]; then
    echo "❌ Error: PubMed queries not found: $STUDY_DIR/$QUERIES_TXT"
    exit 1
fi
echo "  ✅ PubMed queries: $STUDY_DIR/$QUERIES_TXT"

# Auto-detect detailed gold standard (with DOIs) for better multi-database matching
GOLD_DETAILED="gold_pmids_${STUDY_NAME}_detailed.csv"
if [ -f "$STUDY_DIR/$GOLD_DETAILED" ]; then
    GOLD_CSV="$GOLD_DETAILED"
    echo "  ✅ Gold standard (with DOIs): $STUDY_DIR/$GOLD_CSV"
    echo "     Using detailed format for DOI-based matching with Scopus/WOS"
    # Auto-enable multi-key matching when detailed gold standard is detected
    if [ "$USE_MULTI_KEY" = false ]; then
        USE_MULTI_KEY=true
        echo "     Automatically enabled --multi-key mode"
    fi
elif [ ! -f "$STUDY_DIR/$GOLD_CSV" ]; then
    echo "❌ Error: Gold standard not found: $STUDY_DIR/$GOLD_CSV"
    exit 1
else
    echo "  ✅ Gold standard (PMID-only): $STUDY_DIR/$GOLD_CSV"
    echo "     ⚠️  Note: For better Scopus/WOS recall, create detailed gold standard with DOIs"
fi

# Check for database-specific queries
if [[ "$DATABASES" == *"scopus"* ]] && [ -f "$STUDY_DIR/$QUERIES_SCOPUS" ]; then
    echo "  ✅ Scopus queries: $STUDY_DIR/$QUERIES_SCOPUS"
elif [[ "$DATABASES" == *"scopus"* ]]; then
    echo "  ⚠️  Warning: Scopus requested but $STUDY_DIR/$QUERIES_SCOPUS not found"
fi

if [[ "$DATABASES" == *"wos"* || "$DATABASES" == *"web_of_science"* ]] && [ -f "$STUDY_DIR/$QUERIES_WOS" ]; then
    echo "  ✅ WOS queries: $STUDY_DIR/$QUERIES_WOS"
elif [[ "$DATABASES" == *"wos"* || "$DATABASES" == *"web_of_science"* ]]; then
    echo "  ⚠️  Warning: WOS requested but $STUDY_DIR/$QUERIES_WOS not found"
fi

# Validate query counts across provider-specific files
TOTAL_QUERIES=$(count_queries_in_file "$STUDY_DIR/$QUERIES_TXT")
if [ "$TOTAL_QUERIES" -le 0 ]; then
    echo "❌ Error: No valid queries found in $STUDY_DIR/$QUERIES_TXT"
    exit 1
fi
echo "  ✅ Query count detected: $TOTAL_QUERIES"

if [[ "$DATABASES" == *"scopus"* ]] && [ -f "$STUDY_DIR/$QUERIES_SCOPUS" ]; then
    SCOPUS_QUERY_COUNT=$(count_queries_in_file "$STUDY_DIR/$QUERIES_SCOPUS")
    if [ "$SCOPUS_QUERY_COUNT" -ne "$TOTAL_QUERIES" ]; then
        echo "❌ Error: Query count mismatch (pubmed=$TOTAL_QUERIES, scopus=$SCOPUS_QUERY_COUNT)"
        echo "   Ensure queries.txt and queries_scopus.txt have aligned query blocks."
        exit 1
    fi
fi

if [[ "$DATABASES" == *"wos"* || "$DATABASES" == *"web_of_science"* ]] && [ -f "$STUDY_DIR/$QUERIES_WOS" ]; then
    WOS_QUERY_COUNT=$(count_queries_in_file "$STUDY_DIR/$QUERIES_WOS")
    if [ "$WOS_QUERY_COUNT" -ne "$TOTAL_QUERIES" ]; then
        echo "❌ Error: Query count mismatch (pubmed=$TOTAL_QUERIES, wos=$WOS_QUERY_COUNT)"
        echo "   Ensure queries.txt and queries_wos.txt have aligned query blocks."
        exit 1
    fi
fi

# Query execution mode
RUN_QUERY_LEVEL=false
if [ "$QUERY_BY_QUERY" = true ] || [ -n "$QUERY_INDEX" ]; then
    RUN_QUERY_LEVEL=true
fi

QUERY_SEQUENCE=()
if [ "$RUN_QUERY_LEVEL" = true ]; then
    if [ -n "$QUERY_INDEX" ]; then
        if ! [[ "$QUERY_INDEX" =~ ^[0-9]+$ ]]; then
            echo "❌ Error: --query-index must be a positive integer"
            exit 1
        fi
        if [ "$QUERY_INDEX" -lt 1 ] || [ "$QUERY_INDEX" -gt "$TOTAL_QUERIES" ]; then
            echo "❌ Error: --query-index out of range (valid: 1-$TOTAL_QUERIES)"
            exit 1
        fi
        QUERY_SEQUENCE=("$QUERY_INDEX")
    else
        for ((i = 1; i <= TOTAL_QUERIES; i++)); do
            QUERY_SEQUENCE+=("$i")
        done
    fi
    echo "  ✅ Query-level mode enabled: ${#QUERY_SEQUENCE[@]} query run(s)"
fi

echo ""

# ============================================================================
# DATABASE API CONFIGURATION
# ============================================================================

DB_ARGS=()
if [ -n "$DATABASES" ]; then
    DB_ARGS+=(--databases "$DATABASES")
fi

# Scopus configuration
if [ -n "$SCOPUS_API_KEY" ]; then
    DB_ARGS+=(--scopus-api-key "$SCOPUS_API_KEY")
fi
if [ -n "$SCOPUS_INSTTOKEN" ]; then
    DB_ARGS+=(--scopus-insttoken "$SCOPUS_INSTTOKEN")
fi
if [ "${SCOPUS_SKIP_DATE_FILTER:-true}" = "true" ]; then
    DB_ARGS+=(--scopus-skip-date-filter)
fi

# Web of Science configuration
if [ -n "$WOS_API_KEY" ]; then
    DB_ARGS+=(--wos-api-key "$WOS_API_KEY")
fi

QUERY_TMP_DIR=""
if [ "$RUN_QUERY_LEVEL" = true ]; then
    QUERY_TMP_DIR=$(mktemp -d "/tmp/sr_query_workflow_${STUDY_NAME}_XXXXXX")
    trap 'rm -rf "$QUERY_TMP_DIR"' EXIT
fi

# ============================================================================
# STEP 1: EMBASE IMPORT (if CSV files exist)
# ============================================================================

EMBASE_IMPORTED=false
EMBASE_FILES=()

if [ "$SKIP_EMBASE" = false ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  STEP 1: Embase Import"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Check for Embase CSV files in multiple locations
    CSV_LOCATIONS=(
        "$STUDY_DIR/embase_manual_queries/embase_query*.csv"
        "$STUDY_DIR/embase_query*.csv"
    )
    
    EMBASE_CSVS=()
    for pattern in "${CSV_LOCATIONS[@]}"; do
        for file in $pattern; do
            if [ -f "$file" ]; then
                EMBASE_CSVS+=("$file")
            fi
        done
    done
    
    # Remove duplicates
    EMBASE_CSVS=($(printf '%s\n' "${EMBASE_CSVS[@]}" | sort -u))
    
    if [ ${#EMBASE_CSVS[@]} -gt 0 ]; then
        echo "📥 Found ${#EMBASE_CSVS[@]} Embase CSV file(s)"
        
        # Check if queries_embase.txt exists
        if [ ! -f "$STUDY_DIR/$QUERIES_EMBASE" ]; then
            echo "❌ Error: Embase CSV files found but $STUDY_DIR/$QUERIES_EMBASE is missing"
            echo "   Please create this file with your Embase queries (one per line, matching CSV order)"
            exit 1
        fi
        
        # Run batch import
        echo "   Importing Embase results..."
        python scripts/batch_import_embase.py \
            --study "$STUDY_NAME" \
            --csvs "${EMBASE_CSVS[@]}" \
            --queries-file "$STUDY_DIR/$QUERIES_EMBASE"
        
        if [ $? -eq 0 ]; then
            echo "   ✅ Embase import complete!"
            EMBASE_IMPORTED=true
            
            # Collect imported JSON files
            for json_file in "$STUDY_DIR"/embase_query*.json; do
                if [ -f "$json_file" ]; then
                    EMBASE_FILES+=("$json_file")
                fi
            done
            echo "   Created ${#EMBASE_FILES[@]} JSON file(s)"
            
            # Score Embase queries against gold standard (default mode only)
            if [ "$RUN_QUERY_LEVEL" = false ] && [ ${#EMBASE_FILES[@]} -gt 0 ] && [ -f "$STUDY_DIR/$GOLD_CSV" ]; then
                echo ""
                echo "📊 Scoring Embase queries against gold standard..."
                
                MULTI_KEY_FLAG=""
                if [ "$USE_MULTI_KEY" = true ]; then
                    MULTI_KEY_FLAG="--use-multi-key"
                fi
                
                python llm_sr_select_and_score.py \
                    --study-name "$STUDY_NAME" \
                    score-sets \
                    --sets "${EMBASE_FILES[@]}" \
                    --gold-csv "$GOLD_CSV" \
                    --outdir "$BENCHMARK_OUTDIR" \
                    $MULTI_KEY_FLAG
                
                if [ $? -eq 0 ]; then
                    echo "   ✅ Embase scoring complete!"
                    
                    # Show latest Embase scores if available
                    LATEST_EMBASE_SUMMARY=$(ls -t "$BENCHMARK_OUTDIR/$STUDY_NAME"/sets_summary_*.csv 2>/dev/null | head -n 1)
                    if [ -f "$LATEST_EMBASE_SUMMARY" ]; then
                        echo ""
                        echo "📈 Embase Query Performance:"
                        echo "────────────────────────────────────────────────────────────"
                        head -n 10 "$LATEST_EMBASE_SUMMARY" | column -t -s,
                        echo "────────────────────────────────────────────────────────────"
                    fi
                else
                    echo "   ⚠️  Embase scoring failed (continuing workflow)"
                fi
            elif [ "$RUN_QUERY_LEVEL" = true ] && [ ${#EMBASE_FILES[@]} -gt 0 ]; then
                echo "   ℹ️  Query-level mode: Embase scoring will run per query."
            fi
        else
            echo "   ❌ Embase import failed"
            exit 1
        fi
    else
        echo "ℹ️  No Embase CSV files found (checked: embase_query*.csv)"
        echo "   Skipping Embase import. To include Embase:"
        echo "   1. Export queries from Embase.com as CSV"
        echo "   2. Save to: $STUDY_DIR/embase_manual_queries/"
        echo "   3. Re-run this script"
    fi
    echo ""
fi

# If embase-only mode, stop after import
if [ "$EMBASE_ONLY" = true ]; then
    if [ "$EMBASE_IMPORTED" = false ]; then
        echo "❌ Error: --embase-only specified but no Embase files were imported"
        exit 1
    fi
    
    echo "✅ Embase-only mode: Import complete, skipping API queries"
    echo "   Run without --embase-only to aggregate with existing results"
    exit 0
fi

# ============================================================================
# STEP 2: QUERY EXECUTION & SCORING (PubMed, Scopus, WOS)
# ============================================================================

MULTI_KEY_FLAG=""
if [ "$USE_MULTI_KEY" = true ]; then
    MULTI_KEY_FLAG="--use-multi-key"
fi

if [ "$EMBASE_ONLY" = false ] && [ "$RUN_QUERY_LEVEL" = true ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  STEP 2-4: Query-Level Execution"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🔍 Running one query at a time across databases: $DATABASES"
    echo "   Query order: ${QUERY_SEQUENCE[*]}"
    echo ""

    for QUERY_NUM in "${QUERY_SEQUENCE[@]}"; do
        QUERY_LABEL=$(printf "query_%02d" "$QUERY_NUM")
        QUERY_BASE="$QUERY_TMP_DIR/$QUERY_LABEL"
        QUERY_MAIN_TMP="${QUERY_BASE}.txt"
        QUERY_SCOPUS_TMP="${QUERY_BASE}_scopus.txt"
        QUERY_WOS_TMP="${QUERY_BASE}_wos.txt"

        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  Processing Query $QUERY_NUM/$TOTAL_QUERIES ($QUERY_LABEL)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        if ! extract_query_to_file "$STUDY_DIR/$QUERIES_TXT" "$QUERY_NUM" "$QUERY_MAIN_TMP"; then
            echo "❌ Error: Failed to extract query $QUERY_NUM from $STUDY_DIR/$QUERIES_TXT"
            exit 1
        fi

        if [[ "$DATABASES" == *"scopus"* ]] && [ -f "$STUDY_DIR/$QUERIES_SCOPUS" ]; then
            if ! extract_query_to_file "$STUDY_DIR/$QUERIES_SCOPUS" "$QUERY_NUM" "$QUERY_SCOPUS_TMP"; then
                echo "❌ Error: Failed to extract query $QUERY_NUM from $STUDY_DIR/$QUERIES_SCOPUS"
                exit 1
            fi
        fi

        if [[ "$DATABASES" == *"wos"* || "$DATABASES" == *"web_of_science"* ]] && [ -f "$STUDY_DIR/$QUERIES_WOS" ]; then
            if ! extract_query_to_file "$STUDY_DIR/$QUERIES_WOS" "$QUERY_NUM" "$QUERY_WOS_TMP"; then
                echo "❌ Error: Failed to extract query $QUERY_NUM from $STUDY_DIR/$QUERIES_WOS"
                exit 1
            fi
        fi

        echo ""
        echo "🔍 STEP 2: Executing Query $QUERY_NUM across selected databases..."
        # Pass --query-num-offset so per-database CSVs show the actual query number
        # (each invocation only has 1 bundle, so bundle_idx is always 0 → query_num
        # would always be 1 without the offset).
        QUERY_NUM_OFFSET=$(( QUERY_NUM - 1 ))
        python llm_sr_select_and_score.py \
            --study-name "$STUDY_NAME" \
            "${DB_ARGS[@]}" \
            score \
            --queries-txt "$QUERY_MAIN_TMP" \
            --gold-csv "$GOLD_CSV" \
            --outdir "$BENCHMARK_OUTDIR" \
            --query-num-offset "$QUERY_NUM_OFFSET" \
            $MULTI_KEY_FLAG

        LATEST_DETAILS=$(ls -t "$BENCHMARK_OUTDIR/$STUDY_NAME"/details_*.json 2>/dev/null | head -n 1)
        if [ ! -f "$LATEST_DETAILS" ]; then
            echo "❌ Error: Missing details JSON after scoring query $QUERY_NUM"
            exit 1
        fi

        QUERY_BENCH_DIR="$BENCHMARK_OUTDIR/$STUDY_NAME/$QUERY_LABEL"
        mkdir -p "$QUERY_BENCH_DIR"
        LATEST_SUMMARY=$(ls -t "$BENCHMARK_OUTDIR/$STUDY_NAME"/summary_*.csv 2>/dev/null | grep -v "per_database" | head -n 1)
        LATEST_PER_DB=$(ls -t "$BENCHMARK_OUTDIR/$STUDY_NAME"/summary_per_database_*.csv 2>/dev/null | head -n 1)
        [ -f "$LATEST_SUMMARY" ] && cp "$LATEST_SUMMARY" "$QUERY_BENCH_DIR/"
        [ -f "$LATEST_PER_DB" ] && cp "$LATEST_PER_DB" "$QUERY_BENCH_DIR/"
        cp "$LATEST_DETAILS" "$QUERY_BENCH_DIR/"

        if [ "$SKIP_AGGREGATION" = true ]; then
            echo "ℹ️  Skipping aggregation for Query $QUERY_NUM (--skip-aggregation enabled)."
            echo ""
            continue
        fi

        echo ""
        echo "🔄 STEP 3: Aggregating Query $QUERY_NUM (cross-database dedup/merge)..."
        QUERY_AGG_DIR="$AGGREGATES_OUTDIR/$STUDY_NAME/$QUERY_LABEL"
        mkdir -p "$QUERY_AGG_DIR"
        QUERY_AGG_INPUTS=("$LATEST_DETAILS")

        EMBASE_QUERY_FILE="$STUDY_DIR/embase_query${QUERY_NUM}.json"
        if [ -f "$EMBASE_QUERY_FILE" ]; then
            echo "   Including Embase result: $(basename "$EMBASE_QUERY_FILE")"
            QUERY_AGG_INPUTS+=("$EMBASE_QUERY_FILE")
        fi

        AGGREGATE_ARGS=(python scripts/aggregate_queries.py --inputs "${QUERY_AGG_INPUTS[@]}" --outdir "$QUERY_AGG_DIR")
        if [ "$USE_MULTI_KEY" = true ]; then
            AGGREGATE_ARGS+=(--multi-key)
        fi
        "${AGGREGATE_ARGS[@]}"

        echo "📁 Aggregation outputs for Query $QUERY_NUM:"
        for strategy in "$QUERY_AGG_DIR"/*.txt "$QUERY_AGG_DIR"/*.csv; do
            if [ -f "$strategy" ]; then
                item_count=$(wc -l < "$strategy" | tr -d ' ')
                ext="${strategy##*.}"
                if [ "$ext" = "csv" ]; then
                    item_count=$((item_count - 1))
                fi
                echo "   • $(basename "$strategy"): $item_count articles"
            fi
        done

        echo ""
        echo "📊 STEP 4: Scoring Query $QUERY_NUM aggregation strategies..."
        QUERY_SET_FILES=()
        if [ "$USE_MULTI_KEY" = true ]; then
            for set_file in "$QUERY_AGG_DIR"/*.csv; do
                [ -f "$set_file" ] && QUERY_SET_FILES+=("$set_file")
            done
        else
            for set_file in "$QUERY_AGG_DIR"/*.txt; do
                [ -f "$set_file" ] && QUERY_SET_FILES+=("$set_file")
            done
        fi

        if [ ${#QUERY_SET_FILES[@]} -eq 0 ]; then
            echo "⚠️  No aggregation strategy files found for Query $QUERY_NUM. Skipping scoring."
            echo ""
            continue
        fi

        python llm_sr_select_and_score.py \
            --study-name "$STUDY_NAME" \
            score-sets \
            --sets "${QUERY_SET_FILES[@]}" \
            --gold-csv "$GOLD_CSV" \
            --outdir "$AGGREGATES_EVAL_OUTDIR" \
            $MULTI_KEY_FLAG

        QUERY_EVAL_DIR="$AGGREGATES_EVAL_OUTDIR/$STUDY_NAME/$QUERY_LABEL"
        mkdir -p "$QUERY_EVAL_DIR"
        LATEST_QUERY_EVAL=$(ls -t "$AGGREGATES_EVAL_OUTDIR/$STUDY_NAME"/sets_summary_*.csv 2>/dev/null | head -n 1)
        LATEST_QUERY_EVAL_DETAILS=$(ls -t "$AGGREGATES_EVAL_OUTDIR/$STUDY_NAME"/sets_details_*.json 2>/dev/null | head -n 1)
        [ -f "$LATEST_QUERY_EVAL" ] && cp "$LATEST_QUERY_EVAL" "$QUERY_EVAL_DIR/"
        [ -f "$LATEST_QUERY_EVAL_DETAILS" ] && cp "$LATEST_QUERY_EVAL_DETAILS" "$QUERY_EVAL_DIR/"

        if [ -f "$LATEST_QUERY_EVAL" ]; then
            echo "🏆 Query $QUERY_NUM Aggregation Performance:"
            cat "$LATEST_QUERY_EVAL" | column -t -s,
        fi
        echo ""
    done
else
    if [ "$EMBASE_ONLY" = false ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  STEP 2: Query Execution & Scoring"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        echo "🔍 Executing queries for: $DATABASES"
        echo "   This may take 5-20 minutes depending on query complexity..."
        echo ""
        
        if [ "$USE_MULTI_KEY" = true ]; then
            echo "   Using multi-key matching (PMID + DOI)"
        fi
        
        python llm_sr_select_and_score.py \
            --study-name "$STUDY_NAME" \
            "${DB_ARGS[@]}" \
            score \
            --queries-txt "$QUERIES_TXT" \
            --gold-csv "$GOLD_CSV" \
            --outdir "$BENCHMARK_OUTDIR" \
            $MULTI_KEY_FLAG
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Query execution complete!"
            echo ""
            
            # Show combined summary if available
            LATEST_SUMMARY=$(ls -t "$BENCHMARK_OUTDIR/$STUDY_NAME"/summary_*.csv 2>/dev/null | grep -v "per_database" | head -n 1)
            if [ -f "$LATEST_SUMMARY" ]; then
                echo ""
                echo "📊 Query Performance Summary (Combined):"
                echo "────────────────────────────────────────────────────────────"
                head -n 10 "$LATEST_SUMMARY" | column -t -s,
                echo "────────────────────────────────────────────────────────────"
            fi
            
            # Show per-database summary if available
            LATEST_PER_DB=$(ls -t "$BENCHMARK_OUTDIR/$STUDY_NAME"/summary_per_database_*.csv 2>/dev/null | head -n 1)
            if [ -f "$LATEST_PER_DB" ]; then
                echo ""
                echo "📊 Per-Database Query Performance:"
                echo "────────────────────────────────────────────────────────────"
                head -n 30 "$LATEST_PER_DB" | column -t -s,
                echo "────────────────────────────────────────────────────────────"
                
                # Merge Embase results into per-database summary if Embase was scored
                LATEST_EMBASE_SUMMARY=$(ls -t "$BENCHMARK_OUTDIR/$STUDY_NAME"/sets_summary_*.csv 2>/dev/null | head -n 1)
                if [ ${#EMBASE_FILES[@]} -gt 0 ] && [ -f "$LATEST_EMBASE_SUMMARY" ]; then
                    echo ""
                    echo "📊 Merging Embase results into per-database summary..."
                    python -c "
import pandas as pd
import sys

try:
    # Load Embase results
    embase_df = pd.read_csv('$LATEST_EMBASE_SUMMARY')
    per_db_df = pd.read_csv('$LATEST_PER_DB')
    
    # Transform Embase results to per-database format
    embase_rows = []
    for idx, row in embase_df.iterrows():
        # Extract query number from name (e.g., 'embase_query1' -> 1)
        query_num = int(row['name'].replace('embase_query', ''))
        
        embase_row = {
            'query_num': query_num,
            'database': 'embase',
            'query': 'Embase query (see embase_manual_queries/)',
            'results_count': row['Retrieved'],
            'TP': row['TP'],
            'gold_size': row['Gold'],
            'recall': row['Recall'],
            'NNR_proxy': row['Retrieved'] / max(row['TP'], 1)
        }
        
        # Add multi-key columns if they exist
        if 'matches_by_doi' in row:
            embase_row['matches_by_pmid'] = row.get('matches_by_doi', 0) + row.get('matches_by_pmid_fallback', 0)
            embase_row['matches_by_doi_only'] = row.get('matches_by_doi', 0)
        
        embase_rows.append(embase_row)
    
    # Append Embase rows to per-database dataframe
    embase_per_db = pd.DataFrame(embase_rows)
    combined_df = pd.concat([per_db_df, embase_per_db], ignore_index=True)
    
    # Sort by query_num and database
    combined_df = combined_df.sort_values(['query_num', 'database'])
    
    # Save back to the same file
    combined_df.to_csv('$LATEST_PER_DB', index=False)
    print('   ✅ Embase results merged into per-database summary')
except Exception as e:
    print(f'   ⚠️  Failed to merge Embase results: {e}', file=sys.stderr)
"
                fi
            fi
        else
            echo ""
            echo "❌ Query execution failed"
            exit 1
        fi
        echo ""
    fi
    
    # ============================================================================
    # STEP 3: AGGREGATION
    # ============================================================================
    
    if [ "$SKIP_AGGREGATION" = false ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  STEP 3: Query Aggregation"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        # Check if we have results to aggregate
        if [ ! -d "$BENCHMARK_OUTDIR/$STUDY_NAME" ]; then
            echo "⚠️  No benchmark outputs found. Run query execution first."
            
            if [ ${#EMBASE_FILES[@]} -gt 0 ]; then
                echo "   Embase files available but need API query results to aggregate."
                echo "   Skipping aggregation."
            fi
            echo ""
        else
            echo "🔄 Aggregating query results..."
            
            # Prepare input arguments
            AGGREGATE_INPUTS=("$BENCHMARK_OUTDIR/$STUDY_NAME"/details_*.json)
            
            # Add Embase files if available
            if [ ${#EMBASE_FILES[@]} -gt 0 ]; then
                echo "   Including ${#EMBASE_FILES[@]} Embase result file(s)"
                AGGREGATE_INPUTS+=("${EMBASE_FILES[@]}")
            fi
            
            AGGREGATE_ARGS=(python scripts/aggregate_queries.py --inputs "${AGGREGATE_INPUTS[@]}" --outdir "$AGGREGATES_OUTDIR/$STUDY_NAME")
            if [ "$USE_MULTI_KEY" = true ]; then
                AGGREGATE_ARGS+=(--multi-key)
                echo "   Using multi-key mode (PMID + DOI) for improved recall"
            fi
            
            "${AGGREGATE_ARGS[@]}"
            
            if [ $? -eq 0 ]; then
                echo ""
                echo "✅ Aggregation complete!"
                
                # List aggregated sets (handle both .txt and .csv)
                echo ""
                echo "📁 Created aggregation strategies:"
                for strategy in "$AGGREGATES_OUTDIR/$STUDY_NAME"/*.txt "$AGGREGATES_OUTDIR/$STUDY_NAME"/*.csv; do
                    if [ -f "$strategy" ]; then
                        item_count=$(wc -l < "$strategy" | tr -d ' ')
                        ext="${strategy##*.}"
                        if [ "$ext" = "csv" ]; then
                            # Subtract 1 for header row in CSV
                            item_count=$((item_count - 1))
                        fi
                        echo "   • $(basename "$strategy"): $item_count articles"
                    fi
                done
            else
                echo ""
                echo "❌ Aggregation failed"
                exit 1
            fi
            echo ""
        fi
    fi
    
    # ============================================================================
    # STEP 4: SCORING AGGREGATED SETS
    # ============================================================================
    
    if [ "$SKIP_AGGREGATION" = false ] && [ -d "$AGGREGATES_OUTDIR/$STUDY_NAME" ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  STEP 4: Scoring Aggregated Sets"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        echo "📊 Scoring aggregation strategies against gold standard..."
        echo ""
        
        # Determine which file pattern to use based on multi-key mode
        if [ "$USE_MULTI_KEY" = true ]; then
            SET_PATTERN="$AGGREGATES_OUTDIR/$STUDY_NAME/*.csv"
            MULTIKEY_FLAG="--use-multi-key"
            echo "   Using multi-key matching (PMID OR DOI) for improved recall"
            
            # Check if detailed gold standard exists (with DOI column)
            GOLD_DETAILED="gold_pmids_${STUDY_NAME}_detailed.csv"
            if [ -f "$STUDY_DIR/$GOLD_DETAILED" ]; then
                GOLD_CSV="$GOLD_DETAILED"
                echo "   Using detailed gold standard with DOIs: $GOLD_CSV"
            else
                echo "   ⚠️  Detailed gold standard not found, using basic gold CSV"
                echo "      For best results, run: python scripts/generate_gold_standard.py $STUDY_NAME"
            fi
        else
            SET_PATTERN="$AGGREGATES_OUTDIR/$STUDY_NAME/*.txt"
            MULTIKEY_FLAG=""
        fi
        
        python llm_sr_select_and_score.py \
            --study-name "$STUDY_NAME" \
            score-sets \
            --sets $SET_PATTERN \
            --gold-csv "$GOLD_CSV" \
            --outdir "$AGGREGATES_EVAL_OUTDIR" \
            $MULTIKEY_FLAG
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Scoring complete!"
            
            # Show results summary
            LATEST_EVAL=$(ls -t "$AGGREGATES_EVAL_OUTDIR/$STUDY_NAME"/sets_summary_*.csv 2>/dev/null | head -n 1)
            if [ -f "$LATEST_EVAL" ]; then
                echo ""
                echo "🏆 Aggregation Strategy Performance:"
                echo "════════════════════════════════════════════════════════════"
                cat "$LATEST_EVAL" | column -t -s,
                echo "════════════════════════════════════════════════════════════"
                echo ""
                echo "💡 Look for strategies with Recall=1.0 (100% gold studies found)"
            fi
        else
            echo ""
            echo "❌ Scoring failed"
            exit 1
        fi
        echo ""
    fi
fi

# ============================================================================
# FINAL SUMMARY
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "  ✅ Workflow Complete for Study: $STUDY_NAME"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📊 Results Summary:"
echo "───────────────────────────────────────────────────────────────"

EMBASE_COUNT=${#EMBASE_FILES[@]}

echo "  • Databases queried: $DATABASES"
if [ "$EMBASE_COUNT" -gt 0 ]; then
    echo "  • Embase queries imported: $EMBASE_COUNT"
fi

if [ "$RUN_QUERY_LEVEL" = true ]; then
    QUERY_RESULTS=$(ls "$BENCHMARK_OUTDIR/$STUDY_NAME"/details_*.json 2>/dev/null | wc -l | tr -d ' ')
    QUERY_LEVEL_AGG_DIRS=$(find "$AGGREGATES_OUTDIR/$STUDY_NAME" -maxdepth 1 -type d -name 'query_*' 2>/dev/null | wc -l | tr -d ' ')
    QUERY_LEVEL_EVAL_DIRS=$(find "$AGGREGATES_EVAL_OUTDIR/$STUDY_NAME" -maxdepth 1 -type d -name 'query_*' 2>/dev/null | wc -l | tr -d ' ')
    echo "  • Execution mode: query-level (${#QUERY_SEQUENCE[@]} query run(s))"
    echo "  • Processed query indices: ${QUERY_SEQUENCE[*]}"
    echo "  • Query result files generated: $QUERY_RESULTS"
    echo "  • Query aggregate folders: $QUERY_LEVEL_AGG_DIRS"
    echo "  • Query evaluation folders: $QUERY_LEVEL_EVAL_DIRS"
else
    QUERY_RESULTS=$(ls "$BENCHMARK_OUTDIR/$STUDY_NAME"/details_*.json 2>/dev/null | wc -l | tr -d ' ')
    AGGREGATES_TXT=$(ls "$AGGREGATES_OUTDIR/$STUDY_NAME"/*.txt 2>/dev/null | wc -l | tr -d ' ')
    AGGREGATES_CSV=$(ls "$AGGREGATES_OUTDIR/$STUDY_NAME"/*.csv 2>/dev/null | wc -l | tr -d ' ')
    AGGREGATES=$((AGGREGATES_TXT + AGGREGATES_CSV))
    echo "  • Execution mode: full-set (all queries together)"
    echo "  • Query result files: $QUERY_RESULTS"
    echo "  • Aggregation strategies: $AGGREGATES"
fi
echo ""

echo "📁 Output Locations:"
echo "───────────────────────────────────────────────────────────────"
if [ -d "$BENCHMARK_OUTDIR/$STUDY_NAME" ]; then
    echo "  • Query results: $BENCHMARK_OUTDIR/$STUDY_NAME/"
fi
if [ -d "$AGGREGATES_OUTDIR/$STUDY_NAME" ]; then
    echo "  • Aggregated sets: $AGGREGATES_OUTDIR/$STUDY_NAME/"
fi
if [ -d "$AGGREGATES_EVAL_OUTDIR/$STUDY_NAME" ]; then
    echo "  • Performance scores: $AGGREGATES_EVAL_OUTDIR/$STUDY_NAME/"
fi
echo ""

echo "🎯 Next Steps:"
echo "───────────────────────────────────────────────────────────────"
if [ "$RUN_QUERY_LEVEL" = true ]; then
    echo "  1. Review per-query metrics in:"
    echo "     $AGGREGATES_EVAL_OUTDIR/$STUDY_NAME/query_*/"
    echo ""
    echo "  2. Compare best strategy per query before picking a final approach"
    echo ""
    echo "  3. (Optional) Run full-set mode for global strategy scoring:"
    echo "     bash scripts/run_complete_workflow.sh $STUDY_NAME --databases $DATABASES"
else
    echo "  1. Review performance metrics in:"
    echo "     $AGGREGATES_EVAL_OUTDIR/$STUDY_NAME/sets_summary_*.csv"
    echo ""
    echo "  2. Select best aggregation strategy (look for 100% recall)"
    echo ""
    echo "  3. Export final PMID list for screening:"
    echo "     cp $AGGREGATES_OUTDIR/$STUDY_NAME/<best_strategy>.txt final_pmids_$STUDY_NAME.txt"
    echo ""
    echo "  4. (Optional) Analyze query performance by type across databases:"
    echo "     python scripts/analyze_queries_by_type.py $STUDY_NAME --detailed"
fi
echo ""
echo "════════════════════════════════════════════════════════════════"
