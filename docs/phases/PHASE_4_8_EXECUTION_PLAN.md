# Phase 4.8 Execution Plan

## Purpose

This plan turns the runtime and deployment phase into a sequence of practical deliverables instead of a vague "we will host it later" promise.

The goal is to choose the cheapest, safest, most maintainable way to run the finished system as a solo operator workflow.

## Recommended Build Order

### Slice 1: Lock the production shape

Objective:

1. choose the first production runtime target,
2. decide what runs on that host,
3. decide what explicitly stays outside that host.

Deliverables:

1. runtime operating model spec,
2. recommendation for a small Linux VPS,
3. explicit separation between the worker runtime and the WordPress host.

Out of scope:

1. container orchestration,
2. managed cluster design,
3. multiple worker roles.

### Slice 2: Define deployment and scheduling rules

Objective:

1. decide how code updates are deployed,
2. decide how recurring jobs are scheduled,
3. keep the runtime boring and recoverable.

Deliverables:

1. deployment and scheduling policy,
2. recommended `systemd` timer model,
3. defined local-development fallback for Windows Task Scheduler,
4. first-pass job cadence for intake, health, reporting, and backup.

Out of scope:

1. visual scheduler UI,
2. dynamic queue planner,
3. multi-tenant hosting patterns.

### Slice 3: Define backup and recovery

Objective:

1. decide what gets backed up,
2. decide how often it is backed up,
3. decide what recovery must prove before the system is considered production-runnable.

Deliverables:

1. backup and recovery policy,
2. required backup targets,
3. restore expectations,
4. minimum recovery drill.

Out of scope:

1. enterprise disaster recovery,
2. zero-downtime failover,
3. complex archival automation.

### Slice 4: Define the operator runbook

Objective:

1. make daily and weekly operation explicit,
2. avoid "just remember how to run it" as an operations strategy.

Deliverables:

1. operations and deployment runbook,
2. daily operator loop,
3. deployment/update sequence,
4. incident and recovery checklist.

Out of scope:

1. custom dashboards,
2. chat-ops tooling,
3. general infrastructure platform work.

### Slice 5: Validate and close out

Objective:

1. make sure the chosen operating model is runnable,
2. block Phase 5 until runtime questions are no longer open.

Deliverables:

1. validation plan,
2. deployment rehearsal baseline,
3. backup/recovery rehearsal baseline,
4. Phase 4.8 closeout pack.

Out of scope:

1. decision rules,
2. analytics ranking,
3. new content-generation logic.

## Default Recommendation

Unless later evidence says otherwise, the default production recommendation is:

1. small Ubuntu LTS VPS,
2. one repo checkout on that host,
3. one Python virtual environment,
4. one service user,
5. `systemd` timers for recurring jobs,
6. append-only runtime data kept in the repo `data/` directory with daily off-host backup.

## Phase Boundary Rule

Phase 4.8 should solve:

1. how the system runs,
2. how it is updated,
3. how it is backed up,
4. how it is restored.

It must not solve:

1. which content wins,
2. which hooks outperform,
3. what should be promoted.
