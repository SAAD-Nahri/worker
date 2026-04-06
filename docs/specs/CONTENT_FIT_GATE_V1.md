# Content-Fit Gate V1

## Purpose

This document defines the deterministic content-fit checks that sit between Phase 1 source intake and Phase 2 draft trust.

The goal is simple:

1. not every valid source item is automatically a good fit for the current draft templates,
2. anchor quality must be treated as a first-class concern,
3. weak-fit items should be surfaced early instead of being "rescued" later by wider generation.

## Core Rule

The Content Engine should not assume that structurally available text is semantically fit for a short explainer draft.

V1 must protect against three common failure modes:

1. recipe-heavy pages being pushed into explainer templates without enough filtering,
2. boilerplate or summary fragments becoming the framing language of the draft,
3. semantically weak anchor terms making the draft sound complete while still feeling wrong.

## What The Gate Evaluates

The content-fit gate is concerned with deterministic fitness, not style polish.

It should evaluate:

1. subject anchor clarity,
2. support-anchor quality,
3. noise and boilerplate contamination,
4. recipe or instruction heaviness,
5. whether the selected template family still makes sense.

Routing behavior after a weak-fit result should follow:

1. [WEAK_FIT_ROUTING_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/WEAK_FIT_ROUTING_POLICY_V1.md)

## Input Contract

The gate should only use already-known source material:

1. source title,
2. source summary,
3. cleaned or extracted body text,
4. selected template family,
5. candidate explanatory paragraphs,
6. derived topic terms.

It must not depend on:

1. external AI,
2. hidden editorial memory,
3. manual intervention during the check itself.

## V1 Deterministic Checks

### 1. Subject Anchor Check

The formatter must be able to identify a clear subject anchor from the title path.

The subject anchor should:

1. represent what the draft is actually about,
2. avoid boilerplate fragments,
3. avoid filler words,
4. remain consistent with the chosen template.

Examples:

1. `Greek Easter Bread` is a usable subject anchor.
2. `costco croissant container` is a usable subject anchor.
3. `summary`, `until`, or `your` are not usable subject anchors.

### 2. Support Anchor Check

Support anchors should:

1. come from cleaned summary or explanatory body context,
2. avoid sentence-middle fragments,
3. avoid boilerplate,
4. avoid low-signal terms that only sound specific.

Examples of weak support anchors:

1. `exceptions prove he'll`
2. `container, plastic, and your`
3. `photo matt taylor`

Examples of acceptable support anchors:

1. `coconut`
2. `marshmallows`
3. `environmental sustainability`
4. `rice paper wraps`

### 3. Boilerplate And Noise Check

The gate should discount or filter:

1. photo credits,
2. affiliate disclosures,
3. social/embed attributions,
4. newsletter prompts,
5. related-link title fragments,
6. "appeared first on" remnants.

If those elements are still materially shaping anchors, the draft should not quietly pass.

### 4. Recipe-Heaviness Check

Some items are valid food content but still poor fits for the current explainer path because the page is dominated by:

1. ingredient lines,
2. instruction steps,
3. timing blocks,
4. recipe-card scaffolding.

V1 should not pretend these are clean explainer inputs.

Recipe-heavy context should trigger review even when a draft is technically complete.

### 5. Template-Fit Check

If the item is clearly weak-fit for the chosen template family, the system should prefer:

1. `review_flag`,
2. reroute planning,
3. hold/reject behavior,

over:

1. widening prompts,
2. more aggressive rewriting,
3. silently accepting a weak draft.

## Current V1 Implementation Note

In the current repo baseline, content-fit is implemented through:

1. candidate-paragraph filtering in the formatter,
2. title-summary-body anchor selection,
3. semantic profile generation during draft formatting,
4. semantic quality flags in the quality layer.

This is acceptable for the current phase.

It does **not** mean the architecture should stay implicit forever.

If Phase 2 needs a cleaner separation later, the content-fit gate may become an explicit pre-draft step.

## Expected V1 Outcomes

The content-fit gate should support these review outcomes:

1. clean fit -> `pass` remains possible,
2. semantically weak but recoverable -> `review_flag`,
3. clearly wrong fit or blocked by another gate -> `blocked`.

Typical V1 review flags include:

1. `semantic_term_noise`
2. `anchor_title_mismatch`
3. `source_context_recipe_heavy`
4. `source_context_noisy`

## What This Gate Should Not Do

The content-fit gate should not:

1. become a full classifier lab,
2. invent new templates automatically,
3. replace operator review,
4. depend on AI to repair a bad fit,
5. become an excuse for free-form rewriting.

## Strategic Guidance

The main lesson from live Phase 2 work is that anchor quality determines draft quality early.

If the subject and support anchors are wrong:

1. intros become awkward,
2. sections become generic,
3. review time is wasted,
4. downstream Facebook packaging quality will also suffer.

That is why content-fit belongs in the foundation of Phase 2, not as a later polish layer.
