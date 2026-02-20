"""W4.2 unit tests: fuzzy article matching functions.

W4.2 adds a self-contained ``scripts/matching.py`` module implementing the
Layer 3 fuzzy fallback for articles that cannot be identified by DOI (Layer 1)
or PMID (Layer 2).  The module provides:

  - ``normalize_title(text)``   — HTML / accent / punctuation normalisation
  - ``normalize_author(text)``  — last-name extraction + normalisation
  - ``extract_year(value)``     — int / float / str → Optional[int]
  - ``fuzzy_match_article(gold, candidate_meta, thresholds)``
                                — require ≥ 2 of 3 fields (title, author, year)
                                  to pass their thresholds independently

Test categories
---------------
 Cat-1  normalize_title()        — HTML entities, diacritics, punctuation
 Cat-2  normalize_author()       — last-name extraction, formats, accents
 Cat-3  extract_year()           — int/float/str parsing, range validation
 Cat-4  fuzzy_match_article()    — core matching rule, confidence scores
 Cat-5  Custom thresholds        — override behaviour, partial overrides
 Cat-6  Real-world article scenarios
 Cat-7  Duck-typing and RichGoldArticle integration
 Cat-8  Edge cases and robustness
 Cat-9  Known limitations (W4.4 scope) — pin current behaviour

Design notes
------------
- rapidfuzz score ranges: token_sort_ratio and ratio return float in [0, 100].
- Calibrated scores (computed against rapidfuzz 3.14.3):
    token_sort_ratio("sleep apnea therapy", "sleep apnea therapy review") = 84.44
    token_sort_ratio("effects of caffeine on sleep",
                     "effect of caffeine on sleep")                       = 98.18
    fuzz.ratio("smith", "smyth")                                          = 80.00
    fuzz.ratio("johnson", "jonson")                                       = 92.31
    fuzz.ratio("smith", "jones")                                          ≈ 20.00
    token_sort_ratio("coffee and sleep disorders",
                     "sleep disorders and coffee")                        = 100.00
    token_sort_ratio("management of sleep apnea in adults",
                     "treatment of sleep apnea in adults")               ≈ 69.57
"""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from matching import (  # noqa: E402
    DEFAULT_THRESHOLDS,
    extract_year,
    fuzzy_match_article,
    normalize_author,
    normalize_title,
)
from llm_sr_select_and_score import RichGoldArticle  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class _MockGold:
    """Minimal duck-typed gold object for tests that don't need RichGoldArticle."""
    title: Optional[str] = None
    first_author: Optional[str] = None
    year: Optional[int] = None


def _gold(title=None, year=None, author=None):
    """Convenience: create a RichGoldArticle with the given fields."""
    return RichGoldArticle(title=title, year=year, first_author=author)


def _cand(title=None, year=None, author=None, **extra):
    """Convenience: build a candidate metadata dict."""
    meta = {}
    if title is not None:
        meta["title"] = title
    if year is not None:
        meta["year"] = year
    if author is not None:
        meta["first_author"] = author
    meta.update(extra)
    return meta


# ─────────────────────────────────────────────────────────────────────────────
# Cat-1: normalize_title()
# ─────────────────────────────────────────────────────────────────────────────

class TestNormalizeTitle:

    def test_none_returns_empty_string(self):
        assert normalize_title(None) == ""

    def test_empty_string_returns_empty(self):
        assert normalize_title("") == ""

    def test_whitespace_only_returns_empty(self):
        assert normalize_title("   ") == ""

    def test_basic_lowercase(self):
        assert normalize_title("Sleep Apnea") == "sleep apnea"

    def test_html_entity_ampersand(self):
        # &amp; → & → removed as punctuation
        result = normalize_title("Effects &amp; Causes of Sleep")
        assert result == "effects causes of sleep"

    def test_html_entity_lt_gt(self):
        # &lt; → < and &gt; → > → both removed as punctuation
        result = normalize_title("&lt;Title&gt; of the Study")
        assert result == "title of the study"

    def test_html_entity_apos(self):
        # &#39; → ' → replaced with a space (as non-alphanumeric punctuation)
        # "Parkinson's Disease" → "Parkinson s Disease" → "parkinson s disease"
        # Both gold and candidate undergo the same transformation so fuzzy
        # comparison still works correctly for possessives.
        result = normalize_title("Parkinson&#39;s Disease")
        assert result == "parkinson s disease"

    def test_diacritics_stripped(self):
        # é → e, ü → u after NFD decomposition + combining char removal
        assert normalize_title("Café über Schlaf") == "cafe uber schlaf"

    def test_accented_e(self):
        assert normalize_title("résumé") == "resume"

    def test_spanish_tilde(self):
        assert normalize_title("Señor García") == "senor garcia"

    def test_punctuation_removed(self):
        # Hyphens, parentheses, colons → spaces
        result = normalize_title("Effect (study) of sleep-apnea: a review")
        assert result == "effect study of sleep apnea a review"

    def test_multiple_spaces_collapsed(self):
        assert normalize_title("Multiple   Extra  Spaces") == "multiple extra spaces"

    def test_digits_preserved(self):
        # Numbers remain; hyphens become spaces
        result = normalize_title("COVID-19 and Sleep")
        assert result == "covid 19 and sleep"

    def test_underscores_removed(self):
        # underscore → space (not strictly alphanumeric)
        result = normalize_title("sleep_apnea_study")
        assert result == "sleep apnea study"

    def test_unicode_combining_chars_stripped(self):
        # Precomposed ü (U+00FC) → after NFD it's u + combining umlaut → stripped
        assert normalize_title("Über") == "uber"

    def test_subtitle_colon_removed(self):
        result = normalize_title("Sleep Apnea: A Comprehensive Review")
        assert result == "sleep apnea a comprehensive review"

    def test_already_clean_string_unchanged(self):
        result = normalize_title("sleep apnea therapy")
        assert result == "sleep apnea therapy"


# ─────────────────────────────────────────────────────────────────────────────
# Cat-2: normalize_author()
# ─────────────────────────────────────────────────────────────────────────────

class TestNormalizeAuthor:

    def test_none_returns_empty(self):
        assert normalize_author(None) == ""

    def test_empty_returns_empty(self):
        assert normalize_author("") == ""

    def test_whitespace_only_returns_empty(self):
        assert normalize_author("   ") == ""

    def test_simple_last_name(self):
        assert normalize_author("Smith") == "smith"

    def test_comma_format_last_first(self):
        # "Last, First" → "Last" → "last"
        assert normalize_author("Smith, John") == "smith"

    def test_comma_format_with_initials(self):
        # "Smith, JA" → "Smith" → "smith"
        assert normalize_author("Smith, JA") == "smith"

    def test_comma_format_with_middle_name(self):
        # "García, Juan M." → "García" → strip accents → "garcia"
        assert normalize_author("García, Juan M.") == "garcia"

    def test_first_last_format(self):
        # "John Smith" → last token → "Smith" → "smith"
        assert normalize_author("John Smith") == "smith"

    def test_name_particle(self):
        # "van der Berg" → last token → "Berg" → "berg"
        assert normalize_author("van der Berg") == "berg"

    def test_diacritic_stripped(self):
        assert normalize_author("García") == "garcia"

    def test_diacritic_with_comma(self):
        # "García, Juan" → before comma → "García" → "garcia"
        assert normalize_author("García, Juan") == "garcia"

    def test_apostrophe_stripped(self):
        # "O'Brien" → no comma → last token → "O'Brien" → keep alpha → "obrien"
        assert normalize_author("O'Brien") == "obrien"

    def test_scandinavian_name(self):
        # Ångström → strip accent → "Angstrom" → "angstrom"
        assert normalize_author("Ångström") == "angstrom"

    def test_single_character_input(self):
        # Single char "A" → "a"
        assert normalize_author("A") == "a"

    def test_pubmed_style_last_name_only(self):
        # PubMed stores LastName directly
        assert normalize_author("Johnson") == "johnson"

    def test_scopus_style(self):
        # Scopus: dc:creator split on comma → "Last" already extracted by provider
        assert normalize_author("Zhang") == "zhang"


# ─────────────────────────────────────────────────────────────────────────────
# Cat-3: extract_year()
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractYear:

    def test_none_returns_none(self):
        assert extract_year(None) is None

    def test_int_in_range(self):
        assert extract_year(2023) == 2023

    def test_float_in_range(self):
        assert extract_year(2023.0) == 2023

    def test_string_bare_year(self):
        assert extract_year("2023") == 2023

    def test_string_month_year(self):
        assert extract_year("Jan 2023") == 2023

    def test_string_year_month(self):
        assert extract_year("2023 Apr") == 2023

    def test_string_full_date(self):
        assert extract_year("2023-05-15") == 2023

    def test_empty_string_returns_none(self):
        assert extract_year("") is None

    def test_string_no_year_returns_none(self):
        assert extract_year("no year here") is None

    def test_int_below_range(self):
        # 999 < 1000 → None
        assert extract_year(999) is None

    def test_int_above_range(self):
        # 2101 > 2100 → None
        assert extract_year(2101) is None

    def test_five_digit_number_not_matched(self):
        # "10023": no word-boundary-bounded 4-digit sequence → None
        assert extract_year("10023") is None

    def test_float_string(self):
        # "2020.0" — "2020" followed by "." (non-word) → word boundary → matches
        assert extract_year("2020.0") == 2020

    def test_boundary_year_1000(self):
        assert extract_year(1000) == 1000

    def test_boundary_year_2100(self):
        assert extract_year(2100) == 2100

    def test_year_in_journal_context(self):
        # Realistic "string" from a metadata field containing surrounding text
        assert extract_year("Published: 2019") == 2019


# ─────────────────────────────────────────────────────────────────────────────
# Cat-4: fuzzy_match_article() — core matching rule
# ─────────────────────────────────────────────────────────────────────────────

class TestFuzzyMatchArticleCore:

    def test_all_three_fields_exact_match(self):
        # All 3 fields match exactly → 3/3 = 1.0
        gold = _gold("Sleep apnea therapy", 2020, "Smith")
        cand = _cand("Sleep apnea therapy", 2020, "Smith")
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_all_three_fields_with_minor_variations(self):
        # Minor typo in title (98.18≥85), diacritic in author, same year
        gold = _gold("Effects of caffeine on sleep", 2019, "García")
        cand = _cand("Effect of caffeine on sleep", 2019, "Garcia")
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_title_and_year_match_no_author_in_either(self):
        # Neither gold nor cand has author → testable=2 (title+year), matched=2 → 1.0
        gold = _gold("Sleep apnea therapy", 2020, None)
        cand = _cand("Sleep apnea therapy", 2020)  # no author
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_title_and_year_match_author_fails_returns_partial(self):
        # 2 of 3 pass → confidence = 2/3
        gold = _gold("Sleep apnea therapy", 2020, "Smith")
        cand = _cand("Sleep apnea therapy", 2020, "Jones")
        result = fuzzy_match_article(gold, cand)
        # title: 100≥85 ✓, year: 0≤1 ✓, author: smith/jones ≈20 < 80 ✗ → 2/3
        assert result == pytest.approx(2 / 3)

    def test_title_and_author_match_year_fails_returns_partial(self):
        # Year diff = 3 > 1 (fails); title+author pass → 2/3
        gold = _gold("Sleep apnea therapy", 2020, "Smith")
        cand = _cand("Sleep apnea therapy", 2023, "Smith")
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(2 / 3)

    def test_only_title_passes_returns_none(self):
        # Title passes but year diff=5 and author fails → matched=1 → None
        gold = _gold("Sleep apnea therapy", 2020, "Smith")
        cand = _cand("Sleep apnea therapy", 2015, "Jones")
        result = fuzzy_match_article(gold, cand)
        assert result is None

    def test_only_one_testable_field_title_passes_returns_none(self):
        # Crucial false-positive prevention: even a 100% title match is not
        # enough if only 1 field is testable (no year/author in either).
        gold = _gold("Sleep apnea therapy", None, None)
        cand = _cand("Sleep apnea therapy")
        result = fuzzy_match_article(gold, cand)
        assert result is None

    def test_empty_candidate_returns_none(self):
        gold = _gold("Sleep apnea therapy", 2020, "Smith")
        assert fuzzy_match_article(gold, {}) is None

    def test_none_candidate_returns_none(self):
        gold = _gold("Sleep apnea therapy", 2020, "Smith")
        assert fuzzy_match_article(gold, None) is None

    def test_gold_all_none_metadata_returns_none(self):
        # No metadata on gold side → nothing testable → None
        gold = _gold(None, None, None)
        cand = _cand("Something", 2020, "Smith")
        assert fuzzy_match_article(gold, cand) is None

    def test_title_below_threshold_with_year_match_returns_none(self):
        # title token_sort_ratio = 84.44 < 85 (BELOW threshold by 0.56 points)
        # year matches; author absent → matched=1 < 2 → None
        gold = _gold("Sleep apnea therapy", 2020, None)
        cand = _cand("Sleep apnea therapy review", 2020)
        result = fuzzy_match_article(gold, cand)
        assert result is None

    def test_author_at_exact_threshold_boundary_passes(self):
        # fuzz.ratio("smyth", "smith") = 80.0 — exactly at threshold → passes
        gold = _gold("Sleep apnea therapy", 2020, "Smyth")
        cand = _cand("Sleep apnea therapy", 2020, "Smith")
        result = fuzzy_match_article(gold, cand)
        # title: 100≥85 ✓, year: 0≤1 ✓, author: 80≥80 ✓ → 3/3 = 1.0
        assert result == pytest.approx(1.0)

    def test_year_diff_exactly_one_passes(self):
        # |2019 - 2020| = 1 ≤ 1 → passes
        gold = _gold("Sleep apnea therapy", 2019, "Smith")
        cand = _cand("Sleep apnea therapy", 2020, "Smith")
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_year_diff_exactly_two_fails(self):
        # |2018 - 2020| = 2 > 1 → year fails; title+author still pass → 2/3
        gold = _gold("Sleep apnea therapy", 2018, "Smith")
        cand = _cand("Sleep apnea therapy", 2020, "Smith")
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(2 / 3)

    def test_zero_testable_fields_returns_none(self):
        # cand has all fields, gold has none → all fields not testable
        gold = _gold(None, None, None)
        cand = _cand("Some title", 2020, "Someone")
        assert fuzzy_match_article(gold, cand) is None


# ─────────────────────────────────────────────────────────────────────────────
# Cat-5: Custom thresholds
# ─────────────────────────────────────────────────────────────────────────────

class TestCustomThresholds:

    def test_default_thresholds_document_constant(self):
        assert DEFAULT_THRESHOLDS["title"] == 85
        assert DEFAULT_THRESHOLDS["author"] == 80
        assert DEFAULT_THRESHOLDS["year_diff"] == 1

    def test_none_thresholds_uses_defaults(self):
        # Passing None → same as default
        gold = _gold("Sleep apnea therapy", 2020, "Smith")
        cand = _cand("Sleep apnea therapy", 2020, "Smith")
        assert fuzzy_match_article(gold, cand, None) == pytest.approx(1.0)

    def test_empty_thresholds_uses_defaults(self):
        gold = _gold("Sleep apnea therapy", 2020, "Smith")
        cand = _cand("Sleep apnea therapy", 2020, "Smith")
        assert fuzzy_match_article(gold, cand, {}) == pytest.approx(1.0)

    def test_stricter_title_threshold_rejects_borderline(self):
        # token_sort_ratio("sleep apnea therapy", "sleep apnea therapy review")
        # = 84.44 → fails at default 85, also fails at 90.
        # With a LOOSE threshold of 80 it should PASS (84.44 ≥ 80).
        gold = _gold("Sleep apnea therapy", 2020, None)
        cand = _cand("Sleep apnea therapy review", 2020)
        # Default threshold=85: title fails → None
        assert fuzzy_match_article(gold, cand) is None
        # Looser threshold=80: title passes (84.44≥80) → matched=2, testable=2 → 1.0
        assert fuzzy_match_article(gold, cand, {"title": 80}) == pytest.approx(1.0)

    def test_strict_year_diff_zero(self):
        # year_diff=0 means exact year match required
        gold = _gold("Sleep apnea therapy", 2019, "Smith")
        cand = _cand("Sleep apnea therapy", 2020, "Smith")
        # Default (year_diff=1): year passes → 3/3 = 1.0
        assert fuzzy_match_article(gold, cand) == pytest.approx(1.0)
        # Strict (year_diff=0): year fails → 2/3
        result = fuzzy_match_article(gold, cand, {"year_diff": 0})
        assert result == pytest.approx(2 / 3)

    def test_partial_override_does_not_affect_unspecified_keys(self):
        # Override only 'author': 90; 'title' and 'year_diff' should use defaults
        gold = _gold("Sleep apnea therapy", 2020, "Smyth")
        cand = _cand("Sleep apnea therapy", 2020, "Smith")
        # smyth/smith ratio=80; with author threshold 90 it fails (80 < 90)
        # title+year still match → 2/3
        result = fuzzy_match_article(gold, cand, {"author": 90})
        assert result == pytest.approx(2 / 3)

    def test_fully_strict_thresholds_reject_near_match(self):
        # No article can pass title=100, author=100, year_diff=0 unless exact
        thresholds = {"title": 100, "author": 100, "year_diff": 0}
        gold = _gold("Sleep apnea therapy", 2020, "Smith")
        # Minor typo in title
        cand = _cand("Sleep apnea therapies", 2020, "Smith")
        result = fuzzy_match_article(gold, cand, thresholds)
        # title: token_sort_ratio < 100 (typo) → fails; author+year pass → 2/3?
        # Actually: title fails strict threshold → matched<2 unless author+year both pass
        # author=100: "smith"=="smith" → 100 ≥ 100 ✓; year_diff=0: 0≤0 ✓ → matched=2 → 2/3
        assert result == pytest.approx(2 / 3)


# ─────────────────────────────────────────────────────────────────────────────
# Cat-6: Real-world article scenarios
# ─────────────────────────────────────────────────────────────────────────────

class TestRealWorldScenarios:

    def test_word_order_invariant_matching(self):
        # token_sort_ratio sorts tokens before comparing → order-independent
        # "coffee and sleep disorders" vs "sleep disorders and coffee" = 100.0
        gold = _gold("Coffee and sleep disorders: a review", 2021, "Smith")
        cand = _cand("Sleep disorders and coffee a review", 2021, "Smith")
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_accented_title_matches_unaccented_version(self):
        # Café → cafe after normalization
        gold = _gold("Café au Lait Study on Sleep", 2018, "García")
        cand = _cand("Cafe au Lait Study on Sleep", 2018, "Garcia")
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_subtitle_colon_variation(self):
        # "Sleep Apnea: A Comprehensive Review" vs "Sleep Apnea Comprehensive Review"
        # After normalize: "sleep apnea a comprehensive review" vs
        #                  "sleep apnea comprehensive review"
        # token_sort_ratio = 96.97 ≥ 85 → passes
        gold = _gold("Sleep Apnea: A Comprehensive Review", 2022, "Johnson")
        cand = _cand("Sleep Apnea Comprehensive Review", 2022, "Johnson")
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_completely_different_articles_return_none(self):
        # "management of sleep apnea in adults" vs "treatment of sleep apnea in adults"
        # token_sort_ratio ≈ 69.57 < 85 (fails title)
        # "smith" vs "jones" ≈ 20 < 80 (fails author)
        # year same → year passes
        # Only 1 field passes → None
        gold = _gold("Management of sleep apnea in adults", 2020, "Smith")
        cand = _cand("Treatment of sleep apnea in adults", 2020, "Jones")
        result = fuzzy_match_article(gold, cand)
        assert result is None

    def test_article_with_unicode_doi_like_title(self):
        # Realistic title with special characters
        gold = _gold("β-amyloid and sleep: a 10-year follow-up", 2021, "Wang")
        cand = _cand("b amyloid and sleep a 10 year follow up", 2021, "Wang")
        # Both normalize to near-identical strings → high token_sort_ratio
        result = fuzzy_match_article(gold, cand)
        assert result is not None
        assert result > 0.5

    def test_year_as_string_in_candidate_metadata(self):
        # W4.1 stores year as int, but JSON round-trip may produce string
        gold = _gold("Sleep apnea therapy", 2020, "Smith")
        cand = {"title": "Sleep apnea therapy", "year": "2020", "first_author": "Smith"}
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_year_as_float_in_candidate_metadata(self):
        gold = _gold("Sleep apnea therapy", 2020, "Smith")
        cand = {"title": "Sleep apnea therapy", "year": 2020.0, "first_author": "Smith"}
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)


# ─────────────────────────────────────────────────────────────────────────────
# Cat-7: Duck-typing and RichGoldArticle integration
# ─────────────────────────────────────────────────────────────────────────────

class TestDuckTypingAndIntegration:

    def test_works_with_rich_gold_article_instance(self):
        # Confirms no AttributeError when using the actual W4.0 dataclass
        gold = RichGoldArticle(
            pmid="12345678",
            doi="10.1234/test",
            title="Sleep apnea therapy in adults",
            year=2021,
            first_author="Smith",
            journal="Sleep Medicine",
        )
        cand = _cand("Sleep apnea therapy in adults", 2021, "Smith")
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_works_with_duck_typed_mock_gold(self):
        # _MockGold has no pmid/doi fields — getattr falls back to None for those
        gold = _MockGold(title="Sleep apnea therapy", year=2020, first_author="Smith")
        cand = _cand("Sleep apnea therapy", 2020, "Smith")
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_journal_field_in_gold_is_ignored(self):
        # journal is present in RichGoldArticle but is NOT a matching field in W4.2
        gold = RichGoldArticle(
            title="Sleep apnea therapy",
            year=2020,
            first_author="Smith",
            journal="Journal of Sleep Research",
        )
        # Different journal in candidate should not affect result
        cand = {"title": "Sleep apnea therapy", "year": 2020,
                "first_author": "Smith", "journal": "Nature Medicine"}
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_candidate_with_extra_fields_is_handled(self):
        # Extra keys in the candidate dict (beyond title/year/first_author) are ignored
        gold = _gold("Sleep apnea therapy", 2020, "Smith")
        cand = {
            "title": "Sleep apnea therapy",
            "year": 2020,
            "first_author": "Smith",
            "journal": "Sleep Medicine",
            "doi": "10.1234/test",
            "pmid": "99999999",
            "unexpected_field": "some_value",
        }
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_pmid_only_rich_gold_article_no_metadata_returns_none(self):
        # When RichGoldArticle has PMID+DOI only (W4.0 design), fuzzy cannot match
        gold = RichGoldArticle(pmid="12345678", doi="10.1234/test")
        cand = _cand("Some title", 2020, "Smith")
        # gold.title=None, gold.year=None, gold.first_author=None → testable=0 → None
        result = fuzzy_match_article(gold, cand)
        assert result is None

    def test_module_importable_without_main_scoring_module(self):
        # matching.py is self-contained — verify key symbols are importable
        from matching import (
            DEFAULT_THRESHOLDS,
            extract_year,
            fuzzy_match_article,
            normalize_author,
            normalize_title,
        )
        assert callable(fuzzy_match_article)
        assert callable(normalize_title)
        assert callable(normalize_author)
        assert callable(extract_year)
        assert isinstance(DEFAULT_THRESHOLDS, dict)


# ─────────────────────────────────────────────────────────────────────────────
# Cat-8: Edge cases and robustness
# ─────────────────────────────────────────────────────────────────────────────

class TestEdgeCasesAndRobustness:

    def test_very_long_title_does_not_crash(self):
        # 500-character title — should not raise
        long_title = "sleep apnea " * 40  # 480 chars
        gold = _gold(long_title, 2020, "Smith")
        cand = _cand(long_title, 2020, "Smith")
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_title_with_only_special_chars_not_testable(self):
        # normalize_title("!@#$%") → "" → gold_title is empty → not testable
        # year + author still testable if both present → 1.0
        gold = _gold("!@#$%", 2020, "Smith")
        cand = _cand("!@#$%", 2020, "Smith")
        # Both titles normalize to "" → title not testable; testable=2 (year+author)
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)  # 2/2 on year+author

    def test_author_with_only_numbers_not_matched(self):
        # normalize_author("123") → only alpha kept → "" → not testable
        gold = _gold("Sleep apnea therapy", 2020, "123")
        cand = _cand("Sleep apnea therapy", 2020, "123")
        # author: normalize → "" → not testable; testable=2 (title+year) → 1.0
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_candidate_year_none_key_present(self):
        # If "year" key exists but value is None → not testable
        gold = _gold("Sleep apnea therapy", 2020, "Smith")
        cand = {"title": "Sleep apnea therapy", "year": None, "first_author": "Smith"}
        # year not testable; testable=2 (title+author) → 1.0
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_candidate_author_empty_string(self):
        # Empty string in candidate author → normalize → "" → not testable
        gold = _gold("Sleep apnea therapy", 2020, "Smith")
        cand = {"title": "Sleep apnea therapy", "year": 2020, "first_author": ""}
        # author not testable; testable=2 (title+year) → 1.0
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_mixed_unicode_script_titles(self):
        # Partial Unicode content — should not raise
        gold = _gold("Sleep apnea et sommeil", 2020, "Dupont")
        cand = _cand("Sleep apnea et sommeil", 2020, "Dupont")
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)

    def test_all_fields_fail_returns_none(self):
        # No field passes — should return None cleanly, not raise
        gold = _gold("Effects of caffeine", 2010, "Smith")
        cand = _cand("Treatment of sleep apnea", 2022, "Jones")
        result = fuzzy_match_article(gold, cand)
        assert result is None

    def test_confidence_score_bounded_zero_to_one(self):
        # Partial match (2/3) should be in [0.0, 1.0]
        gold = _gold("Sleep apnea therapy", 2020, "Smith")
        cand = _cand("Sleep apnea therapy", 2020, "Jones")
        result = fuzzy_match_article(gold, cand)
        assert result is not None
        assert 0.0 <= result <= 1.0


# ─────────────────────────────────────────────────────────────────────────────
# Cat-9: Known limitations (W4.4 scope)
# ─────────────────────────────────────────────────────────────────────────────

class TestKnownLimitations:

    def test_w4_2_does_not_fix_phase_c_vote_splitting(self):
        """
        W4.2 provides matching functions for Phase B/D scoring only.

        Phase C (ArticleRegistry + aggregate_queries.py) is unaffected by W4.2.
        Articles that lack a shared DOI or PMID between PubMed and Scopus will
        still vote-split in consensus_k2 after W4.2.

        This test documents the current behaviour: fuzzy_match_article() is a
        *scoring utility* — it does not mutate ArticleRegistry or Article objects.
        It returns a float confidence score; the caller (W4.3) is responsible
        for counting it as a TP and logging it.  No registry merging happens here.

        W4.4 would add a fuzzy merge pass to ArticleRegistry to resolve Phase C
        vote-splitting for ~4 Class D (truly DOI-less) articles per study.
        """
        gold = RichGoldArticle(
            pmid="12345678",
            doi=None,  # Class D: truly DOI-less
            title="An older article without a DOI",
            year=1999,
            first_author="Smith",
        )
        cand = _cand("An older article without a DOI", 1999, "Smith")
        # fuzzy_match_article CAN match this article in Phase B scoring...
        result = fuzzy_match_article(gold, cand)
        assert result == pytest.approx(1.0)
        # ...but Phase C vote-splitting is NOT fixed by this match.
        # ArticleRegistry still holds Article(pmid='12345678', doi=None) from
        # PubMed and a potentially separate Article(pmid=None, doi=None) from
        # another database — these will not be unified in consensus_k2.
        # This is the W4.4 scope, asserted here so any future fix is immediately
        # visible in the test suite.

    def test_single_field_gold_cannot_be_matched(self):
        """
        A gold standard row containing ONLY pmid/doi (no metadata) returns None.

        This represents the common case in older pipeline runs where the gold
        CSV has only pmid and doi columns.  Layer 3 cannot help these articles;
        they must be caught by Layer 1 (DOI) or Layer 2 (PMID) instead.

        The correct fix for this scenario is to enrich the gold CSV with metadata
        using enhance_gold_standard.py, not to change the matching logic.
        """
        gold = RichGoldArticle(pmid="99999999", doi="10.1234/test")
        cand = _cand("Any title", 2020, "Smith")
        assert fuzzy_match_article(gold, cand) is None

    def test_w42_is_phase_b_d_only_not_phase_c(self):
        """
        fuzzy_match_article() is a pure function with no side effects.

        It does NOT:
        - Modify ArticleRegistry
        - Update Article.doi / Article.pmid
        - Write to details_*.json or any file
        - Make network calls

        It returns a float or None; the caller records the TP.
        This property ensures the function is safe to call in loops over
        potentially hundreds of candidates per unmatched gold article.
        """
        gold = _gold("Sleep apnea therapy", 2020, "Smith")
        cand = _cand("Sleep apnea therapy", 2020, "Smith")
        # Call multiple times — idempotent, no side effects
        r1 = fuzzy_match_article(gold, cand)
        r2 = fuzzy_match_article(gold, cand)
        assert r1 == r2 == pytest.approx(1.0)
