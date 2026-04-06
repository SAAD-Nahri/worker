# Phase Governance

## Purpose

This document defines how phases are opened, executed, reviewed, and closed.

The goal is simple:

A phase does not end when the code feels done. A phase ends when the work is implemented, validated, documented, operationally understandable, and ready to hand off without hidden dependency debt.

This project is long-running and solo-operator oriented. That means phase discipline is not bureaucracy. It is protection against drift, rework, and accidental overbuilding.

## Core Rule

Every phase must pass five checks before it can be treated as closed:

1. scope check,
2. validation check,
3. operational readiness check,
4. documentation check,
5. handoff check.

If any one of those checks is incomplete, the phase remains open.

## What Counts As A Properly Closed Phase

A phase is properly closed only when all of the following are true:

1. the phase objective is met,
2. the required outputs for that phase exist,
3. the current implementation baseline is validated,
4. the operator knows how to run, review, and reset the phase safely,
5. the authoritative files for the phase are known,
6. the residual risks are recorded,
7. the next phase has a clear entry checklist,
8. the repo-level planning docs reflect reality.

## Mandatory Gate Areas

### 1. Scope Check

Confirm:

1. the phase delivered what its brief said it needed to deliver,
2. the work stayed inside phase boundaries,
3. out-of-scope work was not smuggled in as unfinished technical debt,
4. the upstream and downstream contracts are explicit.

### 2. Validation Check

Confirm:

1. the relevant tests pass,
2. the core validation commands have been run recently,
3. the current baseline behavior is recorded,
4. known defects are classified as blockers or acceptable residual risk.

### 3. Operational Readiness Check

Confirm:

1. the operator can identify the authoritative inputs for the phase,
2. the operator can identify the generated runtime state for the phase,
3. the operator knows how to repeat the core workflow,
4. the operator knows how to recover from a bad run or reset local state safely,
5. no hidden manual steps are required.

### 4. Documentation Check

Confirm:

1. the phase brief is current,
2. the closeout review exists,
3. the next-phase entry checklist exists,
4. `README.md` reflects the current project baseline,
5. `TODO.md` reflects the true completion state,
6. `OPEN_QUESTIONS.md` contains only real unresolved items,
7. any relevant specs or runbooks are aligned with the actual implementation.

### 5. Handoff Check

Confirm:

1. the next phase can start without guessing,
2. the next phase is not expected to patch hidden gaps in the previous phase,
3. the next phase knows what inputs it receives,
4. the next phase knows what it must not redefine,
5. the next phase knows what remains intentionally out of scope.

## Mandatory Artifacts For Phase Closure

Every completed phase should leave these artifacts behind:

1. a current phase brief,
2. a closeout review document,
3. a next-phase entry checklist,
4. an updated `TODO.md`,
5. an updated `README.md`,
6. an updated `OPEN_QUESTIONS.md`,
7. any required runbook or spec updates,
8. a recorded validation baseline.

## Configuration Readiness Rule

Before closing a phase, the team must be able to answer these questions clearly:

1. what files are authoritative inputs,
2. what files are generated outputs,
3. what configuration drives the phase,
4. what commands reproduce the current baseline,
5. what command or procedure resets or archives runtime state,
6. what would break the next phase if misunderstood.

If those answers are not documented, the phase is not fully configured.

## Residual Risk Rule

A phase may close with residual risk only if the residual risk is:

1. known,
2. documented,
3. non-blocking for the next phase,
4. not a disguised scope hole.

If the unresolved issue changes the contract of the phase or would force the next phase to compensate for it, the phase stays open.

## What Must Block Phase Closure

Do not close a phase if any of the following are true:

1. the core validation path is failing,
2. the operator workflow is unclear,
3. the authoritative files are ambiguous,
4. the next phase would need to reverse-engineer the current phase,
5. the docs no longer match the implementation,
6. out-of-scope work is quietly becoming required work,
7. the current baseline cannot be reproduced.

## Default Closeout Sequence

Use this sequence before moving phases:

1. review the phase brief,
2. run the required validation commands,
3. confirm operational readiness,
4. update the runbook and specs if needed,
5. update `README.md`, `TODO.md`, and `OPEN_QUESTIONS.md`,
6. write the closeout review,
7. write the next-phase entry checklist,
8. confirm residual risks and non-goals,
9. only then treat the phase as closed.

## Default Entry Sequence For The Next Phase

Use this sequence before beginning the next phase:

1. read the previous phase closeout review,
2. read the new phase brief,
3. satisfy the entry checklist,
4. confirm the first narrow implementation order,
5. confirm what remains out of scope,
6. start work only after the phase boundary is clear.

## Final Rule

Professional execution in this repository means:

1. no phase skipping,
2. no silent contract changes,
3. no loose handoffs,
4. no "we will fix it in the next phase" behavior for core gaps,
5. no moving on until the current phase is genuinely stable enough to support the next one.
