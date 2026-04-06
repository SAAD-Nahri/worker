# Deployment And Scheduling Policy V1

## Purpose

This policy defines how the system should be deployed and how recurring jobs should be scheduled in the first production operating model.

## Deployment Recommendation

The recommended v1 deployment model is:

1. one production checkout on one small Linux VPS,
2. one Python virtual environment,
3. one dedicated service user,
4. one scheduler based on `systemd` services and timers.

This policy intentionally rejects infrastructure theater.

## Scheduler Recommendation

### Primary choice

Use `systemd` services and timers for production recurring jobs.

Reasons:

1. built into the host,
2. restartable and inspectable,
3. easy to log through the system journal,
4. simple for one person to maintain.

### Acceptable fallback choices

1. `cron` on Linux if `systemd` timers are not practical,
2. Windows Task Scheduler for local development or local fallback only.

Windows Task Scheduler should not be treated as the long-term primary production plan unless the operator intentionally decides to keep the production runtime on Windows.

## Default Job Categories

The scheduler should eventually manage recurring jobs like:

1. source intake,
2. source health reporting,
3. distribution health reporting,
4. tracking summary generation,
5. backup creation.

Manual approval steps should remain outside automatic scheduling.

## Default Job Cadence

The initial default cadence should stay conservative:

1. source intake every few hours, not every few minutes,
2. health/reporting once or twice daily,
3. backup daily,
4. manual publish and review windows kept operator-controlled.

The point is reliability, not hyperactivity.

## Deployment Procedure Rules

A standard update deployment should:

1. pause or temporarily disable recurring timers,
2. create a fresh backup of runtime data,
3. update the code checkout,
4. update Python dependencies if needed,
5. run the test baseline,
6. run key health commands,
7. resume recurring timers.

## Logging Rules

Scheduled jobs should write to an operator-visible log path:

1. journal output is acceptable on Linux,
2. a dedicated log directory is acceptable if journal access is awkward,
3. failures should be easy to inspect without opening the code.

## Things This Policy Rejects For V1

1. multiple parallel worker hosts,
2. container orchestration,
3. queue-broker infrastructure,
4. blue/green or canary infrastructure rollouts,
5. deployment pipelines more complex than the repo needs.
