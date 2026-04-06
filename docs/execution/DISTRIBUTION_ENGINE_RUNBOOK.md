# Distribution Engine Runbook

## Purpose

This runbook defines the normal operator workflow for the current Phase 3 distribution baseline.

The goal is to keep blog publishing, Facebook packaging, queue movement, transport actions, and health review understandable by one person.

## Core Rule

Phase 3 is append-only and review-first.

Do not:

1. bypass the approved draft,
2. bypass social package review,
3. bypass dry-run transport previews,
4. treat queue and mapping state as optional.

## Current Runtime Inputs

This runbook assumes:

1. a Phase 2 draft exists,
2. the latest draft is approved,
3. runtime files in [data/README.md](C:/Users/Administrator/OneDrive/Documents/co_ma/data/README.md) are available,
4. operator credentials or config files are only used when transport preview or execution is intentional.

## Recommended Operator Flow

### 0. Validate Transport Configs Before Live Use

Preview the validation request without mutating external systems:

```powershell
python src\cli\validate_wordpress_transport.py --config-path <wordpress_rest_config.json>
python src\cli\validate_facebook_transport.py --config-path <facebook_graph_config.json>
```

Execute the read-only remote checks only when you are intentionally validating live credentials:

```powershell
python src\cli\validate_wordpress_transport.py --config-path <wordpress_rest_config.json> --execute
python src\cli\validate_facebook_transport.py --config-path <facebook_graph_config.json> --execute
```

### 1. Prepare The WordPress Publish Record

Create the local WordPress-ready payload:

```powershell
python src\cli\prepare_wordpress_publish.py --draft-id <draft_id> --publish-intent draft
```

For items expected to be scheduled later:

```powershell
python src\cli\prepare_wordpress_publish.py --draft-id <draft_id> --publish-intent schedule
```

### 2. Prepare The Facebook Package

Create the first local Facebook package from the same approved draft:

```powershell
python src\cli\prepare_facebook_package.py --draft-id <draft_id> --blog-publish-id <blog_publish_id>
```

### 3. Review The Social Package

Keep the package review visible:

```powershell
python src\cli\review_social_package.py --social-package-id <social_package_id> --outcome approved --note "hook_matches_blog"
```

Use `needs_edits` or `rejected` when the package is not ready.

### 4. Prepare Queue And Mapping Snapshots

Refresh queue and mapping state for the selected publish chain:

```powershell
python src\cli\prepare_distribution_linkage.py --blog-publish-id <blog_publish_id> --social-package-id <social_package_id>
```

### 5. Preview WordPress Transport

Dry-run is the default:

```powershell
python src\cli\sync_wordpress_transport.py --blog-publish-id <blog_publish_id> --config-path <wordpress_rest_config.json>
```

Execute only when the preview looks correct:

```powershell
python src\cli\sync_wordpress_transport.py --blog-publish-id <blog_publish_id> --config-path <wordpress_rest_config.json> --execute
```

If transient failures are likely, use the bounded retry controls explicitly:

```powershell
python src\cli\sync_wordpress_transport.py --blog-publish-id <blog_publish_id> --config-path <wordpress_rest_config.json> --execute --max-attempts 3 --initial-delay-seconds 1.0 --backoff-multiplier 2.0
```

### 6. Record WordPress Schedule Or Publish State

Schedule:

```powershell
python src\cli\record_wordpress_publish_update.py --blog-publish-id <blog_publish_id> --action scheduled --wordpress-post-id <post_id> --schedule-mode manual --scheduled-for-blog <timestamp>
```

Publish:

```powershell
python src\cli\record_wordpress_publish_update.py --blog-publish-id <blog_publish_id> --action published --wordpress-post-id <post_id> --wordpress-post-url <post_url> --published-at-blog <timestamp>
```

### 7. Preview Or Execute Facebook Transport

Dry-run preview:

```powershell
python src\cli\sync_facebook_transport.py --social-package-id <social_package_id> --action published --config-path <facebook_graph_config.json>
```

Scheduled preview:

```powershell
python src\cli\sync_facebook_transport.py --social-package-id <social_package_id> --action scheduled --scheduled-for-facebook <timestamp> --schedule-mode manual --config-path <facebook_graph_config.json>
```

Execute only when the linked blog state already allows it:

```powershell
python src\cli\sync_facebook_transport.py --social-package-id <social_package_id> --action scheduled --scheduled-for-facebook <timestamp> --schedule-mode manual --config-path <facebook_graph_config.json> --execute
```

If transient failures are likely, use the bounded retry controls explicitly:

```powershell
python src\cli\sync_facebook_transport.py --social-package-id <social_package_id> --action scheduled --scheduled-for-facebook <timestamp> --schedule-mode manual --config-path <facebook_graph_config.json> --execute --max-attempts 3 --initial-delay-seconds 1.0 --backoff-multiplier 2.0
```

### 8. Review Distribution Health

Read the latest operator summary:

```powershell
python src\cli\summarize_distribution_health.py
```

Machine-readable output:

```powershell
python src\cli\summarize_distribution_health.py --json
```

### 9. Review Distribution Schedule Planning

Read the scheduling view when deciding what should be queued, scheduled, or held:

```powershell
python src\cli\summarize_distribution_schedule.py
```

Machine-readable output:

```powershell
python src\cli\summarize_distribution_schedule.py --json
```

## What To Check In The Health Summary

The current health summary is the operator checkpoint for:

1. missing queue or mapping state,
2. schedule collisions,
3. blog publish failures,
4. Facebook publish failures,
5. approved social packages that are stuck,
6. published chains missing final identifiers or URLs.

The schedule report is the operator checkpoint for:

1. blog chains ready for blog scheduling,
2. chains waiting on Facebook scheduling,
3. already scheduled pairs,
4. rows that should be reviewed because of schedule alerts.

## Current High-Signal Operator Alerts

Treat these as review-worthy:

1. `blog_publish_failed`
2. `facebook_publish_failed`
3. `state_incomplete`
4. any non-empty `consistency_issues`
5. any non-empty `schedule_alerts`

## Intentional Limits

This runbook does not yet cover:

1. Facebook comment CTA auto-posting,
2. live retry tuning from real production evidence,
3. visual schedule slot optimization beyond the current CLI report,
4. multi-page or multi-channel publishing,
5. Phase 4 performance tracking.

## Validation Commands

Focused Phase 3 health validation:

```powershell
python -m unittest tests.unit.distribution_engine.test_health tests.unit.distribution_engine.test_health_cli -v
```

Focused transport and schedule validation:

```powershell
python -m unittest tests.unit.distribution_engine.test_wordpress_transport tests.unit.distribution_engine.test_facebook_transport tests.unit.distribution_engine.test_wordpress_validation_cli tests.unit.distribution_engine.test_facebook_validation_cli tests.unit.distribution_engine.test_transport_retry tests.unit.distribution_engine.test_schedule_report tests.unit.distribution_engine.test_schedule_cli -v
```

Full repo baseline:

```powershell
python -m unittest discover -s tests -v
```
