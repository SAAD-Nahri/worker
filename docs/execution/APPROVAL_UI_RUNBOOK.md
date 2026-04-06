# Approval UI Runbook

## Purpose

This runbook explains how to operate the first approval UI baseline.

The goal is to let the operator review drafts, social packages, and queue items from WordPress admin while preserving the repo runtime as the source of truth.

## Core Rule

The approval UI is a shell over the repo runtime.

Do not:

1. treat the plugin as the workflow engine,
2. bypass the operator API,
3. store approval decisions outside the append-only runtime records,
4. confuse review actions with transport execution.

## Prerequisites

Before using the approval UI, make sure:

1. the Python repo is available on the worker machine,
2. the operator API config exists at `config/operator_api.local.json`,
3. the shared secret is set,
4. WordPress admin is available,
5. the plugin files are present under `wp-content/plugins/content-ops-approval-ui/`.

## Operator API Setup

### 1. Create local config

Copy the example:

```powershell
Copy-Item config\operator_api_config.example.json config\operator_api.local.json
```

Fill in:

1. `bind_host`
2. `bind_port`
3. `shared_secret`
4. `enable_docs`

### 2. Start the API

```powershell
python src\cli\run_operator_api.py
```

The default local base URL is:

1. `http://127.0.0.1:8765`

For local development on Windows, you can also use:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_operator_api.ps1
```

Important:

1. `127.0.0.1` is correct only when WordPress can reach the operator API on the same machine,
2. if WordPress is hosted elsewhere, the plugin must use a reachable HTTPS operator-API URL instead of localhost,
3. example reverse-proxy baselines live in [deploy/nginx/content-ops-operator-api.nginx.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/nginx/content-ops-operator-api.nginx.example) and [deploy/caddy/content-ops-operator-api.Caddyfile.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/caddy/content-ops-operator-api.Caddyfile.example).

## Plugin Setup

### 1. Install

Copy:

1. [wordpress-plugin/content-ops-approval-ui](C:/Users/Administrator/OneDrive/Documents/co_ma/wordpress-plugin/content-ops-approval-ui)

into:

1. `wp-content/plugins/content-ops-approval-ui/`

### 2. Activate

Activate the plugin from WordPress admin.

### 3. Configure

Open:

1. `Content Ops Approval > Settings`

Set:

1. Operator API base URL
2. Shared secret

Topology rule:

1. `http://127.0.0.1:8765` is only valid when WordPress and the operator API run on the same machine,
2. for a hosted WordPress site, use the reachable HTTPS hostname from the reverse proxy instead.

### 4. Validate

Open:

1. `Content Ops Approval > Validation`

Use that page to confirm:

1. the current WordPress user has review capability,
2. the plugin sees API base URL and shared secret values,
3. the Operator API base URL classification makes sense for the real deployment topology,
4. the operator API responds to the dedicated validation endpoint,
5. dashboard, inbox, queue, and combined-health backend checks are all green,
6. the manual final admin checklist is visible before live closeout.

## Normal Review Flow

### 1. Dashboard

Start at the dashboard to check:

1. pending draft review,
2. pending social review,
3. queue-ready items,
4. transport or activation failures,
5. recent review activity,
6. current alerts,
7. direct links from recent activity and resolvable alerts into the relevant detail screens.

### 2. Draft Review

Use the Draft Review page to:

1. open one draft,
2. inspect preview plus source lineage and downstream linkage,
3. approve,
4. mark needs edits,
5. reject with review note when needed.

### 3. Social Review

Use the Social Review page to:

1. inspect hook, caption, and comment CTA,
2. confirm blog linkage and linked draft context,
3. approve,
4. request edits,
5. reject if not publishable.

### 4. Queue Review

Use the Queue Review page to:

1. approve items for queue,
2. hold items with actionable note,
3. remove items from the current batch with an explicit note,
4. set blog schedule only when the queue item is actually eligible,
5. inspect collision warnings before scheduling,
6. read the approve block reason when failed queue items are not yet eligible,
7. read the schedule block reason when scheduling is not yet available,
8. inspect linked mapping outputs before final queue decisions.

## Important V1 Boundaries

The approval UI currently supports:

1. draft review,
2. social package review,
3. queue review,
4. blog queue scheduling,
5. combined health visibility.

It does not yet replace:

1. WordPress transport execution,
2. Facebook transport execution,
3. media review,
4. analytics workflows,
5. future fast-lane approval.

## Recommended Validation Commands

Backend validation:

```powershell
python -m unittest tests.unit.operator_api.test_app tests.unit.distribution_engine.test_queue_review -v
```

Full Python baseline:

```powershell
python -m unittest discover -s tests -v
```

## Manual Validation Checklist

Use a real WordPress admin environment to verify:

1. the plugin activates cleanly,
2. settings save correctly,
3. the Validation page loads and backend checks are green,
4. dashboard loads from the operator API,
5. draft review actions append runtime state correctly,
6. social review actions append runtime state correctly,
7. queue review and scheduling actions behave correctly,
8. API auth failures surface as safe admin notices.

## Known Limits

1. The plugin is implemented but not PHP-linted in the local repo environment because PHP CLI is not available here.
2. Fast-lane UI is intentionally visible but disabled.
3. Queue scheduling through the UI is limited to blog queue items in V1.
4. Transport actions remain outside this approval shell.
