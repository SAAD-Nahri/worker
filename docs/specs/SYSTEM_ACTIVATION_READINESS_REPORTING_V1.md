# System Activation Readiness Reporting V1

## Purpose

This spec defines the operator-facing readiness report for Phase 4.5.

The report exists to answer one practical question:

1. what still blocks a real live activation pass right now?

It is not a transport validator by itself.

It is a synthesized readiness view built from:

1. local config files,
2. approved draft state,
3. local canary-chain runtime state,
4. tracking audit records for execute-mode transport validation.

## Core Role

The readiness report should make Phase 4.5 safer by replacing guesswork with an explicit operator signal.

It should tell the operator:

1. whether local config scaffolding exists,
2. whether the config still contains placeholder values,
3. whether at least one approved pass-quality canary draft exists,
4. whether a local canary-preparation chain already exists,
5. whether execute-mode transport validation has been recorded,
6. whether a real live canary execution is still missing.

## Inputs

The report reads from:

1. `config/wordpress_rest_config.local.json`
2. `config/facebook_graph_config.local.json`
3. append-only draft records
4. append-only distribution records
5. append-only tracking audit records

## Required Output Areas

The report must expose:

1. summary,
2. config statuses,
3. approved canary draft candidates,
4. local canary rows.

## Summary Requirements

The summary must include:

1. `readiness_signal`
2. `blocking_reasons`
3. `latest_distribution_snapshot_at`
4. `latest_transport_validation_at`
5. `wordpress_config_ready`
6. `facebook_config_ready`
7. `approved_pass_draft_count`
8. `local_canary_chain_count`
9. `successful_wordpress_validations`
10. `successful_facebook_validations`
11. `next_steps`

## Allowed Readiness Signals

The report must use a small controlled set of signals:

1. `config_scaffolding_missing`
2. `awaiting_real_credentials`
3. `awaiting_approved_canary_draft`
4. `awaiting_local_canary_chain`
5. `awaiting_execute_validation`
6. `awaiting_live_canary_execution`
7. `ready_for_phase_4_5_closeout`
8. `activation_blocked`

## Blocking Reason Rules

Blocking reasons must stay specific and operational.

Allowed baseline reasons:

1. `wordpress_config_missing`
2. `wordpress_config_not_ready`
3. `facebook_config_missing`
4. `facebook_config_not_ready`
5. `approved_pass_draft_missing`
6. `local_canary_chain_missing`
7. `wordpress_execute_validation_missing`
8. `facebook_execute_validation_missing`
9. `live_canary_execution_missing`

## Config Inspection Rules

The readiness report must:

1. detect whether the file exists,
2. detect whether the file is valid JSON,
3. detect whether required top-level fields are missing,
4. detect obvious placeholder values,
5. avoid printing secrets.

For WordPress config, obvious placeholders include:

1. `https://example.com`
2. `wordpress_username`
3. application passwords that still contain `xxxx`

For Facebook config, obvious placeholders include:

1. `123456789012345`
2. tokens that still contain `PLACEHOLDER` or `REPLACE_LOCALLY`

## Draft Candidate Rules

The report must only treat a draft as a canary candidate when:

1. `approval_state=approved`
2. `quality_gate_status=pass`

## Local Canary Rules

The report may use the existing distribution-health row baseline as the local canary view.

The report must not pretend a local prepared chain is already a live canary execution.

## Execute Validation Rules

Successful execute-mode validation counts must only come from tracking audit records where:

1. `event_type=transport_validation`
2. `event_status=success`
3. `execution_mode=execute`
4. `entity_type` matches the target transport

## Next-Step Rules

The report must emit practical next steps in the same order the operator should execute them.

Those steps should be derived from blocking reasons, not hard-coded as one static paragraph.

## Non-Goals

This report must not:

1. publish content,
2. validate credentials remotely by itself,
3. override other health reports,
4. become a dashboard system,
5. redefine Phase 4.5 closeout rules.
