# System Activation Runbook

## Purpose

This runbook defines the first real operator activation path for the whole system.

It is the practical bridge between:

1. a locally validated repo baseline,
2. and a real owned-environment canary run.

## Core Rule

Activation must stay:

1. canary-first,
2. dry-run-first,
3. append-only,
4. owned-environment only.

Do not use Phase 4.5 to improvise a production launch.

## Two Honest Activation Levels

Phase 4.5 has two valid levels of progress:

1. a local pre-live subset,
2. a real live activation pass.

The local pre-live subset is useful when:

1. ignored local config scaffolding exists,
2. dry-run validation is safe to execute,
3. the operator is not ready to place real credentials locally yet.

The real live activation pass begins only when:

1. the local files contain real owned-environment credentials,
2. execute-mode validation is safe to run,
3. one canary chain can touch the owned WordPress site and owned Facebook Page.

Do not confuse the first level with phase closeout.

## Inputs

Use this runbook together with:

1. [LOCAL_SECRETS_AND_TRANSPORT_CONFIG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/LOCAL_SECRETS_AND_TRANSPORT_CONFIG_POLICY_V1.md)
2. [PHASE_4_5_SYSTEM_ACTIVATION.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_5_SYSTEM_ACTIVATION.md)
3. [PHASE_4_5_VALIDATION_PLAN.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_5_VALIDATION_PLAN.md)
4. [DISTRIBUTION_ENGINE_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/DISTRIBUTION_ENGINE_RUNBOOK.md)
5. [TRACKING_ENGINE_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/TRACKING_ENGINE_RUNBOOK.md)
6. [SYSTEM_ACTIVATION_READINESS_REPORTING_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/SYSTEM_ACTIVATION_READINESS_REPORTING_V1.md)

## Step 0: Confirm The Local Baseline

Run the repo suite first:

```powershell
python -m unittest discover -s tests -v
```

If the local baseline is not green, stop and fix that first.

Then check the current activation signal:

```powershell
python src\cli\summarize_system_activation.py --json
```

Use that report as the current truth for:

1. config readiness,
2. approved canary candidates,
3. local canary-chain presence,
4. execute-mode validation gaps.

## Step 1: Create Safe Local Config Files

Copy the example configs:

1. [config/wordpress_rest_config.example.json](C:/Users/Administrator/OneDrive/Documents/co_ma/config/wordpress_rest_config.example.json) -> `config/wordpress_rest_config.local.json`
2. [config/facebook_graph_config.example.json](C:/Users/Administrator/OneDrive/Documents/co_ma/config/facebook_graph_config.example.json) -> `config/facebook_graph_config.local.json`

Replace placeholders with:

1. the owned WordPress site URL, username, and application password,
2. real WordPress taxonomy ids,
3. the owned Facebook Page id and Page access token.

## Step 2: Dry-Run Both Transport Validations

Preview both validation requests first:

```powershell
python src\cli\validate_wordpress_transport.py --config-path config\wordpress_rest_config.local.json
python src\cli\validate_facebook_transport.py --config-path config\facebook_graph_config.local.json
```

Review:

1. request URL,
2. method,
3. target identity,
4. absence of printed secrets.

## Step 3: Execute Both Read-Only Validations

Run the execute-mode checks with audit recording:

```powershell
python src\cli\validate_wordpress_transport.py --config-path config\wordpress_rest_config.local.json --execute --record-audit
python src\cli\validate_facebook_transport.py --config-path config\facebook_graph_config.local.json --execute --record-audit
```

Confirm:

1. WordPress identity matches the intended user,
2. Facebook identity matches the intended Page,
3. tracking audit records exist for both runs.

If real credentials are not yet available, stop here and record the run as a local pre-live subset instead of forcing a fake live activation result.

## Step 4: Select One Approved Draft As The Canary

Choose one approved draft only.

Do not batch this step.

The canary should be:

1. already approved,
2. low-risk,
3. easy to inspect manually after publication or scheduling.

## Step 5: Prepare The Canary Chain Locally

Prepare WordPress and Facebook records:

```powershell
python src\cli\prepare_wordpress_publish.py --draft-id <draft_id> --publish-intent draft
python src\cli\prepare_facebook_package.py --draft-id <draft_id> --blog-publish-id <blog_publish_id>
python src\cli\review_social_package.py --social-package-id <social_package_id> --outcome approved --note "phase_4_5_canary"
python src\cli\prepare_distribution_linkage.py --blog-publish-id <blog_publish_id> --social-package-id <social_package_id>
```

## Step 6: Execute The WordPress Canary

Preview first if needed:

```powershell
python src\cli\sync_wordpress_transport.py --blog-publish-id <blog_publish_id> --config-path config\wordpress_rest_config.local.json
```

Execute the real draft sync:

```powershell
python src\cli\sync_wordpress_transport.py --blog-publish-id <blog_publish_id> --config-path config\wordpress_rest_config.local.json --execute
```

If the canary will continue to Facebook publish or schedule, confirm the blog record has the correct final URL and state before continuing.

## Step 7: Record The Blog State Needed For Facebook

Inspect the real remote WordPress post first:

```powershell
python src\cli\reconcile_wordpress_post_state.py --blog-publish-id <blog_publish_id> --config-path config\wordpress_rest_config.local.json --execute
```

If the remote post is already published and the payload looks correct, reconcile the local chain append-only:

```powershell
python src\cli\reconcile_wordpress_post_state.py --blog-publish-id <blog_publish_id> --config-path config\wordpress_rest_config.local.json --execute --reconcile-local-state
```

If the remote post is scheduled instead:

```powershell
python src\cli\reconcile_wordpress_post_state.py --blog-publish-id <blog_publish_id> --config-path config\wordpress_rest_config.local.json --execute --reconcile-local-state --schedule-mode manual
```

## Step 8: Execute The Facebook Canary

Published canary:

```powershell
python src\cli\sync_facebook_transport.py --social-package-id <social_package_id> --action published --config-path config\facebook_graph_config.local.json --execute
```

Scheduled canary:

```powershell
python src\cli\sync_facebook_transport.py --social-package-id <social_package_id> --action scheduled --scheduled-for-facebook <timestamp> --schedule-mode manual --config-path config\facebook_graph_config.local.json --execute
```

If Facebook returns an expired-token or invalid-token error:

1. stop the canary,
2. refresh the Page access token in `config/facebook_graph_config.local.json`,
3. rerun `python src\cli\validate_facebook_transport.py --config-path config\facebook_graph_config.local.json --execute --record-audit`,
4. retry the same approved `social_package_id`,
5. record the retry outcome in the next Phase 4.5 acceptance batch.

## Step 9: Verify Connected-System Health

Inspect the system after the canary:

```powershell
python src\cli\summarize_distribution_health.py --json
python src\cli\summarize_distribution_schedule.py --json
python src\cli\summarize_publish_chain_history.py --view all --json
python src\cli\summarize_tracking_audit.py --json
```

Confirm:

1. the publish chain is visible,
2. the queue and mapping state are coherent,
3. the audit trail reflects the deliberate live validation activity,
4. there are no unexpected broken-chain alerts.

## Step 10: Record Acceptance Evidence

Write a Phase 4.5 activation batch after the canary run.

The record should include:

1. exact commands used,
2. the confirmed WordPress and Facebook identities,
3. the canary draft chosen,
4. the final observed chain state,
5. any residual risks that remain acceptable.

If the run stopped before execute-mode validation, record that honestly as a local pre-live activation batch and leave Phase 4.5 open.

## Intentional Limits

This runbook does not yet cover:

1. bulk release workflows,
2. comment CTA auto-posting,
3. production-scale retry tuning,
4. multiple sites or multiple Pages,
5. paid amplification or analytics interpretation.
