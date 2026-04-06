# Phase 4 Residual Items

## Purpose

This document separates true Phase 4 closeout blockers from legitimate later follow-up work.

Its job is to stop the project from doing one of two bad things:

1. closing Phase 4 while hidden tracking gaps still exist,
2. holding Phase 4 open for later analytics or decision-layer work that does not belong in the tracking-foundation baseline.

## Core Rule

If an item is not required for Phase 5 to trust the tracking contract, operator reporting path, and lineage rules, it should not be treated as a hidden Phase 4 blocker.

It should be written down here with:

1. why it is deferred,
2. when it may be revisited,
3. what evidence should trigger that revisit.

## Phase 4 Core Baseline That Is Already Considered Complete

The following are already part of the accepted Phase 4 baseline:

1. normalized publish-chain snapshots derived on demand,
2. deterministic lineage joins from source item through Facebook publish state,
3. selected-value variant normalization,
4. ledger, exception, activity, and variant-usage reporting views,
5. deliberate tracking audit records for normalization runs,
6. execute-mode transport-validation audit records,
7. a locked persistence policy that keeps snapshots on demand for now.

These items should not be treated as "still open" just because they may evolve later.

## Explicitly Deferred From Phase 4 Closeout

### 1. Persisted Normalized Snapshot Artifact

Status:

1. deferred by explicit policy

Why it is deferred:

1. the current on-demand normalization baseline is deterministic and operator-usable,
2. a persisted artifact would create another runtime truth surface before there is proven need,
3. rebuild and invalidation rules would add complexity too early.

Earliest revisit point:

1. Phase 5 readiness or later

Revisit trigger:

1. Phase 5 needs frozen comparison cohorts, or on-demand normalization becomes materially painful for normal operator use

Reference:

1. [PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md)

### 2. External Performance Data Integration

Status:

1. deferred to later tracking and decision work

Why it is deferred:

1. Phase 4 is about preserving publish lineage and selected outputs first,
2. click, CTR, and revenue-source joins are not yet required to prove the tracking contract,
3. adding performance-data plumbing now would blur the boundary between tracking foundation and decision logic.

Earliest revisit point:

1. early Phase 5 planning

Revisit trigger:

1. the project is ready to define winner signals against real external performance inputs

### 3. Frozen Point-In-Time Snapshot Cohorts

Status:

1. deferred

Why it is deferred:

1. the current operator and validation path only needs latest-chain reconstruction,
2. frozen cohorts are a decision-layer need, not a tracking-foundation need,
3. the repo should not simulate warehouse behavior before repeated analytical comparisons exist.

Earliest revisit point:

1. Phase 5

Revisit trigger:

1. repeated comparison work needs stable point-in-time baselines that cannot rely on latest-snapshot views alone

### 4. Live Non-Empty Publish-History Volume As Acceptance Evidence

Status:

1. deferred as operational acceptance, not architecture

Why it is deferred:

1. the checked-in runtime state may legitimately be sparse or reset,
2. the repo already validates the tracking contract through deterministic tests and acceptance batches,
3. live publish volume is a real-operations maturity question, not a missing tracking contract.

Earliest revisit point:

1. before Phase 5 decisions begin influencing real operator prioritization

Revisit trigger:

1. enough real publish chains exist that decision logic can be checked against actual operator history rather than only tests and fixture-style evidence

## True Remaining Closeout Work

These items are not deferred. They still matter before Phase 4 should be passed:

1. write the formal closeout review,
2. confirm the Phase 5 entry checklist exists and matches the accepted Phase 4 contract,
3. confirm the phase docs and repo guidance reflect the locked on-demand snapshot decision.

## Closeout Interpretation Rule

If a future discussion reopens one of the deferred items above, that does not automatically mean Phase 4 was incomplete.

It means:

1. the baseline tracking contract was intentionally frozen,
2. later evidence has reached a revisit threshold,
3. the new work should be planned against Phase 5 or later context instead of being smuggled back into Phase 4 closeout language.
