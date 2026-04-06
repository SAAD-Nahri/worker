# Asset Record And Linkage Contract V1

## Purpose

This document defines the first asset record shape for the media phase.

## Core Rule

An asset is not “ready” unless its provenance, review state, and intended linkage are visible.

## Required Linkage Targets

An asset record must support linkage to:

1. `draft_id`
2. `blog_publish_id`
3. `social_package_id`

At least `draft_id` is required.

## Required Baseline Fields

The first asset record should contain at minimum:

1. `asset_record_id`
2. `draft_id`
3. `blog_publish_id`
4. `social_package_id`
5. `asset_source_kind`
6. `provenance_reference`
7. `approval_state`
8. `intended_usage`
9. `asset_url_or_path`
10. `alt_text`
11. `caption_support_text`
12. `created_at`
13. `updated_at`

## Allowed Source Kinds

The first allowed values are:

1. `owned`
2. `licensed`
3. `ai_generated`

## Approval States

The first allowed values should include:

1. `pending_review`
2. `approved`
3. `needs_edits`
4. `rejected`

## Readiness Rule

Blog and Facebook outputs must not be treated as asset-complete until the linked asset record is approved.

## Definition Of Done

This spec is satisfied when asset records can preserve:

1. source kind,
2. provenance,
3. approval state,
4. publish-chain linkage,
5. minimum accessibility support fields.
