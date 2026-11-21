# Benchmark v1.3: single decision-rule intervention

| Capability | v1.1 | v1.2 | v1.3 | v1.3 nominal exact binomial 95% CI | Δ vs v1.2 (pp) | Paired task-bootstrap 95% interval (pp) |
|---|---:|---:|---:|---:|---:|---:|
| extraction | 20/160 (12.50%) | 0/160 (0.00%) | 0/160 (0.00%) | [0.00%, 2.28%] | +0.00 | [+0.00, +0.00] |
| comparison | 2/160 (1.25%) | 0/160 (0.00%) | 1/160 (0.62%) | [0.02%, 3.43%] | +0.62 | [+0.00, +1.88] |
| selection | 50/160 (31.25%) | 88/160 (55.00%) | 72/160 (45.00%) | [37.14%, 53.05%] | -10.00 | [-20.00, -0.62] |
| multistep | 0/160 (0.00%) | 0/160 (0.00%) | 0/160 (0.00%) | [0.00%, 2.28%] | +0.00 | [+0.00, +0.00] |
| overall | 72/640 (11.25%) | 88/640 (13.75%) | 73/640 (11.41%) | [9.05%, 14.13%] | -2.34 | [-5.00, +0.00] |

## train

| Capability | v1.1 | v1.2 | v1.3 | IGF v1.3 | Gratuitous / incorrect required / repeated calls v1.3 | JSON/schema failures v1.3 |
|---|---:|---:|---:|---:|---:|---:|
| extraction | 16/112 (14.29%) | 0/112 (0.00%) | 0/112 (0.00%) | 0/7 (0.00%) | 35 / 0 / 0 | 62 |
| comparison | 2/112 (1.79%) | 0/112 (0.00%) | 0/112 (0.00%) | 0/7 (0.00%) | 39 / 0 / 0 | 72 |
| selection | 37/112 (33.04%) | 65/112 (58.04%) | 55/112 (49.11%) | 7/7 (100.00%) | 0 / 56 / 0 | 0 |
| multistep | 0/112 (0.00%) | 0/112 (0.00%) | 0/112 (0.00%) | 0/7 (0.00%) | 0 / 12 / 0 | 95 |
| overall | 55/448 (12.28%) | 65/448 (14.51%) | 55/448 (12.28%) | 7/28 (25.00%) | 74 / 68 / 0 | 229 |

## test

| Capability | v1.1 | v1.2 | v1.3 | IGF v1.3 | Gratuitous / incorrect required / repeated calls v1.3 | JSON/schema failures v1.3 |
|---|---:|---:|---:|---:|---:|---:|
| extraction | 4/48 (8.33%) | 0/48 (0.00%) | 0/48 (0.00%) | 0/3 (0.00%) | 1 / 0 / 0 | 44 |
| comparison | 0/48 (0.00%) | 0/48 (0.00%) | 1/48 (2.08%) | 1/3 (33.33%) | 16 / 0 / 0 | 29 |
| selection | 13/48 (27.08%) | 23/48 (47.92%) | 17/48 (35.42%) | 2/3 (66.67%) | 0 / 31 / 0 | 0 |
| multistep | 0/48 (0.00%) | 0/48 (0.00%) | 0/48 (0.00%) | 0/3 (0.00%) | 0 / 4 / 0 | 44 |
| overall | 17/192 (8.85%) | 23/192 (11.98%) | 18/192 (9.38%) | 3/12 (25.00%) | 17 / 35 / 0 | 117 |

## Uncertainty and inference limits

95% Clopper-Pearson is exact under IID/common-probability binomial sampling. Pooled heterogeneous-task intervals are nominal descriptive intervals, not task-population generalization claims.
Paired bootstrap resamples whole paired task means within category/split strata, retains all 16 seed outcomes per task, 5000 iterations, statistics seed 20261121.
Small strata (3 held-out tasks/category) make intervals coarse. A degenerate bootstrap interval from all-zero observed tasks does not prove zero uncertainty for unseen tasks.
Per-task 16-trial CP intervals and task-level SD/min/max are reported separately. No treatment of 640 outcomes as 640 independent tasks.

Per-seed fixes/regressions, task-level variability, first-lookup/continuation counts, pilot results and failure categories are in comparison.json. All scores are actual unchanged-verifier outcomes, not semantic oracle estimates. Metric/winner correlation and other v1 task defects remain. No general reasoning improvement can be claimed from comparison labels.
No training, new examples, prompt revision, output repair, task regeneration or test-set tuning. Only the requested rule was prepended, and the remaining v1.2 string is byte-identical.

## Interpretation and unexpected behavior

Observed combined successes: v1.1 72/640 (11.25%), v1.2 88/640 (13.75%), v1.3 73/640 (11.41%). Relative to v1.2 there are five fixes and 20 regressions; versus v1.1, 45 fixes and 44 regressions. No semantic/oracle score replaces these binary rewards.

Gratuitous calls on supplied-data tasks decline 153→91 (40.52% fewer). Extraction declines 97→36; comparison 56→55. These count accepted-form unnecessary calls; parsed top-level tool fields decline extraction 109→40 and comparison 147→137, including invalid mixed envelopes. Fewer calls do not produce correct finalization: extraction remains 0/160. Its 106 structure failures include 87 observation-shaped id/result objects; 84 of those contain the correct integer result in the wrong envelope. These are not counted as successes or automatically repaired.

Comparison has one success (0.625%); the winner/metric shortcut still prevents a reasoning interpretation. Selection falls 88→72/160 (55%→45%), retaining 81.82% of the aggregate score. Of the 88 originally successful selection samples, 68 remain successful (77.27% paired retention), four previously failed samples improve, and 20 regress. Required-tool names decline 144→121/160 even though protocol-valid selection actions improve 156→159/160. The trade-off is not explained by syntax alone.

JSON/schema failures increase 283→346 (invalid_json 94→94; invalid_format 189→252). Unknown tools remain zero, invalid arguments 4→1. Wrong required calls are 103, comprising selection 87 and multi-step 16; repeats are zero. Do not confuse wrong required calls with gratuitous lookups.

Multi-step has one correct first lookup, seed 503003: Meta spend for 2143-04-28 through 2143-04-30 returns id 1/result 72. The complete observation is verified in the next model input. The next raw output is exactly: `The tool call did not return the required data.` This fails invalid_json. Continuation correctness is 0/1; terminal success remains 0/160. The statement may mean that more platforms are needed or may reflect misreading; the trace does not uniquely establish the internal cause.

Only selection has informative training groups (7/7); the single mixed comparison group is held-out and must not enter training-data selection. Selection test has 2/3 mixed groups. Extraction and multi-step remain all-zero.

The decision-rule treatment changes behavior in a direction consistent with reduced Action Bias, but does not establish that Action Bias uniquely caused prior failures. A leading instruction also changes input length/position and generation probabilities. The joint objective—recover direct answers without losing selection performance—is not achieved.

Nominal pooled binomial 95% interval for v1.3 overall: [9.05%,14.13%], conditional on binomial assumptions, not 640 independent tasks. Paired task-cluster bootstrap change versus v1.2 is -2.34 pp with 95% interval [-5.00,0.00] pp; versus v1.1 +0.16 pp, [-4.53,+5.31] pp. Intervals are unadjusted descriptive estimates with small task strata, not generalization proof or causal-mechanism tests. Selection change versus v1.2 is -10.00 pp, paired task interval [-20.00,-0.625] pp. Per-instance CP intervals and task-level variability are in CSV/JSON.

Recommended next experiment: on training/validation only, test one synthetic observation-to-final-answer mapping example while holding the decision rule and all other material fixed. This targets the observed correct-result/wrong-envelope behavior without new benchmark hints. Keep it separate from a future shortcut-free benchmark redesign. No broad multi-capability GRPO claim or training is warranted by this result.

First-output JSON diagnostics use 640 first actions. Terminal failure categories include the one second-turn failure; hence 547 first responses parse while 94 rollouts ultimately fail invalid_json. There are 641 generated actions, not 641 benchmark rollouts.
