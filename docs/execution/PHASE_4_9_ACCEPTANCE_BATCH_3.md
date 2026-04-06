# Phase 4.9 Acceptance Batch 3

## Scope

This acceptance batch records the dashboard hardening pass for the Approval UI baseline.

The goal of this batch is to prove that:

1. the operator API dashboard now exposes recent review activity,
2. the operator API dashboard now exposes current alert signals instead of counts alone,
3. the WordPress admin plugin shell now renders those dashboard panels without changing workflow authority.

## What Changed

### Backend

The dashboard summary now includes:

1. `recent_activity`
2. `current_alerts`

`recent_activity` is built from append-only draft, social-package, and queue-review records.

`current_alerts` is built from:

1. distribution failure and consistency signals,
2. schedule alerts,
3. activation blockers.

### WordPress admin plugin

The dashboard now renders:

1. a `Recent Review Activity` panel,
2. a `Current Alerts` panel,
3. the existing fast-lane placeholder card underneath the dashboard status blocks.

## Validation Baseline

Python validation:

```powershell
python -m unittest tests.unit.operator_api.test_app -v
python -m unittest discover -s tests -v
```

Accepted result:

1. focused operator API tests green,
2. full suite green at `223` tests passing.

## Known Limit

The plugin still requires live WordPress-admin validation because PHP CLI is not available in the local repo environment.

So this batch is accepted as:

1. backend-validated,
2. plugin-updated,
3. still awaiting live admin verification.
