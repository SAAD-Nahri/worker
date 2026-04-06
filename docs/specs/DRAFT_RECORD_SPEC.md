# Draft Record Spec

## Purpose

This document defines the required record shape for a Content Engine draft.

The draft record is the main contract between:

1. the Source Engine,
2. the Content Engine,
3. the review workflow,
4. later publishing and social packaging phases.

If the draft record is vague, the Content Engine will drift into ad hoc formatting and hidden assumptions. This spec exists to stop that.

## Core Rule

A draft record is a structured formatting output, not a publish object.

It must preserve source lineage, template choice, draft content structure, quality state, and review state without mixing in publish-layer concerns too early.

The draft record must not be treated as:

1. a WordPress post object,
2. a Facebook package object,
3. a generic free-form text blob.

## Draft Record Ownership

The Content Engine owns draft creation.

The review workflow may update review-related fields.

The draft record should become the upstream input for:

1. review,
2. queue preparation,
3. publishing,
4. later social packaging.

## Required Top-Level Fields

Every draft record should eventually contain at minimum:

1. `draft_id`
2. `workflow_state`
3. `approval_state`
4. `language`
5. `source_item_id`
6. `source_id`
7. `source_url`
8. `source_domain`
9. `source_title`
10. `source_published_at`
11. `template_id`
12. `template_family`
13. `template_version`
14. `category`
15. `tag_candidates`
16. `headline_selected`
17. `headline_variants`
18. `intro_text`
19. `sections`
20. `excerpt`
21. `related_read_bridge`
22. `quality_gate_status`
23. `quality_flags`
24. `derivative_risk_level`
25. `derivative_risk_notes`
26. `ai_assistance_log`
27. `review_notes`
28. `created_at`
29. `updated_at`

## Required Field Meaning

### Identity And State

**`draft_id`**

Stable internal identifier for the draft record.

**`workflow_state`**

Default state on creation:

1. `drafted`

Expected later v1 review states:

1. `reviewed`
2. `needs_revision`
3. `rejected`

**`approval_state`**

Default state on creation:

1. `pending_review`

Expected later v1 review states:

1. `approved`
2. `needs_edits`
3. `rejected`

### Source Lineage

These fields are mandatory because the draft must remain traceable to its upstream input:

1. `source_item_id`
2. `source_id`
3. `source_url`
4. `source_domain`
5. `source_title`
6. `source_published_at`

If source lineage is incomplete, the draft should not be considered valid.

### Template Identity

These fields define what structure the draft is using:

1. `template_id`
2. `template_family`
3. `template_version`

### Classification And Archive Fields

**`language`**

V1 default:

1. `en`

**`category`**

One category from the controlled blog taxonomy.

**`tag_candidates`**

Controlled list of suggested tags, not an open-ended keyword dump.

### Headline And Intro Fields

**`headline_selected`**

The current chosen working headline for the draft.

**`headline_variants`**

Optional small list of working alternatives for review.

These are not assumed to be final publishing titles.

In the current Phase 2 baseline, heuristic variants should be treated as bounded review aids that still require human selection or cleanup.

Recommended v1 range:

1. `2` to `5` variants maximum

**`intro_text`**

The short introductory block that opens the article.

### Section Structure

**`sections`** must be an ordered list of structured sections, not a single long body string.

Each section record should contain at minimum:

1. `section_key`
2. `section_label`
3. `position`
4. `body_blocks`
5. `bullet_points`

Recommended section-level rules:

1. `section_key` must match the template contract slot,
2. `position` preserves order,
3. `body_blocks` should contain one or more short paragraphs,
4. `bullet_points` may be empty when the section does not use bullets.

### Supporting Output Fields

**`excerpt`**

Short article summary suitable for later blog or archive use.

**`related_read_bridge`**

Optional soft closing line that can point into later internal linking or related content.

### Quality And Risk Fields

**`quality_gate_status`**

Allowed v1 values:

1. `pass`
2. `review_flag`
3. `blocked`

**`quality_flags`**

List of named issues or review signals.

**`derivative_risk_level`**

Allowed v1 values:

1. `low`
2. `medium`
3. `high`

**`derivative_risk_notes`**

Short explanation of why the current risk level was assigned.

### AI Assistance Fields

**`ai_assistance_log`**

The draft should record which micro-skills were used.

Each entry should eventually capture:

1. `skill_name`
2. `target_field`
3. `model_label`
4. `created_at`

### Review Fields

**`review_notes`**

Short notes added during manual review or structured quality review.

## Required Structural Rules

The draft record should obey these rules:

1. one draft record maps to one source item,
2. one draft record uses one primary template,
3. required template sections must be represented explicitly,
4. publish-layer IDs must not be stored here yet,
5. social-package fields must not be stored here yet.

## Explicitly Out Of Scope For This Record

Do not put the following into the draft record as if they already belong here:

1. WordPress post ID,
2. final publish timestamp,
3. Facebook post ID,
4. Facebook caption variants,
5. queue schedule details beyond review readiness,
6. analytics metrics.

## Example Shape

```json
{
  "draft_id": "draft_20260402_001",
  "workflow_state": "drafted",
  "approval_state": "pending_review",
  "language": "en",
  "source_item_id": "item_abc123",
  "source_id": "src_food_republic",
  "source_url": "https://example.com/story",
  "source_domain": "foodrepublic.com",
  "source_title": "Why X Happens In The Kitchen",
  "template_id": "blog_food_fact_v1",
  "template_family": "food_fact_article",
  "template_version": "v1",
  "category": "food-facts",
  "tag_candidates": ["ingredient-basics", "kitchen-questions"],
  "headline_selected": "Why This Food Behaves The Way It Does",
  "headline_variants": [
    "Why This Common Food Trick Actually Works",
    "The Real Reason This Kitchen Habit Helps"
  ],
  "intro_text": "A short intro goes here.",
  "sections": [
    {
      "section_key": "direct_answer",
      "section_label": "The Short Answer",
      "position": 1,
      "body_blocks": ["Paragraph text."],
      "bullet_points": []
    }
  ],
  "excerpt": "Short excerpt.",
  "related_read_bridge": null,
  "quality_gate_status": "review_flag",
  "quality_flags": ["derivative_risk_medium"],
  "derivative_risk_level": "medium",
  "derivative_risk_notes": "Structure is good but one section is still too close to source phrasing.",
  "ai_assistance_log": [
    {
      "skill_name": "generate_headline_variants",
      "target_field": "headline_variants",
      "model_label": "gpt-small",
      "created_at": "2026-04-02T20:00:00Z"
    }
  ],
  "review_notes": [],
  "created_at": "2026-04-02T20:00:00Z",
  "updated_at": "2026-04-02T20:00:00Z"
}
```

## Definition Of Done

This spec is satisfied when:

1. the Content Engine can emit a structured draft record instead of loose text,
2. source lineage is preserved,
3. template choice is explicit,
4. quality and derivative-risk fields exist,
5. later phases can use the draft record without redefining it.
