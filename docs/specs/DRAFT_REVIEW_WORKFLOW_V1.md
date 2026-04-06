# Draft Review Workflow V1

## Purpose

This document defines how Content Engine drafts should be reviewed before they are considered ready for queue and publishing workflows.

The project depends on human approval in v1, but review should still be structured. This workflow exists to prevent subjective, inconsistent, or hidden review behavior.

## Core Rule

Review should validate the draft against explicit contracts, not personal preference.

The reviewer is checking whether the draft is:

1. structurally complete,
2. readable,
3. safely transformed,
4. category-safe,
5. worth using a publish slot on.

## Review Inputs

Every draft review should have access to:

1. the full draft record,
2. source lineage fields,
3. selected template identity,
4. quality gate status,
5. quality flags,
6. derivative-risk notes,
7. headline variants if present.

The reviewer should not need to reconstruct the article's origin from memory.

## Review Scope

Draft review belongs to Phase 2 and covers:

1. title quality,
2. section completeness,
3. clarity and formatting,
4. derivative safety,
5. category and tag sanity.

It does not yet decide:

1. WordPress publication,
2. Facebook packaging,
3. scheduling,
4. paid promotion.

## Review Decision States

V1 draft review outcomes should be:

1. `approved`
2. `needs_edits`
3. `rejected`

These should map onto the broader approval model without ambiguity.

Recommended v1 state mapping:

1. `approved` -> `approval_state = approved`, `workflow_state = reviewed`
2. `needs_edits` -> `approval_state = needs_edits`, `workflow_state = needs_revision`
3. `rejected` -> `approval_state = rejected`, `workflow_state = rejected`

### `approved`

The draft is good enough to move into later queue and publishing preparation.

### `needs_edits`

The draft is structurally usable, but one or more fixable issues remain.

### `rejected`

The draft is weak enough that it should not continue in its current form.

## Review Checklist

The reviewer should check these areas in order.

### 1. Lineage Check

Confirm:

1. source item exists,
2. source domain is known,
3. source title is known,
4. selected template is recorded.

If lineage is unclear, the review should not approve the draft.

### 2. Template Check

Confirm:

1. the draft uses one valid template,
2. all required sections exist,
3. section order is correct,
4. the article actually fits the chosen template.

### 3. Title Check

Confirm:

1. the headline is honest,
2. the headline fits the article body,
3. the headline does not overclaim,
4. the headline is not spammy or vague.
5. any heuristic headline variants are treated as working suggestions, not auto-approved final titles.

### 4. Readability Check

Confirm:

1. sections are easy to scan,
2. paragraph lengths are mobile-friendly,
3. the answer or value arrives early enough,
4. the close is not abrupt or weak.

### 5. Derivative-Risk Check

Confirm:

1. the draft is not too close to source phrasing,
2. the section structure is meaningfully transformed,
3. the article feels reformatted and rewritten, not thinly paraphrased.

### 6. Category And Tag Check

Confirm:

1. the primary category makes sense,
2. tags are controlled and useful,
3. the article is not drifting into a weak or misleading classification.

### 7. Publish Worthiness Check

Confirm:

1. the article is good enough to deserve a slot,
2. the topic is not redundant with recent material,
3. the transformation adds enough value to justify use.

## Decision Rules

### Approve

Approve when:

1. structure is complete,
2. title is honest,
3. readability is acceptable,
4. derivative risk is low,
5. no major claim or tone issue exists.

### Needs Edits

Use `needs_edits` when:

1. the title needs tightening,
2. one or two sections need rewriting,
3. intro or close is weak but recoverable,
4. category or tags need correction,
5. derivative risk is medium but fixable.

### Reject

Reject when:

1. the transformation is too weak,
2. the article is too close to the source,
3. the template fit is fundamentally wrong,
4. readability is poor enough that repair would be slower than rebuilding,
5. the content is not worth using.

## Edit Loop Rule

When a draft is marked `needs_edits`, the review record should clearly note:

1. what needs to change,
2. whether the issue is structural or wording-related,
3. whether the same template should still be used.

The system should not allow vague feedback like:

1. `make better`
2. `rewrite`
3. `improve tone`

Instead, notes should point to the fix area directly.

Vague notes should be treated as invalid review input in v1.

## Review Notes Format

Recommended review note categories:

1. `title_fix`
2. `intro_fix`
3. `section_rewrite`
4. `derivative_risk_fix`
5. `category_fix`
6. `reject_not_worth_slot`

## Relation To Quality Gates

Quality gates are pre-review structure.

Review is the human decision layer.

That means:

1. `blocked` drafts should usually not reach approval review,
2. `review_flag` drafts should reach review with visible flags,
3. `pass` drafts should still receive human approval in v1.

## Minimal Review Metadata

Each completed review should eventually store:

1. `reviewed_at`
2. `review_outcome`
3. `review_notes`
4. `reviewer_label`

For v1, `reviewer_label` may simply be the solo operator identity or a default local value.

Review records should be persisted append-only so the project keeps a visible approval trail instead of silently overwriting review history.

## Post-Review Edit Rule

Approval is only valid for the exact reviewed draft snapshot.

If a content-affecting change happens after review, such as:

1. intro rewrite,
2. section rewrite,
3. any later bounded micro-skill that changes article text,

then the system should:

1. re-run the quality evaluation,
2. refresh derivative-risk fields,
3. reset `approval_state` to `pending_review`,
4. reset `workflow_state` to `drafted`.

Headline variants and excerpts may still be updated as bounded review aids, but they should not be treated as a substitute for the approved draft body.

## Definition Of Done

This spec is satisfied when:

1. draft review is a repeatable checklist instead of a loose habit,
2. the team knows when to approve, edit, or reject,
3. review outputs are traceable,
4. later queue and publishing work can trust the approval result.
