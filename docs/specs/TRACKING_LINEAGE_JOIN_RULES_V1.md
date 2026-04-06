# Tracking Lineage Join Rules V1

## Purpose

This document defines how Phase 4 should join the existing runtime records into one traceable lineage model.

The goal is to make the source-to-blog-to-Facebook chain explicit without redefining the Phase 3 contracts.

## Core Rule

Lineage joins must use explicit IDs first.

Do not join chains by:

1. title similarity,
2. slug similarity,
3. URL guesswork,
4. publish timestamps alone.

## Existing Runtime Lineage Fields

The current repo already exposes the following join-capable fields:

### Source item

1. `SourceItem.item_id`
2. `SourceItem.source_id`
3. `SourceItem.source_family`

### Draft

1. `DraftRecord.draft_id`
2. `DraftRecord.source_item_id`
3. `DraftRecord.source_id`
4. `DraftRecord.template_id`
5. `DraftRecord.template_family`

### Blog publish

1. `BlogPublishRecord.blog_publish_id`
2. `BlogPublishRecord.draft_id`
3. `BlogPublishRecord.source_item_id`
4. `BlogPublishRecord.template_id`

### Social package

1. `SocialPackageRecord.social_package_id`
2. `SocialPackageRecord.draft_id`
3. `SocialPackageRecord.blog_publish_id`
4. `SocialPackageRecord.package_template_id`
5. `SocialPackageRecord.comment_template_id`

### Facebook publish

1. `FacebookPublishRecord.facebook_publish_id`
2. `FacebookPublishRecord.social_package_id`
3. `FacebookPublishRecord.draft_id`
4. `FacebookPublishRecord.blog_publish_id`

### Queue

1. `QueueItemRecord.queue_item_id`
2. `QueueItemRecord.queue_type`
3. `QueueItemRecord.draft_id`
4. `QueueItemRecord.blog_publish_id`
5. `QueueItemRecord.social_package_id`

### Mapping

1. `BlogFacebookMappingRecord.mapping_id`
2. `BlogFacebookMappingRecord.source_item_id`
3. `BlogFacebookMappingRecord.draft_id`
4. `BlogFacebookMappingRecord.blog_publish_id`
5. `BlogFacebookMappingRecord.social_package_id`
6. `BlogFacebookMappingRecord.facebook_publish_id`

## Required Join Path

The default Phase 4 lineage path should be:

1. source item
2. draft
3. blog publish
4. social package
5. Facebook publish

Queue and mapping records are supporting views of that chain, not replacements for it.

## Join Rules

### 1. Source item -> draft

Join on:

1. `DraftRecord.source_item_id`
2. normalized `SourceItem.item_id` as `source_item_id`

### 2. Draft -> blog publish

Join on:

1. `BlogPublishRecord.draft_id`

Use `blog_publish_id` as the durable public-chain anchor after this step.

### 3. Blog publish -> social package

Preferred join:

1. `SocialPackageRecord.blog_publish_id`

Fallback join:

1. `SocialPackageRecord.draft_id`

Fallback is allowed only when:

1. `blog_publish_id` is still null,
2. the social package is still a partial pre-linkage record,
3. the chain is marked as incomplete until a `blog_publish_id` is present.

### 4. Social package -> Facebook publish

Join on:

1. `FacebookPublishRecord.social_package_id`

### 5. Blog publish -> queue items

Join on:

1. `QueueItemRecord.blog_publish_id`
2. `QueueItemRecord.queue_type`

Expected queue rows:

1. one `blog_publish` queue row per publish chain,
2. one `facebook_publish` queue row per publish chain once social packaging exists or is pending.

### 6. Blog publish -> mapping

Join on:

1. `BlogFacebookMappingRecord.blog_publish_id`

Preferred supporting joins:

1. `social_package_id`
2. `facebook_publish_id`

## Latest-Snapshot Join Rule

All joins must operate on the latest snapshot for each ID.

That means:

1. latest draft record for `draft_id`,
2. latest blog publish record for `blog_publish_id`,
3. latest social package record for `social_package_id`,
4. latest Facebook publish record for `facebook_publish_id`,
5. latest queue record per `blog_publish_id` and `queue_type`,
6. latest mapping record for `blog_publish_id`.

## Precedence Rules

When multiple records expose overlapping information, use this precedence:

### Selected blog and social values

1. mapping record
2. blog publish or social package record
3. draft record

### Blog URL

1. latest confirmed `wordpress_post_url`
2. mapping `blog_url` when it matches the confirmed published chain

### Publish status

1. blog publish and Facebook publish records remain the source of truth for platform-side publish state
2. queue and mapping states remain operator summaries

## Partial And Failed Chain Rules

Do not drop incomplete chains.

Phase 4 lineage must preserve:

1. blog-ready chains with no social package,
2. packaged chains with no Facebook publish yet,
3. WordPress failures,
4. Facebook failures,
5. rerouted or blog-only chains.

## Known Join Gaps

The current repo already has enough fields to join the chain, but these weak spots must stay explicit:

1. `SourceItem.item_id` versus later `source_item_id` naming needs normalization,
2. some social packages can exist before final blog linkage,
3. actor fields are not uniform across the chain,
4. queue and mapping rows summarize state but should never override the underlying publish records.

## What Must Be Avoided

Do not:

1. join Facebook publish rows directly to source items,
2. treat queue rows as the primary lineage table,
3. let mapping status replace platform publish status,
4. infer lineage from source URLs after a draft and blog publish ID already exist.

## Definition Of Done

This spec is satisfied when:

1. the repo has one explicit join path from source item to Facebook publish,
2. the precedence rules are clear,
3. partial chains remain representable,
4. Phase 4 code can build lineage without guessing.
