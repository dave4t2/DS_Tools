# YAML Similarity KPI Report

- **Script**: `yaml_similarity_kpi.py`
- **Executed**: 202605242321
- **Input directory**: `g:\My Drive\0 - Dev\0 - Workspaces\_DS_Tools\Similarity\Input_Yaml`
- **Reference file**: `steps_1.yaml`  *(oldest by creation date)*
  - Created: 2026-05-24 20:03 | Lines: 125 | Leaves: 72
- **Threshold**: 0.95

## Results

| # | File | Created | Lines (Δ) | Leaves (Δ) | Edit blocks | Score | Status |
|---|------|---------|----------:|-----------:|:-----------:|------:|--------|
| 1 | `steps_2.yaml` | 2026-05-24 20:03 | 127 (+2: 0 content, +2 comment) | 72 | — | 1.0000 | PASS |
| 2 | `steps_3.yaml` | 2026-05-24 22:57 | 136 (+11: 0 content, +11 comment) | 72 | — | 1.0000 | PASS |
| 3 | `steps_4.yaml` | 2026-05-24 23:00 | 149 (+24: +13 content, +11 comment) | 80 (+8) | 5 | 0.8375 | FAIL |
| 4 | `steps_5.yaml` | 2026-05-24 23:04 | 149 (+24: +13 content, +11 comment) | 80 (+8) | 5 | 0.8375 | FAIL |
| 5 | `steps_6.yaml` | 2026-05-24 23:07 | 144 (+19: +6 content, +13 comment) | 74 (+2) | 3 | 0.9054 | FAIL |
| 6 | `steps_7.yaml` | 2026-05-24 23:10 | 144 (+19: +6 content, +13 comment) | 74 (+2) | 3 | 0.9054 | FAIL |
| 7 | `steps_8.yaml` | 2026-05-24 23:13 | 144 (+19: +6 content, +13 comment) | 74 (+2) | 3 | 0.9054 | FAIL |
| 8 | `steps_9.yaml` | 2026-05-24 23:16 | 144 (+19: +6 content, +13 comment) | 74 (+2) | 3 | 0.9054 | FAIL |
| 9 | `steps_10.yaml` | 2026-05-24 23:18 | 144 (+19: +6 content, +13 comment) | 74 (+2) | 3 | 0.9054 | FAIL |

## Summary

**Robustness score: 2/9 candidates above threshold (22.2%)**

## Structural diffs

### `steps_4.yaml`
- `-` `payload_ref` → `FISTesting/payloads/pain001_base.json`
- `+` `steps[0].params.overrides` → `{cashfitMetadata.routingPattern: single_cover, creditTransferTransaction.amount: '1000.00',
  creditTransferTransaction.currency: EUR}`
- `-` `steps[6].verifies[1]` → `shared.R6`
- `~` `steps[8].action`: `search_payment_ui` → `search_payment_api`
- `~` `steps[8].assert.keyword`: `assert_ui_payment_status_in` → `assert_payment_status_in`
- `~` `steps[8].verifies[0]`: `shared.R7` → `shared.R6`
- `+` `steps[9]` → `{action: search_payment_ui, assert: {keyword: assert_ui_payment_status_in, params: {
      allowed: [SETTLED]}}, verifies: [shared.R7]}`
- `+` `test_data.amount` → `1000.00`
- `+` `test_data.currency` → `EUR`
- `+` `test_data.routing_pattern` → `single_cover`

### `steps_5.yaml`
- `-` `payload_ref` → `FISTesting/payloads/pain001_base.json`
- `+` `steps[0].params.overrides` → `{cashfitMetadata.routingPattern: single_cover, creditTransferTransaction.amount: '1000.00',
  creditTransferTransaction.currency: EUR}`
- `-` `steps[6].verifies[1]` → `shared.R6`
- `~` `steps[8].action`: `search_payment_ui` → `search_payment_api`
- `~` `steps[8].assert.keyword`: `assert_ui_payment_status_in` → `assert_payment_status_in`
- `~` `steps[8].verifies[0]`: `shared.R7` → `shared.R6`
- `+` `steps[9]` → `{action: search_payment_ui, assert: {keyword: assert_ui_payment_status_in, params: {
      allowed: [SETTLED]}}, verifies: [shared.R7]}`
- `+` `test_data.amount` → `1000.00`
- `+` `test_data.currency` → `EUR`
- `+` `test_data.routing_pattern` → `single_cover`

### `steps_6.yaml`
- `-` `payload_ref` → `FISTesting/payloads/pain001_base.json`
- `-` `steps[6].verifies[1]` → `shared.R6`
- `~` `steps[8].action`: `search_payment_ui` → `search_payment_api`
- `~` `steps[8].assert.keyword`: `assert_ui_payment_status_in` → `assert_payment_status_in`
- `~` `steps[8].verifies[0]`: `shared.R7` → `shared.R6`
- `+` `steps[9]` → `{action: search_payment_ui, assert: {keyword: assert_ui_payment_status_in, params: {
      allowed: [SETTLED]}}, verifies: [shared.R7]}`

### `steps_7.yaml`
- `-` `payload_ref` → `FISTesting/payloads/pain001_base.json`
- `-` `steps[6].verifies[1]` → `shared.R6`
- `~` `steps[8].action`: `search_payment_ui` → `search_payment_api`
- `~` `steps[8].assert.keyword`: `assert_ui_payment_status_in` → `assert_payment_status_in`
- `~` `steps[8].verifies[0]`: `shared.R7` → `shared.R6`
- `+` `steps[9]` → `{action: search_payment_ui, assert: {keyword: assert_ui_payment_status_in, params: {
      allowed: [SETTLED]}}, verifies: [shared.R7]}`

### `steps_8.yaml`
- `-` `payload_ref` → `FISTesting/payloads/pain001_base.json`
- `-` `steps[6].verifies[1]` → `shared.R6`
- `~` `steps[8].action`: `search_payment_ui` → `search_payment_api`
- `~` `steps[8].assert.keyword`: `assert_ui_payment_status_in` → `assert_payment_status_in`
- `~` `steps[8].verifies[0]`: `shared.R7` → `shared.R6`
- `+` `steps[9]` → `{action: search_payment_ui, assert: {keyword: assert_ui_payment_status_in, params: {
      allowed: [SETTLED]}}, verifies: [shared.R7]}`

### `steps_9.yaml`
- `-` `payload_ref` → `FISTesting/payloads/pain001_base.json`
- `-` `steps[6].verifies[1]` → `shared.R6`
- `~` `steps[8].action`: `search_payment_ui` → `search_payment_api`
- `~` `steps[8].assert.keyword`: `assert_ui_payment_status_in` → `assert_payment_status_in`
- `~` `steps[8].verifies[0]`: `shared.R7` → `shared.R6`
- `+` `steps[9]` → `{action: search_payment_ui, assert: {keyword: assert_ui_payment_status_in, params: {
      allowed: [SETTLED]}}, verifies: [shared.R7]}`

### `steps_10.yaml`
- `-` `payload_ref` → `FISTesting/payloads/pain001_base.json`
- `-` `steps[6].verifies[1]` → `shared.R6`
- `~` `steps[8].action`: `search_payment_ui` → `search_payment_api`
- `~` `steps[8].assert.keyword`: `assert_ui_payment_status_in` → `assert_payment_status_in`
- `~` `steps[8].verifies[0]`: `shared.R7` → `shared.R6`
- `+` `steps[9]` → `{action: search_payment_ui, assert: {keyword: assert_ui_payment_status_in, params: {
      allowed: [SETTLED]}}, verifies: [shared.R7]}`
