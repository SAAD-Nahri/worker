# Blog Template Contracts V1

## Purpose

This document turns the high-level blog template families into concrete contracts for Phase 2 implementation.

The point is not to create endless template variety. The point is to define a small set of reliable article shapes that can be filled deterministically and reviewed quickly.

## Core Rule

Each v1 blog draft must use one primary template contract.

The contract defines:

1. the required section order,
2. the target article length,
3. the tone constraints,
4. the prohibited patterns,
5. the minimum content completeness rules.

## Executable Enforcement Baseline

The accepted v1 implementation now encodes the strongest template rules directly in application code instead of leaving them only as prose.

That executable baseline currently includes:

1. slot-level soft word ranges for `intro` and required body sections,
2. bullet-count expectations for bullet-driven sections,
3. early-answer placement for `direct_answer` in the food-fact template,
4. deterministic validation that can emit named review flags when a slot drifts outside contract.

This matters because template IDs should not become decorative labels. The template contract needs enough behavioral meaning that later phases can trust it.

## Shared Rules Across All Blog Templates

All v1 blog templates must obey these shared rules:

1. English only,
2. mobile-friendly paragraph lengths,
3. short, readable sections,
4. answer or value delivered early,
5. no exaggerated health or medical framing,
6. no dramatic urgency language,
7. no giant wall-of-text body,
8. no free-form article shape outside the template.

### Shared Length Philosophy

V1 blog posts should be:

1. long enough to feel useful,
2. short enough to stay mobile-friendly,
3. short enough to keep the transformation process cheap and repeatable.

The default v1 target band is:

1. `220` to `620` words

Anything shorter than `120` words should usually be treated as too thin.

Anything longer than `900` words should usually be treated as a formatting failure unless there is a strong reason.

## Template 1: Food Fact Article

### Identity

1. `template_id`: `blog_food_fact_v1`
2. `template_family`: `food_fact_article`

### Best Use Cases

1. ingredient behavior explanations,
2. kitchen myth clarification,
3. food origin or process facts,
4. common food questions with simple answers.

### Target Length

1. preferred range: `260` to `520` words
2. soft minimum: `180`
3. soft maximum: `620`

### Required Section Order

1. `headline`
2. `intro`
3. `direct_answer`
4. `why_it_happens`
5. `supporting_points`
6. `recap`
7. `related_read_bridge` optional

### Section Expectations

**`headline`**

1. curiosity-oriented but honest,
2. no fake surprise,
3. should clearly relate to the source fact.

**`intro`**

1. target length: `35` to `70` words,
2. should frame the fact quickly,
3. should not delay the answer too long.

**`direct_answer`**

1. target length: `45` to `90` words,
2. must deliver the main fact early,
3. should appear within the first `120` words of the article.

**`why_it_happens`**

1. target length: `70` to `140` words,
2. explains the mechanism or reason,
3. should remain simple and readable.

**`supporting_points`**

1. use `2` to `4` short subpoints or mini-sections,
2. combined target length: `60` to `140` words,
3. may include examples, comparisons, or practical notes.

**`recap`**

1. target length: `30` to `70` words,
2. should close cleanly without repeating the whole article.

### Prohibited Patterns

1. delaying the answer until the end,
2. overpromising novelty,
3. using unsupported claims,
4. copying the source section order too literally.

## Template 2: Food Benefit Article

### Identity

1. `template_id`: `blog_food_benefit_v1`
2. `template_family`: `food_benefit_article`

### Best Use Cases

1. simple everyday usefulness of foods,
2. practical ingredient value summaries,
3. gentle utility framing that avoids strong medical claims.

### Target Length

1. preferred range: `280` to `560` words
2. soft minimum: `200`
3. soft maximum: `650`

### Required Section Order

1. `headline`
2. `intro`
3. `why_this_food_matters`
4. `practical_points`
5. `caution_or_limit`
6. `conclusion`

### Section Expectations

**`headline`**

1. should frame value conservatively,
2. should avoid medical or disease language,
3. should stay practical.

**`intro`**

1. target length: `35` to `70` words,
2. should explain why the topic is useful,
3. should not sound like a sales claim.

**`why_this_food_matters`**

1. target length: `60` to `120` words,
2. should explain the food or ingredient in simple terms.

**`practical_points`**

1. use `3` to `5` concise points,
2. combined target length: `80` to `180` words,
3. each point should be concrete and moderate in tone.

**`caution_or_limit`**

1. target length: `35` to `80` words,
2. should prevent overstatement,
3. should explicitly keep the article out of exaggerated health territory.

**`conclusion`**

1. target length: `30` to `70` words,
2. should summarize usefulness without hype.

### Prohibited Patterns

1. cure-like or disease-treatment wording,
2. absolute health promises,
3. aggressive wellness framing,
4. making the caution section optional.

## Template 3: Curiosity Article

### Identity

1. `template_id`: `blog_curiosity_food_v1`
2. `template_family`: `curiosity_article`

### Best Use Cases

1. surprising food questions,
2. food culture or history curiosities,
3. familiar foods with unexpected background.

### Target Length

1. preferred range: `220` to `440` words
2. soft minimum: `160`
3. soft maximum: `520`

### Required Section Order

1. `headline`
2. `fast_answer`
3. `background_explanation`
4. `example_or_context`
5. `close`

### Section Expectations

**`headline`**

1. usually question-led or contrast-led,
2. should create curiosity without becoming vague.

**`fast_answer`**

1. target length: `35` to `80` words,
2. the reader should understand the core answer quickly.

**`background_explanation`**

1. target length: `70` to `140` words,
2. gives the main explanation or backstory.

**`example_or_context`**

1. target length: `60` to `130` words,
2. should add one concrete example, comparison, or historical note.

**`close`**

1. target length: `25` to `60` words,
2. should end cleanly, not with a hard sell.

### Prohibited Patterns

1. vague question with no real answer,
2. burying the answer too late,
3. pretending speculation is fact,
4. overstuffing the piece with trivia instead of one clean theme.

## Template Selection Rules

Use the simplest valid template that fits the source item.

Selection defaults:

1. use `blog_food_fact_v1` for straightforward explanatory food facts,
2. use `blog_food_benefit_v1` only when the source is clearly about practical food value and the wording can stay conservative,
3. use `blog_curiosity_food_v1` when the source is driven by a question, contrast, or unusual backstory.

If a source item does not fit one of these templates cleanly, the correct v1 response is:

1. reject the item for Content Engine use,
2. or hold it for later template expansion,
3. not to invent a new one-off structure.

## Required Output Discipline

Every filled blog template must:

1. preserve source lineage,
2. use the contract section keys,
3. stay within reasonable length guidance,
4. remain reviewable section-by-section,
5. keep the article useful even when short.

## Definition Of Done

This spec is satisfied when:

1. the first three blog templates are implementation-ready,
2. each template has explicit section order and length targets,
3. the Content Engine can choose between them without guessing,
4. review can judge drafts against a concrete contract,
5. the key slot-level constraints are executable rather than prose-only.
