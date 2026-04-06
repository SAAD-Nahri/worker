# Facebook Packaging Template Contracts V1

## Purpose

This document defines the first concrete Phase 3 template contracts for Facebook-ready packaging.

The packaging layer is not a side effect of the blog article. It is a first-class business layer whose job is to turn an approved blog post into a click-worthy but honest Facebook Page package.

## Core Rule

Facebook packaging must derive from the approved blog draft or the resulting published blog post.

It must not derive directly from:

1. the raw source item,
2. a rejected or unreviewed draft,
3. a free-form social prompt with no lineage.

## Package Structure

The Phase 3 Facebook package should be composed from three bounded parts:

1. primary post template
2. selected caption text
3. selected comment CTA text

V1 should support one primary selected package per approved draft, with a small number of reviewable variants if useful.

## Required Record Fields

Every Facebook package record should preserve at minimum:

1. `social_package_id`
2. `draft_id`
3. `blog_publish_id` when available
4. `package_template_id`
5. `hook_text`
6. `caption_text`
7. `comment_cta_text`
8. `target_destination = facebook_page`
9. `approval_state`
10. `created_at`
11. `updated_at`

Optional but useful v1 fields:

1. `blog_url`
2. `comment_template_id`
3. `selected_variant_label`
4. `packaging_notes`

## Package Families

### 1. `fb_curiosity_hook_v1`

**Purpose**

Create a clean open-loop post that makes the reader want the short answer on the blog.

**Required parts**

1. hook line
2. short explanatory tease
3. soft click invitation

**Target shape**

1. hook: `8` to `18` words
2. teaser: `1` to `2` short sentences
3. CTA: short and non-aggressive

**Best fit**

1. surprising food questions
2. contrast-led explainers
3. origin and history angles

**Prohibited patterns**

1. engagement bait
2. fake suspense with no real payoff
3. all-caps urgency
4. misleading claims beyond the blog draft

### 2. `fb_short_caption_v1`

**Purpose**

Create a tighter post for familiar or practical angles where a long setup is unnecessary.

**Required parts**

1. one-line observation
2. short framing line
3. soft CTA

**Target shape**

1. `20` to `45` words total
2. ideally `2` short lines or sentences

**Best fit**

1. practical kitchen explainers
2. storage or handling tips
3. short food facts that do not need a dramatic hook

**Prohibited patterns**

1. listicle framing that the article does not support
2. spammy prompting
3. fake authority claims

### 3. `fb_soft_cta_post_v1`

**Purpose**

Lead with usefulness or relevance while keeping the post calm and click-oriented.

**Required parts**

1. utility or curiosity lead
2. one-line reason the blog post is worth reading
3. soft CTA

**Target shape**

1. `25` to `55` words total
2. `2` to `3` short sentences or line blocks

**Best fit**

1. practical food explainers
2. light benefit content
3. gentle educational angles

**Prohibited patterns**

1. exaggerated promise language
2. wellness overclaiming
3. high-pressure click commands

## Comment CTA Families

### 1. `fb_comment_link_line_v1`

**Purpose**

Place the article URL in comments naturally after the main Facebook post is live.

**Required parts**

1. short context line
2. clear read-more intent
3. link placement support

### 2. `fb_comment_curiosity_reinforcement_v1`

**Purpose**

Keep the curiosity loop alive without sounding repetitive or spammy.

**Required parts**

1. short reminder of the payoff
2. calm invitation to read the blog post

### 3. `fb_comment_read_more_prompt_v1`

**Purpose**

Provide a short “continue here” prompt when the main post intentionally stays brief.

**Required parts**

1. short continuation line
2. clear but non-pushy CTA

## Tone Rules

All Facebook package templates should favor:

1. fast readability
2. honest curiosity
3. mobile-friendly pacing
4. non-spammy CTA language
5. close alignment with the approved blog draft

They should avoid:

1. exaggerated clickbait
2. misleading questions
3. direct engagement bait such as “comment yes if…”
4. invented facts not present in the approved draft
5. strong health claims that exceed the article itself

## Variant Rules

V1 should stay conservative.

Recommended baseline:

1. `1` primary Facebook package per approved draft
2. up to `3` reviewable hook or caption variants when needed
3. `1` selected comment CTA line

The system should prefer a few clean variants over a noisy pile of options.

## Selection Rules

The packaging selector should use:

1. the approved draft's template family
2. the approved title
3. the approved direct answer or fast answer
4. the approved excerpt
5. the current routing and review context

It must not:

1. re-open blog content strategy debates,
2. invent a new angle that the draft does not support,
3. optimize for clickbait at the expense of alignment.

## Review Requirement

Facebook packages are not auto-approved in v1.

Human review must confirm:

1. the hook matches the blog content,
2. the caption is not misleading,
3. the comment CTA is not spammy,
4. the selected package is appropriate for a Facebook Page post.

## Definition Of Done

This spec is satisfied when:

1. the first Facebook package families are explicit,
2. every package has required parts and tone boundaries,
3. the repo knows what fields belong in a Facebook package record,
4. implementation can derive Facebook-ready assets from an approved blog draft without guessing.
