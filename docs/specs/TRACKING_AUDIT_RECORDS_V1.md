# Tracking Audit Records V1

## Purpose

This document defines the first dedicated Phase 4 audit records.

The goal is to preserve only the events that are important enough to justify their own append-only log:

1. deliberate normalization runs,
2. real execute-mode transport validation runs.

## Core Rule

Tracking audit records are not a general event stream.

They exist only for blind spots that the current runtime records do not already answer cleanly.

Do not use this layer to log:

1. every report read,
2. every dry-run preview,
3. every helper step,
4. every retry attempt.

## Runtime Artifact

The v1 audit log should live at:

1. `data/tracking_audit_records.jsonl`

The file is append-only and should be treated like other runtime artifacts:

1. useful for audit and debugging,
2. not a planning document,
3. archived by the runtime reset workflow.

## Supported Event Types

### 1. `normalization_run`

Purpose:

1. record a deliberate Phase 4 publish-history run,
2. preserve which view was generated,
3. preserve the chain and exception totals used during that run.

This event should be recorded only when explicitly requested by the operator.

### 2. `transport_validation`

Purpose:

1. record a real execute-mode WordPress or Facebook validation run,
2. preserve the validated identity when successful,
3. preserve the blocking error when validation fails.

This event should not be recorded for dry-run validation previews.

## Required Fields

Every audit record must preserve at minimum:

1. `event_id`
2. `event_type`
3. `entity_type`
4. `entity_id`
5. `chain_id` when applicable
6. `event_status`
7. `event_summary`
8. `event_timestamp`
9. `actor_label`

## V1 Extended Fields

### Normalization-run fields

1. `view_name`
2. `execution_mode`
3. `total_chains`
4. `exception_chain_count`
5. `consistency_issue_chains`
6. `schedule_alert_chains`
7. `latest_snapshot_at`

### Transport-validation fields

1. `execution_mode`
2. `config_path`
3. `validated_identity_id`
4. `validated_identity_name`
5. `error_message`

## Entity Rules

### Normalization runs

Use:

1. `entity_type = "publish_chain_history"`
2. `entity_id = <view_name>`

### WordPress transport validation

Use:

1. `entity_type = "wordpress_transport"`
2. `entity_id = <base_url>`

### Facebook transport validation

Use:

1. `entity_type = "facebook_transport"`
2. `entity_id = <page_id>`

## Recording Rules

### 1. Normalization-run recording

Normalization-run records should be written only when the operator explicitly asks for an audit record.

The normal CLI behavior should stay read-only and non-logging by default.

### 2. Transport-validation recording

Transport-validation records should be written only when:

1. the operator uses execute mode,
2. the operator explicitly enables audit recording.

If the validation fails, the failed result should still be recorded.

### 3. No synthetic chain linkage

Most audit events are not chain-specific.

`chain_id` should therefore remain null unless a future audit event is truly scoped to one publish chain.

## Operator Reporting

Phase 4 should expose a small audit summary view that can answer:

1. how many normalization runs were recorded,
2. how many transport validations were recorded,
3. how many audit events failed,
4. what the most recent audit events were.

## What Must Be Avoided

Do not:

1. turn audit records into a general event bus,
2. write audit records for harmless dry-run previews,
3. duplicate large payloads already preserved elsewhere,
4. treat audit records as a replacement for the underlying source, draft, publish, queue, or mapping records.

## Current Baseline

The current repo now supports:

1. deliberate normalization-run audit records,
2. execute-mode WordPress transport validation audit records,
3. execute-mode Facebook transport validation audit records,
4. a CLI summary for tracking audit history.

## Definition Of Done

This spec is satisfied when:

1. the allowed audit records are explicit,
2. the runtime artifact is append-only,
3. noisy logging is still avoided,
4. the operator can review audit history without reading raw JSONL by hand.
