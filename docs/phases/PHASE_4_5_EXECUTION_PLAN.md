# Phase 4.5 Execution Plan

## Purpose

This document turns the new activation gate into concrete work.

The goal is to prove the existing system can operate with real credentials and real operator-owned endpoints before we add more decision complexity.

## Execution Principle

Phase 4.5 should add as little new architecture as possible.

Its job is to validate the current architecture in a live operator environment, not to invent another subsystem.

## Slice 1: Local Secrets And Config Setup

### Objective

Make local WordPress and Facebook config setup explicit, safe, and repeatable.

### Deliverables

1. local secrets and transport-config policy,
2. safe example config files,
3. clear recommended local config paths,
4. repo guidance that blocks committing secrets,
5. an operator-facing readiness report that makes placeholder config and missing activation evidence visible.

### Out Of Scope

1. secret managers,
2. cloud deployment,
3. environment-variable orchestration,
4. multi-operator credential workflows.

## Slice 2: Execute-Mode Transport Validation

### Objective

Prove that the operator config files work against owned live endpoints without mutating content.

### Deliverables

1. execute-mode WordPress validation evidence,
2. execute-mode Facebook validation evidence,
3. audit records for those validation runs,
4. confirmed target identities for the owned environments.

### Out Of Scope

1. live content publishing,
2. post creation during validation,
3. multi-account transport support.

## Slice 3: Canary Chain Preparation

### Objective

Prepare one approved draft as a live canary without widening system scope.

### Deliverables

1. one approved draft chosen for activation,
2. one WordPress publish record prepared,
3. one social package record prepared and approved,
4. one linkage refresh performed before live transport execution.

### Out Of Scope

1. batch publishing,
2. high-volume scheduling,
3. experimentation across many variants.

## Slice 4: Canary Chain Execution

### Objective

Run one complete owned-environment canary chain through the existing operator workflow.

### Deliverables

1. one live WordPress draft sync or update,
2. one safe remote WordPress post-state inspection path for canaries that are finalized in wp-admin,
3. one recorded WordPress publish-state transition appropriate to the canary,
4. one live Facebook schedule or publish action against the owned Page,
5. append-only records preserved across the whole chain.

### Out Of Scope

1. unattended automation,
2. multi-post queue releases,
3. comment CTA auto-posting.

## Slice 5: Post-Run Verification

### Objective

Confirm that the connected system remains readable and trustworthy after a live canary run.

### Deliverables

1. distribution-health review,
2. schedule-report review,
3. publish-chain history review,
4. tracking-audit review,
5. written activation acceptance evidence.

### Out Of Scope

1. interpreting business performance,
2. winner ranking,
3. scaling decisions.

## Exit Recommendation

Do not move to Phase 5 because the canary merely executed.

Move only when:

1. config setup is safe and documented,
2. both execute-mode validations succeeded,
3. the canary chain is visible in the existing reports,
4. the operator can repeat the process without guessing.

Current status note:

1. slices 1 and the local parts of 3 and 5 now have working evidence in [PHASE_4_5_ACCEPTANCE_BATCH_1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_1.md),
2. slice 2 is complete with real execute-mode validation evidence,
3. slice 4 now has live WordPress publication plus append-only remote-state reconciliation evidence in [PHASE_4_5_ACCEPTANCE_BATCH_6.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_6.md),
4. the only remaining live-execution blocker is the expired Facebook Page token that prevented the final canary publish.
