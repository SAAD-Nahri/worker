# AI Micro-Skill Prompt Contracts V1

## Purpose

This document defines the first provider-backed prompt and output contracts for bounded micro-skills.

## Core Rule

Prompt contracts are slot contracts, not writing freedom.

Each prompt must receive:

1. source lineage,
2. selected template,
3. target field,
4. tone notes,
5. prohibited patterns,
6. length bounds.

## Supported Provider-Backed Skills

### 1. `generate_headline_variants`

Input contract:

1. selected headline,
2. source title,
3. template family,
4. desired count,
5. prohibited clicky or misleading patterns.

Output contract:

1. return `2` to `5` standalone headline variants,
2. preserve subject-anchor relevance,
3. avoid weak “you won’t believe” style wording,
4. do not output explanatory prose.

### 2. `generate_short_intro`

Input contract:

1. selected headline,
2. approved template contract,
3. template intro length bounds,
4. draft context,
5. source lineage.

Output contract:

1. return one intro only,
2. stay within template-aware intro bounds,
3. keep answer-first framing,
4. do not introduce facts not supported by source/draft context.

### 3. `generate_excerpt`

Input contract:

1. selected headline,
2. draft intro and section context,
3. excerpt bounds,
4. tone notes.

Output contract:

1. return one excerpt only,
2. stay within `20` to `50` words,
3. keep the excerpt summary-like rather than promotional.

### 4. Later `smooth_section_copy`

Input contract:

1. one existing section only,
2. source lineage,
3. template role of that section,
4. section-specific boundaries.

Output contract:

1. return one rewritten section only,
2. do not expand into a full article rewrite,
3. preserve the same factual frame and purpose.

## Rejection Rules

Provider output should be rejected or retried when:

1. it exceeds bounds,
2. it becomes clicky or misleading,
3. it loses the subject anchor,
4. it introduces unsupported claims,
5. it turns a bounded task into free-form generation.

## Definition Of Done

This spec is satisfied when provider-backed skills can be implemented with:

1. explicit input contracts,
2. explicit output shapes,
3. bounded failure handling,
4. no ambiguity about what the model is allowed to do.
