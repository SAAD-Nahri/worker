# Phase 4.9 Acceptance Batch 2

## Scope

This acceptance batch records the first queue-guidance hardening pass for the Approval UI.

The goal of this batch is to prove that:

1. the operator API now exposes explicit queue scheduling eligibility,
2. the WordPress admin shell no longer offers blind schedule actions for blocked queue items,
3. queue scheduling still respects the existing append-only approval and scheduling gates.

## What Changed

### Backend

The queue payloads now include:

1. `schedule_allowed`
2. `schedule_block_reason`
3. queue-detail `allowed_actions`

This means the UI can tell the operator:

1. whether schedule action is currently allowed,
2. why it is blocked when it is not,
3. that Approval UI V1 still only supports direct scheduling for blog queue items.

### WordPress admin plugin

The queue pages now:

1. hide the schedule action when scheduling is blocked,
2. show the schedule block reason instead,
3. show schedule eligibility on the queue detail screen.

## Validation Baseline

Python validation:

```powershell
python -m unittest tests.unit.operator_api.test_app -v
python -m unittest discover -s tests -v
```

Accepted result:

1. full suite green at `222` tests passing.

## Known Limit

The plugin still requires live WordPress-admin validation because PHP CLI is not available in the local repo environment.

So this batch is accepted as:

1. backend-validated,
2. plugin-updated,
3. still awaiting live admin verification.
