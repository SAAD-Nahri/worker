# Phase 4 Validation Plan

## Purpose

This document defines how the Tracking Foundation should be validated.

The goal is to avoid a Phase 4 that looks structurally correct on paper but cannot actually reconstruct what the system published.

## Core Rule

Phase 4 validation must prove lineage trust.

That means:

1. the normalized rows are correct,
2. partial and failed chains stay visible,
3. selected variant values survive normalization,
4. reporting views are grounded in the underlying records.

## Validation Layers

### 1. Spec Conformance Checks

Confirm that implementation matches:

1. [PUBLISH_HISTORY_SCHEMA.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_HISTORY_SCHEMA.md)
2. [PUBLISH_CHAIN_SNAPSHOT_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_CONTRACT_V1.md)
3. [PUBLISH_HISTORY_NORMALIZATION_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_HISTORY_NORMALIZATION_V1.md)
4. [TRACKING_LINEAGE_JOIN_RULES_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_LINEAGE_JOIN_RULES_V1.md)
5. [VARIANT_RECORDING_RULES_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/VARIANT_RECORDING_RULES_V1.md)
6. [TRACKING_LOG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_LOG_POLICY_V1.md)
7. [TRACKING_REPORTING_VIEWS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_REPORTING_VIEWS_V1.md)
8. [TRACKING_AUDIT_RECORDS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_AUDIT_RECORDS_V1.md)
9. [PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md)
10. [BLOG_FACEBOOK_MAPPING_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/BLOG_FACEBOOK_MAPPING_CONTRACT_V1.md)

### 2. Unit Test Layer

Minimum unit-test targets:

1. latest-snapshot selection across append-only records
2. source-to-draft normalization
3. draft-to-blog normalization
4. blog-to-social and social-to-Facebook joins
5. queue and mapping attachment
6. partial-chain preservation
7. failed-chain preservation
8. variant normalization for blog title, hook, caption, and comment CTA
9. publish-history ledger rendering
10. exception-view filtering
11. normalization-run audit recording
12. tracking-audit summary rendering
13. confirmation that reporting remains correct with on-demand normalization and does not assume a persisted snapshot file
14. one cross-phase smoke test that proves a clean source item can travel from formatting through publish linkage into tracking and audit

### 3. Fixture Test Layer

Use a small runtime fixture set that includes:

1. one clean blog-only chain
2. one clean blog-plus-Facebook published chain
3. one failed WordPress or failed Facebook chain
4. one partial chain with packaging but no final Facebook publish

The fixture tests should confirm:

1. normalized rows preserve IDs across the full chain,
2. selected variant values are preserved,
3. failures and partial states remain visible,
4. reporting views do not hide incomplete chains.

### 4. Operator Review Layer

At minimum, manually inspect:

1. one normalized publish-history row from a clean chain
2. one normalized row from a failed or partial chain
3. one publish-chain ledger output
4. one exception-view output
5. one variant-usage summary output
6. one tracking-audit summary output
7. confirmation that the operator path does not require a persisted snapshot artifact to answer current Phase 4 questions

## Minimum Manual Acceptance Set

Before Phase 4 can approach closeout work, manually confirm:

1. at least two real chains can be normalized from runtime records
2. at least one published blog-plus-Facebook chain is visible end to end
3. at least one blog-only or failed chain is still visible
4. selected blog title, hook, caption, and comment CTA values survive into the normalized layer
5. the exception view highlights incomplete or failed chains without opening raw JSONL files
6. the current Phase 4 reports stay usable without a stored normalized snapshot file

## Failure Policy

If validation reveals that:

1. joins require title or URL guesswork,
2. failed chains disappear from reports,
3. selected social values are lost,
4. publish-history rows drift away from the append-only records,
5. Phase 5 would still need to redefine the lineage model,

then Phase 4 should still be treated as unstable.

## Current Status

Current status:

1. authoritative upstream Phase 3 runtime records already exist
2. the first normalized publish-chain snapshot baseline is implemented on demand in code
3. the first operator-facing ledger, exception, activity, and variant views are implemented
4. the first audit record baseline for normalization runs and execute-mode transport validation is implemented
5. focused Phase 4 tests exist for chain history, reporting, audit recording, and the tracking CLIs
6. a focused cross-phase integration smoke test now proves one clean chain can move from source item through distribution linkage into tracking and audit
7. the current policy is to keep normalized publish-chain snapshots on demand unless later trigger conditions justify persistence
8. validation should keep expanding from this baseline rather than treating Phase 4 as planning-only

## Definition Of Done

This plan is satisfied when:

1. Phase 4 has a concrete validation strategy,
2. lineage joins, normalized rows, variants, and reporting views are all covered,
3. operator trust is part of validation rather than an afterthought.
