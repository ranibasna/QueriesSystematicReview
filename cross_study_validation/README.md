# Cross-Study Validation Framework

A self-contained meta-analysis package for evaluating aggregation strategy performance across multiple systematic reviews.

## Directory Structure

```
cross_study_validation/
├── __init__.py              # Package initialization
├── __main__.py              # Main CLI entry point
├── collectors/              # Data collection modules
│   ├── collect_study_results.py
│   └── parsers/             # CSV/JSON parsers
├── analysis/                # Statistical analysis
│   └── descriptive_stats.py
├── reporting/               # Report generation
│   └── markdown_reporter.py
├── data/                    # Standardized study data (JSON)
├── reports/                 # Generated reports
├── schemas/                 # JSON validation schemas
└── tests/                   # Unit tests
```

## Quick Start

### Complete Workflow (Recommended)

```bash
# Run everything: collect data + generate report
python -m cross_study_validation run
```

### Step-by-Step

```bash
# Step 1: Collect data from all studies
python -m cross_study_validation collect --all

# Step 2: Generate analysis report
python -m cross_study_validation analyze
```

### Individual Study

```bash
# Collect single study
python -m cross_study_validation collect --study Godos_2024
```

## Features

- **Standardized Data Collection**: Automatically extracts results from `aggregates_eval/` and `benchmark_outputs/`
- **Statistical Analysis**: Descriptive stats, significance testing, correlation analysis
- **Strategy Rankings**: Multi-criteria evaluation of aggregation strategies
- **Automated Reporting**: Markdown and HTML reports with visualizations

## Study Data Schema

Each study is standardized to JSON format containing:
- Study metadata (ID, domain, databases, date range)
- Gold standard reference list (PMIDs)
- Aggregation strategy performance (recall, precision, F1, retrieved count)
- Individual query performance

See `schemas/study_result_schema.json` for complete schema.

## Documentation

For detailed documentation, see:
- `Documentations/plans/cross_study_validation_framework_plan.md` - Overall plan
- `Documentations/tasks/cross_study_validation_tasks.md` - Implementation tasks
