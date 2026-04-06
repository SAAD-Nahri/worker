# Phase 4.7 Execution Plan

## Purpose

This document turns the media and asset layer into explicit implementation work.

The goal is to make blog and Facebook outputs operationally complete with a review-safe visual baseline.

## Execution Principle

Phase 4.7 should add the minimum asset system needed to support mixed-source visuals safely.

It should not become a broad creative platform.

## Slice 1: Asset Policy And Source Baseline

### Objective

Lock the first allowed asset source mix and the safety rules around it.

### Deliverables

1. mixed baseline with `owned`, `licensed`, and `ai_generated` assets,
2. explicit provenance requirements,
3. review-state requirements for every asset.

### Out Of Scope

1. scrape-first web reuse,
2. untracked media uploads,
3. video-first production.

## Slice 2: Asset Record Layer

### Objective

Add a first-class asset record that can attach to the current publish chain.

### Deliverables

1. asset record contract,
2. asset linkage to `draft_id`, `blog_publish_id`, and `social_package_id`,
3. asset approval and review fields,
4. intended-usage and alt-text support.

### Out Of Scope

1. asset versioning across many campaigns,
2. DAM-style search systems,
3. multi-channel asset orchestration.

## Slice 3: Media Brief Layer

### Objective

Derive a clear visual brief from approved draft context.

### Deliverables

1. media brief contract,
2. draft-to-brief generation rules,
3. operator-facing brief fields that support review and asset selection.

### Out Of Scope

1. broad creative ideation systems,
2. brand-strategy tooling.

## Slice 4: Distribution Integration

### Objective

Make asset readiness part of the publish path.

### Deliverables

1. WordPress featured-image readiness baseline,
2. Facebook asset readiness baseline,
3. blocked “asset-complete” behavior until media review passes.

### Out Of Scope

1. auto-publishing unreviewed visuals,
2. broad visual experimentation systems.

## Slice 5: Acceptance Replay

### Objective

Prove that one approved draft can receive a reviewed asset package that remains linked and visible.

### Deliverables

1. unit coverage for asset records and linkage,
2. integration coverage for publish-chain attachment,
3. a written Phase 4.7 acceptance batch.

### Out Of Scope

1. broad visual library migration,
2. production-scale asset operations.

## Exit Recommendation

Close Phase 4.7 only when:

1. mixed-source assets are provenance-tagged,
2. manual review gates remain explicit,
3. the publish chain can see and trust the asset linkage,
4. the system no longer treats visuals as an undefined side task.
