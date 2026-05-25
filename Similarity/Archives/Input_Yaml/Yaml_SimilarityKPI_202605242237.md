# YAML Similarity KPI Report

- **Script**: `yaml_similarity_kpi.py`
- **Executed**: 202605242237
- **Input directory**: `g:\My Drive\0 - Dev\0 - Workspaces\_DS_Tools\Similarity\Input_Yaml`
- **Reference file**: `steps_1.yaml`  *(oldest by creation date)*
  - Created: 2026-05-24 20:03 | Lines: 94 | Leaves: 63
- **Threshold**: 0.95

## Results

| # | File | Created | Lines (Δ) | Leaves (Δ) | Edit blocks | Score | Status |
|---|------|---------|----------:|-----------:|:-----------:|------:|--------|
| 1 | `steps_2.yaml` | 2026-05-24 20:03 | 125 (+31: +5 content, +26 comment) | 72 (+9) | 2 | 0.8750 | FAIL |

## Summary

**Robustness score: 0/1 candidates above threshold (0.0%)**

## Structural diffs

### `steps_2.yaml`
- `+` `test_data` → `{post_submit_statuses: [PACS008_EMITTED, POSTED, ACKNOWLEDGED, SETTLED, REPAIR], pre_submit_statuses: [
    RECEIVED, VALIDATED, ENRICHED, PENDING_SUBMISSION]}`
