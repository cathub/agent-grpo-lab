# 004 — Informative groups and terminal-reward variation

## 1. Date and evidence status

RECONSTRUCTED relative order, recorded during reconstruction on 2026-11-20 (America/Los_Angeles client date). Conversation places initial real runs around November 18 and later experiments before this reconstruction; exact individual run timestamps are UNVERIFIED. Filesystem mtimes are not treated as experiment dates. Git author dates are recorded separately and can disagree with chat dates.

## 2. Original hypothesis

GRPO needs within-prompt reward contrast, not just a favorable aggregate success rate.

## 3. Tasks and configuration

IGF is the existing informative_group_ratio: fraction of prompt groups with 0<success_count<sample_count. group_metrics computes Bernoulli population variance p(1-p). This implementation already exists in Git6fea4d4; precise first conversational use of the acronym IGF is UNVERIFIED. Initial mock four-rollout alternation is an illustrative parser experiment, not real stochastic model evidence.

## 4. Commands and prompts

Commands below are RECONSTRUCTED from current entry points unless explicitly described as saved invocation evidence. Do not rerun them during historical reconstruction; many refuse to overwrite existing directories.

```sh
python -m src.qwen_group_probe
python -m src.qwen_diagnostic_probe
python -m src.qwen_partial_probe
python -m src.qwen_finalization_experiment
```

Exact prompt components are in `../evidence/exact-prompt-components.json`. Full saved condition prompts and input messages are preserved in the relevant evidence snapshots. Initial prompt strings reconstructed from source are labeled RECONSTRUCTED rather than asserted to be captured inference logs.

## 5. Raw artifacts and Git references

`qwen-level2-group16-temp07/summary.json`; `qwen-level2-group16-diagnostics/`; `qwen-partial-state-probe/`; `qwen-finalization-experiment/summary.json`. Theory in src/evaluation.py at6fea4d4.

Use `../evidence/manifest.json` to resolve original repository-relative paths to committed byte-identical snapshots and SHA-256 checksums. `6fea4d4` contains the original task/environment/evaluator design; `8cbae97` contains Qwen adapters and most early experiment runners. Later runner files were uncommitted at reconstruction and are preserved as evidence/source-snapshot; do not attribute them to 8cbae97.

## 6. Observed results (VERIFIED from saved artifacts)

Level2 one-example at temperature0.7,16/task:0/48; IGF0/3. Five first calls execute. Diagnostic rerun matches48 raw outcomes byte-for-byte; 53 turns, all five later prompts preserve calls/observations; 5 length stops. Partial states: platform10/16 valid next Meta lookup but0 immediate terminal successes; four identical campaign states0/16 each. Ten platform branches remain valid nonterminal, not scored terminal failures.

Full-data finalization with matched seeds: original platform0/16,campaign0/64; generic finalization rule also0/16,0/64—0/160 combined. All terminate; zero output truncations. No group has mixed terminal rewards.

## 7. Interpretation at the time

RECONSTRUCTED from this research chat and successive experiment design, not a contemporaneously committed notebook: L1 80% across tasks is insufficient: with one rollout/task, no empirical within-task variance is measured. Hard L2 tasks can yield all-zero groups. Moving to fixed partial states distinguishes next-action progress from eventual terminal success.

## 8. Later findings and corrections

Theory: for group-relative A=(r-mean)/(population_std+1e-8), all0/all1 yield zero centered advantages. Binary all-failure groups may still have nonreward regularization terms, but provide no relative terminal-reward ranking. IID Bernoulli model predicts mixed probability1-p^G-(1-p)^G; this is theoretical, not an empirical guarantee. Population versus sample standard deviation is an explicit convention, not an implemented training algorithm.

## 9. Next question or decision

Find fixed states with mixed terminal rewards, without introducing process rewards or training.
