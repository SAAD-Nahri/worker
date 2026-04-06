# Media Brief Contract V1

## Purpose

This document defines the first media brief shape used to support reviewed asset selection or generation from approved draft context.

## Core Rule

The media brief is derived from approved content.

It is not a free-form creative wish list.

## Required Inputs

The brief should be derived from:

1. `draft_id`
2. approved headline
3. template family
4. selected category and tags
5. short summary or excerpt
6. intended publish destination

## Required Brief Fields

The first media brief should contain at minimum:

1. `media_brief_id`
2. `draft_id`
3. `blog_publish_id` when available
4. `social_package_id` when available
5. `brief_goal`
6. `subject_focus`
7. `visual_style_notes`
8. `prohibited_visual_patterns`
9. `alt_text_seed`
10. `intended_usage`
11. `created_at`

## Style Rule

The brief should support clear, usable visual direction without trying to become a full design spec.

## Prohibited Patterns

The brief should explicitly avoid:

1. medical-claim imagery,
2. misleading before/after framing,
3. exaggerated clickbait visuals,
4. unclear rights status.

## Definition Of Done

This spec is satisfied when one approved draft can be transformed into a brief that is:

1. specific enough to guide asset work,
2. bounded enough to review,
3. linked enough to remain part of the publish chain.
