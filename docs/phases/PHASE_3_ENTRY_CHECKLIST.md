# Phase 3 Entry Checklist

## Purpose

This document controls the start of Phase 3: Social Packaging and Distribution.

It exists to prevent a common failure mode in this project:

1. jumping into WordPress and Facebook plumbing before the Content Engine contract is genuinely stable,
2. forcing Phase 3 to compensate for unclear draft quality or hidden Phase 2 gaps.

Reference:

1. [PHASE_GOVERNANCE.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_GOVERNANCE.md)

## Entry Rule

Do not begin Phase 3 implementation work until the checklist in this file is actively reviewed and satisfied.

Phase 3 should begin from approved blog drafts, not from source items and not from unfinished Content Engine debates.

## Required Inputs From Phase 2

Phase 3 must begin with the following already in place:

1. stable structured draft records,
2. explicit template identity on drafts,
3. visible draft quality outcomes,
4. append-only draft review history,
5. operator-facing draft-health reporting,
6. a fixed gold-set baseline for semantic-fit and routing behavior,
7. a documented Phase 2 residual-items list so later work does not redefine old scope silently.

Primary references:

1. [PHASE_2_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_CLOSEOUT.md)
2. [PHASE_2_CONTENT_ENGINE.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_CONTENT_ENGINE.md)
3. [PHASE_2_CLOSEOUT_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_CLOSEOUT_CHECKLIST.md)
4. [PHASE_2_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_RESIDUAL_ITEMS.md)
5. [PHASE_2_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_VALIDATION_PLAN.md)
6. [CONTENT_ENGINE_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/CONTENT_ENGINE_RUNBOOK.md)
7. [DRAFT_RECORD_SPEC.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_RECORD_SPEC.md)
8. [APPROVAL_WORKFLOW.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/APPROVAL_WORKFLOW.md)
9. [PUBLISH_HISTORY_SCHEMA.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_HISTORY_SCHEMA.md)
10. [WORDPRESS_PUBLISHING_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_PUBLISHING_CONTRACT_V1.md)
11. [WORDPRESS_REST_TRANSPORT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_REST_TRANSPORT_V1.md)
12. [FACEBOOK_PACKAGING_TEMPLATE_CONTRACTS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/FACEBOOK_PACKAGING_TEMPLATE_CONTRACTS_V1.md)
13. [DISTRIBUTION_QUEUE_MODEL_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DISTRIBUTION_QUEUE_MODEL_V1.md)
14. [BLOG_FACEBOOK_MAPPING_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/BLOG_FACEBOOK_MAPPING_CONTRACT_V1.md)
15. [PHASE_3_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_EXECUTION_PLAN.md)
16. [PHASE_3_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_VALIDATION_PLAN.md)

## Entry Checklist

### 1. Upstream contract check

- [x] Phase 2 closeout has been reviewed.
- [x] The accepted Phase 2 contract is stable enough that Phase 3 does not need to redefine draft structure.
- [x] The authoritative Phase 3 upstream input is known: approved draft records, not raw source items.

### 2. Phase boundary check

- [x] Everyone working on Phase 3 agrees that WordPress and Facebook outputs derive from the approved blog draft.
- [x] Everyone working on Phase 3 agrees that Phase 3 does not reopen full-article generation or template design debates.
- [x] Out-of-scope expansion such as Facebook Groups, paid boosts, and analytics dashboards is not mixed into the initial plan.

### 3. Design readiness check

- [x] The first WordPress publishing contract is defined.
- [x] The first Facebook packaging template families are defined.
- [x] The queue and approval state model for blog plus social output is defined before automation expands.

### 4. Operational readiness check

- [x] The relevant Phase 3 docs are current.
- [x] `TODO.md` reflects the active execution work for publishing and packaging.
- [x] The first Phase 3 validation path is understood before implementation starts.

## Default Phase 3 Build Order

When Phase 3 begins, the recommended implementation order is:

1. define the WordPress publishing contract,
2. define Facebook hook, caption, and comment CTA template families,
3. define queue and mapping records,
4. implement approved-draft to blog-post publishing flow,
5. derive Facebook-ready assets from the approved blog draft,
6. add scheduling only after the review path is stable.

## What Must Not Happen At Phase 3 Start

Do not start Phase 3 by:

1. publishing directly from raw source items,
2. bypassing draft approval because the packaging layer feels urgent,
3. adding Facebook Groups or paid boosts,
4. building analytics dashboards before publish records exist,
5. treating social packaging as a later optional polish step.

## First Questions Phase 3 Must Answer

The first Social Packaging and Distribution questions should be:

1. what exact WordPress publish fields are required first,
2. what exact Facebook package structure is required first,
3. how blog and Facebook outputs will be linked in app state,
4. what remains manual versus scheduled,
5. what operator approval events must be recorded before anything is published.

## Entry Decision

Current decision:

1. `ready for Phase 3 implementation planning and first code slices`
