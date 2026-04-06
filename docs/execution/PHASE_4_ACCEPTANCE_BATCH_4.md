# Phase 4 Acceptance Batch 4

## Purpose

Record the Phase 4 decision for normalized publish-chain snapshot persistence.

This batch exists to close the last narrow architecture question that remained after the first tracking baseline, reporting views, and audit layer were already in place.

## Decision Accepted

The repo will keep normalized publish-chain snapshots on demand for the current Phase 4 baseline.

Phase 4 will not add a persisted snapshot artifact yet.

## Why This Was Accepted

The current baseline already has:

1. append-only runtime records as the true source of truth,
2. deterministic lineage joins,
3. operator-readable tracking reports,
4. explicit tracking audit records for deliberate normalization runs.

Adding persisted normalized snapshots now would create more complexity than value:

1. invalidation and staleness rules would need to be invented,
2. reset and archive workflows would gain another runtime artifact,
3. future developers could start trusting the derived file more than the raw records,
4. the current operator path does not yet need frozen snapshot cohorts.

## Documents Updated

The accepted decision is now documented in:

1. [PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md)
2. [PUBLISH_HISTORY_NORMALIZATION_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_HISTORY_NORMALIZATION_V1.md)
3. [PUBLISH_CHAIN_SNAPSHOT_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_CONTRACT_V1.md)
4. [TRACKING_LOG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_LOG_POLICY_V1.md)
5. [PHASE_4_TRACKING_FOUNDATION.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_TRACKING_FOUNDATION.md)
6. [PHASE_4_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_EXECUTION_PLAN.md)
7. [PHASE_4_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_VALIDATION_PLAN.md)
8. [OPEN_QUESTIONS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/OPEN_QUESTIONS.md)
9. [TODO.md](C:/Users/Administrator/OneDrive/Documents/co_ma/TODO.md)

## Revisit Trigger

This decision should only be revisited later if:

1. on-demand normalization becomes materially slow for normal operator use,
2. Phase 5 needs frozen comparison cohorts,
3. external performance data requires stable point-in-time snapshot sets,
4. normalization becomes expensive enough that repeated rebuilds are no longer the simpler path.

## Result

Phase 4 no longer has an open architecture question about normalized snapshot persistence.

The current path stays:

1. raw append-only records are authoritative,
2. normalized publish-chain views are derived on demand,
3. persistence remains a later optimization, not a current dependency.
