# Corrections and limitations

- L1 “80%” is8/10train tasks, not20/20 or a held-out capability estimate. Original mock60% is a different agent/dataset scope.
- No original Qwen system prompt exists at initial task-design commit; initial L1/episode messages are reconstructed from later adapter source. Saved later condition inputs provide stronger prompt evidence.
- Tool-call-only example:1/3L2tool execution,0terminal successes. Complete transition example:60/64campaign successes. Do not merge these findings.
-10/16partial platform actions were valid nonterminal progress, not terminal successes or failures. Later fully observed platform evaluation0/16is a different state.
- Campaign37/64and31/64are two seed sets on one fixed task. Combined68/128does not measure128tasks or held-out generalization.
- No-history means no prior tool messages visible to model. Lookup history was restored privately for scoring; messages contained retrieved plain-text data, not an extra final-answer hint.
- Numeric rule107/128is prompt engineering, not GRPO. Strict integer129versus float129.0 remains a contract ambiguity.
-IGFimplementation predates Qwen in6fea4d4; exact introduction of the acronym and original rationale are not timestamped. Group-relative advantage formulas are theoretical diagnostics; no trainer exists.
- V1capability defects (ROAS/campaignschema mismatch, metric/winner correlation) must not be projected backward onto original L2/L3 February tools. Original environment supports ROAS and optional campaign correctly.
-401format errors are not401correct semantic answers. Confirmed50format-only among those,63acrossallfailures;79/640oraclelowerbound does not alter recorded16/640reward.
- Allv1multistep episodes stop on first action; no conclusion about later observation persistence follows. Separate earlier diagnostic logs did verify five histories preserved.
-139at128retokenized text lengths are truncation candidates; original capability logs lack finish_reason. No exact stop reason should be invented.
- Earliest Git commit already contains all levels. Two Git snapshots cannot establish every intermediate implementation change; later runner files were uncommitted. Snapshots/hashes preserve their current evidence, not a fabricated commit history.
- Most run timestamps, original shell transcript, exact model cache revision at each run, dependency lockfiles and host metrics are missing. Do not infer these from current file timestamps.
- No training gains, after-training metrics or Benchmarkv2results exist. The future blog must retain this boundary.

## Addendum: v1.1 contract-only experiment

The later v1.1 configuration removes the advertised ROAS/campaign mismatch, but does not alter the original v1 evidence or fix its metric/winner shortcut. Success rises 16 -> 72/640; multistep remains zero first lookup/completion. These are prompt-intervention gains, not trained-model gains. Exact historical checkpoint identity remains unverified despite four exact original raw smoke matches.

## Addendum: v1.2 prompt alignment

Aggregate success 72→88/640 is not a universal improvement: all 88 v1.2 successes are selection, with extraction/comparison regressions and zero multi-step progress. JSON/schema errors decline 385→283 but unnecessary calls increase 61→231. Only selection has mixed training groups. Explicit instructions are not equivalent to model compliance; causal attribution to individual wording choices remains unverified. No historical scores changed.

## Addendum: v1.3 decision rule

V1.3 has one real multi-step lookup/observation, unlike v1/v1.1/v1.2; its continuation fails, so prior zero-progression observations remain historically correct. Fewer gratuitous calls are not final-answer success: extraction is still zero. Exact pooled binomial intervals are nominal under IID assumptions; task-bootstrap and per-instance variability are separate. Action Bias remains a mechanistic hypothesis. No training or public push occurred.
