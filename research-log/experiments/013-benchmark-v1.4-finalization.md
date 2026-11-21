# 013 — v1.4: Observation-to-Final-Answer diagnostic

## Research question and chronology

Client date 2026-11-21. VERIFIED run UTC 2026-11-21T15:52:57.048588+00:00 through 2026-11-21T15:55:56.400147+00:00. Can one unrelated finalization demonstration improve conversion of an already-executed lookup into the correct final-answer action? HYPOTHESIS: the shared tool-only example contributes to repeated tool actions; a finalization mapping may improve protocol compliance. This is not proof of an internal mechanism.

VERIFIED preservation step: reviewed committed v1.3 artifacts, 44 passing tests, configuration/results and sensitivity scan; fetched origin/main, verified ancestry, then normal fast-forward push `39898d1..25a7f1a` to origin/main. Published v1.3: https://github.com/cathub/agent-grpo-lab/commit/25a7f1a884fcdf81a4b338785fb7b1a1c353e08a . Its historical journal sentence “no push occurred” describes that earlier task, not this later publication. No historical entry was rewritten.

User explicitly authorized continuation with unrelated modified/untracked work left untouched. Fingerprints of all eight pre-existing files were captured outside the repository. None is part of this experiment's commit. Parent revision: `25a7f1a884fcdf81a4b338785fb7b1a1c353e08a`. New experiment files isolate implementation from those existing files; no worktree was necessary.

## Design frozen before inference

12 synthetic instances, six train/six validation, two per family: integer extraction, floating amount, comparison, native observation fields, user-context distractors, and supported two-platform revenue sum. Construction seed1414; dates/values generated independently of frozen benchmark expected answers. Comparison winner varies independently of metric and order. This tiny inventory cannot establish shortcut-free generalization. All required tool calls execute in the unchanged frozen CapabilityEnvironment before inference, and their exact histories/observations are replayed. One generated continuation per sample, no further tool executions permitted by the existing completed-requirement state. Initial calls are scripted context, not evidence of model tool selection.

Eight samples/state/condition =96/arm (192 new continuations), seeds `610000 + instance_index*100 + sample_index` (0–7). Preselected separate guard: first training instance of original extraction/comparison/selection, first four original seeds each =12/arm (24 rollouts), using the unchanged v1.2 rollout function. Guard A reproduces all12 saved v1.3 trajectories exactly. No test tasks selected, no full640 rerun, no training.

A = byte-identical v1.3 system prompt, including decision-rule prefix and existing tool-action example. B = A plus exactly this suffix (initial separating space included in frozen config):

> Unrelated synthetic finalization demonstration. Tool observation: {"id":1,"result":83,"done":false,"status":null} Assistant final action: {"final_answer":83}

83 is absent from all diagnostic values/answers. No benchmark answer is used as demonstration. Inputs otherwise identical, including all previous calls/observations. Exact full strings and diff: [config](../../benchmark-configs/capability-v1.4-diagnostic.json), [diff](../../benchmark-configs/capability-v1.4-prompt.diff). Frozen schema/expected answers are scorer metadata, not appended to model inputs.

Same `mlx-community/Qwen2.5-0.5B-Instruct-4bit`, revision `a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3`; MLX0.32.4, mlx-lm0.30.7, transformers5.23.0. Local Apple Silicon inference, cached pinned weights; no download or model changes. Temperature0.7, top-p1, max tokens128, initialization seed0 with explicit per-sample resets. Same tokenizer chat template, parser, executor, final verifier and binary reward. No output repair/retry/constrained decoding/process rewards. Source hashes and metadata are saved; historical checkpoint identity beyond recorded v1.3 remains subject to its prior caveats.

## Preflight and commands

48 unit tests passed before successful inference; final50 include additional diagnostic-type/strict-JSON checks. Tests verify deterministic JSON roundtrip, A/B exact diff, demo-value separation, actual native observation replay, scripted correct finalization of every state, rejection of repeated lookup, no semantic credit for ambiguous prose/nested outputs, and separation of type versus semantic correctness.

First launch stopped at frozen-config equality BEFORE inference/output creation because generated tuples and JSON lists differed. Only the NEW generator's JSON canonicalization was fixed; frozen JSON, prompts, tasks and settings stayed unchanged. Added roundtrip regression test; no model sample was discarded or retried. Successful command ran once:

```sh
.venv/bin/python -m unittest discover -s tests -q
.venv/bin/python -m src.capability_v14 --output capability-runs/v1.4-finalization
.venv/bin/python -m src.report_capability_v14 --output capability-runs/v1.4-finalization
```

Offline reporting replayed all192 actions against original scoring, checked every observation/history and all96 paired seeds/inputs. Separate guard replayed24 rollouts and compared12 A controls to saved v1.3. Missing observations:0. Original artifacts remain immutable. Source and artifact SHA-256 manifest: [evidence](../evidence/capability-v1.4/manifest.json).

## Verified results

All96/arm, strict binary reward: A0/96 (0%), B61/96 (63.54%); paired61 fixes/0 regressions. Conservative semantic correctness: A2/96 (2.08%), B61/96. The two A semantic successes were numeric strings in exact final wrappers and remained reward0. No semantic reinterpretation changes a recorded reward.

Compatible subset excluding the known float/prompt conflict: A strict0/80, semantic2/80; B strict45/80 (56.25%), semantic45/80. Float stress stratum: A0/16, B16/16, reported separately. Do not present63.54% as the result on an entirely prompt-consistent task set.

Per family (strict A→B; each16): integer0→15, float0→16, comparison0→0, native_fields0→14, distractors0→16, sum0→0. Per-state8-sample results are in [analysis](../evidence/capability-v1.4/analysis.json). B has two mixed-reward states: integer-1 (7/8), native_fields-1 (6/8); A none. No training follows from these observations.

A failures:89 unnecessary_call,3 invalid_format,2 wrong_final_answer,2 invalid_json. B failures:32 unnecessary_call,3 invalid_json. Valid strict JSON A94/96 versus B93/96. Exact final wrapper A2 versus B61; correct type inside wrapper A0 versus B61. Correct candidate type including permissible observation echoes also0 versus61. Observation-shaped outputs0 for both. Thus this intervention mainly changes action choice and final representation, not basic JSON validity.

Parsed top-level tool fields A92/96→B32/96. A has72 exact repeats of completed calls,20 other tool-field outputs (including three mixed envelopes); B16 exact repeats and16 other requests. All32 B tool attempts occur in comparison/sum states with complete observations. Existing executor returns unnecessary_call; no actual new lookup succeeds. Distinguish tool-field attempts from executed calls.

Separate training guard: extraction0/4→4/4 (four paired fixes), comparison0/4→0/4, selection2/4→2/4 with identical per-seed outcomes/trajectories. No strict regressions in this tiny sample; this does not establish broad safety. B's four comparison outputs are numbers551,561,551,332 instead of the expected platform string; A instead produced mixed envelopes/unneeded calls. Guard totals2/12→6/12 are never pooled with the192 diagnostic samples.

## Complete evidence and representative raw outputs

[Full representative traces](../evidence/capability-v1.4/report.md) contain unmodified system/user messages, actual assistant calls/user observations, raw continuation, parsed output, expected value, scoring history, status/reward and seed. [All192 samples](../evidence/capability-v1.4/samples.jsonl), [24 guard rollouts](../evidence/capability-v1.4/guard.json), [paired sample outcomes](../evidence/capability-v1.4/paired.json) preserve complete records. The model saw real tool history here; this is not the earlier No-History experiment.

Examples (raw outputs below are exact, full inputs in linked evidence):

- Integer-0/sample1/seed610000: A repeats `{"tool": "get_ad_spend", "arguments": {"platform": "meta", "start_date": "2026-03-01", "end_date": "2026-03-03"}}`; B `{"final_answer": 205}`, reward1.
- Native_fields-0/sample4/seed610603: A `{"final_answer": "307"}`, semantictrue but wrong type/reward0. The answer was present; representation was wrong.
- Integer-1/sample2/seed610101: B `Assistant final action: {"final_answer": 488}`, invalid_json/reward0. All three B invalid-JSON cases copy this prose label. The value is visible to a human, but conservative semantic diagnostics intentionally do not strip it or count it correct.
- Comparison-0/sample1/seed610400: B asks get_conversions(tiktok,2026-03-21..23) even though both requested meta/google observations are already supplied; unnecessary_call/reward0. The trace does not expose whether comparison arithmetic itself would be correct under a different action constraint.

## Uncertainty and scope limits

Nominal pooled95% Clopper–Pearson strict intervals: A[0,3.77%], B[53.09%,73.13%]. These condition on this tiny synthetic inventory and do not imply IID task sampling. Paired task-cluster bootstrap5000, statistical seed20261121: all-state delta+63.54pp, interval[60.42,66.67]pp; compatible delta+56.25pp,[52.50,60.00]pp. Two task means are resampled within each family, with train/validation pooled solely as development data, retaining paired seed outcomes. Per-state intervals are supplied. Tiny strata, template dependence, unadjusted comparisons and degenerate zero/all-success intervals limit inference; these are descriptive, not strong population significance claims.

VERIFIED design limitations disclosed before inference:

1. v1.3 says numeric amounts/counts “must be JSON integers”; float task answers are supported by the unchanged verifier but contradict that wording. Their success does not establish literal instruction compliance. Compatible-only metrics are the cleaner protocol comparison. Fixing this contradiction would be a separate version/intervention.
2. Supported native tool observations have only id/result/done/status. `native_fields` covers these real four fields, not nested/multiple metric fields. Irrelevant numeric distractors appear in labeled user metadata, not fabricated tool return fields. Richer observation structures remain untested.
3. Only two states/family; integer/native/distractor families share scalar-result structure. No evidence of generalization to arbitrary records, long histories or unseen domains. Comparison and sum have two observations; scalar extraction has one. Operation and history length are confounded.
4. Stop reasons, exact generated token counts and peak host memory were not logged by the unchanged backend; do not infer truncation from these records. All three B invalid JSON outputs have a prefix plus otherwise closed JSON; truncation is not evidenced there.
5. The demonstration labels may encourage literal label copying (observed3 cases), but this proposed mechanism remains HYPOTHESIS. No output was repaired. Changing the example labels/ordering would be another experiment.

## Interpretation and next experiment

VERIFIED: with B, correct typed scalar extraction occurs across multiple values/platforms, both splits, native metadata and user distractors. One example substantially improves wrapper/action compliance in these states, so an absolute model inability to read scalar observations or emit final_answer is contradicted. It does not fix two-observation comparison/sum: all32 still request tools, and the direct-comparison guard now returns the wrong answer type. Zero observation echoes here differs from historical v1.3 direct extraction; different contexts must not be pooled.

HYPOTHESIS: generalizing the action transition beyond one numeric observation is a remaining bottleneck, alongside task-dependent output representation. The current traces do not isolate arithmetic/comparison capability from history length, action selection or prompt interference. They do not prove end-to-end multi-step competence or a pure reasoning limitation.

Next, pre-register a small training/validation-only matched diagnostic separating operation (extract/compare/sum) from observation count, with compatible output wording. First test a single prompt factor (e.g. a platform-valued transition or removing the demonstration's prose label), separately from any constrained decoding test. Constrained decoding can address prefix/JSON errors but cannot prevent semantically unnecessary valid tool actions unless it changes allowed action space; report that intervention separately. Broader SFT/GRPO is premature; a larger-model control may help localize capability limits, and training would require fresh balanced tasks/holdout and informative training groups. No new experiment or training was started. V1.4 committed locally only; no push authorized.
