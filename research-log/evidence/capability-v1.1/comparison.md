# Benchmark v1 versus v1.1: contract-only prompt intervention

No training. Same 40 tasks, scorer, seed schedule, model ID, decoding and package versions. Original checkpoint revision was unrecorded; current cached revision and four exact original-prompt model reproduction cases are recorded.

| Split / capability | v1 successes | v1.1 successes | Change (pp) | IGF v1 → v1.1 | unknown_tool v1 → v1.1 | JSON/format v1 → v1.1 |
|---|---:|---:|---:|---:|---:|---:|
| train/extraction | 4/112 (3.57%) | 16/112 (14.29%) | +10.71 | 28.57% → 100.00% | 1 → 0 | 43 → 13 |
| train/comparison | 2/112 (1.79%) | 2/112 (1.79%) | +0.00 | 28.57% → 14.29% | 0 → 0 | 84 → 83 |
| train/selection | 4/112 (3.57%) | 37/112 (33.04%) | +29.46 | 42.86% → 100.00% | 40 → 0 | 43 → 48 |
| train/multistep | 0/112 (0.00%) | 0/112 (0.00%) | +0.00 | 0.00% → 0.00% | 1 → 0 | 87 → 109 |
| train/overall | 10/448 (2.23%) | 55/448 (12.28%) | +10.04 | 25.00% → 53.57% | 42 → 0 | 257 → 253 |
| test/extraction | 3/48 (6.25%) | 4/48 (8.33%) | +2.08 | 33.33% → 33.33% | 0 → 0 | 42 → 28 |
| test/comparison | 1/48 (2.08%) | 0/48 (0.00%) | -2.08 | 33.33% → 0.00% | 0 → 0 | 41 → 39 |
| test/selection | 2/48 (4.17%) | 13/48 (27.08%) | +22.92 | 33.33% → 100.00% | 13 → 0 | 24 → 21 |
| test/multistep | 0/48 (0.00%) | 0/48 (0.00%) | +0.00 | 0.00% → 0.00% | 1 → 0 | 37 → 44 |
| test/overall | 6/192 (3.12%) | 17/192 (8.85%) | +5.73 | 25.00% → 33.33% | 14 → 0 | 144 → 132 |

## Action/progression diagnostics

Tool-name correctness is diagnostic: a parsed first action names a required tool, independent of arguments. Full next-action correctness and binary success remain unchanged scorer metrics. Selection ends after its correct lookup; multi-step requires three lookups plus final answer.
| Split / capability | First correct tool name v1 → v1.1 | First successful lookup v1 → v1.1 | All successful lookups v1 → v1.1 | Later model turns v1 → v1.1 |
|---|---:|---:|---:|---:|
| train/extraction | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| train/comparison | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| train/selection | 15 → 56 | 4 → 37 | 4 → 37 | 0 → 0 |
| train/multistep | 4 → 43 | 0 → 0 | 0 → 0 | 0 → 0 |
| train/overall | 19 → 99 | 4 → 37 | 4 → 37 | 0 → 0 |
| test/extraction | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| test/comparison | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| test/selection | 7 → 26 | 2 → 13 | 2 → 13 | 0 → 0 |
| test/multistep | 1 → 14 | 0 → 0 | 0 → 0 | 0 → 0 |
| test/overall | 8 → 40 | 2 → 13 | 2 → 13 | 0 → 0 |

Paired fixes: 64; paired regressions: 8.
All v1.1 histories were replayed with the unchanged scorer. Every prior tool-call/observation pair in every later v1.1 input was checked for exact inclusion. This verifies passing context, not that the model uses it correctly.

## Limits on attribution
Only unusable advertised material was removed. This also shortens/reorders the model input token sequence, so changed outputs do not prove each prior failure was caused by a tool mismatch. Correct required-tool names with wrong scopes still fail. Unknown tools can still be hallucinated. No output repair, numeric-output rule, extra demonstration, retry policy, dataset shortcut fix or budget change was introduced.
The v1 metric-to-winner shortcut and unusual 2142/2143 dates remain. Held-out metrics are descriptive, not used for tuning. This is not a v2 benchmark or evidence of trained improvements. Detailed status transitions, all per-seed changes and per-instance IGF are separate JSON/CSV files.

## Paired trace findings

Of the 56 original unknown_tool failures, 16 now succeed, 28 fail action format, 11 fail the required scope, and one fails argument validation. This supports improved tool-protocol alignment but not the claim that all 56 became successes. Across all pairs, 64 failures become successes and eight successes regress.

Multi-step: no first successful lookup in either arm; no model turn after a tool observation. Observation handling is therefore not empirically assessed in this run (zero opportunities), rather than demonstrated correct by a vacuous history check.

Typical v1.1 selection format error: `{"tool-action":"get_ad_spend","arguments":{...}}` instead of `tool`. Typical multi-step format error: one object containing `tool`, `arguments`, and `final_answer`. Wrong date scopes and numeric strings remain. Full paired examples are in representatives.json.
