"""
Cross-Study Validation Framework

A meta-analysis system for evaluating aggregation strategy performance
across multiple systematic review studies.
"""

from importlib import import_module

__version__ = '1.0.0'

__all__ = [
    'collect_study_results',
    'load_studies_data',
    'DescriptiveStats',
    'MarkdownReporter',
]


def __getattr__(name):
    """Lazily expose package-level helpers without importing optional dependencies upfront."""
    if name in {'collect_study_results', 'load_studies_data'}:
        module = import_module('.collectors', __name__)
        return getattr(module, name)
    if name == 'DescriptiveStats':
        module = import_module('.analysis', __name__)
        return getattr(module, name)
    if name == 'MarkdownReporter':
        module = import_module('.reporting', __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
