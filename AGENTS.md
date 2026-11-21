# Research experiment logging

For every experimental Codex task in this repository, update research-log/ as part of the same task before reporting completion. This applies to inference evaluations, prompt/scoring/benchmark changes, diagnostics, ablations, data generation, and future training. Pure unrelated maintenance does not require an experiment entry.

- Add a dated/versioned entry with hypothesis, task/split, exact prompt or prompt hash, model/checkpoint/adapter, decoding, seeds, command, code revision (or dirty-state source hashes), environment versions, artifacts, metrics, uncertainty, corrections and next question.
- Mark evidence VERIFIED, RECONSTRUCTED or UNVERIFIED. Preserve negative results and timestamp uncertainty; do not invent provenance.
- Save reproducible raw evidence or compact snapshots and SHA-256 manifests under research-log/evidence/. Never commit weights, credentials, company/proprietary data or virtual environments. Large local-only logs must have precise paths/hashes and documented recovery limitations.
- Keep old datasets, outputs and scores immutable. Change task/scorer/prompt versions explicitly; distinguish historical outcomes from new diagnostic oracle estimates.
- Keep train/validation/test boundaries explicit. Never use held-out rewards for gradients, training selection or tuning.
- State whether inference/training ran. Record unfinished/blocked evaluations separately from scored failures. No silent output repair.
- Extend timeline.md and corrections-and-limitations.md when evidence or conclusions change; never rewrite past claims as if later knowledge existed then.

This is a repository-level agent instruction, not a background automation. It does not authorize training, inference, or external publication without the task's existing scope.
