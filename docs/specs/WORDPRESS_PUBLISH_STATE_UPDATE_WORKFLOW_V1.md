# WordPress Publish State Update Workflow V1

## Purpose

This document defines the first explicit update workflow for Phase 3 WordPress publish records.

The goal is to let the operator record meaningful post-preparation progress whether the update is entered manually or produced by the first live WordPress REST draft-sync adapter.

## Core Rule

The WordPress publish record is append-only.

State changes should be recorded as new snapshots, not silent mutation of old records.

## Allowed V1 Update Actions

The local workflow should support these explicit actions:

1. `draft_created`
2. `draft_updated`
3. `scheduled`
4. `published`
5. `failed`

These actions should update the latest `BlogPublishRecord` snapshot and refresh queue/mapping state when appropriate.

## Required Inputs

Each update begins from:

1. `blog_publish_id`
2. latest blog publish snapshot
3. action-specific fields when required

## Action Rules

### `draft_created`

Requires:

1. `wordpress_post_id`

Optional but useful:

1. `wordpress_post_url`

### `draft_updated`

Requires:

1. `wordpress_post_id`

### `scheduled`

Requires:

1. `wordpress_post_id`
2. `scheduled_for_blog`
3. `schedule_mode`

Optional but useful:

1. `wordpress_post_url`
2. `schedule_approved_by`
3. `schedule_applied_by`

### `published`

Requires:

1. `wordpress_post_id`
2. `wordpress_post_url`
3. `published_at_blog`

### `failed`

Requires:

1. `error_message`

Failure should not erase existing WordPress identifiers already known.

## Queue And Mapping Effect

After a new blog publish snapshot is recorded, the workflow should refresh:

1. the blog queue record,
2. the Facebook queue record when a linked social package exists,
3. the blog-to-Facebook mapping record.

Expected v1 behavior:

1. confirmed WordPress draft creation should move the blog queue into `wordpress_draft_created`,
2. schedule-intent records with a remote WordPress draft should move the blog queue into `ready_for_blog_schedule`,
3. scheduling should move the blog queue into `scheduled_blog`,
3. publication should move the blog queue into `published_blog`,
4. a linked approved social package may become `approved_for_queue` once the blog URL is confirmed,
5. failure should remain visible in both the blog publish snapshot and the refreshed queue state.

## What Must Be Avoided

Do not:

1. overwrite old publish snapshots,
2. drop `last_error` visibility on failed attempts,
3. update queue state without a corresponding publish snapshot.

## Definition Of Done

This spec is satisfied when:

1. local WordPress publish-state updates are explicit,
2. required fields are known per update action,
3. queue and mapping refresh behavior is clear enough for implementation.
