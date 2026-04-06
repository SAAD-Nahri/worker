# Source Review Decision Spec

## Purpose

This document defines how source-review outcomes should be recorded in Phase 1.

The goal is to keep source management operationally real. A source decision should not live only in memory, chat, or a Markdown note if it materially affects intake behavior.

## Why This Exists

Phase 1 is not complete when the system can only fetch sources. It also needs a disciplined way to capture whether a source should remain active, be downgraded, be paused, or be retired.

Without recorded review decisions, source quality management becomes fragile and inconsistent.

## Core Rule

In Phase 1, source-review outcomes must be stored as decision records.

They may optionally update the registry, but the decision itself should still be preserved as its own audit record.

## Required Decision Inputs

Each source-review decision should be based on at least:

1. `source_id`
2. current source status
3. reviewed item count
4. strong candidate count
5. weak or repetitive item count
6. fetch failure count when relevant

Optional operator notes may also be stored.

## Required Decision Outputs

Each decision record should include at minimum:

1. `decision_id`
2. `source_id`
3. `source_name`
4. `reviewed_at`
5. `current_status`
6. `recommended_status`
7. `final_status`
8. `reviewed_items`
9. `strong_candidates`
10. `weak_or_repetitive_items`
11. `fetch_failures`
12. `recommendation_reason`
13. `reviewer_notes`
14. whether the decision was applied back to the registry

## Phase 1 Recommendation Rules

The decision logic should remain practical and deterministic:

1. downgrade after a meaningful review window with zero strong candidates,
2. pause when the source is mostly weak, repetitive, or failing repeatedly,
3. allow selective promotion when a watchlist or downgraded source starts producing strong candidates,
4. keep the source unchanged when the review signal is not strong enough to justify movement.

## Registry Update Rules

When a decision is applied back to the registry:

1. `status` should be updated,
2. `active` should reflect whether the new status allows intake,
3. `updated_at` should be refreshed,
4. the registry should preserve the last review timestamp,
5. the registry should preserve the latest status reason,
6. retirement reason should be captured when a source is retired.

## Phase 1 Operating Choice

For Phase 1, decision recording is required.

Registry updates should remain operator-applied, not automatic by default.

That keeps the workflow professional without letting incomplete heuristics silently change the live source set.

## What This Spec Does Not Require Yet

This spec does not require:

1. automatic promotion or pausing,
2. a dedicated UI,
3. a scoring model,
4. a multi-reviewer workflow,
5. advanced analytics-driven source governance.

## Definition Of Done

This spec is satisfied when:

1. review decisions are stored as first-class records,
2. recommendations are deterministic and auditable,
3. registry updates are possible without being mandatory,
4. source governance is no longer dependent on informal notes alone.
