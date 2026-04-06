# Phase 2 Execution Plan

## Purpose

This document turns Phase 2 from a set of specs into a practical execution plan.

The goal is to keep implementation narrow, sequenced, and verifiable. This is especially important because Phase 2 is where the project could easily drift into free-form article generation or overbuilt editorial tooling.

## Execution Principle

Build the smallest working Content Engine slice that proves the draft-production contract.

Do not try to build:

1. publishing,
2. Facebook packaging,
3. analytics,
4. broad UI work,
5. advanced AI orchestration.

## Phase 2 Objective

Turn valid Phase 1 source items into structured blog draft records that can be reviewed without ambiguity.

## Required Inputs

Phase 2 execution should build directly on:

1. [PHASE_1_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_1_CLOSEOUT.md)
2. [DRAFT_RECORD_SPEC.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_RECORD_SPEC.md)
3. [BLOG_TEMPLATE_CONTRACTS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/BLOG_TEMPLATE_CONTRACTS_V1.md)
4. [CONTENT_FORMATTING_PIPELINE_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CONTENT_FORMATTING_PIPELINE_V1.md)
5. [CONTENT_FIT_GATE_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CONTENT_FIT_GATE_V1.md)
6. [WEAK_FIT_ROUTING_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WEAK_FIT_ROUTING_POLICY_V1.md)
7. [CONTENT_QUALITY_GATES.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CONTENT_QUALITY_GATES.md)
8. [DERIVATIVE_RISK_POLICY.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DERIVATIVE_RISK_POLICY.md)
9. [AI_MICRO_SKILL_POLICY.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/AI_MICRO_SKILL_POLICY.md)
10. [DRAFT_REVIEW_WORKFLOW_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_REVIEW_WORKFLOW_V1.md)
11. [DRAFT_HEALTH_REPORTING_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_HEALTH_REPORTING_V1.md)

## Recommended Build Slices

### Slice 1: Draft Record Foundations

Objective:

Define the code-level draft model and persistence shape.

Deliverables:

1. draft record model,
2. draft identity generation,
3. draft storage shape,
4. lineage preservation from source item to draft.

Acceptance signal:

1. a source item can be converted into an empty or partially filled valid draft record skeleton.

Current status:

1. completed in the current repo baseline

### Slice 2: Template Contracts In Code

Objective:

Encode the three v1 blog templates as application-level contracts.

Deliverables:

1. template registry or constants,
2. required sections by template,
3. length guidance metadata,
4. prohibited-pattern metadata.

Acceptance signal:

1. the application can select and validate one of the three v1 templates without guessing.

Current status:

1. completed in the current repo baseline

### Slice 3: Deterministic Formatter

Objective:

Build the non-AI formatting path from source item to section-filled draft.

Deliverables:

1. eligibility checks,
2. template selection,
3. section planning,
4. deterministic section fill,
5. excerpt placeholder or generation path.

Acceptance signal:

1. a valid source item can become a structurally complete first-pass draft with no AI dependency.

Current status:

1. implemented in the current repo baseline
2. deterministic output is now quality-evaluated instead of left in a placeholder state
3. deterministic output now includes controlled category and tag assignment
4. deterministic output now includes anchor filtering and semantic-profile generation for content-fit signals
5. still incomplete until closeout-quality validation is stronger

### Slice 4: Quality Gate Layer

Objective:

Evaluate the produced draft and assign pass, review-flag, or blocked.

Deliverables:

1. template completeness checks,
2. length checks,
3. readability checks,
4. derivative-risk evaluation hooks,
5. title and claim safety checks,
6. quality flag recording.

Acceptance signal:

1. every generated draft receives a visible quality decision and quality flags when needed.

Current status:

1. implemented in the current repo baseline
2. quality evaluation currently covers lineage, template completeness, thinness, readability, title integrity, claim safety, category/tag sanity, derivative risk, semantic anchor noise, and weak-fit source-context signals

### Slice 5: Review Workflow Support

Objective:

Make draft review explicit and traceable.

Deliverables:

1. approval state handling,
2. review outcome recording,
3. review note storage,
4. clear path for `approved`, `needs_edits`, and `rejected`.

Acceptance signal:

1. a reviewer can inspect a draft and record a durable decision without ambiguity.

Current status:

1. implemented in the current repo baseline
2. review recording now enforces explicit outcomes, durable notes, and draft state transitions

### Slice 5B: Operator Draft Workflow

Objective:

Make the Phase 2 draft flow operable without custom scripts or raw log inspection.

Deliverables:

1. draft creation entry point from a known `source_item_id`,
2. draft-health reporting built from latest draft snapshots and latest review snapshots,
3. operator-facing signals for blocked, pending, revision, approved, and rejected draft states,
4. visible routing recommendations and reasons for `proceed`, `review_only`, `hold_for_reroute`, and `reject_for_v1`.

Acceptance signal:

1. the operator can create a draft, summarize current draft health, and see the current handoff state without opening JSONL files manually.

Current status:

1. implemented in the current repo baseline
2. the current slice includes `create_draft_from_source_item.py` plus `summarize_draft_health.py`
3. draft health is summarized from append-only runtime state using latest-snapshot semantics
4. the health summary now exposes routing recommendations directly in both text and JSON output

### Slice 6: Optional AI Micro-Skills

Objective:

Add bounded AI enhancements only after the deterministic formatter is stable.

Deliverables:

1. headline variant generation,
2. short intro generation,
3. excerpt generation,
4. limited section smoothing where justified,
5. AI assistance logging.

Acceptance signal:

1. AI improves bounded fields without becoming required for basic draft creation.

Current status:

1. initial baseline implemented in the current repo
2. the current slice supports bounded enrichment for headline variants, intro tightening, and excerpt refinement
3. a heuristic provider is available so the system still works when external AI is absent
4. headline variants now use title-shape-aware fallback patterns and discard obviously weak wrapper outputs before they are written back into the draft record
5. content-affecting intro rewrites now re-run quality and reopen the draft review state instead of leaving stale approvals in place
6. intro generation now follows template intro slot guidance and is rejected for templates that do not expose an intro slot
7. full section smoothing and taxonomy assist remain deferred until the bounded provider contract is clearer

### Slice 7: Gold-Set And Weak-Fit Routing Baseline

Objective:

Lock semantic-anchor quality and weak-fit handling into a repeatable acceptance layer.

Deliverables:

1. fixed gold-set case manifest,
2. replay command or harness,
3. deterministic routing recommendations for `proceed`, `review_only`, `hold_for_reroute`, and `reject_for_v1`,
4. documented routing rules for weak-fit source families.

Acceptance signal:

1. the gold-set replay passes,
2. weak-fit cases are surfaced consistently instead of being judged ad hoc.

Current status:

1. implemented as a first baseline in the current repo
2. the gold-set manifest and replay command now exist
3. routing recommendations now exist both as a deterministic helper layer and as visible operator-facing report output
4. the baseline has now been widened with additional live weak-fit cases
5. the baseline now also includes a captured live blocked duplicate-snapshot control
6. the remaining closeout gap is now mostly about final quality acceptability rather than missing blocked/weak-fit coverage

## Current Live Finding

The first live operator batch is recorded in [PHASE_2_ACCEPTANCE_BATCH_1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_1.md).

That batch confirmed:

1. the execution order works in practice,
2. review and draft-health reporting are doing their job,
3. the next execution priority should be semantic quality improvement rather than broader automation.

The follow-up replay in [PHASE_2_ACCEPTANCE_BATCH_2.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_2.md) confirmed:

1. deterministic anchor quality improved materially on the same live cases,
2. recipe-heavy and noisy sources are now surfaced more honestly,
3. the next execution priority is closeout-quality validation, not more feature spread.

The routing-visible health replay in [PHASE_2_ACCEPTANCE_BATCH_3.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_3.md) confirmed:

1. weak-fit routing is now visible in the normal operator reporting path,
2. live runtime state and the fixed gold set still agree on routing behavior,
3. the next execution priority is expanding closeout coverage rather than debating whether routing should stay hidden.

The closeout-oriented gold-set expansion replay in [PHASE_2_ACCEPTANCE_BATCH_4.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_4.md) confirmed:

1. additional live weak-fit cases now exist in the fixed pack,
2. hyphenated food-title handling is more stable,
3. the remaining closeout gap is now narrower and easier to state honestly.

The live blocked-control replay in [PHASE_2_ACCEPTANCE_BATCH_5.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_5.md) confirmed:

1. the fixed pack now includes a real blocked case instead of relying on synthetic-only blocked coverage,
2. non-unique source items are rejected more explicitly at eligibility time,
3. the next Phase 2 decision can stay focused on content-quality acceptability rather than missing validation shapes.

The bounded headline replay in [PHASE_2_ACCEPTANCE_BATCH_6.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_6.md) confirmed:

1. heuristic headline variants now respect common title shapes instead of wrapping everything in the same generic pattern,
2. weak provider output now falls back to safer deterministic variants instead of polluting the draft record,
3. headline heuristics are no longer the main closeout blocker for Phase 2.

The closeout audit in [PHASE_2_ACCEPTANCE_BATCH_7.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_7.md) confirmed:

1. the remaining uncovered live candidates were better modeled as weak-fit families rather than forced clean-fit additions,
2. the fixed gold set is now broad enough to freeze for the accepted Phase 2 template scope,
3. the formal closeout can proceed without pretending the live source pool contains more trustworthy clean-fit diversity than it really does.

The template-contract hardening pass in [PHASE_2_ACCEPTANCE_BATCH_8.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_8.md) confirmed:

1. the accepted v1 template rules now include executable slot-level guidance instead of living only in prose,
2. deterministic baseline drafts still satisfy the stronger contract,
3. slot-level drift now appears as named review flags before later phases depend on the draft shape.

The post-closeout hardening pass in [PHASE_2_ACCEPTANCE_BATCH_9.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_9.md) confirmed:

1. template overrides can no longer cross template families,
2. content-affecting intro rewrites now invalidate prior approval and refresh quality state,
3. intro micro-skills are now constrained by the selected template instead of a single global range.

That remaining closeout work is now resolved and recorded in [PHASE_2_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_CLOSEOUT.md).

The items that are intentionally deferred rather than left ambiguous are now recorded in [PHASE_2_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_RESIDUAL_ITEMS.md).

## Validation Strategy

Phase 2 should not rely on ad hoc manual spot checks alone.

Minimum validation layers:

1. unit tests for template selection and draft model behavior,
2. unit tests for formatting helpers,
3. unit tests for quality gate decisions,
4. fixture-based tests using a few real-like source items,
5. unit tests for draft-health reporting and CLI entry points,
6. one manual operator review pass on generated drafts,
7. a fixed gold-set replay using known live failures and edge cases.

## Phase 2 Acceptance Criteria

Phase 2 should only be considered closeout-ready when all of the following are true:

1. a valid source item can produce a structured draft record,
2. one of the three v1 templates is always explicit,
3. source lineage survives draft generation,
4. a quality decision is recorded for every draft,
5. draft review outcomes are stored clearly,
6. AI remains optional and tightly scoped,
7. the operator can see which drafts are blocked, pending, revision-required, or ready for handoff,
8. semantic anchor and content-fit behavior is stable across the fixed gold set,
9. routing recommendations are visible enough to support batch triage and weak-fit handling,
10. the output is stable enough for Phase 3 to derive packaging from the approved blog draft.

## What Should Still Be Deferred

Keep the following out of Phase 2:

1. WordPress publishing logic,
2. Facebook packaging generation,
3. queue scheduling,
4. analytics dashboards,
5. winner detection,
6. agent-first workflows.

## Suggested Working Order

Use this order unless a clear dependency forces a change:

1. draft model and storage,
2. template contracts in code,
3. deterministic formatting,
4. quality gates,
5. review workflow support,
6. operator draft workflow,
7. optional AI micro-skills.

## Completion Note

If implementation pressure starts pushing Phase 2 toward publishing or social outputs, pause and realign. The professional version of this project preserves phase boundaries even when it is tempting to "just keep going."
