# Phase 4.9: Approval UI And Operator Console

## Objective

Build the first real human-approval console on top of the repo runtime.

This phase exists because human approval is already part of the system contract, but CLI-only review is not the right long-term operator surface for a solo publishing workflow. The system needs one serious review console before later scoring and autoapproval work can be trusted.

## Recommended Default

The default Approval UI V1 shape is:

1. a private internal operator API on the Python worker,
2. a thin WordPress admin plugin as the review shell,
3. repo runtime records remaining the source of truth,
4. fast-lane support designed into the UI but disabled.

## Why This Phase Matters

Without this phase:

1. human approval stays technically possible but operationally awkward,
2. later scoring and approval automation have no stable oversight surface,
3. the operator must bounce between runtime files and CLI actions,
4. the project risks inventing a second workflow system later under pressure.

## Main Responsibilities

1. define the operator API contract,
2. define the WordPress admin plugin contract,
3. expose draft, social, and queue review in one review shell,
4. preserve append-only review and scheduling actions,
5. keep the future fast lane visible but disabled.

## Required Outputs

1. operator API contract,
2. WordPress admin approval-plugin contract,
3. approval UI runbook,
4. phase execution plan,
5. phase validation plan,
6. acceptance evidence,
7. updated roadmap showing that Phase 5 should not bypass the operator console.

## What This Phase Must Not Do

1. become a second workflow database,
2. turn WordPress into the workflow source of truth,
3. build a full editorial CMS,
4. expose public publishing shortcuts outside the repo audit path,
5. enable fast-lane or autoapproval behavior.

## Current Implementation Baseline

The current phase baseline already includes:

1. internal operator API implementation,
2. append-only queue review records,
3. WordPress admin plugin shell,
4. Python-side automated validation,
5. dedicated live-validation support through a plugin Validation page and operator-validation endpoint,
6. documented plugin validation gap caused by missing PHP CLI in the local repo environment.

## Definition Of Done

Phase 4.9 is done when:

1. the operator API is documented and test-covered,
2. the WordPress plugin shell is documented and installable,
3. dashboard, draft review, social review, and queue review are all reachable in the UI,
4. plugin-to-backend auth is explicit,
5. real WordPress-admin validation has been recorded,
6. Phase 5 can assume a stable operator oversight surface exists.
