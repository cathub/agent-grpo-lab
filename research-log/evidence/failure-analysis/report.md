# Audit of the frozen 640-rollout capability baseline

## Scope and evidence

No inference or training was run. No repository source, prompt, dataset, reward, or existing evaluation output was changed. All 640 trajectories were rechecked offline with the existing parser/environment: zero observation, status, or reward discrepancies. Source SHA-256 values are recorded in metrics.json and checked again after analysis.

All 640 saved episodes contain exactly one action. Exact input messages below are reconstructed from the frozen system/task inputs and saved evaluation loop; rendered prompts were not originally logged for this benchmark. No later model input or hidden observation is inferred. The classifier audits all failures; the complete audit and uncertain cases are in audit.csv/jsonl. Semantic-only confirmations were additionally inspected. This is an evidence-based lower-bound audit, not a replacement scoring run.

## Executive findings

- Recorded success is 16/640 (2.50%): extraction 7, comparison 3, selection 6, multistep 0.

- 390 invalid_json plus 11 invalid_format failures = 401. Only 50/401 (12.47%) are conservatively confirmed to contain an unambiguous correct task answer with presentation-only defects. The remaining 351 are NOT automatically correct answers; some contain wrong actions or conclusions and many remain ambiguous.

- Another 13 failures outside those 401 are confirmed semantic answers with wrong representation, for 63 confirmed formatting/schema-only failures overall. The resulting conservative oracle-format lower bound is 79/640 (12.34%), not 417/640.

- The new fixture exposes only three lookup tools and no campaign selector, but every system prompt advertises calculate_roas and optional campaign arguments. 56 parsed ROAS calls were classified unknown_tool; 15 parsed calls supplied an advertised campaign parameter. These are real protocol inconsistencies, not proof that those task attempts would otherwise succeed.

- Comparison and multistep labels have a perfect metric shortcut: spend -> google; conversions -> meta; revenue -> tiktok. The shortcut predicts all 20 labels without reading values. Multi-step reward still requires lookups, but its comparison decision can be shortcut after that.

- Multi-step did not reach its first successful tool observation in any of 160 episodes. The zero score does not test actual observation-to-next-action ability in this dataset.

## Observable verifier distribution

Percentages in the next table use all 640 attempts; category failure percentages later use category failures.

| Verifier outcome | Count | % of attempts |
|---|---:|---:|
| wrong_final_answer | 95 | 14.84% |
| unnecessary_call | 45 | 7.03% |
| invalid_json | 390 | 60.94% |
| invalid_arguments | 15 | 2.34% |
| invalid_format | 11 | 1.72% |
| unknown_tool | 56 | 8.75% |
| missing_requirements | 12 | 1.88% |
| success | 16 | 2.50% |



## Per-category outcomes

| Capability | Success | invalid_json | invalid_format | wrong_final_answer | unnecessary_call | unknown_tool | invalid_arguments | missing_requirements |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| extraction | 7/160 | 82 | 3 | 44 | 17 | 1 | 6 | 0 |
| comparison | 3/160 | 125 | 0 | 30 | 0 | 0 | 2 | 0 |
| selection | 6/160 | 66 | 1 | 0 | 27 | 53 | 7 | 0 |
| multistep | 0/160 | 117 | 7 | 21 | 1 | 2 | 0 | 12 |



## Likely cause classification (conservative)

Primary labels partition the 624 failures, but are diagnostic, not observed model mental states. Correct-semantic formatting-only cases require explicit evidence. Reasoning is restricted to valid typed scalar decisions that are wrong. Context labels require explicit unsupported claims that supplied data is absent. Wrong-format and wrong-content combinations stay mixed. Many potentially solvable outputs remain unclassified rather than receiving optimistic oracle credit.

Category 5 (benchmark/verifier issues) is cross-cutting and quantified separately below; it is not forced into a primary cause when the same action also fails the task. Zeros in conservative reasoning/context columns do not mean those underlying problems are absent.

| Capability | Failures | Formatting/schema-only | Reasoning | Tool/action | Context | Unclear/mixed |
|---|---:|---:|---:|---:|---:|---:|
| extraction | 153 | 61 (39.9%) | 0 (0.0%) | 26 (17.0%) | 0 (0.0%) | 66 (43.1%) |
| comparison | 157 | 2 (1.3%) | 11 (7.0%) | 2 (1.3%) | 24 (15.3%) | 118 (75.2%) |
| selection | 154 | 0 (0.0%) | 0 (0.0%) | 88 (57.1%) | 0 (0.0%) | 66 (42.9%) |
| multistep | 160 | 0 (0.0%) | 0 (0.0%) | 41 (25.6%) | 0 (0.0%) | 119 (74.4%) |
| overall | 624 | 63 (10.1%) | 11 (1.8%) | 157 (25.2%) | 24 (3.8%) | 369 (59.1%) |



## Conservative oracle-format analysis

Oracle credit means that an explicitly correct semantic task answer can be identified without supplying missing reasoning, guessing intended values, executing a new model turn, or changing original scores. Checks accept exact scalar numeric strings, unique correctly labeled singleton value wrappers, clear short observed-metric assertions with correct platform/value/date scope, and explicit correct winner assertions with no contradictory numerical claim. Merely mentioning the expected number, a hidden fixture winner, or one correct calculation inside a conflicting plan earns no credit. Removing a fence around a wrong tool/action does not make it correct. No actual outputs were repaired.

| Category | Recorded successes | Confirmed format-only failures | Oracle lower bound | JSON/format failures proven only |
|---|---:|---:|---:|---:|
| extraction | 7/160 | 61 | 68/160 (42.50%) | 50/85 |
| comparison | 3/160 | 2 | 5/160 (3.12%) | 0/125 |
| selection | 6/160 | 0 | 6/160 (3.75%) | 0/67 |
| multistep | 0/160 | 0 | 0/160 (0.00%) | 0/124 |
| overall | 16/640 | 63 | 79/640 (12.34%) | 50/401 |



The 351 residual JSON/format failures need semantic review or cannot establish full-task correctness from the saved output. This is not a finding that all 351 are semantically wrong. All 124 multistep JSON/format failures have no completed required lookup sequence; no oracle formatting transform can establish a full successful episode without sampling further actions, which this audit does not do.

## Why extraction differs from the 83.59% campaign result

Confirmed commonalities: identical model ID and package versions (mlx 0.32.4, mlx-lm 0.30.7, transformers 5.23.0); temperature 0.7, top-p 1, 128 tokens; strict integer type/value final-answer checking; no repair. The benchmark system prompt exactly equals the ORIGINAL campaign no-history system prompt, not the improved one.

Confirmed differences:

1. The 83.59% campaign result appended the explicit JSON-number/value-only instruction. That instruction is absent here.

2. Campaign used one repeated Google-brand spend value, 129, in plain retrieved-data text. Extraction spans ten scenarios, three metrics, different platforms and values (e.g. 260, 235, 643, 885), with an embedded observation object carrying id=1 and result. It does not provide observation provenance as a tool turn.

3. Campaign evaluated a restored scoring state with a completed lookup; extraction has no required calls and a one-action budget. A needless call immediately fails, rather than retrieving data already supplied.

4. Dates here are in 2142/2143 because generation adds seed*1000 days. Earlier campaign dates were February 2025. The only tool-call example uses June 2024. Model outputs often overwrite the task dates with 2024 dates.

5. Sampling seeds differ: benchmark 500000 + row_index*100 + sample_index versus campaign 20000..20063 and 30000..30063.

6. General tool instructions, three irrelevant schemas on extraction, and ROAS reference machinery remain present even for direct answers.

Extraction is therefore 7/160 (4.38%) combined, versus 107/128 (83.59%) on a different single-state, improved-prompt experiment. This is not a controlled estimate of one causal factor. Its 61 confirmed formatting-only failures show a major representation component, but do not justify predicting 83.59% on all extraction scenarios.

## Multi-step zero-success diagnosis

All 160 trajectories end after one model action, with zero successful tool results. There is no evidence here of a later-turn history omission or inability to use returned observations because no such model turns occurred.

Observable outcomes: 117 invalid JSON, 7 invalid format, 21 wrong final answers, 12 missing-requirement failures, 2 unknown tools, and 1 unnecessary call. Thirty-five parsed outputs contain final_answer on turn one (including malformed envelopes); they are premature without lookup evidence. Twelve return the correct name but earn zero because all three required calls are missing; this can be guessing or a metric shortcut, not verified comparison skill.

The budget of four actions permits exactly three correct lookups plus a final answer; no retries. Requests to output multiple tool calls in one response violate the one-action protocol. Many outputs attempt batches, fabricate dates or observation IDs, or discuss ROAS for a simple maximum comparison.

Offline retokenization found 74/160 multi-step texts at exactly 128 tokens (comparison 62, extraction 1, selection 2; 139/640 total). These are length-limit candidates, NOT confirmed stop reasons: the benchmark did not log finish_reason or generated token IDs. Increasing the cap alone cannot establish correct tools, dates, or rewards.

## Benchmark and verifier audit

1. **Advertised/executable tool mismatch (confirmed):** all prompts expose calculate_roas, but CapabilityEnvironment._call rejects every name outside the three lookup metrics. All 56 unknown_tool outcomes are parsed calculate_roas selections: extraction 1, selection 53, multistep 2. They are still inappropriate task choices; making the tool executable would not automatically make those samples pass.

2. **Parameter mismatch (confirmed):** schemas advertise optional campaign, while the fixture requires exactly platform/start_date/end_date. Fifteen parsed calls contain campaign (6 extraction, 2 comparison, 6 selection, 1 multistep). Many also use incorrect dates or scopes. These flags overlap other error modes and are not recoverable-success estimates.

3. **Synthetic observation identity (confirmed):** extraction embeds id=1 but the environment starts with no completed lookup. Attempts to use that id for ROAS are neither necessary nor valid. A purpose-specific extraction protocol would avoid this confusion.

4. **Type contract underspecification (confirmed):** instructions say JSON number, while integer expected values require exactly Python int; equivalent floats would fail. The main extraction failures here are strings/wrappers, so this is a contract problem, not an explanation for the whole score.

5. **Misleading failure label (confirmed):** unnecessary_call on a first action usually means wrong tool/scope, not a repeated call. With one turn in every saved episode, no repeated executed call exists in this benchmark.

6. **Generator defect / shortcut (confirmed):** condition=i%3 chooses both metric and forced winner. Spend always has Google as maximum, conversions Meta, revenue TikTok; 4/3/3 instances per comparison category. Train has 3/2/2 and test 1/1/1. All 20 comparison/multistep labels, including all six held-out labels, are predictable from metric alone. There is no need to read totals. Multi-step still requires lookups for reward, but ranking ability cannot be inferred from final-name gains. This is label leakage through a deterministic feature, not literal reference-answer insertion into prompts.

7. **Split integrity:** all 40 scenario IDs and date windows are distinct; no scenario paraphrase crosses train/test. That does not prevent the metric shortcut, template overlap, or index/seed-derived date artifacts.

8. **Reference/scoring checks:** 640/640 saved statuses/rewards reproduce offline. No evidence of a parser implementation regression or incorrect recorded rewards. Labels agree with the generated unique maximum or supplied extraction value. Unknown-tool naming and schema exposure are inconsistent, not arithmetic reference ambiguity.

9. **Comparability:** selection reward means correct next action, while multistep reward means full episode completion. Averaging these rewards is a mixed-capability index, not a uniform task difficulty measure. All rollout failures terminate at first error, with no output repair.

10. **Provenance limitation:** exact rendered prompts/stop reasons/token IDs were not saved in these 640 records. Message reconstruction is deterministic from frozen inputs; truncation is an estimate. Future baseline versions should preserve evaluator-source hashes and resolved model/tokenizer revisions, in addition to dataset hash and versions.

## Mixed-reward instances

Training: extraction 2/7, comparison 2/7, selection 3/7, multistep 0/7. Test: 1/3, 1/3, 1/3, 0/3 respectively. Seven of 28 training instances and three of 12 test instances are mixed. Held-out rewards must not be used to pick GRPO training examples or tune hyperparameters.

| Instance | Split | Successes / 16 |
|---|---|---:|
| capability-v1-42-extraction-0002 | train | 1/16 |
| capability-v1-42-extraction-0005 | test | 3/16 |
| capability-v1-42-extraction-0008 | train | 3/16 |
| capability-v1-42-comparison-0003 | train | 1/16 |
| capability-v1-42-comparison-0005 | test | 1/16 |
| capability-v1-42-comparison-0007 | train | 1/16 |
| capability-v1-42-selection-0000 | train | 2/16 |
| capability-v1-42-selection-0001 | test | 2/16 |
| capability-v1-42-selection-0006 | train | 1/16 |
| capability-v1-42-selection-0007 | train | 1/16 |



## Recommendations (ranked)

1. **Correct the benchmark contract in a NEW version — high impact, low/moderate effort.** Make advertised tools/arguments match execution, explicitly state integer vs number requirements, and remove unused ROAS machinery from extraction/comparison/selection where not applicable. Preserve v1 and do not rescore it under new rules.

2. **Remove the metric-to-winner shortcut — essential validity fix, low effort.** Independently balance requested metric, winner, platform order, and missing information. Add adversarial tests where the same metric has different winners in each split. Generate a fresh holdout; this already-inspected test set is no longer suitable for tuning new versions.

3. **Purpose-specific, frozen prompts — likely high impact, low effort.** On training/validation only, test the already-supported numeric-value instruction and explicit direct-answer task framing. Keep task-specific output schemas minimal. A single transition demonstration is promising for terminal extraction but its effect on this task distribution is untested. Do not assume previously measured campaign gains transfer.

4. **Keep a separately measured schema-constrained decoding arm — moderate effort.** It could isolate generation-format failures but changes the inference protocol; do not silently strip fences, coerce numbers, or replace the current baseline.

5. **Reduce multi-step difficulty in a diagnostic curriculum — moderate impact, moderate effort.** Add separate frozen one-lookup-plus-final and two-lookup comparison tasks before the three-lookup episode. First require reliable initial tool actions. The present data cannot diagnose later-turn memory or observation-to-final transitions.

6. **Improve diagnostic capture — low effort.** Save rendered inputs, token counts, stop reasons, exact prompt/schema hashes, checkpoint revision and scorer fingerprints. Log typed final-answer semantic diagnostics separately from strict reward.

7. **GRPO only after contract/shortcut fixes.** Extraction and selection have sparse mixed training rewards, but current learning signals are dominated by protocol compliance and include mismatched advertised tools. Comparison is confounded; multistep has no relative binary reward differentiation. A separate fixed-state campaign formatting experiment remains a cleaner narrow proof of concept, not evidence of general agent-reasoning improvement.

## Manual-review queue and uncertainty

There are 369 unclear/mixed primary cases. They include unsupported observation objects, malformed/incomplete ROAS actions, multi-action batches, correct intermediate numbers with wrong conclusions, and prose with conflicting scope. Review the rows in audit.csv (primary_cause=unclear/mixed) and the full raw output in audit.jsonl. The 351 JSON/format failures without oracle credit are a related but different set; neither count is a count of proven wrong reasoning. Automated evidence rules and human spot checks cannot infer latent model knowledge.

## Exact shared system prompt and schemas

The following string is the frozen system content used for every representative below. It includes all available schemas and the one-example suffix; it was not improved for this audit.

````text

Return exactly one JSON action per turn, without markdown, explanation, or tags. A tool action has exactly keys "tool" and "arguments". After the required tools, submit {"final_answer": value}, using a JSON number for amounts or ratios, or a lowercase name for comparisons. Date ranges include both endpoints. Preserve the requested scope. Do not duplicate calls. Tool observations contain id and result. calculate_roas requires revenue and spend objects with observation_id referencing earlier get_revenue and get_ad_spend observations for the same scope, not raw numbers. Perform all checks requested by the task before submitting the answer. Available tool schemas: [{"name": "get_ad_spend", "description": "Total ad spend in USD.", "parameters": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["google", "meta", "tiktok"]}, "start_date": {"type": "string", "description": "YYYY-MM-DD inclusive"}, "end_date": {"type": "string", "description": "YYYY-MM-DD inclusive"}, "campaign": {"type": "string", "enum": ["brand", "prospecting"], "description": "Optional; omit to sum all campaigns."}}, "required": ["platform", "start_date", "end_date"], "additionalProperties": false}}, {"name": "get_conversions", "description": "Total conversions.", "parameters": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["google", "meta", "tiktok"]}, "start_date": {"type": "string", "description": "YYYY-MM-DD inclusive"}, "end_date": {"type": "string", "description": "YYYY-MM-DD inclusive"}, "campaign": {"type": "string", "enum": ["brand", "prospecting"], "description": "Optional; omit to sum all campaigns."}}, "required": ["platform", "start_date", "end_date"], "additionalProperties": false}}, {"name": "get_revenue", "description": "Total revenue in USD.", "parameters": {"type": "object", "properties": {"platform": {"type": "string", "enum": ["google", "meta", "tiktok"]}, "start_date": {"type": "string", "description": "YYYY-MM-DD inclusive"}, "end_date": {"type": "string", "description": "YYYY-MM-DD inclusive"}, "campaign": {"type": "string", "enum": ["brand", "prospecting"], "description": "Optional; omit to sum all campaigns."}}, "required": ["platform", "start_date", "end_date"], "additionalProperties": false}}, {"name": "calculate_roas", "description": "Revenue divided by spend as a ratio.", "parameters": {"type": "object", "properties": {"revenue": {"type": "object", "properties": {"observation_id": {"type": "integer"}}, "required": ["observation_id"], "additionalProperties": false}, "spend": {"type": "object", "properties": {"observation_id": {"type": "integer"}}, "required": ["observation_id"], "additionalProperties": false}}, "required": ["revenue", "spend"], "additionalProperties": false}}] Example tool action (raw JSON, without Markdown fences): {"tool":"get_conversions","arguments":{"platform":"tiktok","start_date":"2024-06-10","end_date":"2024-06-12"}}

````

## Complete representative traces

An expandable HTML version is in representative-traces.html; machine-readable copies are in the four category representatives JSON files. There are 3–5 failures per category, plus one success where available. Every record below includes its full user task, expected output/behavior, raw action, observation and score. Shared system prompt above plus this user message constitute the complete model input; all saved trajectories have one turn. Fixture values/labels shown as expected behavior are evaluator-only, not additional model context.

### extraction

#### capability-v1-42-extraction-0002 / sample 8 / seed 500207

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Extract the revenue in USD for meta. Date range: 2143-01-06 through 2143-01-08. Observation: {"id": 1, "result": 235}

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [],
  "final_action": {
    "final_answer": 235
  },
  "selection_success_rule": null
}

````

Raw model output, before parsing (complete):

````text

{"final_answer": 235}

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "success"
}

````

Binary reward: **1**. Primary cause: **success**.

The original environment accepted the exact scalar answer or exact required next action.

Explicit correct scalar answer; only representation differs

Other evidence flags: none

#### capability-v1-42-extraction-0001 / sample 1 / seed 500100

System input: the exact shared system string above, unchanged.

User input (complete):

````text

What is the observed conversions for meta? Date range: 2143-01-02 through 2143-01-04. Observation: {"id": 1, "result": 529}

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [],
  "final_action": {
    "final_answer": 529
  },
  "selection_success_rule": null
}

````

Raw model output, before parsing (complete):

````text

The observed conversions for meta within the date range from 2143-01-02 to 2143-01-04 are 529.

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "invalid_json"
}

````

Binary reward: **0**. Primary cause: **formatting/schema only (confirmed lower bound)**.

Raw text is not a single strict JSON action (may be prose, fenced, incomplete, batched, or duplicate-key JSON). Correct semantics is not inferred without separate evidence.

Short explicit observed-metric assertion, correct platform/value, no competing numeric claim

Other evidence flags: none

#### capability-v1-42-extraction-0008 / sample 3 / seed 500802

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Extract the revenue in USD for meta. Date range: 2143-01-30 through 2143-02-01. Observation: {"id": 1, "result": 398}

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [],
  "final_action": {
    "final_answer": 398
  },
  "selection_success_rule": null
}

````

Raw model output, before parsing (complete):

````text

{"tool":"calculate_roas","arguments":{"revenue":{"observation_id":1}, "spend":{"observation_id":1}}}

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "unknown_tool"
}

````

Binary reward: **0**. Primary cause: **tool/action**.

The action selected calculate_roas, which is advertised but not executable by this fixture environment, and is not the required lookup for this task.

Ambiguous/mixed output; correct value occurrence alone is insufficient

Other evidence flags: ROAS material in irrelevant task; advertised tool rejected as unknown by fixture environment

#### capability-v1-42-extraction-0000 / sample 6 / seed 500005

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Extract the advertising spend in USD for meta. Date range: 2142-12-29 through 2142-12-31. Observation: {"id": 1, "result": 260}

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [],
  "final_action": {
    "final_answer": 260
  },
  "selection_success_rule": null
}

````

Raw model output, before parsing (complete):

````text

{"tool":"get_ad_spend","arguments":{"platform":"meta","start_date":"2024-12-31","end_date":"2024-12-31","campaign":"prospecting"}}

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "invalid_arguments"
}

````

Binary reward: **0**. Primary cause: **tool/action**.

Lookup arguments violate this fixture environment’s exact three-key/string contract. Optional campaign is advertised but rejected here.

Ambiguous/mixed output; correct value occurrence alone is insufficient

Other evidence flags: optional campaign advertised but rejected by fixture schema; incorrect date scope

#### capability-v1-42-extraction-0000 / sample 5 / seed 500004

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Extract the advertising spend in USD for meta. Date range: 2142-12-29 through 2142-12-31. Observation: {"id": 1, "result": 260}

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [],
  "final_action": {
    "final_answer": 260
  },
  "selection_success_rule": null
}

````

Raw model output, before parsing (complete):

````text

To calculate the advertising spend in USD for Meta, we need to use the "get_ad_spend" tool with the start and end dates provided by the "arguments" argument. Let's execute the tool action now.

{"tool":"get_ad_spend","arguments":{"platform":"meta","start_date":"2024-06-10","end_date":"2024-06-10"}}

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "invalid_json"
}

````

Binary reward: **0**. Primary cause: **unclear/mixed**.

Raw text is not a single strict JSON action (may be prose, fenced, incomplete, batched, or duplicate-key JSON). Correct semantics is not inferred without separate evidence.

Ambiguous/mixed output; correct value occurrence alone is insufficient

Other evidence flags: format verifier failure NOT proven formatting-only

### comparison

#### capability-v1-42-comparison-0003 / sample 16 / seed 501315

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Which platform has the highest advertising spend in USD from 2143-02-19 through 2143-02-21? Retrieved totals: meta=620; google=855; tiktok=400.

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [],
  "final_action": {
    "final_answer": "google"
  },
  "selection_success_rule": null
}

````

Raw model output, before parsing (complete):

````text

{
  "final_answer": "google"
}

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "success"
}

````

Binary reward: **1**. Primary cause: **success**.

The original environment accepted the exact scalar answer or exact required next action.

Explicit correct scalar answer; only representation differs

Other evidence flags: none

#### capability-v1-42-comparison-0002 / sample 12 / seed 501211

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Which platform has the highest revenue in USD from 2143-02-15 through 2143-02-17? Retrieved totals: google=531; tiktok=793; meta=783.

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [],
  "final_action": {
    "final_answer": "tiktok"
  },
  "selection_success_rule": null
}

````

Raw model output, before parsing (complete):

````text

{"final_answer": "The platform with the highest revenue is TikTok with a total of 793 USD."}

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "wrong_final_answer"
}

````

Binary reward: **0**. Primary cause: **formatting/schema only (confirmed lower bound)**.

The final answer fails the unchanged strict type/value check. See the exact expected value and raw output; wrappers and prose do not count as the requested scalar.

Explicit unique correct winner assertion with no contradictory numerical claim

Other evidence flags: none

#### capability-v1-42-comparison-0000 / sample 2 / seed 501001

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Which platform has the highest advertising spend in USD from 2143-02-07 through 2143-02-09? Retrieved totals: tiktok=521; google=551; meta=332.

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [],
  "final_action": {
    "final_answer": "google"
  },
  "selection_success_rule": null
}

````

Raw model output, before parsing (complete):

````text

{
  "final_answer": "tiktok"
}

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "wrong_final_answer"
}

````

Binary reward: **0**. Primary cause: **reasoning**.

The final answer fails the unchanged strict type/value check. See the exact expected value and raw output; wrappers and prose do not count as the requested scalar.

Semantic correctness not established conservatively

Other evidence flags: none

#### capability-v1-42-comparison-0000 / sample 4 / seed 501003

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Which platform has the highest advertising spend in USD from 2143-02-07 through 2143-02-09? Retrieved totals: tiktok=521; google=551; meta=332.

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [],
  "final_action": {
    "final_answer": "google"
  },
  "selection_success_rule": null
}

````

Raw model output, before parsing (complete):

````text

To determine the platform with the highest advertising spend, we need to look at the given information. However, the task only specifies the start and end date for the period from 2143-02-10 to 2143-02-12. Since the data is not provided directly for the exact start and end dates, we cannot accurately provide the answer based solely on the given information.

To fulfill the tool action requirement, I will now submit the observation of calculate_roas:

{"tool":"calculate_roas","arguments":{"revenue":{"observation_id":1},"spend":{"observation_id":2

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "invalid_json"
}

````

Binary reward: **0**. Primary cause: **context**.

Raw text is not a single strict JSON action (may be prose, fenced, incomplete, batched, or duplicate-key JSON). Correct semantics is not inferred without separate evidence.

Ambiguous/mixed output; correct value occurrence alone is insufficient

Other evidence flags: ROAS material in irrelevant task; format verifier failure NOT proven formatting-only

#### capability-v1-42-comparison-0000 / sample 11 / seed 501010

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Which platform has the highest advertising spend in USD from 2143-02-07 through 2143-02-09? Retrieved totals: tiktok=521; google=551; meta=332.

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [],
  "final_action": {
    "final_answer": "google"
  },
  "selection_success_rule": null
}

````

Raw model output, before parsing (complete):

````text

{"tool":"get_ad_spend","arguments":{"platform":"tiktok","start_date":"2024-02-10","end_date":"2024-02-12","campaign":"prospecting"}}

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "invalid_arguments"
}

````

Binary reward: **0**. Primary cause: **tool/action**.

Lookup arguments violate this fixture environment’s exact three-key/string contract. Optional campaign is advertised but rejected here.

Ambiguous/mixed output; correct value occurrence alone is insufficient

Other evidence flags: optional campaign advertised but rejected by fixture schema; incorrect date scope

#### capability-v1-42-comparison-0000 / sample 3 / seed 501002

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Which platform has the highest advertising spend in USD from 2143-02-07 through 2143-02-09? Retrieved totals: tiktok=521; google=551; meta=332.

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [],
  "final_action": {
    "final_answer": "google"
  },
  "selection_success_rule": null
}

````

Raw model output, before parsing (complete):

````text

To determine the highest advertising spend from the given date range, I will check the advertising spend for each platform:

1. TikTok: 521 USD
2. Google: 551 USD
3. Meta: 332 USD

Comparing the values, TikTok has the highest advertising spend.

To calculate the ratio, we'll divide the advertising spend by the total ad spend:

Advertising spend / Total ad spend = TikTok / Google = 521 / 551 = 0.931773173

Thus, TikTok has the highest advertising spend.



````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "invalid_json"
}

````

Binary reward: **0**. Primary cause: **unclear/mixed**.

Raw text is not a single strict JSON action (may be prose, fenced, incomplete, batched, or duplicate-key JSON). Correct semantics is not inferred without separate evidence.

Ambiguous/mixed output; correct value occurrence alone is insufficient

Other evidence flags: format verifier failure NOT proven formatting-only

### selection

#### capability-v1-42-selection-0000 / sample 6 / seed 502005

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Retrieve advertising spend in USD for meta from 2143-03-19 through 2143-03-21. No value for this metric has been retrieved. Return only the next tool action. Available unrelated information: {"platform": "meta", "metric": "get_conversions", "result": 675}

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [
    [
      "get_ad_spend",
      {
        "platform": "meta",
        "start_date": "2143-03-19",
        "end_date": "2143-03-21"
      }
    ]
  ],
  "final_action": null,
  "selection_success_rule": "exact next required lookup"
}

````

Raw model output, before parsing (complete):

````text

{"tool":"get_ad_spend","arguments":{"platform": "meta", "start_date": "2143-03-19", "end_date": "2143-03-21"}}

````

Actual observation/verifier result:

````json

{
  "id": 1,
  "result": 697,
  "done": true,
  "status": "success"
}

````

Binary reward: **1**. Primary cause: **success**.

The original environment accepted the exact scalar answer or exact required next action.

Single complete schema-correct required tool action with only external formatting

Other evidence flags: none

#### capability-v1-42-selection-0000 / sample 2 / seed 502001

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Retrieve advertising spend in USD for meta from 2143-03-19 through 2143-03-21. No value for this metric has been retrieved. Return only the next tool action. Available unrelated information: {"platform": "meta", "metric": "get_conversions", "result": 675}

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [
    [
      "get_ad_spend",
      {
        "platform": "meta",
        "start_date": "2143-03-19",
        "end_date": "2143-03-21"
      }
    ]
  ],
  "final_action": null,
  "selection_success_rule": "exact next required lookup"
}

````

Raw model output, before parsing (complete):

````text

{"tool":"calculate_roas","arguments":{"revenue":{"observation_id":1},"spend":{"observation_id":2}}}

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "unknown_tool"
}

````

Binary reward: **0**. Primary cause: **tool/action**.

The action selected calculate_roas, which is advertised but not executable by this fixture environment, and is not the required lookup for this task.

No unambiguous complete correct next action

Other evidence flags: ROAS material in irrelevant task; advertised tool rejected as unknown by fixture environment; wrong requested metric/tool

#### capability-v1-42-selection-0000 / sample 8 / seed 502007

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Retrieve advertising spend in USD for meta from 2143-03-19 through 2143-03-21. No value for this metric has been retrieved. Return only the next tool action. Available unrelated information: {"platform": "meta", "metric": "get_conversions", "result": 675}

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [
    [
      "get_ad_spend",
      {
        "platform": "meta",
        "start_date": "2143-03-19",
        "end_date": "2143-03-21"
      }
    ]
  ],
  "final_action": null,
  "selection_success_rule": "exact next required lookup"
}

````

Raw model output, before parsing (complete):

````text

{"tool":"get_revenue","arguments":{"platform":"meta","start_date":"2024-03-19","end_date":"2024-03-21","campaign":"prospecting"}}

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "invalid_arguments"
}

````

Binary reward: **0**. Primary cause: **tool/action**.

Lookup arguments violate this fixture environment’s exact three-key/string contract. Optional campaign is advertised but rejected here.

No unambiguous complete correct next action

Other evidence flags: optional campaign advertised but rejected by fixture schema; incorrect date scope; wrong requested metric/tool

#### capability-v1-42-selection-0000 / sample 4 / seed 502003

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Retrieve advertising spend in USD for meta from 2143-03-19 through 2143-03-21. No value for this metric has been retrieved. Return only the next tool action. Available unrelated information: {"platform": "meta", "metric": "get_conversions", "result": 675}

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [
    [
      "get_ad_spend",
      {
        "platform": "meta",
        "start_date": "2143-03-19",
        "end_date": "2143-03-21"
      }
    ]
  ],
  "final_action": null,
  "selection_success_rule": "exact next required lookup"
}

````

Raw model output, before parsing (complete):

````text

{"tool":"calculate_roas","arguments":{"revenue":{"observation_id":1},"spend":{"observation_id":675}}}" final_answer": {"revenue": {"observation_id": 1}, "spend": {"observation_id": 675}, "tool": "calculate_roas", "action": "requires advertiser's data"}}

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "invalid_json"
}

````

Binary reward: **0**. Primary cause: **unclear/mixed**.

Raw text is not a single strict JSON action (may be prose, fenced, incomplete, batched, or duplicate-key JSON). Correct semantics is not inferred without separate evidence.

No unambiguous complete correct next action

Other evidence flags: ROAS material in irrelevant task; format verifier failure NOT proven formatting-only

### multistep

#### capability-v1-42-multistep-0005 / sample 14 / seed 503513

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Use the tools to compare revenue in USD for meta, google, tiktok from 2143-05-18 through 2143-05-20. Retrieve all three totals and return the highest platform name.

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [
    [
      "get_revenue",
      {
        "platform": "meta",
        "start_date": "2143-05-18",
        "end_date": "2143-05-20"
      }
    ],
    [
      "get_revenue",
      {
        "platform": "google",
        "start_date": "2143-05-18",
        "end_date": "2143-05-20"
      }
    ],
    [
      "get_revenue",
      {
        "platform": "tiktok",
        "start_date": "2143-05-18",
        "end_date": "2143-05-20"
      }
    ]
  ],
  "final_action": {
    "final_answer": "tiktok"
  },
  "selection_success_rule": null
}

````

Raw model output, before parsing (complete):

````text

{"tool":"calculate_roas","arguments":{"revenue":{"platform":"meta","start_date":"2024-05-18","end_date":"2024-05-20"}, "spend":{"platform":"google","start_date":"2024-05-18","end_date":"2024-05-20"}}}

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "unknown_tool"
}

````

Binary reward: **0**. Primary cause: **tool/action**.

The action selected calculate_roas, which is advertised but not executable by this fixture environment, and is not the required lookup for this task.

No required tools executed; no output-only fix can satisfy full-task requirements

Other evidence flags: ROAS material in irrelevant task; advertised tool rejected as unknown by fixture environment

#### capability-v1-42-multistep-0000 / sample 10 / seed 503009

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Use the tools to compare advertising spend in USD for meta, tiktok, google from 2143-04-28 through 2143-04-30. Retrieve all three totals and return the highest platform name.

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [
    [
      "get_ad_spend",
      {
        "platform": "meta",
        "start_date": "2143-04-28",
        "end_date": "2143-04-30"
      }
    ],
    [
      "get_ad_spend",
      {
        "platform": "tiktok",
        "start_date": "2143-04-28",
        "end_date": "2143-04-30"
      }
    ],
    [
      "get_ad_spend",
      {
        "platform": "google",
        "start_date": "2143-04-28",
        "end_date": "2143-04-30"
      }
    ]
  ],
  "final_action": {
    "final_answer": "google"
  },
  "selection_success_rule": null
}

````

Raw model output, before parsing (complete):

````text

{
  "final_answer": "Meta"
}

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "wrong_final_answer"
}

````

Binary reward: **0**. Primary cause: **tool/action**.

The final answer fails the unchanged strict type/value check. See the exact expected value and raw output; wrappers and prose do not count as the requested scalar.

No required tools executed; no output-only fix can satisfy full-task requirements

Other evidence flags: premature final answer with no observations

#### capability-v1-42-multistep-0002 / sample 6 / seed 503205

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Use the tools to compare revenue in USD for tiktok, google, meta from 2143-05-06 through 2143-05-08. Retrieve all three totals and return the highest platform name.

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [
    [
      "get_revenue",
      {
        "platform": "tiktok",
        "start_date": "2143-05-06",
        "end_date": "2143-05-08"
      }
    ],
    [
      "get_revenue",
      {
        "platform": "google",
        "start_date": "2143-05-06",
        "end_date": "2143-05-08"
      }
    ],
    [
      "get_revenue",
      {
        "platform": "meta",
        "start_date": "2143-05-06",
        "end_date": "2143-05-08"
      }
    ]
  ],
  "final_action": {
    "final_answer": "tiktok"
  },
  "selection_success_rule": null
}

````

Raw model output, before parsing (complete):

````text

{
  "final_answer": "tiktok"
}

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "missing_requirements"
}

````

Binary reward: **0**. Primary cause: **tool/action**.

The final platform name is correct, but the required lookups were never executed; this is not terminal success.

No required tools executed; no output-only fix can satisfy full-task requirements

Other evidence flags: premature final answer with no observations

#### capability-v1-42-multistep-0000 / sample 1 / seed 503000

System input: the exact shared system string above, unchanged.

User input (complete):

````text

Use the tools to compare advertising spend in USD for meta, tiktok, google from 2143-04-28 through 2143-04-30. Retrieve all three totals and return the highest platform name.

````

Expected behavior/output (evaluator-side):

````json

{
  "required_tools": [
    [
      "get_ad_spend",
      {
        "platform": "meta",
        "start_date": "2143-04-28",
        "end_date": "2143-04-30"
      }
    ],
    [
      "get_ad_spend",
      {
        "platform": "tiktok",
        "start_date": "2143-04-28",
        "end_date": "2143-04-30"
      }
    ],
    [
      "get_ad_spend",
      {
        "platform": "google",
        "start_date": "2143-04-28",
        "end_date": "2143-04-30"
      }
    ]
  ],
  "final_action": {
    "final_answer": "google"
  },
  "selection_success_rule": null
}

````

Raw model output, before parsing (complete):

````text

```json
{
  "tool": "get_ad_spend",
  "arguments": {
    "platform": "meta",
    "start_date": "2024-04-28",
    "end_date": "2024-04-30"
  },
  "observation_id": 10000
}

{
  "tool": "get_ad_spend",
  "arguments": {
    "platform": "tiktok",
    "start_date": "2024-04-28",
    "end_date": "2024-

````

Actual observation/verifier result:

````json

{
  "done": true,
  "status": "invalid_json"
}

````

Binary reward: **0**. Primary cause: **unclear/mixed**.

Raw text is not a single strict JSON action (may be prose, fenced, incomplete, batched, or duplicate-key JSON). Correct semantics is not inferred without separate evidence.

No required tools executed; no output-only fix can satisfy full-task requirements

Other evidence flags: format verifier failure NOT proven formatting-only



## Bottom line

The current v1 benchmark is NOT ready as a clean general-capability GRPO target. Fix the advertised-versus-executable protocol and metric/winner leakage first in a versioned benchmark, freeze training/validation/test boundaries, and rerun a new baseline only after approval. Formatting is a major extraction bottleneck, but the 401 format failures are not 401 hidden successes. Multistep currently measures failure to enter the tool loop, not successful multi-turn reasoning.
