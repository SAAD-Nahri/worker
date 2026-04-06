# Draft Health Reporting V1

## Purpose

This document defines the minimum operator-facing reporting contract for Phase 2 drafts.

The Content Engine should not be judged only one draft at a time. The operator needs a clean way to see:

1. which drafts are blocked,
2. which drafts are review-ready,
3. which drafts still need edits,
4. which drafts are approved and safe to hand off to Phase 3,
5. which drafts should proceed normally versus be kept review-only, held for reroute, or rejected from the v1 path.

## Core Rule

Draft health reporting should be built from append-only runtime state, not from hidden mutable state.

That means:

1. the latest draft snapshot per `draft_id` is the current draft state,
2. draft review history comes from the append-only review log,
3. the report is derived at runtime,
4. the report is not its own source of truth.

## Inputs

The draft health report should read from:

1. `draft_records.jsonl`
2. `draft_reviews.jsonl`

It should not require:

1. WordPress data,
2. Facebook data,
3. analytics data,
4. queue scheduling data.

## Required Row-Level Outputs

Each report row should expose enough information for an operator to act without opening multiple files first.

Minimum row fields:

1. `draft_id`
2. `source_item_id`
3. `source_id`
4. `source_domain`
5. `template_id`
6. `category`
7. `workflow_state`
8. `approval_state`
9. `quality_gate_status`
10. `derivative_risk_level`
11. `quality_flag_count`
12. `quality_flags`
13. `headline_variant_count`
14. `has_excerpt`
15. `ai_assistance_count`
16. `review_count`
17. `latest_review_outcome`
18. `latest_reviewed_at`
19. `latest_updated_at`
20. `operator_signal`
21. `routing_action`
22. `routing_reason_count`
23. `routing_reasons`

## Required Summary Outputs

The report should also provide quick summary counts so the operator can judge the whole Phase 2 state without reading every row.

Minimum summary fields:

1. `latest_snapshot_at`
2. `total_drafts`
3. `quality_gate_counts`
4. `approval_state_counts`
5. `operator_signal_counts`
6. `category_counts`
7. `ai_enriched_drafts`
8. `drafts_with_headline_variants`
9. `drafts_with_excerpt`
10. `top_quality_flags`
11. `routing_action_counts`
12. `top_routing_reasons`

## Operator Signals

The report should convert draft state into a small set of actionable signals.

### `blocked_quality`

Use when:

1. `quality_gate_status = blocked`

Meaning:

1. the draft is not ready for normal review,
2. formatting or safety fixes are required first.

### `needs_revision`

Use when:

1. `approval_state = needs_edits`, or
2. `workflow_state = needs_revision`

Meaning:

1. the draft is reviewable,
2. human review has already identified fixable issues,
3. the next action is editing, not approval.

### `review_flag_pending`

Use when:

1. `approval_state = pending_review`, and
2. `quality_gate_status = review_flag`

Meaning:

1. the draft can be reviewed,
2. the reviewer should expect flagged issues,
3. it is not clean enough to treat as routine.

### `ready_for_review`

Use when:

1. `approval_state = pending_review`, and
2. `quality_gate_status = pass`

Meaning:

1. the draft is structurally ready for human review,
2. the operator does not need to fix obvious quality failures first.

### `approved_with_review_flags`

Use when:

1. `approval_state = approved`, and
2. `quality_gate_status != pass`

Meaning:

1. the draft has been approved,
2. but the quality record should still be inspected carefully before Phase 3 depends on it.

### `approved_ready_for_phase_3`

Use when:

1. `approval_state = approved`, and
2. `quality_gate_status = pass`

Meaning:

1. the draft is the cleanest Phase 2 handoff state,
2. Phase 3 can safely derive packaging from it.

### `rejected`

Use when:

1. `approval_state = rejected`

Meaning:

1. the draft should not continue in the normal flow.

### `monitor`

Use only when:

1. the draft state combination does not fit the normal workflow,
2. the operator should inspect the record directly.

This should be uncommon.

## Routing Signals

The draft health report should also surface the current weak-fit routing recommendation.

Routing is not the same thing as approval state.

A draft may:

1. be structurally reviewable but still need reroute,
2. pass the quality gate but still be a weak fit for the v1 content path,
3. be rejected for the current path even though it still exists in append-only runtime history.

Minimum routing actions:

### `proceed`

Meaning:

1. the draft fits the current Phase 2 path closely enough to continue normally.

### `review_only`

Meaning:

1. the draft can stay in the review loop,
2. the operator should inspect the flagged concerns before treating it as a routine case.

### `hold_for_reroute`

Meaning:

1. the draft should not continue as a normal v1 content item right now,
2. the operator should either reroute it to a different content treatment later or leave it out of the current batch.

### `reject_for_v1`

Meaning:

1. the draft should not continue in the current v1 path,
2. the operator should treat it as a stop signal, not a normal review case.

## Reporting Constraints

Draft health reporting exists to support Phase 2 control, not to smuggle in later-phase behavior.

It must not:

1. decide publish timing,
2. decide Facebook packaging,
3. decide winner status,
4. act like an analytics dashboard,
5. replace human review,
6. mutate draft state by itself.

## Recommended Operator Use

The report should be used:

1. after a batch of drafts is created,
2. after micro-skills are applied,
3. after a review session,
4. before claiming that Phase 2 is closeout-ready,
5. before moving any approved draft toward a Phase 3 handoff list.

If a content-affecting micro-skill rewrites the intro or later rewrites another article field, the next report run should surface that draft as pending review again instead of leaving it in an approved handoff state.

## Definition Of Done

This spec is satisfied when:

1. operators can see current draft state from runtime records,
2. the latest draft snapshot is surfaced cleanly,
3. approval and quality state are visible together,
4. routing recommendations are visible alongside approval and quality state,
5. the report highlights what needs attention next,
6. Phase 2 can be managed as a system instead of a pile of isolated draft files.
