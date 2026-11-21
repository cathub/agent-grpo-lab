# 012 — Benchmark v1.3: tool-use decision boundary

## Date and research question

Client date 2026-11-21. VERIFIED full-run start UTC 2026-11-21T15:19:47.482409+00:00; finish 2026-11-21T15:29:30.370630+00:00. Can one explicit sufficiency rule recover direct answers without sacrificing v1.2 selection gains? No training or v2 implementation.

HYPOTHESIS: prioritizing supplied information attenuates prompt-induced Action Bias. Alternatives: additional instruction length/position changes generation without semantic decision improvement; correct observations may be echoed in unsupported envelopes; a shared tool-only example may still bias output. These are hypotheses, not established internal mechanisms.

## Exact single intervention and controls

Prepend exactly this string and one separating space to the otherwise byte-identical v1.2 prompt:

> Before calling a tool, determine whether the information already provided is sufficient to answer the user's question. If the information is sufficient, return the final answer directly using the required JSON schema. Otherwise, call the appropriate available tool to obtain the missing information. Do not call tools merely because tools are available.

Programmatic equality asserts `v1.3_prompt == RULE + ' ' + v1.2_prompt`; insertion occurs once, has no digits/platform-name hints, and changes no schema or example suffix. Config/diff: benchmark-configs/capability-v1.3.json and capability-v1.3-prompt.diff.

Same Qwen2.5-0.5B-Instruct-4bit, pinned revision a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3; versions {"mlx": "0.32.4", "mlx-lm": "0.30.7", "transformers": "5.23.0"}. Same 40 frozen records, 28 train/12 test, 16 samples each; temperature 0.7, top-p 1, max tokens 128; seeds 500000 + row_index*100 + sample_index (0..15). Dataset SHA-256 c7712fe925f53c0f6f65d699800ec3122b0604601af08b232935473931bc5586. Same frozen scorer, parser, lookup implementations, step limits and binary rewards. The v1.2 rollout function is reused unchanged.

## Static validation and pilot

VERIFIED: 42 tests before inference, 44 final tests after adding two uncertainty tests. Existing contract/negative/protocol checks pass. New checks assert the exact insert and unchanged schema/example/config. Concrete consistency checks cover sufficient supplied-data tasks, missing requested metrics in selection (unrelated information is insufficient), and every subset of the three required multi-step lookups. This is not a formal proof of English semantics outside the frozen reachable states. No genuine prompt/executor contradiction was found and no prompt revision occurred.

Exactly 16 new training-only v1.3 pilot samples: first training instance/category and its first four frozen seeds. V1.1/v1.2 controls are saved paired trajectories, not new inference. All 16 pilot v1.3 trajectories reproduced exactly in the full run. Pilot counts are not pooled into the full denominator.

| Category | v1.1 pilot successes | v1.2 | v1.3 | v1.3 JSON/schema failures |
|---|---:|---:|---:|---:|
| Extraction | 1/4 | 0/4 | 0/4 | 1/4 |
| Comparison | 0/4 | 0/4 | 0/4 | 2/4 |
| Selection | 0/4 | 2/4 | 2/4 | 0/4 |
| Multi-step | 0/4 | 0/4 | 0/4 | 4/4 |
| Overall | 1/16 | 2/16 | 2/16 | 7/16 |

Pilot v1.3 has two correct selection calls plus one correct multi-step first lookup; no successful continuation or multi-step finalization. No performance-based prompt adjustment or held-out tuning.

## Commands and artifacts

```sh
.venv/bin/python -m unittest discover -q
.venv/bin/python -m src.capability_v13 --output capability-runs/v1.3-decision
.venv/bin/python -m src.report_capability_v13
```

Raw local directory capability-runs/v1.3-decision; committed synthetic snapshots research-log/evidence/capability-v1.3. Includes exact inputs/raw outputs/observations, 640 rewards, pilot, full configuration, 1,280 paired comparisons (two controls), per-instance exact-binomial intervals, aggregate metrics, representative traces, envelope audit and one actual continuation. Manifest records SHA-256/source paths; provenance.json includes parent Git revision/source hashes and stats settings. No prior artifact changed.

## Full results

| Capability | v1.1 | v1.2 | v1.3 |
|---|---:|---:|---:|
| Extraction | 20/160 (12.50%) | 0/160 | 0/160 |
| Comparison | 2/160 (1.25%) | 0/160 | 1/160 (0.625%) |
| Selection | 50/160 (31.25%) | 88/160 (55.00%) | 72/160 (45.00%) |
| Multi-step | 0/160 | 0/160 | 0/160 |
| Overall | 72/640 (11.25%) | 88/640 (13.75%) | 73/640 (11.41%) |

| Capability | v1.1 train | v1.2 train | v1.3 train | v1.1 test | v1.2 test | v1.3 test |
|---|---:|---:|---:|---:|---:|---:|
| Extraction | 16/112 | 0/112 | 0/112 | 4/48 | 0/48 | 0/48 |
| Comparison | 2/112 | 0/112 | 0/112 | 0/48 | 0/48 | 1/48 |
| Selection | 37/112 | 65/112 | 55/112 | 13/48 | 23/48 | 17/48 |
| Multi-step | 0/112 | 0/112 | 0/112 | 0/48 | 0/48 | 0/48 |
| Overall | 55/448 | 65/448 | 55/448 | 17/192 | 23/192 | 18/192 |

Overall vs v1.2: -2.34 pp, five fixes/20 regressions. Vs v1.1: +0.16 pp, 45 fixes/44 regressions. Selection loses 10.00 pp versus v1.2, retains 81.82% of its aggregate score. Paired retention is different: 68/88 formerly correct selection samples remain correct (77.27%), with four new fixes and 20 regressions. No original scores are replaced by diagnostics.

## Confidence intervals and task variability

95% Clopper–Pearson nominal binomial intervals for v1.3: extraction [0,2.28%], comparison [0.016%,3.43%], selection [37.14%,53.05%], multi-step [0,2.28%], overall [9.05%,14.13%]. Per-instance 16-trial intervals, all train/test/category intervals, task min/max/SD and task means are in CSV/JSON.

Pooled intervals are exact only under the binomial/common-probability assumption; they are NOT an assertion of 640 independent tasks or exact unseen-task population coverage. Primary paired uncertainty resamples whole paired task means within capability/split strata, preserving 16 seeds/task: 5,000 bootstrap replicates, statistics seed 20261121. Overall change vs v1.2: -2.34 pp, percentile interval [-5.00,0.00] pp; vs v1.1 +0.16 pp, [-4.53,+5.31] pp. Selection change vs v1.2: -10.00 pp, [-20.00,-0.625] pp. These are unadjusted descriptive intervals, not multiple-testing significance claims.

Selection task rates range 0 to 87.5%, between-task SD 26.32 pp. Only three held-out tasks/category produce coarse uncertainty. Degenerate zero bootstrap intervals for all-zero observed categories do not establish zero uncertainty on unseen tasks or unseen seeds.

## Decision-boundary diagnostics

VERIFIED gratuitous accepted-form calls: extraction 97→36, comparison 56→55, combined direct tasks 153→91 (40.52% fewer). Parsed top-level tool fields also fall extraction 109→40, comparison 147→137; these include invalid envelopes and are not all executed calls.

Nevertheless, extraction remains zero: 106 invalid structures, 36 unnecessary calls, 18 wrong final answers. Of 106 invalid structures, 87 have exactly id/result keys; 84 contain the correct expected integer result but the wrong action envelope. No coercion or repair was performed. The inserted rule changes output behavior but does not solve final-answer representation.

Selection: protocol-valid first outputs 156→159/160, but correct required tool names 144→121/160 and successful full calls 88→72. Thus lost performance is not a simple decline in JSON syntax. Incorrect required calls: selection 87, multi-step 16, total 103. Verified repeats: zero. These are distinct from 91 gratuitous calls.

JSON/schema terminal failures rise 283→346: invalid_json 94→94 and invalid_format 189→252. Unknown tools stay zero; invalid arguments 4→1. No evidence supports a general protocol or reasoning improvement.

## Actual multi-step continuation

VERIFIED one first lookup among 160 episodes, training task multistep-0000/sample4/seed503003: get_ad_spend(meta,2143-04-28..30) returns id1/result72/donefalse. Exact observation and prior call are present in the second model input. Its next raw response is:

> The tool call did not return the required data.

This fails invalid_json. Continuation correctness 0/1, completion0/160. The text might refer to remaining platforms or might reflect misreading; the trace does not uniquely reveal an internal cause. Scripted continuation tests pass, but that is not model skill. Full record is observation-continuation.json. No unfinished valid branch is mislabeled a terminal failure; the environment actually ends every rollout.

## IGF and GRPO relevance

Training: selection 7/7 mixed, all other categories0/7. Test: selection2/3 and comparison1/3 mixed; extraction/multi-step0/3. The comparison signal is held-out and must not be used for gradients, training selection or tuning. Only selection currently supplies useful mixed terminal training groups. No process reward or training was added.

## Interpretation and next question

OBSERVATION: fewer gratuitous calls, no extraction recovery, one comparison success, reduced selection score, one partial multi-step advance and zero completion. The joint research objective is not achieved.

HYPOTHESIS: the behavior is consistent with attenuation of prompt-induced Action Bias, but this does not establish a unique internal mechanism. Prepending a rule also changes length, ordering, emphasis and sampling probabilities. For these fixed seeds the prompt-only treatment changes outcomes; it does not establish general reasoning improvement or explain every historical failure.

Known metric/winner correlation, future dates, generic 2024 example, limited test set and shared templates remain unchanged. The one comparison success cannot be claimed as numerical reasoning. No prompt was revised after pilot or test inspection.

Recommended next experiment: on training/validation only, test exactly one synthetic observation-to-final-answer mapping example, holding the decision rule and all other material fixed. This targets the 84 correct-result echoes without benchmark-specific hints. Keep a future shortcut-free v2 redesign separate. Do not start broad GRPO on the current evidence. No training or push occurred.
