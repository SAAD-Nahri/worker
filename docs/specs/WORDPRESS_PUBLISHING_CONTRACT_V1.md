# WordPress Publishing Contract V1

## Purpose

This document defines the first Phase 3 contract for turning an approved draft into a WordPress publishable object.

The goal is to define the application-facing publish contract clearly enough that transport details stay downstream and replaceable.

## Core Rule

WordPress publishing begins from an approved draft record.

It does not begin from:

1. a raw source item,
2. an unreviewed draft,
3. a Facebook package,
4. a manually pasted article with no lineage.

The WordPress layer is a renderer and publishing adapter, not a new writing engine.

## Upstream Inputs

The minimum upstream requirements are:

1. `draft_id`
2. `source_item_id`
3. `template_id`
4. `approval_state = approved`
5. `quality_gate_status = pass` or an explicit operator-approved exception
6. final headline selection
7. final category
8. final tag set
9. structured draft sections
10. excerpt

Reference inputs:

1. [DRAFT_RECORD_SPEC.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_RECORD_SPEC.md)
2. [DRAFT_REVIEW_WORKFLOW_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_REVIEW_WORKFLOW_V1.md)
3. [APPROVAL_WORKFLOW.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/APPROVAL_WORKFLOW.md)

## Publish Contract Scope

The WordPress publishing contract covers:

1. rendering a structured draft into WordPress-safe body content,
2. preserving lineage from draft to WordPress post,
3. creating or updating the minimal WordPress post fields required for v1,
4. recording the resulting WordPress publish state.

It does not yet cover:

1. theme customization,
2. media-library workflows,
3. SEO plugin metadata,
4. featured-image generation,
5. custom Gutenberg block design,
6. permalink strategy beyond basic slug creation.

## Required WordPress Payload Fields

Every WordPress-ready payload should contain at minimum:

1. `draft_id`
2. `source_item_id`
3. `template_id`
4. `wordpress_title`
5. `wordpress_slug`
6. `wordpress_excerpt`
7. `wordpress_body_html`
8. `wordpress_category`
9. `wordpress_tags`
10. `publish_intent`
11. `canonical_source_url`
12. `created_at`
13. `updated_at`

### `publish_intent`

Allowed v1 values:

1. `draft`
2. `schedule`
3. `publish_now`

The first live workflow should default to `draft` or `schedule`, not blind `publish_now`.

## Required Body Rendering Rules

The WordPress renderer must:

1. preserve the approved draft title exactly unless a later explicit publish edit changes it,
2. render intro and sections in the approved order,
3. keep paragraphs and bullets mobile-readable,
4. preserve template shape instead of flattening the article into one text blob,
5. support optional `related_read_bridge` content when present,
6. avoid silently introducing promotional copy or new claims.

### Minimum HTML Output Shape

The rendered body should support at minimum:

1. intro paragraph(s),
2. section headings,
3. paragraph blocks,
4. unordered lists for bullet sections,
5. closing recap or conclusion block,
6. optional related-read bridge paragraph.

The rendering layer should prefer simple HTML over theme-specific complexity.

## Slug Rules

The v1 slug rules should be simple and deterministic:

1. derive from the final approved title,
2. normalize to lowercase,
3. replace spaces with hyphens,
4. remove obvious punctuation noise,
5. let WordPress remain the final source of truth if it adjusts the slug.

## Category And Tag Rules

WordPress category and tag output should come from the approved draft taxonomy layer.

The publish layer may:

1. map internal category names to WordPress category names or IDs,
2. map internal tags to WordPress tag names or IDs.

The publish layer must not:

1. invent new categories dynamically,
2. bypass the approved taxonomy because WordPress allows looser tagging,
3. treat WordPress taxonomy as a replacement for the Content Engine taxonomy.

## Required Publish Record Fields

When the WordPress layer creates or updates a post, the resulting publish record should preserve:

1. `blog_publish_id`
2. `draft_id`
3. `source_item_id`
4. `wordpress_post_id`
5. `wordpress_post_url` when available
6. `wordpress_status`
7. `publish_intent`
8. `schedule_mode` when the post has been scheduled
9. `schedule_approved_by` when the post has been scheduled
10. `schedule_applied_by` when the post has been scheduled
11. `scheduled_for_blog` when the post has been scheduled
12. `published_at_blog` when available
13. `last_publish_attempt_at`
14. `last_publish_result`
15. `last_error` when a publish step fails

For the first implementation slice, a local prepared record may exist before any remote WordPress post exists. In that case:

1. `wordpress_post_id` may remain empty,
2. `wordpress_post_url` may remain empty,
3. `wordpress_status` should clearly show that the record is locally prepared, not remotely published.

## State Expectations

The WordPress layer should support these practical v1 outcomes:

1. WordPress payload prepared locally
2. WordPress draft created successfully
3. WordPress draft updated successfully
4. WordPress post scheduled successfully
5. WordPress post published successfully
6. WordPress publish failed with a visible error

The publish adapter should not hide partial failure.

## Transport Decision Boundary

This contract remains transport-stable even though the first adapter has now been selected.

The current first adapter is:

1. WordPress REST API with application-password authentication
2. draft create and draft update only
3. dry-run by default

Transport-specific behavior lives in:

1. [WORDPRESS_REST_TRANSPORT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_REST_TRANSPORT_V1.md)

The contract in this file should still not change just because the transport changes later.

## What Must Be Avoided

Do not:

1. publish directly from raw source content,
2. let WordPress publishing mutate the approved draft record silently,
3. mix Facebook packaging fields into the WordPress payload,
4. let theme-specific concerns redefine the body-rendering contract,
5. block Phase 3 planning on the final auth method choice.

## Definition Of Done

This spec is satisfied when:

1. the repo has an explicit WordPress-ready payload shape,
2. approved drafts can be rendered into a predictable WordPress body structure,
3. the output fields needed for v1 publishing are known,
4. publish-state recording is defined clearly enough for implementation to begin.
