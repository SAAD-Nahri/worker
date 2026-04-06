# Phase 3 Residual Items

## Purpose

This document separates true Phase 3 closeout blockers from legitimate later follow-up work.

Its job is to stop the project from doing one of two bad things:

1. closing Phase 3 while hidden publish/distribution gaps still exist,
2. holding Phase 3 open for optional work that belongs to later evidence or later phases.

## Core Rule

If an item is not required for Phase 4 to trust the publish chain and runtime lineage, it should not be treated as a hidden Phase 3 blocker.

It should be written down here with:

1. why it is deferred,
2. when it may be revisited,
3. what evidence should trigger that revisit.

## Phase 3 Core Baseline That Is Already Considered Complete

The following are already part of the accepted Phase 3 baseline:

1. deterministic WordPress payload creation,
2. deterministic Facebook package creation,
3. append-only blog publish, social package, Facebook publish, queue, and mapping records,
4. manual social package review,
5. local publish-state progression for WordPress and Facebook,
6. real WordPress REST draft transport,
7. real Facebook Graph Page-feed transport,
8. conservative scheduling policy rules,
9. distribution health reporting,
10. transport validation entry points,
11. transport retry/backoff support,
12. schedule planning reporting.

These items should not be treated as "still open" just because they may improve later.

## Explicitly Deferred From Phase 3 Closeout

### 1. Live External Credential Validation In The Real Operator Environment

Status:

1. deferred as an operational acceptance task

Why it is deferred:

1. the repo now provides validation commands for both transports,
2. the actual external accounts and secrets are operator-owned and cannot be proven in repo-only test runs,
3. this is an environment activation task, not a missing application contract.

Earliest revisit point:

1. immediately before live production use

Revisit trigger:

1. the operator is ready to validate real WordPress and Facebook credentials against owned environments

### 2. Comment CTA Auto-Posting

Status:

1. deferred by decision

Why it is deferred:

1. the first live Facebook transport intentionally focuses on the main Page feed post only,
2. comment CTA text is already preserved in the selected package and mapping records,
3. auto-comment posting adds another live mutation step that is not required for Phase 4 tracking to trust the chain.

Earliest revisit point:

1. after Phase 4 tracking exists

Revisit trigger:

1. operator evidence shows that manual comment handling is the dominant recurring pain point

### 3. Visual Scheduling Dashboard

Status:

1. deferred

Why it is deferred:

1. the operator now has schedule-planning and collision reporting in CLI form,
2. a visual dashboard would improve convenience, not the underlying Phase 3 contract,
3. a dashboard should be justified by real scheduling volume rather than assumed early.

Earliest revisit point:

1. after repeated live scheduling cycles

Revisit trigger:

1. the CLI schedule report becomes too slow or too hard to use for actual operator volume

### 4. Retry Policy Tuning From Live Evidence

Status:

1. deferred

Why it is deferred:

1. the repo now has a shared retry/backoff baseline,
2. exact tuning should be informed by real transport behavior, not guessed in advance,
3. over-tuning now would create fake precision.

Earliest revisit point:

1. after live transport validation and early production use

Revisit trigger:

1. repeated transport failures show the default retry envelope is either too weak or too aggressive

## True Remaining Closeout Work

These items are not deferred. They still matter before Phase 3 should be passed:

1. write the formal closeout review,
2. confirm the Phase 4 entry checklist exists and matches the accepted Phase 3 contract,
3. confirm the phase docs and repo guidance reflect the hardened Phase 3 baseline.

## Closeout Interpretation Rule

If a future discussion reopens one of the deferred items above, that does not automatically mean Phase 3 was incomplete.

It means:

1. the baseline contract was intentionally frozen,
2. later evidence has reached a revisit threshold,
3. a new change should be planned against the later-phase context instead of being smuggled back into old closeout language.
