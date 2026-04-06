# Active Source Registry V1

## Purpose

This document is the operational day-one source registry for the first pilot cycle.

Until source records are moved into the actual implementation store, this file should be treated as the active registry of record.

## Registry Rule

Only sources marked active in this file should be used during the first pilot cycle.

If a source is not listed here as active, it should not be part of the live intake workflow yet.

## Status Key

- `active_primary`
  Review on every active intake day.

- `active_secondary`
  Review regularly, but below primary sources.

- `active_selective`
  Use to add diversification or when primary sources are not yielding enough.

- `watchlist`
  Valid source candidate, but not active in the first live cycle.

## Day-One Active Sources

The following sources are activated for the first live pilot.

| source_id | source_name | domain | source_family | source_type | status | priority_tier | rss_feed_url | body_extraction_required | week_one_target_reviews | why_active_now | main_risk |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `src_tasting_table` | Tasting Table | `tastingtable.com` | `food_editorial` | `rss_plus_fetch` | `active_primary` | `tier_1` | `https://www.tastingtable.com/feed/` | `yes` | `4-5` | Strong curiosity fit, broad-interest food topics, good source of clickable angles | Can drift into glossy or trend-heavy pieces |
| `src_food_republic` | Food Republic | `foodrepublic.com` | `food_editorial` | `rss_plus_fetch` | `active_primary` | `tier_1` | `https://www.foodrepublic.com/feed/` | `yes` | `4-5` | Good mix of ingredient explainers, food culture, and transformation-friendly topics | Quality consistency varies by item |
| `src_curious_cuisiniere` | Curious Cuisiniere | `curiouscuisiniere.com` | `ingredient_reference` | `rss_plus_fetch` | `active_primary` | `tier_1` | `https://www.curiouscuisiniere.com/feed/` | `yes` | `3-4` | High-signal ingredient and food-origin material, useful for structured factual pieces | Lower volume than large editorial sites |
| `src_saveur` | Saveur | `saveur.com` | `food_editorial` | `rss_plus_fetch` | `active_secondary` | `tier_2` | `https://www.saveur.com/feed/` | `yes` | `3-4` | Strong food history and cultural depth, good for higher-trust background angles | Some content may be too long-form or less Facebook-direct |
| `src_bon_appetit` | Bon Appetit | `bonappetit.com` | `food_editorial` | `rss_plus_fetch` | `active_secondary` | `tier_2` | `https://www.bonappetit.com/feed/rss` | `yes` | `2-3` | Strong editorial brand and trust, useful for selective explanatory items | Very recipe-heavy feed mix requires careful filtering |
| `src_mashed` | Mashed | `mashed.com` | `curiosity_editorial` | `rss_plus_fetch` | `active_selective` | `tier_3` | `https://www.mashed.com/feed/` | `yes` | `2-3` | Useful as a curiosity stress test for Facebook-facing angles | Higher low-value and sensational-risk profile |

## Week-One Family Emphasis

The first week should emphasize the following source-family mix:

1. `food_editorial`: primary emphasis
2. `ingredient_reference`: secondary emphasis
3. `curiosity_editorial`: controlled selective emphasis

This means the pilot should learn first from strong editorial and reference-like material, then selectively test curiosity-heavy items rather than building the batch around them.

## Operational Quota Guidance

For week one, the total target is:

1. 18 to 24 reviewed source items,
2. 10 to 12 shortlisted items,
3. 6 to 8 advanced items for drafting.

The source mix should not become overly dependent on any one domain.

## Retention Rule For The First Week

Each active source should justify its place quickly.

Practical rule:

1. if a source yields zero strong candidates after its first 4 reviewed items, downgrade it,
2. if a source yields mostly weak or repetitive items, pause it,
3. if a secondary or selective source produces unexpectedly strong material, promote it in week two.

## Why This Registry Is Conservative

This registry is designed to:

1. favor signal over noise,
2. favor manageable intake over broad coverage,
3. keep the first pilot professional and reviewable,
4. learn from a mixed but disciplined source set.

## Immediate Next Use

The next use of this file is:

1. review the active feeds,
2. collect the first week's candidate items,
3. record which sources actually produce strong transformation candidates,
4. update source status after the first operating cycle.

## Initial Intake Signal As Of 2026-04-02

The first reviewed batch suggests:

1. `src_food_republic` is producing strong early transformation candidates,
2. `src_mashed` is producing strong hooks but still needs selective quality control,
3. `src_tasting_table` has at least one strong practical-curiosity candidate,
4. `src_saveur` and `src_bon_appetit` are more mixed because recipe and editorial pieces require tighter filtering,
5. `src_curious_cuisiniere` may still be useful, but the first sampled items leaned more recipe-forward than expected.

No source should be downgraded yet from this first small batch, but the next intake cycle should keep pressure on:

1. whether `src_curious_cuisiniere` yields enough non-recipe transformation candidates,
2. whether `src_bon_appetit` justifies the filtering effort,
3. whether `src_mashed` keeps producing usable curiosity content without dragging quality down.
