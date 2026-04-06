# Phase 2 Acceptance Batch 5

## Purpose

This acceptance note records the first live blocked control added to the fixed Phase 2 gold set.

The purpose of this batch was to close a specific professional gap:

1. the fixed pack already had weak-fit live cases,
2. the fixed pack already had a synthetic blocked control,
3. but the pack still needed at least one real live blocked case.

## Strategic Change

This batch also introduced a small but important content-engine rule clarification:

1. Phase 2 should only draft `unique` source items,
2. non-unique source items should be rejected explicitly at eligibility time,
3. duplicate snapshots should not drift into draft formatting and only fail later for incidental reasons like thin text.

That rule now aligns the Content Engine more cleanly with the dedupe policy.

## Live Blocked Control Added

The new blocked case is:

1. `haunted_restaurant_duplicate_snapshot_reject`

Source title:

1. `This NYC Restaurant Is Supposedly Haunted By Over 20 Ghosts`

Why it matters:

1. it is a real feed-derived source item,
2. it represents a duplicate snapshot with `dedupe_status = exact_duplicate`,
3. article-body fetch is skipped for that snapshot,
4. the Content Engine now rejects it explicitly as a non-unique source item.

## Why This Is Better Than Synthetic-Only Coverage

The synthetic blocked control is still useful, but this live blocked control protects a more realistic failure path:

1. a source can be real,
2. the title can look draftable,
3. but the current snapshot is still not valid for Phase 2 because it is non-unique and should not re-enter drafting.

That is a real operational risk, not a toy edge case.

## Commands Run

```powershell
python -m unittest discover -s tests -v
python src\cli\replay_phase2_gold_set.py
python src\cli\replay_phase2_gold_set.py --json
```

## Result

The fixed gold set now passes with `12/12` cases.

This matters because the pack now includes:

1. clean fits,
2. review-only cases,
3. multiple live weak-fit hold cases,
4. one live blocked control,
5. one synthetic blocked thin-text control.

## What Changed In The Baseline

### 1. Live blocked coverage now exists

The pack no longer depends on the synthetic blocked control alone.

### 2. Eligibility is cleaner

The Content Engine now rejects non-unique items explicitly instead of relying on a secondary failure path to stop them.

### 3. Closeout evidence is stronger

Phase 2 now has both:

1. live weak-fit coverage,
2. live blocked coverage.

That makes the closeout argument more credible.

## Remaining Phase 2 Gap After Batch 5

This batch closes the biggest remaining gold-set coverage gap.

The main remaining closeout work is now narrower:

1. decide whether the current heuristic headline quality is acceptable for Phase 2 closeout,
2. finalize the closeout pack and handoff language once that decision is made.

## Conclusion

Batch 5 is a real foundation improvement.

It does not add new surface area. It makes the current surface more honest by proving that Phase 2 handles both live weak-fit and live blocked cases in a repeatable way.
