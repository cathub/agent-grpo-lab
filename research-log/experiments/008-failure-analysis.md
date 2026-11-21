# 008 — Read-only failure audit

## 1. Date and evidence status

RECONSTRUCTED relative order, recorded during reconstruction on 2026-11-20 (America/Los_Angeles client date). Conversation places initial real runs around November 18 and later experiments before this reconstruction; exact individual run timestamps are UNVERIFIED. Filesystem mtimes are not treated as experiment dates. Git author dates are recorded separately and can disagree with chat dates.

## 2. Original hypothesis

Determine whether low capability scores reflect representation, reasoning, context, or benchmark defects.

## 3. Tasks and configuration

No inference. Existing640raw trajectories offline replayed with unchanged environment; zero mismatches. Conservative semantic evidence rules classify all624failures, retaining369unclear/mixed rather than imputing hidden correctness. Nineteen representative full traces include reconstructed frozen inputs and complete raw outputs. Exact rendered prompt and finish reasons were not saved for these640rollouts.

## 4. Commands and prompts

Commands below are RECONSTRUCTED from current entry points unless explicitly described as saved invocation evidence. Do not rerun them during historical reconstruction; many refuse to overwrite existing directories.

```sh
# No historical inference command: read-only audit
# Analysis method preserved at research-log/evidence/failure-analysis/analysis-method.py
```

Exact prompt components are in `../evidence/exact-prompt-components.json`. Full saved condition prompts and input messages are preserved in the relevant evidence snapshots. Initial prompt strings reconstructed from source are labeled RECONSTRUCTED rather than asserted to be captured inference logs.

## 5. Raw artifacts and Git references

`research-log/evidence/failure-analysis/{report.md,metrics.json,audit.csv,audit.jsonl,analysis-method.py}`; original output paths/hashes in manifest. Selected HTML report remains in the chat workspace outputs; complete per-sample raw traces are preserved in samples.jsonl.

Use `../evidence/manifest.json` to resolve original repository-relative paths to committed byte-identical snapshots and SHA-256 checksums. `6fea4d4` contains the original task/environment/evaluator design; `8cbae97` contains Qwen adapters and most early experiment runners. Later runner files were uncommitted at reconstruction and are preserved as evidence/source-snapshot; do not attribute them to 8cbae97.

## 6. Observed results (VERIFIED from saved artifacts)

390invalid_json+11invalid_format=401.50/401confirmed formatting-only;351not established.63confirmed format/schema-only failures across all statuses; oracle-format lower bound79/640, including68/160extraction. These are diagnostic counterfactual lower bounds, not new recorded rewards. Other primary causes:157tool/action,11conservative reasoning,24context,369mixed. All640episodes one turn; zero successful multistep observations.56unknown_tool actions select advertised ROAS;15parsed calls include advertised optional campaign rejected by fixture shape.52parsed tool actions have wrong date scope.139outputs retokenize to128tokens: truncation candidates, not saved stop reasons.

## 7. Interpretation at the time

RECONSTRUCTED from this research chat and successive experiment design, not a contemporaneously committed notebook: Benchmark is not a clean general-capability GRPO target; fix schema contract and shortcut in a future version before training.

## 8. Later findings and corrections

Metric determines winner in all20comparison/multistep labels: spendGoogle,conversionsMeta,revenueTikTok, includingheldout. Scoring replay consistency does not establish construct validity. All1turn failures do not demonstrate later-turn history loss. Correct-name multistep outputs withoutrequiredcalls legitimately getmissing_requirements; some mayguessshortcut. The earlier83.59% campaign used the numeric rule absent in v1 and a different repeated task/context.

## 9. Next question or decision

Propose v2 only after journal review; no v2 implementation or GRPO is authorized by this reconstruction task.
