# Content Formatting Pipeline V1

## Purpose

This document defines the deterministic formatting pipeline for the Phase 2 Content Engine.

The purpose of this pipeline is to make draft creation predictable, reviewable, and cheap. The pipeline should take a normalized source item from Phase 1 and transform it into a structured draft record without drifting into free-form writing behavior.

## Core Rule

The Content Engine is a formatting pipeline with optional micro-enhancement, not a blank-page writing engine.

That means:

1. the source item provides the factual basis,
2. the template contract provides the article shape,
3. deterministic transformation happens first,
4. AI enhancement happens only after structure exists,
5. quality gates evaluate the result before the draft is treated as usable.

## Input Contract

The pipeline should only start from a source item that already passed the Source Engine contract.

Required upstream inputs:

1. `source_item_id`
2. `source_id`
3. `source_url`
4. `source_domain`
5. `source_title`
6. `normalized_title`
7. cleaned source text or enriched body text
8. source classification
9. dedupe status
10. body extraction status

The formatting pipeline must not accept:

1. arbitrary URLs,
2. raw HTML,
3. unreviewed feed fragments with no lineage,
4. non-unique source items unless manually overridden through an explicit later-phase workflow.

## Output Contract

The pipeline must emit one structured draft record following:

1. [DRAFT_RECORD_SPEC.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DRAFT_RECORD_SPEC.md)

The output should remain draft-layer only. It should not quietly include WordPress publish fields or Facebook packaging fields.

## Pipeline Stages

The v1 deterministic flow should be:

1. eligibility check,
2. template selection,
3. content-fit and anchor check,
4. source condensation,
5. section planning,
6. deterministic section fill,
7. micro-skill enhancement,
8. category and tag suggestion,
9. quality gate evaluation,
10. draft record emission.

## Stage 1: Eligibility Check

Purpose:

Confirm the source item is allowed into Content Engine processing.

Required checks:

1. source lineage is complete,
2. dedupe result is `unique`,
3. source text is sufficiently usable,
4. source classification suggests a valid v1 blog template,
5. no blocking source-level error flags remain.

Failure rule:

1. if the item fails eligibility, do not attempt draft generation,
2. record a blocked or rejected processing outcome instead.

## Stage 2: Template Selection

Purpose:

Map the source item to one valid blog template.

The selection must follow:

1. [BLOG_TEMPLATE_CONTRACTS_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/BLOG_TEMPLATE_CONTRACTS_V1.md)

V1 default selection rules:

1. direct explanatory food fact -> `blog_food_fact_v1`
2. conservative food value framing -> `blog_food_benefit_v1`
3. question-led or surprising background angle -> `blog_curiosity_food_v1`

If the item does not fit one of the existing templates cleanly:

1. do not invent a one-off structure,
2. mark it for hold or rejection.

## Stage 3: Content-Fit And Anchor Check

Purpose:

Confirm that the item is a clean enough fit for the selected template before draft wording is trusted.

This stage should follow:

1. [CONTENT_FIT_GATE_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CONTENT_FIT_GATE_V1.md)

Required checks:

1. identify a usable subject anchor,
2. filter boilerplate and obvious site chrome,
3. filter recipe-step and instruction-heavy paragraphs where possible,
4. identify a small set of support anchors,
5. record semantic risk signals when the fit is weak.

Failure rule:

1. weak fit should produce explicit review signals,
2. the formatter must not quietly promote boilerplate fragments into intro or section framing.

## Stage 4: Source Condensation

Purpose:

Convert the source material into a smaller structured fact set before section writing starts.

The goal is to move away from source sentence order and toward article-slot intent.

Recommended condensed outputs:

1. core answer or main takeaway,
2. one to three explanation points,
3. one to four supporting facts or examples,
4. one category suggestion,
5. one likely template family.

This stage should not try to produce polished prose. It should produce usable structured raw material.

## Stage 5: Section Planning

Purpose:

Map the condensed source material into the required section slots of the chosen template.

Each section plan should know:

1. `section_key`
2. `content_goal`
3. `source_fact_inputs`
4. `target_length_range`
5. whether bullets are appropriate

This stage is critical for derivative-risk reduction because it forces the system to rewrite around section goals rather than source paragraph order.

## Stage 6: Deterministic Section Fill

Purpose:

Produce the first complete draft structure using deterministic rules first.

V1 deterministic fill should focus on:

1. answer-first ordering,
2. short readable paragraphs,
3. clean section boundaries,
4. light summarization from the condensed source material,
5. consistent use of headings and bullets.

This stage should produce:

1. intro placeholder or first-pass intro,
2. section bodies,
3. recap or close,
4. excerpt placeholder if needed.

The result at this stage should already be structurally usable even before AI enhancement.

In the current v1 operating model, deterministic drafts should aim to be useful mobile explainers first. It is acceptable for a first-pass draft to land in `review_flag` because it is still a little close to source phrasing, slightly outside the ideal template range, or semantically weak-fit for the current template family, as long as the structure is complete and the reasons are recorded clearly.

## Stage 7: Micro-Skill Enhancement

Purpose:

Improve bounded fields only after the deterministic structure exists.

Allowed enhancements should follow:

1. [AI_MICRO_SKILL_POLICY.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/AI_MICRO_SKILL_POLICY.md)

Typical v1 order:

1. headline variants,
2. selected intro wording,
3. one-section smoothing when needed,
4. excerpt generation,
5. category and tag suggestion assist.

Failure rule:

1. if a micro-skill result is weak, do not widen scope,
2. fall back to deterministic wording or route to review.

## Stage 8: Category And Tag Suggestion

Purpose:

Assign the smallest controlled archive classification needed for the draft.

This stage must follow:

1. [CATEGORY_AND_TAG_POLICY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CATEGORY_AND_TAG_POLICY_V1.md)

The pipeline should assign:

1. one primary category,
2. three to six tag candidates when possible.

## Stage 9: Quality Gate Evaluation

Purpose:

Decide whether the draft passes, needs flagged review, or is blocked.

This stage must follow:

1. [CONTENT_QUALITY_GATES.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/CONTENT_QUALITY_GATES.md)
2. [DERIVATIVE_RISK_POLICY.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/DERIVATIVE_RISK_POLICY.md)

Expected outputs:

1. `quality_gate_status`
2. `quality_flags`
3. `derivative_risk_level`
4. `derivative_risk_notes`

## Stage 10: Draft Record Emission

Purpose:

Write the final structured draft record that downstream review will consume.

The pipeline should only emit a completed draft record when:

1. required fields are present,
2. required sections are represented,
3. source lineage is intact,
4. quality gate outcome is recorded.

## Recommended Failure Handling

The pipeline should fail clearly and narrowly.

Recommended failure categories:

1. `source_not_eligible`
2. `non_unique_source_item`
3. `template_not_found`
4. `insufficient_source_text`
5. `section_fill_failed`
6. `quality_blocked`

The system should not hide formatting failures inside vague notes.

## Recommended Minimal Observability

V1 does not need heavy telemetry, but each formatting attempt should be able to answer:

1. which source item was used,
2. which template was selected,
3. whether AI was used,
4. whether the draft passed, flagged, or blocked,
5. why a blocked draft failed.

## Default Implementation Sequence

The recommended code implementation order for this pipeline is:

1. eligibility check,
2. template selection,
3. section planning,
4. deterministic section fill,
5. draft record builder,
6. quality gate evaluator,
7. optional micro-skill integration.

This order matters because the project should become useful before AI is added.

## Definition Of Done

This spec is satisfied when:

1. the Content Engine has a clear stage-by-stage transformation path,
2. deterministic formatting is explicitly first,
3. AI is clearly secondary,
4. the output contract is stable enough for implementation and testing.
