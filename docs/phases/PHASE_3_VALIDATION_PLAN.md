# Phase 3 Validation Plan

## Purpose

This document defines how the first Social Packaging and Distribution layer should be validated.

The goal is to avoid a fragile Phase 3 where:

1. WordPress payloads look correct only by accident,
2. Facebook packages drift away from the approved draft,
3. queue states become confusing,
4. mapping records are incomplete from the start.

## Core Rule

Phase 3 validation must prove both correctness and operator trust.

That means:

1. the records are right,
2. the rendered output is right,
3. the workflow state is readable,
4. the operator can recover from failure without guesswork.

## Validation Layers

### 1. Spec Conformance Checks

Confirm that implementation matches:

1. [WORDPRESS_PUBLISHING_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_PUBLISHING_CONTRACT_V1.md)
2. [WORDPRESS_REST_TRANSPORT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_REST_TRANSPORT_V1.md)
3. [WORDPRESS_TRANSPORT_VALIDATION_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_TRANSPORT_VALIDATION_V1.md)
4. [FACEBOOK_PACKAGING_TEMPLATE_CONTRACTS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/FACEBOOK_PACKAGING_TEMPLATE_CONTRACTS_V1.md)
5. [FACEBOOK_GRAPH_TRANSPORT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/FACEBOOK_GRAPH_TRANSPORT_V1.md)
6. [FACEBOOK_TRANSPORT_VALIDATION_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/FACEBOOK_TRANSPORT_VALIDATION_V1.md)
7. [DISTRIBUTION_QUEUE_MODEL_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DISTRIBUTION_QUEUE_MODEL_V1.md)
8. [BLOG_FACEBOOK_MAPPING_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/BLOG_FACEBOOK_MAPPING_CONTRACT_V1.md)
9. [DISTRIBUTION_HEALTH_REPORTING_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DISTRIBUTION_HEALTH_REPORTING_V1.md)
10. [DISTRIBUTION_SCHEDULE_REPORTING_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DISTRIBUTION_SCHEDULE_REPORTING_V1.md)
11. [PUBLISH_HISTORY_SCHEMA.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_HISTORY_SCHEMA.md)
12. [APPROVAL_WORKFLOW.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/APPROVAL_WORKFLOW.md)

### 2. Unit Test Layer

Minimum unit-test targets:

1. WordPress payload creation
2. HTML rendering from approved draft sections
3. slug generation
4. category and tag mapping
5. Facebook package creation
6. queue-state transitions
7. mapping-record creation
8. failure-state preservation
9. WordPress REST request preview and transport execution rules
10. Facebook Graph request preview and transport execution rules
11. transport validation entry points
12. retry and backoff behavior for transient failures
13. distribution-health consistency and schedule-collision reporting
14. distribution schedule reporting

### 3. Fixture Test Layer

Use a small approved-draft fixture set from Phase 2.

Recommended mix:

1. one clean food-fact draft
2. one curiosity draft
3. one draft that is approved but still needs careful packaging tone
4. one draft that should remain blog-only when social packaging is intentionally skipped

The fixture tests should confirm:

1. WordPress payloads are complete,
2. Facebook packaging stays aligned with the draft,
3. queue states transition in the expected order,
4. mapping records preserve lineage.

### 4. Operator Review Layer

At minimum, manually inspect:

1. one WordPress-ready payload rendered from a clean food-fact draft
2. one Facebook package for that same draft
3. one queue transition set for blog plus Facebook
4. one WordPress transport dry-run preview for that same blog publish record
5. one Facebook transport dry-run preview for that same social package
6. one failure or hold case where the queue state remains visible
7. one distribution-health summary review that exposes either a schedule collision or a broken-chain consistency alert
8. one distribution-schedule summary review that distinguishes schedule-ready from collision-heavy chains

## Minimum Manual Acceptance Set

Before Phase 3 can approach closeout work, manually confirm:

1. at least two approved drafts can become WordPress-ready payloads
2. at least two approved drafts can produce Facebook packages
3. at least one item reaches a blog queue-ready state
4. at least one item reaches a social queue-ready state
5. at least one mapping record preserves the full draft-to-blog-to-social chain
6. at least one WordPress transport dry run can be reviewed without mutating runtime state
7. at least one Facebook transport dry run can be reviewed without mutating runtime state
8. at least one failed or skipped publish path remains visible in runtime state
9. at least one distribution-health report can expose operator-visible collision or consistency alerts
10. at least one schedule-planning report can distinguish schedule-ready from collision-heavy chains

## Failure Policy

If validation reveals that:

1. Facebook packaging is being derived from raw source content,
2. WordPress rendering drops structure or lineage,
3. queue states are ambiguous,
4. mapping records do not preserve selected outputs,
5. the operator cannot explain what happened after a failed publish step,

then Phase 3 should still be treated as unstable even if one integration appears to work.

## Current Status

Current status:

1. planning baseline created
2. the first local WordPress-preparation slice is implemented
3. the first local Facebook-packaging slice is implemented
4. the first local queue-and-mapping slice is implemented
5. the first local review-and-publish-update slice is implemented
6. the first local Facebook-publish update slice is implemented
7. the first local scheduling-policy slice is implemented
8. the first real WordPress transport slice is implemented with dry-run request preview, remote draft create/update support, and append-only failure recording
9. the first real Facebook Graph transport slice is implemented with dry-run request preview, publish and schedule support, and append-only success and failure recording
10. transport-validation entry points now exist for both WordPress and Facebook
11. shared retry/backoff now exists for transient WordPress and Facebook transport failures
12. focused validation now exists for WordPress payload rendering, WordPress REST request building, Facebook Graph request building, transport CLI dry-run and execute behavior, transport validation entry points, retry/backoff behavior, publish-record storage, Facebook package derivation, social-package storage, social review logging, local WordPress publish-state updates, local Facebook publish-state updates, scheduling policy enforcement, queue/mapping creation, schedule reporting, and runtime reset coverage
13. focused validation now also exists for distribution-health summary reporting, schedule-collision visibility, and broken-chain consistency alerts
14. the current implementation evidence is recorded in [PHASE_3_ACCEPTANCE_BATCH_1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_1.md), [PHASE_3_ACCEPTANCE_BATCH_2.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_2.md), [PHASE_3_ACCEPTANCE_BATCH_3.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_3.md), [PHASE_3_ACCEPTANCE_BATCH_4.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_4.md), [PHASE_3_ACCEPTANCE_BATCH_5.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_5.md), [PHASE_3_ACCEPTANCE_BATCH_6.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_6.md), [PHASE_3_ACCEPTANCE_BATCH_7.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_7.md), [PHASE_3_ACCEPTANCE_BATCH_8.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_8.md), and [PHASE_3_ACCEPTANCE_BATCH_9.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_9.md)
15. the full repo unittest baseline remains green at `189` tests passing

## Definition Of Done

This plan is satisfied when:

1. Phase 3 has a concrete validation strategy,
2. rendering, packaging, queue, and mapping are all covered,
3. transport validation, retry/backoff, and schedule visibility are covered,
4. the operator workflow is part of validation, not an afterthought.
