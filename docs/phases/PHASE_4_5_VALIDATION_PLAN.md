# Phase 4.5 Validation Plan

## Purpose

This document defines what must be validated before Phase 4.5 can be treated as complete.

The focus is not new feature coverage.

The focus is live operator readiness.

## Validation Layers

Phase 4.5 validation has four layers:

1. repo baseline validation,
2. local-config validation,
3. live transport validation,
4. canary-chain verification.

Current status:

1. layers 1 and 2 are complete,
2. layer 3 is complete for both transports,
3. layer 4 now reaches live WordPress publication, remote-state reconciliation, and a real Facebook publish attempt,
4. the replacement-canary evidence is recorded in [PHASE_4_5_ACCEPTANCE_BATCH_5.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_5.md),
5. the live WordPress reconciliation plus failed Facebook publish attempt are recorded in [PHASE_4_5_ACCEPTANCE_BATCH_6.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_4_5_ACCEPTANCE_BATCH_6.md),
6. the only remaining blocker is an expired Facebook Page token, not missing system behavior.

Recommended checkpoint command:

```powershell
python src\cli\summarize_system_activation.py --json
```

That command does not replace the detailed validation commands.

It provides the current operator gate summary before and after those commands are run.

## 1. Repo Baseline Validation

The existing repo baseline must still be green before any live activation work is trusted.

Required command:

```powershell
python -m unittest discover -s tests -v
```

Expected result:

1. the current suite remains green,
2. the system is not being activated on top of a broken local baseline.

## 2. Local Config Validation

The operator must confirm that local config files load safely before any execute-mode call is attempted.

Required dry-run commands:

```powershell
python src\cli\validate_wordpress_transport.py --config-path config\wordpress_rest_config.local.json
python src\cli\validate_facebook_transport.py --config-path config\facebook_graph_config.local.json
```

Expected result:

1. config files load,
2. request previews are visible,
3. secrets are not printed,
4. no remote mutation occurs.

## 3. Live Transport Validation

Both transports must be validated with execute-mode read-only checks and audit recording.

Required commands:

```powershell
python src\cli\validate_wordpress_transport.py --config-path config\wordpress_rest_config.local.json --execute --record-audit
python src\cli\validate_facebook_transport.py --config-path config\facebook_graph_config.local.json --execute --record-audit
```

Expected result:

1. WordPress returns the authenticated user identity,
2. Facebook returns the target Page identity,
3. tracking audit records reflect both validation runs,
4. no content is created during this step.

## 4. Canary Chain Verification

One approved draft must be taken through the existing connected workflow.

Minimum canary path:

```powershell
python src\cli\prepare_wordpress_publish.py --draft-id <draft_id> --publish-intent draft
python src\cli\prepare_facebook_package.py --draft-id <draft_id> --blog-publish-id <blog_publish_id>
python src\cli\review_social_package.py --social-package-id <social_package_id> --outcome approved --note "phase_4_5_canary"
python src\cli\prepare_distribution_linkage.py --blog-publish-id <blog_publish_id> --social-package-id <social_package_id>
python src\cli\sync_wordpress_transport.py --blog-publish-id <blog_publish_id> --config-path config\wordpress_rest_config.local.json --execute
```

If the canary continues to a published or scheduled state:

```powershell
python src\cli\reconcile_wordpress_post_state.py --blog-publish-id <blog_publish_id> --config-path config\wordpress_rest_config.local.json --execute
python src\cli\reconcile_wordpress_post_state.py --blog-publish-id <blog_publish_id> --config-path config\wordpress_rest_config.local.json --execute --reconcile-local-state
python src\cli\sync_facebook_transport.py --social-package-id <social_package_id> --action published --config-path config\facebook_graph_config.local.json --execute
```

If the Facebook canary is scheduled instead:

```powershell
python src\cli\reconcile_wordpress_post_state.py --blog-publish-id <blog_publish_id> --config-path config\wordpress_rest_config.local.json --execute --reconcile-local-state --schedule-mode manual
python src\cli\sync_facebook_transport.py --social-package-id <social_package_id> --action scheduled --scheduled-for-facebook <timestamp> --schedule-mode manual --config-path config\facebook_graph_config.local.json --execute
```

Required post-run verification:

```powershell
python src\cli\summarize_distribution_health.py --json
python src\cli\summarize_distribution_schedule.py --json
python src\cli\summarize_publish_chain_history.py --view all --json
python src\cli\summarize_tracking_audit.py --json
```

Expected result:

1. the chain is visible across distribution and tracking views,
2. audit records exist for the deliberate validation activity,
3. the connected workflow remains understandable after live execution,
4. no hidden contract break appears once real config and real transports are involved.

If the Facebook execute step fails because the Page token has expired:

1. refresh the token in `config/facebook_graph_config.local.json`,
2. rerun `validate_facebook_transport.py --execute --record-audit`,
3. retry the same approved canary publish,
4. record the retry outcome in a follow-on Phase 4.5 acceptance batch.

## Required Evidence

Phase 4.5 should not close without:

1. a written activation acceptance batch,
2. the exact commands used,
3. the identities confirmed during validation,
4. the observed end-state of the canary chain,
5. any residual live-environment risks that remain acceptable.
