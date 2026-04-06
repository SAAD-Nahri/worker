# Phase 4: Tracking Foundation

## Objective

Create the minimum durable data layer needed to understand what was published and to support later analysis.

## Why This Phase Matters

The project cannot become a decision system until it can remember what happened. Phase 4 is where the business stops being only a content workflow and becomes a measurable operating system.

## Main Responsibilities

1. define publish history normalization,
2. define source-to-blog-to-Facebook lineage joins,
3. define variant recording rules,
4. define the minimum audit logs that matter,
5. define operator-readable tracking views.

## Current Planning Baseline

The current planning baseline for Phase 4 is now documented in:

1. [PUBLISH_HISTORY_SCHEMA.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_HISTORY_SCHEMA.md)
2. [PUBLISH_CHAIN_SNAPSHOT_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_CONTRACT_V1.md)
3. [PUBLISH_HISTORY_NORMALIZATION_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_HISTORY_NORMALIZATION_V1.md)
4. [TRACKING_LINEAGE_JOIN_RULES_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_LINEAGE_JOIN_RULES_V1.md)
5. [VARIANT_RECORDING_RULES_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/VARIANT_RECORDING_RULES_V1.md)
6. [TRACKING_LOG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_LOG_POLICY_V1.md)
7. [TRACKING_REPORTING_VIEWS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_REPORTING_VIEWS_V1.md)
8. [TRACKING_AUDIT_RECORDS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_AUDIT_RECORDS_V1.md)
9. [PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md)
10. [PHASE_4_ENTRY_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_ENTRY_CHECKLIST.md)
11. [PHASE_4_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_EXECUTION_PLAN.md)
12. [PHASE_4_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_VALIDATION_PLAN.md)

## Current Implementation Status

Phase 4 is no longer planning-only.

The current repo now includes:

1. a first `tracking_engine` baseline,
2. on-demand publish-chain snapshots anchored by `blog_publish_id`,
3. deterministic source-to-draft-to-blog-to-social-to-Facebook lineage joins,
4. an operator-readable publish-chain ledger,
5. dedicated Phase 4 exception, activity, and variant usage views,
6. append-only tracking audit records for deliberate normalization runs and execute-mode transport validation.

What remains intentionally unfinished:

1. persisted normalized snapshot artifacts,
2. external performance data such as clicks or CTR.

The current locked decision is:

1. keep normalized publish-chain snapshots on demand for the current Phase 4 baseline,
2. revisit persistence only when Phase 5 comparison work or operator pain clearly justifies it.

The accepted closeout and handoff baseline is now recorded in:

1. [PHASE_4_CLOSEOUT_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_CLOSEOUT_CHECKLIST.md)
2. [PHASE_4_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_RESIDUAL_ITEMS.md)
3. [PHASE_4_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_CLOSEOUT.md)
4. [PHASE_4_5_SYSTEM_ACTIVATION.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_5_SYSTEM_ACTIVATION.md)
5. [PHASE_5_ENTRY_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_5_ENTRY_CHECKLIST.md)

## Required Outputs

1. normalized publish-history model,
2. stable lineage join rules,
3. selected-variant recording rules,
4. logging categories that matter,
5. basic operator-readable tracking views.

## Key Decisions Now Locked

1. the normalized publish-history chain is anchored by `blog_publish_id`,
2. Phase 4 normalizes append-only runtime data instead of replacing it,
3. selected variant texts are first-class tracking values even when strong variant IDs are not yet available,
4. reporting stays CLI-first and JSON-capable instead of turning into dashboard work,
5. logging remains minimal and audit-focused rather than firehose-style.

## Things This Phase Must Not Do

1. overbuild dashboards,
2. force advanced attribution too early,
3. introduce predictive scoring without enough history,
4. prioritize analytics complexity over operational clarity,
5. redefine the accepted Phase 3 publish, queue, or mapping contracts.

## Risks

1. storing too little to support later decisions,
2. storing too much noisy data,
3. weak mapping between entities,
4. tracking fields that do not match real workflow states,
5. letting Phase 4 drift into analytics product work before the tracking layer is stable.

## Definition Of Done

Phase 4 is done when:

1. every published or attempted publish chain can be traced back to its source,
2. blog and Facebook outputs are linked in a normalized tracking layer,
3. selected variants are recorded when relevant,
4. the operator can inspect publish history without guesswork,
5. Phase 4.5 and later Phase 5 can build on the tracking layer without redefining lineage.

## Handoff To Phase 4.5 And Phase 5

The next required gate after Phase 4 is activation.

Phase 4.5 should validate the live operator path before Decision Layer work begins.

Phase 5 should only begin after the tracking foundation is stable enough to compare outcomes and identify patterns with confidence and after Phase 4.5 proves the connected live workflow.

## Entry Control

Reference:

1. [PHASE_3_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_CLOSEOUT.md)
2. [PHASE_3_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_3_RESIDUAL_ITEMS.md)
3. [PHASE_4_ENTRY_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_ENTRY_CHECKLIST.md)
4. [PHASE_4_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_EXECUTION_PLAN.md)
5. [PHASE_4_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_VALIDATION_PLAN.md)
