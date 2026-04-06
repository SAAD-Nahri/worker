# Workflow State Model

## Purpose

This document defines the required lifecycle states for a content item and the allowed transitions between those states.

The point of the state model is to make the system traceable, reviewable, and hard to confuse.

## Core Principle

Every content item starts as a source item and moves through controlled stages. A later stage must not exist unless an earlier stage has completed successfully or has been explicitly overridden by review.

## Entity Chain

The system must preserve the relationship between:

1. source item,
2. cleaned item,
3. drafted blog item,
4. approved blog item,
5. published blog item,
6. social package,
7. published Facebook item.

These can be implemented as separate records or related states, but the lineage must remain visible.

## Required States

### 1. `sourced`

The item has been discovered and registered from an approved source.

Minimum expectations:

1. source identity is known,
2. source URL is known,
3. raw title or discovery signal exists.

### 2. `cleaned`

The raw content has been normalized enough for downstream processing.

Minimum expectations:

1. body text noise reduced,
2. repeated junk removed,
3. normalization outcome recorded.

### 3. `classified`

The item has been assigned an initial template family or topic label.

Minimum expectations:

1. likely content type identified,
2. topic fit recorded,
3. classification confidence or notes stored if needed.

### 4. `deduped`

The item has been checked against previously processed material.

Minimum expectations:

1. duplicate or near-duplicate status recorded,
2. action decision captured,
3. duplicate target referenced if a match exists.

### 5. `drafted`

The item has been transformed into a blog draft using templates and allowed enhancement skills.

Minimum expectations:

1. selected template recorded,
2. draft content exists,
3. draft metadata exists.

### 6. `reviewed`

The item has gone through human or structured review and received a decision.

Allowed review outcomes:

1. approved,
2. needs edits,
3. rejected.

### 7. `queued`

The item is approved and waiting for scheduled publication.

Minimum expectations:

1. publish intent exists,
2. scheduling metadata exists or is pending,
3. approval history exists.

### 8. `published_blog`

The blog post is live in WordPress.

Minimum expectations:

1. blog post identifier exists,
2. blog publication time exists,
3. final title used is recorded.

### 9. `social_packaged`

The Facebook-ready assets have been derived from the approved or published blog item.

Minimum expectations:

1. hook variants exist,
2. caption or CTA variants exist,
3. mapping to the blog item exists.

### 10. `published_facebook`

One or more Facebook posts have been published or scheduled with a linkable record.

Minimum expectations:

1. Facebook post identifier exists or scheduling record exists,
2. mapped blog post exists,
3. chosen social variant is known.

### 11. `archived`

The item is complete and retained for history.

### 12. `promoted_candidate`

The item or pattern has been flagged for later scaling consideration.

This is not a v1 operational requirement, but the state should remain conceptually reserved.

## Terminal Or Exception States

### `rejected`

The item should not continue through the workflow.

### `duplicate_blocked`

The item was stopped because a stronger or earlier equivalent already exists.

### `failed_processing`

The item encountered a system or content-processing failure that needs intervention.

## Allowed Transition Pattern

The normal path is:

`sourced -> cleaned -> classified -> deduped -> drafted -> reviewed -> queued -> published_blog -> social_packaged -> published_facebook -> archived`

Allowed exception paths:

1. `deduped -> duplicate_blocked`
2. `reviewed -> rejected`
3. `any active state -> failed_processing`
4. `published_blog -> archived` when social distribution is skipped for a valid reason

## Review Rules

An item must not move into `queued` unless:

1. it has a valid source lineage,
2. it has passed dedupe checks,
3. it has a selected template,
4. it has passed the required review process.

## State Ownership By Phase

### Source Engine owns:

1. sourced,
2. cleaned,
3. classified,
4. deduped.

### Content Engine owns:

1. drafted,
2. quality-ready draft outputs feeding review.

### Review and Distribution flow owns:

1. reviewed,
2. queued,
3. published_blog,
4. social_packaged,
5. published_facebook,
6. archived.

## Implementation Guidance

The state model should be simple enough to support a solo-operator workflow. Do not add decorative states unless they solve a real operational problem.

## Definition Of Done

This spec is satisfied when:

1. every content item can be placed in exactly one meaningful primary state,
2. transitions are explicit,
3. blocked or rejected items remain traceable,
4. source-to-publish lineage is preserved.
