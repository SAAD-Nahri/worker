# Publish History Schema

## Purpose

This document defines the minimum publish-history model required for v1.

The goal is not to create a full analytics warehouse. The goal is to preserve enough structured history that the operator can trace what happened and the later decision layer can learn from real activity.

## Core Requirement

Every published or queued item must be traceable from:

source item -> blog draft -> blog post -> Facebook package -> Facebook post

If that chain breaks, later analysis becomes weak and debugging becomes harder.

## Minimum V1 Records

V1 should preserve at least the following logical record types:

1. source item record,
2. blog draft record,
3. blog publish record,
4. Facebook package record,
5. Facebook publish record.

These can be represented in one store or multiple linked stores, but the identifiers and relationships must be preserved.

## Required Source Item Fields

At minimum:

1. `source_item_id`
2. `source_id`
3. `source_family`
4. `source_url`
5. `canonical_url`
6. `raw_title`
7. `published_at_source` when available
8. `discovered_at`
9. `dedupe_status`

## Required Blog Draft Fields

At minimum:

1. `draft_id`
2. `source_item_id`
3. `template_id`
4. `draft_title`
5. `category`
6. `tags`
7. `review_status`
8. `created_at`
9. `updated_at`

## Required Blog Publish Fields

At minimum:

1. `blog_publish_id`
2. `draft_id`
3. `wordpress_post_id`
4. `final_title`
5. `slug` when available
6. `schedule_mode` when scheduled
7. `published_at_blog`
8. `queue_batch_id` when applicable
9. `publish_status`

## Required Facebook Package Fields

At minimum:

1. `social_package_id`
2. `draft_id` or `blog_publish_id`
3. `package_template_id`
4. `hook_variant_id`
5. `caption_variant_id`
6. `comment_cta_variant_id`
7. `created_at`
8. `approval_status`

## Required Facebook Publish Fields

At minimum:

1. `facebook_publish_id`
2. `social_package_id`
3. `facebook_post_id` when available
4. `schedule_mode` when scheduled
5. `publish_status`
6. `scheduled_for`
7. `published_at_facebook`
8. `destination_type`

For v1, `destination_type` should primarily be `facebook_page`.

## Minimum Relationship Rules

The schema must make it possible to answer:

1. which source item produced this blog post,
2. which blog post produced this Facebook post,
3. which template was used,
4. which title variant was used,
5. when the item was published,
6. what state or approval outcome it had.

## Required Variant Recording

V1 does not need deep experimentation infrastructure, but it should preserve the selected variant for:

1. blog title,
2. Facebook hook,
3. Facebook caption,
4. comment CTA when one is used.

## Suggested Minimal Audit Fields

Every major record should preserve:

1. `created_at`
2. `updated_at`
3. `created_by`
4. `last_modified_by`

These can be human or system markers.

## What This Schema Does Not Need Yet

V1 does not need:

1. full clickstream analytics,
2. detailed attribution logic,
3. BI-layer denormalization,
4. advanced performance cohorts,
5. complex experiment tracking.

## Why This Matters

If the project cannot answer "what source became what published content and how was it packaged," then later winner detection will be mostly guesswork.

## Definition Of Done

This spec is satisfied when:

1. the source-to-blog-to-Facebook chain is representable,
2. publish history is queryable by item lineage,
3. chosen variants are preserved,
4. the v1 schema remains simple enough for a solo-operator system.
