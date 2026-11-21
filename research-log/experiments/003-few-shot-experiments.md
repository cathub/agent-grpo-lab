# 003 — Prompt and protocol experiments

## 1. Date and evidence status

RECONSTRUCTED relative order, recorded during reconstruction on 2026-11-20 (America/Los_Angeles client date). Conversation places initial real runs around November 18 and later experiments before this reconstruction; exact individual run timestamps are UNVERIFIED. Filesystem mtimes are not treated as experiment dates. Git author dates are recorded separately and can disagree with chat dates.

## 2. Original hypothesis

Concrete protocol demonstrations might help more than verbal tool-use rules.

## 3. Tasks and configuration

All early arms keep the same 0.5B model, original tasks, strict environment, temperature 0/top-p 1/seed 0/128 tokens except the independent 256-token diagnostic. Condition ordering reconstructed from chat: conditional rule, tool-call-only example, description A/B, then stochastic groups. Original outputs preserved. Later transition demonstration is a distinct manipulation, not the same few-shot result.

## 4. Commands and prompts

Commands below are RECONSTRUCTED from current entry points unless explicitly described as saved invocation evidence. Do not rerun them during historical reconstruction; many refuse to overwrite existing directories.

```sh
python -m src.qwen_prompt_comparison
python -m src.qwen_fewshot_experiment
python -m src.qwen_description_experiment
python -m src.qwen_transition_experiment
```

Exact prompt components are in `../evidence/exact-prompt-components.json`. Full saved condition prompts and input messages are preserved in the relevant evidence snapshots. Initial prompt strings reconstructed from source are labeled RECONSTRUCTED rather than asserted to be captured inference logs.

## 5. Raw artifacts and Git references

`qwen-prompt-comparison/`; `qwen-fewshot-experiment/manifest.json`; `qwen-description-experiment/system-prompts.json`; `qwen-transition-experiment/{summary.json,rollouts.jsonl}`; prompt suffixes snapshotted exactly.

Use `../evidence/manifest.json` to resolve original repository-relative paths to committed byte-identical snapshots and SHA-256 checksums. `6fea4d4` contains the original task/environment/evaluator design; `8cbae97` contains Qwen adapters and most early experiment runners. Later runner files were uncommitted at reconstruction and are preserved as evidence/source-snapshot; do not attribute them to 8cbae97.

## 6. Observed results (VERIFIED from saved artifacts)

Conditional instruction: L2/L3 remain 0/3 and no executed tools. One synthetic get_conversions(tiktok,2024-06-10..12) action example: L2 still 0/3 but 1/3 enters tool loop; Google brand lookup yields129 then is repeated. L3 stays0/3. Original prompt at256 tokens remains0/3 at both levels. Description-only B:0/3 each, no tools; L3 valid envelope improves from0/3 to1/3 but incorrect premature final.

Later complete transition example replaces, rather than appends to, the tool-call-only example. Synthetic TikTok brand spend87: A platform0/16, campaign60/64; B no-history platform1/16, campaign37/64. A campaign and both B groups have mixed binary rewards.

## 7. Interpretation at the time

RECONSTRUCTED from this research chat and successive experiment design, not a contemporaneously committed notebook: Action demonstration can improve entry into tool loop; complete observation-to-final example can change terminal extraction behavior substantially.

## 8. Later findings and corrections

“Few-shot improves performance” must specify which example and endpoint: initial action-only example improves tool execution, not terminal success; complete numeric transition example reaches93.75% on a fixed campaign state but0% on platform. No trained weights exist. Description changes did not establish a capacity limitation.

## 9. Next question or decision

Isolate terminal finalization and exact scalar formatting versus history effects.
