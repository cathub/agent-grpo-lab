# 007 — Four-category frozen benchmark v1

## 1. Date and evidence status

RECONSTRUCTED relative order, recorded during reconstruction on 2026-11-20 (America/Los_Angeles client date). Conversation places initial real runs around November 18 and later experiments before this reconstruction; exact individual run timestamps are UNVERIFIED. Filesystem mtimes are not treated as experiment dates. Git author dates are recorded separately and can disagree with chat dates.

## 2. Original hypothesis

Measure training-set improvement and held-out transfer by capability before future training.

## 3. Tasks and configuration

40 scenarios:10 each extraction/comparison/selection/multistep;7 train+3 test per category. Seed42.16 rollouts/instance =448train+192test. Seeds500000+row*100+sample. Original one-example prompt, NOT numeric instruction. Dates2142/2143 from seed*1000day offset. Environment subclass reuses parser, final checks, history; dispatches independent frozen totals. Selection terminates successfully on a correct next lookup; multistep requires3lookups+final, budget4. Other tasks budget1.

## 4. Commands and prompts

Commands below are RECONSTRUCTED from current entry points unless explicitly described as saved invocation evidence. Do not rerun them during historical reconstruction; many refuse to overwrite existing directories.

```sh
python -m src.capability_benchmark evaluate --dataset benchmarks/capability-v1/dataset.json --output capability-runs/base-before
```

Exact prompt components are in `../evidence/exact-prompt-components.json`. Full saved condition prompts and input messages are preserved in the relevant evidence snapshots. Initial prompt strings reconstructed from source are labeled RECONSTRUCTED rather than asserted to be captured inference logs.

## 5. Raw artifacts and Git references

`benchmarks/capability-v1/dataset.json`; `capability-runs/base-before/{summary.json,samples.jsonl}`; all snapshotted. Dataset SHA256 c7712fe925f53c0f6f65d699800ec3122b0604601af08b232935473931bc5586. This module/dataset were UNCOMMITTED at reconstruction, not part of8cbae97.

Use `../evidence/manifest.json` to resolve original repository-relative paths to committed byte-identical snapshots and SHA-256 checksums. `6fea4d4` contains the original task/environment/evaluator design; `8cbae97` contains Qwen adapters and most early experiment runners. Later runner files were uncommitted at reconstruction and are preserved as evidence/source-snapshot; do not attribute them to 8cbae97.

## 6. Observed results (VERIFIED from saved artifacts)

Train: extraction4/112,comparison2/112,selection4/112,multistep0/112; overall10/448. Test:3/48,1/48,2/48,0/48; overall6/192. Total16/640 (2.5%). Mixed training instances2/7,2/7,3/7,0/7; test1/3,1/3,1/3,0/3. After-training cells remain Not run.

## 7. Interpretation at the time

RECONSTRUCTED from this research chat and successive experiment design, not a contemporaneously committed notebook: Sparse mixed groups suggest capability-specific diagnostic value, but 401 JSON/format failures make raw score interpretation difficult.

## 8. Later findings and corrections

Later audit found advertised/executable schema mismatches and perfect metric/winner shortcut. These defects belong to capability-v1, not automatically to the original February2025 campaign environment. No v2 exists and no training comparison exists.

## 9. Next question or decision

Audit failures and validity before training or modifying v1.
