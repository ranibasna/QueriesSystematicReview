"""W4.2: Fuzzy article matching for Layer 3 identifier-resolution fallback.

This module provides the fuzzy matching logic used by Layer 3 of
``set_metrics_row_level()`` in ``llm_sr_select_and_score.py`` (W4.3).

Purpose
-------
Articles that cannot be identified by DOI (Layer 1) or PMID (Layer 2) may
still be recoverable when rich metadata (title, first author, year) is
available from W4.1.  This module implements the matching primitives for
that fallback.

Public API
----------
fuzzy_match_article(gold, candidate_meta, thresholds=None) -> Optional[float]
    Core matching function.  Returns a confidence score in [0.0, 1.0] when
    ≥ 2 metadata fields independently pass their thresholds; None otherwise.

normalize_title(text) -> str
    Normalise a title string for comparison: HTML decoding, diacritic
    stripping, punctuation removal, whitespace collapsing, lowercase.

normalize_author(text) -> str
    Extract and normalise the last-name component of an author field.

extract_year(value) -> Optional[int]
    Parse a year integer from int / float / string values.

DEFAULT_THRESHOLDS: dict
    {'title': 85, 'author': 80, 'year_diff': 1}

Design rationale
----------------
Requiring ≥ 2 of 3 fields to independently pass their thresholds prevents
false positives from coincidentally similar titles across different papers
(e.g., two review articles with near-identical generic titles).  A single
high-scoring title match alone is *not* sufficient for a confident match.

Each field is only counted as "testable" when both the gold record and the
candidate metadata carry a non-None/non-empty value for that field.  If
fewer than 2 fields are testable the function returns None — it cannot
gather enough evidence for a confident decision.

The module is intentionally self-contained so that it can be tested in
isolation without importing any other pipeline modules.

Dependency: rapidfuzz (already in environment.yml).
"""

from __future__ import annotations

import html
import re
import unicodedata
from typing import Optional, Union

try:
    from rapidfuzz import fuzz as _fuzz  # type: ignore

    _token_sort_ratio = _fuzz.token_sort_ratio
    _ratio = _fuzz.ratio
except ImportError as _exc:  # pragma: no cover
    raise ImportError(
        "rapidfuzz is required for W4.2 fuzzy matching. "
        "Install with: conda install -c conda-forge rapidfuzz"
    ) from _exc


# ─────────────────────────────────────────────────────────────────────────────
# Default per-field thresholds
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_THRESHOLDS: dict = {
    # rapidfuzz token_sort_ratio score (0–100); ≥ 85 is intentionally strict
    # to avoid false positives from coincidentally similar review-article titles
    "title": 85,
    # rapidfuzz ratio score (0–100) for last-name-only author strings
    "author": 80,
    # Maximum absolute difference in publication year (years)
    "year_diff": 1,
}


# ─────────────────────────────────────────────────────────────────────────────
# Normalisation helpers
# ─────────────────────────────────────────────────────────────────────────────

def normalize_title(text: Optional[str]) -> str:
    """Normalise a title string for fuzzy comparison.

    Transformation pipeline
    -----------------------
    1. Return ``""`` for None or empty input.
    2. Decode HTML entities (``&amp;`` → ``&``, ``&#39;`` → ``'``, etc.).
    3. Unicode NFD decomposition + strip combining characters (removes accents
       and diacritics: é→e, ü→u, ñ→n, etc.).
    4. Replace all non-alphanumeric / non-space characters (punctuation,
       underscores, remaining Unicode symbols) with a space.
    5. Collapse multiple spaces into one, strip, and lowercase.

    The output contains only ASCII letters, digits, and single spaces.
    This format is optimal for ``rapidfuzz.fuzz.token_sort_ratio``, which
    sorts space-separated tokens alphabetically before comparing — making the
    result invariant to different word orderings in equivalent titles.

    Examples
    --------
    >>> normalize_title("Effects of Caffeine on Sleep")
    'effects of caffeine on sleep'
    >>> normalize_title("COVID-19 &amp; Sleep Disorders")
    'covid 19 sleep disorders'
    >>> normalize_title("Café: A Review")
    'cafe a review'
    >>> normalize_title(None)
    ''
    """
    if not text:
        return ""

    # 1. HTML entity decoding
    text = html.unescape(text)

    # 2. NFD normalisation + strip combining characters (diacritics)
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))

    # 3. Replace non-alphanumeric / non-whitespace characters with a space.
    #    \w in re matches [a-zA-Z0-9_]; we additionally strip underscores
    #    (alphabetically ambiguous) so the char set is purely alphanumeric.
    text = re.sub(r"[^\w\s]", " ", text)
    text = text.replace("_", " ")

    # 4. Collapse whitespace, strip, lowercase
    text = re.sub(r"\s+", " ", text).strip().lower()

    return text


def normalize_author(text: Optional[str]) -> str:
    """Normalise an author name to a comparable last-name-only string.

    The function is designed to handle the varying formats returned by
    different bibliographic databases and gold-standard CSVs:

    - PubMed metadata cache: ``"Smith"`` (``AuthorList[0].LastName`` — already
      last name only)
    - Scopus metadata cache: ``"Smith"`` (``dc:creator`` split on comma)
    - WOS metadata cache:    ``"Smith"`` (``displayName`` split on comma)
    - Embase metadata cache: ``"Smith"`` (from imported CSV)
    - Gold CSV variants:     ``"Smith"``, ``"Smith, J."```, ``"John Smith"``

    Normalisation pipeline
    ----------------------
    1. Return ``""`` for None or empty input.
    2. Decode HTML entities.
    3. Unicode NFD + strip combining characters (removes accents: García→Garcia).
    4. Last-name extraction:
       a. If the string contains a comma, take the part before the first comma
          (handles ``"Last, First Middle"`` → ``"Last"``).
       b. Otherwise take the last whitespace-separated token
          (handles ``"First Last"`` → ``"Last"``,
          ``"van der Berg"`` → ``"Berg"``).
    5. Keep only alphabetic characters, lowercase.

    Note: both gold and candidate strings go through the same normalisation,
    so minor format differences cancel out at comparison time.  The resulting
    strings are compared with ``rapidfuzz.fuzz.ratio`` — an edit-distance
    based metric well-suited for last-name matching.

    Examples
    --------
    >>> normalize_author("Smith")
    'smith'
    >>> normalize_author("Smith, John A.")
    'smith'
    >>> normalize_author("John Smith")
    'smith'
    >>> normalize_author("García")
    'garcia'
    >>> normalize_author("van der Berg")
    'berg'
    >>> normalize_author(None)
    ''
    """
    if not text:
        return ""

    # HTML entity decoding
    text = html.unescape(text)

    # NFD + strip combining chars (accents)
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))

    # Last-name extraction
    if "," in text:
        # "Last, First M." → "Last"
        text = text.split(",")[0]
    else:
        # "First Last" or "van der Berg" → last token
        parts = text.split()
        text = parts[-1] if parts else text

    # Keep only alphabetic characters, lowercase
    text = re.sub(r"[^a-zA-Z]", "", text).lower()

    return text


def extract_year(value: Union[int, float, str, None]) -> Optional[int]:
    """Parse a publication year from a numeric or string value.

    Accepts ints, floats, and strings (the latter may contain surrounding
    text such as ``"Jan 2023"`` or ``"2023-05-15"``).

    Returns the year as an ``int`` in the range [1000, 2100], or ``None``
    if the value is None, empty, or cannot be parsed.  The upper bound of
    2100 is intentionally generous to avoid false negatives for future
    publications while excluding obviously invalid multi-digit sequences.

    For strings, only the first ``\\b(\\d{4})\\b`` word-boundary match is
    used — this correctly rejects 5-digit strings such as ``"10023"`` and
    DOI fragments like ``"10.1016"``.

    Examples
    --------
    >>> extract_year(2023)
    2023
    >>> extract_year("2023")
    2023
    >>> extract_year("Jan 2023")
    2023
    >>> extract_year(2023.0)
    2023
    >>> extract_year(None)
    >>> extract_year("no year here")
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        year = int(value)
        if 1000 <= year <= 2100:
            return year
        return None

    text = str(value).strip()
    if not text:
        return None

    # Find first 4-digit sequence bounded by non-word characters or
    # string start/end.  Word boundaries (\b) prevent matching 4-digit
    # substrings inside longer digit sequences (e.g., "10023").
    match = re.search(r"\b(\d{4})\b", text)
    if match:
        year = int(match.group(1))
        if 1000 <= year <= 2100:
            return year

    return None


# ─────────────────────────────────────────────────────────────────────────────
# Core fuzzy matching function
# ─────────────────────────────────────────────────────────────────────────────

def fuzzy_match_article(
    gold,
    candidate_meta: dict,
    thresholds: Optional[dict] = None,
) -> Optional[float]:
    """Layer 3 fuzzy fallback: match a gold article against a retrieved candidate.

    Compares the gold article (a ``RichGoldArticle`` or any duck-typed object
    exposing ``.title``, ``.first_author``, ``.year`` attributes) against a
    candidate metadata dict from W4.1's ``_metadata_cache``.

    Matching rule
    -------------
    - **Title** (primary):  ``token_sort_ratio(norm_gold, norm_cand)``
                            ≥ ``thresholds['title']``
    - **First author** (secondary): ``ratio(norm_gold, norm_cand)``
                                    ≥ ``thresholds['author']``
    - **Year** (secondary): ``abs(gold_year - cand_year)``
                            ≤ ``thresholds['year_diff']``

    A field is **testable** only when *both* the gold record and the candidate
    carry a non-empty value for it.  If fewer than 2 fields are testable (or
    fewer than 2 pass their thresholds), the function returns ``None``.

    This requirement prevents false positives such as:
    - Two reviews with near-identical generic titles but different contexts.
    - An article matched purely on year with no title information.

    Parameters
    ----------
    gold : RichGoldArticle or duck-typed object
        Gold-standard article with attributes ``title``, ``first_author``,
        ``year`` (all may be None).
    candidate_meta : dict
        Metadata dict as produced by W4.1 ``_metadata_cache`` entries.
        Expected keys: ``'title'``, ``'first_author'``, ``'year'``
        (subset is fine; missing keys are treated as unavailable).
    thresholds : dict, optional
        Override per-field thresholds.  Any key absent from this dict falls
        back to ``DEFAULT_THRESHOLDS``.  Supported keys:
        ``'title'`` (int 0-100), ``'author'`` (int 0-100),
        ``'year_diff'`` (int ≥ 0).

    Returns
    -------
    float
        Confidence score in [0.0, 1.0] = ``matched_fields / testable_fields``
        when ≥ 2 fields are testable AND ≥ 2 fields pass their thresholds.
    None
        When the candidate cannot be confidently identified as a match:
        insufficient testable fields, insufficient fields pass threshold,
        or ``candidate_meta`` is falsy.

    Examples
    --------
    >>> from llm_sr_select_and_score import RichGoldArticle
    >>> gold = RichGoldArticle(title="Sleep apnea therapy", year=2020,
    ...                        first_author="Smith")
    >>> cand = {"title": "Sleep apnea therapy review", "year": 2020,
    ...         "first_author": "Smith"}
    >>> fuzzy_match_article(gold, cand)
    1.0
    """
    if not candidate_meta:
        return None

    effective = {**DEFAULT_THRESHOLDS, **(thresholds or {})}

    matched = 0
    testable = 0

    # ── Title (primary field) ─────────────────────────────────────────────────
    gold_title = normalize_title(getattr(gold, "title", None))
    cand_title = normalize_title(candidate_meta.get("title") or "")
    if gold_title and cand_title:
        testable += 1
        if _token_sort_ratio(gold_title, cand_title) >= effective["title"]:
            matched += 1

    # ── First author (secondary) ──────────────────────────────────────────────
    gold_author = normalize_author(getattr(gold, "first_author", None))
    cand_author = normalize_author(candidate_meta.get("first_author") or "")
    if gold_author and cand_author:
        testable += 1
        if _ratio(gold_author, cand_author) >= effective["author"]:
            matched += 1

    # ── Year (secondary) ──────────────────────────────────────────────────────
    gold_year = extract_year(getattr(gold, "year", None))
    cand_year = extract_year(candidate_meta.get("year"))
    if gold_year is not None and cand_year is not None:
        testable += 1
        if abs(gold_year - cand_year) <= effective["year_diff"]:
            matched += 1

    # ── Matching rule: require ≥ 2 testable fields AND ≥ 2 matched ───────────
    if testable < 2 or matched < 2:
        return None

    return matched / testable
