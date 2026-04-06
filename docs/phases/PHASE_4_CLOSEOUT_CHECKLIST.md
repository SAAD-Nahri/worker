# Phase 4 Closeout Checklist

## Purpose

This checklist defines what must be true before Phase 4 can be treated as professionally complete.

Phase 4 should not close because:

1. one derived report exists,
2. one tracking view renders,
3. tests are green.

Phase 4 should close only when lineage trust, operator readability, auditability, and tracking-scope discipline are all stable enough for Phase 5 to build on them without redefining the tracking layer.

## Core Rule

Closeout requires implementation proof, operator proof, and explicit residual-item handling.

That means:

1. the normalized tracking contract must be stable,
2. the operator must be able to inspect chains without reading raw JSONL by hand,
3. audit visibility must exist for deliberate normalization work,
4. deferred tracking work must be written down instead of left implied.

## Closeout Gates

### 1. Normalization And Lineage Baseline

- [x] The normalized publish-chain snapshot contract is explicit.
- [x] The append-only runtime records remain the source of truth.
- [x] Deterministic lineage joins exist from source item to draft to blog to social to Facebook.
- [x] Partial and failed chains remain representable instead of being filtered out.
- [x] Selected blog and social values survive into the normalized layer.

### 2. Reporting And Operator Baseline

- [x] The operator can read a publish-chain ledger without opening raw JSONL files.
- [x] The operator can read an exception view without opening raw JSONL files.
- [x] The operator can read activity and variant-usage views from the same normalized baseline.
- [x] Zero-state outputs remain valid and operator-readable when runtime publish data is currently sparse or empty.
- [x] A dedicated Phase 4 tracking runbook exists for the accepted operator path.

### 3. Audit And Persistence-Policy Baseline

- [x] Deliberate normalization-run audit records exist.
- [x] Execute-mode transport-validation audit records exist.
- [x] The repo has an explicit answer to whether normalized snapshots stay on demand or become persisted artifacts.
- [x] The current accepted answer is to keep snapshots on demand until later trigger conditions justify persistence.

### 4. Validation Baseline

- [x] The standard unittest suite passes from the repo root.
- [x] Focused Phase 4 tests cover chain history, reporting, audit recording, and tracking CLI paths.
- [x] A focused cross-phase smoke test proves one clean chain can move from source item through publish linkage into tracking and audit.
- [x] Key Phase 4 reporting commands load and run from the repo root.
- [x] Phase 4 acceptance batches are recorded in the repo.

### 5. Documentation Baseline

- [x] The Phase 4 phase brief reflects the real implementation baseline.
- [x] The Phase 4 execution plan reflects the real implemented slices.
- [x] The Phase 4 validation plan reflects the implemented tracking and audit layer.
- [x] The new Phase 4 policy docs are linked from the specs index.
- [x] This closeout checklist exists and is linked from the phase docs.
- [x] The explicit residual-items record exists so deferred work is not confused with hidden blockers.
- [x] The formal closeout review exists.
- [x] The Phase 5 entry checklist exists before Phase 4 is treated as passable.

## What Is Still Intentionally Open

No remaining Phase 4 closeout blockers are open.

The accepted deferred items are recorded in [PHASE_4_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_4_RESIDUAL_ITEMS.md).

## What Is Explicitly Not Required For Closeout

Do not hold Phase 4 open waiting for:

1. click or CTR ingestion,
2. dashboards,
3. winner scoring,
4. paid promotion logic,
5. persisted normalized snapshot storage,
6. OpenClaw or agent-first decision orchestration.

Those belong to Phase 5, Phase 6, or explicit later follow-up.

## Current Status

Phase 4 is now closeout-ready and formally passable with explicit residual items.

The current strongest evidence is:

1. deterministic lineage normalization exists,
2. operator-readable ledger, exception, activity, and variant views exist,
3. deliberate audit records exist for normalization and transport validation work,
4. the snapshot-persistence question is now explicitly resolved instead of left open,
5. the repo now has one explicit cross-phase connectivity proof in addition to per-engine tests,
6. the repo-wide validation baseline currently passes with `203` tests.

## Exit Rule

Phase 4 can be proposed for closeout only when every unchecked item in this file is either:

1. completed, or
2. explicitly moved to later work with written justification in the phase docs.
