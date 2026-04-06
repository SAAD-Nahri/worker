# Phase 4.5: System Activation And Live Validation

## Objective

Prove that the current system can run as a real operator workflow in a live environment before more decision complexity is added.

This phase exists between Phase 4 and Phase 5 on purpose.

The repo already has:

1. internal component contracts,
2. append-only runtime records,
3. transport adapters,
4. cross-phase tests,
5. operator-facing health and audit reporting.

What it does not yet prove is the live operator baseline:

1. real local config setup,
2. real credential validation,
3. one owned-environment canary chain,
4. one repeatable activation runbook.

## Why This Phase Matters

The biggest risk now is no longer architecture drift inside the repo.

The biggest risk is a false sense of readiness:

1. tests pass,
2. contracts look clean,
3. docs are complete,
4. but the real operator environment is still unproven.

Phase 4.5 is the gate that separates:

1. a well-built internal machine,
2. from an actually runnable system.

## Main Responsibilities

1. define the local secrets and transport-config policy,
2. define the safe operator setup path for WordPress and Facebook credentials,
3. validate both transports against owned live environments with execute-mode read-only checks,
4. run one controlled canary chain through the current operator flow,
5. confirm that health, schedule, tracking, and audit outputs still make sense after the canary run,
6. capture acceptance evidence before Decision Layer work starts.

## Inputs

Phase 4.5 starts from the accepted upstream baseline in:

1. [PHASE_4_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_CLOSEOUT.md)
2. [PHASE_4_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_RESIDUAL_ITEMS.md)
3. [DISTRIBUTION_ENGINE_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/DISTRIBUTION_ENGINE_RUNBOOK.md)
4. [TRACKING_ENGINE_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/TRACKING_ENGINE_RUNBOOK.md)
5. [WORDPRESS_TRANSPORT_VALIDATION_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_TRANSPORT_VALIDATION_V1.md)
6. [FACEBOOK_TRANSPORT_VALIDATION_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/FACEBOOK_TRANSPORT_VALIDATION_V1.md)
7. [LOCAL_SECRETS_AND_TRANSPORT_CONFIG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/LOCAL_SECRETS_AND_TRANSPORT_CONFIG_POLICY_V1.md)
8. [SYSTEM_ACTIVATION_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/SYSTEM_ACTIVATION_RUNBOOK.md)

## What This Phase Is Not

Phase 4.5 is not:

1. a Decision Layer phase,
2. a dashboard phase,
3. a new AI phase,
4. a channel expansion phase,
5. a paid amplification phase.

It must not be used to smuggle in:

1. winner scoring,
2. CTR logic,
3. paid campaign logic,
4. additional social channels,
5. agent orchestration.

## Required Outputs

1. a locked local secrets and config policy,
2. safe example config files for WordPress and Facebook,
3. a system-activation runbook,
4. execute-mode transport-validation evidence for both transports,
5. one controlled canary-chain acceptance record,
6. an updated gate that blocks Phase 5 until activation succeeds.
7. safe remote-state inspection and local reconciliation for live WordPress canaries.

## Definition Of Done

Phase 4.5 is done when:

1. WordPress local config exists in a non-committed operator location,
2. Facebook local config exists in a non-committed operator location,
3. `validate_wordpress_transport.py --execute --record-audit` succeeds against the owned WordPress environment,
4. `validate_facebook_transport.py --execute --record-audit` succeeds against the owned Facebook Page,
5. one approved draft is used as a canary chain through the existing distribution workflow,
6. the post-canary distribution, tracking, and audit views remain coherent,
7. acceptance evidence is written down before Decision Layer work begins.

## Current Status

Current decision:

1. Phase 4 is still accepted as closed for tracking-scope purposes,
2. Phase 5 is no longer the immediate next active phase,
3. Phase 4.5 is now the required release gate before more system complexity is added.

Current operational status:

1. ignored local WordPress and Facebook config scaffolding files now exist,
2. dry-run validation has been executed successfully for both transports,
3. one technical local canary-preparation chain has been recorded in [PHASE_4_5_ACCEPTANCE_BATCH_1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_1.md),
4. the second activation checkpoint in [PHASE_4_5_ACCEPTANCE_BATCH_2.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_2.md) confirms the current readiness signal is `awaiting_real_credentials`,
5. the execute-mode checkpoint in [PHASE_4_5_ACCEPTANCE_BATCH_3.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_3.md) confirms Facebook validation now succeeds against the owned Page,
6. the live draft-sync checkpoint in [PHASE_4_5_ACCEPTANCE_BATCH_4.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_4.md) confirms WordPress validation now succeeds and remote draft creation works against the owned site,
7. the replacement-canary checkpoint in [PHASE_4_5_ACCEPTANCE_BATCH_5.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_5.md) confirms a cleaner live draft now exists as remote WordPress draft `25`,
8. the remote-state reconciliation batch in [PHASE_4_5_ACCEPTANCE_BATCH_6.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_6.md) confirms WordPress post `25` is truly published, the local chain now reflects that published state, and the first live Facebook publish attempt failed only because the Page token had expired,
9. the remaining blocker is now an operator credential refresh on Facebook, not a missing WordPress state transition,
10. the current blocking state can now be reviewed directly through `python src\\cli\\summarize_system_activation.py --json`, `python src\\cli\\summarize_distribution_health.py --json`, and `python src\\cli\\summarize_publish_chain_history.py --view all --json`.
