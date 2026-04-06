# Phase 5 Entry Checklist

## Purpose

This document controls the start of Phase 5: Decision Layer.

It exists to prevent a common failure mode in this project:

1. jumping into scoring and winner logic before the tracking contract is genuinely stable,
2. forcing Phase 5 to compensate for missing data collection, weak lineage, or unclear Phase 4 boundaries.

Reference:

1. [PHASE_GOVERNANCE.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_GOVERNANCE.md)

## Entry Rule

Do not begin Phase 5 implementation work until the checklist in this file is actively reviewed and satisfied.

Phase 5 should begin from trusted tracking outputs, a proven live operator path, a stabilized AI-quality layer, a defined media baseline, an explicit runtime operating model, and a stable operator oversight surface, not from guesses, dashboards, or agent-first ambitions.

## Required Inputs From Phase 4

Phase 5 must begin with the following already in place:

1. a stable normalized publish-history contract,
2. deterministic lineage joins from source item through Facebook publish state,
3. selected-value preservation for title and social outputs,
4. operator-readable ledger, exception, activity, and variant reporting views,
5. a deliberate tracking audit layer,
6. an explicit policy for keeping normalized snapshots on demand until persistence is actually justified,
7. a documented Phase 4 residual-items list so later work does not silently redefine old scope,
8. completed Phase 4.5 activation work that proves the system can run with live local config and a canary publish chain,
9. completed Phase 4.6 AI-assisted content-quality work that proves provider-backed enhancement can stay bounded and fallback-safe,
10. completed Phase 4.7 media work that proves the publish chain is not missing its visual layer.
11. completed Phase 4.8 runtime and deployment work that proves the system can be run, scheduled, backed up, and recovered by one person without guesswork,
12. completed Phase 4.9 approval UI work that proves human review has a stable operator console before later scoring or autopilot work begins.

Primary references:

1. [PHASE_4_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_CLOSEOUT.md)
2. [PHASE_4_CLOSEOUT_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_CLOSEOUT_CHECKLIST.md)
3. [PHASE_4_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_RESIDUAL_ITEMS.md)
4. [PHASE_4_TRACKING_FOUNDATION.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_TRACKING_FOUNDATION.md)
5. [PUBLISH_CHAIN_SNAPSHOT_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_CONTRACT_V1.md)
6. [PUBLISH_HISTORY_NORMALIZATION_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_HISTORY_NORMALIZATION_V1.md)
7. [TRACKING_LINEAGE_JOIN_RULES_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_LINEAGE_JOIN_RULES_V1.md)
8. [VARIANT_RECORDING_RULES_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/VARIANT_RECORDING_RULES_V1.md)
9. [TRACKING_REPORTING_VIEWS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_REPORTING_VIEWS_V1.md)
10. [TRACKING_AUDIT_RECORDS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/TRACKING_AUDIT_RECORDS_V1.md)
11. [PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md)
12. [TRACKING_ENGINE_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/TRACKING_ENGINE_RUNBOOK.md)
13. [PHASE_4_5_SYSTEM_ACTIVATION.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_5_SYSTEM_ACTIVATION.md)
14. [PHASE_4_5_ENTRY_CHECKLIST.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_5_ENTRY_CHECKLIST.md)
15. [PHASE_4_5_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_5_EXECUTION_PLAN.md)
16. [PHASE_4_5_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_5_VALIDATION_PLAN.md)
17. [PHASE_4_6_AI_ASSISTED_CONTENT_QUALITY.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_6_AI_ASSISTED_CONTENT_QUALITY.md)
18. [PHASE_4_7_MEDIA_AND_ASSET_LAYER.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_7_MEDIA_AND_ASSET_LAYER.md)
19. [PHASE_4_8_RUNTIME_OPERATIONS_AND_DEPLOYMENT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_8_RUNTIME_OPERATIONS_AND_DEPLOYMENT.md)
20. [PHASE_4_8_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_8_EXECUTION_PLAN.md)
21. [PHASE_4_8_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_8_VALIDATION_PLAN.md)
22. [PHASE_4_9_APPROVAL_UI_AND_OPERATOR_CONSOLE.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_9_APPROVAL_UI_AND_OPERATOR_CONSOLE.md)
23. [PHASE_4_9_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_9_EXECUTION_PLAN.md)
24. [PHASE_4_9_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_9_VALIDATION_PLAN.md)
25. [OPERATOR_API_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/OPERATOR_API_CONTRACT_V1.md)
26. [WORDPRESS_ADMIN_APPROVAL_PLUGIN_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_ADMIN_APPROVAL_PLUGIN_V1.md)
27. [APPROVAL_UI_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/APPROVAL_UI_RUNBOOK.md)
28. [RUNTIME_OPERATING_MODEL_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/RUNTIME_OPERATING_MODEL_V1.md)
29. [DEPLOYMENT_AND_SCHEDULING_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DEPLOYMENT_AND_SCHEDULING_POLICY_V1.md)
30. [BACKUP_AND_RECOVERY_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/BACKUP_AND_RECOVERY_POLICY_V1.md)
31. [OPERATIONS_AND_DEPLOYMENT_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/OPERATIONS_AND_DEPLOYMENT_RUNBOOK.md)
32. [LOCAL_SECRETS_AND_TRANSPORT_CONFIG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/LOCAL_SECRETS_AND_TRANSPORT_CONFIG_POLICY_V1.md)
33. [AI_ASSISTED_CONTENT_QUALITY_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/AI_ASSISTED_CONTENT_QUALITY_POLICY_V1.md)
34. [MEDIA_AND_VISUAL_ASSET_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/MEDIA_AND_VISUAL_ASSET_POLICY_V1.md)
35. [SYSTEM_ACTIVATION_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/SYSTEM_ACTIVATION_RUNBOOK.md)
36. [PHASE_5_DECISION_LAYER.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_5_DECISION_LAYER.md)

## Entry Checklist

### 1. Upstream contract check

- [x] Phase 4 closeout has been reviewed.
- [x] The accepted Phase 4 contract is stable enough that Phase 5 does not need to redefine lineage or normalization.
- [x] The authoritative Phase 5 upstream input is known: trusted tracking outputs and append-only runtime records, not guessed metrics.

### 2. Phase boundary check

- [x] Everyone working on Phase 5 agrees that it starts with decision rules on top of the existing tracking layer.
- [x] Everyone working on Phase 5 agrees that Phase 5 does not reopen data collection, transport, or dashboard architecture.
- [x] Out-of-scope expansion such as paid amplification, multilingual rollout, and agent-first orchestration is not mixed into the initial plan.

### 3. Design readiness check

- [x] The first Phase 5 work should begin with data-readiness gates and early winner-signal definitions, not broad automation.
- [x] Sparse-data guardrails are understood as mandatory before ranking outputs become operationally important.
- [x] The current snapshot-persistence policy is understood and will not be bypassed casually during decision-layer work.

### 4. Operational readiness check

- [x] The relevant Phase 5 docs are current enough to start planning.
- [ ] Phase 4.5 activation has been completed and recorded.
- [ ] Phase 4.6 AI-assisted content quality has been completed and recorded.
- [ ] Phase 4.7 media and asset handling has been completed and recorded.
- [ ] Phase 4.8 runtime operations and deployment has been completed and recorded.
- [ ] Phase 4.9 approval UI and operator console has been completed and recorded.
- [ ] `TODO.md` reflects that the current gate before Phase 5 is now 4.5 -> 4.6 -> 4.7 -> 4.8 -> 4.9.
- [x] The first Phase 5 validation path is understood before broader decision logic is proposed.

## Default Phase 5 Build Order

When Phase 5 begins, the recommended implementation order is:

1. define minimum data-readiness gates for any decision output,
2. define the first early winner-signal rules,
3. define the first source, template, and hook comparison inputs,
4. define promotion-candidate rules only after the earlier signals are explicit,
5. reconsider heavier reasoning or persistence only if the earlier deterministic layer proves insufficient.

## What Must Not Happen At Phase 5 Start

Do not start Phase 5 by:

1. assuming click or revenue data already exists,
2. building dashboards first,
3. introducing agent orchestration before deterministic decision rules exist,
4. persisting normalized snapshots without meeting the accepted trigger conditions,
5. letting weak or empty live history masquerade as enough evidence for strong ranking decisions.

## First Questions Phase 5 Must Answer

The first Decision Layer questions should be:

1. what minimum evidence threshold is required before any source, template, or hook is treated as a meaningful signal,
2. which early signals can remain deterministic before richer performance data is added,
3. what the first external performance data source should be when the repo is ready to add one,
4. how Phase 5 will avoid overfitting sparse or early publish history,
5. which outputs stay advisory versus which could eventually influence operator prioritization.

## Entry Decision

Current decision:

1. `hold Phase 5 implementation until Phases 4.5, 4.6, 4.7, 4.8, and 4.9 complete`
