# Social Package Review Workflow V1

## Purpose

This document defines the first operator review workflow for Phase 3 Facebook package records.

The goal is to preserve a visible approval trail between:

1. prepared social package,
2. operator review outcome,
3. refreshed Facebook queue state,
4. refreshed blog-to-Facebook mapping state.

## Core Rule

Facebook packages are not auto-approved in v1.

Every package should remain reviewable until a human explicitly records one of:

1. `approved`
2. `needs_edits`
3. `rejected`

## Required Inputs

The review workflow begins from:

1. `social_package_id`
2. latest social package snapshot
3. optional linked `blog_publish_id`
4. actionable review notes when the outcome is not approval

## Required Review Record Fields

Each social package review record should preserve at minimum:

1. `review_id`
2. `social_package_id`
3. `draft_id`
4. `blog_publish_id` when available
5. `reviewer_label`
6. `reviewed_at`
7. `review_outcome`
8. `previous_approval_state`
9. `updated_approval_state`
10. `review_notes`

## Review Outcome Rules

### `approved`

Meaning:

1. the hook matches the blog content,
2. the caption is not misleading,
3. the comment CTA is acceptable,
4. the package can move toward queue readiness when blog linkage is valid.

Notes are optional but still useful.

### `needs_edits`

Meaning:

1. the package is close enough to keep,
2. one or more specific issues must be fixed before queueing.

This outcome requires at least one actionable review note.

### `rejected`

Meaning:

1. the package should not be queued in its current form,
2. the packaging approach or angle needs a replacement, not a light tweak.

This outcome requires at least one actionable review note.

## Queue And Mapping Effect

If the package is linked to a `blog_publish_id`, the review workflow should refresh:

1. the Facebook queue record,
2. the blog-to-Facebook mapping record.

Expected v1 behavior:

1. `approved` may move the Facebook queue to `approved_for_queue` when the blog URL is confirmed,
2. `approved` should still remain `social_packaging_pending` when the package is approved but the blog URL is not yet confirmed,
3. `needs_edits` should keep the queue review-visible,
4. `rejected` should keep the mapping but prevent queue progression.

## What Must Be Avoided

Do not:

1. mark a package approved without a stored review event,
2. treat packaging notes as a replacement for review records,
3. let queue approval drift away from the actual reviewed package snapshot.

## Definition Of Done

This spec is satisfied when:

1. social package review has explicit outcomes,
2. review events are append-only and auditable,
3. queue and mapping refresh behavior is clear enough for implementation.
