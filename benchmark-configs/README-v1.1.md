# Benchmark v1.1: advertised contract correction only

The config references the byte-identical, committed v1 dataset in
`research-log/evidence/benchmarks/capability-v1/dataset.json`. No task is generated
or edited. The scorer is loaded from the committed v1 source snapshot, so unrelated
uncommitted benchmark work is neither altered nor required for this experiment.

Only model-visible contract material changes:

1. Remove the `calculate_roas` tool schema, unsupported by this fixture executor.
2. Remove its observation-reference instruction sentence.
3. Remove the optional `campaign` property from all three lookup schemas.

The three tool descriptions, three required arguments, general action protocol,
one-example suffix, user prompts, labels, step budgets, binary reward and parser
are unchanged. The raw prompt diff is `capability-v1.1-prompt.diff`.
No numeric-format rule, new demonstration, decoding constraint or output repair
is added. The metric/winner shortcut and unusual future dates remain deliberately
unfixed; this is not Benchmark v2.

```sh
.venv/bin/python -m unittest discover -q
.venv/bin/python -m src.capability_v11 --output capability-runs/v1.1-contract
.venv/bin/python -m src.report_capability_v11
```

Output directories refuse overwrite. Preflight must pass before the 640-rollout
arm: nine executable schema/platform combinations, four scripted full-category
smokes, exact runtime-version match and four original-prompt raw-output matches.
If a check fails the runner stops rather than presenting a comparable baseline.

Original model ID: `mlx-community/Qwen2.5-0.5B-Instruct-4bit`. It is the same
4-bit model family/checkpoint name, but the original v1 run did not record a
resolved checkpoint revision. v1.1 records currently cached revisions; this
historical uncertainty cannot be removed retrospectively. The four exact original
smoke matches provide empirical reproducibility evidence, not proof of all 640
original outcomes or cryptographic identity to unrecorded original weights.

Temperature 0.7, top-p 1, max tokens 128; 16 samples per instance; seed
`500000 + row_index*100 + sample_index`, sample_index 0..15. All 40 original
instances and 28/12 split assignments are unchanged. Each sample resets its seed.

Outputs include per-turn model input messages, raw trajectories, binary rewards,
configuration snapshots, package versions, paired changes and per-instance CSV.
Do not use the held-out feedback to tune this prompt. The contrast is a prompt
intervention: removing unusable material also changes input length and token
sequence, so not every changed sample can be assigned a unique causal mechanism.
