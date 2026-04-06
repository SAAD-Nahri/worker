# WordPress Admin Approval Plugin V1

## Purpose

This spec defines the first WordPress admin plugin used as the operator-facing approval shell.

The plugin exists to give the solo operator one familiar review surface inside WordPress admin while leaving the repo runtime as the real workflow engine.

## Core Rule

The plugin is a thin review shell.

It may:

1. render operator pages,
2. collect review notes and actions,
3. call the internal operator API,
4. surface workflow and transport context.

It must not:

1. become the workflow source of truth,
2. mirror approval state as authoritative WordPress data,
3. act like a full editorial CMS,
4. publish directly outside the repo audit path.

## Implementation Shape

The plugin lives at:

1. [wordpress-plugin/content-ops-approval-ui](C:/Users/Administrator/OneDrive/Documents/co_ma/wordpress-plugin/content-ops-approval-ui)

The current implementation is a PHP WordPress admin plugin with:

1. one top-level admin menu,
2. dashboard page,
3. draft review page,
4. social review page,
5. queue review page,
6. validation page,
7. settings page,
8. server-side HTTP calls to the internal operator API.

## Operator-Facing Pages

### Dashboard

Shows:

1. draft counts,
2. social review counts,
3. queue counts,
4. transport and activation signals,
5. recent review activity,
6. current alerts,
7. fast-lane placeholder card,
8. deep links from review activity and resolvable alerts into the relevant detail screens.

### Draft Review

Provides:

1. draft inbox rows,
2. draft detail screen,
3. approve / needs-edits / reject actions,
4. review-note capture,
5. review-history visibility,
6. source-lineage context,
7. headline-suggestion visibility.

### Social Review

Provides:

1. social package inbox rows,
2. social package detail screen,
3. approve / needs-edits / reject actions,
4. review-note capture,
5. linked blog preview,
6. linked draft context.

### Queue Review

Provides:

1. queue inbox rows,
2. queue detail screen,
3. approve / hold / remove actions,
4. conditional blog schedule form for eligible blog queue items,
5. schedule-alert visibility,
6. schedule block reasons when direct scheduling is not yet allowed,
7. approve block reasons when failed queue items are not yet eligible for approval,
8. mapping and selected-output context on the detail screen.

### Validation

Provides:

1. local config and capability checks,
2. operator-API connectivity and endpoint-check visibility,
3. one backend-readiness snapshot for the approval shell,
4. one operator-API reachability classification so localhost mistakes are visible early,
5. a manual live-admin checklist for the final WordPress validation pass.

### Settings

Stores:

1. operator API base URL,
2. shared secret.

The settings page should explicitly warn when the base URL is:

1. missing,
2. invalid,
3. localhost-only,
4. internal-network-only,
5. remote but not HTTPS.

## Capability Model

The plugin currently uses:

1. `edit_others_posts` for review pages,
2. `manage_options` for settings.

This keeps the v1 shell admin-only and review-focused.

## Backend Link

The plugin talks to the internal operator API through:

1. `wp_remote_request`
2. shared-secret header authentication

Required request header:

1. `X-Content-Ops-Shared-Secret`

## Settings And Configuration

The plugin can be configured through:

1. the WordPress admin settings page,
2. optional constants for locked production settings.

Current supported constants:

1. `CONTENT_OPS_APPROVAL_UI_API_BASE_URL`
2. `CONTENT_OPS_APPROVAL_UI_SHARED_SECRET`

## Data Rule

The plugin should not store mirrored workflow state.

Permitted local WordPress storage:

1. plugin settings,
2. short-lived admin notices or cache/transients if needed,
3. standard WordPress nonce/capability state.

The plugin must not assume that `127.0.0.1` is usable from hosted WordPress.

If WordPress is hosted elsewhere, the plugin must point to a reachable HTTPS operator-API hostname, typically exposed through a reverse proxy on the worker host.

Not permitted as authoritative workflow storage:

1. post meta copies of approval state,
2. plugin-owned workflow tables,
3. approval history duplicated into WordPress as the source of truth.

## Review-State Rule

The plugin must respect the current workflow boundaries:

1. draft review is separate from social review,
2. social review is separate from queue review,
3. queue review is separate from transport execution,
4. content-affecting edits must still reopen review through repo-side logic,
5. no silent bypass of human approval is allowed.

## Fast-Lane Rule

The plugin should already show that a future fast lane exists conceptually, but it must remain non-operative.

The UI should:

1. show disabled placeholder status,
2. show that autoapproval is not active,
3. avoid any live automatic-review behavior.

## Validation Reality

The repo currently validates the Python backend thoroughly through the Python test suite.

The plugin itself still requires live WordPress-admin validation because:

1. PHP CLI linting is not available in the local repo environment,
2. no automated WordPress plugin test harness is currently in place.

That means the plugin should be treated as:

1. implemented,
2. reviewable,
3. installable,
4. self-checkable through its validation page,
5. still awaiting real admin-environment validation.

## V1 Limits

The plugin does not yet:

1. provide a full article editor,
2. manage assets,
3. expose analytics dashboards,
4. manage autoapproval or shadow mode,
5. replace the transport runbooks.
