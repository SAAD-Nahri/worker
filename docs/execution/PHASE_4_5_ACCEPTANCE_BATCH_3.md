# Phase 4.5 Acceptance Batch 3

## Purpose

This batch records the first execute-mode transport-validation pass with real local config values.

The goal of this batch was to prove:

1. the ignored local config files now contain real operator values,
2. both dry-run validations still behave safely,
3. execute-mode validation can now distinguish a real transport success from a real live-environment failure,
4. the remaining Phase 4.5 blocker is specific and actionable.

## Scope

Included in this batch:

1. activation-readiness summary after real config replacement,
2. dry-run WordPress transport validation,
3. dry-run Facebook transport validation,
4. execute-mode WordPress transport validation with audit recording,
5. execute-mode Facebook transport validation with audit recording,
6. post-run activation summary and tracking-audit review.

Not included in this batch:

1. live WordPress draft sync,
2. live Facebook publish or schedule,
3. formal Phase 4.5 closeout.

## Commands Run

### Activation summary before execute-mode validation

```powershell
python src\cli\summarize_system_activation.py --json
```

Observed result:

1. readiness signal: `awaiting_execute_validation`,
2. both local config files parsed cleanly,
3. both local config files were marked `ready_for_execute=true`,
4. one approved-pass draft candidate remained available,
5. one local canary-preparation chain remained available.

### Dry-run transport validation

```powershell
python src\cli\validate_wordpress_transport.py --config-path config\wordpress_rest_config.local.json
python src\cli\validate_facebook_transport.py --config-path config\facebook_graph_config.local.json
```

Observed result:

1. WordPress dry-run request targeted `https://kuchniatwist.pl/wp-json/wp/v2/users/me?context=edit`,
2. Facebook dry-run request targeted `https://graph.facebook.com/v24.0/1117973474723361?fields=id,name`,
3. both commands stayed non-mutating,
4. no secrets were printed.

### Execute-mode transport validation

```powershell
python src\cli\validate_wordpress_transport.py --config-path config\wordpress_rest_config.local.json --execute --record-audit
python src\cli\validate_facebook_transport.py --config-path config\facebook_graph_config.local.json --execute --record-audit
```

Observed result:

1. Facebook validation succeeded,
2. validated Page id: `1117973474723361`,
3. validated Page name: `Kuchniatwist`,
4. WordPress validation failed with HTTP `401`,
5. returned WordPress error:
   `{"code":"rest_not_logged_in","message":"You are not currently logged in.","data":{"status":401}}`

### Post-run status review

```powershell
python src\cli\summarize_system_activation.py --json
python src\cli\summarize_tracking_audit.py --json
```

Observed result:

1. readiness signal remained `awaiting_execute_validation`,
2. successful Facebook execute validations: `1`,
3. successful WordPress execute validations: `0`,
4. current remaining blocking reasons:
   1. `wordpress_execute_validation_missing`
   2. `live_canary_execution_missing`
5. tracking audit now contains:
   1. one successful Facebook transport validation,
   2. one failed WordPress transport validation,
   3. the earlier publish-chain normalization record.

## Key Observations

1. The Facebook transport is now validated against the real owned Page.
2. The WordPress issue is no longer a config-shape issue.
3. The current WordPress blocker is an authentication acceptance problem at the live endpoint.
4. Phase 4.5 is closer to closeout, but not yet ready because WordPress execute validation is still failing.

## Current Blocker Interpretation

The WordPress failure is consistent with one of these operator-environment issues:

1. the username does not match the account that created the application password,
2. the application password value is incorrect or incomplete,
3. the WordPress site or hosting layer is not accepting the authorization header correctly,
4. application-password authentication is restricted or disabled in the target environment.

This batch does not try to guess which one is true. It records the exact observed failure first.

## Recommendation

The next work should stay narrow:

1. verify the WordPress username matches the application-password owner exactly,
2. regenerate the WordPress application password if needed,
3. rerun `validate_wordpress_transport.py --execute --record-audit`,
4. once WordPress validates successfully, execute the live canary chain,
5. then write the formal Phase 4.5 closeout.
