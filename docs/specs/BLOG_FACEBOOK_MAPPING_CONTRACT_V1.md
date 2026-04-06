# Blog-Facebook Mapping Contract V1

## Purpose

This document defines the operational mapping contract between:

1. approved draft,
2. WordPress publish record,
3. Facebook package record,
4. Facebook publish record.

The goal is to preserve the source-to-blog-to-Facebook chain during Phase 3, before Phase 4 expands the tracking layer.

## Core Rule

Every public Facebook output must be traceable back to the exact approved draft and the exact blog post it promotes.

If that chain is weak, later tracking and decision work becomes mostly guesswork.

## Mapping Scope

This contract exists for operational linkage.

It should answer:

1. which draft produced this WordPress post,
2. which WordPress post produced this Facebook package,
3. which selected hook/caption/comment CTA were used,
4. which Facebook post was published from that package.

It is not yet a performance analytics model.

## Required Mapping Fields

Each mapping record should preserve at minimum:

1. `mapping_id`
2. `source_item_id`
3. `draft_id`
4. `blog_publish_id`
5. `social_package_id` when available
6. `facebook_publish_id` when available
7. `selected_blog_title`
8. `selected_hook_text`
9. `selected_caption_text`
10. `selected_comment_cta_text`
11. `blog_url`
12. `facebook_destination_type`
13. `mapping_status`
14. `created_at`
15. `updated_at`

## Relationship Rules

V1 relationship assumptions:

1. one approved draft maps to one primary blog publish record,
2. one blog publish record may have zero or more derived Facebook packages,
3. one selected Facebook package maps to at most one published Facebook post in the first live workflow,
4. the mapping record should preserve the selected package even if Facebook publication fails later.

## Mapping Status Values

Suggested v1 mapping statuses:

1. `blog_only`
2. `packaged_social_pending`
3. `social_queued`
4. `social_published`
5. `social_publish_failed`

These statuses are operational summaries, not replacements for the underlying publish records.

## Variant Preservation Rule

The mapping record must preserve the selected output values, not just generic variant IDs.

That means v1 should keep:

1. the final WordPress title,
2. the chosen Facebook hook text,
3. the chosen caption text,
4. the chosen comment CTA text.

This keeps the first tracking layer useful even before a larger experiment system exists.

## URL Rule

The mapping record should preserve the final blog URL whenever available.

Facebook packages should use that final URL, not:

1. a source URL,
2. a placeholder draft link,
3. a guessed permalink string when WordPress has already returned the real one.

## Failure Handling

If Facebook publication fails after a package is selected:

1. keep the mapping record,
2. keep the selected package values,
3. update `mapping_status`,
4. preserve the failure in the Facebook publish record rather than discarding the chain.

## What Must Be Avoided

Do not:

1. derive Facebook packages from raw source URLs,
2. drop the selected packaging fields from the mapping,
3. treat a published Facebook post as independent from the approved draft,
4. wait until Phase 4 to decide how blog and Facebook outputs are linked.

## Definition Of Done

This spec is satisfied when:

1. the repo has an explicit mapping record shape,
2. the WordPress-to-Facebook linkage is defined clearly enough for implementation,
3. selected packaging values are preserved,
4. Phase 4 can later build on this contract instead of inventing it from scratch.
