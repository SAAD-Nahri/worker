# Facebook Publish State Update Workflow V1

## Purpose

This document defines the first local update workflow for Phase 3 Facebook publish records.

The goal is to let the operator record explicit Facebook-side progress without forcing a live transport adapter into the architecture too early.

## Core Rule

The Facebook publish record is append-only.

State changes should be recorded as new snapshots, not silent mutation of old records.

## Required Anchors

Each Facebook publish update begins from:

1. `social_package_id`
2. latest social package snapshot
3. linked `blog_publish_id`
4. latest blog publish snapshot with a confirmed blog URL
5. action-specific fields when required

The workflow should key from `social_package_id`, not from `blog_publish_id` alone, so replacement packages do not accidentally inherit the wrong publish state.

## Allowed V1 Update Actions

The local workflow should support these explicit actions:

1. `scheduled`
2. `published`
3. `failed`

These actions should update the latest `FacebookPublishRecord` snapshot and refresh queue/mapping state when appropriate.

## Action Rules

### `scheduled`

Requires:

1. approved social package
2. confirmed blog URL
3. `facebook_post_id`
4. `scheduled_for_facebook`
5. `schedule_mode`

### `published`

Requires:

1. approved social package
2. confirmed blog URL
3. `facebook_post_id`
4. `published_at_facebook`

Optional but useful:

1. `scheduled_for_facebook` when the publish came from a previously scheduled post

### `failed`

Requires:

1. approved social package
2. confirmed blog URL
3. `error_message`

Failure should not erase already known Facebook identifiers or scheduled timestamps.

## Queue And Mapping Effect

After a new Facebook publish snapshot is recorded, the workflow should refresh:

1. the Facebook queue record
2. the blog-to-Facebook mapping record

Expected v1 behavior:

1. `scheduled` should move the Facebook queue into `scheduled_facebook`
2. `published` should move the Facebook queue into `published_facebook`
3. `failed` should move the Facebook queue into `facebook_publish_failed`
4. `scheduled` should move the mapping into `social_queued`
5. `published` should move the mapping into `social_published`
6. `failed` should move the mapping into `social_publish_failed`
7. final mapping snapshots should preserve `facebook_publish_id`

## Required Record Fields

Each local Facebook publish snapshot should preserve at minimum:

1. `facebook_publish_id`
2. `social_package_id`
3. `draft_id`
4. `blog_publish_id`
5. `destination_type`
6. `publish_status`
7. `facebook_post_id` when available
8. `schedule_mode` when scheduled
9. `schedule_approved_by` when scheduled
10. `schedule_applied_by` when scheduled
11. `scheduled_for_facebook` when available
12. `published_at_facebook` when available
13. `last_publish_attempt_at`
14. `last_publish_result`
15. `last_error`
16. `created_at`
17. `updated_at`

## What Must Be Avoided

Do not:

1. record Facebook publish outcomes against the wrong package when a newer replacement package exists
2. mark Facebook publication as successful without a recorded publish identifier
3. let a failed Facebook action erase the selected hook, caption, and comment CTA from the mapping chain
4. overwrite old Facebook publish snapshots

## Definition Of Done

This spec is satisfied when:

1. local Facebook publish-state updates are explicit
2. required fields are known per update action
3. queue and mapping refresh behavior is clear enough for implementation
4. Facebook publish identifiers are preserved before live transport exists
