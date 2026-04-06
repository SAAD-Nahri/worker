# Coolify Operator API Deployment Runbook

## Purpose

This runbook defines the recommended deployment path for the internal Operator API when WordPress is hosted on Coolify.

## Recommended Shape

Use one separate Coolify application for the Operator API.

That application should:

1. build from this repo,
2. expose one HTTPS hostname such as `https://ops-api.kuchniatwist.pl`,
3. keep shared-secret auth enabled,
4. be independent from the WordPress container lifecycle.

## Why This Is The Preferred Path

This is better than running the API on a laptop because:

1. WordPress can actually reach it,
2. Coolify can restart it automatically,
3. Git-based redeploys become predictable,
4. the plugin can use a stable HTTPS URL instead of localhost.

## Repo Files To Use

1. [Dockerfile.operator-api](C:/Users/Administrator/OneDrive/Documents/co_ma/Dockerfile.operator-api)
2. [docker-compose.operator-api.yml](C:/Users/Administrator/OneDrive/Documents/co_ma/docker-compose.operator-api.yml)
3. [operator-api.env.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/coolify/operator-api.env.example)

## Coolify Option A: Dockerfile Build Pack

This is the simplest path.

Use:

1. Git repository: this repo
2. Base directory: `/`
3. Build pack: `Dockerfile`
4. Dockerfile location: `Dockerfile.operator-api`

Environment variables:

1. `CONTENT_OPS_OPERATOR_API_HOST=0.0.0.0`
2. `CONTENT_OPS_OPERATOR_API_PORT=8765`
3. `CONTENT_OPS_OPERATOR_API_SHARED_SECRET=<real secret>`
4. `CONTENT_OPS_OPERATOR_API_ENABLE_DOCS=false`

Port:

1. `8765`

Health check path:

1. `/healthz`

Domain:

1. `ops-api.kuchniatwist.pl`

Plugin setting:

1. `Operator API Base URL = https://ops-api.kuchniatwist.pl`

## Coolify Option B: Docker Compose Build Pack

Use:

1. Base directory: `/`
2. Docker Compose location: `docker-compose.operator-api.yml`
3. environment values from Coolify or from a copied env file based on [operator-api.env.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/coolify/operator-api.env.example)

This is useful if you want the health check and runtime shape declared in compose from day one.

## Auto Deploy

Recommended:

1. connect the Coolify application to the Git repository,
2. enable Auto Deploy on push,
3. keep production secrets in Coolify environment variables, not in the repo,
4. redeploy only from the tracked branch used for production.

## Validation Steps After Deploy

1. open `https://ops-api.kuchniatwist.pl/healthz`
2. confirm it returns a simple JSON `ok` status
3. in WordPress plugin settings, set the API base URL to the HTTPS hostname
4. keep the same shared secret in both places
5. open `Content Ops Approval > Validation`
6. confirm the reachability classification is `Remote-ready HTTPS`
7. confirm backend checks are green

## Do Not Do

1. do not point the hosted plugin to `127.0.0.1`
2. do not keep the API only on a laptop for production
3. do not expose the API without HTTPS and the shared secret
4. do not store Coolify secrets in tracked repo files
