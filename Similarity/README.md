# Similarity KPI Tools

Measure the robustness of an LLM agent by comparing multiple generated files
against the first (reference) output, sorted by creation date.

---

## Prerequisites

Python 3.11+ must be available on your PATH.

---

## Installation

From the `Tools/Similarity/` directory, create and activate the virtual environment
then install dependencies :

```bash
# Create venv (one-time)
python -m venv .venv

# Activate — Windows CMD
.venv\Scripts\activate.bat

# Activate — Windows PowerShell
.venv\Scripts\Activate.ps1

# Activate — Git Bash / macOS / Linux
source .venv/Scripts/activate   # Windows Git Bash
source .venv/bin/activate        # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

---

## Where to put the files

| Tool | Input directory | File extension |
|---|---|---|
| `py_similarity_kpi.py` | `Tools/Similarity/Input_Python/` | `.py` |
| `yaml_similarity_kpi.py` | `Tools/Similarity/Input_Yaml/` | `.yml` or `.yaml` |

When done with a run, use `archive.py` to move files out of the input directories.

Drop all generated files for a single agent run into the relevant subdirectory.
The tool automatically picks the **oldest file by creation date** as the reference
and compares every other file against it.

Minimum 2 files required per run.

---

## Running the tools

Make sure the venv is activated, then from `Tools/Similarity/`:

```bash
# Python similarity KPI
python Scripts/py_similarity_kpi.py

# YAML similarity KPI
python Scripts/yaml_similarity_kpi.py

# Optional: override the similarity threshold (default 0.95)
python Scripts/py_similarity_kpi.py --threshold 0.90
python Scripts/yaml_similarity_kpi.py --threshold 0.90
```

---

## Archiving files

Use `archive.py` to move files from the input directories into `Archives/`.

```bash
# Move ALL files from both Input_Python/ and Input_Yaml/ to Archives/
python Scripts/archive.py

# Move only report .md files, keeping the most recent one in each input directory
python Scripts/archive.py --reports
```

---

## Output

Each run writes a Markdown report to `Tools/Similarity/`:

```
Py_SimilarityKPI_yyyymmddhhmm.md
Yaml_SimilarityKPI_yyyymmddhhmm.md
```

The report contains:
- Reference file name
- Per-file similarity score and PASS / FAIL status
- Final robustness score: percentage of candidates at or above the threshold

---

## Directory layout

```
Tools/Similarity/
  Scripts/                    ← scripts folder
    py_similarity_kpi.py      ← Python similarity tool
    yaml_similarity_kpi.py    ← YAML similarity tool
    archive.py                ← archiving tool
  requirements.txt            ← pyyaml dependency
  .venv/                      ← virtual environment (not committed)
  Input_Python/               ← drop .py files here
  Input_Yaml/                 ← drop .yml / .yaml files here
  Py_SimilarityKPI_*.md       ← generated reports
  Yaml_SimilarityKPI_*.md     ← generated reports
  Archives/
    Input_Python/             ← archived .py files and reports
    Input_Yaml/               ← archived .yml/.yaml files and reports
```
