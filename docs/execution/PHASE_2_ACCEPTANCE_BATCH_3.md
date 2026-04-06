# Phase 2 Acceptance Batch 3

## Purpose

This acceptance note records the first operator-facing replay of Phase 2 draft health after weak-fit routing recommendations became visible in the standard reporting path.

The point of this batch is not to create new drafts. It is to confirm that the operator can now see:

1. current draft approval and quality state,
2. current routing recommendation per draft,
3. current routing reason counts across the batch,
4. whether the runtime health view is aligned with the weak-fit policy and gold-set baseline.

## Commands Run

```powershell
python src\cli\summarize_draft_health.py
python src\cli\summarize_draft_health.py --json
python src\cli\replay_phase2_gold_set.py
```

## Runtime Draft-Health Result

Current runtime health summary after the reporting update:

1. `4` total drafts
2. `3` drafts in `needs_edits`
3. `1` rejected draft
4. `3` drafts with routing action `proceed`
5. `1` draft with routing action `review_only`
6. `0` runtime drafts currently in `hold_for_reroute`
7. `0` runtime drafts currently in `reject_for_v1`

Routing-visible summary confirms that:

1. the three cleaner items remain routine proceed candidates even though they still need human edits,
2. the weaker Costa Rican soup case is now clearly visible as `review_only`,
3. derivative-risk routing reasons are surfaced without needing to inspect the raw draft file.

## Gold-Set Replay Result

The fixed gold-set replay still passes after the reporting change.

This matters because the routing-visible operator report should not drift away from the deterministic routing baseline already locked in the gold set.

Observed result:

1. clean-fit cases continue to route to `proceed`,
2. weak-fit and recipe-heavy controls continue to route to `hold_for_reroute`,
3. the blocked thin control continues to route to `reject_for_v1`,
4. the replay remains the guardrail for future routing or semantic-quality refactors.

## Operational Conclusion

This batch closes one of the remaining professional gaps in Phase 2.

Routing recommendation is no longer an internal helper only. It is now visible in the standard operator report and can be used during:

1. batch triage,
2. manual review prioritization,
3. closeout readiness checks,
4. future Phase 3 handoff filtering.

## Remaining Phase 2 Gaps After Batch 3

1. expand the gold set with more live blocked or clearly weak-fit cases,
2. improve bounded headline suggestion quality,
3. decide whether routing should later become a stronger pre-draft gate instead of only a visible recommendation layer.
