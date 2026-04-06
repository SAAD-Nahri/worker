# Dedupe Policy

## Purpose

This document defines how duplicate and near-duplicate content should be handled in the first working version.

The goal of dedupe is to prevent the system from publishing repetitive, low-value, or overly similar content while keeping the logic simple enough for early implementation.

## Why Dedupe Matters

Weak dedupe creates several problems:

1. repetitive blog output,
2. repetitive Facebook packaging,
3. wasted publishing slots,
4. lower perceived quality,
5. weaker future analysis.

For this project, dedupe is not just a cleanup feature. It is a quality-protection feature.

## Dedupe Scope

V1 dedupe should operate at three levels:

1. source-item duplication,
2. draft-topic duplication,
3. title and angle collision.

V1 does not need advanced semantic clustering across the entire archive, but it must catch obvious repetition.

## V1 Dedupe Inputs

The dedupe process should consider at minimum:

1. canonical URL,
2. raw title,
3. normalized title,
4. source family,
5. extracted key terms,
6. existing draft titles,
7. existing published titles,
8. existing topical label or template family.

## Required Dedupe Outcomes

Each candidate item should end in one of these statuses:

1. `unique`
   Safe to proceed.

2. `exact_duplicate`
   Same canonical source or same clearly matching existing record.

3. `near_duplicate`
   Close enough to an existing item that it needs manual review or blocking.

4. `angle_collision`
   Not a strict duplicate, but too close in framing or publish value to justify separate processing right now.

## Exact Duplicate Rules

An item should be treated as an exact duplicate if:

1. the canonical URL matches an existing processed item,
2. the same source item was already fetched and processed,
3. the title and source identity clearly indicate the same content record.

Exact duplicates should normally be blocked immediately.

## Near-Duplicate Rules

An item should be treated as a near-duplicate if:

1. the title is very similar to an already processed title,
2. the core fact or angle appears materially the same,
3. the content would likely produce almost the same blog structure,
4. publishing both would not create meaningful archive variety.

Near-duplicates may be blocked or sent to manual review depending on confidence.

## Angle Collision Rules

An item should be flagged as an angle collision if:

1. it covers the same core food fact through slightly different phrasing,
2. it would compete with an already queued or recently published item,
3. it adds little incremental value despite not being textually similar.

This status matters because the system should not chase volume through shallow topic repetition.

## Minimum V1 Dedupe Strategy

V1 should implement a practical layered approach:

1. exact URL or item-ID matching first,
2. normalized title comparison second,
3. basic topic-angle comparison third,
4. human review fallback for ambiguous cases.

This is enough for v1. It is better to have a simple reliable dedupe policy than to delay implementation waiting for sophisticated semantic similarity systems.

## Dedupe Decision Rules

### Allow forward

Allow the item to move forward if:

1. it is clearly unique,
2. it adds a distinct angle,
3. it is not colliding with active queue items.

### Block

Block the item if:

1. it is an exact duplicate,
2. it is a strong near-duplicate with no meaningful differentiation,
3. it is a weak-value angle collision.

### Manual review

Send to manual review if:

1. the title looks similar but the angle may still be usable,
2. the topic is repeated but the presentation may differ enough to justify it,
3. the dedupe system lacks confidence.

## Records To Preserve

For every dedupe decision, preserve:

1. candidate item ID,
2. dedupe status,
3. matched prior item ID when relevant,
4. brief reason,
5. reviewer override if applicable.

## What V1 Dedupe Should Not Try To Solve

V1 dedupe should not try to:

1. build full semantic clustering across all content,
2. understand every nuance of topic overlap,
3. optimize archive diversity mathematically,
4. use expensive reasoning for every item.

The correct v1 goal is to stop obvious repetition and reduce low-value collisions.

## Definition Of Done

This spec is satisfied when:

1. exact duplicates are blocked,
2. clear near-duplicates are identified,
3. ambiguous duplicates can be reviewed manually,
4. dedupe outcomes are stored as part of item history.
