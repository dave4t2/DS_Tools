# YAML Similarity KPI Report

- **Script**: `yaml_similarity_kpi.py`
- **Executed**: 202605231958
- **Input directory**: `G:\My Drive\0 - Dev\0 - Workspaces\SG_FISTF\FISTF\Tools\Similarity\Yaml`
- **Reference file**: `steps v1.yaml`  *(oldest by creation date)*
  - Created: 2026-05-23 16:54 | Lines: 103 | Leaves: 67
- **Threshold**: 0.9

## Results

| # | File | Created | Lines (Δ) | Leaves (Δ) | Score | Status |
|---|------|---------|----------:|-----------:|------:|--------|
| 1 | `steps v2.yaml` | 2026-05-23 16:54 | 104 (+1) | 67 | 1.0000 | PASS |
| 2 | `steps v2 copy.yaml` | 2026-05-23 19:38 | 104 (+1) | 66 (-1) | 0.9104 | PASS |

## Summary

**Robustness score: 2/2 candidates above threshold (100.0%)**

## Diff details

### `steps v2 copy.yaml`

| Path | Reference value | Candidate value |
|------|-----------------|-----------------|
| `steps[0].params.overrides.controlSum` | `5000.00` | `6000.00` |
| `steps[0].params.overrides.creditTransferTransaction.amount` | `5000.00` | `6000.00` |
| `steps[1].params.allowed[0]` | `PENDING_SUBMISSION` | `PENDING_` |
| `steps[3].assert.params.allowed[1]` | `VALIDATED` | `ENRICHED` |
| `steps[3].assert.params.allowed[2]` | `ENRICHED` | `PENDING_SUBMISSION` |
| `steps[3].assert.params.allowed[3]` | `PENDING_SUBMISSION` | `—` |
