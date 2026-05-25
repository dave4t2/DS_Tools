"""
batch_generate.py — orchestrate Copilot CLI passes for one or many TEST-IDs.

Usage
-----
# Run steps pass (generate steps.yaml):
python Scripts/batch_generate.py --run steps

# Run py pass (generate pytest, requires existing steps.yaml):
python Scripts/batch_generate.py --run py

# Specific test cases only:
python Scripts/batch_generate.py PAM-SMOKE-001 --run steps

# Dry-run (print prompts without calling Copilot CLI):
python Scripts/batch_generate.py --dry-run

Authentication
--------------
Set COPILOT_GITHUB_TOKEN (or GH_TOKEN / GITHUB_TOKEN) before running.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths — all relative to REPO_ROOT
# ---------------------------------------------------------------------------
REPO_ROOT = Path(r"g:\My Drive\0 - Dev\0 - Workspaces\_SG\FISTF")
PROMPTS_DIR = REPO_ROOT / ".github" / "prompts"
EXAMPLES_DIR = REPO_ROOT / "FISTesting" / "dsl" / "examples"
BATCH_OUTPUT_DIR = REPO_ROOT / "FISTesting" / "Batch_Output"
GENERATED_DIR = REPO_ROOT / "FISTesting" / "tests" / "generated"

PROMPT_GENERATE_STEPS = PROMPTS_DIR / "generate-steps.prompt.md"
PROMPT_GENERATE_PYTEST = PROMPTS_DIR / "generate-pytest.prompt.md"

# Copilot CLI flags used for every non-interactive call
COPILOT_FLAGS = [
    "--allow-all",       # no permission prompts
    "--no-ask-user",     # agent never pauses for user input
    "--autopilot",       # multi-step continuation without approval
    "-s",                # silent: output only agent response
]

INPUT_PATTERN = re.compile(r"\$\{input:[^}]+\}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def strip_frontmatter(text: str) -> str:
    """Remove the YAML frontmatter block (--- ... ---) from a prompt file."""
    if text.startswith("---"):
        end = text.index("---", 3)
        return text[end + 3:].lstrip("\n")
    return text


def load_prompt(path: Path, test_id: str) -> str:
    """Load a .prompt.md file, strip frontmatter, substitute testId."""
    raw = path.read_text(encoding="utf-8")
    body = strip_frontmatter(raw)
    # Replace every ${input:testId:...} pattern with the actual test_id
    return INPUT_PATTERN.sub(test_id, body)


def discover_test_ids() -> list[str]:
    """Return sorted list of TEST-IDs found under FISTesting/dsl/examples/."""
    return sorted(
        d.name
        for d in EXAMPLES_DIR.iterdir()
        if d.is_dir() and (d / "requirements.md").exists()
    )


def output_path_for(run_type: str, test_id: str) -> Path:
    """Return the standard output file path for a given run type and test ID."""
    if run_type == "steps":
        return EXAMPLES_DIR / test_id / "steps.yaml"
    return GENERATED_DIR / f"{test_id}.py"


def copy_to_batch_output(test_id: str, run_type: str, run_number: int, dry_run: bool) -> None:
    """Copy the generated output file to Batch_Output/<TEST-ID>/, renamed with _<n> suffix."""
    src = output_path_for(run_type, test_id)
    if not src.exists():
        print(f"  [WARN] Output file not found after run {run_number}: {src.relative_to(REPO_ROOT)}")
        return
    dest_dir = BATCH_OUTPUT_DIR / test_id
    dest = dest_dir / f"{src.stem}_{run_number}{src.suffix}"
    if dry_run:
        print(f"  DRY-RUN copy → {dest.relative_to(REPO_ROOT)}")
        return
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    print(f"  Copied → {dest.relative_to(REPO_ROOT)}", flush=True)


def run_copilot(prompt: str, test_id: str, pass_label: str, dry_run: bool) -> bool:
    """
    Call `copilot -p <prompt> --allow-all ...` from REPO_ROOT.
    Returns True on success, False on failure.
    """
    if dry_run:
        print(f"\n{'='*70}")
        print(f"DRY-RUN  {pass_label}  [{test_id}]")
        print(f"{'='*70}")
        print(prompt[:500] + ("..." if len(prompt) > 500 else ""))
        return True

    print(f"\n>>> {pass_label}  [{test_id}]", flush=True)

    result = subprocess.run(
        ["copilot", "-p", prompt, *COPILOT_FLAGS],
        cwd=REPO_ROOT,
        # Do NOT set shell=True — keeps the prompt string out of the OS
        # command line (no length limit, no quoting issues on Windows)
    )

    success = result.returncode == 0
    status = "OK" if success else f"FAILED (exit {result.returncode})"
    print(f"    {pass_label} [{test_id}] → {status}", flush=True)
    return success


# ---------------------------------------------------------------------------
# Per-test-ID logic
# ---------------------------------------------------------------------------

def run_pass1(test_id: str, dry_run: bool) -> bool:
    requirements_file = EXAMPLES_DIR / test_id / "requirements.md"
    if not requirements_file.exists():
        print(f"  [SKIP] {test_id}: no requirements.md found")
        return False

    prompt = load_prompt(PROMPT_GENERATE_STEPS, test_id)
    return run_copilot(prompt, test_id, "Steps (generate-steps)", dry_run)


def run_pass2(test_id: str, dry_run: bool) -> bool:
    steps_file = EXAMPLES_DIR / test_id / "steps.yaml"
    if not steps_file.exists():
        print(f"  [SKIP] {test_id}: no steps.yaml (run pass 1 first)")
        return False

    prompt = load_prompt(PROMPT_GENERATE_PYTEST, test_id)
    return run_copilot(prompt, test_id, "Py (generate-pytest)", dry_run)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Batch-run Copilot CLI generation passes.")
    parser.add_argument(
        "test_ids",
        nargs="*",
        metavar="TEST-ID",
        help="Test case IDs to process. Defaults to all discovered IDs.",
    )
    parser.add_argument("--run", choices=["steps", "py"], required=True, help="Pass to run: steps or py.")
    parser.add_argument("--runs", type=int, default=2, metavar="N", help="Number of generation runs per test case (default: 2, min: 2).")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts without calling Copilot CLI.")
    args = parser.parse_args()

    if args.runs < 2:
        parser.error("--runs must be >= 2")

    # Resolve test IDs
    test_ids = args.test_ids or discover_test_ids()[:1]
    if not test_ids:
        print("No test IDs found under FISTesting/dsl/examples/. Nothing to do.")
        return 0

    run_p1 = args.run == "steps"
    run_p2 = args.run == "py"

    run_fn = run_pass1 if run_p1 else run_pass2
    run_key = "steps" if run_p1 else "py"

    print(f"Test IDs : {', '.join(test_ids)}")
    print(f"Pass     : {args.run}")
    print(f"Runs     : {args.runs}")
    print(f"Dry-run  : {args.dry_run}")
    print(f"Repo root: {REPO_ROOT}")

    results: dict[str, dict[str, bool | None]] = {}

    for tid in test_ids:
        results[tid] = {"steps": None, "py": None}

        for n in range(1, args.runs + 1):
            print(f"\n  [{tid}] Run {n}/{args.runs}", flush=True)
            ok = run_fn(tid, args.dry_run)
            if results[tid][run_key] is not False:
                results[tid][run_key] = ok
            if ok:
                copy_to_batch_output(tid, args.run, n, args.dry_run)
            else:
                print(f"  [WARN] Run {n} failed — skipping copy for {tid}")

    # Summary
    print(f"\n{'='*70}")
    print("Summary")
    print(f"{'='*70}")
    any_failure = False
    for tid, r in results.items():
        p1 = "✓" if r["steps"] is True else ("✗" if r["steps"] is False else "-")
        p2 = "✓" if r["py"] is True else ("✗" if r["py"] is False else "-")
        print(f"  {tid:<35} steps={p1}  py={p2}")
        if r["steps"] is False or r["py"] is False:
            any_failure = True

    return 1 if any_failure else 0


if __name__ == "__main__":
    sys.exit(main())
