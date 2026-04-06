# Category And Tag Policy V1

## Purpose

This document defines the first controlled taxonomy for blog categories and tags.

The system needs a small taxonomy because:

1. review becomes faster,
2. archive structure stays clean,
3. later analysis becomes easier,
4. the Content Engine avoids random keyword sprawl.

## Core Rule

V1 uses:

1. one required primary category per draft,
2. a small controlled set of tags,
3. no open-ended taxonomy expansion by default.

## V1 Primary Categories

Use the smallest taxonomy that still supports useful organization.

### 1. `food-facts`

Default category for straightforward explanatory pieces about ingredients, food behavior, or kitchen facts.

### 2. `ingredient-guides`

Use when the article is centered on one ingredient and its behavior, usage, or background.

### 3. `food-questions`

Use when the article is built around a clear question-led curiosity angle.

### 4. `food-history-culture`

Use when the article is mainly about origin, history, tradition, or cultural context.

### 5. `food-benefits-light`

Use only for conservative utility or benefit framing that stays well away from medical claims.

## Category Selection Rules

Use exactly one primary category.

Selection defaults:

1. `blog_food_fact_v1` -> default to `food-facts`
2. `blog_food_benefit_v1` -> default to `food-benefits-light`
3. `blog_curiosity_food_v1` -> default to `food-questions`

Override only when the article is clearly better described by:

1. `ingredient-guides`
2. `food-history-culture`

If the category is unclear, flag for review instead of inventing a new category.

## Tag Policy

Tags are optional but recommended.

V1 target:

1. `3` to `6` tags per article

Tags should come from controlled patterns such as:

1. ingredient name,
2. kitchen concept,
3. food process,
4. cuisine or origin context,
5. question angle.

## Tag Formatting Rules

Tags should be:

1. lowercase,
2. hyphenated when multi-word,
3. short and reusable,
4. not sentence-like,
5. not duplicate of the category.

Good examples:

1. `olive-oil`
2. `fermentation`
3. `food-origins`
4. `kitchen-myths`
5. `cheese-storage`

Weak examples:

1. `why this food works better than you think`
2. `the best amazing health secret`
3. `food-facts` when that is already the category

## Tags To Avoid

Do not create tags that are:

1. one-off long phrases,
2. obvious title copies,
3. spammy keywords,
4. health-claim terms,
5. analytics-driven filler tags.

## Review Rules

Category and tag quality should usually result in:

1. `review_flag` if uncertain,
2. not an automatic block unless classification is fundamentally broken.

## Definition Of Done

This spec is satisfied when:

1. every draft can receive one primary category,
2. tags follow a controlled pattern,
3. taxonomy sprawl is avoided,
4. later publishing and analysis can rely on stable classification.
