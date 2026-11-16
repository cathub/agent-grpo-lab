# agent-grpo-lab

A small lab for learning LLM post-training with SFT and GRPO. Day 1
implements a deterministic tool-calling benchmark with Python 3.9+ and
the standard library. It does not run a model, train anything, or call an API.

From the project directory:

```sh
python3 -m unittest discover -v
python3 -m src.benchmark
```

Each prompt expects a single JSON object with exactly two keys:

```json
{"tool":"get_ad_spend","arguments":{"platform":"google","start_date":"2025-01-01","end_date":"2025-01-03"}}
```

Google and Meta spend (USD) and conversions are synthetic daily totals.
Date ranges use YYYY-MM-DD and include both endpoints. ROAS is revenue
divided by positive spend, expressed as a ratio. The 20 tasks include eight
spend queries, eight conversion queries, and four ROAS calculations.
Reference results are specified independently of the tools.

The verifier reports the first failing check: malformed JSON
(`invalid_json`), wrong object shape (`invalid_format`), wrong tool
(`wrong_tool`), wrong arguments (`wrong_arguments`), tool exception
(`execution_error`), or a result that differs from the reference
(`wrong_result`). A call passes only if all checks pass.

The mock reads prompts without seeing the expected calls. It passes 12/20
tasks (60.0%); four have wrong arguments, two invalid JSON, and two wrong
tools. Unit tests also exercise format, execution, and result failures.

This is a smoke test for the verifier, not a measure of model capability.
Prompts use fixed templates, each task expects one canonical call, and
there are no multi-step tool chains or held-out tasks.

## Evaluation and logs

```sh
python3 -m src.evaluation --output-dir evaluation-output
```

`evaluate(tasks, sampler, metadata)` passes each task's prompt to
`sampler(prompt)`, which yields raw completion strings. It grades each string
with `verify()` and records a binary reward (1 for success, 0 for failure)
and the verifier's status. The mock alternates between the original mock and
the same parser with its deliberate errors disabled, for four samples per
prompt. Its scores illustrate the metrics using a fixed sampling pattern.

`write_evaluation(output_dir, rollouts, summary)` writes one record per sample
to `rollouts.jsonl` and writes metrics and run metadata to `summary.json`.
Task IDs follow the dataset order, and sample IDs start at one within each
task. Use the dataset version with the task ID when comparing logs. Update
the dataset and verifier version labels when their respective behavior changes.
Each file is overwritten when reusing the output directory.

Overall task success rate is weighted by rollout count. Per-prompt metrics
include success rate, mean reward, and population reward variance. A prompt
group is informative when it has both a success and a failure. The informative
group ratio uses all prompt groups as its denominator. Empty groups count as
non-informative, contribute no rollouts, and report zero for rates, mean, and
variance. Rates with a zero denominator are reported as zero.

A future Qwen3 adapter can implement the same `sampler(prompt)` interface.
It can build the chat input from the prompt, tool descriptions, and JSON
instructions, then yield the generated completion text for each sample.
The evaluator handles grading and logging. Record the Qwen3 checkpoint and
generation settings such as temperature, top-p, sample count, and seed in
`EvaluationMetadata`. Keep reference calls and expected results on the
evaluator side.

## Multi-level environment

The original 20 tasks and verifier are Level 1. Level 2 adds independent
lookups for cross-platform conversions, campaign spend, and combined campaign
revenue. Level 3 adds chained ROAS calculations, campaign comparison, and
a platform comparison with a minimum conversion requirement.

`build_suite(split)` in `src/scenarios.py` returns only the requested split.
Level 1 contributes 10 train, 5 validation, and 5 test tasks. Levels 2 and 3
each contribute three tasks per split and use disjoint February date windows.
Scenario templates are shared across splits, so this tests held-out prompts
and scopes rather than generalization to entirely new task types.
The expanded fixture has four days per split, three platforms (Google, Meta,
and TikTok), and two campaigns (brand and prospecting). Spend and revenue are
in USD and all date ranges are inclusive.

Use Python 3.9+ to list training tasks or interact with one locally:

```sh
python3 -m src.environment train
python3 -m src.environment train l3-train-roas
python3 -m unittest discover -v
```

`Environment(task)` starts with an empty trajectory. Each `step(raw_output)`
accepts one JSON string. For Levels 2 and 3, the lookup tools are
`get_ad_spend`, `get_conversions`, and `get_revenue`. Each takes
`platform`, `start_date`, and `end_date`; pass `campaign` to filter or omit
it to sum across campaigns. Use lowercase platform and campaign names. Example:

```json
{"tool":"get_revenue","arguments":{"platform":"google","campaign":"brand","start_date":"2025-02-01","end_date":"2025-02-03"}}
```

A successful lookup returns an observation with a numeric `result`, a
one-based `id`, and episode fields `done` and `status`. For Level 3,
`calculate_roas` takes observation references from earlier revenue and spend
lookups for the same platform, date range, and campaign. For example, after
revenue produces observation 1 and spend produces observation 2:

```json
{"tool":"calculate_roas","arguments":{"revenue":{"observation_id":1},"spend":{"observation_id":2}}}
```

Submit a final action such as `{"final_answer":"meta"}` for a platform
comparison. For spend and revenue, submit a JSON integer in USD. For ROAS,
submit a numeric ratio with enough precision to match within relative
tolerance of 1e-6 (absolute tolerance 1e-9). Level 1 ends on the original
single tool-call response and has no separate final-answer action.

The trajectory records each raw action and its observation. A successful
episode earns reward 1. Levels 2 and 3 require a correct final answer and
every specified lookup and calculation. Independent calls can be reordered
or interleaved. Duplicate or out-of-scope calls, malformed actions, execution
errors, missing requirements, incorrect answers, and exhausting the step
budget without a final answer terminate the episode with reward 0. An
alternative lookup scope, such as summing separate single-day lookups for
a requested date range, counts as out of scope. The budget counts every
action including the final answer.

For a future Qwen3 adapter, implement a factory with the interface
`sampler(prompt, level, sample_id) -> session`. Each fresh session receives
the trajectory so far and returns the next raw JSON action. Format the
level-specific tool instructions and observations as model input. The
evaluator keeps the reference answers and required scopes outside the
session. Call
`evaluate_episodes(build_suite("validation"), sampler, samples_per_prompt, metadata)`
and pass the returned results and summary to `write_evaluation()` for
JSONL and JSON logs. Use the training split for development and reserve test
for held-out evaluation.

The summary reports rollout success rate, informative group ratio, average
tool-call attempts per rollout, trajectory lengths (including terminal
actions), rewards, and failure counts by level. Final-answer correctness
uses submitted final answers as its denominator, even when a correct answer
failed the tool requirements. The summary also reports how many answers were
submitted. Level 1 reports final-answer correctness as null and counts its
single response as one attempt. Scripted multi-step sessions live in tests
to verify the pipeline.
