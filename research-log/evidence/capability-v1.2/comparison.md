# Benchmark v1.2: output-protocol intervention

| Capability | v1.1 Train | v1.2 Train | v1.1 Test | v1.2 Test | Train change (pp) | Test change (pp) |
|---|---:|---:|---:|---:|---:|---:|
| extraction | 16/112 (14.29%) | 0/112 (0.00%) | 4/48 (8.33%) | 0/48 (0.00%) | -14.29 | -8.33 |
| comparison | 2/112 (1.79%) | 0/112 (0.00%) | 0/48 (0.00%) | 0/48 (0.00%) | -1.79 | +0.00 |
| selection | 37/112 (33.04%) | 65/112 (58.04%) | 13/48 (27.08%) | 23/48 (47.92%) | +25.00 | +20.83 |
| multistep | 0/112 (0.00%) | 0/112 (0.00%) | 0/48 (0.00%) | 0/48 (0.00%) | +0.00 | +0.00 |
| overall | 55/448 (12.28%) | 65/448 (14.51%) | 17/192 (8.85%) | 23/192 (11.98%) | +2.23 | +3.12 |

## Detailed diagnostics

| Split/category | JSON/schema failures v1.1 → v1.2 | Unknown tools | Invalid arguments | IGF | First correct action | Lookups executed | Later turns |
|---|---:|---:|---:|---:|---:|---:|---:|
| train/extraction | 13 → 16 | 0 → 0 | 0 → 0 | 100.00% → 0.00% | 14.29% → 0.00% | 0 → 0 | 0 → 0 |
| train/comparison | 83 → 67 | 0 → 0 | 0 → 2 | 14.29% → 0.00% | 1.79% → 0.00% | 0 → 0 | 0 → 0 |
| train/selection | 48 → 2 | 0 → 0 | 1 → 1 | 100.00% → 100.00% | 33.04% → 58.04% | 37 → 65 | 0 → 0 |
| train/multistep | 109 → 106 | 0 → 0 | 0 → 0 | 0.00% → 0.00% | 0.00% → 0.00% | 0 → 0 | 0 → 0 |
| train/overall | 253 → 191 | 0 → 0 | 1 → 3 | 53.57% → 25.00% | 12.28% → 14.51% | 37 → 65 | 0 → 0 |
| test/extraction | 28 → 14 | 0 → 0 | 0 → 0 | 33.33% → 0.00% | 8.33% → 0.00% | 0 → 0 | 0 → 0 |
| test/comparison | 39 → 33 | 0 → 0 | 0 → 1 | 0.00% → 0.00% | 0.00% → 0.00% | 0 → 0 | 0 → 0 |
| test/selection | 21 → 1 | 0 → 0 | 1 → 0 | 100.00% → 66.67% | 27.08% → 47.92% | 13 → 23 | 0 → 0 |
| test/multistep | 44 → 44 | 0 → 0 | 0 → 0 | 0.00% → 0.00% | 0.00% → 0.00% | 0 → 0 | 0 → 0 |
| test/overall | 132 → 92 | 0 → 0 | 1 → 1 | 33.33% → 16.67% | 8.85% → 11.98% | 13 → 23 | 0 → 0 |

Paired fixes: 47; regressions: 31.
The typed-final-value diagnostic counts explicit correct values even in invalid envelopes; it is not a repaired reward or evidence of genuine reasoning. In particular, the metric/winner shortcut remains. Strict JSON, protocol-valid actions, exact task correctness and terminal completion are separate quantities in comparison.json.
No test-set tuning, numerical hints, new examples, weight updates, parser repair or reward changes. The synthetic v1.1 example suffix and tool schemas are byte-identical. Pilot used first training instance/category and first four existing seeds; all 16 live v1.1 controls matched recorded trajectories. Pilot v1.2 trajectories also reproduced exactly when sampled again in the full run. No prompt revisions occurred.
Checkpoint was pinned to the single cache revision recorded by v1.1; package versions were checked before running. Original v1 checkpoint provenance remains historically incomplete.

## Interpretation of this run

Overall success rises 72/640 (11.25%) to 88/640 (13.75%), +2.50 pp, but all 88 successes are selection tasks. Extraction falls 20/160 to zero; comparison 2/160 to zero; multi-step stays zero. Selection rises 50/160 (31.25%) to 88/160 (55.00%). Thus this is not a universal prompt improvement.

Strict JSON first responses increase 387/640 to 546/640. The separate action-protocol validator passes 145/640 to 319/640. Verifier JSON/schema failures fall 385 to 283 (invalid_json 253→94; invalid_format 132→189). Unnecessary calls increase 61→231, wrong_final_answer declines 119→34, invalid arguments increase 2→4, and unknown tools remain zero. No output was repaired.

Selection: correct required tool names increase 82/160 to 144/160; correct full calls/executions increase 50 to 88. Its protocol-valid first actions rise 89/160 to 156/160. This combines representation and tool/scope-selection changes, not evidence of improved numerical reasoning.

Multi-step still has zero successful first lookups and zero later turns. Observation retention passes scripted tests, but no model observation-to-next-action opportunity exists in this full run. All 640 trajectories end after one model action. Parsed calls often mix tool/arguments with final_answer or result, batch calls, or substitute 2024 dates.

Paired improvements: 35 former invalid_format cases, one invalid_json case and 11 unnecessary_call cases now succeed. All 47 fixes are in selection. Nine formerly successful selection samples regress; all 22 former extraction/comparison successes regress, for 31 total. This cannot identify what fraction of historical failures was caused by unclear wording. The intervention changes instruction length, emphasis and token sequence together.

Explicit correct typed final-value claims (including invalid envelopes) decline 41→27. Such claims are diagnostic only; they do not override original scoring and are not evidence of ranking skill while the metric/winner shortcut persists.

Only selection has mixed training rewards: 7/7 instances; test 2/3. Extraction, comparison and multi-step each have zero mixed groups. Overall training IGF drops 15/28→7/28 despite higher aggregate success.

Recommended next experiment: preserve this negative/mixed result, then test a shorter, capability-specific protocol on training/validation only, without changing scoring. Do not infer that more verbose instructions are necessarily clearer to a 0.5B model. A separate benchmark version must remove the metric/winner shortcut before broad reasoning-GRPO claims. No training, schema decoding constraints or benchmark redesign was performed here.

## Answers to the interpretation questions

1. No causal percentage of v1.1 failures can be assigned to unclear instructions from this experiment. There are 47 fixes and 31 regressions under a multi-part prompt intervention; only the net change is identified for this frozen setting.
2. JSON parsing and selection/action compliance improve. Extraction/comparison terminal performance regresses to zero. There is no demonstrated improvement in numerical reasoning.
3. No multi-step first lookup executes successfully (0/160), despite some correct tool-name claims.
4. Actual observation handling is unmeasured here because there are no later model turns. The scripted continuation test passes.
5. Selection has 7/7 mixed training groups; all other categories have 0/7. This supports only a narrow action-selection reward signal, not broad multi-capability readiness.
6. Remaining defects include perfect metric/winner correlation, unusual future dates, only 12 held-out instances, shared templates, and mixed next-action versus full-episode denominators. The unchanged generic 2024 example may invite scope copying; that mechanism remains a hypothesis. These were not fixed in this experiment.
