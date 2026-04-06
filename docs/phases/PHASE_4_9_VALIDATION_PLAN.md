# Phase 4.9 Validation Plan

## Purpose

This plan defines how to validate that the Approval UI and Operator Console are good enough for the solo-operator workflow.

The validation target is not visual polish. It is:

1. correct runtime reads,
2. correct append-only review writes,
3. safe plugin-to-backend auth,
4. usable operator review flow.

## Validation Questions

Phase 4.9 should answer:

1. can the operator API expose current runtime state correctly,
2. do review actions use the same underlying logic as the CLI paths,
3. does the dashboard surface recent review and alert context instead of counts alone,
4. does the plugin fail safely when backend auth or connectivity fails,
5. does the UI preserve the existing approval boundaries,
6. does the queue UI hide blocked review actions and explain why,
7. can the dashboard move the operator into the correct detail screen without guesswork,
8. does the dedicated Validation page make live admin verification easier and less error-prone,
9. does the plugin warn clearly when the configured Operator API URL is only locally reachable and therefore unusable from hosted WordPress.

## Required Validation Baseline

### 1. Repository baseline

```powershell
python -m unittest discover -s tests -v
```

### 2. Focused backend approval-UI baseline

```powershell
python -m unittest tests.unit.operator_api.test_app tests.unit.distribution_engine.test_queue_review -v
```

### 3. Manual WordPress validation

Because the local repo environment does not currently include PHP CLI or a WordPress plugin harness, Phase 4.9 still requires live admin validation covering:

1. plugin activation,
2. settings save path,
3. validation-page load,
4. dashboard load,
5. draft review submission,
6. social review submission,
7. queue review submission,
8. blog queue schedule submission,
9. safe admin-notice display on backend failure.

### 4. Acceptance scenarios

Before closeout, one live admin session should prove:

1. one draft can be approved from the plugin,
2. one draft can be marked `needs_edits` with note,
3. one social package can be approved,
4. one queue item can be held,
5. one queue item can be removed from the current batch,
6. one blog queue item can be scheduled,
7. one failed queue item shows an approve block reason instead of a false action path,
8. dashboard activity and alert links open the correct review detail screen,
9. the Validation page shows green backend checks before manual review begins,
10. fast-lane UI stays visible but disabled,
11. runtime history still shows the decision trail afterward,
12. hosted WordPress deployments do not rely on accidental localhost assumptions.

## Acceptance Evidence

Before Phase 4.9 closes, the repo should contain:

1. at least one acceptance batch for the implemented backend/plugin baseline,
2. at least one later batch for real WordPress-admin validation,
3. updated TODO and Phase 5 gate reflecting that the operator console is now a prerequisite for later decision and autoapproval work.

## Failure Conditions

Phase 4.9 should remain open if any of the following are still true:

1. the plugin has never been exercised in a real WordPress admin environment,
2. review actions in the UI do not match CLI-backed workflow behavior,
3. queue scheduling bypasses current publish-state contracts,
4. the plugin stores mirrored approval state as authoritative data,
5. fast-lane behavior becomes active before Phase 5.5.
