# Content Ops Approval UI

This plugin is the first WordPress admin shell for the Content Ops approval workflow.

It is intentionally thin:

1. it renders review screens in WordPress admin,
2. it calls the private operator API on the repo worker,
3. it does not become the workflow source of truth.

## Setup

1. Copy this folder into `wp-content/plugins/`.
2. Activate the plugin in WordPress admin.
3. Open `Content Ops Approval > Settings`.
4. Enter:
   - Operator API base URL
   - shared secret matching the repo worker operator API

## Required backend

Run the internal operator API from the repo worker:

```powershell
python src\cli\run_operator_api.py
```

The plugin expects the operator API shared secret to match the WordPress plugin settings.
