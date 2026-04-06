# Phase 4.9 Acceptance Batch 4

## Scope

This acceptance batch records the queue-removal hardening pass for the Approval UI baseline.

The goal of this batch is to prove that:

1. queue removal is now a first-class append-only review outcome,
2. the operator can remove an item from the current batch without faking it as another state,
3. the plugin now exposes `Remove` as a real queue action in the review shell.

## What Changed

### Backend

Queue review now accepts:

1. `approved`
2. `hold`
3. `removed`

`removed` records an explicit queue-review outcome and writes queue-review state `removed` without mutating queue items in place.

This keeps removal:

1. auditable,
2. append-only,
3. clearly separate from approval and scheduling.

### WordPress admin plugin

The queue UI now exposes `Remove` alongside the other queue-review actions.

The queue inbox links the operator into the detail screen for note-backed removal, and the queue detail form now includes a direct `Remove` button.

## Validation Baseline

Python validation:

```powershell
python -m unittest tests.unit.distribution_engine.test_queue_review tests.unit.operator_api.test_app -v
python -m unittest discover -s tests -v
```

Accepted result:

1. focused queue/operator tests green,
2. full suite green at `225` tests passing.

## Known Limit

The plugin still requires live WordPress-admin validation because PHP CLI is not available in the local repo environment.

So this batch is accepted as:

1. backend-validated,
2. plugin-updated,
3. still awaiting live admin verification.
