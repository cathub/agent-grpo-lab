# Agent GRPO Lab research journal

Reconstructed on 2026-11-20 using the client date, Git, saved synthetic experiments, and this research chat. No inference/training was run. Start with [timeline](timeline.md), then the eight [experiment entries](experiments/001-original-task-design.md). [Corrections](corrections-and-limitations.md) separate later knowledge from historical interpretations; [open questions](open-questions.md) records unresolved decisions.

## Evidence labels

- VERIFIED: directly checked in a saved artifact or Git object; scope is stated.
- RECONSTRUCTED: derived from source/task generator or chat chronology, not a captured timestamp/input log.
- UNVERIFIED: missing independent evidence. Never infer a run date from file modification time or assign a commit to a run without proof.

`evidence/manifest.json` records original paths, byte-identical committed snapshots, SHA-256 hashes and sizes. `evidence/external-logs.json` separately hashes local-only diagnostic logs. Raw diagnostics containing repeated rendered prompts remain local and are not duplicated wholesale; prompt snapshots, messages, raw rollout outcomes, summaries and source snapshots preserve essential evidence. No Gmail/Slack/company content is included: these are synthetic research fixtures. Keep model weights, credentials, caches and virtual environments out of Git.

The original `.gitignore` excludes most evaluation directories. This journal intentionally snapshots research evidence under a different version-controlled path; references alone would not survive a fresh clone. Source snapshots are historical evidence, not a second importable implementation or instruction to rerun inference.

## Future experiments

Repository AGENTS.md requires experimental tasks to add/update an entry before reporting completion, with exact configuration, commands, seeds, raw artifact hashes, results, limitations and negative findings. Never silently edit historical records; append explicit corrections. This is an agent instruction, not a background filesystem watcher or guarantee for experiments run outside Codex.

No GRPO training, IGF-driven task selection, or Benchmark v2 has been implemented in this reconstruction.
