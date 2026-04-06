# AI Micro-Skill Policy

## Purpose

This document defines the exact role AI is allowed to play inside the v1 Content Engine.

The project is not an AI-first writing system. AI exists here only to fill small, controlled slots after the structure and source lineage are already known.

## Core Rule

AI may improve small parts of a draft.

AI may not own the article.

That means:

1. the template determines the article shape,
2. the source item determines the factual basis,
3. the Content Engine determines the section structure,
4. AI only helps with bounded wording tasks.

The current repo baseline also supports a heuristic fallback provider so these bounded skills can be exercised without making external AI a runtime dependency.

## Allowed V1 Micro-Skills

### 1. `generate_headline_variants`

Purpose:

1. create `2` to `5` honest title options,
2. keep them within the chosen template and article angle.
3. preserve the source-title shape or subject anchor instead of wrapping every title in the same generic pattern.

Implementation note:

1. the local heuristic provider should stay conservative,
2. weak, clicky, or awkward variants should be discarded instead of padded into the draft record,
3. heuristic variants are review aids, not auto-approved publishing titles.

### 2. `generate_short_intro`

Purpose:

1. write the opening intro block,
2. frame the article cleanly without burying the answer.

Rules:

1. this skill is only valid for templates that actually include an `intro` slot,
2. intro normalization should respect the selected template's intro slot guidance instead of a single global range,
3. if the intro text changes, the draft must be re-evaluated and moved back to `pending_review`.

### 3. `smooth_section_copy`

Purpose:

1. lightly rewrite one short section for flow,
2. reduce awkward phrasing after deterministic formatting.

This is not permission to regenerate the whole article body.

### 4. `generate_excerpt`

Purpose:

1. create a short summary for archive or later publishing use.

### 5. `assign_tags_and_category_assist`

Purpose:

1. suggest a category from the controlled taxonomy,
2. suggest a small set of tags from the controlled policy.

The final output must still remain within the approved taxonomy.

## Inputs Required For AI Use

Every AI micro-skill call should already have:

1. source lineage,
2. selected template,
3. section or field target,
4. tone notes,
5. prohibited patterns,
6. length constraint.

If those inputs do not exist, the correct action is to fix the deterministic setup first, not to send a broader prompt.

## Disallowed V1 AI Uses

The following are explicitly out of scope:

1. generating a full article from scratch,
2. deciding article structure without a template contract,
3. inventing facts, examples, or claims,
4. generating unsupported health framing,
5. replacing manual review,
6. deciding which source should be used,
7. deciding publish timing,
8. generating Facebook packaging inside the Content Engine.

## Output Boundaries

To keep AI tightly scoped, use these default limits:

1. headline variants: `2` to `5`
2. intro length: follow the selected template's intro slot guidance; the current intro-bearing v1 templates use `35` to `70` words
3. section smoothing rewrite: one section at a time, not the full body
4. excerpt length: `20` to `50` words
5. tag suggestions: `3` to `6` candidates

## Logging Requirement

AI usage should be recorded in the draft record.

Minimum fields:

1. `skill_name`
2. `target_field`
3. `model_label`
4. `created_at`

## Review Requirement

AI output should be treated as proposed wording, not truth.

The review path should still confirm:

1. the output matches the source,
2. the output fits the template,
3. the output does not create misleading framing,
4. the output does not increase derivative risk accidentally.

If a content-affecting micro-skill changes the draft text, the system should:

1. re-run quality evaluation,
2. refresh derivative-risk fields,
3. reset `approval_state` to `pending_review`,
4. reset `workflow_state` to `drafted`.

## Failure Rule

If a micro-skill output is weak, the system should:

1. fall back to deterministic wording if available,
2. flag the draft for review,
3. reject the micro-skill call when the selected template does not support the requested field,
4. avoid expanding the AI scope just to rescue the draft.
5. prefer fewer honest headline variants over a full set of weak ones.

The wrong response is to keep widening the prompt until AI effectively writes the article.

## Definition Of Done

This spec is satisfied when:

1. the allowed AI role is narrow and explicit,
2. full-article generation remains out of scope,
3. the Content Engine can log AI use clearly,
4. implementation can build AI support without drifting into a writing engine.
