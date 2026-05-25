# FISTF — Copilot CLI Batch Automation

## Chosen solution

Use **GitHub Copilot CLI** (`winget install GitHub.Copilot`, v1.0.51) as a
non-interactive agent called from a Python orchestrator script. The CLI
accepts a full prompt string via `-p PROMPT` and runs autonomously with
`--allow-all --no-ask-user --autopilot -s` (no permission prompts, no
mid-task pauses, silent output).

The Python script reads the two existing VS Code prompt files, strips their
YAML frontmatter, substitutes the TEST-ID variable, and calls the CLI via
`subprocess.run` (list form — no shell, no length limit).

## Repo & key paths

| Item | Path (relative to `FISTF/`) |
|---|---|
| Orchestrator script | `FISTesting/scripts/batch_generate.py` |
| Pass-1 prompt | `.github/prompts/generate-steps.prompt.md` |
| Pass-2 prompt | `.github/prompts/generate-pytest.prompt.md` |
| Pass-1 output | `FISTesting/dsl/examples/<TEST-ID>/steps.yaml` |
| Pass-2 output | `FISTesting/tests/generated/<TEST-ID>.py` |
| Test cases (input) | `FISTesting/dsl/examples/` — PAM-SMOKE-001, PAM-AMS2-NOK-001, PAM-VALIDATION-001, PAM-USD-MULTICOVER-001 |

## Auth

CLI authenticates via env var `COPILOT_GITHUB_TOKEN` — a GitHub fine-grained
PAT with **"Copilot Requests"** permission scope.

> **Blocker**: The org-managed account had Copilot CLI disabled by org policy.
> A **personal** GitHub account with an individual **Copilot Pro** subscription
> is required.

## What is done

- [x] Copilot CLI v1.0.51 installed (`winget install GitHub.Copilot`)
- [x] Both `.prompt.md` files read and understood (frontmatter strip + `${input:testId:...}` substitution)
- [x] `FISTesting/scripts/batch_generate.py` written and verified working
  - `strip_frontmatter()`, `load_prompt()`, `discover_test_ids()`, `run_copilot()`, `copy_to_batch_output()`
  - CLI args: positional TEST-IDs, `--run {steps,py}` (required), `--runs N` (default 2, min 2), `--dry-run`
  - Each run copies output to `FISTesting/Batch_Output/<TEST-ID>/`, renamed `<stem>_<n><ext>`
- [x] Personal GitHub PAT obtained and `COPILOT_GITHUB_TOKEN` set
- [x] Smoke test steps pass: `PAM-SMOKE-001/steps.yaml` generated (9 steps, all requirements covered)
- [x] Smoke test py pass: `PAM-SMOKE-001.py` generated (374 lines, 0 TODOs)

## What remains

**Full batch** (all TEST-IDs). Set token in terminal first — do not commit it to source:
```powershell
$env:COPILOT_GITHUB_TOKEN = "github_pat_..."   # personal Copilot Pro PAT
cd "G:\My Drive\0 - Dev\0 - Workspaces\_SG\FISTF"
python FISTesting/scripts/batch_generate.py --run steps --runs 2
python FISTesting/scripts/batch_generate.py --run py --runs 2
```
