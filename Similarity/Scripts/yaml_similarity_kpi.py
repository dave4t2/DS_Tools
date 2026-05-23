"""
yaml_similarity_kpi.py
Compare all YAML files in Tools/Similarity/Input_Yaml/ against the first file
(sorted by creation date) and produce a Markdown KPI report.

Usage:
    python Scripts/yaml_similarity_kpi.py [--threshold 0.95]
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import yaml

INPUT_DIR = Path(__file__).parent.parent / "Input_Yaml"
DEFAULT_THRESHOLD = 0.95


# ---------------------------------------------------------------------------
# File collection
# ---------------------------------------------------------------------------

def collect_files(directory: Path) -> list[tuple[Path, float]]:
    files = list(directory.glob("*.yml")) + list(directory.glob("*.yaml"))
    if not files:
        print(f"[ERROR] No .yml/.yaml files found in {directory}", file=sys.stderr)
        sys.exit(1)
    files.sort(key=lambda p: os.path.getctime(p))
    if len(files) < 2:
        print(
            f"[ERROR] At least 2 YAML files required in {directory} (found 1).",
            file=sys.stderr,
        )
        sys.exit(1)
    return [(p, os.path.getctime(p)) for p in files]


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> tuple[object, int]:
    """Return (parsed_obj, line_count). parsed_obj is None on error."""
    try:
        text = path.read_text(encoding="utf-8")
        line_count = len(text.splitlines())
        return yaml.safe_load(text), line_count
    except yaml.YAMLError as exc:
        print(f"[WARN] YAML parse error in {path.name}: {exc}", file=sys.stderr)
        try:
            line_count = len(path.read_text(encoding="utf-8").splitlines())
        except Exception:
            line_count = 0
        return None, line_count
    except Exception as exc:
        print(f"[WARN] Could not read {path.name}: {exc}", file=sys.stderr)
        return None, 0


# ---------------------------------------------------------------------------
# Recursive leaf counting and matching
# ---------------------------------------------------------------------------

def count_leaves(obj) -> int:
    if isinstance(obj, dict):
        return sum(count_leaves(v) for v in obj.values()) or 1
    if isinstance(obj, list):
        return sum(count_leaves(item) for item in obj) or 1
    return 1


def matching_leaves(a, b) -> int:
    if isinstance(a, dict) and isinstance(b, dict):
        total = 0
        for key in a:
            if key in b:
                total += matching_leaves(a[key], b[key])
        return total
    if isinstance(a, list) and isinstance(b, list):
        return sum(matching_leaves(x, y) for x, y in zip(a, b))
    return 1 if a == b else 0


# ---------------------------------------------------------------------------
# Similarity
# ---------------------------------------------------------------------------

def similarity(dict_a, dict_b) -> float:
    if dict_a is None or dict_b is None:
        return 0.0
    if dict_a == dict_b:
        return 1.0
    total = max(count_leaves(dict_a), count_leaves(dict_b))
    if total == 0:
        return 1.0
    return matching_leaves(dict_a, dict_b) / total


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def _fmt_delta(candidate_val: int, ref_val: int) -> str:
    delta = candidate_val - ref_val
    sign = "+" if delta > 0 else ""
    return f"{candidate_val} ({sign}{delta})" if delta != 0 else str(candidate_val)


def render_markdown(
    reference: Path,
    ref_ctime: float,
    ref_lines: int,
    ref_leaves: int,
    results: list[dict],
    threshold: float,
    timestamp: str,
) -> str:
    passed = sum(1 for r in results if r["score"] >= threshold)
    total = len(results)
    robustness = (passed / total * 100) if total else 0.0
    ref_date = datetime.fromtimestamp(ref_ctime).strftime("%Y-%m-%d %H:%M")

    lines = [
        "# YAML Similarity KPI Report",
        "",
        f"- **Script**: `yaml_similarity_kpi.py`",
        f"- **Executed**: {timestamp}",
        f"- **Input directory**: `{INPUT_DIR}`",
        f"- **Reference file**: `{reference.name}`  *(oldest by creation date)*",
        f"  - Created: {ref_date} | Lines: {ref_lines} | Leaves: {ref_leaves}",
        f"- **Threshold**: {threshold}",
        "",
        "## Results",
        "",
        "| # | File | Created | Lines (\u0394) | Leaves (\u0394) | Score | Status |",
        "|---|------|---------|----------:|-----------:|------:|--------|",
    ]

    for i, r in enumerate(results, start=1):
        score_str = f"{r['score']:.4f}"
        if r["parse_error"]:
            status = "PARSE ERROR"
        elif r["score"] >= threshold:
            status = "PASS"
        else:
            status = "FAIL"
        cdate = datetime.fromtimestamp(r["ctime"]).strftime("%Y-%m-%d %H:%M")
        lines_str = _fmt_delta(r["line_count"], ref_lines)
        leaves_str = _fmt_delta(r["leaf_count"], ref_leaves) if not r["parse_error"] else "\u2014"
        lines.append(
            f"| {i} | `{r['name']}` | {cdate} | {lines_str} | {leaves_str} | {score_str} | {status} |"
        )

    lines += [
        "",
        "## Summary",
        "",
        f"**Robustness score: {passed}/{total} candidates above threshold "
        f"({robustness:.1f}%)**",
        "",
    ]

    key_diffs = [r for r in results if r["missing_keys"] or r["added_keys"]]
    if key_diffs:
        lines += ["## Key diffs", ""]
        for r in key_diffs:
            lines.append(f"### `{r['name']}`")
            if r["missing_keys"]:
                missing_str = ", ".join(f"`{k}`" for k in sorted(r["missing_keys"]))
                lines.append(f"- Missing (present in reference): {missing_str}")
            if r["added_keys"]:
                added_str = ", ".join(f"`{k}`" for k in sorted(r["added_keys"]))
                lines.append(f"- Added (not in reference): {added_str}")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="YAML file similarity KPI")
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Similarity threshold (default: {DEFAULT_THRESHOLD})",
    )
    args = parser.parse_args()

    file_entries = collect_files(INPUT_DIR)
    ref_path, ref_ctime = file_entries[0]
    candidates = file_entries[1:]

    ref_data, ref_lines = load_yaml(ref_path)
    ref_leaves = count_leaves(ref_data) if ref_data is not None else 0
    ref_keys = set(ref_data.keys()) if isinstance(ref_data, dict) else set()

    results = []
    for cand_path, cand_ctime in candidates:
        cand_data, cand_lines = load_yaml(cand_path)
        score = similarity(ref_data, cand_data)
        cand_leaves = count_leaves(cand_data) if cand_data is not None else 0
        cand_keys = set(cand_data.keys()) if isinstance(cand_data, dict) else set()
        results.append(
            {
                "name": cand_path.name,
                "ctime": cand_ctime,
                "line_count": cand_lines,
                "leaf_count": cand_leaves,
                "score": score,
                "parse_error": cand_data is None,
                "missing_keys": ref_keys - cand_keys,
                "added_keys": cand_keys - ref_keys,
            }
        )

    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    report = render_markdown(
        ref_path, ref_ctime, ref_lines, ref_leaves,
        results, args.threshold, timestamp
    )

    output_path = INPUT_DIR / f"Yaml_SimilarityKPI_{timestamp}.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"Report written to: {output_path}")


if __name__ == "__main__":
    main()
