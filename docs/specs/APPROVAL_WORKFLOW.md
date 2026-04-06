# Approval Workflow

## Purpose

This document defines what must be reviewed by a human before content is allowed to move forward in v1.

The workflow is intentionally conservative. The project is designed for a solo operator, which means low-quality automation can do real damage if approval rules are weak.

## Approval Philosophy

V1 uses automation for preparation, not for blind publishing.

The system should automate:

1. sourcing,
2. cleaning,
3. template filling,
4. lightweight packaging,
5. queue preparation.

The system should not fully automate final public output without review.

## What Requires Human Approval In V1

The following require explicit human approval before publication:

1. final blog title,
2. final blog draft,
3. selected blog category or tags when unclear,
4. final Facebook hook/caption package,
5. final scheduling intent for public posting.

## What May Be Auto-Prepared Without Human Approval

The following may be prepared automatically:

1. source intake,
2. cleaning,
3. classification,
4. dedupe suggestion,
5. first-pass draft formatting,
6. hook and CTA variants,
7. queue suggestions.

These may be generated automatically, but they are not equivalent to approval.

## Review Stages

### Stage 1: Draft Review

The human reviewer should confirm:

1. the draft is structurally complete,
2. the draft is readable,
3. the draft is not too close to source phrasing,
4. the title is accurate enough,
5. the content does not drift into spammy or exaggerated framing.

Possible outcomes:

1. approve,
2. needs edits,
3. reject.

### Stage 2: Social Package Review

The human reviewer should confirm:

1. the chosen hook matches the blog content,
2. the caption is not misleading,
3. the CTA is not overly spammy,
4. the package is fit for a Facebook Page post.

Possible outcomes:

1. approve,
2. switch variant,
3. rewrite manually,
4. reject package.

### Stage 3: Queue Review

The human reviewer should confirm:

1. the item should be published,
2. the selected time or batch is acceptable,
3. the content is not colliding with recent queue items,
4. the mapping between blog and Facebook output is correct,
5. whether the item is using manual scheduling or a previously approved auto-scheduling path.

## Approval States

Suggested v1 approval states:

1. `pending_review`
2. `approved`
3. `needs_edits`
4. `rejected`
5. `approved_for_queue`
6. `approved_for_publish`

## Rejection Rules

An item should be rejected if:

1. the transformation is too weak,
2. the content is too repetitive,
3. the title or packaging is misleading,
4. the formatting quality is too low,
5. the item is not worth using a publish slot on.

## Manual Override Rules

The human reviewer may override:

1. template choice,
2. title selection,
3. social package selection,
4. queue order,
5. dedupe block in edge cases.

Overrides should be deliberate and traceable.

## Scheduling Approval Rule

V1 may support both manual scheduling and policy-approved auto scheduling, but both must remain explicit.

That means:

1. manual scheduling should preserve who approved and applied the schedule,
2. auto scheduling should preserve who approved the auto path and that the system applied the schedule,
3. the system should not treat a timestamp alone as proof of schedule approval.

## What This Workflow Is Trying To Prevent

1. blind auto-publishing,
2. low-value content going live,
3. spammy Facebook packaging,
4. repetitive topic collisions,
5. weak source transformations being mistaken for finished work.

## Future Relaxation

Automation may become more aggressive later only if:

1. draft quality is consistently high,
2. packaging quality is consistently high,
3. publish history shows the system is stable,
4. review rules can be replaced with trustworthy checks.

Until then, human approval is part of the business model, not a temporary inconvenience.

## Definition Of Done

This spec is satisfied when:

1. the team knows exactly what needs approval,
2. draft review and social review are separate concerns,
3. queue approval is explicit,
4. the v1 system cannot quietly bypass review.
