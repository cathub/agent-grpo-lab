# 005 — Campaign no-history seed evaluations

## 1. Date and evidence status

RECONSTRUCTED relative order, recorded during reconstruction on 2026-11-20 (America/Los_Angeles client date). Conversation places initial real runs around November 18 and later experiments before this reconstruction; exact individual run timestamps are UNVERIFIED. Filesystem mtimes are not treated as experiment dates. Git author dates are recorded separately and can disagree with chat dates.

## 2. Original hypothesis

Can the model emit a correct scalar answer from sufficient plain-text retrieved data, reproducibly?

## 3. Tasks and configuration

Original system = episode_instructions()+EXAMPLE, not complete transition demonstration and not numeric instruction. User task asks Google brand spend February1–3,2025; plain-text retrieved total129 USD is appended. Only system+user messages enter model. Environment privately replays one correct lookup so required calls are satisfied for unchanged scoring. Expected final integer129. Temperature0.7,top-p1,max128, matched per-rollout seeds. No additional expected-answer hint beyond observed data.

## 4. Commands and prompts

Commands below are RECONSTRUCTED from current entry points unless explicitly described as saved invocation evidence. Do not rerun them during historical reconstruction; many refuse to overwrite existing directories.

```sh
python -m src.qwen_transition_experiment
python -m src.qwen_nohistory_reproduction
```

Exact prompt components are in `../evidence/exact-prompt-components.json`. Full saved condition prompts and input messages are preserved in the relevant evidence snapshots. Initial prompt strings reconstructed from source are labeled RECONSTRUCTED rather than asserted to be captured inference logs.

## 5. Raw artifacts and Git references

`qwen-transition-experiment/summary.json` B_plain_data; `qwen-nohistory-reproduction/{summary.json,rollouts.jsonl}`. Saved raw model input and full diagnostics remain local; journal snapshots include exact messages, outputs, source hashes and provenance.

Use `../evidence/manifest.json` to resolve original repository-relative paths to committed byte-identical snapshots and SHA-256 checksums. `6fea4d4` contains the original task/environment/evaluator design; `8cbae97` contains Qwen adapters and most early experiment runners. Later runner files were uncommitted at reconstruction and are preserved as evidence/source-snapshot; do not attribute them to 8cbae97.

## 6. Observed results (VERIFIED from saved artifacts)

Seeds20000–20063:37/64 (57.8125%),26 wrong_final_answer,1 invalid_json. Reproduction matches64/64 raw responses, outcomes and rewards. Seeds30000–30063:31/64 (48.4375%),32 wrong_final_answer,1 invalid_json. Combined68/128 (53.125%); not128 independent tasks. Both seed groups are informative.

## 7. Interpretation at the time

RECONSTRUCTED from this research chat and successive experiment design, not a contemporaneously committed notebook: An isolated no-history finalization state has reproducible mixed binary reward, unlike previous all-zero full-history groups.

## 8. Later findings and corrections

No-history is model-visible context only; scoring still restores a real required lookup. It is not a zero-tool episode from an empty environment. Most failures package129 as string/prose/object. It is not evidence that the model cannot read129. Early group summary versions copied package metadata from prior runs rather than independently recording all host details.

## 9. Next question or decision

Test whether one numeric-output instruction solves the format problem before considering GRPO.
