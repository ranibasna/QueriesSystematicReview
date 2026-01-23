# Cross-Study Validation Framework

This directory contains the cross-study validation framework for evaluating aggregation strategy performance across multiple systematic reviews.

## Directory Structure

- `data/` - Standardized JSON data from completed studies
- `reports/` - Generated analysis reports (markdown, HTML, JSON)
- `reports/figures/` - Visualization outputs (PNG, SVG)
- `schemas/` - JSON schemas for data validation
- `analysis/` - Analysis engine modules
- `reporting/` - Report generation modules
- `tests/` - Unit and integration tests

## Quick Start

### Collect Study Results

```bash
# Collect single study
python scripts/collect_study_results.py --study Godos_2024

# Collect all studies
python scripts/collect_study_results.py --all-studies
```

### Generate Analysis Report

```bash
# Generate cross-study analysis
python cross_study_validation/analyze_studies.py
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
