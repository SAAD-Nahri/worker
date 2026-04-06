# Phase 4.9 Acceptance Batch 9

## Purpose

Make the Operator API realistically deployable for a hosted WordPress site running on Coolify.

## Work Completed

1. Added a container baseline in [Dockerfile.operator-api](C:/Users/Administrator/OneDrive/Documents/co_ma/Dockerfile.operator-api).
2. Added a compose baseline in [docker-compose.operator-api.yml](C:/Users/Administrator/OneDrive/Documents/co_ma/docker-compose.operator-api.yml).
3. Added a public health endpoint at `/healthz` for platform checks.
4. Extended config loading so `CONTENT_OPS_OPERATOR_API_ENABLE_DOCS` can be controlled from environment variables in hosted deployments.
5. Added a Coolify environment example in [operator-api.env.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/coolify/operator-api.env.example).
6. Added a hosted deployment runbook in [COOLIFY_OPERATOR_API_DEPLOYMENT_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/COOLIFY_OPERATOR_API_DEPLOYMENT_RUNBOOK.md).

## Why This Matters

The approval plugin can only work reliably with hosted WordPress when the Operator API is also deployed as a reachable service.

This batch converts the Operator API from:

1. a local developer helper

into:

1. a deployable hosted service with a health check,
2. an environment-variable runtime model,
3. a documented Coolify autodeploy path.

## Validation

1. `python -m unittest discover -s tests -v`
2. the Python suite now validates the public `/healthz` endpoint and env-driven docs config behavior

## Remaining Gap

1. create the Coolify application,
2. attach the real HTTPS domain,
3. enable Auto Deploy in Coolify,
4. point the WordPress plugin at the hosted Operator API URL,
5. complete the first live admin validation batch.
