# Phase 4.9 Plugin Refresh And Live Run

## Purpose

This document gives the exact repeatable path for the first real WordPress-admin validation session.

Use it together with:

1. [APPROVAL_UI_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/APPROVAL_UI_RUNBOOK.md)
2. [PHASE_4_9_LIVE_VALIDATION_WORKSHEET.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_9_LIVE_VALIDATION_WORKSHEET.md)

## 1. Build The Refresh Package

Run this from the repo root:

```powershell
python src\cli\build_wordpress_plugin_package.py
```

Expected result:

1. JSON is printed with `output_path`, `file_count`, `size_bytes`, and `sha256`.
2. The default package is rebuilt at:
   1. [content-ops-approval-ui.zip](C:/Users/Administrator/OneDrive/Documents/co_ma/wordpress-plugin/content-ops-approval-ui.zip)

If you want a throwaway package elsewhere:

```powershell
python src\cli\build_wordpress_plugin_package.py --output-path C:\temp\content-ops-approval-ui.zip
```

## 2. Worker Preflight

Before touching WordPress admin, run:

```powershell
git pull --ff-only origin main
python -m unittest discover -s tests -v
python src\cli\run_operator_api.py
```

Then verify:

```powershell
Invoke-WebRequest http://127.0.0.1:8765/healthz | Select-Object -ExpandProperty Content
```

Record the exact commit and package hash in the worksheet session header.

## 3. Refresh The Plugin In WordPress

Recommended refresh path:

1. open `wp-admin/plugin-install.php?tab=upload`
2. click `Choose File`
3. select:
   1. [content-ops-approval-ui.zip](C:/Users/Administrator/OneDrive/Documents/co_ma/wordpress-plugin/content-ops-approval-ui.zip)
4. click `Install Now`
5. if WordPress shows the replace flow, choose the option that replaces the existing plugin with the uploaded package
6. return to `wp-admin/plugins.php`
7. confirm `Content Ops Approval` is still present and active

If plugin upload is disabled in that environment, use the fallback file-sync path:

1. replace `wp-content/plugins/content-ops-approval-ui/` with the contents of:
   1. [content-ops-approval-ui](C:/Users/Administrator/OneDrive/Documents/co_ma/wordpress-plugin/content-ops-approval-ui)
2. reload `wp-admin/plugins.php`
3. confirm the plugin remains active

## 4. Configure The Plugin

Open:

1. `wp-admin/admin.php?page=content-ops-approval-settings`

Enter:

1. the real Operator API base URL
2. the shared secret from the worker config

Rule:

1. use `http://127.0.0.1:8765` only when WordPress and the operator API run on the same machine
2. for hosted WordPress, use the reachable HTTPS reverse-proxy hostname instead

## 5. Execute The Admin Pages In Order

Run the session in this exact order:

1. `wp-admin/admin.php?page=content-ops-approval-validation`
2. `wp-admin/admin.php?page=content-ops-approval-dashboard`
3. `wp-admin/admin.php?page=content-ops-approval-drafts`
4. `wp-admin/admin.php?page=content-ops-approval-social`
5. `wp-admin/admin.php?page=content-ops-approval-media`
6. `wp-admin/admin.php?page=content-ops-approval-queue`
7. `wp-admin/admin.php?page=content-ops-approval-settings`

At each step, use the exact entity IDs already recorded in:

1. [PHASE_4_9_LIVE_VALIDATION_WORKSHEET.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_9_LIVE_VALIDATION_WORKSHEET.md)

## 6. Exact Review Actions

Use the worksheet IDs and perform these actions in order:

1. Draft A: open detail, switch headline variant, approve
2. Draft B: mark `needs_edits` with one actionable note
3. Social Package A: open detail, switch to `manual_validation_alt_v1`, approve
4. Media Asset A: open detail, confirm provenance and linkage, approve or mark `needs_edits`
5. Queue Item A: `hold` with note
6. Queue Item B: `removed` with note
7. Queue Item C: approve first, then schedule from detail
8. Queue Item D: confirm the blocked approve reason is visible and no false approve path appears
9. Settings: temporarily break the shared secret, confirm a safe admin error, then restore the correct secret

## 7. Evidence To Capture

Capture these before ending the session:

1. package build JSON output
2. Validation page screenshot
3. Dashboard screenshot
4. Draft A result
5. Draft B result
6. Social Package A result
7. Media Asset A result
8. Queue hold result
9. Queue remove result
10. Queue schedule result
11. blocked-approve result
12. safe failure-notice result

## 8. After The Session

If the session passes:

1. write the first real live validation batch for Phase 4.9
2. include the commit, package hash, and exact IDs used
3. attach or summarize the captured evidence

If the session fails:

1. stop at the first failing step
2. record the page URL, entity ID, and on-screen error
3. classify the failure as plugin rendering, API auth, topology, runtime state, or workflow mismatch
