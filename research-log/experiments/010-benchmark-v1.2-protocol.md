# 010 — Benchmark v1.2: output-protocol alignment

## Date, hypothesis and evidence

Client date 2026-11-21. VERIFIED full-run start UTC: 2026-11-21T08:02:33.563176+00:00; finish: 2026-11-21T08:17:46.725316+00:00. Hypothesis: explicit mutually exclusive JSON action forms, integer/string answer types and continuation rules improve protocol adherence without changing weights or scoring. This entry preserves a mixed/negative result, not a retroactively improved narrative.

## Frozen inputs and intervention

Same 40 task instances, 28/12 split, 640 seeds, 16 rollouts/instance, fixture executor, parser, exact required calls, step budgets and binary rewards as v1.1. Dataset SHA-256 c7712fe925f53c0f6f65d699800ec3122b0604601af08b232935473931bc5586. Scorer snapshot SHA-256 b5b3b82ce73d182c8d5f0308ee6141be9dcb399feda9f310e8f1fc24ed788b19.

Only the system instruction prefix changes; exact config/diff: benchmark-configs/capability-v1.2.json and capability-v1.2-prompt.diff. Tool schemas and old one-action example suffix are byte-identical. No new examples, benchmark answer values or hints are added. Instructions specify tool/arguments versus final_answer objects, required keys/no optional keys, string lookup arguments, integer numeric answers, lowercase platform names, no fences/prose, use of supplied data, and next lookup versus finalization after observations. The instruction block is longer; length, emphasis and token sequence change together.

Model: mlx-community/Qwen2.5-0.5B-Instruct-4bit. Physical local checkpoint pinned to the cache revision recorded by v1.1: a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3. Temperature 0.7, top-p 1, max tokens 128. Same package versions: {"mlx": "0.32.4", "mlx-lm": "0.30.7", "transformers": "5.23.0"}. Seed = 500000 + row_index*100 + sample_index, index 0..15. No weights changed. Earlier original-v1 checkpoint provenance remains historically incomplete; this run pins the v1.1 recorded revision.

## Commands and protocol preflight

```sh
.venv/bin/python -m unittest discover -q
.venv/bin/python -m src.capability_v12 --output capability-runs/v1.2-protocol
.venv/bin/python -m src.report_capability_v12
```

VERIFIED: 39 working-tree tests passed before inference; one diagnostic-validator test was subsequently added and final total is 40. Tests include all nine tool/platform combinations, exact argument sets, preserved example compatibility on a synthetic matching fixture, malformed/duplicate JSON, unknown tools, wrong argument types, wrong string/float final types, and scripted three-lookup observation passing plus successful finalization. The example is not claimed to match current frozen task dates. No benchmark task was edited to validate it.

## Training-only paired pilot

Frozen before inference: first training instance per category, first four original seeds each, 16 samples per arm. All 16 live v1.1 control trajectories match saved v1.1 exactly. No held-out task enters the pilot. Pilot v1.2 trajectories reproduce exactly when their seeds recur in the full run. Pilot records are separate and not included again in full-run denominators.

| Category | Pilot v1.1 success | Pilot v1.2 success | JSON/schema failures v1.1 → v1.2 |
|---|---:|---:|---:|
| Extraction | 1/4 | 0/4 | 0 → 1 |
| Comparison | 0/4 | 0/4 | 3 → 3 |
| Selection | 0/4 | 2/4 | 0 → 0 |
| Multistep | 0/4 | 0/4 | 4 → 4 |
| Overall | 1/16 | 2/16 | 7 → 8 |

Selection first calls execute 0→2; multi-step first lookups and later turns remain zero. Model outputs combine tool/arguments/final_answer despite explicit mutually exclusive instructions. This is noncompliance with an internally tested protocol, not evidence of an advertised/executable mismatch. No prompt revision was made for performance; revision count is zero.

## Full-run results

| Capability | v1.1 Train | v1.2 Train | v1.1 Test | v1.2 Test |
|---|---:|---:|---:|---:|
| Extraction | 16/112 | 0/112 | 4/48 | 0/48 |
| Comparison | 2/112 | 0/112 | 0/48 | 0/48 |
| Selection | 37/112 | 65/112 | 13/48 | 23/48 |
| Multistep | 0/112 | 0/112 | 0/48 | 0/48 |
| Overall | 55/448 | 65/448 | 17/192 | 23/192 |

Overall 72/640 (11.25%) → 88/640 (13.75%), +2.50 pp. Train 12.28%→14.51%, +2.23 pp; test 8.85%→11.98%, +3.13 pp. All v1.2 successes are selection tasks. Selection 50/160 (31.25%)→88/160 (55.00%). Extraction 20/160→0; comparison 2/160→0. Thus the aggregate gain masks severe capability regressions.

Paired fixes 47 (all selection), regressions 31 (22 former extraction/comparison successes plus nine selection successes). Of the fixes, 35 previously failed invalid_format, one invalid_json, and 11 unnecessary_call. Detailed task/seed changes are in paired.json and per-instance.csv.

JSON/schema verifier failures 385→283: invalid_json 253→94, invalid_format 132→189. Unknown tools stay zero; invalid arguments 2→4; unnecessary calls 61→231; wrong_final_answer 119→34. Strict JSON first responses 387→546/640; independent protocol-valid first actions 145→319/640. These diagnostics are not replacement rewards.

Selection correct required-tool names 82→144/160; protocol-valid actions 89→156/160; exact correct calls/executions 50→88/160. Multi-step executes zero first lookups and zero later turns; no empirical observation-handling opportunity exists. All 640 trajectories terminate after one action. Scripted continuation is verified separately, not attributed to model ability.

Correct typed final-value claims, including invalid envelopes, decline 41→27. Such claims may merely copy observations or exploit the metric/winner shortcut and do not establish successful reasoning or justify repaired rewards.

IGF train: extraction 7/7→0/7; comparison 1/7→0/7; selection 7/7→7/7; multistep 0/7→0/7. Test: extraction 1/3→0/3; comparison 0/3→0/3; selection 3/3→2/3; multistep zero. Overall mixed training groups drop 15/28→7/28 despite the aggregate score gain. Only selection provides mixed terminal rewards in v1.2.

## Artifacts and provenance

Raw local directory: capability-runs/v1.2-protocol/. Committed snapshots: research-log/evidence/capability-v1.2/, including raw per-turn input messages, outputs, observations, rewards, pilot, metrics, paired comparisons, representative cases and a SHA-256 manifest. Frozen config/diff are under benchmark-configs/. provenance.json records source hashes and parent commit 5544081, actual commands and reproduction checks. Historical v1/v1.1 artifacts are unchanged; unrelated working-tree work is excluded from the commit.

## Interpretation, limitations and next question

VERIFIED: clearer explicit instructions in this implementation improve JSON parsing and selection/action compliance, but not final-answer tasks. Zero multi-step first execution means later observation handling remains untested. Cannot estimate what fraction of v1.1 failures was CAUSED by unclear wording; this is a multi-part prompt intervention, not a decomposition of causal mechanisms.

HYPOTHESES: verbose shared instructions plus a tool-only example may bias tool invocation and mixed envelopes even when observations are already supplied. Merely mentioning prohibited fields might affect generation. These mechanisms were not isolated. No held-out result was used to tune the prompt. A small pilot on one metric per category has limited predictive power.

The metric/winner shortcut, unusual future dates, small/template-overlapping test set and tight four-action multi-step budget remain. No comparison accuracy gain may be interpreted as ranking ability. No formatting improvement is a trained reasoning gain.

Recommended next experiment: retain this result and test a shorter capability-specific protocol on training/validation only, or a separately labeled constrained-output diagnostic. Do not silently repair outputs. Remove ranking shortcuts only in a separately versioned benchmark; no v2 was implemented. Selection is the only narrow informative training group source here; broad multi-capability GRPO is not justified by these results. No GRPO/SFT training or automatic push occurred.
