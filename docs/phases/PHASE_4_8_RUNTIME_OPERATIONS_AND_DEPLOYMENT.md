# Phase 4.8: Runtime Operations And Deployment

## Objective

Define the boring, repeatable production operating model for the finished system.

This phase exists because activation proves the live path works, but it does not fully answer how the system should run every day after build:

1. where the worker lives,
2. how recurring jobs fire,
3. how updates are deployed,
4. how runtime data is backed up,
5. how the solo operator recovers from failure.

## Recommended Default

The default production shape should be:

1. one small Linux VPS,
2. one repo checkout,
3. one Python virtual environment,
4. one service user,
5. one scheduled-job runner based on `systemd` services and timers,
6. WordPress kept as a separately hosted destination rather than merged into this repo runtime.

This project should run as a scheduled CLI worker, not as a public-facing always-on application server.

## Why This Phase Matters

Without an explicit runtime model, the system stays half-finished even if the content and transport logic are good.

The main risks are:

1. the system only works from the developer workstation,
2. updates become manual and fragile,
3. backups are forgotten,
4. runtime state becomes hard to restore,
5. later Decision Layer work starts on top of an undefined operations baseline.

## Main Responsibilities

1. lock the recommended production host model,
2. define the deployment and update process,
3. define recurring scheduled jobs versus manual operator actions,
4. define backup and recovery policy,
5. define the day-to-day operator runbook,
6. define what does and does not justify more infrastructure complexity.

## Required Outputs

1. runtime operating model,
2. deployment and scheduling policy,
3. backup and recovery policy,
4. operations and deployment runbook,
5. phase execution plan,
6. phase validation plan.

Planning references:

1. [PHASE_4_8_EXECUTION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_8_EXECUTION_PLAN.md)
2. [PHASE_4_8_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_8_VALIDATION_PLAN.md)
3. [RUNTIME_OPERATING_MODEL_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/RUNTIME_OPERATING_MODEL_V1.md)
4. [DEPLOYMENT_AND_SCHEDULING_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DEPLOYMENT_AND_SCHEDULING_POLICY_V1.md)
5. [BACKUP_AND_RECOVERY_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/BACKUP_AND_RECOVERY_POLICY_V1.md)
6. [OPERATIONS_AND_DEPLOYMENT_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/OPERATIONS_AND_DEPLOYMENT_RUNBOOK.md)

## What This Phase Must Not Do

1. introduce Kubernetes, swarm, or multi-host orchestration,
2. turn Docker into a mandatory runtime dependency,
3. create a custom admin web app just to run CLI tasks,
4. assume high-availability requirements that the business has not earned,
5. mix infrastructure complexity into Decision Layer planning.

## Definition Of Done

Phase 4.8 is done when:

1. the recommended production host model is explicit,
2. recurring jobs have a defined scheduler and cadence,
3. manual review steps are separated clearly from automated jobs,
4. backup and recovery rules are documented and testable,
5. the operator can deploy, update, restart, and recover the system without guesswork,
6. Phase 5 no longer needs to reopen runtime or deployment architecture questions.
