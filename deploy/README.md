# Deployment Examples

This folder contains practical deployment helpers for the parts of the system that need a stable runtime shape.

## Current Files

1. [systemd/content-ops-operator-api.service.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/systemd/content-ops-operator-api.service.example)
   Example `systemd` service for running the internal operator API on the production worker host.
2. [nginx/content-ops-operator-api.nginx.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/nginx/content-ops-operator-api.nginx.example)
   Example `nginx` reverse-proxy config for exposing the operator API through one restricted HTTPS hostname.
3. [caddy/content-ops-operator-api.Caddyfile.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/caddy/content-ops-operator-api.Caddyfile.example)
   Example `Caddy` reverse-proxy config for the same production shape.
4. [coolify/operator-api.env.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/coolify/operator-api.env.example)
   Example Coolify environment-variable baseline for the hosted Operator API service.
5. [systemd/content-ops-source-intake.service.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/systemd/content-ops-source-intake.service.example)
   Example oneshot `systemd` service for scheduled source intake on the worker host.
6. [systemd/content-ops-source-intake.timer.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/systemd/content-ops-source-intake.timer.example)
   Example timer for running the source-intake service every 6 hours.
7. [systemd/content-ops-runtime-backup.service.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/systemd/content-ops-runtime-backup.service.example)
   Example oneshot `systemd` service for creating runtime backup bundles.
8. [systemd/content-ops-runtime-backup.timer.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/systemd/content-ops-runtime-backup.timer.example)
   Example timer for daily runtime backups.
9. [systemd/content-ops-daily-reports.service.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/systemd/content-ops-daily-reports.service.example)
   Example oneshot `systemd` service for writing daily JSON health and history reports into `data/reports/`.
10. [systemd/content-ops-daily-reports.timer.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/systemd/content-ops-daily-reports.timer.example)
   Example timer for the daily reporting snapshot.

## Important Rule

These files are examples, not live production config.

Before using them:

1. change the service user,
2. change the working directory,
3. confirm the Python path,
4. confirm the operator API config path,
5. confirm backup and report output paths,
6. confirm the reverse-proxy or firewall rules that protect access from the WordPress host,
7. confirm the plugin points to the reachable HTTPS hostname instead of `127.0.0.1`.
