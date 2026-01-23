"""
Cross-Study Validation Framework

A meta-analysis system for evaluating aggregation strategy performance
across multiple systematic review studies.
"""

__version__ = '1.0.0'

from .collectors import (
    collect_study_results,
    load_studies_data
)
from .analysis import (
    DescriptiveStats
)
from .reporting import (
    MarkdownReporter
)

__all__ = [
    'collect_study_results',
    'load_studies_data',
    'DescriptiveStats',
    'MarkdownReporter',
]
