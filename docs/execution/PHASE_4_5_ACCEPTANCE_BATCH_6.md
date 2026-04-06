# Phase 4.5 Acceptance Batch 6

## Purpose

Record the first real remote-state reconciliation pass for the replacement canary and the first live Facebook publish attempt against the owned Page.

## Commands Run

```powershell
python -m unittest discover -s tests -v
python src\cli\reconcile_wordpress_post_state.py --blog-publish-id blog-draft-0637ac-20260404T202650.440295+0000-e4f08c4c --config-path config\wordpress_rest_config.local.json --execute
python src\cli\reconcile_wordpress_post_state.py --blog-publish-id blog-draft-0637ac-20260404T202650.440295+0000-e4f08c4c --config-path config\wordpress_rest_config.local.json --execute --reconcile-local-state
python src\cli\sync_facebook_transport.py --social-package-id social-draft-0637ac-20260404T202714.535914+0000-6516d378 --action published --config-path config\facebook_graph_config.local.json
python src\cli\sync_facebook_transport.py --social-package-id social-draft-0637ac-20260404T202714.535914+0000-6516d378 --action published --config-path config\facebook_graph_config.local.json --execute
python src\cli\summarize_distribution_health.py --json
python src\cli\summarize_publish_chain_history.py --view all --json
python src\cli\summarize_system_activation.py --json
```

## Observed Results

### Repo Baseline

1. `python -m unittest discover -s tests -v` passed with `214` tests.

### WordPress Remote State

1. Remote inspection of WordPress post `25` succeeded.
2. The remote state was:
   1. `remote_status = publish`
   2. `remote_slug = how-to-give-your-costco-croissant-container-a-second-life-2`
   3. `remote_title = How To Give Your Costco Croissant Container A Second Life`
   4. `remote_published_at = 2026-04-04T21:05:25+00:00`
   5. `remote_post_url = https://kuchniatwist.pl/2026/04/04/how-to-give-your-costco-croissant-container-a-second-life-2/`
3. Local reconciliation succeeded.
4. The replacement canary chain is now locally recorded as:
   1. `wordpress_status = published`
   2. `blog_queue_state = published_blog`
   3. `facebook_queue_state = approved_for_queue`
   4. `mapping_status = packaged_social_pending`

### Facebook Canary

1. The dry-run Facebook publish preview was clean.
2. The execute-mode Facebook publish attempt reached the platform boundary and failed with HTTP `401`.
3. The returned Facebook error was an expired Page access token:
   1. OAuth error code `190`
   2. subcode `463`
4. The failure was preserved append-only as:
   1. `facebook_publish_id = fbpub-social-draft-20260404T211633.535596+0000-4eeb3536`
   2. `publish_status = failed`
   3. `facebook_queue_state = facebook_publish_failed`
   4. `mapping_status = social_publish_failed`

## Reporting Snapshot

### Distribution Health

The replacement canary now appears as:

1. `wordpress_status = published`
2. `blog_queue_state = published_blog`
3. `facebook_publish_status = failed`
4. `operator_signal = facebook_publish_failed`

### Publish Chain History

The replacement canary now appears as:

1. `chain_status = facebook_publish_failed`
2. `publish_intent = publish_now`
3. `published_at_blog = 2026-04-04T21:05:25+00:00`
4. the approved social package and selected copy remain visible
5. the failure reason is preserved in `last_facebook_publish_error`

## Decision

This batch proves:

1. the replacement canary is genuinely live on WordPress,
2. the repo can reconcile real remote WordPress state back into append-only local records,
3. the Facebook publish path itself is operational up to live credential validity,
4. the current blocker is not system architecture and not transport code.

The remaining Phase 4.5 blocker is:

1. refresh the expired Facebook Page access token,
2. rerun execute-mode Facebook validation,
3. retry the same approved replacement canary publish.
