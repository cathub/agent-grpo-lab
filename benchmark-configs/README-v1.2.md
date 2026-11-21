# Benchmark v1.2: frozen output-protocol instructions

Only the instruction prefix before `Available tool schemas:` changes from v1.1.
The schemas and existing example suffix are byte-identical. The new instructions
specify mutually exclusive tool/final objects, required keys, string lookup
arguments, integer amount/count answers, lowercase platform-name answers, no
optional fields or extra text, and how to continue after observations.

The frozen config is `capability-v1.2.json`; exact before/after text is in
`capability-v1.2-prompt.diff`. No numeric benchmark answer or new demonstration is
introduced. The existing June 2024 example is a generic schema-valid example,
not a correct action for the frozen 2142/2143 scenarios. Tests execute it against
a synthetic matching fixture with the unchanged scorer; no production task is
altered to make that test pass.

The existing 40 tasks, task IDs, labels, train/test assignments, binary reward,
lookup implementations, strict parser, step budgets and all 640 seeds remain
unchanged. The v1.1 cached model revision is pinned locally. Library versions
must match v1.1. Decoding: temperature 0.7, top-p 1, max tokens 128. A longer
instruction prefix changes the model input length and token sequence as well as
wording; this is a prompt intervention, not an estimate of a unique cause.

```sh
.venv/bin/python -m unittest discover -q
.venv/bin/python -m src.capability_v12 --output capability-runs/v1.2-protocol
.venv/bin/python -m src.report_capability_v12
```

The runner first performs a paired pilot on the first training task per category,
using its first four frozen seeds (16 samples per arm). Live v1.1 trajectories
must match saved results exactly. No held-out task enters the pilot. The v1.2
prompt is frozen before this pilot and is not revised for performance. Protocol
tests must pass. Full evaluation then resets every original seed, repeats the
pilot cases, checks exact reproduction, and writes 640 full-run records. Pilot
samples are not added to full-run denominators. Output directories cannot be
overwritten. No test-set feedback is used to tune or select this prompt.

Tests cover all executable tool names/arguments, preserved example compatibility,
incorrect types, duplicate/malformed JSON, unknown tools, action-envelope errors,
and scripted lookup-observation-final transitions. Model noncompliance does not
by itself establish a mismatch in the defined executable protocol.

Reports separate JSON parsing, protocol-valid first actions, explicit typed final
value claims, exact task correctness and terminal success. A correct value inside
an invalid action is not a repaired reward; comparison claims are not evidence
of numerical reasoning because the metric/winner shortcut remains. Recorded
raw outputs are never coerced or stripped. No training or benchmark v2 redesign.
