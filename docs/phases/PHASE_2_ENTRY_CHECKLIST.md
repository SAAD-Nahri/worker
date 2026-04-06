# Phase 2 Entry Checklist

## Purpose

This document controls the start of Phase 2: Content Engine.

It exists to prevent the common failure mode where a new phase starts with vague assumptions, blurred boundaries, or hidden dependency debt from the previous phase.

Reference:

1. [PHASE_GOVERNANCE.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_GOVERNANCE.md)

## Entry Rule

Do not begin Phase 2 implementation work until the checklist in this file is reviewed and explicitly satisfied.

Phase 2 should begin narrow and professional, not broad and speculative.

## Required Inputs From Phase 1

Phase 2 must begin with the following already in place:

1. a working source registry,
2. stable normalized source item records,
3. dedupe outcomes on source items,
4. source review decision recording,
5. article-body enrichment as an optional bounded input,
6. source health reporting,
7. runtime reset workflow,
8. explicit fallback handling for degraded and non-RSS sources.

Primary references:

1. [PHASE_1_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_1_CLOSEOUT.md)
2. [PHASE_1_SOURCE_ENGINE.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_1_SOURCE_ENGINE.md)
3. [SOURCE_ENGINE_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/SOURCE_ENGINE_RUNBOOK.md)
4. [WORKFLOW_STATE_MODEL.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORKFLOW_STATE_MODEL.md)
5. [TEMPLATE_LIBRARY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TEMPLATE_LIBRARY_V1.md)
6. [DRAFT_RECORD_SPEC.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_RECORD_SPEC.md)
7. [BLOG_TEMPLATE_CONTRACTS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/BLOG_TEMPLATE_CONTRACTS_V1.md)
8. [CONTENT_QUALITY_GATES.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CONTENT_QUALITY_GATES.md)
9. [DERIVATIVE_RISK_POLICY.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DERIVATIVE_RISK_POLICY.md)
10. [AI_MICRO_SKILL_POLICY.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/AI_MICRO_SKILL_POLICY.md)
11. [CATEGORY_AND_TAG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CATEGORY_AND_TAG_POLICY_V1.md)
12. [CONTENT_FORMATTING_PIPELINE_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CONTENT_FORMATTING_PIPELINE_V1.md)
13. [DRAFT_REVIEW_WORKFLOW_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_REVIEW_WORKFLOW_V1.md)
14. [DRAFT_HEALTH_REPORTING_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_HEALTH_REPORTING_V1.md)
15. [PHASE_2_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_EXECUTION_PLAN.md)
16. [PHASE_2_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_VALIDATION_PLAN.md)

## Entry Checklist

### 1. Source Engine contract check

- [ ] The latest Source Engine validation commands succeed.
- [ ] The latest source health summary shows no unexpected degraded core sources.
- [ ] The operator understands which runtime files are authoritative inputs versus generated state.

### 2. Phase boundary check

- [ ] Everyone working on Phase 2 agrees that Content Engine starts from normalized source items, not raw URLs.
- [ ] Everyone working on Phase 2 agrees that templates are mandatory.
- [ ] Everyone working on Phase 2 agrees that full AI article generation is out of scope.

### 3. Required design decisions check

- [ ] The first blog template contracts to implement are chosen.
- [ ] The first draft record shape is defined before broad formatting logic is written.
- [ ] The first quality checks are defined before AI enhancement is expanded.
- [ ] The derivative-risk expectations for v1 drafts are documented clearly enough to guide implementation.

### 4. Operational readiness check

- [ ] The repo navigation points to the correct current-phase documents.
- [ ] `TODO.md` is the execution checklist of record.
- [ ] Any Phase 2 work can be checked against the master plan and phase brief without guessing.

## Default Phase 2 Build Order

When Phase 2 begins, the recommended implementation order is:

1. define the draft record shape,
2. encode blog template contracts,
3. implement deterministic formatting from source item to draft structure,
4. implement draft quality checks,
5. implement operator-facing draft creation and draft-health reporting,
6. add tightly scoped AI micro-skills only where the deterministic structure already exists.

This order matters because the Content Engine is supposed to be a formatting machine, not a free-form generation layer.

## What Must Not Happen At Phase 2 Entry

Do not start Phase 2 by:

1. writing giant prompts first,
2. adding full-article generation,
3. building WordPress publishing,
4. building Facebook packaging,
5. building analytics dashboards,
6. widening the source system instead of using the current contract.

## First Questions Phase 2 Must Answer

The first Content Engine questions should be:

1. what exact draft schema will the system emit,
2. what sections are mandatory for each first-wave blog template,
3. what transformations are deterministic versus AI-assisted,
4. what quality checks block draft advancement,
5. what review metadata must accompany a draft.

## Final Entry Note

Phase 2 should start narrow.

If the work begins to feel like publishing, distribution, or analytics, that is a sign the team is skipping phase boundaries again.

## Entry Decision

Current decision:

1. `ready after the checklist is actively re-confirmed at Phase 2 start`
