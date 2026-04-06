# Publish Chain Snapshot Contract V1

## Purpose

This document defines the first derived tracking object for Phase 4.

The goal is to create one operator-readable, reporting-ready snapshot for each publish chain without replacing the append-only runtime records created in earlier phases.

## Core Rule

Phase 4 must not invent a second source of truth.

The source of truth remains the append-only records created in:

1. Source Engine,
2. Content Engine,
3. Distribution Engine.

The publish-chain snapshot is a derived view built from those records so reporting and later analysis do not need to replay every raw record by hand.

## Snapshot Scope

Each v1 snapshot represents one primary chain:

1. source item,
2. draft,
3. blog publish record,
4. selected social package,
5. Facebook publish record when available,
6. latest queue and mapping state.

V1 does not attempt to model every possible future branch or experiment family.

## Snapshot Identity

Each snapshot should preserve at minimum:

1. `chain_id`
2. `source_item_id`
3. `draft_id`
4. `blog_publish_id`
5. `social_package_id` when available
6. `facebook_publish_id` when available
7. `snapshot_generated_at`
8. `snapshot_version`

Recommended v1 rule:

1. `chain_id` should be derived from `blog_publish_id`

That keeps one primary blog publish record as the anchor for the full chain.

## Required Source Fields

At minimum preserve:

1. `source_id`
2. `source_name`
3. `source_family`
4. `source_url`
5. `canonical_url`
6. `source_title`
7. `source_published_at`
8. `source_dedupe_status`

## Required Draft Fields

At minimum preserve:

1. `template_id`
2. `template_family`
3. `draft_workflow_state`
4. `draft_approval_state`
5. `quality_gate_status`
6. `derivative_risk_level`
7. `category`
8. `tag_candidates`
9. `headline_selected`
10. `headline_variants_count`
11. `draft_created_at`
12. `draft_updated_at`

## Required Blog Publish Fields

At minimum preserve:

1. `wordpress_status`
2. `publish_intent`
3. `wordpress_post_id`
4. `wordpress_post_url`
5. `wordpress_title`
6. `wordpress_slug`
7. `wordpress_category`
8. `wordpress_tags`
9. `schedule_mode_blog`
10. `scheduled_for_blog`
11. `published_at_blog`
12. `blog_last_error`

## Required Social Package Fields

At minimum preserve:

1. `package_template_id`
2. `comment_template_id`
3. `social_approval_state`
4. `selected_variant_label`
5. `hook_text`
6. `caption_text`
7. `comment_cta_text`
8. `target_destination`
9. `blog_url_used_in_package`
10. `social_packaging_notes`

## Required Facebook Publish Fields

At minimum preserve:

1. `facebook_publish_status`
2. `facebook_post_id`
3. `destination_type`
4. `schedule_mode_facebook`
5. `scheduled_for_facebook`
6. `published_at_facebook`
7. `facebook_last_error`

## Required Workflow Fields

At minimum preserve:

1. `blog_queue_state`
2. `blog_queue_approval_state`
3. `facebook_queue_state`
4. `facebook_queue_approval_state`
5. `mapping_status`
6. `has_confirmed_blog_url`
7. `has_social_package`
8. `has_facebook_publish_record`

## Join Rules

The v1 lineage join rules are:

1. `source_item_id` joins source item to draft
2. `draft_id` joins draft to blog publish and social package
3. `blog_publish_id` anchors the main publish chain
4. `social_package_id` joins the selected package to Facebook publish and mapping state
5. `facebook_publish_id` is optional until Facebook publish work exists for that chain

## Latest-Record Rule

When Phase 4 derives a publish-chain snapshot:

1. use the latest append-only record for each entity type
2. never mutate older records to "fix" history
3. keep report generation deterministic by using explicit latest-snapshot rules

## Missing-Link Rule

If part of the chain is missing, the snapshot should still exist.

It should preserve:

1. the known fields,
2. the missing-link condition,
3. the latest visible workflow state.

This is required so reporting remains useful for:

1. blog-only chains,
2. packaging-pending chains,
3. failed publish attempts,
4. manually deferred social steps.

## What This Snapshot Is Not

This snapshot is not:

1. a BI warehouse,
2. a click analytics table,
3. a replacement for append-only publish history,
4. a future winner-detection model.

It is a normalized reporting object for the current content and distribution chain.

## Definition Of Done

This contract is satisfied when:

1. one stable chain-level snapshot shape exists,
2. the snapshot is derived from current append-only records,
3. missing links remain visible instead of being dropped,
4. Phase 4 reporting can build on this object without redefining lineage.

## Current Persistence Position

For the current Phase 4 baseline, this snapshot remains an on-demand derived object.

It is not yet a persisted runtime artifact.

The persistence decision and future trigger conditions are documented in [PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md).
