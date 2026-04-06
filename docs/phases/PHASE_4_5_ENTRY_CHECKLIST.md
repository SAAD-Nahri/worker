# Phase 4.5 Entry Checklist

## Purpose

This checklist controls the start of Phase 4.5: System Activation And Live Validation.

It exists to prevent a simple mistake:

1. assuming the system is ready for live operator use because tests and internal contracts are already strong.

## Entry Rule

Do not treat live activation as an informal side task.

Before Decision Layer work continues, activation must be treated as explicit phase work with its own execution and validation path.

## Required Inputs

Phase 4.5 begins from:

1. [PHASE_4_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_CLOSEOUT.md)
2. [PHASE_4_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_RESIDUAL_ITEMS.md)
3. [PHASE_4_5_SYSTEM_ACTIVATION.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_5_SYSTEM_ACTIVATION.md)
4. [PHASE_4_5_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_5_EXECUTION_PLAN.md)
5. [PHASE_4_5_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_5_VALIDATION_PLAN.md)
6. [LOCAL_SECRETS_AND_TRANSPORT_CONFIG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/LOCAL_SECRETS_AND_TRANSPORT_CONFIG_POLICY_V1.md)
7. [SYSTEM_ACTIVATION_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/SYSTEM_ACTIVATION_RUNBOOK.md)

## Entry Checklist

### 1. Upstream contract check

- [x] Phase 4 closeout has been reviewed.
- [x] The accepted Phase 1 to Phase 4 contracts do not need redesign before activation.
- [x] The repo already has dry-run-safe WordPress and Facebook transport paths.
- [x] The repo already has audit and reporting paths strong enough to inspect a canary run.

### 2. Activation-boundary check

- [x] This phase is explicitly about activation, not more product logic.
- [x] This phase will not be used to add winner scoring, analytics product work, or more channels.
- [x] Local secrets handling is now treated as first-class repo documentation, not tribal knowledge.

### 3. Operator-environment check

- [ ] An owned WordPress environment for the canary run has been selected.
- [ ] An owned Facebook Page for the canary run has been selected.
- [ ] The operator is ready to use non-committed local config files for both transports.
- [ ] The operator understands that test or owned environments are required before any real production use.

### 4. Canary-readiness check

- [ ] One approved draft has been selected as the first canary chain.
- [ ] The operator understands the full canary path from draft to WordPress to Facebook to tracking.
- [ ] The acceptance evidence location for the canary run is known before execution starts.

## Current Decision

Current decision:

1. `ready to begin Phase 4.5 activation planning and operator setup`
2. `not ready for Phase 5 implementation until Phase 4.5 is complete`
