"""
py_similarity_kpi.py
Compare all Python files in Tools/Similarity/Python/ against the first file
(sorted by creation date) and produce a Markdown KPI report.

Usage:
    python py_similarity_kpi.py [--threshold 0.95]
"""

import argparse
import ast
import os
import sys
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

INPUT_DIR = Path(__file__).parent / "Python"
DEFAULT_THRESHOLD = 0.95


# ---------------------------------------------------------------------------
# File collection
# ---------------------------------------------------------------------------

def collect_files(directory: Path) -> list[tuple[Path, float]]:
    files = list(directory.glob("*.py"))
    if not files:
        print(f"[ERROR] No .py files found in {directory}", file=sys.stderr)
        sys.exit(1)
    files.sort(key=lambda p: os.path.getctime(p))
    if len(files) < 2:
        print(f"[ERROR] At least 2 .py files required in {directory} (found 1).", file=sys.stderr)
        sys.exit(1)
    return [(p, os.path.getctime(p)) for p in files]


# ---------------------------------------------------------------------------
# Parsing & similarity
# ---------------------------------------------------------------------------

def ast_dump(path: Path) -> tuple[str | None, int, int]:
    """Return (dump_str, line_count, node_count). dump_str is None on error."""
    try:
        text = path.read_text(encoding="utf-8")
        line_count = len(text.splitlines())
        tree = ast.parse(text)
        node_count = sum(1 for _ in ast.walk(tree))
        return ast.dump(tree), line_count, node_count
    except SyntaxError as exc:
        print(f"[WARN] SyntaxError in {path.name}: {exc}", file=sys.stderr)
        try:
            line_count = len(path.read_text(encoding="utf-8").splitlines())
        except Exception:
            line_count = 0
        return None, line_count, 0
    except Exception as exc:
        print(f"[WARN] Could not parse {path.name}: {exc}", file=sys.stderr)
        return None, 0, 0


def top_level_symbols(path: Path) -> list[str]:
    """Return names of top-level FunctionDef, AsyncFunctionDef, ClassDef nodes."""
    try:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        return [
            node.name
            for node in ast.iter_child_nodes(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        ]
    except Exception:
        return []


def similarity(dump_a: str | None, dump_b: str | None) -> tuple[float, int]:
    """Return (score, edit_block_count). edit_block_count is 0 when score == 1.0."""
    if dump_a is None or dump_b is None:
        return 0.0, 0
    if dump_a == dump_b:
        return 1.0, 0
    sm = SequenceMatcher(None, dump_a, dump_b)
    edit_blocks = sum(1 for tag, *_ in sm.get_opcodes() if tag != "equal")
    return sm.ratio(), edit_blocks


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
    ref_nodes: int,
    ref_symbols: list[str],
    results: list[dict],
    threshold: float,
    timestamp: str,
) -> str:
    passed = sum(1 for r in results if r["score"] >= threshold)
    total = len(results)
    robustness = (passed / total * 100) if total else 0.0
    ref_date = datetime.fromtimestamp(ref_ctime).strftime("%Y-%m-%d %H:%M")

    lines = [
        "# Python Similarity KPI Report",
        "",
        f"- **Script**: `py_similarity_kpi.py`",
        f"- **Executed**: {timestamp}",
        f"- **Input directory**: `{INPUT_DIR}`",
        f"- **Reference file**: `{reference.name}`  *(oldest by creation date)*",
        f"  - Created: {ref_date} | Lines: {ref_lines} | AST nodes: {ref_nodes}",
        f"- **Threshold**: {threshold}",
        "",
        "## Results",
        "",
        "| # | File | Created | Lines (\u0394) | Nodes (\u0394) | Edit blocks | Score | Status |",
        "|---|------|---------|----------:|----------:|:-----------:|------:|--------|",
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
        nodes_str = _fmt_delta(r["node_count"], ref_nodes) if not r["parse_error"] else "\u2014"
        edit_str = str(r["edit_blocks"]) if r["edit_blocks"] > 0 else "\u2014"
        lines.append(
            f"| {i} | `{r['name']}` | {cdate} | {lines_str} | {nodes_str} | {edit_str} | {score_str} | {status} |"
        )

    lines += [
        "",
        "## Summary",
        "",
        f"**Robustness score: {passed}/{total} candidates above threshold "
        f"({robustness:.1f}%)**",
        "",
    ]

    symbol_diffs = [r for r in results if r["missing_symbols"] or r["added_symbols"]]
    if symbol_diffs:
        lines += ["## Symbol diffs", ""]
        for r in symbol_diffs:
            lines.append(f"### `{r['name']}`")
            if r["missing_symbols"]:
                missing_str = ", ".join(f"`{s}`" for s in sorted(r["missing_symbols"]))
                lines.append(f"- Missing (present in reference): {missing_str}")
            if r["added_symbols"]:
                added_str = ", ".join(f"`{s}`" for s in sorted(r["added_symbols"]))
                lines.append(f"- Added (not in reference): {added_str}")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Python file similarity KPI")
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

    ref_dump, ref_lines, ref_nodes = ast_dump(ref_path)
    ref_symbols = top_level_symbols(ref_path)

    results = []
    for cand_path, cand_ctime in candidates:
        cand_dump, cand_lines, cand_nodes = ast_dump(cand_path)
        score, edit_blocks = similarity(ref_dump, cand_dump)
        cand_symbols = top_level_symbols(cand_path)
        results.append(
            {
                "name": cand_path.name,
                "ctime": cand_ctime,
                "line_count": cand_lines,
                "node_count": cand_nodes,
                "edit_blocks": edit_blocks,
                "score": score,
                "parse_error": cand_dump is None,
                "missing_symbols": set(ref_symbols) - set(cand_symbols),
                "added_symbols": set(cand_symbols) - set(ref_symbols),
            }
        )

    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    report = render_markdown(
        ref_path, ref_ctime, ref_lines, ref_nodes, ref_symbols,
        results, args.threshold, timestamp
    )

    output_path = INPUT_DIR / f"Py_SimilarityKPI_{timestamp}.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"Report written to: {output_path}")


if __name__ == "__main__":
    main()
