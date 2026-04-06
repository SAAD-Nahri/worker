# Phase 2 Validation Plan

## Purpose

This document defines how Phase 2 should be validated as it is implemented.

The goal is to make sure the Content Engine becomes trustworthy through repeated checks, not through one final manual glance.

## Core Rule

Validation should happen slice by slice.

Do not wait until the end of Phase 2 to discover that:

1. the draft shape is unstable,
2. templates were encoded incorrectly,
3. quality gates are too weak,
4. AI was made mandatory by accident.

## Validation Layers

### 1. Spec Conformance Checks

Confirm that implementation matches:

1. [DRAFT_RECORD_SPEC.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_RECORD_SPEC.md)
2. [BLOG_TEMPLATE_CONTRACTS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/BLOG_TEMPLATE_CONTRACTS_V1.md)
3. [CONTENT_FORMATTING_PIPELINE_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CONTENT_FORMATTING_PIPELINE_V1.md)
4. [CONTENT_FIT_GATE_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CONTENT_FIT_GATE_V1.md)
5. [WEAK_FIT_ROUTING_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WEAK_FIT_ROUTING_POLICY_V1.md)
6. [CONTENT_QUALITY_GATES.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CONTENT_QUALITY_GATES.md)
7. [DERIVATIVE_RISK_POLICY.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DERIVATIVE_RISK_POLICY.md)
8. [AI_MICRO_SKILL_POLICY.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/AI_MICRO_SKILL_POLICY.md)
9. [DRAFT_REVIEW_WORKFLOW_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_REVIEW_WORKFLOW_V1.md)
10. [DRAFT_HEALTH_REPORTING_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_HEALTH_REPORTING_V1.md)

### 2. Unit Test Layer

Minimum unit-test targets:

1. draft record creation,
2. template selection,
3. required section validation,
4. deterministic formatting helpers,
5. category and tag assignment rules,
6. quality gate decisions,
7. derivative-risk classification helpers,
8. review state transitions and note validation,
9. routing recommendation behavior,
10. draft-health reporting and CLI behavior.

### 3. Fixture Test Layer

Create a small fixture set using representative Phase 1 source items.

Recommended fixture mix:

1. one straightforward explanatory food fact,
2. one question-led curiosity item,
3. one conservative benefit-style item,
4. one weak or thin item that should fail or flag,
5. one recipe-heavy or noisy item that should review-flag for content-fit reasons.

The fixture tests should confirm:

1. the correct template is selected,
2. the draft record is complete,
3. quality gate outcomes behave as expected,
4. subject and support anchors do not regress into low-signal fragments.

### 4. Operator Review Layer

At least a few generated drafts should be manually reviewed to confirm:

1. the drafts feel readable,
2. the titles are not misleading,
3. the transformation is meaningful,
4. the review flow is usable in practice,
5. the draft-health summary reflects the current operator state correctly.

## Validation By Build Slice

### Slice 1 Validation

Confirm:

1. draft IDs are stable,
2. lineage fields are preserved,
3. empty required fields are rejected cleanly.

### Slice 2 Validation

Confirm:

1. only the three v1 templates are available,
2. section order is encoded correctly,
3. invalid template references fail cleanly.

### Slice 3 Validation

Confirm:

1. source items can be converted into structured sections,
2. the deterministic path works without AI,
3. the formatter does not produce a single giant body blob.

### Slice 4 Validation

Confirm:

1. blocked drafts are blocked for clear reasons,
2. review flags are recorded clearly,
3. clean drafts pass without hidden issues.

Current status:

1. unit coverage now exists for blocked, review-flagged, and passing draft quality outcomes
2. the current repo baseline validates quality decisions through the standard unittest suite

### Slice 5 Validation

Confirm:

1. review outcomes can be recorded,
2. notes are preserved,
3. approved versus needs-edits behavior is unambiguous.

Current status:

1. unit coverage now exists for approval, needs-edits, blocked-approval rejection, and vague-note rejection behavior
2. the current repo baseline validates review persistence and state transitions through the standard unittest suite

### Slice 5B Validation

Confirm:

1. latest draft snapshots win over older snapshots,
2. latest review snapshots win over older reviews,
3. operator signals match the current quality and approval state,
4. JSON reporting is machine-readable and stable.

Current status:

1. unit coverage now exists for draft-health aggregation, pending-review signal mapping, and JSON CLI output
2. the current repo baseline validates latest-snapshot semantics through the standard unittest suite

### Slice 6 Validation

Confirm:

1. the system still works when AI is disabled,
2. AI outputs stay inside bounded fields,
3. AI assistance is logged.

Current status:

1. unit coverage now exists for heuristic no-AI operation, AI-provider logging, weak-output fallback, and CLI application of bounded micro-skills
2. the current repo baseline validates that draft enrichment remains optional and does not break deterministic draft creation
3. unit coverage now exists for content-affecting intro rewrites reopening review and for rejecting intro generation on templates without an intro slot

## Minimum Manual Acceptance Set

Before Phase 2 is considered stable enough for closeout work, manually inspect:

1. at least three passing drafts,
2. at least two flagged drafts,
3. at least one blocked draft,
4. one draft-health summary before review updates,
5. one draft-health summary after review updates,
6. one routing-visible draft-health summary that can be checked against the fixed gold-set policy.

This protects against a false sense of quality from tests alone.

Current status:

1. the first live acceptance batch is recorded in [PHASE_2_ACCEPTANCE_BATCH_1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_1.md)
2. that batch completed the before-review and after-review health-summary checks with `4` live drafts
3. the result confirmed that the operator workflow works, but semantic phrasing quality still needs stronger guardrails before approvals become common
4. the second live-style replay is recorded in [PHASE_2_ACCEPTANCE_BATCH_2.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_2.md)
5. that replay confirmed that semantic anchor and content-fit improvements are materially helping on the same live cases
6. the routing-visible operator replay is recorded in [PHASE_2_ACCEPTANCE_BATCH_3.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_3.md)
7. that replay confirmed that draft-health reporting now surfaces weak-fit routing directly in the normal operator path
8. the closeout-oriented gold-set expansion replay is recorded in [PHASE_2_ACCEPTANCE_BATCH_4.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_4.md)
9. that replay confirmed that the fixed pack now contains broader live weak-fit coverage
10. the live blocked-control replay is recorded in [PHASE_2_ACCEPTANCE_BATCH_5.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_5.md)
11. that replay confirmed that the fixed pack no longer depends on a synthetic blocked control alone
12. the bounded headline replay is recorded in [PHASE_2_ACCEPTANCE_BATCH_6.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_6.md)
13. that replay confirmed that weak heuristic headline patterns are now filtered or replaced before they reach the draft record
14. the closeout audit is recorded in [PHASE_2_ACCEPTANCE_BATCH_7.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_7.md)
15. that audit confirmed the fixed gold set is broad enough to freeze without forcing fake clean-fit cases
16. the template-contract hardening pass is recorded in [PHASE_2_ACCEPTANCE_BATCH_8.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_8.md)
17. that pass confirmed the strongest template rules are now executable instead of prose-only
18. deferred-but-legitimate follow-up work is now separated from closeout blockers in [PHASE_2_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_RESIDUAL_ITEMS.md)
19. the formal closeout is recorded in [PHASE_2_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_CLOSEOUT.md)
20. the post-closeout hardening pass is recorded in [PHASE_2_ACCEPTANCE_BATCH_9.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_9.md)
21. that pass confirmed that approved drafts are reopened after content-affecting intro edits and that template overrides now stay inside the source item's accepted template family

## Gold-Set Requirement

Before Phase 2 closeout, the repo should maintain a fixed gold set of real source items that includes:

1. clean fits,
2. weak-fit items,
3. recipe-heavy items,
4. noisy-source items,
5. named-person food stories.

Each gold-set case should define:

1. expected template family,
2. expected subject anchor,
3. forbidden low-signal terms,
4. expected quality outcome,
5. expected routing action.

The purpose of this requirement is to stop semantic regressions from hiding behind passing structural tests.

The current gold-set baseline lives in:

1. [PHASE_2_GOLD_SET_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_GOLD_SET_V1.md)
2. [PHASE_2_GOLD_SET_V1.json](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_GOLD_SET_V1.json)
3. [PHASE_2_ACCEPTANCE_BATCH_4.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_4.md)
4. [PHASE_2_ACCEPTANCE_BATCH_5.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_5.md)
5. [PHASE_2_ACCEPTANCE_BATCH_6.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_6.md)
6. [PHASE_2_ACCEPTANCE_BATCH_7.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_7.md)
7. [PHASE_2_ACCEPTANCE_BATCH_8.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_8.md)
8. [PHASE_2_ACCEPTANCE_BATCH_9.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_9.md)

## Failure Policy

If validation reveals that:

1. the formatter depends on AI to be usable,
2. templates are being bypassed,
3. derivative-risk behavior is inconsistent,
4. the review workflow is ambiguous,

then Phase 2 should be treated as still unstable even if some tests pass.

## Definition Of Done

This plan is satisfied when:

1. Phase 2 has a concrete validation strategy,
2. tests and manual checks are both expected,
3. the Content Engine can be judged professionally before handoff.
