#!/usr/bin/env python3

from __future__ import annotations

import csv
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
BENCHMARK_DIR = BASE_DIR / "benchmark_outputs"
STUDIES_DIR = BASE_DIR / "studies"
ORIGINAL_DIR = BASE_DIR / "original_queries_markdown"
OUTPUT_PATH = BASE_DIR / "analysis_results" / "strategy_aware_q1_q2_vs_original_queries_20260409.md"

BENCHMARK_STUDIES = [
    "ai_2022",
    "Cid_Verdejo_2024_Paper",
    "Godos_2024",
    "lang_2024",
    "Lehner_2022",
    "Li_2024",
    "Medeiros_2023",
    "Nexha_2024",
    "Riedy_2021",
    "Varallo_2022",
]

ORIGINAL_QUERY_MAP = {
    "ai_2022": "Ai 2022 - Search queries.md",
    "Cid_Verdejo_2024_Paper": "Cid-Verdejo 2024 - Search queries.md",
    "lang_2024": "Lange 2024 - Search queries.md",
    "Lehner_2022": "Lehner 2022 - Search queries.md",
    "Riedy_2021": "Riedy 2021 - Search queries.md",
    "Varallo_2022": "Varallo 2022 - Search queries.md",
}

GENERATED_QUERY_FILES = {
    "pubmed": "queries.txt",
    "scopus": "queries_scopus.txt",
    "wos": "queries_wos.txt",
    "embase": "queries_embase.txt",
}

DATABASE_LABELS = {
    "pubmed": "PubMed",
    "scopus": "Scopus",
    "wos": "Web of Science",
    "embase": "Embase",
}


def normalize_space(text: str) -> str:
    return " ".join(text.replace("\xa0", " ").split())


def parse_generated_queries(file_path: Path) -> dict[str, str]:
    text = file_path.read_text()
    header_pattern = re.compile(
        r"^#\s+(?:Q(?P<short>[1-6])|Query\s+(?P<long>[1-6])):\s+.*$",
        flags=re.MULTILINE,
    )
    parsed = {}
    headers = list(header_pattern.finditer(text))
    for index, header in enumerate(headers):
        query_num = header.group("short") or header.group("long")
        if query_num not in {"1", "2"}:
            continue
        start = header.end()
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        parsed[f"Q{query_num}"] = normalize_space(text[start:end].strip())
    return parsed


def parse_original_queries(file_path: Path) -> dict[str, dict[str, str | int | None]]:
    text = file_path.read_text().replace("\r\n", "\n").replace("\xa0", " ")
    parsed = parse_original_search_string_sections(text)
    if parsed:
        return parsed
    parsed = parse_original_appendix_sections(text)
    if parsed:
        return parsed
    parsed = parse_original_blockquote_sections(text)
    if parsed:
        return parsed
    return parse_original_database_segments(text)


def parse_original_search_string_sections(text: str) -> dict[str, dict[str, str | int | None]]:
    lines = text.splitlines()
    result: dict[str, dict[str, str | int | None]] = {}
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if line.startswith("*Search string (") and line.endswith(")*"):
            db_name = line[len("*Search string (") : -2].strip().lower()
            db_key = map_original_database(db_name)
            index += 1
            while index < len(lines) and not lines[index].strip():
                index += 1
            query_lines = []
            while index < len(lines):
                current = lines[index].strip()
                if not current:
                    index += 1
                    continue
                if current.startswith("N"):
                    break
                if current.startswith("*Search string (") and current.endswith(")*"):
                    break
                query_lines.append(current)
                index += 1

            count = None
            while index < len(lines):
                current = lines[index].strip()
                if current.startswith("N"):
                    match = re.search(r"([0-9][0-9,]*)", current)
                    if match:
                        count = int(match.group(1).replace(",", ""))
                    index += 1
                    break
                if current.startswith("*Search string (") and current.endswith(")*"):
                    break
                index += 1

            result[db_key] = {
                "label": db_name,
                "query": normalize_space(" ".join(query_lines)),
                "reported_n": count,
            }
            continue
        index += 1
    return result


def parse_original_appendix_sections(text: str) -> dict[str, dict[str, str | int | None]]:
    lines = text.splitlines()
    result: dict[str, dict[str, str | int | None]] = {}
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if line.startswith("*Appendix") and "Search strategy for" in line:
            db_name = line.split("Search strategy for", 1)[1].strip().strip("*")
            db_key = map_original_database(db_name)
            index += 1
            section_lines = []
            while index < len(lines) and not lines[index].strip().startswith("*Appendix"):
                section_lines.append(lines[index].strip())
                index += 1
            count = None
            for section_line in section_lines:
                match = re.search(r"([0-9][0-9,]*)\s+results", section_line, flags=re.IGNORECASE)
                if match:
                    count = int(match.group(1).replace(",", ""))
                    break
            query_start = 0
            for line_index, section_line in enumerate(section_lines):
                if re.search(r"[0-9][0-9,]*\s+results", section_line, flags=re.IGNORECASE):
                    query_start = line_index + 1
                    break
            query = normalize_space(" ".join(section_lines[query_start:]))
            result[db_key] = {
                "label": db_name,
                "query": query,
                "reported_n": count,
            }
            continue
        index += 1
    return result


def parse_original_blockquote_sections(text: str) -> dict[str, dict[str, str | int | None]]:
    lines = text.splitlines()
    result: dict[str, dict[str, str | int | None]] = {}
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if line.startswith("> [") and "]" in line:
            db_name = line.split("[", 1)[1].split("]", 1)[0].strip()
            db_key = map_original_database(db_name)
            index += 1
            section_lines = []
            while index < len(lines) and not lines[index].strip().startswith("> ["):
                section_lines.append(lines[index].strip())
                index += 1
            result[db_key] = {
                "label": db_name,
                "query": normalize_space(" ".join(section_lines)),
                "reported_n": None,
            }
            continue
        index += 1
    return result


def parse_original_database_segments(text: str) -> dict[str, dict[str, str | int | None]]:
    cleaned = text
    for token in ("|", "+", "-", "=", "`", "{.mark}", "{.underline}"):
        cleaned = cleaned.replace(token, " ")
    cleaned = normalize_space(cleaned)

    label_patterns = {
        "pubmed": spaced_label_pattern("PubMed"),
        "scopus": spaced_label_pattern("Scopus"),
        "wos": spaced_label_pattern("Web of Science"),
        "embase": spaced_label_pattern("Embase"),
    }

    matches = []
    for key, pattern in label_patterns.items():
        match = re.search(pattern, cleaned, flags=re.IGNORECASE)
        if match:
            matches.append((match.start(), match.end(), key))
    matches.sort()

    result: dict[str, dict[str, str | int | None]] = {}
    for index, (_, end, key) in enumerate(matches):
        next_start = matches[index + 1][0] if index + 1 < len(matches) else len(cleaned)
        segment = cleaned[end:next_start].strip()
        if not segment:
            continue
        counts = re.findall(r"\b([0-9][0-9,]{2,})\b", segment)
        count = int(counts[-1].replace(",", "")) if counts else None
        result[key] = {
            "label": DATABASE_LABELS.get(key, key),
            "query": segment,
            "reported_n": count,
        }
    return result


def spaced_label_pattern(label: str) -> str:
    pieces = []
    for char in label:
        if char == " ":
            pieces.append(r"\s+")
        else:
            pieces.append(re.escape(char) + r"\s*")
    return "".join(pieces)


def map_original_database(name: str) -> str:
    lower = name.lower()
    if "pubmed" in lower:
        return "pubmed"
    if "web of science" in lower:
        return "wos"
    if "embase" in lower:
        return "embase"
    if "scopus" in lower:
        return "scopus"
    return lower.replace(" ", "_")


def load_summary_row(study: str, query_num: int, database: str) -> tuple[Path, dict[str, str]]:
    summary_dir = BENCHMARK_DIR / study / f"query_{query_num:02d}"
    summary_files = sorted(summary_dir.glob("summary_per_database_*.csv"))
    if not summary_files:
        raise FileNotFoundError(f"Missing summary file for {study} Q{query_num}")
    summary_path = summary_files[-1]
    with summary_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row["database"] == database:
                return summary_path, row
    raise ValueError(f"Missing {database} row in {summary_path}")


def parse_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def parse_int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    return int(float(value))


def extract_features(query: str) -> set[str]:
    features: set[str] = set()
    lower = query.lower()
    if any(token in query for token in ("[Mesh]", "[Majr]", "[mh]", "/exp", "/de", ".mp.", " exp ")):
        features.add("controlled vocabulary")
    if any(token in lower for token in ("[tiab]", "title-abs-key(", "ts=(", ":ti,ab", ".ti,ab.")):
        features.add("fielded free text")
    if any(token in lower for token in ("child", "adolescent", "pediatric", "paediatric", "adult", "aged", "women", "men")):
        features.add("population restriction")
    if any(token in lower for token in ("cohort", "prospective", "retrospective", "trial", "observational", "cross-sectional", "case-control", "sensitivity and specificity", "diagnos", "valid", "agreement")):
        features.add("design or analytic restriction")
    if any(token in lower for token in ("english", "language", "humans[filter]", "doctype(", "dt=(article", "review[pt]", "publication type")):
        features.add("filter layer")
    return features


def feature_delta(q1: str, q2: str) -> str:
    q1_features = extract_features(q1)
    q2_features = extract_features(q2)
    added = sorted(q2_features - q1_features)
    removed = sorted(q1_features - q2_features)
    if not added and not removed:
        return "Q2 preserves the same feature profile as Q1 and mainly tightens wording or synonym scope."
    parts = []
    if added:
        parts.append("adds " + ", ".join(added))
    if removed:
        parts.append("drops " + ", ".join(removed))
    return "Q2 " + " and ".join(parts) + "."


def top_level_blocks(query: str) -> int:
    return query.count(" AND ") + 1


def short_query(query: str, limit: int = 220) -> str:
    query = normalize_space(query)
    if len(query) <= limit:
        return query
    return query[: limit - 3] + "..."


def main() -> None:
    lines: list[str] = []
    lines.append("# Strategy-Aware Q1/Q2 vs Original Paper Queries")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This comparison uses the latest benchmark summary CSV in each study's `benchmark_outputs/<study>/query_01` and `query_02` folder, and compares those Q1/Q2 results to the extracted original paper query markdown where that markdown is available.")
    lines.append("")
    lines.append("Direct text-to-text query comparison is possible for 6 of the 10 benchmark studies because only those 6 currently have extracted original query markdown in `original_queries_markdown/`.")
    lines.append("")
    lines.append("## System Inputs")
    lines.append("")
    lines.append("The strategy-aware generator is correctly wired to four evidence sources:")
    lines.append("")
    lines.append("- the per-study protocol file")
    lines.append("- `studies/guidelines.md`")
    lines.append("- `studies/general_guidelines.md`")
    lines.append("- `prompts/database_guidelines.md`")
    lines.append("")
    lines.append("`prompts/prompt_template_multidb_strategy_aware.md` explicitly states all three auxiliary guidance files and assigns them distinct roles: domain hierarchy from `studies/guidelines.md`, generic search-method rules from `studies/general_guidelines.md`, and database syntax and knob mapping from `prompts/database_guidelines.md`.")
    lines.append("")
    lines.append("## Comment on `studies/guidelines.md`")
    lines.append("")
    lines.append("`studies/guidelines.md` is a sleep-medicine-specific guidance document, centered on PubMed-oriented sleep filters. Its useful contribution to the generator is not database syntax but domain structure: sleep-disorder hierarchy, terminology expansion patterns, spelling variants, acronym caution, and the principle that free text should usually be fielded rather than left as raw automatic term mapping.")
    lines.append("")
    lines.append("Short summary: it is effectively a sleep-specific vocabulary and query-design aid. It helps the model expand within the right clinical concept family, but it should not override the protocol-defined concept architecture and it should not be treated as a cross-database syntax source.")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append("| Study | Q1/Q2 benchmark available | Original query markdown available |")
    lines.append("| --- | --- | --- |")

    original_available = set(ORIGINAL_QUERY_MAP)
    for study in BENCHMARK_STUDIES:
        has_original = "yes" if study in original_available else "no"
        lines.append(f"| {study} | yes | {has_original} |")

    lines.append("")
    lines.append("Studies without original query markdown in `original_queries_markdown/`: `Godos_2024`, `Li_2024`, `Medeiros_2023`, `Nexha_2024`.")
    lines.append("")
    lines.append("## Benchmark Results for Q1 and Q2")
    lines.append("")
    lines.append("The `results_count` below is the combined deduplicated count from the `COMBINED` row in the latest summary CSV for each query. `results_count_raw` is the raw total across providers before combined deduplication when available in the CSV.")
    lines.append("")
    lines.append("| Study | Query | Summary file | Combined dedup | Combined raw | TP | Gold | Recall |")
    lines.append("| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |")

    benchmark_rows: dict[tuple[str, int], dict[str, object]] = {}
    for study in BENCHMARK_STUDIES:
        for query_num in (1, 2):
            summary_path, row = load_summary_row(study, query_num, "COMBINED")
            benchmark_rows[(study, query_num)] = {
                "summary_path": summary_path,
                "results_count": parse_int(row.get("results_count")),
                "results_count_raw": parse_int(row.get("results_count_raw")),
                "tp": parse_int(row.get("TP")),
                "gold_size": parse_int(row.get("gold_size")),
                "recall": parse_float(row.get("recall")),
            }
            recall = benchmark_rows[(study, query_num)]["recall"]
            recall_text = "" if recall is None else f"{recall:.3f}"
            lines.append(
                "| "
                f"{study} | Q{query_num} | {summary_path.name} | "
                f"{benchmark_rows[(study, query_num)]['results_count']} | "
                f"{benchmark_rows[(study, query_num)]['results_count_raw']} | "
                f"{benchmark_rows[(study, query_num)]['tp']} | "
                f"{benchmark_rows[(study, query_num)]['gold_size']} | "
                f"{recall_text} |"
            )

    lines.append("")
    lines.append("## Original Query Files and Reported Ns")
    lines.append("")
    lines.append("These counts come from the markdown files in `original_queries_markdown/`. They are paper-reported counts, often database-specific and not normalized to the benchmark pipeline. They are useful for contextual comparison, not as a like-for-like replacement for the benchmark `COMBINED` counts.")
    lines.append("")
    lines.append("| Study | Database | Reported N in original markdown |")
    lines.append("| --- | --- | ---: |")

    original_query_data: dict[str, dict[str, dict[str, str | int | None]]] = {}
    for study, filename in ORIGINAL_QUERY_MAP.items():
        parsed = parse_original_queries(ORIGINAL_DIR / filename)
        original_query_data[study] = parsed
        for database, entry in parsed.items():
            label = DATABASE_LABELS.get(database, str(entry["label"]))
            lines.append(f"| {study} | {label} | {entry['reported_n']} |")

    lines.append("")
    lines.append("## Study-by-Study Query Comparison")
    lines.append("")

    for study in BENCHMARK_STUDIES:
        lines.append(f"### {study}")
        lines.append("")

        q1_metrics = benchmark_rows[(study, 1)]
        q2_metrics = benchmark_rows[(study, 2)]
        q1_pubmed = parse_generated_queries(STUDIES_DIR / study / GENERATED_QUERY_FILES["pubmed"])["Q1"]
        q2_pubmed = parse_generated_queries(STUDIES_DIR / study / GENERATED_QUERY_FILES["pubmed"])["Q2"]

        lines.append(
            f"- Benchmark outcome: Q1 retrieved {q1_metrics['results_count']} combined records with recall {q1_metrics['recall']:.3f}; "
            f"Q2 retrieved {q2_metrics['results_count']} combined records with recall {q2_metrics['recall']:.3f}."
        )
        lines.append(
            f"- Generated PubMed structure: Q1 has about {top_level_blocks(q1_pubmed)} top-level AND-linked blocks; "
            f"Q2 has about {top_level_blocks(q2_pubmed)}. {feature_delta(q1_pubmed, q2_pubmed)}"
        )
        lines.append(
            f"- Generated PubMed Q1 excerpt: `{short_query(q1_pubmed)}`"
        )
        lines.append(
            f"- Generated PubMed Q2 excerpt: `{short_query(q2_pubmed)}`"
        )

        if study in original_query_data:
            original_databases = ", ".join(
                DATABASE_LABELS.get(key, key) for key in sorted(original_query_data[study])
            )
            lines.append(f"- Original query markdown availability: {original_databases}.")
            for database in sorted(original_query_data[study]):
                entry = original_query_data[study][database]
                lines.append(
                    f"- Original {DATABASE_LABELS.get(database, database)} excerpt: `{short_query(str(entry['query']))}`"
                )
            original_features = sorted(
                {
                    feature
                    for entry in original_query_data[study].values()
                    for feature in extract_features(str(entry["query"]))
                }
            )
            if original_features:
                lines.append(
                    "- Original query feature profile: " + ", ".join(original_features) + "."
                )
            generated_features = sorted(extract_features(q1_pubmed) | extract_features(q2_pubmed))
            if generated_features:
                lines.append(
                    "- Generated Q1/Q2 feature profile: " + ", ".join(generated_features) + "."
                )
        else:
            lines.append("- Original query markdown availability: not available in `original_queries_markdown/`, so this study can only be compared on the benchmark-result side.")

        lines.append("")

    lines.append("## High-Level Takeaways")
    lines.append("")
    lines.append("- The prompt wiring is correct: the main strategy-aware template really does use the sleep-domain guidance, the general search-method guidance, and the database-specific syntax guidance in distinct roles.")
    lines.append("- `studies/guidelines.md` is best understood as a sleep-vocabulary and concept-hierarchy aid rather than a syntax guide. That matches how the prompt claims to use it.")
    lines.append("- The benchmark side is complete for 10 studies for Q1 and Q2.")
    lines.append("- The original-query text side is incomplete: only 6 of those 10 studies currently have extracted original query markdown in the folder you pointed to.")
    lines.append("- Because the original markdown mixes database-specific counts and paper-reporting conventions, the cleanest like-for-like quantitative comparison remains the benchmark Q1/Q2 table. The original markdown is most useful for structural comparison of query blocks, filters, and vocabulary choices.")

    OUTPUT_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()