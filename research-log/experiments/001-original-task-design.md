# 001 — Original task design

## 1. Date and evidence status

RECONSTRUCTED relative order, recorded during reconstruction on 2026-11-20 (America/Los_Angeles client date). Conversation places initial real runs around November 18 and later experiments before this reconstruction; exact individual run timestamps are UNVERIFIED. Filesystem mtimes are not treated as experiment dates. Git author dates are recorded separately and can disagree with chat dates.

## 2. Original hypothesis

Establish deterministic tool-use tasks and independent reference checking before model training.

## 3. Tasks and configuration

Level 1: 20 single-call January 1–3, 2025 tasks: 8 spend, 8 conversion and 4 ROAS. Tools get_ad_spend/get_conversions(platform,start_date,end_date), calculate_roas(revenue,spend). Example: Get spend for google from 2025-01-01 through 2025-01-01. Exact action keys tool/arguments; no final_answer. One model response. verify checks strict JSON/shape, exact tool and arguments, execution, numeric reference result. Binary success reward is added by evaluate. Original mock passes 12/20, not Qwen's later 8/10.

Level 1 split later represented by build_suite: 10 train / 5 validation / 5 test, preserving original tasks. Level 2: three tasks per split—platform conversions comparison, one campaign spend lookup, combined campaign revenue. Lookup tools get_ad_spend/get_conversions/get_revenue take platform/start_date/end_date and optional campaign (omit to aggregate). Training example asks Google brand spend February 1–3, 2025; one lookup returns 129, then final_answer 129. Step budgets 3, 2, 3 respectively.

Level 3: ROAS for one campaign (two lookups + ROAS + final, budget 4), compare campaign ROAS (four lookups + two ROAS + final, budget 7), conversion-constrained platform ROAS (nine lookups + three ROAS + final, budget 13). calculate_roas requires observation_id references to matching revenue/spend lookup scopes. Lookups produce id/result; final_answer carries number/name. Correct final value AND all required calls are necessary. Invalid actions, repeated/out-of-scope calls, or step exhaustion terminate unsuccessfully.

Both Level 2/3 use disjoint February windows per split; schemas/templates shared across splits. Ties differ by task: L2 platform alphabetically later; L3 campaign max tie rule favors brand; constrained platform alphabetically earlier. Exact task wording and labels are snapshotted in original-tasks.json. No original L2/L3 model system prompt existed in the initial commit: those were added with the Qwen adapter. The original mock was prompt-only parsing.

## 4. Commands and prompts

Commands below are RECONSTRUCTED from current entry points unless explicitly described as saved invocation evidence. Do not rerun them during historical reconstruction; many refuse to overwrite existing directories.

```sh
python3 -m src.benchmark
python3 -m src.environment train
python3 -m src.evaluation
```

Exact prompt components are in `../evidence/exact-prompt-components.json`. Full saved condition prompts and input messages are preserved in the relevant evidence snapshots. Initial prompt strings reconstructed from source are labeled RECONSTRUCTED rather than asserted to be captured inference logs.

## 5. Raw artifacts and Git references

`src/benchmark.py`, `src/scenarios.py`, `src/environment.py`, `src/verifier.py`, `src/episode_evaluation.py`; Git 6fea4d4. Full source snapshot and original-tasks.json preserve definitions.

Use `../evidence/manifest.json` to resolve original repository-relative paths to committed byte-identical snapshots and SHA-256 checksums. `6fea4d4` contains the original task/environment/evaluator design; `8cbae97` contains Qwen adapters and most early experiment runners. Later runner files were uncommitted at reconstruction and are preserved as evidence/source-snapshot; do not attribute them to 8cbae97.

## 6. Observed results (VERIFIED from saved artifacts)

Original mock score 12/20 (60%) is stated in original README and tests; no fresh benchmark was run during this reconstruction. Tests/scripts establish three-level task structure already exists at earliest available Git commit.

## 7. Interpretation at the time

RECONSTRUCTED from this research chat and successive experiment design, not a contemporaneously committed notebook: A multi-level simulator supplies objective feedback; no model training has occurred.

## 8. Later findings and corrections

There is no separate Git commit recording a chronological L1-only to L2/L3 evolution. The earliest checkpoint already contains all three levels. Do not invent intervening dates or claim later fixed-fixture defects existed in these original tasks.

## 9. Next question or decision

Introduce real local model inference, leaving original mock and scoring intact.
