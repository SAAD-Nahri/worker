# Content Quality Gates

## Purpose

This document defines the quality checks that apply to v1 blog drafts before they move deeper into review and publishing workflows.

The system should not treat every issue the same way. Some issues should block a draft automatically. Some should route it to review with flags. Some should pass normally.

This spec exists to make that distinction explicit.

The current v1 implementation is intentionally tuned for short, mobile-first explainers rather than traditional long-form editorial posts. The quality gates should reflect that operating model.

## Core Rule

Quality gates should protect:

1. structural completeness,
2. readability,
3. lineage integrity,
4. derivative safety,
5. tone safety,
6. semantic anchor quality,
7. content-fit honesty.

They should not become a giant scoring system in v1.

## Gate Outcomes

Every draft should receive one top-level quality outcome:

1. `pass`
2. `review_flag`
3. `blocked`

## Mandatory Gate Categories

### 1. Source Lineage Gate

Checks:

1. source item exists,
2. source ID exists,
3. source URL exists,
4. source title exists,
5. selected template is recorded.

Outcome rules:

1. missing lineage fields -> `blocked`

### 2. Template Completeness Gate

Checks:

1. all required template sections exist,
2. section order is valid,
3. required headline and intro fields exist,
4. required recap or close section exists where applicable.

Outcome rules:

1. missing required section -> `blocked`
2. wrong section order but still recoverable -> `review_flag`

### 2A. Template Slot Guidance Gate

Checks:

1. intro and required body sections stay inside template slot soft ranges when those ranges are explicitly encoded,
2. bullet-driven sections stay inside the allowed bullet-count range,
3. early-answer slots appear early enough when the template contract encodes an explicit timing rule.

Outcome rules:

1. slot-level drift outside the accepted contract -> `review_flag`
2. repeated slot-level drift should remain visible as named flags rather than being hidden under one vague quality label

### 3. Length And Thinness Gate

Checks:

1. article stays inside the template's soft range,
2. article is not too thin to be useful,
3. section bodies are not mostly empty.

Initial v1 rules:

1. below `120` total words -> `blocked`
2. within template soft range -> `pass`
3. outside soft range but still above the minimum useful threshold -> `review_flag`
4. above `900` words without strong reason -> `review_flag`

### 4. Readability Gate

Checks:

1. paragraphs are short enough for mobile,
2. section headings are clear,
3. sentences are not overly dense,
4. article avoids large uninterrupted blocks.

Initial v1 rules:

1. paragraph over `110` words -> `review_flag`
2. repeated wall-of-text behavior across multiple sections -> `blocked`
3. no headings or section breaks in a multi-section template -> `blocked`

### 5. Title Integrity Gate

Checks:

1. title matches the article body,
2. title does not overstate the source,
3. title does not make unsupported health or certainty claims,
4. title is not misleadingly broad.

Outcome rules:

1. clearly misleading title -> `blocked`
2. fixable title tone issue -> `review_flag`

### 6. Derivative Risk Gate

Checks:

1. phrasing transformation is sufficient,
2. structure is not too close to source order,
3. sections are not trivial paraphrases.

Outcome rules:

1. `derivative_risk_level = high` -> `blocked`
2. `derivative_risk_level = medium` -> `review_flag`
3. `derivative_risk_level = low` -> `pass`

### 7. Claim Safety Gate

Checks:

1. no medical-sounding promises,
2. no cure-like phrasing,
3. no strong unsupported health claims,
4. no fake certainty where the source is weaker.

Outcome rules:

1. prohibited claim language -> `blocked`
2. mild overstatement that is easy to fix -> `review_flag`

### 8. Category And Tag Gate

Checks:

1. one valid category exists,
2. tags follow the controlled policy,
3. tags are not a keyword dump.

Outcome rules:

1. missing or invalid category -> `review_flag`
2. weak tags only -> `review_flag`

### 9. Semantic Anchor And Content-Fit Gate

Checks:

1. subject anchor is usable,
2. support anchors are not sentence fragments or boilerplate,
3. the draft is not being driven by obviously weak terms,
4. recipe-heavy or noisy source context is surfaced clearly,
5. the chosen template still makes sense for the item.

Outcome rules:

1. semantic anchor noise or title mismatch -> `review_flag`
2. recipe-heavy or noisy source context in an otherwise usable draft -> `review_flag`
3. if semantic weakness combines with another blocking issue, the overall draft may still be `blocked`

## Auto-Block Conditions

The following should block a draft automatically in v1:

1. missing source lineage,
2. missing required template sections,
3. draft below minimum useful length,
4. high derivative risk,
5. clearly misleading title,
6. prohibited health or certainty claims,
7. repeated wall-of-text formatting,
8. duplicate-blocked source item passed through incorrectly.

## Review-Flag Conditions

The following should usually send a draft to review with flags instead of blocking it:

1. medium derivative risk,
2. title is serviceable but too clicky,
3. article is somewhat outside target length,
4. one or more long paragraphs need tightening,
5. category or tags are uncertain,
6. intro is weak but the structure is usable,
7. conclusion is thin but fixable,
8. semantic anchors are weak but still recoverable,
9. source context is too recipe-heavy or noisy for a clean automatic pass,
10. one or more template slots drift outside their encoded soft ranges,
11. bullet-driven sections use too few or too many points for the accepted template.

## Pass Conditions

A draft should pass cleanly when:

1. source lineage is complete,
2. template structure is complete,
3. the article lands within reasonable length targets,
4. readability is mobile-friendly,
5. title is honest,
6. derivative risk is low,
7. no prohibited claims are present,
8. semantic framing is coherent enough that the draft does not need rescue editing just to explain what it is about.

## Recording Requirements

The system should record:

1. one top-level quality gate status,
2. zero or more named quality flags,
3. short notes for blocked or flagged drafts when helpful.

Example flags:

1. `missing_required_section`
2. `title_integrity_issue`
3. `paragraph_too_long`
4. `derivative_risk_medium`
5. `claim_safety_issue`
6. `category_uncertain`
7. `semantic_term_noise`
8. `anchor_title_mismatch`
9. `source_context_recipe_heavy`
10. `source_context_noisy`
11. `intro_length_outside_target`
12. `supporting_points_bullet_count_outside_target`
13. `direct_answer_position_too_late`

## Review Philosophy

These gates are not intended to replace human review.

They are intended to:

1. stop obvious failures early,
2. make review faster,
3. keep the Content Engine honest,
4. prevent weak drafts from being treated as ready just because text exists.

## Definition Of Done

This spec is satisfied when:

1. the team knows what blocks automatically,
2. the team knows what only needs review flags,
3. the draft record can store the result clearly,
4. implementation can follow a deterministic first-pass quality policy.
