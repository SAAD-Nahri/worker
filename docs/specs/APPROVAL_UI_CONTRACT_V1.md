# Approval UI Contract V1

## Purpose

This spec defines how human approval should fit into the system from a UI point of view.

The goal is not to build a giant editorial CMS.

The goal is to give the solo operator one clean control surface for:

1. seeing what needs attention,
2. reviewing the right context,
3. making explicit approve/edit/reject decisions,
4. preserving an audit trail,
5. moving content forward without guesswork.

## Core UI Principle

Human approval should sit as a thin operator console between:

1. automated preparation,
2. public publishing.

The UI should not replace the pipeline.

The pipeline still does:

1. source intake,
2. cleaning,
3. formatting,
4. micro-skill assistance,
5. packaging preparation,
6. queue preparation.

The UI exists to let the operator make explicit decisions at the few points that matter most.

## Main UI Shape

The recommended v1 UI shape is:

1. one operator dashboard,
2. three approval inboxes,
3. one publish queue view,
4. one detail-review panel,
5. one audit/history panel.

This should feel like a review console, not like a full writing environment.

## Approval Stages In The UI

### 1. Draft Review Inbox

This is where prepared drafts first wait for human approval.

Each row should show:

1. title,
2. source domain,
3. template,
4. category,
5. quality status,
6. derivative-risk level,
7. routing action,
8. last updated time,
9. approval state.

Primary actions:

1. approve,
2. mark needs edits,
3. reject,
4. open full draft detail,
5. inspect source lineage.

### 2. Social Package Review Inbox

This is where Facebook packaging waits for approval after a blog draft is approved.

Each row should show:

1. linked blog title,
2. selected hook,
3. caption preview,
4. comment CTA preview,
5. blog linkage state,
6. social approval state,
7. last updated time.

Primary actions:

1. approve package,
2. switch variant,
3. mark needs edits,
4. reject package,
5. open package detail.

### 3. Queue Review Inbox

This is where approved items wait for scheduling or publish intent confirmation.

Each row should show:

1. blog post title,
2. social package status,
3. queue readiness state,
4. schedule mode,
5. proposed time,
6. collision warnings if any.

Primary actions:

1. approve for queue,
2. set schedule,
3. hold,
4. remove from current batch.

## Recommended Screen Structure

### Screen A: Operator Dashboard

This is the landing page.

It should answer one question first:

1. what needs my attention now.

Recommended blocks:

1. draft review counts,
2. social review counts,
3. queue-ready counts,
4. blocked or failed items,
5. recent publish-chain failures,
6. current canary or live transport alerts.

### Screen B: Review Detail

This is the main approval workspace.

Recommended layout:

1. left column: item list or inbox list,
2. center column: full content preview,
3. right column: metadata and decision actions.

The center preview should show:

1. final title,
2. intro,
3. sections,
4. excerpt,
5. social package preview when relevant.

The right column should show:

1. source lineage,
2. quality flags,
3. derivative-risk notes,
4. template id,
5. category/tags,
6. approval history,
7. action buttons,
8. required review note field when outcome is not approval.

### Screen C: Queue And Schedule View

This is not a creative editor.

It is the final operational checkpoint before public output.

It should show:

1. approved blog items,
2. approved social packages,
3. current queue state,
4. proposed publish time,
5. collisions or recent-topic overlap,
6. current transport status.

## Decision Buttons

The UI should keep decision verbs small and explicit.

For draft review:

1. `Approve Draft`
2. `Needs Edits`
3. `Reject Draft`

For social review:

1. `Approve Package`
2. `Needs Edits`
3. `Reject Package`
4. `Switch Variant`

For queue review:

1. `Approve For Queue`
2. `Schedule`
3. `Hold`
4. `Remove`

## Required Context On Every Review Screen

The operator should never need to review from memory.

At minimum, every review surface should show:

1. source title,
2. source domain,
3. template used,
4. quality gate status,
5. approval state,
6. latest review note,
7. linked records when relevant.

## UI Boundaries

The approval UI should not try to do all of these in v1:

1. long-form article authoring,
2. drag-and-drop page building,
3. analytics dashboarding,
4. asset design editing,
5. infrastructure management.

If manual text editing is needed, it should be:

1. lightweight,
2. bounded,
3. tied to review,
4. saved as a new append-only snapshot.

## Recommended Implementation Direction

The chosen first UI direction is:

1. a thin WordPress admin plugin as the operator shell,
2. a private internal operator API on the Python worker,
3. built on top of the existing append-only records and review/update logic,
4. not a replacement for the pipeline modules.

That means:

1. the UI reads current state through the operator API,
2. the operator API reads and writes the same runtime records the CLI paths use,
3. review actions are still written back as append-only events,
4. WordPress admin provides operator auth and familiar navigation without becoming the source of truth.

Implementation references:

1. [OPERATOR_API_CONTRACT_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/OPERATOR_API_CONTRACT_V1.md)
2. [WORDPRESS_ADMIN_APPROVAL_PLUGIN_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WORDPRESS_ADMIN_APPROVAL_PLUGIN_V1.md)

## Relation To Future Autoapproval

Even if later autoapproval exists, the UI still matters.

It becomes the place to:

1. inspect shadow-mode results,
2. review autoapproved items,
3. see why an item was autoapproved,
4. override or reverse an automated decision,
5. disable autopilot quickly.

So the UI should be designed now as:

1. operator-first,
2. approval-first,
3. audit-friendly,
4. later compatible with autopilot oversight.

## Definition Of Done

This spec is satisfied when:

1. the role of human approval in the UI is explicit,
2. the system has one clear approval-console shape,
3. draft review, social review, and queue review are separated cleanly,
4. approval actions remain traceable and review-safe,
5. later autoapproval can fit into the same operator console without replacing it.
