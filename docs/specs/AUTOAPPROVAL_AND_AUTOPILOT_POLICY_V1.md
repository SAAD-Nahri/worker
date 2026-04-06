# Autoapproval And Autopilot Policy V1

## Purpose

This policy defines how approval automation may be introduced later without violating the project's current human-approval-first baseline.

## Current Rule

For v1 and all phases before Phase 5.5:

1. human approval remains required,
2. scoring may be advisory,
3. no content should be autoapproved for public distribution by default.

## Allowed Future Direction

Autoapproval may be introduced only after:

1. Phase 5 scoring exists,
2. Phase 4.5, 4.6, 4.7, 4.8, and 4.9 are complete,
3. shadow-mode evidence has been collected,
4. rollback and kill-switch rules exist.

## Approval Automation Principles

1. explainable beats opaque,
2. narrow lanes beat broad automation,
3. shadow mode beats guesswork,
4. rollback must be immediate,
5. operator override is mandatory.

## Required Safeguards

Any live autoapproval layer must preserve:

1. visible reasons,
2. approval audit records,
3. override capability,
4. kill-switch capability,
5. hard blocks for unsafe or weak-fit content.

## Disallowed Approaches

1. autoapproving every content family,
2. using one score threshold with no lane restrictions,
3. hiding model-based decisions from the operator,
4. enabling autopublish before shadow mode is proven,
5. treating autoapproval as a substitute for quality policy.
