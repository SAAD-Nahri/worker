# Derivative Risk Policy

## Purpose

This document defines how v1 should judge whether a draft is too close to its source.

The project is intentionally derivative in the sense that it transforms existing material into a better presentation format. That does not mean weak transformation is acceptable.

The system must produce:

1. cleaner structure,
2. rewritten phrasing,
3. a different presentation shape,
4. an answer-first or mobile-friendly reading experience,
5. clear value beyond copy-and-paste paraphrasing.

## Core Rule

The Content Engine may reuse facts and themes from the source.

It may not:

1. reproduce the source article sentence-by-sentence,
2. keep the source structure almost unchanged,
3. perform trivial synonym swaps and call that transformation,
4. rely on direct quotation as the normal v1 behavior.

## What Counts As Acceptable Transformation

Acceptable transformation usually includes several of the following:

1. reordering the information into the chosen template,
2. answering the main question earlier than the source,
3. condensing long source passages into shorter explanation blocks,
4. converting source paragraphs into bullets or mini-sections,
5. changing heading structure completely,
6. rewriting the phrasing in a simpler, cleaner voice,
7. removing noise or weak tangents.

The point is not originality for its own sake. The point is meaningful re-presentation.

## Risk Levels

### Low Risk

The draft is safely transformed.

Typical signals:

1. wording is clearly rewritten,
2. the article shape is template-driven rather than source-driven,
3. sections are reorganized around the blog contract,
4. no section feels copied or lightly swapped.

Action:

1. `pass`

### Medium Risk

The draft is probably usable, but still feels too close in one or more places.

Typical signals:

1. one section mirrors source phrasing too closely,
2. the overall structure still resembles the source too much,
3. some sentence shapes feel carried over,
4. the transformation is real but not yet comfortably distinct.

Action:

1. `review_flag`

### High Risk

The draft is too close to the source and should not move forward.

Typical signals:

1. multiple sections read like direct rewrites of source paragraphs,
2. the article follows the source in nearly the same order with minimal restructuring,
3. several phrases remain recognizably copied,
4. the output feels like thin paraphrase instead of reformatting.

Action:

1. `blocked`

## Practical V1 Thresholds

The system is not required to implement perfect plagiarism detection in v1, but it should follow these practical thresholds:

1. any obvious `12+` word carryover from source phrasing should be treated as high risk,
2. repeated `8` to `11` word carryover or strong structural mirroring should be treated as at least medium risk,
3. if two or more core sections feel directly traceable to source paragraphs, treat the draft as high risk,
4. if the draft keeps the same order, same examples, and near-same wording, treat it as high risk even if some sentences were shortened.

These are operational thresholds, not legal advice.

## Direct Quote Rule

Direct quotation is not part of the standard v1 pipeline.

Default rule:

1. do not quote source text directly,
2. do not rely on attribution as a substitute for transformation,
3. if a quote ever appears, it should be a manual exception and reviewed carefully.

## High-Risk Patterns To Avoid

The following patterns are not acceptable in v1:

1. paragraph-by-paragraph paraphrase,
2. swapping a few words while keeping the sentence skeleton,
3. reproducing the source introduction with light edits,
4. keeping the source headline idea and body structure almost unchanged,
5. using the source's examples in the same order with the same explanation framing.

## Medium-Risk Patterns To Watch

These do not always require rejection, but they should trigger review:

1. one section is still too close while the rest is acceptable,
2. the structure is improved but still follows the source too literally,
3. the draft adds little beyond shortening the source,
4. bullets were added, but the underlying phrasing still feels imported.

## How To Reduce Derivative Risk

The safest v1 methods are:

1. choose the correct template first,
2. rewrite around section goals, not around source sentences,
3. answer early and reorganize aggressively,
4. use simpler wording and shorter sections,
5. remove non-essential source details instead of carrying them through by default.

## Relation To Quality Gates

This policy should feed directly into the draft quality gate result:

1. `low` -> `pass`
2. `medium` -> `review_flag`
3. `high` -> `blocked`

## Review Notes Requirement

If a draft is marked `medium` or `high`, the system or reviewer should record a short note describing why.

Examples:

1. `first explanation section mirrors source too closely`
2. `structure still follows source paragraph order`
3. `headline and intro feel like thin source rewrite`

## Definition Of Done

This spec is satisfied when:

1. derivative risk has explicit levels,
2. acceptable transformation is defined,
3. reviewers know what to flag or block,
4. the Content Engine has a concrete standard to build against.
