# Open questions before v2 or GRPO

1. What minimal versioned schema/fixture contract should replace the v1advertised ROAS/campaign mismatch?
2. How should metric,winner,platformorder,missinginformation and dates be independently balanced without shortcut leakage?
3. Should the scalar contract explicitly requireinteger or accept mathematically equal floats? Any change needs new scorer version and baseline.
4. Which training/validation-only prompt should be frozen before fresh held-out evaluation? Do not tune against the inspected12testinstances.
5. Does the numeric-format rule transfer across novel extraction values and metrics? Single129task results do not answer this.
6. Can a one-lookup-plus-final curriculum produce diverse terminal signals without process rewards? Does a transition example help platform decisions as well as numeric extraction?
7. Is fixed-state formatting GRPO a worthwhile proof of concept after inexpensive prompt fixes, and what generalization test would falsify success-by-memorization?
8. Capture checkpoint/tokenizer revision, scorer source hashes, exact rendered inputs, stop reasons, dependency lock and per-run start/end UTC timestamps in every future experiment.
9. Do any older local logs or commits exist outside the available two checkpoints? Until recovered, exact early run dates and some historical host details remainunverified.

Decisions deferred: noBenchmarkv2implementation and noGRPOtraining in this journal task.
