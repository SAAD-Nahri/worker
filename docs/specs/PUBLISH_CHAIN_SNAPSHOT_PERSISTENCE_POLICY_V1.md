# Publish Chain Snapshot Persistence Policy V1

## Purpose

This document decides whether Phase 4 should persist normalized publish-chain snapshots as their own runtime artifact or keep them derived on demand.

The goal is to prevent a weak middle state where the repo quietly grows a second truth layer without a clear reason, rebuild rule, or invalidation policy.

## Current Decision

Keep normalized publish-chain snapshots on demand for the current Phase 4 baseline.

Do not add a persisted snapshot artifact yet.

## Why This Is The Right Decision Now

The current repo already has the pieces it needs for trustworthy tracking:

1. append-only source, draft, review, publish, queue, and mapping records,
2. deterministic lineage joins,
3. operator-readable ledger, exception, activity, and variant views,
4. deliberate audit records for normalization runs and transport validation.

At the current project stage, a persisted snapshot artifact would add more operational weight than value.

The main costs would be:

1. deciding when the persisted file is stale,
2. defining rebuild triggers and invalidation behavior,
3. debugging disagreements between the raw records and the derived artifact,
4. maintaining another runtime file during reset, archive, and rerun workflows,
5. creating a second place where future developers may accidentally look for truth first.

The current on-demand baseline keeps the architecture cleaner:

1. raw append-only records remain authoritative,
2. normalization stays deterministic and reproducible,
3. tracking reports stay honest about being derived views,
4. Phase 4 avoids premature warehouse-style complexity.

## Current Operating Rule

For Phase 4 and the current pre-Phase-5 baseline:

1. normalized publish-chain snapshots are generated when a report or deliberate normalization command is run,
2. the normalized snapshot is treated as a derived object, not a stored source of truth,
3. audit records may log that a normalization run happened, but they do not replace the normalized result itself,
4. no dedicated persisted snapshot file should be introduced as part of the default runtime state.

## When This Decision Must Be Revisited

Persisted snapshot storage should only be reconsidered when one or more of the following becomes true:

1. on-demand normalization becomes materially slow for normal operator use,
2. Phase 5 comparison work needs frozen cohorts or repeatable decision-run inputs,
3. external performance data needs to be joined against a stable snapshot set rather than rebuilt every time,
4. normalization becomes multi-step enough that rerunning it repeatedly adds real cost or fragility,
5. the operator needs point-in-time historical snapshots for audit or review, not just latest-chain reconstruction.

If those conditions are not true, the repo should continue using on-demand normalization.

## Future Persistence Requirements

If persisted normalized snapshots are added later, they must follow these rules:

### 1. Raw Records Stay Authoritative

The persisted snapshot artifact must remain derived from append-only runtime records.

It must not become the primary source of truth.

### 2. Rebuild First, Not Incremental Mutation First

The first persisted baseline should use a deliberate full rebuild workflow.

Do not start with complex incremental mutation rules.

### 3. Explicit Snapshot Metadata

Any persisted snapshot artifact must preserve at minimum:

1. `snapshot_version`
2. `generated_at`
3. `build_run_id`
4. `input_record_counts` or equivalent source-watermark summary
5. `normalization_contract_version`

### 4. Clear Artifact Boundary

If the artifact is introduced later, it should live as an explicit runtime artifact with a documented rebuild command and archive/reset treatment.

It must not appear silently as an undocumented cache file.

### 5. Reproducibility Over Cleverness

The rebuild path must be deterministic, idempotent, and operator-readable.

If the operator cannot explain how to rebuild it from the raw records, the persistence layer is not ready.

## What Must Be Avoided

Do not:

1. persist snapshots just because reporting exists,
2. treat faster local reads as enough justification on their own,
3. create a hidden cache without a rebuild policy,
4. let future decision logic depend on an undocumented derived file,
5. blur the line between audit logs and stored normalized outputs.

## Practical Proceeding Rule

Proceed with Phase 4 and early Phase 5 planning under this assumption:

1. normalized publish-chain snapshots remain on demand,
2. audit records continue to log deliberate normalization runs,
3. persistence is a later optimization, not a current dependency,
4. the next revisit point is Phase 5 readiness or proven operator pain, whichever comes first.

## Definition Of Done

This policy is satisfied when:

1. the repo has one explicit answer to the snapshot-persistence question,
2. Phase 4 no longer treats this as an unresolved architectural gap,
3. future persistence work has clear trigger conditions and guardrails,
4. the current operator path stays simple and trustworthy.
