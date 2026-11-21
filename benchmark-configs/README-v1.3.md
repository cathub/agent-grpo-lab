# Benchmark v1.3: tool-use decision boundary

The sole model-visible change is prepending the exact requested decision rule
and one separator space to the byte-identical v1.2 system prompt. The frozen
configuration and raw diff are capability-v1.3.json and capability-v1.3-prompt.diff.
Tests assert exact equality, one occurrence, no numeric/platform hints in the
insert, unchanged tool schemas/example suffix, dataset hash, scorer hash,
decoding and sample schedule. No templates, examples or values are regenerated.

Static checks retain all existing contract/protocol/negative tests. Additional
checks cover the frozen decision states: extraction/comparison have sufficient
supplied data and no required calls; selection explicitly lacks the requested
metric (unrelated data does not supply it); multi-step only obtains all required
totals after all three required lookups. All subsets of its required calls are
checked against the unchanged final-answer verifier. This checks consistency
on concrete reachable fixture states, not a formal proof of English semantics
or a claim about hypothetical tasks outside this dataset.

```sh
.venv/bin/python -m unittest discover -q
.venv/bin/python -m src.capability_v13 --output capability-runs/v1.3-decision
.venv/bin/python -m src.report_capability_v13
```

The runner pins the v1.2 checkpoint revision and runtime versions. Pilot is
exactly 16 NEW v1.3 samples: first training task/category, first four existing
seeds. Saved paired v1.1/v1.2 cases are controls; neither older arm is rerun.
No held-out feedback enters the pilot. No performance-based prompt revision is
allowed. Full-run repetitions of pilot seeds must match their pilot trajectories.
Pilot counts remain outside the full 640 denominator. Outputs refuse overwrite.

Sampling stays temperature 0.7, top-p 1, max tokens 128. Seeds remain
500000 + row_index*100 + sample_index (0..15). The same 28/12 train/test split,
40 task records, original parser, tools, budgets and binary rewards are used.
The v1.2 rollout implementation is reused without modifications.

Exact Clopper-Pearson 95% binomial intervals are supplied per instance and for
pooled rates. Pooled heterogeneous-task intervals are NOMINAL under a binomial
assumption, not exact population generalization guarantees. The primary paired
change interval uses 5,000 whole-task paired bootstrap resamples, stratified by
category and split, with statistics seed 20261121. Each resampled task retains
all sixteen matched seed outcomes. Per-task rates, SD and ranges are separate.
With only three held-out tasks/category, uncertainty is coarse. Degenerate zero
bootstrap intervals do not establish no uncertainty on unseen scenarios. These
are unadjusted descriptive intervals, not multiple-comparison significance tests.

Reports distinguish gratuitous direct-answer calls, incorrect required calls,
repeats, parsed tool-name matches, full first-action correctness, first lookup
execution, observation continuation and terminal reward. Model noncompliance
is not evidence of a prompt/executor contradiction by itself. The metric/winner
shortcut and other historical benchmark limitations remain. No training or push.
