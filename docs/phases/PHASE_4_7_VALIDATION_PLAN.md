# Phase 4.7 Validation Plan

## Purpose

This document defines how the media and asset layer should be validated.

The focus is safe linkage, provenance visibility, and review enforcement.

## Validation Layers

Phase 4.7 validation has four layers:

1. asset-record validation,
2. media-brief validation,
3. distribution-linkage validation,
4. mixed-source acceptance replay.

## 1. Asset-Record Validation

Required unit coverage:

1. asset source kind is limited to `owned`, `licensed`, or `ai_generated`,
2. provenance or reference fields are required,
3. review state is explicit,
4. intended usage is explicit,
5. linkage to publish-chain IDs is preserved when present.

## 2. Media-Brief Validation

Required unit coverage:

1. media briefs can be generated from approved draft context,
2. brief outputs include enough context for asset selection or generation,
3. brief fields stay bounded and reusable.

## 3. Distribution-Linkage Validation

Required integration coverage:

1. blog and Facebook publish paths can see asset linkage,
2. “asset-complete” status is blocked until review passes,
3. asset metadata survives into operator-readable state.

## 4. Mixed-Source Acceptance Replay

Required acceptance work:

1. one approved draft is given a reviewed asset package,
2. the chosen asset source kind is recorded,
3. provenance and review state are visible,
4. blog/Facebook linkage remains coherent,
5. the result is recorded in a Phase 4.7 acceptance batch.

## Definition Of Pass

Phase 4.7 should be considered validated only when:

1. mixed-source assets are all reviewable and provenance-tagged,
2. asset linkage does not break the existing publish chain,
3. the system blocks unreviewed media from being treated as ready,
4. the first visual baseline is operationally understandable by one person.
