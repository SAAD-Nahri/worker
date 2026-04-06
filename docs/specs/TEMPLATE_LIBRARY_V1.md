# Template Library V1

## Purpose

This document defines the first required template families for blog output, Facebook packaging, and comment CTA output.

Templates are mandatory infrastructure. They are not optional content helpers. The system depends on templates to remain cheap, consistent, and reviewable.

## V1 Template Philosophy

Templates should:

1. reduce variation,
2. make outputs faster to review,
3. support mobile-friendly formatting,
4. make AI enhancements small and controlled,
5. keep the content machine focused on presentation quality rather than unconstrained writing.

Templates should not:

1. encourage full free-form generation,
2. become endlessly customized before real publishing begins,
3. depend on heavy reasoning to function.

## Required V1 Blog Templates

### 1. Food Fact Article

**Purpose**

Present a surprising or useful food fact in a clean explanatory format.

**Required sections**

1. headline,
2. short intro,
3. direct answer or core fact,
4. explanation section,
5. supporting points or examples,
6. closing recap,
7. optional related-read bridge.

**Best use cases**

1. ingredient origins,
2. food behavior facts,
3. kitchen myth clarification,
4. simple explanatory food knowledge.

### 2. Food Benefit Article

**Purpose**

Present a food-related benefit or practical value without sliding into exaggerated health claims.

**Required sections**

1. headline,
2. short context intro,
3. what the food is or why it matters,
4. structured list of points,
5. caution against overstating,
6. short conclusion.

**Best use cases**

1. everyday food usefulness,
2. ingredient value summaries,
3. simple practical benefits framed conservatively.

### 3. Curiosity Article

**Purpose**

Turn a surprising food-related question into a fast, readable article.

**Required sections**

1. question-style headline,
2. fast answer,
3. short explanation blocks,
4. one or more supporting examples,
5. concise close.

**Best use cases**

1. surprising food questions,
2. cultural or historical food curiosities,
3. familiar foods with unexpected background.

## Required V1 Facebook Templates

### 1. Curiosity Hook Post

**Purpose**

Create an open loop that pushes the reader toward the blog.

**Required parts**

1. hook line,
2. short tease,
3. click invitation.

### 2. Short Caption Post

**Purpose**

Create a tighter, lower-friction Facebook post for lightweight distribution.

**Required parts**

1. single observation,
2. short framing line,
3. soft CTA.

### 3. Soft CTA Post

**Purpose**

Lead with usefulness or intrigue and softly point to the blog.

**Required parts**

1. curiosity or utility lead,
2. one-line explanation of why the blog post is worth the click,
3. soft CTA.

## Required V1 Comment CTA Templates

### 1. Link Placement Line

**Purpose**

Place the article link naturally in comments without sounding spammy.

### 2. Curiosity Reinforcement Line

**Purpose**

Keep the open loop active in the comments and encourage the click.

### 3. Read More Prompt

**Purpose**

Give a clean invitation to continue to the blog post.

## Required Template Fields

Every template should eventually define at minimum:

1. `template_id`
2. `template_name`
3. `template_group`
4. `content_goal`
5. `required_sections`
6. `optional_sections`
7. `tone_notes`
8. `prohibited_patterns`
9. `target_length_guidance`

## Tone Rules For V1 Templates

The templates should favor:

1. clear,
2. light,
3. curiosity-driven,
4. readable,
5. non-spammy,
6. non-sensationalized.

The templates should avoid:

1. exaggerated promises,
2. aggressive clickbait,
3. strong unsupported health framing,
4. long dense paragraphs,
5. dramatic urgency language.

## AI Usage Inside Templates

AI is allowed only for template slots such as:

1. headline variants,
2. short intros,
3. hook variants,
4. CTA wording,
5. short smoothing rewrites.

AI is not allowed to replace the template structure itself.

## Review Requirements

Every filled template should be reviewable against:

1. structural completeness,
2. readability,
3. derivative-risk,
4. mobile formatting,
5. tone safety.

## Definition Of Done

This spec is satisfied when:

1. the first blog template set is defined,
2. the first Facebook packaging set is defined,
3. comment CTA templates are defined,
4. all templates have clear required sections,
5. template-driven output is clearly preferred over free-form generation.
