"""
archive.py
Move files from Input_Python/ and Input_Yaml/ into their
respective Archives/ subdirectories.

Usage:
    python Scripts/archive.py                # move ALL files
    python Scripts/archive.py --reports      # move only report .md files,
                                             # keeping the most recent one
"""

import argparse
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

MOVES = [
    (BASE_DIR / "Input_Python", BASE_DIR / "Archives" / "Input_Python", "Py_SimilarityKPI_*.md"),
    (BASE_DIR / "Input_Yaml",   BASE_DIR / "Archives" / "Input_Yaml",   "Yaml_SimilarityKPI_*.md"),
]


def archive_dir(src: Path, dst: Path, files: list[Path]) -> None:
    if not files:
        print(f"[SKIP] No files to archive in {src.relative_to(BASE_DIR)}")
        return
    dst.mkdir(parents=True, exist_ok=True)
    for f in files:
        target = dst / f.name
        if target.exists():
            print(f"[WARN] Already exists, skipping: {target.relative_to(BASE_DIR)}", file=sys.stderr)
            continue
        shutil.move(str(f), target)
        print(f"[MOVE] {f.relative_to(BASE_DIR)}  →  {target.relative_to(BASE_DIR)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive input files")
    parser.add_argument(
        "--reports",
        action="store_true",
        help="Only archive report .md files, keeping the most recent one",
    )
    args = parser.parse_args()

    for src, dst, report_glob in MOVES:
        if args.reports:
            candidates = sorted(src.glob(report_glob))  # sorted by name = sorted by timestamp
            files = candidates[:-1]                      # exclude the most recent (last)
        else:
            files = [f for f in src.iterdir() if f.is_file()]
        archive_dir(src, dst, files)


if __name__ == "__main__":
    main()
