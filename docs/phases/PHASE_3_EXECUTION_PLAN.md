# Phase 3 Execution Plan

## Purpose

This document turns Phase 3 from a broad distribution idea into a sequenced execution plan.

The goal is to build the thinnest reliable path from:

approved draft -> WordPress post -> Facebook package -> queue record

without mixing in later analytics or scaling concerns.

## Execution Principle

Start with contracts and operator safety.

Do not start with:

1. deep API automation,
2. paid-traffic thinking,
3. Facebook Groups,
4. analytics dashboards,
5. cross-channel expansion.

## Phase 3 Objective

Turn approved blog drafts into publishable WordPress records and Facebook-ready package records with visible queue and mapping state.

## Required Inputs

Phase 3 execution should build directly on:

1. [PHASE_2_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_CLOSEOUT.md)
2. [PHASE_3_ENTRY_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_ENTRY_CHECKLIST.md)
3. [WORDPRESS_PUBLISHING_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_PUBLISHING_CONTRACT_V1.md)
4. [WORDPRESS_REST_TRANSPORT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_REST_TRANSPORT_V1.md)
5. [FACEBOOK_PACKAGING_TEMPLATE_CONTRACTS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/FACEBOOK_PACKAGING_TEMPLATE_CONTRACTS_V1.md)
6. [FACEBOOK_GRAPH_TRANSPORT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/FACEBOOK_GRAPH_TRANSPORT_V1.md)
7. [DISTRIBUTION_QUEUE_MODEL_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DISTRIBUTION_QUEUE_MODEL_V1.md)
8. [BLOG_FACEBOOK_MAPPING_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/BLOG_FACEBOOK_MAPPING_CONTRACT_V1.md)
9. [DISTRIBUTION_HEALTH_REPORTING_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DISTRIBUTION_HEALTH_REPORTING_V1.md)
10. [WORDPRESS_TRANSPORT_VALIDATION_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_TRANSPORT_VALIDATION_V1.md)
11. [FACEBOOK_TRANSPORT_VALIDATION_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/FACEBOOK_TRANSPORT_VALIDATION_V1.md)
12. [DISTRIBUTION_SCHEDULE_REPORTING_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DISTRIBUTION_SCHEDULE_REPORTING_V1.md)
13. [PUBLISH_HISTORY_SCHEMA.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_HISTORY_SCHEMA.md)
14. [APPROVAL_WORKFLOW.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/APPROVAL_WORKFLOW.md)

## Recommended Build Slices

### Slice 1: Publishing And Packaging Contracts

Objective:

Freeze the data contracts before implementation starts.

Deliverables:

1. WordPress publish payload shape
2. Facebook package record shape
3. queue-item shape
4. blog-to-Facebook mapping shape

Acceptance signal:

1. implementation can begin without guessing what fields belong to each Phase 3 object.

Current status:

1. completed in the current planning baseline

### Slice 2: WordPress Rendering And Publish Preparation

Objective:

Render approved draft records into WordPress-ready payloads.

Deliverables:

1. WordPress payload model
2. deterministic HTML renderer from approved draft sections
3. slug preparation
4. category and tag mapping
5. append-only blog publish record storage

Acceptance signal:

1. an approved draft can become a WordPress-ready object even before the final transport adapter is chosen.

Current status:

1. first local baseline implemented in the current repo
2. approved drafts can now be rendered into WordPress-ready HTML
3. append-only local blog publish records now exist
4. a CLI entry point can prepare a local WordPress-ready publish record from an approved draft
5. remote WordPress transport remains deferred

### Slice 3: Facebook Packaging Derivation

Objective:

Generate Facebook-ready packages from the approved draft or blog publish record.

Deliverables:

1. package template registry
2. deterministic hook and caption derivation
3. comment CTA derivation
4. package record storage
5. package review support

Acceptance signal:

1. at least one approved draft can produce one reviewable Facebook package with explicit lineage.

Current status:

1. first local baseline implemented in the current repo
2. approved drafts can now produce one primary reviewable Facebook package
3. append-only local social package records now exist
4. package creation can optionally link to a prepared WordPress record while keeping blog URLs empty until the URL is confirmed
5. operator-facing local Facebook package preparation now exists through a CLI

### Slice 4: Queue And Mapping Layer

Objective:

Make the Phase 3 workflow operable and traceable.

Deliverables:

1. blog queue records
2. Facebook queue records
3. queue-state transitions
4. blog-to-Facebook mapping records
5. operator-facing queue summary support

Acceptance signal:

1. the operator can see where an item is stuck between approved draft, WordPress preparation, packaging, and publish readiness.

Current status:

1. first local baseline implemented in the current repo
2. initial blog queue records can now be created from local WordPress preparation records
3. initial Facebook queue records can now be created from local packaging state or explicit packaging-pending state
4. initial blog-to-Facebook mapping records can now preserve the selected blog and social outputs
5. manual social-package review and local WordPress publish-state updates can now refresh queue and mapping state
6. dedicated local Facebook publish records can now preserve `facebook_publish_id`, `facebook_post_id`, and Facebook-side publish results
7. local Facebook publish-state updates can now drive `scheduled_facebook`, `published_facebook`, `facebook_publish_failed`, `social_queued`, `social_published`, and `social_publish_failed`
8. live transport remains deferred

### Slice 5: First Transport Adapter

Objective:

Choose and implement the first real publish adapter.

Deliverables:

1. first WordPress publish transport
2. first Facebook publish or scheduling transport, if feasible in the same slice
3. visible success and failure recording

Acceptance signal:

1. at least one approved item can be pushed through the selected live integration path or safely created as a remote draft.

Current status:

1. first WordPress transport baseline implemented in the current repo
2. the first adapter is WordPress REST with application-password auth
3. the adapter is intentionally draft-sync only and dry-run safe by default
4. execute mode can now create or update a remote WordPress draft and append the resulting local publish snapshot
5. transport failures now append a visible failed publish snapshot instead of disappearing as operator guesswork
6. the first Facebook Graph transport slice is now implemented with the same dry-run-safe and append-only pattern

### Slice 6: Scheduling Baseline

Objective:

Add conservative scheduling behavior after the publish and packaging path is stable.

Deliverables:

1. schedule fields on queue items
2. schedule validation rules
3. manual approval checkpoints before public publish

Acceptance signal:

1. scheduling remains visible and reversible instead of becoming hidden automation.

Current status:

1. first local baseline implemented in the current repo
2. blog scheduling now preserves manual versus auto mode metadata
3. blog queue records can now surface `ready_for_blog_schedule` before a final scheduled timestamp is recorded
4. Facebook scheduling now requires the linked blog publish record to already be scheduled or published
5. Facebook scheduling can no longer precede the linked scheduled blog publish time

### Slice 7: Distribution Health And Operator Visibility

Objective:

Make the current publish chain readable enough that the operator can spot collisions, failures, and broken lineage before Phase 4 tracking begins.

Deliverables:

1. distribution health summary
2. per-chain operator rows
3. visible schedule-collision alerts
4. visible chain-consistency alerts
5. operator runbook coverage for the current publish loop

Acceptance signal:

1. the operator can explain the latest state of each blog-to-Facebook chain without reading raw JSONL files first.

Current status:

1. implemented in the current repo
2. the distribution health CLI can now summarize blog publish, social review, Facebook publish, queue, and mapping state together
3. the report now surfaces blog and Facebook schedule collisions
4. the report now surfaces broken-state issues such as missing workflow state, queue/mapping mismatches, missing published identifiers, and Facebook schedules that outrun the blog
5. the current operator flow is now documented in the Distribution Engine runbook

### Slice 8: Transport Validation, Resilience, And Schedule Planning

Objective:

Close the remaining operator-safety gaps around live transport readiness, transient failure handling, and schedule planning visibility.

Deliverables:

1. non-mutating WordPress transport validation
2. non-mutating Facebook transport validation
3. shared retry/backoff support for transport execution
4. operator-facing schedule planning report
5. repo entry points for validation and schedule reporting

Acceptance signal:

1. the operator can validate transport configs, survive transient failures more safely, and review schedule-ready versus collision-heavy chains without reading raw JSONL files directly.

Current status:

1. implemented in the current repo
2. both transport layers now have dry-run-safe validation entry points
3. transient WordPress and Facebook transport failures now share a bounded retry/backoff path
4. a dedicated schedule planning report now exists alongside the distribution health report
5. the remaining Phase 3 work is now closeout and residual-item separation rather than another major code slice

## Phase 3 Acceptance Criteria

Phase 3 should only be considered implementation-stable when all of the following are true:

1. an approved draft can be rendered into a WordPress-ready payload,
2. a Facebook package can be derived from that same approved draft or published blog post,
3. queue records preserve the current blog and Facebook state separately,
4. blog and Facebook outputs are linked through explicit mapping records,
5. public publishing still respects human approval.

The current acceptance evidence for the baseline is recorded in:

1. [PHASE_3_ACCEPTANCE_BATCH_1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_1.md)
2. [PHASE_3_ACCEPTANCE_BATCH_2.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_2.md)
3. [PHASE_3_ACCEPTANCE_BATCH_3.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_3.md)
4. [PHASE_3_ACCEPTANCE_BATCH_4.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_4.md)
5. [PHASE_3_ACCEPTANCE_BATCH_5.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_5.md)
6. [PHASE_3_ACCEPTANCE_BATCH_6.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_6.md)
7. [PHASE_3_ACCEPTANCE_BATCH_7.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_7.md)
8. [PHASE_3_ACCEPTANCE_BATCH_8.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_8.md)
9. [PHASE_3_ACCEPTANCE_BATCH_9.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_3_ACCEPTANCE_BATCH_9.md)

## What Should Still Be Deferred

Keep the following out of the first Phase 3 implementation pass:

1. Facebook Groups
2. paid boosts
3. analytics dashboards
4. winner detection
5. multi-channel publishing
6. deep WordPress theme or media customization

## Completion Note

If Phase 3 implementation starts drifting into platform sprawl, pause and realign.

The job of this phase is not "be everywhere." The job is:

1. publish approved blog content cleanly,
2. package Facebook Page content cleanly,
3. preserve queue and mapping state from day one.

The accepted closeout baseline for this plan is now recorded in:

1. [PHASE_3_CLOSEOUT_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_CLOSEOUT_CHECKLIST.md)
2. [PHASE_3_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_CLOSEOUT.md)
3. [PHASE_3_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_RESIDUAL_ITEMS.md)
