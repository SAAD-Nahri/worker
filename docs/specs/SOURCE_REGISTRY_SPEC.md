# Source Registry Spec

## Purpose

The source registry is the authoritative list of approved intake sources for the system. It exists to make sourcing deliberate, auditable, and improvable.

The registry is not just a list of URLs. It is the control layer for source quality.

## Goals

The source registry must:

1. define where the system is allowed to get content,
2. capture enough metadata to support future source scoring,
3. support RSS-first intake,
4. support selective scraping only where justified,
5. reduce single-source dependence,
6. keep the first niche focused on food facts.

## V1 Source Selection Criteria

For v1, a source is a strong candidate if it is:

1. relevant to food facts, food origins, ingredient explanations, cooking knowledge, or broad food curiosity,
2. stable enough to fetch repeatedly,
3. structured enough to extract useful text without excessive noise,
4. broad-interest rather than overly technical,
5. not primarily built around aggressive health claims,
6. useful for derivative formatting rather than direct copying,
7. likely to produce repeatable candidate items over time.

## Source Types

The registry should support the following source types:

1. `rss_native`
   A site with a usable RSS feed that surfaces candidate items directly.

2. `rss_plus_fetch`
   A site with RSS for discovery but requiring article-page fetching for body extraction.

3. `selective_scrape`
   A source without useful RSS where page-level retrieval is still worthwhile.

4. `manual_seed`
   A source family manually added for research or experimentation before automation support is formalized.

## Source Family Model

Each source should belong to a source family. This supports future scoring and diversification.

Suggested v1 source family categories:

1. `food_reference`
   Reference-style food information and explanations.

2. `food_editorial`
   General food journalism or lifestyle content with usable explanatory value.

3. `recipe_editorial`
   Recipe-focused sites when the extracted material supports facts or short explanatory articles.

4. `ingredient_reference`
   Ingredient-specific explainers and background resources.

5. `curiosity_editorial`
   Broad-interest content sources that occasionally publish food-curiosity material.

The family label is not just descriptive. It should be usable later for comparison and diversification rules.

## Required Registry Fields

Each source record should include at minimum:

1. `source_id`
   Stable internal identifier.

2. `source_name`
   Human-readable name.

3. `domain`
   Primary source domain.

4. `source_family`
   One of the allowed family categories.

5. `source_type`
   One of the allowed source types.

6. `primary_topic_fit`
   Short label or description of how the source fits the food-facts niche.

7. `active`
   Whether the source is currently allowed for intake.

8. `priority_level`
   Relative priority for fetching or review.

9. `rss_feed_url`
   Present when RSS is available.

10. `fetch_method`
    High-level method used for retrieval.

11. `body_extraction_required`
    Whether item detail pages must be fetched for usable content.

12. `freshness_pattern`
    Approximate cadence such as daily, weekly, evergreen, or irregular.

13. `quality_notes`
    Human notes about strengths, weaknesses, and extraction behavior.

14. `risk_notes`
    Known issues such as low reliability, too much health framing, or unstable markup.

15. `created_at`
    Registry entry creation time.

16. `updated_at`
    Last update time.

## Optional V1 Fields

These are useful but not mandatory on day one:

1. `status`
2. `language`
3. `region_focus`
4. `example_urls`
5. `last_fetch_at`
6. `last_success_at`
7. `last_failure_at`
8. `manual_review_score`
9. `retirement_reason`

## V1 Source Status Model

The source registry should support a practical status model for operator control.

Recommended v1 statuses:

1. `active_primary`
   Intake on every normal run.

2. `active_secondary`
   Valid intake source, but below primary sources.

3. `active_selective`
   Use for diversification or lower-confidence sources.

4. `downgraded`
   Still eligible for intake, but should be deprioritized until it proves value again.

5. `paused`
   Do not intake until manually reviewed.

6. `retired`
   No longer part of the working source set.

7. `watchlist`
   Candidate source not yet active in live intake.

The status field does not replace the `active` flag. It refines the operator's intent around active or inactive sources.

## Source Acceptance Rules

A new source may be accepted into the registry if:

1. it fits the first niche,
2. it has a plausible repeatable content yield,
3. its structure is not excessively noisy,
4. it does not create immediate policy-quality concerns,
5. it adds diversification or quality, not just more of the same.

## Source Rejection Rules

A source should be rejected or not added if:

1. it is highly dependent on sensational health claims,
2. it is too noisy to extract reliably,
3. it produces mostly thin, repetitive, or unusable items,
4. it adds no real value beyond existing registry sources,
5. it is too fragile to maintain at v1 complexity.

## Source Retirement Rules

A source should be marked inactive if:

1. extraction repeatedly fails,
2. the site changes structure and becomes too expensive to maintain,
3. the content quality drops,
4. the source drifts away from the target niche,
5. the source repeatedly produces low-value candidates.

## Initial Normalized Source Item Shape

Every fetched item should eventually normalize into a common item shape with at least:

1. `item_id`
2. `source_id`
3. `source_name`
4. `source_family`
5. `source_url`
6. `canonical_url`
7. `discovered_at`
8. `fetched_at`
9. `raw_title`
10. `raw_summary`
11. `raw_body_text`
12. `author_name` when available
13. `published_at` when available
14. `topical_label`
15. `freshness_label`
16. `normalization_status`
17. `dedupe_status`
18. `quality_flags`

## V1 Retrieval Philosophy

The Source Engine should prefer:

1. fewer better sources,
2. repeatable intake,
3. easy-to-audit registry entries,
4. source diversification across families,
5. low-maintenance fetch paths.

It should avoid:

1. broad crawler behavior,
2. speculative ingestion from random domains,
3. one-source dependency,
4. intake complexity that outruns the solo operator model.

## Selective Scraping Boundaries

When article-page fetching is used in v1, it should follow strict boundaries:

1. discovery should still begin from the approved registry and, where possible, from RSS,
2. article-page fetching should remain limited to source domains already approved in the registry,
3. fetching should target specific candidate items rather than crawl whole sites,
4. non-HTML or off-domain responses should be blocked,
5. failed extraction should fall back to feed-derived text instead of triggering broader scraping behavior.

## V1 Fallback Policy

V1 should distinguish clearly between normal intake, degraded intake, and manual-only sources.

Recommended behavior:

1. `rss_native` and `rss_plus_fetch`
   Use automated intake when the feed is healthy.

2. degraded RSS-first source
   If the feed is missing, broken, or no longer parseable, mark the fetch as degraded and route the source to manual review.

3. `manual_seed`
   Keep as manual-only input until there is a reason to formalize automation.

4. `selective_scrape`
   Treat as manual-only in Phase 1 rather than building generalized scrape escalation.

The key rule is simple:

Phase 1 must not react to RSS degradation by quietly turning into a crawler.

## Definition Of Done

This spec is satisfied when Phase 1 can implement:

1. a clear source registry record,
2. a clear normalized source item shape,
3. clear source acceptance and retirement rules,
4. clear source-family grouping,
5. a strong RSS-first intake bias.
