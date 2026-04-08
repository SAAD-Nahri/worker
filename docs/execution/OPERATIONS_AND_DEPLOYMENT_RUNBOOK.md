# Operations And Deployment Runbook

## Purpose

This runbook defines the practical answer to:

1. how the finished project should be run after build.

The recommended answer is:

1. run it on one small Linux VPS,
2. keep WordPress separately hosted,
3. run recurring repo jobs with `systemd` timers,
4. run the operator API as one narrow `systemd` service for the approval UI,
5. keep manual review and approval steps explicit,
6. back up runtime data daily.

## Recommended Production Shape

### Host model

Use:

1. one Ubuntu LTS or equivalent VPS,
2. one repo checkout,
3. one Python virtual environment,
4. one service user,
5. one set of ignored local config files.

### Keep separate

Do not merge these into the worker host:

1. WordPress hosting,
2. Facebook itself,
3. optional OpenAI provider,
4. backup destination.

## Day-One Production Checklist

1. provision the Linux VPS,
2. install Python and required system basics,
3. place the repo checkout on the host,
4. create the virtual environment,
5. copy local config files into `config/*.local.json`,
6. verify `data/` permissions,
7. run the repo test baseline,
8. run the activation and health-reporting commands,
9. set up the operator API `systemd` service,
10. set up the reverse proxy or restricted HTTPS route for the operator API if WordPress is hosted elsewhere,
11. set up `systemd` services and timers for recurring jobs,
12. test one manual run of each scheduled job before enabling timers.

## Recurring Automation Baseline

The first recurring jobs should be limited to:

1. source intake,
2. source/draft/distribution health summaries,
3. tracking summary generation,
4. backup creation.

Manual approvals should remain manual:

1. draft approval,
2. social-package approval,
3. media approval,
4. unusual publish retries.

## Operator API Runtime

The approval plugin needs the operator API to be reachable while WordPress admin is in use.

That means:

1. run the operator API continuously on the worker host,
2. keep it separate from the recurring timer jobs,
3. keep it internal and review-only,
4. if WordPress is separately hosted, expose it through a restricted HTTPS endpoint rather than localhost.

Recommended service example:

1. [deploy/systemd/content-ops-operator-api.service.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/systemd/content-ops-operator-api.service.example)

Recommended timer examples:

1. [deploy/systemd/content-ops-source-intake.service.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/systemd/content-ops-source-intake.service.example)
2. [deploy/systemd/content-ops-source-intake.timer.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/systemd/content-ops-source-intake.timer.example)
3. [deploy/systemd/content-ops-daily-reports.service.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/systemd/content-ops-daily-reports.service.example)
4. [deploy/systemd/content-ops-daily-reports.timer.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/systemd/content-ops-daily-reports.timer.example)
5. [deploy/systemd/content-ops-runtime-backup.service.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/systemd/content-ops-runtime-backup.service.example)
6. [deploy/systemd/content-ops-runtime-backup.timer.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/systemd/content-ops-runtime-backup.timer.example)

Recommended reverse-proxy examples:

1. [deploy/nginx/content-ops-operator-api.nginx.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/nginx/content-ops-operator-api.nginx.example)
2. [deploy/caddy/content-ops-operator-api.Caddyfile.example](C:/Users/Administrator/OneDrive/Documents/co_ma/deploy/caddy/content-ops-operator-api.Caddyfile.example)

Recommended hosted-platform runbook:

1. [COOLIFY_OPERATOR_API_DEPLOYMENT_RUNBOOK.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/COOLIFY_OPERATOR_API_DEPLOYMENT_RUNBOOK.md)

Recommended local helper for Windows development:

1. [scripts/run_operator_api.ps1](C:/Users/Administrator/OneDrive/Documents/co_ma/scripts/run_operator_api.ps1)

## Daily Operator Loop

The normal daily loop should look like:

1. check health summaries,
2. review shortlisted or draft-ready items,
3. approve or reject drafts,
4. approve or reject social packages,
5. review publish queue and live states,
6. confirm backup success.

## Deployment Update Routine

For a normal update:

1. pause recurring timers,
2. take a runtime-data backup,
3. update the repo checkout,
4. refresh dependencies if needed,
5. run `python -m unittest discover -s tests -v`,
6. run the main health/reporting commands,
7. resume timers,
8. watch the first scheduled cycle after deployment.

Before or during that flow, the repo now has a dedicated backup command:

```powershell
python src\cli\create_runtime_backup.py --backup-root backups
```

## Recovery Routine

If the host fails or the working copy becomes unusable:

1. rebuild the host or create a fresh host,
2. restore the repo checkout,
3. restore the Python environment,
4. restore `data/`,
5. restore local config files from the secure source,
6. rerun health, history, and audit commands,
7. only then resume scheduled jobs.

Dry-run restore preview:

```powershell
python src\cli\restore_runtime_backup.py --backup-path backups\<bundle>.zip --target-root <restore_root> --dry-run
```

Restore with config when appropriate:

```powershell
python src\cli\restore_runtime_backup.py --backup-path backups\<bundle>.zip --target-root <restore_root> --restore-config
```

## Local Development Note

The Windows workstation remains fine for:

1. development,
2. debugging,
3. temporary fallback.

It should not stay the long-term primary production runtime unless the operator intentionally chooses that path and accepts the added maintenance burden.

For local Windows work, the simplest operator API start path is:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_operator_api.ps1
```
