# Phase 4.9 Live Validation Worksheet

## Purpose

This worksheet turns the final WordPress-admin validation pass into one controlled session.

Use it when we are ready to prove that the approval shell works end to end in a real WordPress admin environment.

## Session Header

Fill these before starting:

1. Date:
2. Operator:
3. WordPress site:
4. WordPress admin user:
5. Operator API base URL:
6. Repo commit:
7. Plugin version folder refreshed: `yes/no`

## Pass Rule

The session passes only if:

1. the plugin loads cleanly in real WordPress admin,
2. draft, social, media, and queue review actions all succeed,
3. one schedule action succeeds for an eligible blog queue item,
4. one blocked queue item clearly shows a block reason,
5. one intentional auth/config break produces a safe admin notice,
6. the plugin remains a review shell and does not bypass repo-side workflow rules.

## Stop Conditions

Stop the session and record failure immediately if:

1. the plugin activates with a fatal error,
2. the Validation page does not load,
3. any review action returns a blank page or fatal admin response,
4. queue scheduling works when the backend says it should be blocked,
5. a content-changing selection fails to reopen review safely,
6. the plugin appears to store authoritative workflow state in WordPress instead of the repo runtime.

## Preflight Commands

Run these on the worker host before touching WordPress admin.

### 1. Sync the repo

```powershell
git pull --ff-only origin main
git rev-parse HEAD
```

Record the commit in the Session Header.

### 2. Run the Python baseline

```powershell
python -m unittest discover -s tests -v
```

Expected result:

1. the suite is green,
2. there are no local code surprises before live validation.

### 3. Start the operator API

```powershell
python src\cli\run_operator_api.py
```

If WordPress is hosted elsewhere, use the real HTTPS hostname from the reverse proxy instead of localhost in the next checks.

### 4. Check API health

```powershell
Invoke-WebRequest http://127.0.0.1:8765/healthz | Select-Object -ExpandProperty Content
```

Expected result:

1. JSON with `"status": "ok"`.

### 5. Check operator validation payload

Replace the secret first:

```powershell
$secret = 'REPLACE_WITH_SHARED_SECRET'
$headers = @{ 'X-Content-Ops-Shared-Secret' = $secret }
Invoke-RestMethod http://127.0.0.1:8765/validation/operator-baseline -Headers $headers | ConvertTo-Json -Depth 6
```

Expected result:

1. `status` is `ready_for_live_plugin_validation`,
2. endpoint checks are all `ok`,
3. `media_review_available` is `true`.

## Minimum Data Set

Do not start the admin session until these exist.

Prepared local validation set as of `2026-04-08`:

1. Draft A for approve plus headline-variant test: `draft-0637ac87046e-20260402T223513Z-f74c7982`
2. Draft B for needs-edits test: `draft-5d1d078eb1ee-20260402T223503Z-1d67fdad`
3. Social Package A for approve plus variant test: `social-draft-0637ac-20260404T202714.535914+0000-6516d378`
4. Media Asset A for review test: `asset-draft-0637ac-20260408T213923.498938+0000-29e0cc39`
5. Queue Item A for hold test: `fbq-blog-draft-0-20260404T201852.612031+0000-10b30437`
6. Queue Item B for remove test: `blogq-blog-draft-0-20260404T211633.540445+0000-1ebd20ce`
7. Queue Item C for schedule test: `blogq-blog-draft-0-20260404T201852.612031+0000-eb30dd5f`
8. Queue Item D for blocked-approve test: `fbq-blog-draft-0-20260404T211633.540445+0000-c3b3866f`

If any of these are missing, stop and seed runtime data first.

Operator note:

1. Queue Item C is the blog queue row that should be approved first and then scheduled from its detail screen.
2. Social Package A now includes `deterministic_primary_v1` and `manual_validation_alt_v1`, so the variant-switch path can be exercised safely.
3. Media Asset A is a review-only placeholder asset linked to the Costco canary chain and should not be treated as production creative.

## Plugin Refresh

### 1. Build the refresh package on the worker host

```powershell
python src\cli\build_wordpress_plugin_package.py
```

Preferred package:

1. [content-ops-approval-ui.zip](C:/Users/Administrator/OneDrive/Documents/co_ma/wordpress-plugin/content-ops-approval-ui.zip)

Fallback unpacked source:

1. [content-ops-approval-ui](C:/Users/Administrator/OneDrive/Documents/co_ma/wordpress-plugin/content-ops-approval-ui)

### 2. Refresh plugin files on the WordPress host

Preferred path:

1. upload the rebuilt zip in WordPress admin and replace the existing plugin

Fallback path:

1. copy the unpacked folder into:

1. `wp-content/plugins/content-ops-approval-ui/`

### 3. Activate or refresh the plugin

Open:

1. `wp-admin/plugins.php`

Expected result:

1. plugin activates with no fatal error,
2. `Content Ops Approval` appears in the admin menu.

## Exact Admin Sequence

Run the pages in this order.

### 1. Settings

Open:

1. `wp-admin/admin.php?page=content-ops-approval-settings`

Actions:

1. enter the Operator API base URL,
2. enter the shared secret,
3. save.

Expected result:

1. settings save cleanly,
2. no warning appears unless the topology is actually wrong,
3. if WordPress is hosted elsewhere, localhost is flagged as a bad choice.

Evidence:

1. screenshot of saved settings page,
2. note the exact base URL used.

### 2. Validation

Open:

1. `wp-admin/admin.php?page=content-ops-approval-validation`

Expected result:

1. page loads,
2. local checks are populated,
3. backend snapshot shows draft, social, media, and queue rows,
4. endpoint checks include:
   1. `dashboard_summary`
   2. `drafts_inbox`
   3. `social_packages_inbox`
   4. `media_assets_inbox`
   5. `queue_inbox`
   6. `combined_health`

Evidence:

1. screenshot of the full Validation page.

### 3. Dashboard

Open:

1. `wp-admin/admin.php?page=content-ops-approval-dashboard`

Expected result:

1. dashboard cards render for draft, social, media, queue, and transport,
2. recent activity renders,
3. current alerts render,
4. priority lists render,
5. media priority items link into media detail screens,
6. fast-lane card stays visible but disabled.

Evidence:

1. screenshot of dashboard top section,
2. screenshot of one priority list row with a working link target.

### 4. Draft Review

Open:

1. `wp-admin/admin.php?page=content-ops-approval-drafts`

Actions:

1. filter to the Draft A and Draft B candidates,
2. open Draft A detail,
3. if a second headline variant is available, switch to it,
4. approve Draft A,
5. go back to the inbox and confirm filter state still makes sense,
6. mark Draft B as `needs_edits` with a short actionable note.

Expected result:

1. success notices appear,
2. Draft A shows updated approval history,
3. Draft A variant change reopens review safely before approval,
4. Draft B requires and stores an actionable note,
5. inbox context survives detail navigation.

Evidence:

1. screenshot of Draft A success notice,
2. screenshot of Draft A approval history,
3. screenshot of Draft B needs-edits result.

### 5. Social Review

Open:

1. `wp-admin/admin.php?page=content-ops-approval-social`

Actions:

1. filter to Social Package A,
2. open detail,
3. switch to another prepared variant if available,
4. approve the package.

Expected result:

1. success notice appears,
2. selected variant updates,
3. review reopens safely before final approval,
4. linked draft context and AI provenance remain read-only.

Evidence:

1. screenshot of selected variant on detail,
2. screenshot of success notice,
3. screenshot of approval history.

### 6. Media Review

Open:

1. `wp-admin/admin.php?page=content-ops-approval-media`

Actions:

1. filter to Media Asset A,
2. open detail,
3. confirm provenance, alt text, media-brief context, and linkage,
4. approve the asset or mark it `needs_edits` with an actionable note.

Expected result:

1. success notice appears,
2. review history updates,
3. linkage back to draft or social detail works,
4. media review stays review-only and does not expose upload or generation controls.

Evidence:

1. screenshot of media detail,
2. screenshot of success notice,
3. screenshot of media approval history.

### 7. Queue Review

Open:

1. `wp-admin/admin.php?page=content-ops-approval-queue`

Actions:

1. use Queue Item A to test `hold`,
2. use Queue Item B to test `removed`,
3. use Queue Item C to open detail and set a schedule,
4. use Queue Item D to confirm the approve block reason is visible and no false action path is offered.

Expected result:

1. hold action succeeds with note,
2. remove action succeeds with note,
3. schedule action succeeds only on the schedule-eligible blog item,
4. blocked item clearly shows why approve is unavailable,
5. linked mapping and linked asset context are visible on detail.

Evidence:

1. screenshot of hold result,
2. screenshot of remove result,
3. screenshot of successful schedule result,
4. screenshot of blocked approve reason.

### 8. Safe Failure Notice Test

Run this only after all successful-path checks are done.

Open:

1. `wp-admin/admin.php?page=content-ops-approval-settings`

Actions:

1. temporarily change the shared secret to a wrong value,
2. open Dashboard,
3. confirm a safe admin error is shown,
4. restore the correct secret,
5. reload Dashboard and confirm recovery.

Expected result:

1. no blank page,
2. no fatal error,
3. no silent failure,
4. normal behavior returns after the correct secret is restored.

Evidence:

1. screenshot of the safe admin error,
2. screenshot of the restored working dashboard.

## Evidence Bundle

Collect these before ending the session:

1. Validation page screenshot,
2. Dashboard screenshot,
3. Draft A approve evidence,
4. Draft B needs-edits evidence,
5. Social Package A approve evidence,
6. Media Asset A review evidence,
7. Queue hold evidence,
8. Queue remove evidence,
9. Queue schedule evidence,
10. blocked queue evidence,
11. safe failure-notice evidence,
12. exact IDs used in the session.

## Outcome Log

Fill this during the session:

1. Validation page: `pass/fail`
2. Dashboard page: `pass/fail`
3. Draft approve path: `pass/fail`
4. Draft needs-edits path: `pass/fail`
5. Social approve path: `pass/fail`
6. Media review path: `pass/fail`
7. Queue hold path: `pass/fail`
8. Queue remove path: `pass/fail`
9. Queue schedule path: `pass/fail`
10. Blocked queue visibility: `pass/fail`
11. Safe failure notice path: `pass/fail`
12. Overall session: `pass/fail`

## After The Session

If the session passes:

1. write the first real live validation batch for Phase 4.9,
2. include the exact IDs used,
3. include screenshots or notes for each evidence item,
4. close the remaining Phase 4.9 validation gap.

If the session fails:

1. record the exact failing step,
2. record the page URL,
3. record the affected entity ID,
4. record the on-screen error,
5. record whether the failure was plugin rendering, API auth, runtime state, or operator-flow mismatch,
6. fix that issue before attempting another live session.
