# Backup And Recovery Policy V1

## Purpose

This policy defines what must be backed up, how often, and what recovery must prove before the system is treated as safely runnable.

## What Must Be Protected

The critical assets are:

1. append-only runtime data in `data/`,
2. local runtime config files in `config/*.local.json`,
3. the repo code and docs baseline,
4. any host-level scheduler/service definitions needed to run the system.

WordPress content and media hosted remotely should also have their own platform-appropriate backup path, but that is not a substitute for backing up this repo runtime.

## Minimum Backup Rules

1. runtime `data/` must be backed up daily,
2. a pre-deploy backup must be taken before production updates,
3. local config/secrets must be recoverable from a secure source outside git,
4. backups must leave the production host.

## Recommended Retention Baseline

The simple default is:

1. recent daily backups,
2. a small set of weekly backups,
3. a small set of monthly backups if storage allows.

This policy does not require complex archival systems.

## Recovery Rules

A recovery drill should prove that the operator can:

1. restore the repo checkout,
2. restore runtime data,
3. restore local config files from a secure source,
4. recreate the Python environment,
5. rerun health and reporting commands successfully.

## Recovery Success Criteria

Recovery is good enough when:

1. the runtime records are readable,
2. the key CLI commands work,
3. the operator can explain what happened to the latest publish chain,
4. the scheduler can be restarted cleanly.

## What This Policy Does Not Require

1. instant failover,
2. high availability,
3. multi-region replication,
4. enterprise disaster recovery tooling.

The correct v1 goal is recoverable, not overengineered.
