# Phase 2 Closeout Checklist

## Purpose

This checklist defines what must be true before Phase 2 can be treated as professionally complete.

Phase 2 should not close because:

1. drafts can be generated,
2. tests are green,
3. the operator CLI exists.

Phase 2 should close only when deterministic content production, reviewability, routing honesty, and operator visibility are all stable enough for Phase 3 to depend on them.

## Core Rule

Closeout requires both implementation proof and operational proof.

That means:

1. code paths must work,
2. validation must be repeatable,
3. weak-fit behavior must be visible,
4. docs and runbooks must match the actual baseline,
5. unresolved gaps must be explicit rather than hidden.

## Closeout Gates

### 1. Draft Production Baseline

- [x] Eligible Phase 1 source items can be converted into structured draft records.
- [x] The deterministic formatter works without any external AI dependency.
- [x] Template contracts are explicit and enforced in code, including slot-level guidance where the accepted v1 contract encodes it.
- [x] Explicit template overrides cannot cross template families and bypass the source item's accepted fit.
- [x] Source lineage survives from source item to draft record.
- [x] Category and tag assignment uses the controlled v1 taxonomy.

### 2. Quality And Risk Baseline

- [x] Every generated draft receives a visible `pass`, `review_flag`, or `blocked` outcome.
- [x] Derivative-risk notes are recorded as part of the draft result.
- [x] Semantic-fit signals exist for noisy or recipe-heavy source context.
- [x] Weak-fit routing exists for `proceed`, `review_only`, `hold_for_reroute`, and `reject_for_v1`.
- [x] The gold set includes enough blocked and clearly weak-fit live cases to protect closeout from false confidence.

### 3. Operator Workflow Baseline

- [x] The operator can create a draft from a known `source_item_id`.
- [x] Draft creation output includes the current routing recommendation.
- [x] The operator can review a draft and record an append-only decision.
- [x] Content-affecting intro rewrites reopen the draft review state and refresh quality fields.
- [x] The operator can summarize batch health without opening JSONL files manually.
- [x] Draft health reporting exposes approval state, quality state, and routing state together.

### 4. Validation Baseline

- [x] The standard unittest suite passes from the repo root.
- [x] The fixed Phase 2 gold-set replay passes.
- [x] At least one live acceptance batch is recorded against runtime source items.
- [x] A routing-visible acceptance replay is recorded in the repo.
- [x] One more closeout-oriented replay is recorded after the gold set is expanded with additional weak-fit cases.

### 5. Documentation Baseline

- [x] The Phase 2 phase brief reflects the real implementation baseline.
- [x] The runbook reflects the real operator workflow.
- [x] The validation plan reflects the gold-set and routing layers.
- [x] The weak-fit routing policy is documented.
- [x] This closeout checklist exists and is linked from the phase docs.
- [x] The explicit residual-items record exists so deferred work is not confused with hidden blockers.
- [x] The Phase 3 entry checklist exists before Phase 2 is treated as passable.
- [x] The formal closeout review exists.

## What Is Still Intentionally Open

No remaining closeout blockers are open.

The former gold-set breadth question was resolved in [PHASE_2_ACCEPTANCE_BATCH_7.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/PHASE_2_ACCEPTANCE_BATCH_7.md), and the formal closeout is now recorded in [PHASE_2_CLOSEOUT.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_CLOSEOUT.md).

## Explicitly Deferred Out Of Phase 2 Closeout

The following items are now recorded as later follow-up work rather than current closeout blockers:

1. external AI provider-backed micro-skills,
2. `smooth_section_copy`,
3. AI-assisted taxonomy support,
4. routing as a hard pre-draft gate,
5. stronger pre-draft content-fit gating.

Reference:

1. [PHASE_2_RESIDUAL_ITEMS.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/phases/PHASE_2_RESIDUAL_ITEMS.md)

## What Is Explicitly Not Required For Closeout

Do not hold Phase 2 open waiting for:

1. WordPress publishing,
2. Facebook packaging,
3. scheduling logic,
4. analytics dashboards,
5. OpenClaw or agent orchestration,
6. full-article AI generation.

Those belong to later phases or are explicitly out of scope.

## Current Status

Phase 2 is now closeout-ready and formally recorded as passed with explicit residual risks.

The current strongest evidence is:

1. deterministic formatting, review, health reporting, and routing are all implemented,
2. the unittest suite and the fixed gold set both pass,
3. live acceptance batches have already exposed the real quality gaps instead of hiding them,
4. bounded headline-variant replay now shows safer title-shape-aware heuristic behavior instead of generic wrapper output,
5. the template layer now has executable slot-level enforcement instead of relying only on prose guidance,
6. post-closeout hardening now protects against stale approvals after intro rewrites and against unsafe cross-family template overrides.

The remaining follow-up work is now later-phase or post-closeout work only.

## Exit Rule

Phase 2 can be proposed for closeout only when every unchecked item in this file is either:

1. completed, or
2. explicitly moved to a later phase with written justification in the phase docs.
