# Phase 2: Content Engine

## Objective

Turn normalized source items into clean, structured blog drafts using templates and tightly scoped AI enhancement.

Phase 2 should only begin after [PHASE_2_ENTRY_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_ENTRY_CHECKLIST.md) is actively reviewed and satisfied.

## Why This Phase Matters

This phase is where the project becomes a formatting machine instead of a source collector. The goal is not creative writing. The goal is to convert source material into consistent, readable, monetizable blog output.

## Main Responsibilities

1. define blog template families,
2. define formatting rules,
3. define the AI micro-skill layer,
4. define quality checks,
5. define the review-ready draft flow.

## Current Planning Baseline

The current planning baseline for Phase 2 is now documented in:

1. [DRAFT_RECORD_SPEC.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_RECORD_SPEC.md)
2. [BLOG_TEMPLATE_CONTRACTS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/BLOG_TEMPLATE_CONTRACTS_V1.md)
3. [CONTENT_QUALITY_GATES.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CONTENT_QUALITY_GATES.md)
4. [DERIVATIVE_RISK_POLICY.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DERIVATIVE_RISK_POLICY.md)
5. [AI_MICRO_SKILL_POLICY.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/AI_MICRO_SKILL_POLICY.md)
6. [CATEGORY_AND_TAG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CATEGORY_AND_TAG_POLICY_V1.md)
7. [CONTENT_FORMATTING_PIPELINE_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CONTENT_FORMATTING_PIPELINE_V1.md)
8. [DRAFT_REVIEW_WORKFLOW_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_REVIEW_WORKFLOW_V1.md)
9. [DRAFT_HEALTH_REPORTING_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_HEALTH_REPORTING_V1.md)
10. [CONTENT_FIT_GATE_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CONTENT_FIT_GATE_V1.md)
11. [WEAK_FIT_ROUTING_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WEAK_FIT_ROUTING_POLICY_V1.md)
12. [PHASE_2_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_EXECUTION_PLAN.md)
13. [PHASE_2_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_VALIDATION_PLAN.md)
14. [PHASE_2_CLOSEOUT_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_CLOSEOUT_CHECKLIST.md)
15. [PHASE_2_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_CLOSEOUT.md)
16. [PHASE_2_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_RESIDUAL_ITEMS.md)
17. [CONTENT_ENGINE_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/CONTENT_ENGINE_RUNBOOK.md)

## Current Implementation Status

Phase 2 has now started with slices 1 through 7 implemented, plus operator-facing draft creation and routing-visible draft-health reporting in the current repo baseline.

The current code baseline already includes:

1. [src/content_engine/models.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/models.py)
2. [src/content_engine/drafts.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/drafts.py)
3. [src/content_engine/templates.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/templates.py)
4. [src/content_engine/formatting.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/formatting.py)
5. [src/content_engine/taxonomy.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/taxonomy.py)
6. [src/content_engine/micro_skills.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/micro_skills.py)
7. [src/content_engine/quality.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/quality.py)
8. [src/content_engine/review.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/review.py)
9. [src/content_engine/review_cli.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/review_cli.py)
10. [src/content_engine/health.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/health.py)
11. [src/content_engine/routing.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/routing.py)
12. [src/content_engine/formatting_cli.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/formatting_cli.py)
13. [src/content_engine/health_cli.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/health_cli.py)
14. [src/content_engine/storage.py](C:/Users/Administrator/OneDrive/Documents/co_ma/src/content_engine/storage.py)
15. [tests/unit/content_engine](C:/Users/Administrator/OneDrive/Documents/co_ma/tests/unit/content_engine)

What exists today:

1. structured draft-record models,
2. section skeleton generation,
3. blog template contracts with slot-level guidance encoded in application code,
4. template selection from source-item template suggestions,
5. draft identity creation,
6. append-only draft storage,
7. source-lineage preservation into the draft record,
8. deterministic formatting from eligible source item to structured draft,
9. explicit eligibility rejection for non-unique source items before draft formatting proceeds,
10. deterministic anchor extraction with noise filtering and recipe-aware candidate paragraph selection,
11. semantic-profile and content-fit signals carried into the draft quality path,
12. deterministic category and tag assignment using the controlled v1 taxonomy,
13. draft quality evaluation with explicit `pass`, `review_flag`, or `blocked` outcomes,
14. slot-level template enforcement for section ranges, bullet-count expectations, and early-answer timing where the accepted contract encodes those rules,
15. derivative-risk notes recorded as part of the draft result,
16. structured review recording with `approved`, `needs_edits`, and `rejected` outcomes,
17. append-only draft review storage for operator traceability,
18. bounded micro-skill enrichment for headline variants, intro tightening, and excerpt refinement,
19. template-family-safe override validation so explicit template selection cannot bypass the source item's accepted template family,
20. content-affecting micro-skill edits now re-run quality and reopen review instead of leaving stale approved snapshots behind,
21. intro micro-skill normalization now respects template slot guidance and rejects templates with no intro slot,
22. operator-facing draft creation from a known `source_item_id`,
23. operator-facing draft-health reporting across latest draft and review snapshots,
24. visible routing recommendations and reasons in the operator draft-health report,
25. unit coverage for draft creation, template selection, formatting, taxonomy, quality, review, micro-skills, routing, health reporting, and storage behavior.

## First Live Acceptance Result

The first live acceptance batch is recorded in [PHASE_2_ACCEPTANCE_BATCH_1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_1.md).

That batch matters because it tested the current Content Engine against real runtime source items instead of fixtures alone.

Observed result:

1. `4` drafts were created from live `source_item_id` values,
2. pre-review health showed `3` drafts as `ready_for_review` and `1` as `review_flag_pending`,
3. post-review health showed `3` drafts as `needs_revision` and `1` as `rejected`,
4. no draft was approved for handoff,
5. the main weakness was semantic phrasing quality rather than missing structure.

This is an important professional signal:

1. the operator loop is working,
2. the current deterministic quality gates are not yet sufficient to protect against weak topic-term framing,
3. the next quality work should focus on semantic coherence before broader automation.

## Strategic Adjustment Since Batch 1

The next Phase 2 quality slice has now been implemented and replayed against the same live source set.

That work is documented in:

1. [CONTENT_FIT_GATE_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CONTENT_FIT_GATE_V1.md)
2. [PHASE_2_ACCEPTANCE_BATCH_2.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_2.md)
3. [PHASE_2_ACCEPTANCE_BATCH_3.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_3.md)
4. [PHASE_2_ACCEPTANCE_BATCH_4.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_4.md)
5. [PHASE_2_ACCEPTANCE_BATCH_5.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_5.md)
6. [PHASE_2_ACCEPTANCE_BATCH_6.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_6.md)
7. [PHASE_2_ACCEPTANCE_BATCH_7.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_7.md)
8. [PHASE_2_ACCEPTANCE_BATCH_8.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_8.md)
9. [PHASE_2_ACCEPTANCE_BATCH_9.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_9.md)
10. [PHASE_2_GOLD_SET_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_GOLD_SET_V1.md)
11. [WEAK_FIT_ROUTING_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WEAK_FIT_ROUTING_POLICY_V1.md)

What changed:

1. anchor extraction now filters more boilerplate and procedural noise,
2. topic-term selection now relies more on title and cleaned body support,
3. semantic-quality signals now surface recipe-heavy and noisy source context,
4. live replay results show stronger intros for the Costco and Jacques Pépin items and safer review-flag behavior for Tsoureki,
5. closeout-oriented replay work has widened the fixed gold set with additional live weak-fit cases and improved title handling for hyphenated food names,
6. bounded headline variants now use title-shape-aware heuristics and filter obviously weak wrapper patterns before they are recorded,
7. template enforcement now checks encoded slot-level section ranges, bullet counts, and the food-fact early-answer rule instead of treating those expectations as prose only,
8. post-closeout hardening now ensures content-affecting intro rewrites re-open review and template overrides cannot cross template families.

This work changed the direction of the remaining closeout work:

1. the final closeout-oriented task was deciding whether the fixed gold-set acceptance pack already had enough clean-fit breadth,
2. weak-fit source families now have explicit reroute or rejection rules,
3. headline refinement remains secondary to the deterministic content-fit layer.

That closeout-oriented path is now materially underway:

1. the fixed gold-set baseline has been created,
2. the first weak-fit routing policy is now documented,
3. replay support now exists for the current baseline cases,
4. routing recommendations are now visible in the normal operator health summary,
5. the closeout checklist now exists so the remaining Phase 2 work is judged against explicit gates instead of vague momentum,
6. the fixed pack now also includes a live blocked control and an explicit non-unique-source eligibility rule,
7. the heuristic headline gap has been tightened enough that headline variants can be treated as bounded review aids instead of a closeout blocker by themselves.

The repo now also separates deferred follow-up work from real closeout blockers in [PHASE_2_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_RESIDUAL_ITEMS.md), and the formal closeout is recorded in [PHASE_2_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_CLOSEOUT.md).

## Required Outputs

1. blog template contracts,
2. formatting engine requirements,
3. approved micro-skill list,
4. quality-check requirements,
5. draft data structure,
6. review-state definition,
7. operator-readable draft health and handoff signals.

## Key Decisions For Later Revisit

1. whether approved drafts with non-pass quality states should remain visible as a separate operator signal in later phases,
2. what must be manually approved before a draft can move toward publishing.

The other previously open design items are now explicitly deferred in [PHASE_2_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_RESIDUAL_ITEMS.md) so they do not keep Phase 2 artificially open.

## Things This Phase Must Not Do

1. switch to full AI article writing,
2. treat templates as optional,
3. optimize for novelty over consistency,
4. start building channel distribution logic,
5. add data-driven winner logic before publishing history exists.

## Risks

1. weak template definitions,
2. vague AI boundaries,
3. output that is too close to source phrasing,
4. unreadable or inconsistent draft formatting,
5. quality checks that are too weak or too broad,
6. topic-term extraction that produces structurally valid but semantically awkward copy.

## Definition Of Done

Phase 2 is done when:

1. source items can be transformed into predictable blog drafts,
2. templates clearly define structure and executable slot-level expectations,
3. quality outcomes are recorded deterministically,
4. AI is used only for controlled enhancements,
5. drafts can be reviewed without ambiguity,
6. the operator can summarize current draft state without reading raw runtime files,
7. routing recommendations are visible enough for batch triage and closeout review.

## Handoff To Phase 3

Phase 3 should inherit approved blog output as its core input. Social packaging must be derived from the structured blog draft, not directly from raw source material.

Reference:

1. [PHASE_3_ENTRY_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_ENTRY_CHECKLIST.md)
