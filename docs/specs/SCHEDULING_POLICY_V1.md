# Scheduling Policy V1

## Purpose

This document defines the first explicit scheduling policy for Phase 3.

The goal is to let the system support scheduling without quietly sliding into blind automation.

## Core Rule

Scheduling is not the same thing as publishing.

Scheduling is a governed decision that must preserve:

1. whether the schedule was manual or auto,
2. who approved that schedule path,
3. who or what applied the schedule,
4. the exact scheduled timestamp.

## Allowed Schedule Modes

V1 allows only:

1. `manual`
2. `auto`

### `manual`

Meaning:

1. the operator explicitly chose the schedule for this item,
2. the operator is both the approval source and the applied-by actor unless recorded otherwise.

### `auto`

Meaning:

1. the operator already approved the item for scheduling,
2. the actual timestamp application was performed by a system scheduling actor,
3. the auto path is still traceable and reversible.

V1 should use `system_auto_scheduler` as the default system scheduling actor label.

## Blog Scheduling Rules

### Manual blog scheduling

Allowed only when:

1. a WordPress draft already exists,
2. the item has a `wordpress_post_id`,
3. the schedule timestamp is explicit.

### Auto blog scheduling

Allowed only when:

1. the same prerequisites as manual scheduling are already satisfied,
2. the blog publish record was prepared with `publish_intent = schedule`,
3. the item already represents an intentional schedule candidate rather than a generic draft.

## Facebook Scheduling Rules

### Manual Facebook scheduling

Allowed only when:

1. the selected social package is approved,
2. the linked blog post already has a confirmed blog URL,
3. the linked blog publish record is already `scheduled` or `published`,
4. the Facebook schedule does not precede the linked blog schedule when the blog is scheduled.

### Auto Facebook scheduling

Allowed only when:

1. the same prerequisites as manual Facebook scheduling are already satisfied,
2. the schedule application is recorded with the system scheduling actor,
3. the chosen social package remains the selected package of record.

## Required Schedule Metadata

Whenever a scheduled state is recorded, the publish snapshot should preserve:

1. `schedule_mode`
2. `schedule_approved_by`
3. `schedule_applied_by`

This applies to:

1. `BlogPublishRecord`
2. `FacebookPublishRecord`

## Queue Impact

Scheduling policy should affect queue interpretation:

1. WordPress drafts prepared with `publish_intent = schedule` and a remote draft should be visible as `ready_for_blog_schedule`
2. a recorded blog schedule should move the queue to `scheduled_blog`
3. a recorded Facebook schedule should move the queue to `scheduled_facebook`

## What Must Be Avoided

Do not:

1. treat a schedule timestamp as proof that approval happened,
2. let auto scheduling run without preserving who approved the auto path,
3. schedule Facebook before the linked blog schedule or publish time,
4. let replacement Facebook packages inherit stale scheduling state from earlier packages.

## Definition Of Done

This spec is satisfied when:

1. manual and auto scheduling are both explicitly modeled,
2. scheduling decisions preserve approval and application metadata,
3. blog and Facebook scheduling rules are conservative enough for v1,
4. queue behavior can reflect the scheduling policy without guessing.
