# 002 — Initial local Qwen baselines

## 1. Date and evidence status

RECONSTRUCTED relative order, recorded during reconstruction on 2026-11-20 (America/Los_Angeles client date). Conversation places initial real runs around November 18 and later experiments before this reconstruction; exact individual run timestamps are UNVERIFIED. Filesystem mtimes are not treated as experiment dates. Git author dates are recorded separately and can disagree with chat dates.

## 2. Original hypothesis

Replace hard-coded outputs with real generation and test increasing task difficulty.

## 3. Tasks and configuration

Qwen2.5-0.5B-Instruct-4bit, mlx-community conversion; local Apple M1 8GB, macOS 14.5, arm64 Python 3.11. MLX 0.32.4 / mlx-lm 0.30.7 / transformers 5.23.0 reported by subsequent saved metadata. Initial L1 metadata lacks a runtime package lock, so exact initial versions are RECONSTRUCTED rather than independently verified. Temperature 0, top-p 1, seed 0, 128 maximum tokens. L1 10 train tasks; L2/L3 3 train tasks each. L1 final output is tool JSON; episodes allow tool or final_answer.

## 4. Commands and prompts

Commands below are RECONSTRUCTED from current entry points unless explicitly described as saved invocation evidence. Do not rerun them during historical reconstruction; many refuse to overwrite existing directories.

```sh
python -m src.qwen_evaluation --output-dir qwen-evaluation-output
python -m src.qwen_episodes --level 2 --output-dir qwen-level2-output
python -m src.qwen_episodes --level 3 --output-dir qwen-level3-output
```

Exact prompt components are in `../evidence/exact-prompt-components.json`. Full saved condition prompts and input messages are preserved in the relevant evidence snapshots. Initial prompt strings reconstructed from source are labeled RECONSTRUCTED rather than asserted to be captured inference logs.

## 5. Raw artifacts and Git references

`qwen-evaluation-output/{summary.json,rollouts.jsonl}`; `qwen-level2-output/`; `qwen-level3-output/`. Exact L1/episode system strings reconstructed in prompt components; raw outputs snapshotted.

Use `../evidence/manifest.json` to resolve original repository-relative paths to committed byte-identical snapshots and SHA-256 checksums. `6fea4d4` contains the original task/environment/evaluator design; `8cbae97` contains Qwen adapters and most early experiment runners. Later runner files were uncommitted at reconstruction and are preserved as evidence/source-snapshot; do not attribute them to 8cbae97.

## 6. Observed results (VERIFIED from saved artifacts)

L1 8/10 (80%), two wrong_arguments: Meta January 2 spend/conversions start date incorrectly changed to January 1. L2 0/3: invalid_json 1, wrong_final_answer 2. L3 0/3: invalid_json 3. All L2/L3 episodes end before tool execution. Chat-reported L1 wall time 21.06 seconds included download/loading; timing output is not saved in evaluation JSON and is UNVERIFIED as an independently preserved artifact.

## 7. Interpretation at the time

RECONSTRUCTED from this research chat and successive experiment design, not a contemporaneously committed notebook: An 80% small-model single-call baseline collapses on more complex action protocol; investigate protocol and formatting before GRPO.

## 8. Later findings and corrections

This is 8/10 on the training split, not 80% across all 20 L1 tasks or unseen data. L2/3 zero does not measure later history use. Native Qwen tool template branch is not used; custom JSON is embedded in standard chat-template messages.

## 9. Next question or decision

Test minimal prompt changes and reward diversity without training.
