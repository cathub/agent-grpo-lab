# 009 — Benchmark v1.1: prompt/executor contract correction

## Date, hypothesis and evidence

Client date: 2026-11-20. VERIFIED run UTC start: 2026-11-21T07:32:34.234998+00:00; finish: 2026-11-21T07:41:45.557371+00:00. Hypothesis: removing tools/arguments that the v1 fixture cannot execute will improve tool selection without changing tasks, reward or model weights. This is a controlled prompt intervention, not training or Benchmark v2.

## Baseline establishment

Read AGENTS.md, historical entries 007/008, committed v1 dataset/source/results, and failure-audit evidence. V1 configuration VERIFIED: 40 tasks, 28 train/12 test; 16 samples each; 448/192 rollouts; seed = 500000 + row_index*100 + sample_index. Dataset SHA-256: c7712fe925f53c0f6f65d699800ec3122b0604601af08b232935473931bc5586.

Model ID: mlx-community/Qwen2.5-0.5B-Instruct-4bit; 4-bit local MLX inference; temperature 0.7, top-p 1, max tokens 128. Runtime versions matched v1 exactly: {"mlx": "0.32.4", "mlx-lm": "0.30.7", "transformers": "5.23.0"}. Original resolved checkpoint revision is UNVERIFIED because v1 did not record it. Current cached revision: a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3. Four original-prompt model outputs reproduced exactly under the original seeds, providing empirical comparability evidence rather than proof of all 640 original samples or historical weight identity.

## Exact intervention

New config: benchmark-configs/capability-v1.1.json. Raw diff: benchmark-configs/capability-v1.1-prompt.diff.

1. Remove calculate_roas schema from advertised tools.
2. Remove its unusable observation-reference instruction sentence.
3. Remove optional campaign property from the three lookup schemas.

All remaining general instructions, tool descriptions, required arguments, one-example suffix and user prompts are unchanged. No numeric-output rule, extra example, schema-constrained generation, output repair, dataset regeneration or step-budget change. V1 task IDs remain unchanged to enable exact pairing. Scorer/parser/reward come from the committed v1 evidence source, not the unrelated uncommitted benchmark module. No historical artifact was overwritten.

## Commands and preflight

```sh
.venv/bin/python -m unittest discover -q
.venv/bin/python -m src.capability_v11 --output capability-runs/v1.1-contract
.venv/bin/python -m src.report_capability_v11
```

VERIFIED: all 36 working-tree tests pass (including pre-existing uncommitted benchmark tests); two new contract tests check nine tool/platform combinations and four scripted category successes. Tests verify advertised names and exact argument fields against actual execution. Preflight also enforces runtime-version and dataset-hash equality and four exact original-prompt raw model smoke matches. Full run only starts after preflight passes. No v1.1 prompt tuning follows test feedback.

## Results

| Capability | Train v1 | Train v1.1 | Test v1 | Test v1.1 |
|---|---:|---:|---:|---:|
| Extraction | 4/112 | 16/112 | 3/48 | 4/48 |
| Comparison | 2/112 | 2/112 | 1/48 | 0/48 |
| Selection | 4/112 | 37/112 | 2/48 | 13/48 |
| Multistep | 0/112 | 0/112 | 0/48 | 0/48 |
| Overall | 10/448 | 55/448 | 6/192 | 17/192 |

Combined: 16/640 (2.50%) -> 72/640 (11.25%), +8.75 percentage points. Paired: 64 fixed and eight regressed. Unknown tools: 56 -> 0. JSON/format failures: 401 -> 385, comprising invalid_json 390 -> 253 and invalid_format 11 -> 132. These categories shift substantially; disappearance of unknown_tool is not equivalent to universal success.

Of the 56 original unknown-tool failures, 16 now succeed, 28 fail action format, 11 fail required scope and one fails argument validation. Representative v1.1 failures include tool-action instead of tool, combined tool/arguments/final_answer objects, date substitutions, and string-valued numeric answers.

Selection tool-name match (diagnostic, not argument correctness): train 15 -> 56/112, test 7 -> 26/48. Executed correct selection actions: train 4 -> 37, test 2 -> 13. Multistep tool-name matches rise train 4 -> 43, test 1 -> 14, but zero correct first lookups, zero later model turns and zero completions remain. No empirical observation-handling opportunities occur; do not interpret a vacuous history check as success using observations.

IGF train: extraction 2/7 -> 7/7; comparison 2/7 -> 1/7; selection 3/7 -> 7/7; multistep 0/7 -> 0/7. Test: extraction 1/3 -> 1/3; comparison 1/3 -> 0/3; selection 1/3 -> 3/3; multistep 0/3 -> 0/3. Binary rewards remain task-specific: selection is next-action completion, multistep is full episode completion. No process rewards.

## Artifacts, provenance and preservation

Local raw run: capability-runs/v1.1-contract/. Version-controlled synthetic snapshots: research-log/evidence/capability-v1.1/. Included: 640 raw trajectories with per-turn messages, summary/config, preflight outputs, provenance hashes, comparison, 640 paired records, per-instance CSV and representative paired traces. manifest.json records source paths/checksums. Source parent commit: 9edb4d4; dirty new-source hashes are in provenance.json. Existing unrelated working-tree changes are not included in the experiment commit. Original v1 data, source snapshots and results remain byte-identical.

## Interpretation and limitations

VERIFIED: correct executable tool selection improves markedly, extraction improves, comparison does not, and multistep still cannot enter the loop. HYPOTHESIS: removing irrelevant ROAS/reference material reduces protocol distraction. The shorter input/token sequence is also a changed stimulus, so individual changes cannot all be assigned to a unique mismatch mechanism. We did not add executor capabilities or change scoring.

The perfect metric/winner shortcut, future dates, strict integer contract, early-error termination and missing original checkpoint revision remain. Test results are descriptive only and were not used to select new instructions. The four-sample original reproduction check is not a full original 640-rollout rerun. No hypothetical/oracle success estimates are included.

## Recommended next experiment

Do not call this a clean general-reasoning GRPO result. Separately diagnose one-action schema errors and numeric finalization on training/validation only. A later v2 should remove the metric/winner shortcut and independently balance conditions, but no such redesign is implemented here. Preserve v1/v1.1 for historical paired comparisons. No training and no push were performed.
