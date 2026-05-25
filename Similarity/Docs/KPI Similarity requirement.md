# KPI Similarity — Requirements

## Goal

Measure the robustness of an LLM agent that generates files from a fixed input,
by comparing multiple outputs of the same agent run against the first (reference) output.

## Tools

Two standalone Python scripts, one per file type:

| Script | Input directory | Output file |
|---|---|---|
| `py_similarity_kpi.py` | `Tools/Similarity/Input_Python/` | `Py_SimilarityKPI_yyyymmddhhmm.md` |
| `yaml_similarity_kpi.py` | `Tools/Similarity/Input_Yaml/` | `Yaml_SimilarityKPI_yyyymmddhhmm.md` |

`yyyymmddhhmm` is the timestamp of the script execution.
Output files are written in the same directory as the input files (`Input_Python/` / `Input_Yaml/`).

## File ordering

- Scan all files with the relevant extension (`.py` / `.yml`) inside the input directory.
- Sort files by **creation date** (ascending).
- The first file in that sorted list is the **reference file**.
- Every other file is compared against the reference only (not against each other).

## Python similarity (`py_similarity_kpi.py`)

- Parse each file into an AST using Python's built-in `ast` module.
- Compare the AST dump of each candidate against the AST dump of the reference.
- Strict equality check first (score = 1.0 if equal).
- If not strictly equal, measure partial similarity using `SequenceMatcher` from `difflib`
  on the AST dump strings.
- Ignore comments and formatting; focus on structure only.
- Produce a similarity score between 0 and 1 for each (reference, candidate) pair.

## YAML similarity (`yaml_similarity_kpi.py`)

- Parse each file using `pyyaml` into Python dictionaries.
- Compare each candidate dict against the reference dict.
- Strict equality check first (score = 1.0 if equal).
- If not strictly equal, walk both dicts recursively and count matching vs differing
  leaf values (keys and values).
- Ignore key ordering, whitespace, and comments.
- Produce a similarity score between 0 and 1 for each (reference, candidate) pair.
- Count **leaf nodes** in each file (parser strips comments; ordering ignored).
- Count **edit blocks** between non-comment content lines using `SequenceMatcher`.
- Track **comment lines** separately; line delta is broken down into content Δ + comment Δ.
- Produce a **Structural diffs** section showing added (`+`), removed (`-`), and changed (`~`)
  nodes at any depth, with their values.

## Output format (both scripts)

Markdown file written to `Tools/Similarity/`, named with the execution timestamp.

Content:
- Header: script name, execution timestamp, input directory, reference file name, reference metrics.
- Table with columns: `#`, `File`, `Created`, `Lines (Δ)`, `Leaves (Δ)` *(YAML only)*, `Edit blocks`, `Score`, `Status`.
  - `Lines (Δ)`: total line count with delta broken down as `(total: content, comment)` when non-zero.
  - `Leaves (Δ)`: recursive leaf-node count with delta *(YAML only)*.
  - `Edit blocks`: number of differing edit regions in non-comment content lines.
- Summary line: robustness score = percentage of candidates at or above the threshold.
- **Structural diffs** section *(YAML only)*: for each candidate with differences, lists every
  added (`+`), removed (`-`), or changed (`~`) node with its dot-notation path and value(s).
