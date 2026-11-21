# v1.4 post-observation diagnostic (not the 640-rollout benchmark)

Frozen config: [capability-v1.4-diagnostic.json](capability-v1.4-diagnostic.json).
A is the exact v1.3 system prompt; B appends one unrelated observation-to-final mapping.
The exact change is in [capability-v1.4-prompt.diff](capability-v1.4-prompt.diff).

12 deterministic synthetic states (six train/six validation), eight paired continuations per state/condition. No held-out benchmark task is used for development. `generation_seed=1414`; sample seeds `610000 + instance_index*100 + sample_index`, sample_index 0–7. Separate guard: first original training task in extraction/comparison/selection, four original seeds each; 24 rollouts total across A/B. Its A trajectories must reproduce saved v1.3 controls exactly.

Every initial lookup is executed by the unchanged frozen CapabilityEnvironment and replayed before inference. Inputs use the existing assistant tool-call / user `Tool observation: ...` convention. Only one NEW model action is generated per restored state. The original environment scores and terminates that action, including rejecting extra calls. No post-processing, repairs, retries or auxiliary rewards.

The original pinned MLX Qwen2.5-0.5B 4-bit checkpoint and installed versions are asserted. Temperature 0.7, top-p 1, max tokens 128, base initialization seed 0; explicit per-sample MLX seeds override initialization. Existing tokenizer chat template/inference backend unchanged. Local Apple Silicon setup: install `requirements-mlx.txt` into the existing environment, ensure the pinned cached checkpoint from v1.3 is available, then:

```sh
.venv/bin/python -m unittest discover -s tests -q
.venv/bin/python -m src.capability_v14 --output capability-runs/v1.4-finalization
.venv/bin/python -m src.report_capability_v14 --output capability-runs/v1.4-finalization
```

Inference refuses an existing output directory. Read-only reporting can be rerun without inference. The original full benchmark and all earlier results remain unchanged.

## Important scope limits

- Native tool observations contain `id`, scalar `result`, `done`, `status`. All states use this actual four-field structure. The `native_fields` family does NOT test nested or multiple metric results. Distractor numeric fields are explicit unrelated USER metadata, not invented executor response fields.
- Float values conflict with the unchanged v1.3 instruction demanding integer amounts/counts. Report this stress stratum separately; the compatible primary subset excludes it (80 samples/arm). The unchanged verifier supports floating answers; successful float output therefore does not establish compliance with the literal system wording.
- Comparison uses two completed conversion lookups with varied ordering and winner. Sum uses two completed revenue lookups and existing combined-revenue semantics. Neither requires a new tool or a modified executor.
- Semantic diagnostics accept only a scalar strict JSON value, an exact `final_answer` wrapper, or a native observation-shaped `result`. Numeric strings can be semantically correct but still receive reward 0. No prose/fence removal, nested search, or inferred arithmetic answers. Wrapper/type/semantic metrics are distinct.
- Two states per family and eight samples/state provide exploratory evidence only. The paired bootstrap holds family balance and resamples two paired task means per family, pooling train/validation solely as development data. Degenerate intervals do not imply certainty. No multiple-testing or unseen-task generalization claim.

Committed results and complete representative histories: [report](../research-log/evidence/capability-v1.4/report.md). Research entry: [013](../research-log/experiments/013-benchmark-v1.4-finalization.md). No training or v1.4 push.
