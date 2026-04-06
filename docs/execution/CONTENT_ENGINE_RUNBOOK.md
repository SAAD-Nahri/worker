# Content Engine Runbook

## Purpose

This runbook explains how to operate the current Phase 2 baseline without guessing.

It assumes Phase 1 intake has already produced valid source items and that the operator wants to:

1. create drafts,
2. enrich drafts only where useful,
3. review drafts cleanly,
4. monitor overall draft health.

## Core Rule

Phase 2 is still a controlled formatting system.

That means:

1. draft creation starts from a real source item,
2. the source item should be a `unique` Phase 1 result, not a duplicate snapshot,
3. deterministic formatting comes first,
4. micro-skills are optional,
5. human review remains mandatory,
6. draft health should be checked across the batch, not only draft by draft.

## Working Order

Use this order unless a specific debugging need forces a different path:

1. create draft records from shortlisted source items,
2. inspect draft health,
3. apply bounded micro-skills only where they help,
4. review the draft and record the outcome,
5. re-check draft health before handoff to Phase 3 planning.

## 1. Create A Draft

Create a structured draft record from the latest snapshot of a source item:

```powershell
python src\cli\create_draft_from_source_item.py --source-item-id <source_item_id>
```

Optional template override:

```powershell
python src\cli\create_draft_from_source_item.py --source-item-id <source_item_id> --template-id blog_food_fact_v1
```

Template-override rule:

1. explicit overrides are only valid when they stay inside the same template family as the source item's `template_suggestion`,
2. overrides are an operator control, not permission to force a weak-fit item through the wrong template family.

Expected result:

1. a new draft snapshot is appended to `draft_records.jsonl`,
2. the output prints the `draft_id`,
3. the draft already includes category, quality status, derivative-risk fields, and the first routing recommendation.

Important:

1. if the selected source item is non-unique, the Content Engine should reject it at eligibility time,
2. duplicate or near-duplicate snapshots are not valid Phase 2 drafting inputs in the v1 workflow.

## 2. Inspect Draft Health

Summarize the current draft set:

```powershell
python src\cli\summarize_draft_health.py
```

JSON output for scripting or deeper inspection:

```powershell
python src\cli\summarize_draft_health.py --json
```

Use this command to answer:

1. which drafts are blocked,
2. which drafts are ready for review,
3. which drafts still need edits,
4. which drafts are approved and ready for Phase 3 handoff,
5. which drafts should proceed normally,
6. which drafts should stay review-only,
7. which drafts should be held for reroute or rejected from the current v1 path.

## 3. Apply Bounded Micro-Skills

Use micro-skills only when they clearly improve a bounded field:

```powershell
python src\cli\apply_draft_micro_skills.py --draft-id <draft_id> --skill generate_headline_variants --skill generate_excerpt
```

Current local provider behavior:

1. heuristic fallback is available now,
2. external AI is not required,
3. micro-skills do not replace deterministic draft creation,
4. `generate_short_intro` is only valid for templates that include an `intro` slot,
5. intro rewrites now respect the selected template's intro slot range,
6. content-affecting micro-skill edits move the draft back to `pending_review` and `drafted` with refreshed quality fields.

## 4. Record Review Outcome

Review a draft and record the result:

```powershell
python src\cli\review_draft.py --draft-id <draft_id> --outcome needs_edits --note "derivative_risk_fix: tighten wording in direct answer"
```

Normal review outcomes:

1. `approved`
2. `needs_edits`
3. `rejected`

Review rules:

1. blocked drafts should not be approved,
2. vague notes are not valid,
3. review records are append-only.

## 5. Re-Check Draft Health

After review or enrichment work, re-run:

```powershell
python src\cli\summarize_draft_health.py
```

This confirms whether the batch is moving in the right direction.

It also confirms whether the routing mix is reasonable before the batch gets any closer to Phase 3.

If a draft was previously approved, this re-check matters even more after content-affecting micro-skill work because the approval is intentionally reopened.

## Recommended Operator Routine

For a small Phase 2 batch:

1. create drafts for `3` to `5` shortlisted source items,
2. run the health summary,
3. apply micro-skills only to drafts that clearly benefit,
4. review the cleanest drafts first,
5. leave blocked drafts visible instead of hiding them,
6. stop and fix repeated quality issues before generating a much larger batch.

## What To Watch Closely

Pay special attention to:

1. repeated derivative-risk flags,
2. too many drafts staying in `review_flag_pending`,
3. a rising number of blocked drafts,
4. drafts being approved while still carrying avoidable quality concerns,
5. too many drafts accumulating in `hold_for_reroute` or `review_only`,
6. micro-skills being used to rescue weak formatting instead of polishing good formatting.

## What To Avoid

Do not:

1. create drafts without preserving source lineage,
2. treat micro-skills as mandatory,
3. skip the health summary and review drafts blindly,
4. approve blocked drafts,
5. treat this runbook as a substitute for the specs.

## Related Docs

1. [PHASE_2_CONTENT_ENGINE.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_CONTENT_ENGINE.md)
2. [PHASE_2_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_EXECUTION_PLAN.md)
3. [PHASE_2_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_VALIDATION_PLAN.md)
4. [PHASE_2_CLOSEOUT_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_CLOSEOUT_CHECKLIST.md)
5. [DRAFT_REVIEW_WORKFLOW_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_REVIEW_WORKFLOW_V1.md)
6. [DRAFT_HEALTH_REPORTING_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_HEALTH_REPORTING_V1.md)
