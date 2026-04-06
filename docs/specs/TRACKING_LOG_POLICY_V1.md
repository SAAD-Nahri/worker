# Tracking Log Policy V1

## Purpose

This document defines what logs Phase 4 should treat as essential and what should remain out of scope.

The goal is to keep debugging and auditability strong without creating noisy infrastructure that a solo operator will not actually trust or maintain.

## Core Rule

Use the existing append-only records as the default audit trail.

Only add a new tracking log category when an important operational question cannot already be answered from:

1. source item records,
2. source review decisions,
3. draft records,
4. draft reviews,
5. blog publish records,
6. social package records,
7. social package reviews,
8. Facebook publish records,
9. queue records,
10. mapping records,
11. archived runtime snapshots.

## Required Log Categories

Phase 4 should explicitly support these log categories:

### 1. Content Lineage Logs

Purpose:

1. explain how a published chain maps back to its source and draft

Primary backing records:

1. source items
2. drafts
3. blog publish records
4. mapping records

### 2. Review And Approval Logs

Purpose:

1. explain who approved, rejected, or edited a draft or social package

Primary backing records:

1. draft reviews
2. social package reviews

### 3. Publish Attempt Logs

Purpose:

1. explain what happened during blog or Facebook publish attempts

Primary backing records:

1. blog publish records
2. Facebook publish records

### 4. Workflow Exception Logs

Purpose:

1. explain broken-chain states, scheduling conflicts, or missing-link conditions

Primary backing records:

1. queue records
2. mapping records
3. derived health reports

### 5. Runtime Reset And Archive Logs

Purpose:

1. explain when runtime history was archived during clean local reruns

Primary backing records:

1. archive folder snapshots
2. reset workflow outputs

### 6. Tracking Normalization Run Logs

Purpose:

1. explain when normalized publish-history snapshots were generated
2. preserve input row counts, output row counts, and error totals
3. make Phase 4 rebuilds auditable

Primary backing records:

1. Phase 4 normalization-run records when implemented

### 7. Transport Validation Audit Logs

Purpose:

1. explain when a real WordPress or Facebook transport validation was executed
2. preserve which identity was validated or which error blocked validation
3. avoid relying on shell history as the only proof of live-environment readiness

Primary backing records:

1. Phase 4 transport-validation audit records when implemented

## Essential Log Fields

When a dedicated Phase 4 log record is justified, it should preserve at minimum:

1. `event_id`
2. `event_type`
3. `entity_type`
4. `entity_id`
5. `chain_id` when applicable
6. `event_status`
7. `event_summary`
8. `event_timestamp`
9. `actor_label`

## What Not To Log

Do not add logs for:

1. every report read,
2. every harmless CLI preview,
3. every internal helper step,
4. duplicated copies of fields already visible in append-only entity records,
5. speculative future analytics events,
6. every retry attempt unless live evidence proves the final publish records are insufficient.

## Logging Decision Rule

Before adding a new log type, ask:

1. what operator question cannot currently be answered
2. which current append-only records already answer most of it
3. whether a derived report would solve the problem more simply than a new log file

If a derived report is enough, prefer the report.

## Phase 4 Default Position

The default Phase 4 position should be:

1. normalize existing records first
2. build reporting on those records second
3. add new logs only for proven blind spots

## Definition Of Done

This policy is satisfied when:

1. essential log categories are explicit,
2. noisy logging is actively avoided,
3. later debugging and audit work can build on a small trustworthy set of records.

## Current Baseline

The current repo now implements:

1. deliberate normalization-run audit records,
2. execute-mode WordPress transport validation audit records,
3. execute-mode Facebook transport validation audit records,
4. a dedicated CLI summary for the tracking audit log.

The current snapshot policy remains:

1. normalized publish-chain snapshots stay on demand,
2. audit records log deliberate rebuild activity when needed,
3. no persisted snapshot artifact is added until the trigger conditions in [PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md) are met.

The remaining question is not whether an audit layer exists. It is whether any additional record types are justified beyond this narrow baseline.
