# Phase 2 Residual Items

## Purpose

This document separates true Phase 2 closeout blockers from legitimate later follow-up work.

Its job is to stop the project from doing one of two bad things:

1. closing Phase 2 while hidden gaps still exist,
2. holding Phase 2 open for work that belongs to later evidence and later phases.

## Core Rule

If an item is not required for Phase 3 to trust the Content Engine contract, it should not be treated as a hidden Phase 2 blocker.

It should be written down here with:

1. why it is deferred,
2. when it may be revisited,
3. what evidence should trigger that revisit.

## Phase 2 Core Baseline That Is Already Considered Complete

The following are already part of the accepted Phase 2 baseline:

1. draft record shape and append-only storage,
2. template contracts in code,
3. deterministic formatting from eligible source item to draft,
4. deterministic quality gates with `pass`, `review_flag`, and `blocked`,
5. derivative-risk evaluation and notes,
6. deterministic taxonomy assignment,
7. draft review workflow and append-only review logging,
8. operator draft creation and draft-health reporting,
9. weak-fit routing recommendations,
10. fixed gold-set replay support,
11. bounded headline, intro, and excerpt micro-skill support,
12. heuristic fallback behavior that keeps external AI optional.

These items should not be treated as "still open" just because they may improve later.

## Explicitly Deferred From Phase 2 Closeout

### 1. External AI Provider Contract

Status:

1. deferred

Why it is deferred:

1. Phase 2 only needs bounded enhancement support, not a production AI integration,
2. the heuristic provider already proves that draft creation and bounded enrichment work without making AI a dependency,
3. adding a provider contract now would add cost, configuration, and policy drift before Phase 3 depends on the output.

Earliest revisit point:

1. after Phase 3 baseline exists and the operator workflow is stable enough to justify an external dependency

Revisit trigger:

1. repeated operator evidence shows that bounded headline, intro, or excerpt improvement is still worth the added runtime cost

### 2. `smooth_section_copy`

Status:

1. deferred

Why it is deferred:

1. it increases body-level rewrite surface area,
2. it risks turning Phase 2 into a soft full-rewrite phase,
3. the current project priority is trustable structure and review visibility, not broader rewrite automation.

Earliest revisit point:

1. after Phase 2 closeout, with new acceptance evidence from approved drafts

Revisit trigger:

1. repeated review notes show that one section at a time is the dominant remaining fix pattern

### 3. AI-Assisted Category Or Tag Suggestion

Status:

1. deferred

Why it is deferred:

1. deterministic taxonomy is already working,
2. AI assistance here is optional convenience, not a contract requirement,
3. changing category logic too early would blur the current controlled taxonomy baseline.

Earliest revisit point:

1. after Phase 3, once real publishing and packaging workflows expose actual taxonomy pain points

Revisit trigger:

1. operators repeatedly override deterministic tags or categories in a pattern that can be measured

### 4. Routing As A Hard Pre-Draft Gate

Status:

1. deferred

Why it is deferred:

1. Phase 2 already surfaces routing clearly enough for operator triage,
2. turning routing into a hard pre-draft gate would change upstream behavior, not just visibility,
3. that decision should be informed by later workflow evidence, not just current formatting intuition.

Earliest revisit point:

1. after Phase 4 tracking exists and the system can compare draft effort against real downstream outcomes

Revisit trigger:

1. operator evidence shows that `hold_for_reroute` and `review_only` drafts are consuming effort without downstream value

### 5. Stronger Pre-Draft Content-Fit Gating

Status:

1. deferred

Why it is deferred:

1. the current semantic-profile and routing layer already exposes weak-fit cases,
2. making the gate stricter too early could hide useful evidence instead of improving it,
3. the better next step is to learn from more accepted and rejected draft outcomes first.

Earliest revisit point:

1. after more live approval history exists

Revisit trigger:

1. repeated weak-fit cases continue slipping through despite the current routing and review path

## True Remaining Closeout Work

These items are not deferred. They still matter before Phase 2 should be passed:

1. decide whether the fixed gold set needs one more clean-fit expansion before freeze,
2. once that decision is made, write the formal Phase 2 closeout review,
3. confirm the Phase 3 entry checklist stays aligned with the accepted Phase 2 contract.

## Closeout Interpretation Rule

If a future discussion reopens one of the deferred items above, that does not automatically mean Phase 2 was incomplete.

It means:

1. the baseline contract was intentionally frozen,
2. the later revisit trigger has been reached,
3. a new change should now be planned against the later-phase context instead of being smuggled back into old closure language.
