# Chronological research timeline

Dates use explicit evidence, not filesystem mtimes. Relative ordering is RECONSTRUCTED from the research chat and dependencies of saved runners. Exact run dates are mostly UNVERIFIED.

1. **VERIFIED Git checkpoint, 2026-11-15T17:31:13-08:00, `6fea4d4`:** original mock, Level1 benchmark, Level2/3 scenario environment, grouped evaluation and informative-group metrics already coexist. Separate earlier task-design commits are unavailable.
2. **RECONSTRUCTED around Nov18:** local arm64 Qwen setup; Level1 train8/10; subsequent L2/L3train0/3each.
3. **RECONSTRUCTED subsequent order:** root-cause inspection -> conditional tool-first A/B0 -> one action example enables1/3L2tool execution but0terminal success -> independent256token diagnostic0 -> tool-description A/B0.
4. **RECONSTRUCTED:** stochastic16/taskL2probe0/48 -> diagnostic rerun matches raw outputs and confirms five observations present -> partial-state probe yields10/16valid platform next-lookups,0campaign finalizations.
5. **RECONSTRUCTED:** fully observed finalization A/B0/160 -> complete synthetic transition example campaign60/64/platform0/16; plain-data campaign37/64/platform1/16.
6. **VERIFIED Git checkpoint, 2026-11-20T21:47:34-08:00, `8cbae97`:** local inference adapters and controlled early experiments committed together. This is not evidence of individual experiment execution dates. The chat's date context does not monotonically align with this Git author timestamp; preserve both rather than normalize away the discrepancy.
7. **RECONSTRUCTED after code push:** same-seed campaign reproduction37/64with64/64exactmatches; new-seed31/64. Numeric rule boosts combined68/128to107/128.
8. **RECONSTRUCTED:** frozen four-category v1 baseline16/640 -> read-only failure audit finds schema mismatches and metric-label shortcut.
9. **2026-11-20 client date, current reconstruction:** journal and blog outline created; no inference, benchmark revision or training.

Saved artifacts verify results and configurations, not most timestamps. See experiment entries for raw evidence, limitations and commands.

10. **2026-11-20 client date, VERIFIED artifacts:** [Benchmark v1.1 contract correction](experiments/009-benchmark-v1.1-contract.md), after four exact original-prompt smoke matches and passing contract tests. Same 640 seeds/tasks; 16 -> 72 successes, unknown_tool 56 -> 0; no training. Full UTC timestamps are in the entry and run metadata.

11. **2026-11-21 client date, VERIFIED artifacts:** [Benchmark v1.2 output protocol](experiments/010-benchmark-v1.2-protocol.md). Training-only paired pilot reproduced 16 v1.1 controls; frozen full run 72→88/640 but extraction/comparison regress to zero. Selection improves 50→88/160. No training; no test-set-driven revisions.

12. **2026-11-21, read-only regression audit:** [Entry 011](experiments/011-v1.2-regression-analysis.md) classifies all 31 losses and 47 fixes; Action Bias remains a hypothesis. No inference/training. Publication review pauses push because pending ancestors contain large raw rollouts and machine-specific provenance paths requiring explicit release approval.

13. **2026-11-21, VERIFIED v1.3 experiment:** [Entry 012](experiments/012-benchmark-v1.3-decision.md). Exact decision-rule prepend; 16-sample training pilot, then 640 frozen seeds. 73/640 versus v1.2 88/640; gratuitous calls 153→91, no extraction recovery, selection88→72/160, one first multi-step lookup then invalid-JSON continuation. Task-aware paired uncertainty recorded; no training or push.
