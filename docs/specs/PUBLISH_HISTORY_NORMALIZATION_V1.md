# Publish History Normalization V1

## Purpose

This document defines how Phase 4 should normalize the existing append-only runtime records into a tracking-ready publish history layer.

The goal is not to replace the runtime logs. The goal is to build one stable, queryable view of what actually happened across:

1. source intake,
2. draft creation,
3. blog publish preparation and publish state,
4. social packaging,
5. Facebook publish state.

## Core Rule

The append-only runtime records remain the source of truth.

Phase 4 should add a normalized tracking layer on top of them. It should not:

1. rewrite the raw JSONL records,
2. collapse the append-only history into one mutable blob,
3. infer lineage from titles, slugs, or URLs when IDs already exist.

## Authoritative Runtime Inputs

Phase 4 normalization should read from:

1. [data/source_items.jsonl](C:/Users/Administrator/OneDrive/Documents/co_ma/data/source_items.jsonl)
2. [data/draft_records.jsonl](C:/Users/Administrator/OneDrive/Documents/co_ma/data/draft_records.jsonl)
3. [data/draft_reviews.jsonl](C:/Users/Administrator/OneDrive/Documents/co_ma/data/draft_reviews.jsonl)
4. [data/blog_publish_records.jsonl](C:/Users/Administrator/OneDrive/Documents/co_ma/data/blog_publish_records.jsonl)
5. [data/social_package_records.jsonl](C:/Users/Administrator/OneDrive/Documents/co_ma/data/social_package_records.jsonl)
6. [data/social_package_reviews.jsonl](C:/Users/Administrator/OneDrive/Documents/co_ma/data/social_package_reviews.jsonl)
7. [data/facebook_publish_records.jsonl](C:/Users/Administrator/OneDrive/Documents/co_ma/data/facebook_publish_records.jsonl)
8. [data/queue_item_records.jsonl](C:/Users/Administrator/OneDrive/Documents/co_ma/data/queue_item_records.jsonl)
9. [data/blog_facebook_mapping_records.jsonl](C:/Users/Administrator/OneDrive/Documents/co_ma/data/blog_facebook_mapping_records.jsonl)

## Normalization Unit

The primary normalization unit for v1 should be the publish chain keyed by `blog_publish_id`.

Why this is the right unit:

1. blog publishing is the first public content layer in the current business model,
2. Facebook packaging and Facebook publishing already hang off the blog publish record,
3. queue and mapping records already use `blog_publish_id` as a stable chain anchor,
4. this avoids inventing a second lineage root during Phase 4.

## Required Normalized Tracking Fields

Each normalized publish-history row should preserve at minimum:

### Identity fields

1. `publish_chain_id`
2. `source_item_id`
3. `source_id`
4. `draft_id`
5. `blog_publish_id`
6. `social_package_id` when available
7. `facebook_publish_id` when available

### Source fields

1. `source_family`
2. `source_url`
3. `canonical_source_url`
4. `source_title`
5. `source_published_at`
6. `dedupe_status`

### Draft fields

1. `template_id`
2. `template_family`
3. `draft_language`
4. `draft_workflow_state`
5. `draft_approval_state`
6. `draft_quality_gate_status`
7. `draft_derivative_risk_level`
8. `category`
9. `tag_candidates`

### Blog publish fields

1. `wordpress_title`
2. `wordpress_slug`
3. `wordpress_category`
4. `wordpress_tags`
5. `wordpress_post_id`
6. `wordpress_post_url`
7. `wordpress_status`
8. `publish_intent`
9. `schedule_mode_blog`
10. `scheduled_for_blog`
11. `published_at_blog`
12. `last_blog_publish_result`
13. `last_blog_publish_error`

### Social package fields

1. `package_template_id`
2. `comment_template_id`
3. `selected_variant_label`
4. `hook_text`
5. `caption_text`
6. `comment_cta_text`
7. `social_package_approval_state`
8. `target_destination`

### Facebook publish fields

1. `facebook_post_id`
2. `facebook_publish_status`
3. `schedule_mode_facebook`
4. `scheduled_for_facebook`
5. `published_at_facebook`
6. `last_facebook_publish_result`
7. `last_facebook_publish_error`
8. `facebook_destination_type`

### Workflow summary fields

1. `blog_queue_state`
2. `facebook_queue_state`
3. `mapping_status`
4. `chain_last_updated_at`

## Normalization Rules

### 1. Latest-snapshot rule

Use the latest record for each ID from the append-only files.

Phase 4 should not:

1. assume the first record is the current truth,
2. guess state from stale snapshots,
3. sort by an invented version counter that does not exist.

### 2. Canonical ID rule

Normalize the source-item key name to `source_item_id` in the tracking layer even though the raw Source Engine model currently uses `item_id`.

That means:

1. `SourceItem.item_id` becomes `source_item_id` in normalized tracking rows,
2. downstream tracking code should stop leaking the `item_id` naming inconsistency into later layers.

### 3. Selected-output rule

When both a social package record and a mapping record are available, the normalized row should prefer the mapping record for selected output values.

That is because the mapping record is the accepted Phase 3 contract for:

1. `selected_blog_title`
2. `selected_hook_text`
3. `selected_caption_text`
4. `selected_comment_cta_text`

### 4. Confirmed-URL rule

Use `wordpress_post_url` or `blog_url` only when the latest record contains a confirmed value.

Do not:

1. regenerate the URL from the slug,
2. fall back to the source URL,
3. assume a draft preview link is the public URL.

### 5. Partial-chain rule

Tracking rows may exist for partial chains.

Examples:

1. blog-ready with no social package yet,
2. packaged social with no Facebook publish yet,
3. failed WordPress publish with no confirmed post ID,
4. failed Facebook publish with preserved selected package values.

Phase 4 should keep these rows visible instead of filtering them out.

## What Should Stay Out Of The Normalized Row

Do not copy large content payloads into the normalized history row when references are enough.

Keep out:

1. full `raw_body_text`,
2. full `wordpress_body_html`,
3. full draft section bodies,
4. whole approval-note histories.

Those remain available in the authoritative runtime records.

## Known Gaps That Phase 4 Must Handle Explicitly

The current runtime baseline is strong, but these normalization gaps still need explicit treatment:

1. the source-item identity field name is inconsistent between runtime and later specs,
2. actor fields such as `created_by` and `last_modified_by` are not uniformly present across runtime models,
3. variant identity is partially text-based rather than fully ID-based,
4. report-ready publish history does not yet exist as a dedicated normalized layer.

## What Must Be Avoided

Do not:

1. invent a second lineage root instead of using `blog_publish_id`,
2. throw away failed or partial chains,
3. infer joins from slugs, titles, or timestamps when IDs are already present,
4. duplicate large blobs into the tracking history row,
5. treat the normalized layer as a replacement for the raw runtime records.

## Definition Of Done

This spec is satisfied when:

1. the repo has one explicit normalized publish-history row contract,
2. the row is grounded in existing runtime records,
3. partial, failed, scheduled, and published chains all remain representable,
4. Phase 4 implementation can begin without guessing which fields belong in the tracking layer.

## Current Baseline

The current repo now implements the first normalization layer as an on-demand reporting baseline in `tracking_engine`.

That means:

1. normalization exists,
2. lineage joins exist,
3. reporting views exist,
4. persisted normalized snapshot storage is still intentionally deferred,
5. the current persistence decision is documented in [PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/PUBLISH_CHAIN_SNAPSHOT_PERSISTENCE_POLICY_V1.md).
