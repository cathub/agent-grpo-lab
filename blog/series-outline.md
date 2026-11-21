# Agent GRPO Lab: proposed chronological blog series

This is an outline, not a claim that training occurred. Link evidence from research-log; distinguish VERIFIED results from reconstructed chronology.

1. **A tiny Qwen model succeeds80%of the time.** Introduce synthetic tools, strict JSON,8/10training tasks; contrast original mock12/20. Explain narrow scope.
2. **A harder task collapses to zero.** OriginalL2/L30/3each; first-action failures prevent measuring later reasoning. Native versus custom action protocol.
3. **Few-shot prompting changes the picture.** Verbal tool-first and descriptions fail; one tool-action example opens a loop but repeats calls; complete transition example later reaches60/64oncampaign only.
4. **Why GRPO needs informative reward groups.** Original group-metric code; theoretical within-group contrast versus aggregate rate; empirical0/48L2and0/160finalization. No training yet.
5. **The37/64and31/64experiments.** Exact no-history input, scoring-only restored lookup, matched-seed reproduction, seed variability and false generalization claims to avoid.
6. **One formatting instruction changes success to83.59%.** Paired68->107/128,44fixes/5regressions, strictinteger type caveat. Prompt engineering, not trained reasoning.
7. **A larger benchmark exposes evaluation problems.** Frozen40instances,640rollouts,16successes; disjoint scenarios do not prevent metric/winner shortcut. Advertised versus executable tool mismatch; conservative failureaudit.
8. **What must be fixed before GRPO.** Newversioncontract, independentlybalancedlabels,freshholdout,validation-onlypromptselection and immutable provenance. Finish with testable plans, not nonexistenttrainingimprovements.
