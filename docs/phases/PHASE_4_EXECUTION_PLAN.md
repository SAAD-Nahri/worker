# Phase 4 Execution Plan

## Purpose

This document turns Phase 4 from a generic "tracking" idea into a sequenced implementation plan.

The goal is to build the thinnest useful tracking foundation on top of the accepted Phase 3 publish chain.

## Execution Principle

Start by normalizing what already exists.

Do not start with:

1. dashboards,
2. click attribution,
3. winner scoring,
4. BI-style denormalization,
5. metrics the repo cannot yet observe.

## Phase 4 Objective

Create a normalized, reportable publish-history layer that preserves source-to-blog-to-Facebook lineage and selected variant values without redefining Phase 3.

## Required Inputs

Phase 4 execution should build directly on:

1. [PHASE_3_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_CLOSEOUT.md)
2. [PHASE_3_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_RESIDUAL_ITEMS.md)
3. [PHASE_4_ENTRY_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_ENTRY_CHECKLIST.md)
4. [PUBLISH_HISTORY_SCHEMA.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_HISTORY_SCHEMA.md)
5. [PUBLISH_CHAIN_SNAPSHOT_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_CONTRACT_V1.md)
6. [PUBLISH_HISTORY_NORMALIZATION_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_HISTORY_NORMALIZATION_V1.md)
7. [TRACKING_LINEAGE_JOIN_RULES_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_LINEAGE_JOIN_RULES_V1.md)
8. [VARIANT_RECORDING_RULES_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/VARIANT_RECORDING_RULES_V1.md)
9. [TRACKING_LOG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_LOG_POLICY_V1.md)
10. [TRACKING_REPORTING_VIEWS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_REPORTING_VIEWS_V1.md)
11. [TRACKING_AUDIT_RECORDS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_AUDIT_RECORDS_V1.md)
12. [PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md)
13. [BLOG_FACEBOOK_MAPPING_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/BLOG_FACEBOOK_MAPPING_CONTRACT_V1.md)
14. [DISTRIBUTION_HEALTH_REPORTING_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DISTRIBUTION_HEALTH_REPORTING_V1.md)

## Recommended Build Slices

### Slice 1: Publish History Normalization Contract

Objective:

Freeze the normalized row shape before implementation starts.

Deliverables:

1. normalized publish-history row contract
2. canonical chain key decision
3. upstream input file list
4. field-level inclusion and exclusion rules

Acceptance signal:

1. implementation can begin without guessing what belongs in the tracking row.

Current status:

1. implemented in code as the first on-demand publish-chain snapshot baseline
2. locked to remain on demand until the persistence triggers in [PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md) are actually met

### Slice 2: Lineage Join Layer

Objective:

Build deterministic joins from append-only runtime records into stable publish chains.

Deliverables:

1. latest-snapshot loading rules
2. source-to-draft join
3. draft-to-blog join
4. blog-to-social and social-to-Facebook joins
5. queue and mapping attachment rules

Acceptance signal:

1. one source item can be traced deterministically through the latest known publish chain.

Current status:

1. implemented in code as the first deterministic lineage join layer

### Slice 3: Variant Normalization

Objective:

Preserve the selected title, hook, caption, and comment CTA values in a consistent tracking form.

Deliverables:

1. selected variant slot rules
2. text-first normalization for current runtime records
3. template and variant-label preservation
4. explicit handling for missing strong variant IDs

Acceptance signal:

1. later comparison work can identify what text and template choices were actually used.

Current status:

1. implemented in code as the first selected-value normalization baseline

### Slice 4: Reporting Views

Objective:

Make the normalized tracking layer readable to the operator.

Deliverables:

1. publish-chain ledger
2. publish exception view
3. variant usage summary
4. source and template activity summary

Acceptance signal:

1. the operator can inspect what was published and what is broken without reading raw JSONL files.

Current status:

1. implemented in code as the first operator-facing ledger, exception, activity, and variant views

### Slice 5: Logging And Audit Layer

Objective:

Add only the logs that Phase 4 actually needs for trust and debugging.

Deliverables:

1. normalization-run audit log
2. optional transport-validation audit log
3. explicit non-goals for noisy logging

Acceptance signal:

1. tracking work is auditable without creating a second noisy event firehose.

Current status:

1. implemented in code as the first normalization-run and transport-validation audit baseline

## Acceptance Evidence

Current implementation evidence is recorded in:

1. [PHASE_4_ACCEPTANCE_BATCH_1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_ACCEPTANCE_BATCH_1.md)
2. [PHASE_4_ACCEPTANCE_BATCH_2.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_ACCEPTANCE_BATCH_2.md)
3. [PHASE_4_ACCEPTANCE_BATCH_3.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_ACCEPTANCE_BATCH_3.md)
4. [PHASE_4_ACCEPTANCE_BATCH_4.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_ACCEPTANCE_BATCH_4.md)
5. [PHASE_4_ACCEPTANCE_BATCH_5.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_ACCEPTANCE_BATCH_5.md)

## Phase 4 Acceptance Criteria

Phase 4 should only be considered implementation-stable when all of the following are true:

1. one normalized publish-history row can represent the current latest chain for a `blog_publish_id`,
2. source, draft, blog publish, social package, Facebook publish, queue, and mapping records can be joined without guesswork,
3. selected variant values are preserved in a stable normalized form,
4. the operator can read at least one publish-history ledger and one exception view,
5. Phase 5 does not need to redefine the tracking lineage contract,
6. Phase 4 does not quietly introduce a persisted snapshot runtime artifact without a separately justified rebuild policy.

## What Should Still Be Deferred

Keep the following out of the first Phase 4 implementation pass:

1. click metrics,
2. attribution models,
3. dashboards,
4. winner scoring,
5. paid promotion logic,
6. any OpenClaw or agent-centered reasoning layer.

Also keep out:

1. persisted normalized snapshot storage before real operator pain or Phase 5 cohort requirements justify it.

## Completion Note

If Phase 4 starts drifting into analytics product work, pause and realign.

The job of this phase is:

1. normalize the publish history,
2. preserve lineage and selected outputs,
3. expose simple trustworthy reporting views,
4. prepare Phase 5 without pretending performance data already exists.
