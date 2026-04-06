# Phase 4.9 Acceptance Batch 7

## Scope

This acceptance batch records the live-validation support pass for the Approval UI baseline.

The goal of this batch is to prove that:

1. the operator API now exposes one dedicated backend-readiness payload for plugin validation,
2. the WordPress admin plugin now provides a dedicated Validation page instead of forcing the operator to guess from multiple screens,
3. the Validation page can surface local config readiness, backend endpoint checks, workflow visibility, and a manual admin checklist in one place,
4. the repo test baseline remains green while this live-validation support is added.

## What Changed

### Operator API

The operator API now exposes:

1. `GET /validation/operator-baseline`

This endpoint returns:

1. backend readiness status,
2. endpoint check results for the approval-shell surfaces,
3. current workflow snapshot counts,
4. record-count visibility,
5. review-surface availability flags,
6. validation notes,
7. combined health payload for the same current runtime baseline.

### WordPress admin plugin shell

The plugin now includes a dedicated **Validation** submenu page.

That page now shows:

1. local validation checks for user, capability, API base URL, and shared-secret presence,
2. backend validation snapshot counts from the operator API,
3. endpoint check results from the new validation endpoint,
4. a live admin validation checklist for the final manual WordPress pass.

## Validation Baseline

Focused validation:

```powershell
python -m unittest tests.unit.operator_api.test_app -v
```

Full repository baseline:

```powershell
python -m unittest discover -s tests -v
```

Accepted result:

1. focused operator API suite green at `10` tests,
2. full repository suite green at `227` tests passing.

## Known Limit

This batch improves live-validation support, but it does not replace the final real WordPress-admin test.

The remaining honest gap is still:

1. plugin rendering and behavior must be exercised inside a real WordPress admin session because PHP CLI and an automated WordPress plugin harness are not available in the local repo environment.
