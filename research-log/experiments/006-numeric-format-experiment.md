# 006 — Numeric formatting instruction

## 1. Date and evidence status

RECONSTRUCTED relative order, recorded during reconstruction on 2026-11-20 (America/Los_Angeles client date). Conversation places initial real runs around November 18 and later experiments before this reconstruction; exact individual run timestamps are UNVERIFIED. Filesystem mtimes are not treated as experiment dates. Git author dates are recorded separately and can disagree with chat dates.

## 2. Original hypothesis

Explicitly requesting a JSON numeric scalar may fix many failures without weight updates.

## 3. Tasks and configuration

Exactly one rule is appended to original campaign no-history system; unchanged user input, model, seeds, temperature0.7,top-p1,max128, parser and strict integer scoring. Rule text saved in prompt-components numeric_rule and qwen-numeric-prompt-experiment/summary.json.

## 4. Commands and prompts

Commands below are RECONSTRUCTED from current entry points unless explicitly described as saved invocation evidence. Do not rerun them during historical reconstruction; many refuse to overwrite existing directories.

```sh
python -m src.qwen_numeric_prompt_experiment
```

Exact prompt components are in `../evidence/exact-prompt-components.json`. Full saved condition prompts and input messages are preserved in the relevant evidence snapshots. Initial prompt strings reconstructed from source are labeled RECONSTRUCTED rather than asserted to be captured inference logs.

## 5. Raw artifacts and Git references

`qwen-numeric-prompt-experiment/{summary.json,rollouts.jsonl}`; runner initially uncommitted at reconstruction, preserved as source snapshot. Baseline raw responses included per seed for pairing.

Use `../evidence/manifest.json` to resolve original repository-relative paths to committed byte-identical snapshots and SHA-256 checksums. `6fea4d4` contains the original task/environment/evaluator design; `8cbae97` contains Qwen adapters and most early experiment runners. Later runner files were uncommitted at reconstruction and are preserved as evidence/source-snapshot; do not attribute them to 8cbae97.

## 6. Observed results (VERIFIED from saved artifacts)

Seed20k:37->51/64;18 fixes,4 regressions. Seed30k:31->56/64;26 fixes,1 regression. Combined68->107/128 (53.125%->83.59375%),+30.46875pp. Modified failures:19 numeric strings,1 other string($129),1 numeric type mismatch129.0;0 objects,invalid JSON or incorrect numeric values. Exact fixed/regressed seed lists preserved in summary. Baseline numeric-string categorization includes string1.29; earlier string-other count differed by definition, not changed outcomes.

## 7. Interpretation at the time

RECONSTRUCTED from this research chat and successive experiment design, not a contemporaneously committed notebook: Prompt engineering substantially improves this fixed task; all-success not reached and both groups remain mixed.

## 8. Later findings and corrections

“Numeric JSON number” includes129.0, but the unchanged verifier requires Python int for integer labels. The instruction leaves that ambiguity. This is a narrow fixed-state formatting result, not a trained-model gain or multi-task generalization score.

## 9. Next question or decision

Build a frozen broader benchmark before deciding whether residual formatting errors justify GRPO.
