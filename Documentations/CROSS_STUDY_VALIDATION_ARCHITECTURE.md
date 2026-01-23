# Cross-Study Validation: Architecture Redesign

**Date**: January 23, 2026  
**Version**: 2.0 (Reorganized)

---

## Problem Statement

The initial implementation had **scattered code** across multiple directories:
- Collection script: `scripts/collect_study_results.py`
- Parsers: `scripts/parsers/`
- Analysis: `cross_study_validation/analysis/`
- Reporting: `cross_study_validation/reporting/`

This created confusion about:
1. **Where does cross-study code live?** (scripts/ vs cross_study_validation/)
2. **What's the difference?** Mixed single-study and cross-study tools in `scripts/`
3. **How to use it?** Multiple entry points, unclear workflow

---

## New Architecture: Self-Contained Package

### Principle: Separation of Concerns

```
scripts/                          ← Single-study tools
├── generate_queries.py           (run once per study)
├── extract_included_studies.py   
├── validate_gold_standard.py
└── ...

cross_study_validation/           ← Meta-analysis package
├── __init__.py                   (Self-contained, clear purpose)
├── __main__.py                   ← Unified CLI entry point
├── collectors/                   ← Data collection
│   ├── collect_study_results.py
│   └── parsers/                  (moved from scripts/)
├── analysis/                     ← Statistical analysis
├── reporting/                    ← Report & visualization generation
│   ├── markdown_reporter.py
│   └── visualizations.py         ← Phase 3: Publication-quality figures
├── data/                         ← Standardized data (gitignored)
├── reports/                      ← Generated reports (gitignored)
│   └── figures/                  ← Visualization outputs
└── schemas/                      ← Validation rules
```

###Why This Is Better

**1. Clear Boundaries**
- `scripts/` = Individual study workflows (one study at a time)
- `cross_study_validation/` = Meta-analysis (across all studies)

**2. Self-Contained Package**
- Everything related to cross-study analysis in ONE place
- Can import as: `from cross_study_validation import ...`
- Could be extracted as standalone Python package later

**3. Single Entry Point**
```bash
# Old way (confusing)
python scripts/collect_study_results.py --all-studies
python cross_study_validation/reporting/markdown_reporter.py

# New way (intuitive)
python -m cross_study_validation run
```

**4. Logical Data Flow**

```
Individual Study Workflow → Cross-Study Analysis
════════════════════════    ═══════════════════

studies/<study>/            cross_study_validation/
  ├── queries.txt             ├── collectors/  (reads studies/)
  └── gold_*.csv              ├── analysis/    (analyzes data)
                              └── reports/     (outputs findings)
↓                           
                            
aggregates_eval/<study>/   
  └── sets_summary_*.csv    
                            
benchmark_outputs/<study>/  
  └── summary_*.csv         
```

---

## Usage Comparison

### Old Way (v1.0)

```bash
# Step 1: Collect data
python scripts/collect_study_results.py --all-studies

# Step 2: Generate report  
python cross_study_validation/reporting/markdown_reporter.py

# Problems:
# - Two separate commands in different locations
# - Unclear what order to run them
# - Mixed concerns in scripts/ directory
```

### New Way (v2.0)

```bash
# Complete workflow (collect + analyze + visualize)
python -m cross_study_validation run

# Or step-by-step
python -m cross_study_validation collect --all
python -m cross_study_validation analyze
python -m cross_study_validation visualize

# Benefits:
# - Single entry point
# - Clear subcommands
# - Self-documenting with --help
# - Generates publication-quality visualizations
```

---

## File Organization

### scripts/ Directory (Single-Study Tools)

Tools that operate on ONE study at a time:

```
scripts/
├── generate_queries.py           # Generate queries from PROSPERO
├── extract_included_studies.py   # Extract PMIDs from paper
├── validate_gold_standard.py     # Validate gold standard PMIDs
├── prepare_study.py               # PDF → Markdown conversion
├── import_embase_manual.py        # Import Embase CSV
└── aggregate_queries.py           # Run aggregation strategies
```

**When to use**: During individual study workflow

### cross_study_validation/ Package (Meta-Analysis)

Tools that operate on MULTIPLE studies:

```
cross_study_validation/
├── __main__.py                    # CLI: python -m cross_study_validation
├── collectors/
│   ├── collect_study_results.py  # Extract data from all studies
│   └── parsers/                   # Parse CSV/JSON files
├── analysis/
│   └── descriptive_stats.py      # Cross-study statistics
├── reporting/
│   ├── markdown_reporter.py      # Generate markdown reports
│   └── visualizations.py         # Generate publication-quality figures
├── data/                          # Collected study data (JSON, gitignored)
├── reports/                       # Generated reports (gitignored)
│   └── figures/                   # Visualization outputs (PNG, 300 DPI)
└── schemas/                       # Data validation
```

**When to use**: After completing 2+ individual studies

---

## Command Reference

### New CLI Commands

```bash
# Show help
python -m cross_study_validation --help

# Run complete workflow (collect + analyze + visualize)
python -m cross_study_validation run

# Collect data only
python -m cross_study_validation collect --all
python -m cross_study_validation collect --study Godos_2024

# Generate report only
python -m cross_study_validation analyze
python -m cross_study_validation report  # alias for analyze

# Generate visualizations only
python -m cross_study_validation visualize
python -m cross_study_validation visualize --output ./my_figures/

# Custom output
python -m cross_study_validation analyze --output my_report.md

# Verbose logging
python -m cross_study_validation run --verbose
```

### Package Imports

```python
# Import as package
from cross_study_validation import (
    collect_study_results,
    load_studies_data,
    DescriptiveStats,
    MarkdownReporter
)

# Programmatic usage
studies = collect_study_results(all_studies=True)
stats = DescriptiveStats(studies)
report = MarkdownReporter(studies)
report.save_report('my_report.md')
```

---

## Migration Guide

### For Existing Users

**Old commands still work** (for now):
```bash
# These still work but are deprecated
python scripts/collect_study_results.py --all-studies
python cross_study_validation/reporting/markdown_reporter.py
```

**Recommended migration**:
```bash
# Replace with new unified CLI
python -m cross_study_validation run
```

### For Scripts/Automation

**Before**:
```bash
#!/bin/bash
python scripts/collect_study_results.py --all-studies
python cross_study_validation/reporting/markdown_reporter.py
```

**After**:
```bash
#!/bin/bash
python -m cross_study_validation run
```

---

## Benefits Summary

| Aspect | Old (v1.0) | New (v2.0) |
|--------|-----------|-----------|
| **Organization** | Scattered across `scripts/` and `cross_study_validation/` | Self-contained in `cross_study_validation/` |
| **Entry Point** | Multiple scripts in different locations | Single CLI: `python -m cross_study_validation` |
| **Clarity** | Mixed single-study and cross-study tools | Clear separation: `scripts/` vs `cross_study_validation/` |
| **Usability** | Two separate commands | One unified command with subcommands |
| **Maintainability** | Hard to find related code | All related code in one package |
| **Extensibility** | Add files anywhere | Clear package structure |

---

## Conclusion

The reorganization makes the cross-study validation framework:
1. **Self-contained**: Everything in one logical package
2. **Intuitive**: Clear purpose and single entry point
3. **Professional**: Proper Python package structure
4. **Scalable**: Easy to extend with new features

The old structure worked but created confusion about organization and usage. The new structure follows Python best practices and makes the framework much easier to understand and use.

---

**Documentation**:
- User Guide: `Documentations/CROSS_STUDY_VALIDATION_GUIDE.md`
- Quick Start: `cross_study_validation/README.md`
- Design Plan: `Documentations/plans/cross_study_validation_framework_plan.md`
