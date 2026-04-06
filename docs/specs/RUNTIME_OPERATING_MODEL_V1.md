# Runtime Operating Model V1

## Purpose

This spec answers the practical question:

1. what is the best way to run the finished system after build.

The answer for v1 is intentionally boring.

## Recommended Default

The first production runtime should be:

1. one small Linux VPS running Ubuntu LTS or equivalent,
2. one repo checkout on that host,
3. one Python virtual environment,
4. one service user dedicated to the repo,
5. one scheduled-job model using `systemd` services and timers,
6. WordPress kept as a separate hosted destination,
7. Facebook and optional OpenAI accessed as external APIs from the worker.

This repo should run as a scheduled CLI worker, not as a public-facing web application.

## Why This Is The Right V1 Shape

This model is preferred because it is:

1. cheap,
2. easy for one person to understand,
3. easy to back up,
4. easy to restart,
5. aligned with the current CLI-first architecture.

It also avoids the usual overbuild mistakes:

1. unnecessary containers,
2. unnecessary databases,
3. unnecessary orchestration layers,
4. unnecessary split services.

## Production Topology

### External services

The worker depends on external platforms, but does not absorb them:

1. WordPress host for the blog,
2. Facebook Page and Graph API,
3. optional OpenAI provider in later phases,
4. optional off-host backup storage.

### Worker host

The worker host owns:

1. repo checkout,
2. Python environment,
3. local config files,
4. append-only runtime `data/`,
5. scheduled jobs,
6. operational logs.

### Operator workstation

The workstation remains acceptable for:

1. manual review,
2. debugging,
3. development,
4. emergency fallback.

It should not be the primary production runtime.

## Recommended Directory Shape

The exact path can vary, but the recommended layout is:

1. `/opt/co_ma/current/` for the repo checkout,
2. `/opt/co_ma/current/.venv/` for the Python environment,
3. `/opt/co_ma/current/config/` for ignored local config files,
4. `/opt/co_ma/current/data/` for append-only runtime data,
5. `/opt/co_ma/backups/` for short-lived local backup bundles before off-host copy,
6. journal or host logging for service output.

The runtime should preserve the repo-relative `config/` and `data/` structure because the code already expects it.

## Process Model

The process model should be:

1. short-lived scheduled CLI commands,
2. clear manual approval commands,
3. one narrow always-on operator API only when the approval UI is in use or enabled for production,
4. no broader mandatory long-running application server,
5. no background worker farm.

The operator API is the one justified exception to the otherwise CLI-first runtime model because the WordPress approval plugin needs a stable backend while the operator is reviewing content.

### Automated recurring jobs

Likely automation targets include:

1. source intake,
2. source health summaries,
3. distribution health summaries,
4. tracking audit/report generation,
5. backup jobs.

### Narrow always-on service

When the Approval UI phase is active, keep:

1. one operator API process running on the worker,
2. that process internal and review-only,
3. that process separate from the recurring timer jobs.

### Operator-triggered jobs

The operator should still directly run or approve:

1. draft review,
2. social-package review,
3. media review,
4. live canary or unusual publish retries,
5. recovery operations.

## Operational Principles

1. One host is the default.
2. One operator is the default.
3. One runtime copy is the default.
4. One scheduler is the default.
5. Simplicity beats theoretical scale.

## Explicit Non-Goals

Do not make these part of the v1 operating model:

1. Kubernetes,
2. microservice decomposition,
3. auto-scaling workers,
4. always-on queue brokers,
5. custom infrastructure dashboards,
6. turning the operator API into a broad public application backend.

## Complexity Triggers

The runtime model should only become more complex if later evidence shows:

1. the single worker cannot keep up with volume,
2. job collisions become operationally painful,
3. recovery windows become unacceptable,
4. Decision Layer or Scaling Layer creates justified pressure for more isolation.
