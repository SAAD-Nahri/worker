# Weak-Fit Routing Policy V1

## Purpose

This document defines how Phase 2 should treat drafts that are structurally valid but still poor fits for the current short-explainer path.

The purpose is not to create a giant editorial triage system.

The purpose is to stop weak-fit items from being mistaken for publish-ready wins just because a draft exists.

## Core Rule

Quality outcome and routing outcome are related but not identical.

A draft can:

1. `pass` quality but still be `hold_for_reroute`,
2. `review_flag` and still be worth keeping in the current path,
3. fail early enough that it should be rejected from the current v1 workflow.

That distinction matters because Phase 2 is still using only a small template set.

## Routing Actions

### 1. `proceed`

Use when:

1. the draft is a clean enough fit for the current template,
2. semantic anchors are clear,
3. no reroute-level warnings are present.

Meaning:

1. the item can stay in the current Phase 2 path,
2. normal review still applies,
3. no template-family rethink is required.

### 2. `review_only`

Use when:

1. the draft is usable but still needs human judgment,
2. derivative or semantic issues are moderate rather than structural,
3. the item still belongs to the current template family.

Meaning:

1. keep it in the current path,
2. do not auto-promote it,
3. require review before it can influence later phases.

### 3. `hold_for_reroute`

Use when:

1. the draft shape exists,
2. the item is weak-fit for the current explainer templates,
3. review alone is not the right answer because the content type itself is the problem.

Meaning:

1. do not treat the draft as queue-ready,
2. do not widen prompting to rescue it,
3. hold it until a better template or content path exists,
4. optionally reject it later if reroute is not worth supporting.

### 4. `reject_for_v1`

Use when:

1. the item fails the minimum eligibility floor,
2. the current workflow should not spend more attention on it,
3. the draft is blocked or formatting should never have proceeded.

Meaning:

1. stop processing in the current v1 path,
2. record why,
3. move on.

## Current V1 Deterministic Rules

### Rule Group A: Automatic Reject

Recommend `reject_for_v1` when:

1. the quality gate is `blocked`,
2. the formatter cannot create a draft because the source item is not eligible.

### Rule Group B: Automatic Hold For Reroute

Recommend `hold_for_reroute` when:

1. `source_context_recipe_heavy` is present,
2. `source_context_noisy` is present,
3. the title is a roundup or listicle pattern such as numbered `recipes`, `foods`, or `you need to try`,
4. the title has a trailing sentiment/news clause after a dash, such as `— And Fans Are Underwhelmed`,
5. the title is a venue-novelty story, such as a `restaurant` ghost or haunted-location story,
6. the title is a geographic price-comparison roundup, such as `most and least expensive` food items by `states`,
7. derivative risk is medium and the title looks like a direct recipe-title page rather than an explainer.

### Rule Group C: Review Only

Recommend `review_only` when:

1. semantic-anchor problems are present but reroute is not required,
2. derivative risk is medium without a stronger reroute signal,
3. the item still fits the current template family better than any deferred alternative.

### Rule Group D: Proceed

Recommend `proceed` when:

1. no hold or reject rule matches,
2. the draft is at least a clean enough fit for normal review,
3. later phases can safely assume the draft belongs in the current pipeline.

## Examples From The Current Gold Set

### `proceed`

Examples:

1. Costco croissant container reuse story,
2. Jacques Pepin preference story,
3. Pak Mo Krob explainer.

### `review_only`

Examples:

1. Sopa Negra explainer with medium derivative overlap but still usable framing.

### `hold_for_reroute`

Examples:

1. Tsoureki recipe-heavy explainer source,
2. Italian street-food roundup,
3. Costco automated pay-station consumer-news title,
4. restaurant ghost-story novelty coverage,
5. state-by-state burger price-comparison coverage,
6. Red wine-braised short ribs recipe-title page.

### `reject_for_v1`

Examples:

1. insufficient-text synthetic blocked control,
2. any draft blocked by the current quality gate.

## Implementation Note

In the current repo baseline, routing recommendation exists as a deterministic helper layer and as a visible operator-facing reporting signal, not yet as a hard pre-draft stop.

That is intentional.

The project is still learning where reroute boundaries belong, so routing should guide operator decisions first through the normal draft-health report before it becomes a stricter workflow gate.

## What This Policy Must Not Become

This policy must not become:

1. a justification for rescuing bad content with wider AI,
2. a replacement for human review,
3. a hidden classifier with unexplained rules,
4. an excuse to keep obviously weak-fit items in the queue indefinitely.

## Strategic Guidance

The routing policy exists to keep the project honest.

If the current template set is too narrow for an item:

1. surface that fact,
2. hold or reject the item,
3. improve the system deliberately later,
4. do not pretend the current draft is stronger than it is.
