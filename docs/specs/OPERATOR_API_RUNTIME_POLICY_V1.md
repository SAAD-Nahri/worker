# Operator API Runtime Policy V1

## Purpose

This spec answers the practical question:

1. how the operator API should be run now,
2. how it should be run later in production,
3. how that fits the broader runtime model without creating avoidable infrastructure complexity.

## Core Decision

The operator API is the first justified narrow long-running internal service in the system.

That is acceptable because:

1. the WordPress approval plugin needs a stable backend while the operator is using admin review pages,
2. the API remains internal and review-only,
3. it does not replace the CLI-first workflow engine,
4. it does not create a second source of truth.

## Local Development And Validation

For local development or local WordPress validation, run:

```powershell
python src\cli\run_operator_api.py
```

Or use the helper:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_operator_api.ps1
```

Preferred local config:

1. `config/operator_api.local.json`

Required fields:

1. `bind_host`
2. `bind_port`
3. `shared_secret`
4. `enable_docs`

Default local bind:

1. `127.0.0.1:8765`

That localhost binding is correct only when:

1. WordPress and the plugin run on the same machine as the operator API, or
2. local validation is being done from the same host.

## Production Rule

In production, the operator API should run as:

1. one `systemd` service on the worker host,
2. one Uvicorn process,
3. one internal configuration file,
4. one restricted HTTPS entry path that the WordPress host can reach.

The operator API should not be treated as:

1. a public internet API,
2. a general application backend,
3. a second workflow engine,
4. a general-purpose dashboard service.

## Why Localhost Alone Is Not Enough In Production

If WordPress is hosted separately, the plugin runs on the WordPress server, not on the worker host.

That means the plugin cannot call:

1. `http://127.0.0.1:8765`

on the worker, because `127.0.0.1` from WordPress points back to the WordPress host itself.

So the future production shape must be:

1. operator API binds locally on the worker,
2. a reverse proxy exposes one restricted HTTPS endpoint,
3. the WordPress plugin uses that HTTPS base URL,
4. the shared secret remains required.

## Recommended Production Shape

### Worker host

Run the service locally on:

1. `127.0.0.1:8765`

using:

1. `systemd`
2. a repo checkout under `/opt/co_ma/current`
3. the repo virtual environment

### Reverse proxy

Expose the operator API through:

1. a dedicated hostname such as `https://ops-api.example.com`

with:

1. HTTPS only,
2. docs disabled by default,
3. optional IP allowlisting where practical,
4. no indexing or public linking,
5. the shared-secret header still required.

Example reverse-proxy baselines:

1. [content-ops-operator-api.nginx.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/nginx/content-ops-operator-api.nginx.example)
2. [content-ops-operator-api.Caddyfile.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/caddy/content-ops-operator-api.Caddyfile.example)

### WordPress plugin setting

The plugin's `api_base_url` should point to:

1. the restricted HTTPS operator API URL reachable from the WordPress host

and not to:

1. worker localhost,
2. an internal-only address that the WordPress host cannot reach.

## Security Minimum

The operator API production baseline must keep:

1. shared-secret auth,
2. HTTPS transport,
3. docs disabled unless intentionally enabled for local debugging,
4. a dedicated hostname or path,
5. no broader public use than the approval plugin or operator troubleshooting path.

## Operational Recommendation

For the solo-operator baseline:

1. keep the operator API always on during normal production operation,
2. keep the rest of the system mostly CLI-plus-scheduler based,
3. do not expand this into a broader application server unless later evidence justifies it.

This preserves the current architecture:

1. one narrow always-on review API,
2. recurring jobs still handled by timers,
3. workflow state still append-only in repo runtime data.
