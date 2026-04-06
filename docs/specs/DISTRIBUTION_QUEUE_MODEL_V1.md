# Distribution Queue Model V1

## Purpose

This document defines the first queue-state model for Phase 3 blog publishing and Facebook packaging work.

The queue exists to keep the workflow reviewable, schedulable, and traceable. It should make public publishing safer, not more mysterious.

## Core Rule

Queue state is not the same thing as content quality state.

Quality and review belong upstream in Phase 2.

The Phase 3 queue starts after:

1. a draft is approved,
2. a WordPress-ready publish payload exists,
3. a Facebook-ready package exists or is intentionally pending.

## Queue Units

V1 should use two queue unit types:

1. `blog_publish`
2. `facebook_publish`

These should remain separate so the system can:

1. create a WordPress draft before Facebook scheduling,
2. allow blog publication to succeed even if Facebook packaging is delayed,
3. preserve cleaner failure handling.

## Required Queue Record Fields

Each queue item should preserve at minimum:

1. `queue_item_id`
2. `queue_type`
3. `draft_id`
4. `blog_publish_id` when available
5. `social_package_id` when available
6. `queue_state`
7. `approval_state`
8. `scheduled_for`
9. `last_transition_at`
10. `last_error`
11. `created_at`
12. `updated_at`

## Blog Queue States

### `ready_for_wordpress`

Meaning:

1. the draft is approved,
2. the WordPress payload has been prepared,
3. the item is ready for the first WordPress action.

### `wordpress_draft_created`

Meaning:

1. the item now has a WordPress post ID,
2. the post exists as a WordPress draft,
3. the operator can inspect the rendered post before scheduling or publishing.

### `ready_for_blog_schedule`

Meaning:

1. the WordPress draft is acceptable,
2. the operator may now assign a schedule or publish-now intent.

### `scheduled_blog`

Meaning:

1. the post has a concrete scheduled publish time,
2. the queue record should preserve that time.

### `published_blog`

Meaning:

1. the post is live in WordPress,
2. the queue record should now link to the final blog publish record.

### `blog_publish_failed`

Meaning:

1. a WordPress action failed,
2. the error should stay visible until handled.

## Facebook Queue States

### `social_packaging_pending`

Meaning:

1. the blog-side item exists,
2. the Facebook package has not been finalized yet.

### `ready_for_social_review`

Meaning:

1. a Facebook package has been derived,
2. the package is ready for operator review.

### `approved_for_queue`

Meaning:

1. the operator approved the selected Facebook package,
2. the item can now be scheduled for Facebook.

### `scheduled_facebook`

Meaning:

1. the Facebook post has a scheduled publish time or queued publish intent,
2. the queue record should preserve that time.

### `published_facebook`

Meaning:

1. the post is live on the Facebook Page,
2. the queue record should preserve the publish identifier when available.

### `facebook_publish_failed`

Meaning:

1. the Facebook publish step failed,
2. the error remains visible for retry or manual recovery.

## Approval States Inside The Queue

Queue approval should stay explicit.

Suggested v1 values:

1. `pending_review`
2. `approved`
3. `needs_edits`
4. `rejected`

These approval values should describe the queue item's public-readiness, not replace the Phase 2 draft review history.

## Default Operator Flow

The v1 default order should be:

1. approved draft enters `ready_for_wordpress`
2. WordPress draft is created
3. operator checks the rendered WordPress output
4. item moves to `ready_for_blog_schedule`
5. Facebook package is created and reviewed
6. Facebook queue item moves to `approved_for_queue`
7. blog and Facebook items are scheduled or published

## Scheduling Rules

V1 scheduling should remain conservative.

Recommended baseline:

1. no blind auto-publish from a freshly approved draft,
2. no Facebook scheduling before the corresponding blog post exists or has a confirmed URL path,
3. scheduling should be explicit and recorded per queue item,
4. queue collisions should be reviewed by the operator, not guessed away,
5. blog schedule snapshots should preserve whether scheduling was `manual` or `auto`,
6. Facebook scheduling should not happen before the linked blog schedule when the blog is already scheduled.

## Failure Handling Rules

Queue failure should be visible and local.

The queue layer must preserve:

1. what failed,
2. when it failed,
3. which queue item failed,
4. whether the blog side or Facebook side failed,
5. enough error detail for manual recovery.

It must not:

1. silently retry forever,
2. mark an item successful without a platform identifier or explicit result,
3. let a Facebook failure erase the fact that the blog publication succeeded.

## What Must Be Avoided

Do not:

1. collapse the blog queue and Facebook queue into one vague status,
2. let scheduling states replace approval states,
3. auto-schedule public output without an explicit operator checkpoint,
4. bury failed items out of view,
5. let queue behavior redefine the upstream content contract.

## Definition Of Done

This spec is satisfied when:

1. the repo has an explicit queue-item shape,
2. blog and Facebook queue states are distinct,
3. approval and scheduling are kept separate,
4. implementation can add Phase 3 queue logic without guessing what the states mean.
