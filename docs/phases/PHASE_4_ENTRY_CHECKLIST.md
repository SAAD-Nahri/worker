# Phase 4 Entry Checklist

## Purpose

This document controls the start of Phase 4: Tracking Foundation.

Its job is to prevent two bad handoffs:

1. starting tracking work before the publish chain is stable enough to trust,
2. forcing Phase 4 to compensate for unclear Phase 3 lineage or hidden workflow gaps.

## Core Rule

Do not begin Phase 4 implementation work until the checklist in this file is actively reviewed and satisfied.

Phase 4 should begin from trusted publish and mapping records, not from guesses about what was probably published.

## Required Inputs

Phase 4 must begin with the following already in place:

1. [PHASE_3_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_CLOSEOUT.md)
2. [PHASE_3_CLOSEOUT_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_CLOSEOUT_CHECKLIST.md)
3. [PHASE_3_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_RESIDUAL_ITEMS.md)
4. [PUBLISH_HISTORY_SCHEMA.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_HISTORY_SCHEMA.md)
5. [PUBLISH_CHAIN_SNAPSHOT_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_CONTRACT_V1.md)
6. [PUBLISH_HISTORY_NORMALIZATION_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_HISTORY_NORMALIZATION_V1.md)
7. [TRACKING_LINEAGE_JOIN_RULES_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_LINEAGE_JOIN_RULES_V1.md)
8. [VARIANT_RECORDING_RULES_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/VARIANT_RECORDING_RULES_V1.md)
9. [TRACKING_LOG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_LOG_POLICY_V1.md)
10. [TRACKING_REPORTING_VIEWS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_REPORTING_VIEWS_V1.md)
11. [BLOG_FACEBOOK_MAPPING_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/BLOG_FACEBOOK_MAPPING_CONTRACT_V1.md)
12. [DISTRIBUTION_HEALTH_REPORTING_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DISTRIBUTION_HEALTH_REPORTING_V1.md)
13. [PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md)
14. [PHASE_4_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_EXECUTION_PLAN.md)
15. [PHASE_4_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_VALIDATION_PLAN.md)

## Checklist

### 1. Phase 3 Contract Stability

- [x] The accepted Phase 3 contract is stable enough that Phase 4 does not need to redefine publish, queue, or mapping records.
- [x] The authoritative Phase 4 upstream inputs are known: latest publish records, mapping records, queue records, and append-only review history.
- [x] The Phase 3 residual items are explicit and do not hide a missing tracking prerequisite.

### 2. Publish And Mapping Trust

- [x] Blog publish records preserve stable publish identifiers and URLs when available.
- [x] Facebook publish records preserve stable publish identifiers and status outcomes when available.
- [x] Blog-to-Facebook mapping records preserve selected blog and social output values.
- [x] Distribution health reporting can expose missing or inconsistent chain states before Phase 4 assumes the data is trustworthy.

### 3. Workflow Visibility

- [x] Queue state and mapping state remain readable without opening raw JSONL files by hand.
- [x] Schedule collisions and broken-chain inconsistencies are operator-visible.
- [x] Transport validation and dry-run workflows exist for WordPress and Facebook.

### 4. Documentation And Operator Baseline

- [x] The relevant Phase 3 docs are current.
- [x] The Distribution Engine runbook exists for the accepted operator path.
- [x] `README.md`, `TODO.md`, and `OPEN_QUESTIONS.md` reflect the real post-Phase-3 baseline.

## Default Phase 4 Build Order

When Phase 4 begins, the recommended implementation order is:

1. publish history normalization,
2. stable lineage joins,
3. operator reporting views,
4. variant recording rules,
5. audit and debug logs that matter.

## What Must Not Happen At Phase 4 Start

Do not start Phase 4 by:

1. inventing a new publish lineage model,
2. skipping over append-only records in favor of a fake summary-only store,
3. treating unresolved live production questions as proof that the tracking contract is unclear,
4. jumping into winner detection before the tracking foundation exists.

## Current Status

Current status:

1. Phase 3 closeout is formally recorded
2. the Phase 4 planning baseline now exists
3. the on-demand tracking baseline is implemented and operator-readable
4. the normalized publish-chain snapshot remains intentionally on demand for the current baseline
5. ready to keep extending Phase 4 against the accepted tracking contracts instead of reopening Phase 3
