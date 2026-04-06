# Source Candidates

## Purpose

This document defines the recommended first seed sources for the v1 pilot.

These are not "forever sources." They are the first operational set for a manual-first vertical slice. The goal is to start with sources that are:

1. broad-interest,
2. food-relevant,
3. usable for curiosity-driven explanatory posts,
4. operationally realistic for a solo operator,
5. relatively easy to ingest through RSS or stable editorial structure.

## Selection Logic

The first seed set is intentionally mixed:

1. some sources are good for broad food curiosity,
2. some are good for ingredient or cooking explainers,
3. some are stronger editorial brands but need more filtering,
4. some are slightly more listicle-driven and should be used carefully.

The correct pilot strategy is not to assume every source is equal. It is to use a diversified starting set, observe which ones actually yield usable content, and narrow later.

## Intake Status Key

- `seed_now`
  Recommended for the first pilot batch.

- `watchlist`
  Valuable source, but use after the first pilot or after more manual verification.

- `high_friction`
  Good potential value, but intake path or site behavior is less efficient right now.

## Recommended Seed Set

The following sources are recommended as the first 8-source seed set.

Feed availability was checked on 2026-04-02 by direct HTTP request to likely feed endpoints.

| Priority | Domain | Source Family | Intake Type | Status | Why It Fits | Main Risk |
|---|---|---|---|---|---|---|
| 1 | `tastingtable.com` | `food_editorial` | `rss_plus_fetch` | `seed_now` | Broad-interest food culture, ingredient explainers, curiosity-friendly topics, usable editorial volume | Can lean glossy or trend-driven, so item filtering matters |
| 2 | `foodrepublic.com` | `food_editorial` | `rss_plus_fetch` | `seed_now` | Good mix of food culture, ingredient knowledge, and explainer-style content | Some content may be too broad or personality-driven |
| 3 | `thedailymeal.com` | `food_editorial` | `rss_plus_fetch` | `seed_now` | Large volume, broad-interest food stories, practical food curiosity angles | Quality consistency may vary across items |
| 4 | `bonappetit.com` | `food_editorial` | `rss_plus_fetch` | `seed_now` | Strong editorial quality, food culture depth, high trust, useful background angles | A lot of content will be recipe or lifestyle oriented and must be filtered |
| 5 | `saveur.com` | `food_editorial` | `rss_plus_fetch` | `seed_now` | Strong food history, culture, origin, and travel-adjacent food content | Some pieces may be too long-form or less Facebook-friendly |
| 6 | `chowhound.com` | `food_editorial` | `rss_plus_fetch` | `seed_now` | Useful for ingredient explainers, kitchen facts, and consumer-interest food topics | Editorial mix may include opinion-like pieces that are weak for templating |
| 7 | `mashed.com` | `curiosity_editorial` | `rss_plus_fetch` | `seed_now` | Strong curiosity and click-driving angle potential, easy to adapt into short readable pieces | Must be filtered aggressively to avoid low-value or overly sensational items |
| 8 | `curiouscuisiniere.com` | `ingredient_reference` | `rss_plus_fetch` | `seed_now` | Good for food origins, ingredient/cultural food explanations, niche differentiation | Smaller volume than larger editorial sites |

## Secondary Seed Candidates

These are good candidates to add once the first seed set is producing usable results.

| Domain | Source Family | Intake Type | Status | Why It Fits | Main Risk |
|---|---|---|---|---|---|
| `epicurious.com` | `recipe_editorial` | `rss_plus_fetch` | `watchlist` | Large brand with good food knowledge content around ingredients and technique | Very recipe-heavy, requires stronger filtering |
| `eater.com` | `food_editorial` | `rss_plus_fetch` | `watchlist` | Strong food-world brand, may yield food-culture and trend content | Too much restaurant/news content for the first niche |
| `atlasobscura.com` | `curiosity_editorial` | `rss_plus_fetch` | `watchlist` | Good curiosity angle and unusual food stories | Not food-specific enough for first-pass intake |

## High-Value Research Queue

These are worth revisiting later because the brand value or content quality is attractive, but the intake path is currently less efficient or more protected.

| Domain | Likely Value | Current Issue |
|---|---|---|
| `seriouseats.com` | High-value ingredient and cooking explainers, strong editorial fit | Feed endpoint or automated access appears high-friction right now |
| `thespruceeats.com` | Broad food and ingredient coverage, easy-to-format article types | Automated access appears high-friction right now |
| `foodandwine.com` | High-quality editorial food content | Feed access was not efficient in the current check |
| `allrecipes.com` | Massive volume and familiar food topics | Feed access appears high-friction for current intake path |
| `simplyrecipes.com` | Good explainer and recipe-adjacent educational content | Feed access appears high-friction for current intake path |

## Recommended First Source Mix

The first live mix should avoid overreliance on any one editorial style.

Recommended starting mix:

1. 3 broad editorial sources,
2. 2 higher-trust food culture or history sources,
3. 1 to 2 curiosity-leaning sources,
4. 1 more reference-like or ingredient-focused source.

The current seed list already reflects that balance.

## How To Use This List

For the pilot:

1. start with the 8 `seed_now` sources,
2. review actual item quality manually for the first 20 to 30 candidates,
3. down-rank or pause weak sources quickly,
4. only add `watchlist` sources after the first pilot cycle.

## Source Filtering Guidance

Even approved sources must still be filtered at the item level.

Prefer items that:

1. explain a food fact clearly,
2. have a strong curiosity hook,
3. can be converted into a short blog template,
4. are not primarily recipes,
5. are not primarily health claims,
6. are not pure food news with no evergreen value.

Avoid items that:

1. are just recipe instructions,
2. depend on celebrity or trend gossip,
3. rely on strong health claims,
4. are too thin to support transformation,
5. are too close to recently queued items.

## Pilot Recommendation

The first pilot should aim to sample from all 8 seed sources rather than leaning too hard on one site. The goal is to learn which sources yield the best transformation candidates, not to maximize initial volume from the easiest feed.

## Day-One Activation Recommendation

The day-one active source set is documented in:

[ACTIVE_SOURCE_REGISTRY_V1.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/execution/ACTIVE_SOURCE_REGISTRY_V1.md)

That registry narrows the 8-source seed set into the first operational mix and priority tiers.

## Definition Of Done

This document is serving its purpose when:

1. the first 5 to 10 sources are explicitly named,
2. there is a clear reason each source is in or out,
3. the pilot can begin without guessing where to look first.
