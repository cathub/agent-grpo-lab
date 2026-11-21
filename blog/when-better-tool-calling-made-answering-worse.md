# When Better Tool Calling Made My Agent Worse at Answering Questions

Status: draft research outline, not published. No training occurred.

1. **A misleading upward curve.** v1 16/640 (2.50%), v1.1 72/640 (11.25%), v1.2 88/640 (13.75%). All values are saved baseline observations, not trained improvements.
2. **The capability breakdown changes the story.** Selection improves 6→50→88/160. Extraction regresses from v1.1 20/160 to zero; comparison 2/160 to zero. Multi-step remains zero and never reaches an observation.
3. **What changed.** V1.1 removed unsupported advertised contract material. V1.2 replaced the instruction prefix while preserving schemas, example, tasks, seeds and scoring.
4. **Read the paired failures.** Of 31 regressions, 12 needlessly call tools on supplied extraction data, nine use wrong tools/scopes in selection tasks, five have invalid structures, four have type-only failures and one returns an end date instead of revenue. Exact before/after evidence is linked below.
5. **Action Bias — a hypothesis.** Tool-field outputs grow 14→109 for extraction and 8→147 for comparison. This supports the behavioral description of more tool-oriented output. It does not prove a unique prompt-induced internal mechanism; length, ordering, negative instructions and the unchanged example also matter.
6. **Formatting is not task success.** JSON/schema errors decline 385→283 while unnecessary calls increase 61→231. A valid call can be the wrong action. A correct scalar inside an invalid envelope still fails.
7. **The GRPO decision is still open.** Only selection has informative training groups in v1.2. Broad reasoning claims remain blocked by benchmark shortcuts and absent multi-step progress. Test cheaper prompt/protocol hypotheses first, on training/validation only.

Evidence: [regression journal](../research-log/experiments/011-v1.2-regression-analysis.md), [all 31 pairs](../research-log/evidence/v1.2-regression-analysis/regressions.json), [successful changes](../research-log/evidence/v1.2-regression-analysis/fixes.json). Do not turn this outline into a published article without a separate request.

## v1.3 follow-up: fewer calls did not mean better answers

VERIFIED: one decision-rule prepend reduced gratuitous calls153→91, but extraction stayed0/160. Selection fell88→72/160; overall73/640. Eighty-four failed extraction replies preserved the correct result inside an observation-shaped envelope. One multi-step lookup succeeded, then continuation failed. Action Bias attenuation is consistent with the direction of behavior, not a confirmed unique mechanism. Distinguish nominal binomial intervals from paired task-cluster uncertainty; do not treat640rollouts as640independenttasks. Evidence: [entry012](../research-log/experiments/012-benchmark-v1.3-decision.md). Draft only; no article publication.
